"""Zenginleştirilmiş gönderi şeması — KATMAN 1 çıktısı (spec 6.1).

Bu kayıt kullanıcıdan bağımsız üretilir ve kullanıcılar arasında paylaşılır.
Maliyet modelinin temeli budur: aynı gönderiyi 1000 kullanıcı görse de atomik
özet bir kez üretilir (spec 4.1 "neden böyle" bölümü).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class EnrichedPost(BaseModel):
    """Bir gönderinin akış hızında üretilmiş türevleri."""

    post_id: str
    author_id: str
    # 1-2 cümle, en fazla config.atomic_summary_max_words kelime.
    atomic_summary: str
    embedding: list[float]
    topic_label: str
    enriched_at: datetime
    # Kısa gönderilerde özet üretilmez, metnin kendisi kullanılır (spec 6.1).
    # Bu bayrak ölçümde "kaç LLM çağrısından tasarruf ettik" sorusunu cevaplar.
    summary_skipped: bool = False
    # Hangi sağlayıcı üretti — maliyet ve tekrarlanabilirlik takibi için.
    provider: str = "fake"
    tags: list[str] = Field(default_factory=list)
