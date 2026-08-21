"""Doğrulama ajanı şemaları (spec 6.7).

Şemalar P1 uygulamasından ÖNCE yazıldı. Sebebi: çıktı biçimi bu modülün en
kritik tasarım kararıdır. Üç durumlu çıktıyı tip düzeyinde sabitlemek, ileride
"pratik olsun diye" ikili bir doğru/yanlış alanı eklenmesini engeller.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# ÜÇ DURUM — dördüncüsü yoktur ve eklenmeyecektir (İlke 3).
#   DESTEKLEYEN : bulunan kaynaklar iddiayı destekliyor
#   CELISEN     : kaynaklar birbiriyle veya iddiayla çelişiyor
#   KAYNAK_YOK  : izin listesindeki kaynaklarda ilgili bilgi bulunamadı
VerificationStatus = Literal["DESTEKLEYEN", "CELISEN", "KAYNAK_YOK"]


class SourceRef(BaseModel):
    """Ajanın gittiği tek bir kaynak.

    `quote` alanı bilinçli olarak KISA tutulur (telif — spec 2, madde 5).
    Ajan uzun alıntı yapmaz; kendi cümlesiyle özetler ve kaynağa yönlendirir.
    """

    url: str
    domain: str
    title: str | None = None
    # En fazla bir cümlelik bağlam; tam metin değil.
    quote: str = Field(default="", max_length=300)
    retrieved_at: str | None = None


class ToolCall(BaseModel):
    """Denetlenebilirlik kaydı: ajanın yaptığı her araç çağrısı loglanır."""

    step: int
    tool: str
    argument: str
    ok: bool
    note: str | None = None


class VerificationResult(BaseModel):
    """Bir iddianın doğrulama sonucu."""

    claim: str
    status: VerificationStatus
    supporting: list[SourceRef] = Field(default_factory=list)
    conflicting: list[SourceRef] = Field(default_factory=list)
    # Kaynaklar çelişiyorsa çelişkinin NE OLDUĞU yazılır; hangisinin haklı
    # olduğu YAZILMAZ.
    disagreement_note: str | None = None
    # Denetim izi — jüri "ajan ne yaptı" diye sorabilir.
    tool_calls: list[ToolCall] = Field(default_factory=list)
    steps_used: int = 0
    truncated: bool = False  # adım sınırına takıldı mı
