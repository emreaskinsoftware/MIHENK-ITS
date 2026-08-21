"""YZ metin sinyali (spec 6.5).

İki parça:
  - decision.py : çekimserlik kuralları (modelden bağımsız, İlke 2)
  - detector.py : eğitilmiş modeli yükleyip olasılık üretir
"""

from app.detection.decision import karar_ver, length_bucket

__all__ = ["karar_ver", "length_bucket"]
