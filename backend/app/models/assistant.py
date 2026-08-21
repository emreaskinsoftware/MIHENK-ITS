"""Gönderi asistanı şeması (spec 6.3).

`refused` alanı bir hata durumu değildir; İlke 2'nin (çekimserlik) ürün
yüzeyindeki karşılığıdır ve ölçülür: "bağlam dışı soruda doğru reddetme oranı"
raporun Tablo 5'inde yer alır.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

RefusalReason = Literal[
    "baglamda_yok",  # Cevap gönderi bağlamında bulunmuyor
    "enjeksiyon_supheli",  # Girdi istem enjeksiyonu içeriyor (spec 6.4)
    "cikti_kisiti",  # Üretilen yanıt URL/komut içerdiği için reddedildi
    "atifsiz",  # Yanıt kaynak gösteremedi (İlke 1)
]


class AssistantResponse(BaseModel):
    """Asistanın tek bir soruya yanıtı."""

    answer: str
    source_post_ids: list[str] = Field(default_factory=list)
    refused: bool = False
    refusal_reason: RefusalReason | None = None
    latency_ms: int = 0
