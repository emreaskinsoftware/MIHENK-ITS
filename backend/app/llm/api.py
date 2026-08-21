"""Anthropic Messages API sağlayıcısı.

Bu dosya, sağlayıcıya özgü TEK yerdir (spec 4.3). Başka bir servise geçmek
gerektiğinde yalnızca burası değişir; çağıran modüller `LLMProvider` arayüzünü
görür.

MALİYET NOTU: Çağrı sayısı ve token kullanımı `usage` alanından okunup
`CallStats` içinde biriktirilir. Raporun "1000 özet başına maliyet" satırı
(spec 7) uydurma değil, bu sayaçtan üretilir.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from app.config import config
from app.llm.provider import BaseProvider


@dataclass
class CallStats:
    """Sağlayıcı üzerinden yapılan çağrıların birikimli sayaçları."""

    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    errors: int = 0
    per_task: dict[str, int] = field(default_factory=dict)

    def kaydet(self, gorev: str, girdi: int, cikti: int) -> None:
        self.calls += 1
        self.input_tokens += girdi
        self.output_tokens += cikti
        self.per_task[gorev] = self.per_task.get(gorev, 0) + 1


class APIProvider(BaseProvider):
    """Anthropic API üzerinden metin üretimi.

    Anahtar `ANTHROPIC_API_KEY` ortam değişkeninden okunur. Anahtar yoksa
    nesne oluşturulurken hata verir — sessizce sahte sağlayıcıya düşmeyiz,
    çünkü o durumda ölçüm hangi modelle yapıldığı belirsizleşir (spec 2).
    """

    name = "anthropic-api"

    def __init__(self, model: str | None = None) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as hata:  # pragma: no cover - kurulum kaynaklı
            raise RuntimeError(
                "anthropic paketi kurulu değil. `pip install anthropic` veya "
                "MIHENK_LLM_PROVIDER=fake ile çalıştırın."
            ) from hata

        anahtar = os.environ.get("ANTHROPIC_API_KEY")
        if not anahtar:
            raise RuntimeError(
                "ANTHROPIC_API_KEY tanımlı değil. Ölçüm ve demo için gerçek "
                "sağlayıcı gerekir; test için MIHENK_LLM_PROVIDER=fake kullanın."
            )
        self.model = model or config.llm_model
        self.name = f"anthropic:{self.model}"
        self._client = Anthropic(api_key=anahtar, timeout=config.llm_timeout_s)
        self.stats = CallStats()

    def complete(self, system: str, user: str, max_tokens: int) -> str:
        """Tek turlu tamamlama.

        NEDEN TEK TUR: Bu hattaki hiçbir görev çok turlu diyalog gerektirmiyor.
        Bağlam taşımamak hem maliyeti düşürür hem de enjeksiyonun turlar arası
        kalıcı olma ihtimalini ortadan kaldırır (spec 6.4).
        """
        gorev = user.partition("\n")[0].replace("GOREV:", "").strip() or "bilinmiyor"
        try:
            yanit = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception:
            self.stats.errors += 1
            raise

        self.stats.kaydet(
            gorev,
            getattr(yanit.usage, "input_tokens", 0),
            getattr(yanit.usage, "output_tokens", 0),
        )
        parcalar = [blok.text for blok in yanit.content if getattr(blok, "type", "") == "text"]
        return "".join(parcalar).strip()
