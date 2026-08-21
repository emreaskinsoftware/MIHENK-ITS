"""YZ tespiti modeli eğitimi (spec 5.2 / rapor 3.2).

İKİ ARKA UÇ:
  --backend tfidf    : TF-IDF + lojistik regresyon temel çizgisi (saniyeler)
  --backend berturk  : Türkçe encoder ince ayarı (MODEL_KARTI.md'deki model)

NEDEN TEMEL ÇİZGİ ZORUNLU: "Türkçe encoder ince ayarı yaptık" cümlesi tek
başına bir başarı iddiası değildir. Basit bir n-gram sınıflandırıcısı aynı
sonucu veriyorsa, ağır modelin maliyeti savunulamaz. Rapor Tablo 4'te iki
satır yan yana durur; bu, jürinin soracağı "neden bu model" sorusunun cevabıdır.

TEKRARLANABİLİRLİK: Tüm tohumlar sabitlenir ve kullanılan hiperparametreler
çıktı dosyasına yazılır. Rapordaki hiperparametre tablosu oradan kopyalanır,
elle yazılmaz.

Kullanım:
    python ml/scripts/train_detector.py --backend tfidf
    python ml/scripts/train_detector.py --backend berturk --seeds 3
"""

from __future__ import annotations

import argparse
import json
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import _bootstrap  # noqa: F401
import numpy as np

from app.config import config
from app.detection.detector import BERTURK_DIR, LABELS, TFIDF_PATH

REPO_ROOT = _bootstrap.REPO_ROOT
VERI_DIZINI = REPO_ROOT / "ml" / "data" / "detection"
ARTIFACT_DIR = REPO_ROOT / "ml" / "artifacts"


@dataclass
class EgitimRaporu:
    """Eğitim koşusunun kaydı — rapor 3.2 hiperparametre tablosunun kaynağı."""

    backend: str
    model_name: str
    seed: int
    train_size: int
    val_size: int
    hyperparameters: dict = field(default_factory=dict)
    val_accuracy: float = 0.0
    val_f1: float = 0.0
    duration_s: float = 0.0


def veri_yukle(ad: str) -> tuple[list[str], list[int]]:
    """Bölmeyi (metin, etiket) olarak yükler. Etiket: 0=insan, 1=yapay_zeka."""
    yol = VERI_DIZINI / f"{ad}.jsonl"
    if not yol.exists():
        raise SystemExit(
            f"Veri yok: {yol}\nÖnce kurun: python ml/scripts/build_dataset.py"
        )
    metinler, etiketler = [], []
    for satir in yol.read_text(encoding="utf-8").splitlines():
        if not satir.strip():
            continue
        kayit = json.loads(satir)
        metinler.append(kayit["text"])
        etiketler.append(LABELS.index(kayit["label"]))
    return metinler, etiketler


def _f1(gercek: list[int], tahmin: list[int]) -> float:
    """Pozitif sınıf (yapay_zeka) için F1."""
    tp = sum(1 for g, t in zip(gercek, tahmin) if g == 1 and t == 1)
    fp = sum(1 for g, t in zip(gercek, tahmin) if g == 0 and t == 1)
    fn = sum(1 for g, t in zip(gercek, tahmin) if g == 1 and t == 0)
    if tp == 0:
        return 0.0
    kesinlik = tp / (tp + fp)
    duyarlilik = tp / (tp + fn)
    return 2 * kesinlik * duyarlilik / (kesinlik + duyarlilik)


# ----------------------------------------------------------------------
# TF-IDF temel çizgisi
# ----------------------------------------------------------------------
def egit_tfidf(seed: int) -> EgitimRaporu:
    """Karakter + kelime n-gram TF-IDF üzerinde lojistik regresyon eğitir.

    ÖZELLİK SEÇİMİ GEREKÇESİ:
      - `char_wb` 2-5 n-gram: Türkçe sondan eklemeli olduğu için kelime
        sonlarındaki ek kalıpları ("-mektedir", "-mıştır") sınıf sinyali taşır.
        Kelime sınırına duyarlı (wb) varyant, kelimeler arası gürültüyü keser.
      - Kelime 1-2 gram: kalıplaşmış ifadeler ("önem arz etmektedir") bütün
        olarak yakalanır.
      - `sublinear_tf`: bir kelimenin 10 kez geçmesi 10 kat önemli değildir.
      - `class_weight="balanced"`: sınıf dengesizliğine karşı koruma; veri seti
        dengeli kurulsa da bu ayar, dengenin bozulduğu durumda sessiz sapmayı
        önler.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import FeatureUnion, Pipeline

    baslangic = time.perf_counter()
    random.seed(seed)
    np.random.seed(seed)

    x_train, y_train = veri_yukle("train")
    x_val, y_val = veri_yukle("val")

    hiper = {
        "char_ngram": "2-5 (char_wb)",
        "word_ngram": "1-2",
        "min_df": 2,
        "sublinear_tf": True,
        "C": 4.0,
        "class_weight": "balanced",
        "max_iter": 2000,
    }

    ozellikler = FeatureUnion(
        [
            (
                "karakter",
                TfidfVectorizer(
                    analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True
                ),
            ),
            (
                "kelime",
                TfidfVectorizer(
                    analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True
                ),
            ),
        ]
    )
    hat = Pipeline(
        [
            ("ozellikler", ozellikler),
            (
                "siniflandirici",
                LogisticRegression(
                    C=hiper["C"],
                    max_iter=hiper["max_iter"],
                    class_weight=hiper["class_weight"],
                    random_state=seed,
                ),
            ),
        ]
    )
    hat.fit(x_train, y_train)

    tahmin = list(hat.predict(x_val))
    dogruluk = sum(1 for g, t in zip(y_val, tahmin) if g == t) / len(y_val)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    import joblib

    joblib.dump(hat, TFIDF_PATH)

    return EgitimRaporu(
        backend="tfidf",
        model_name="tfidf-char_wb(2,5)+word(1,2) + LogisticRegression",
        seed=seed,
        train_size=len(x_train),
        val_size=len(x_val),
        hyperparameters=hiper,
        val_accuracy=round(dogruluk, 4),
        val_f1=round(_f1(y_val, tahmin), 4),
        duration_s=round(time.perf_counter() - baslangic, 2),
    )


# ----------------------------------------------------------------------
# BERTurk ince ayarı
# ----------------------------------------------------------------------
def egit_berturk(seed: int) -> EgitimRaporu:
    """Türkçe encoder'ı ikili sınıflandırma için ince ayarlar.

    NEDEN TÜRKÇE-ÖZEL ENCODER: Çok dilli modeller Türkçe morfolojisini daha
    kaba parçalara ayırır; Türkçe korpusta eğitilmiş bir tokenizer, ek
    yapılarını daha az parçayla temsil eder ve kısa metinlerde (K1 kovası)
    bilgi kaybı azalır. Kısa metin bizim en zor bölgemiz olduğu için bu fark
    önemlidir.

    Eğitim tamamen CPU'da koşabilecek boyutta tutulmuştur (küçük veri seti,
    3 epoch): ekipte GPU garantisi yok ve demo makinesinde çalışması gerekiyor.
    """
    import torch
    from torch.utils.data import DataLoader, Dataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    baslangic = time.perf_counter()
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    x_train, y_train = veri_yukle("train")
    x_val, y_val = veri_yukle("val")

    tokenizer = AutoTokenizer.from_pretrained(config.detection_model)
    model = AutoModelForSequenceClassification.from_pretrained(
        config.detection_model,
        num_labels=len(LABELS),
        id2label={i: ad for i, ad in enumerate(LABELS)},
        label2id={ad: i for i, ad in enumerate(LABELS)},
    )

    # --- CPU'da eğitilebilirlik için iki optimizasyon -------------------
    # ÖLÇÜLEN SORUN: Sabit 256 token doldurma ve tüm katmanların eğitilmesiyle
    # tek adım bu makinede ~57 saniye sürüyordu; 3 epoch ≈ 2 saat. Ekipte GPU
    # yok ve modelin demo makinesinde yeniden eğitilebilmesi gerekiyor.
    #
    # 1) DİNAMİK DOLDURMA: Her parti, o partideki en uzun örneğe kadar
    #    doldurulur. Veri setindeki metinlerin çoğu 50-100 token; sabit 256'ya
    #    doldurmak hesabın büyük bölümünü boş token üzerinde harcıyordu.
    #
    # 2) KISMÎ İNCE AYAR: Gömme katmanı ve alt encoder katmanları dondurulur;
    #    yalnızca üst katmanlar ve sınıflandırma başlığı eğitilir. Bu hem geri
    #    yayılım maliyetini yarıya indirir hem de 714 örneklik küçük veri
    #    setinde aşırı öğrenmeyi azaltır. Alt katmanlar genel dil bilgisini
    #    taşır ve bu görev için yeniden öğrenilmesine gerek yoktur.
    class MetinKumesi(Dataset):
        """Ham metin + etiket taşıyan küme; tokenizasyon parti anında yapılır."""

        def __init__(self, metinler: list[str], etiketler: list[int]) -> None:
            self.metinler = metinler
            self.etiketler = etiketler

        def __len__(self) -> int:
            return len(self.etiketler)

        def __getitem__(self, i: int) -> tuple[str, int]:
            return self.metinler[i], self.etiketler[i]

    def parti_hazirla(ogeler: list[tuple[str, int]]) -> dict:
        """Parti içindeki en uzun örneğe kadar doldurur (dinamik doldurma)."""
        metinler = [m for m, _ in ogeler]
        etiketler = [e for _, e in ogeler]
        kodlar = tokenizer(
            metinler,
            truncation=True,
            padding=True,
            max_length=config.detection_max_length,
            return_tensors="pt",
        )
        kodlar["labels"] = torch.tensor(etiketler)
        return kodlar

    dondurulan_katman = config.detection_frozen_layers
    if dondurulan_katman > 0:
        for parametre in model.bert.embeddings.parameters():
            parametre.requires_grad = False
        for katman in model.bert.encoder.layer[:dondurulan_katman]:
            for parametre in katman.parameters():
                parametre.requires_grad = False
    egitilebilir = sum(p.numel() for p in model.parameters() if p.requires_grad)
    toplam = sum(p.numel() for p in model.parameters())
    print(f"  eğitilebilir parametre: {egitilebilir:,} / {toplam:,} "
          f"(alt {dondurulan_katman} katman donduruldu)")

    egitim_yukleyici = DataLoader(
        MetinKumesi(x_train, y_train),
        batch_size=config.detection_batch_size,
        shuffle=True,
        collate_fn=parti_hazirla,
    )
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=config.detection_learning_rate
    )

    model.train()
    for epoch in range(config.detection_epochs):
        toplam_kayip = 0.0
        epoch_baslangic = time.perf_counter()
        for parti in egitim_yukleyici:
            optimizer.zero_grad()
            cikti = model(**parti)
            cikti.loss.backward()
            # Gradyan kırpma: küçük veri setinde büyük gradyanlar eğitimi
            # dengesizleştirebiliyor; 1.0 standart ve güvenli bir sınır.
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            toplam_kayip += float(cikti.loss)
        print(
            f"  epoch {epoch + 1}/{config.detection_epochs} "
            f"kayıp={toplam_kayip / max(1, len(egitim_yukleyici)):.4f} "
            f"süre={time.perf_counter() - epoch_baslangic:.0f}s",
            flush=True,
        )

    model.eval()
    tahminler: list[int] = []
    with torch.no_grad():
        for i in range(0, len(x_val), 16):
            parti = tokenizer(
                x_val[i : i + 16],
                padding=True,
                truncation=True,
                max_length=config.detection_max_length,
                return_tensors="pt",
            )
            tahminler.extend(int(t) for t in model(**parti).logits.argmax(dim=-1))

    dogruluk = sum(1 for g, t in zip(y_val, tahminler) if g == t) / len(y_val)

    BERTURK_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(BERTURK_DIR))
    tokenizer.save_pretrained(str(BERTURK_DIR))

    return EgitimRaporu(
        backend="berturk",
        model_name=config.detection_model,
        seed=seed,
        train_size=len(x_train),
        val_size=len(x_val),
        hyperparameters={
            "epochs": config.detection_epochs,
            "batch_size": config.detection_batch_size,
            "learning_rate": config.detection_learning_rate,
            "max_length": config.detection_max_length,
            "optimizer": "AdamW",
            "grad_clip": 1.0,
            "frozen_layers": config.detection_frozen_layers,
            "padding": "dinamik (parti ici en uzun)",
            "trainable_params": egitilebilir,
            "total_params": toplam,
        },
        val_accuracy=round(dogruluk, 4),
        val_f1=round(_f1(y_val, tahminler), 4),
        duration_s=round(time.perf_counter() - baslangic, 2),
    )


def main() -> None:
    ayristirici = argparse.ArgumentParser(description="YZ tespiti modelini eğitir")
    ayristirici.add_argument("--backend", choices=["tfidf", "berturk"], default="tfidf")
    ayristirici.add_argument("--seed", type=int, default=20260824)
    args = ayristirici.parse_args()

    print(f"Eğitim başlıyor: {args.backend} (tohum {args.seed})")
    rapor = egit_tfidf(args.seed) if args.backend == "tfidf" else egit_berturk(args.seed)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    kayit_yolu = ARTIFACT_DIR / f"training_{args.backend}.json"
    kayit_yolu.write_text(json.dumps(asdict(rapor), ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"bitti: doğrulama doğruluğu={rapor.val_accuracy} F1={rapor.val_f1} "
        f"süre={rapor.duration_s}s"
    )
    print(f"eğitim kaydı -> {kayit_yolu}")
    print("NOT: Nihai metrikler test kümesinde ölçülür: python ml/scripts/evaluate.py")


if __name__ == "__main__":
    main()
