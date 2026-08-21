"""LLM ve gömme katmanı (spec 4.3).

Dışarıya açılan tek kapı `get_provider()`'dır. Modüller sağlayıcı sınıflarını
doğrudan içe aktarmaz; böylece sağlayıcı değişimi tek dosyada kalır.
"""

from app.llm.embedding import cosine, get_embedder, turkish_lower
from app.llm.provider import LLMProvider, get_provider, reset_provider

__all__ = [
    "LLMProvider",
    "cosine",
    "get_embedder",
    "get_provider",
    "reset_provider",
    "turkish_lower",
]
