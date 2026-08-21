"""Yerel vLLM (OpenAI-uyumlu) sağlayıcısı.

DURUM: İskelet. P1'de doğrulanacak (spec 9). Bu dosyanın şimdiden var olmasının
sebebi, soyutlamanın gerçekten iki uygulamayı taşıdığını göstermektir; raporun
6.2'sinde "dış servis bağımlılığından çıkabiliriz" iddiası, arayüzün ikinci bir
uygulamayla test edilmiş olmasına dayanır.

vLLM `/v1/chat/completions` uç noktasını OpenAI biçiminde sunar; bu yüzden
istek gövdesi standart sohbet biçimindedir ve ek bir istemci kütüphanesi
gerekmez (yalnızca HTTP).
"""

from __future__ import annotations

import json
import os
import urllib.request

from app.config import config
from app.llm.provider import BaseProvider


class LocalVLLMProvider(BaseProvider):
    """Yerelde çalışan OpenAI-uyumlu uç noktaya bağlanır."""

    name = "vllm-local"

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        # Varsayılan adres vLLM'in standart portu; ortam değişkeniyle ezilebilir.
        self.base_url = (base_url or os.environ.get("MIHENK_VLLM_URL", "http://localhost:8000")).rstrip("/")
        self.model = model or os.environ.get("MIHENK_VLLM_MODEL", "yerel-model")
        self.name = f"vllm:{self.model}"

    def complete(self, system: str, user: str, max_tokens: int) -> str:
        """OpenAI sohbet biçiminde tamamlama ister."""
        govde = json.dumps(
            {
                "model": self.model,
                "max_tokens": max_tokens,
                # Sıcaklık 0: ölçümün tekrarlanabilir olması gerekiyor (spec 7,
                # "farklı tohumlarla tekrarlı çalıştırma" yalnızca eğitim için;
                # çıkarımda belirlenimcilik istiyoruz).
                "temperature": 0.0,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            }
        ).encode("utf-8")
        istek = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=govde,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(istek, timeout=config.llm_timeout_s) as yanit:
            veri = json.loads(yanit.read().decode("utf-8"))
        return veri["choices"][0]["message"]["content"].strip()
