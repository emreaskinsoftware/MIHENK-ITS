"""KATMAN 1 — eşzamansız zenginleştirme (spec 4.1 / 6.1)."""

from app.enrichment.topics import keywords, topic_label
from app.enrichment.worker import (
    EnrichmentStats,
    cache_key,
    enrich_feed,
    enrich_post,
    get_enriched,
)

__all__ = [
    "EnrichmentStats",
    "cache_key",
    "enrich_feed",
    "enrich_post",
    "get_enriched",
    "keywords",
    "topic_label",
]
