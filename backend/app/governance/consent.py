"""Eğitim havuzu izin kapısı (spec 5.3).

KURAL: `training_consent` alanı bulunmayan veya False olan hiçbir kayıt eğitim
havuzuna giremez. Prototipte gerçek kullanıcı verisi yoktur; buna rağmen kapı
kodda vardır ve testi vardır.

NEDEN ŞİMDİDEN VAR: Bir veri yönetişim iddiası, sistem büyüdükten sonra
eklenemez. İzin kontrolü sonradan eklendiğinde, o ana kadar toplanmış tüm veri
"izinsiz toplanmış" olur ve geriye dönük düzeltilemez. Kapı ilk günden kapalı
olmalı; bu, jüriye gösterilebilir somut bir tasarım kararıdır.

VARSAYILAN REDDETMEDİR: Alan eksikse izin var sayılmaz. Belirsizlikte veri
işlememek, İlke 2'nin (çekimserlik) veri yönetişimindeki karşılığıdır.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

CONSENT_FIELD = "training_consent"


class ConsentError(ValueError):
    """İzinsiz kaydı eğitim havuzuna sokma girişimi."""


@dataclass
class ConsentFilterResult:
    """Süzme çıktısı: kabul edilenler ve neden reddedildikleri."""

    accepted: list[dict[str, Any]] = field(default_factory=list)
    rejected_missing_field: int = 0
    rejected_no_consent: int = 0

    @property
    def rejected_total(self) -> int:
        return self.rejected_missing_field + self.rejected_no_consent


def has_consent(record: dict[str, Any]) -> bool:
    """Kayıtta geçerli eğitim izni var mı.

    Yalnızca `True` (bool) kabul edilir. "true", 1, "evet" gibi değerler
    REDDEDİLİR: tip gevşekliği, izin gibi kritik bir alanda sessiz hataya yol
    açar (örneğin "false" dizgesi Python'da doğru sayılır).
    """
    return record.get(CONSENT_FIELD) is True


def assert_consent(record: dict[str, Any]) -> None:
    """İzin yoksa hata fırlatır — eğitim hattında sert kapı olarak kullanılır."""
    if not has_consent(record):
        kimlik = record.get("id", "<kimliksiz>")
        raise ConsentError(
            f"Kayıt {kimlik}: {CONSENT_FIELD} alanı True değil, eğitim havuzuna alınamaz."
        )


def filter_for_training(records: Iterable[dict[str, Any]]) -> ConsentFilterResult:
    """Eğitim havuzuna girecek kayıtları süzer ve reddetme sebeplerini sayar.

    Sayaçlar veri yönetişim raporuna girer: kaç kayıt izin eksikliğinden
    dışarıda kaldı sorusunun cevabı ölçülebilir olmalıdır.
    """
    sonuc = ConsentFilterResult()
    for kayit in records:
        if CONSENT_FIELD not in kayit:
            sonuc.rejected_missing_field += 1
            continue
        if not has_consent(kayit):
            sonuc.rejected_no_consent += 1
            continue
        sonuc.accepted.append(kayit)
    return sonuc
