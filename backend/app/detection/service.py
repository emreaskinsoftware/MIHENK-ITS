"""Tespit servisi — model + çekimserlik kurallarını birleştirir (spec 6.5).

Bu ince katmanın varlık sebebi: API ve ölçüm tarafı, "model yükle, olasılık al,
kuralları uygula" dizisini tekrar tekrar yazmasın. Sıralamanın tek bir yerde
olması, çekimserlik kuralının atlanmasını imkânsız kılar.
"""

from __future__ import annotations

from app.detection.decision import karar_ver
from app.detection.detector import get_detector
from app.models import DetectionResult


def detect(text: str) -> DetectionResult:
    """Tek metin için tespit sonucu üretir.

    Model yoksa olasılık None olarak geçilir ve karar katmanı çekimser kalır.
    """
    model = get_detector()
    if model is None:
        return karar_ver(text, None)
    return karar_ver(text, model.predict_proba([text])[0])


def detect_many(texts: list[str]) -> list[DetectionResult]:
    """Toplu tespit — ölçüm koşuları için (tek tek çağırmak yavaş).

    Karar kuralları her metne ayrı ayrı uygulanır; toplu çalışmak yalnızca
    model çağrısını hızlandırır, davranışı değiştirmez.
    """
    model = get_detector()
    if model is None:
        return [karar_ver(t, None) for t in texts]
    olasiliklar = model.predict_proba(texts)
    return [karar_ver(t, p) for t, p in zip(texts, olasiliklar)]
