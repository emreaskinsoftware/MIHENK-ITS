"""Özet şeması — KATMAN 2 çıktısı (spec 6.2).

İlke 1 (atıf zorunluluğu) burada tip düzeyinde zorlanır: source_post_ids alanı boş
olan bir SummarySentence nesnesi oluşturulamaz. Servis katmanı atıfsız cümleyi
silmek zorunda kalır, çünkü onu taşıyabileceği bir kap yoktur.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class SummarySentence(BaseModel):
    """Kaynağına bağlı tek bir özet cümlesi."""

    text: str
    source_post_ids: list[str] = Field(min_length=1)

    @field_validator("source_post_ids")
    @classmethod
    def _kaynak_bos_olamaz(cls, v: list[str]) -> list[str]:
        """İlke 1: atıfsız cümle kullanıcıya gösterilemez.

        Doğrulayıcıyı min_length kuralına ek olarak yazıyoruz, çünkü boş
        metinlerden oluşan bir liste min_length kontrolünü geçer ama atıf sayılmaz.
        """
        temiz = [pid.strip() for pid in v if pid and pid.strip()]
        if not temiz:
            raise ValueError("Ilke 1: ozet cumlesi en az bir kaynak gonderi ID tasimali")
        return temiz


class SummaryResponse(BaseModel):
    """Bir kategori için üretilmiş atıflı özet ve ölçüm alanları."""

    category: str
    sentences: list[SummarySentence]
    cluster_count: int
    # Atıfsız veya uydurma kaynaklı olduğu için silinen cümle sayısı.
    # Bu bir hata sayacı değil, raporlanan bir metriktir (spec 7).
    dropped_sentence_count: int = 0
    latency_ms: int = 0
    # Çoğulculuk gereği (İlke 3) özet üretilmeyen küme sayısı: tek yazarlı kümeler.
    single_source_cluster_count: int = 0
    # Zenginleştirmesi hazır olmadığı için atlanan gönderi sayısı (spec 6.2 adım 1).
    skipped_post_count: int = 0
    cache_hit_ratio: float = 0.0
