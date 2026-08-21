"""Eğitilmiş tespit modelinin yüklenmesi ve olasılık üretimi (spec 6.5).

İKİ ARKA UÇ — NEDEN İKİSİ BİRDEN:

1. `TfidfDetector` (temel çizgi): karakter + kelime n-gram TF-IDF üzerinde
   lojistik regresyon. Saniyeler içinde eğitilir, ağırlığı birkaç yüz kilobayt,
   CPU'da anında çalışır. Görevi iki yönlü:
     - Raporun karşılaştırma satırını üretir. "Türkçe encoder ince ayarı işe
       yaradı" demek, ancak basit bir temel çizgiyle kıyaslanınca anlam taşır.
     - Ağır bağımlılıklar (torch) kurulu olmadığında hattın çalışmasını sağlar.

2. `BerturkDetector` (ana model): MODEL_KARTI.md'de kayıtlı Türkçe encoder'ın
   ince ayarlı hâli. Raporun Tablo 4'ü bununla üretilir.

Model bulunamazsa `get_detector()` None döner ve karar katmanı çekimser kalır
(`reason="model_yok"`). Uydurma olasılık üretmiyoruz (spec 2).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol

from app.config import REPO_ROOT, get_settings

logger = logging.getLogger(__name__)

ARTIFACT_DIR = REPO_ROOT / "ml" / "artifacts"
TFIDF_PATH = ARTIFACT_DIR / "detector_tfidf.joblib"
BERTURK_DIR = ARTIFACT_DIR / "detector_berturk"

# Sınıf sırası: 0 = insan, 1 = yapay_zeka. Bu sıra eğitim ve çıkarımda
# aynı olmak zorunda; tek yerde tanımlı olması karışıklığı önler.
LABELS = ("insan", "yapay_zeka")


class Detector(Protocol):
    """Tespit modeli arayüzü."""

    name: str

    def predict_proba(self, texts: list[str]) -> list[float]:
        """Her metin için 'yapay zekâ ürünü' olasılığını döndürür."""
        ...


class TfidfDetector:
    """TF-IDF + lojistik regresyon temel çizgisi."""

    name = "tfidf-logreg"

    def __init__(self, path: Path | None = None) -> None:
        import joblib

        self.path = path or TFIDF_PATH
        if not self.path.exists():
            raise FileNotFoundError(
                f"Model dosyası yok: {self.path}\n"
                "Önce eğitin: python ml/scripts/train_detector.py --backend tfidf"
            )
        self._pipeline = joblib.load(self.path)

    def predict_proba(self, texts: list[str]) -> list[float]:
        # predict_proba sütun sırası sınıfların sıralı hâlidir; LABELS ile
        # aynı olduğunu eğitim tarafında garanti ediyoruz.
        return [float(p[1]) for p in self._pipeline.predict_proba(texts)]


class BerturkDetector:
    """İnce ayarlı Türkçe encoder (BERTurk) sınıflandırıcısı."""

    name = "berturk-finetuned"

    def __init__(self, model_dir: Path | None = None) -> None:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self._torch = torch
        self.model_dir = model_dir or BERTURK_DIR
        if not self.model_dir.exists():
            raise FileNotFoundError(
                f"Model dizini yok: {self.model_dir}\n"
                "Önce eğitin: python ml/scripts/train_detector.py --backend berturk"
            )
        self._tokenizer = AutoTokenizer.from_pretrained(str(self.model_dir))
        self._model = AutoModelForSequenceClassification.from_pretrained(str(self.model_dir))
        self._model.eval()

    def predict_proba(self, texts: list[str]) -> list[float]:
        """Toplu çıkarım.

        Parti boyutu 16: CPU'da bellek ve gecikme arasında makul denge.
        max_length 256: veri setindeki en uzun kova (K3) 170 token civarı;
        256 güvenli üst sınır ve gereksiz doldurma yapmaz.
        """
        sonuclar: list[float] = []
        with self._torch.no_grad():
            for i in range(0, len(texts), 16):
                parti = texts[i : i + 16]
                girdiler = self._tokenizer(
                    parti, padding=True, truncation=True, max_length=256, return_tensors="pt"
                )
                mantik = self._model(**girdiler).logits
                olasiliklar = self._torch.softmax(mantik, dim=-1)[:, 1]
                sonuclar.extend(float(x) for x in olasiliklar)
        return sonuclar


_detector: Detector | None = None
_denendi = False


def get_detector(force: str | None = None) -> Detector | None:
    """Kullanılabilir tespit modelini döndürür; yoksa None.

    None dönmesi bir hata değildir: karar katmanı bu durumda çekimser kalır ve
    arayüzde hiçbir rozet gösterilmez. Model yokken "insan" varsaymak, sessiz
    ve ölçülemeyen bir yanlış pozitif kaynağı olurdu.
    """
    global _detector, _denendi
    if force is None and _denendi:
        return _detector

    secim = force or get_settings().detection_backend
    adaylar: list[type] = []
    if secim in ("auto", "berturk"):
        adaylar.append(BerturkDetector)
    if secim in ("auto", "tfidf"):
        adaylar.append(TfidfDetector)

    secilen: Detector | None = None
    for sinif in adaylar:
        try:
            secilen = sinif()
            break
        except Exception as hata:
            logger.info("%s yüklenemedi: %s", sinif.__name__, hata)

    if force is None:
        _detector, _denendi = secilen, True
    if secilen is None:
        logger.warning("Tespit modeli yok; sistem çekimser kalacak (reason=model_yok).")
    return secilen


def reset_detector() -> None:
    """Tekil model önbelleğini sıfırlar (testler ve yeniden eğitim sonrası)."""
    global _detector, _denendi
    _detector, _denendi = None, False
