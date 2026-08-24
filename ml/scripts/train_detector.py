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
import statistics
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
def egit_berturk(seed: int, *, max_steps: int = 0, devam: bool = True) -> EgitimRaporu:
    """Türkçe encoder'ı ikili sınıflandırma için ince ayarlar.

    NEDEN TÜRKÇE-ÖZEL ENCODER: Çok dilli modeller Türkçe morfolojisini daha
    kaba parçalara ayırır; Türkçe korpusta eğitilmiş bir tokenizer, ek
    yapılarını daha az parçayla temsil eder ve kısa metinlerde (K1 kovası)
    bilgi kaybı azalır. Kısa metin bizim en zor bölgemiz olduğu için bu fark
    önemlidir.

    Eğitim tamamen CPU'da koşabilecek boyutta tutulmuştur (küçük veri seti,
    3 epoch): ekipte GPU garantisi yok ve demo makinesinde çalışması gerekiyor.

    Args:
        seed: Rastgelelik tohumu.
        max_steps: Bu çağrıda yapılacak en fazla optimizasyon adımı (0 = sınırsız).
            Sınıra ulaşılırsa ilerleme kaydedilir ve çıkılır; aynı komut tekrar
            çalıştırıldığında kaldığı yerden devam eder.
        devam: Kayıtlı bir eğitim durumu varsa oradan devam et (varsayılan).
            False verilirse temel modelden sıfırdan başlanır.
    """
    import os

    import torch
    from torch.utils.data import DataLoader, Dataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    from app.detection.device import resolve_runtime

    profil = resolve_runtime()
    if not profil.is_cuda:
        # torch, CPU'da varsayılan olarak fiziksel çekirdek sayısını kullanıyor
        # (bu makinede 12 mantıksal çekirdeğin 8'i). Eğitim tamamen CPU'da
        # koşacaksa tüm çekirdekleri vermek doğrudan süreye yansır.
        torch.set_num_threads(os.cpu_count() or 8)
    print(f"  {profil.summary()}", flush=True)

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
    ).to(profil.device)

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
    #    yayılım maliyetini yarıya indirir hem de 836 örneklik küçük veri
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

    dondurulan_katman = profil.frozen_layers
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
        batch_size=profil.batch_size,
        shuffle=True,
        collate_fn=parti_hazirla,
    )
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=config.detection_learning_rate
    )

    # --- Kaldığı yerden devam (checkpoint/resume) ----------------------
    # NEDEN GEREKLİ: Bu makinede tam eğitim yaklaşık yarım saat sürüyor ve
    # geliştirme ortamında uzun süreli arka plan süreçleri sonlandırılabiliyor
    # (iki denemede eğitim sessizce kesildi). Parça parça koşabilmek, eğitimi
    # ortama bağımlı olmaktan çıkarır. Ayrıca bu, GPU'suz bir ekibin modeli
    # yeniden üretebilmesi için pratik bir gerekliliktir.
    #
    # Durum dosyası ilerlemeyi taşır; optimizer momentumu da kaydedilir çünkü
    # AdamW'de moment durumu atılırsa devam eden eğitim baştan başlamış gibi
    # davranır ve kayıp eğrisi bozulur.
    durum_yolu = BERTURK_DIR / "training_state.json"
    optimizer_yolu = BERTURK_DIR / "optimizer.pt"
    baslangic_epoch = 0
    global_adim = 0

    if devam and durum_yolu.exists():
        durum = json.loads(durum_yolu.read_text(encoding="utf-8"))
        if durum.get("done"):
            print("  eğitim zaten tamamlanmış (training_state.json: done=true)")
        baslangic_epoch = int(durum.get("epoch", 0))
        global_adim = int(durum.get("global_step", 0))
        # Kaydedilmiş ağırlıkları yükle: temel modelden değil, kaldığı yerden.
        model = AutoModelForSequenceClassification.from_pretrained(str(BERTURK_DIR)).to(
            profil.device
        )
        if dondurulan_katman > 0:
            for parametre in model.bert.embeddings.parameters():
                parametre.requires_grad = False
            for katman in model.bert.encoder.layer[:dondurulan_katman]:
                for parametre in katman.parameters():
                    parametre.requires_grad = False
        optimizer = torch.optim.AdamW(
            [p for p in model.parameters() if p.requires_grad],
            lr=config.detection_learning_rate,
        )
        if optimizer_yolu.exists():
            optimizer.load_state_dict(torch.load(optimizer_yolu, weights_only=True))
        print(f"  devam ediliyor: epoch {baslangic_epoch}, toplam adım {global_adim}")

    def _kaydet(epoch_bitti: int, adim: int, tamamlandi: bool) -> None:
        """Model, optimizer ve ilerleme durumunu diske yazar."""
        BERTURK_DIR.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(str(BERTURK_DIR))
        tokenizer.save_pretrained(str(BERTURK_DIR))
        torch.save(optimizer.state_dict(), optimizer_yolu)
        durum_yolu.write_text(
            json.dumps(
                {
                    "epoch": epoch_bitti,
                    "global_step": adim,
                    "total_epochs": config.detection_epochs,
                    "seed": seed,
                    "done": tamamlandi,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    olcekleyici = (
        torch.amp.GradScaler("cuda") if (profil.is_cuda and profil.amp) else None
    )

    model.train()
    kalan_butce = max_steps if max_steps > 0 else float("inf")
    for epoch in range(baslangic_epoch, config.detection_epochs):
        toplam_kayip = 0.0
        adim_sayisi = 0
        epoch_baslangic = time.perf_counter()
        for parti in egitim_yukleyici:
            if kalan_butce <= 0:
                # Adım bütçesi doldu: epoch'un ortasındayız. İlerlemeyi
                # kaydedip çıkıyoruz; bir sonraki çağrı bu epoch'u BAŞTAN
                # koşar. NEDEN BAŞTAN: parti sırasını yeniden kurmak yerine
                # epoch'u tekrarlamak, birkaç fazladan adım pahasına çok daha
                # basit ve hataya kapalı bir devam mantığı verir.
                _kaydet(epoch, global_adim, tamamlandi=False)
                print(
                    f"  adım bütçesi doldu (epoch {epoch + 1} yarıda kaldı, "
                    f"toplam adım {global_adim}). Devam için aynı komutu "
                    "tekrar çalıştırın.",
                    flush=True,
                )
                return EgitimRaporu(
                    backend="berturk",
                    model_name=config.detection_model,
                    seed=seed,
                    train_size=len(x_train),
                    val_size=len(x_val),
                    hyperparameters={"durum": "yarim", "global_step": global_adim},
                    duration_s=round(time.perf_counter() - baslangic, 2),
                )
            parti = {k: v.to(profil.device) for k, v in parti.items()}
            optimizer.zero_grad()
            if olcekleyici is not None:
                # Karışık hassasiyet: ileri geçiş float16'da yapılır, kayıp
                # ölçeklenerek geri yayılır. GPU'da belirgin hız ve bellek
                # kazancı sağlar; sayısal kararlılık ölçekleyiciyle korunur.
                with torch.autocast(device_type="cuda", dtype=torch.float16):
                    cikti = model(**parti)
                olcekleyici.scale(cikti.loss).backward()
                # Kırpmadan önce ölçek geri alınmalı, yoksa eşik anlamsızlaşır.
                olcekleyici.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                olcekleyici.step(optimizer)
                olcekleyici.update()
            else:
                cikti = model(**parti)
                cikti.loss.backward()
                # Gradyan kırpma: küçük veri setinde büyük gradyanlar eğitimi
                # dengesizleştirebiliyor; 1.0 standart ve güvenli bir sınır.
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
            toplam_kayip += float(cikti.loss)
            adim_sayisi += 1
            global_adim += 1
            kalan_butce -= 1
            # ARA KAYIT: Süreç beklenmedik biçimde sonlanırsa (ortam kotası,
            # kapatma) en fazla son birkaç adım kaybolsun. Model kaydetme
            # birkaç saniye sürüyor; 10 adımda bir yapmak, tekrarlanan işi
            # kayıt maliyetinin altında tutar.
            if global_adim % 10 == 0:
                _kaydet(epoch, global_adim, tamamlandi=False)
                print(f"    ara kayıt: adım {global_adim}", flush=True)
        print(
            f"  epoch {epoch + 1}/{config.detection_epochs} "
            f"kayıp={toplam_kayip / max(1, adim_sayisi):.4f} "
            f"süre={time.perf_counter() - epoch_baslangic:.0f}s",
            flush=True,
        )
        _kaydet(epoch + 1, global_adim, tamamlandi=(epoch + 1 == config.detection_epochs))

    model.eval()
    tahminler: list[int] = []
    with torch.no_grad():
        for i in range(0, len(x_val), profil.batch_size):
            parti = tokenizer(
                x_val[i : i + profil.batch_size],
                padding=True,
                truncation=True,
                max_length=config.detection_max_length,
                return_tensors="pt",
            ).to(profil.device)
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
            "learning_rate": config.detection_learning_rate,
            "max_length": config.detection_max_length,
            "optimizer": "AdamW",
            "grad_clip": 1.0,
            "device": profil.device,
            "device_name": profil.device_name,
            "batch_size_used": profil.batch_size,
            "amp": profil.amp,
            "frozen_layers": dondurulan_katman,
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
    ayristirici.add_argument(
        "--max-steps",
        type=int,
        default=0,
        help=(
            "Bu çağrıda yapılacak en fazla optimizasyon adımı (0 = sınırsız). "
            "CPU'da uzun eğitimi parçalara bölmek için; ilerleme kaydedilir."
        ),
    )
    ayristirici.add_argument(
        "--bastan",
        action="store_true",
        help="Kayıtlı eğitim durumunu yok say, temel modelden başla.",
    )
    ayristirici.add_argument(
        "--seeds",
        type=int,
        default=1,
        help=(
            "Kaç farklı tohumla tekrarlı eğitim yapılsın (spec 7: ortalama ± "
            "standart sapma). Kaydedilen model son tohuma aittir."
        ),
    )
    args = ayristirici.parse_args()

    # NEDEN ÇOK TOHUM: Tek koşudan çıkan bir doğruluk değeri, modelin
    # başarımını değil o koşunun şansını da içerir. Rapora ortalama ± standart
    # sapma yazılır; tek sayı yazmak, olmayan bir kesinlik iddia etmektir.
    #
    # ÖLÇÜLEN NOT (rapora girer): TF-IDF + lojistik regresyon hattı bu veride
    # TAM BELİRLENİMCİDİR; 5 tohumda standart sapma 0.000 çıktı. Tohum yalnızca
    # çözücünün rastgeleliğini etkiliyor, o da lbfgs'te kullanılmıyor. Bu hattın
    # gerçek değişkenliği VERİ tohumundan gelir:
    #     python ml/scripts/build_dataset.py --seed <farklı>
    # BERTurk tarafında ise ağırlık başlatma ve parti karıştırma nedeniyle tohum
    # farkı gerçek bir değişkenlik üretir; CPU maliyeti nedeniyle tek tohumla
    # koşuldu ve bu sınırlılık model kartında belirtildi.
    tohumlar = [args.seed + i for i in range(max(1, args.seeds))]
    raporlar: list[EgitimRaporu] = []

    for tohum in tohumlar:
        print(f"Eğitim başlıyor: {args.backend} (tohum {tohum})")
        rapor = (
            egit_tfidf(tohum)
            if args.backend == "tfidf"
            else egit_berturk(tohum, max_steps=args.max_steps, devam=not args.bastan)
        )
        raporlar.append(rapor)
        print(
            f"  bitti: doğrulama doğruluğu={rapor.val_accuracy} F1={rapor.val_f1} "
            f"süre={rapor.duration_s}s"
        )

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    kayit_yolu = ARTIFACT_DIR / f"training_{args.backend}.json"

    # Yarıda kesilen koşular (adım bütçesi doldu) ortalamaya girmez: onların
    # doğrulama skoru hiç ölçülmemiştir, 0.0 olarak ortalamayı bozar.
    tamamlanan = [r for r in raporlar if r.hyperparameters.get("durum") != "yarim"]
    if not tamamlanan:
        print("Eğitim yarıda kaldı; devam etmek için aynı komutu tekrar çalıştırın.")
        return
    raporlar = tamamlanan
    dogruluklar = [r.val_accuracy for r in raporlar]
    f1ler = [r.val_f1 for r in raporlar]
    ozet = {
        "backend": args.backend,
        "model_name": raporlar[-1].model_name,
        "seeds": tohumlar,
        "runs": [asdict(r) for r in raporlar],
        "val_accuracy_mean": round(statistics.mean(dogruluklar), 4),
        "val_accuracy_std": round(statistics.stdev(dogruluklar), 4) if len(dogruluklar) > 1 else 0.0,
        "val_f1_mean": round(statistics.mean(f1ler), 4),
        "val_f1_std": round(statistics.stdev(f1ler), 4) if len(f1ler) > 1 else 0.0,
        "hyperparameters": raporlar[-1].hyperparameters,
    }
    kayit_yolu.write_text(json.dumps(ozet, ensure_ascii=False, indent=2), encoding="utf-8")

    if len(raporlar) > 1:
        print(
            f"ORTALAMA: doğruluk {ozet['val_accuracy_mean']} ± {ozet['val_accuracy_std']} "
            f"| F1 {ozet['val_f1_mean']} ± {ozet['val_f1_std']} ({len(tohumlar)} tohum)"
        )
    print(f"eğitim kaydı -> {kayit_yolu}")
    print("NOT: Nihai metrikler test kümesinde ölçülür: python ml/scripts/evaluate.py")


if __name__ == "__main__":
    main()
