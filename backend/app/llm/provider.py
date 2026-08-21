"""LLM sağlayıcı soyutlaması (spec 4.3).

NEDEN SOYUTLAMA: Proje uzun vadede dış servis bağımlılığını azaltıp kendi
altyapısında çalışan modellere geçmeyi hedefliyor. Kod hiçbir yerde belirli bir
sağlayıcıya doğrudan bağlanmamalı ki geçiş tek dosyada olsun. Bu, raporun 6.2
(Teknik Sürdürülebilirlik) bölümünde iddia ettiğimiz şeydir; iddianın kod
karşılığı bu dosyadır.

Uygulamalar:
  - `FakeProvider`  (llm/fake.py)  — deterministik, dış çağrısız; test ve CI.
  - `APIProvider`   (llm/api.py)   — Anthropic Messages API.
  - `LocalVLLMProvider` (llm/vllm.py) — yerel OpenAI-uyumlu uç nokta.

Gömme çağrısı (embed) sohbet sağlayıcısından bağımsızdır ve llm/embedding.py'ye
devredilir; hiçbir sohbet sağlayıcısı gömme üretmez.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.config import config
from app.llm.embedding import get_embedder


@runtime_checkable
class LLMProvider(Protocol):
    """LLM sağlayıcı arayüzü."""

    name: str

    def complete(self, system: str, user: str, max_tokens: int) -> str:
        """Sistem + kullanıcı mesajından metin üretir."""
        ...

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Metinleri vektöre çevirir."""
        ...


class BaseProvider:
    """Ortak davranış: gömme çağrısını embedding katmanına devretmek.

    NEDEN BURADA: Her sağlayıcı aynı gömme koduna sahip olmasın diye. Sağlayıcı
    değiştiğinde vektör uzayının değişmemesi ayrıca önemlidir: önbellekteki
    gömmeler ile yeni gömmeler aynı uzayda olmalı, yoksa kümeleme bozulur.
    """

    name: str = "base"

    def embed(self, texts: list[str]) -> list[list[float]]:
        return get_embedder().embed(texts)


_provider: LLMProvider | None = None


def get_provider(force: str | None = None) -> LLMProvider:
    """Yapılandırmada seçili sağlayıcıyı döndürür (tekil).

    Args:
        force: Testlerde sağlayıcıyı doğrudan seçmek için ("fake" | "api" | "vllm").

    Sağlayıcı adı ölçüm çıktısına yazılır (spec 7): hangi modelle ölçtüğümüz
    raporda belli olmalı.
    """
    global _provider
    secim = force or config.llm_provider
    if _provider is not None and force is None:
        return _provider

    if secim == "api":
        from app.llm.api import APIProvider

        saglayici: LLMProvider = APIProvider()
    elif secim == "vllm":
        from app.llm.vllm import LocalVLLMProvider

        saglayici = LocalVLLMProvider()
    else:
        from app.llm.fake import FakeProvider

        saglayici = FakeProvider()

    if force is None:
        _provider = saglayici
    return saglayici


def reset_provider() -> None:
    """Tekil sağlayıcıyı sıfırlar (testler için)."""
    global _provider
    _provider = None
