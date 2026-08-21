"""YZ metin sinyali (spec 6.5).

İki parça:
  - decision.py : çekimserlik kuralları (modelden bağımsız, İlke 2)
  - detector.py : eğitilmiş modeli yükleyip olasılık üretir
"""

from app.detection.decision import karar_ver, length_bucket
from app.detection.detector import LABELS, get_detector, reset_detector
from app.detection.device import RuntimeProfile, resolve_runtime
from app.detection.service import detect, detect_many

__all__ = [
    "LABELS",
    "RuntimeProfile",
    "detect",
    "detect_many",
    "get_detector",
    "karar_ver",
    "length_bucket",
    "reset_detector",
    "resolve_runtime",
]
