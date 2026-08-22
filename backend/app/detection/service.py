"""Tespit servisi — model + çekimserlik kurallarını birleştirir (spec 6.5).

Bu ince katmanın varlık sebebi: API ve ölçüm tarafı, "model yükle, olasılık al,
kuralları uygula" dizisini tekrar tekrar yazmasın. Sıralamanın tek bir yerde
olması, çekimserlik kuralının atlanmasını imkânsız kılar.
"""

from __future__ import annotations

from app.detection.calibration import aktif_bant
from app.detection.decision import karar_ver
from app.detection.detector import get_detector
from app.models import DetectionResult


def detect(text: str) -> DetectionResult:
    """Tek metin için tespit sonucu üretir.

    Model yoksa olasılık None olarak geçilir ve karar katmanı çekimser kalır.
    Karar bandı modele göre seçilir: her modelin olasılık ölçeği farklıdır,
    tek bir sabit bant ikisine birden uymaz (bkz. calibration.py).
    """
    model = get_detector()
    if model is None:
        return karar_ver(text, None)
    return karar_ver(
        text, model.predict_proba([text])[0], bant=aktif_bant(model.name)
    )


def detect_many(texts: list[str]) -> list[DetectionResult]:
    """Toplu tespit — ölçüm koşuları için (tek tek çağırmak yavaş).

    Karar kuralları her metne ayrı ayrı uygulanır; toplu çalışmak yalnızca
    model çağrısını hızlandırır, davranışı değiştirmez.
    """
    model = get_detector()
    if model is None:
        return [karar_ver(t, None) for t in texts]
    olasiliklar = model.predict_proba(texts)
    bant = aktif_bant(model.name)
    return [karar_ver(t, p, bant=bant) for t, p in zip(texts, olasiliklar)]
