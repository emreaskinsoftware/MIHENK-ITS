"""İstem enjeksiyonu savunması (spec 6.4).

Dört katman, her biri ayrı dosyada:
  1. Yapısal ayrım        -> prompt_guard.py
  2. Girdi temizleme+sinyal -> sanitize.py
  3. Çıktı kısıtı          -> output_guard.py
  4. Yetki ve izin listesi -> agent modülünde (config.allowed_domains)

Kırmızı takım kümesi `eval/injection_suite.yaml` dosyasındadır ve savunma oranı
`ml/scripts/evaluate.py` tarafından ölçülür.
"""

from app.security.output_guard import OutputCheck, check_output
from app.security.prompt_guard import (
    DELIM_END,
    DELIM_START,
    GUVENLIK_BASLIGI,
    wrap_posts,
    wrap_untrusted,
)
from app.security.sanitize import SanitizeResult, sanitize

__all__ = [
    "DELIM_END",
    "DELIM_START",
    "GUVENLIK_BASLIGI",
    "OutputCheck",
    "SanitizeResult",
    "check_output",
    "sanitize",
    "wrap_posts",
    "wrap_untrusted",
]
