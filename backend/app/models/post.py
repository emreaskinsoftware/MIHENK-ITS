"""Gönderi şeması — sentetik NSosyal akışının temel birimi (spec 5.1).

KRİTİK TASARIM KARARI: Değerlendirme etiketleri (`_eval_*`) bu modelde durur ama
`to_service_dict()` ile servis katmanına aktarılırken kesinlikle dışarıda kalır.
Sebep: bu etiketler "doğru cevap"tır. Prompt'a veya servise sızarlarsa ölçüm
geçersiz olur — model tespit etmiş gibi görünür, oysa cevabı okumuştur.
Bu ayrım `backend/tests/test_eval_sizinti.py` ile test edilir.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PostCategory = Literal["gundem", "spor", "kisisel"]

# Servis katmanına ve prompt'lara asla girmemesi gereken alan öneki.
EVAL_FIELD_PREFIX = "_eval_"


class MediaRef(BaseModel):
    """Gönderiye ekli görsel/video referansı.

    `provenance_manifest` alanı C2PA / IPTC üst verisinin sentetik karşılığıdır:
    gerçek dosya yerine üst verinin var/yok olma durumunu taşırız (spec 6.6).
    Gerçek dünyada bu alan dosyadan okunur; sentetik akışta üretilir.
    """

    media_id: str
    kind: Literal["image", "video"] = "image"
    # None = üst veri yok (platform sıkıştırması silmiş olabilir) -> çekimserlik
    provenance_manifest: dict[str, Any] | None = None


class Post(BaseModel):
    """Tek bir sosyal medya gönderisi.

    author_id gerçek kişi değil, sentetik takma addır (spec 2: gerçek kişisel
    veri işlenmez).
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    author_id: str
    text: str
    created_at: datetime
    category: PostCategory
    media: list[MediaRef] = Field(default_factory=list)
    # Alıntı zinciri: asistanın bağlam sınırını belirler (spec 6.3).
    quoted_post_id: str | None = None
    reply_to_post_id: str | None = None

    # --- yalnızca değerlendirme için, ürüne sızdırılmaz (spec 5.1) ---
    eval_is_ai_generated: bool | None = Field(default=None, alias="_eval_is_ai_generated")
    eval_is_manipulative: bool | None = Field(default=None, alias="_eval_is_manipulative")
    eval_has_injection: bool | None = Field(default=None, alias="_eval_has_injection")
    # Aynı olayı farklı açıdan anlatan gönderileri gruplayan kurgusal olay kimliği.
    eval_event_id: str | None = Field(default=None, alias="_eval_event_id")
    eval_length_bucket: Literal["K1", "K2", "K3"] | None = Field(
        default=None, alias="_eval_length_bucket"
    )

    def to_service_dict(self) -> dict[str, Any]:
        """Servis katmanının göreceği temiz sözlüğü döndürür.

        NEDEN AYRI FONKSİYON: `model_dump()` çağıran her yer `_eval_*` alanlarını
        elemeyi unutabilir. Tek bir kapı bırakıp testle koruyoruz — sızıntı riski
        insan dikkatine değil, koda emanet edilir.
        """
        data = self.model_dump(mode="json", by_alias=True)
        return {k: v for k, v in data.items() if not k.startswith(EVAL_FIELD_PREFIX)}

    @property
    def word_count(self) -> int:
        """Kelime sayısı — zenginleştirmede kısa gönderi kararı için kullanılır."""
        return len(self.text.split())
