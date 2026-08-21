"""YZ metin sinyali (spec 6.5).

İki parça:
  - decision.py : çekimserlik kuralları (modelden bağımsız, İlke 2)
  - detector.py : eğitilmiş modeli yükleyip olasılık üretir
"""

from app.detection.decision import karar_ver, length_bucket
from app.detection.detector import LABELS, get_detector, reset_detector
from app.detection.service import detect

__all__ = ["LABELS", "detect", "get_detector", "karar_ver", "length_bucket", "reset_detector"]
