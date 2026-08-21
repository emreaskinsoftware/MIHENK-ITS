"""YZ metin sinyali şeması (spec 6.5).

label = None çekimserliktir ve arayüzde hiçbir rozet gösterilmemesi anlamına gelir
(spec 6.9 tasarım kuralı). Bu yüzden label alanı isteğe bağlıdır; "bilinmiyor" diye
ayrı bir etiket değeri uydurmuyoruz — belirsizliği etikete dönüştürmek İlke 2'yi
ihlal ederdi.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

DetectionLabel = Literal["insan_olasi", "yz_olasi"]
AbstainReason = Literal["metin_cok_kisa", "belirsiz", "model_yok"]
LengthBucket = Literal["K1", "K2", "K3"]


class DetectionResult(BaseModel):
    """Tek bir metin için YZ üretimi sinyali."""

    label: DetectionLabel | None = None
    confidence: float | None = None
    abstained: bool = False
    reason: AbstainReason | None = None
    token_count: int = 0
    # Hangi kovadan geldiği — uzunluk kovası bazlı doğruluk tablosu için (spec 7).
    length_bucket: LengthBucket | None = None
