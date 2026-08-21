"""Veri yönetişim sınırı (spec 5.3).

Bu paket bir belge değil, çalışan koddur. Raporun 6.2 bölümündeki KVKK uyumlu
tasarım iddiasının kod karşılığı buradadır:

  - pii.py         : eğitim havuzuna giren her metin maskeden geçer
  - consent.py     : izinsiz kayıt eğitim havuzuna giremez (varsayılan reddetme)
  - aggregation.py : k eşiğinin altındaki grup hiç döndürülmez
  - retention.py   : özet için çekilen içerik kalıcı saklanmaz
"""

from app.governance.aggregation import AggregationResult, aggregate_with_k_threshold
from app.governance.consent import ConsentError, assert_consent, filter_for_training, has_consent
from app.governance.pii import MaskResult, contains_pii, mask_pii
from app.governance.retention import PurgeReport, RetentionPolicy, forget_user, purge_expired

__all__ = [
    "AggregationResult",
    "ConsentError",
    "MaskResult",
    "PurgeReport",
    "RetentionPolicy",
    "aggregate_with_k_threshold",
    "assert_consent",
    "contains_pii",
    "filter_for_training",
    "forget_user",
    "has_consent",
    "mask_pii",
    "purge_expired",
]
