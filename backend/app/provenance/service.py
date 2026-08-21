"""Görsel köken denetimi (spec 6.6) — P1.

ÜÇ KATMAN, SIRAYLA:

1. KESİN KATMAN — C2PA / Content Credentials manifesti, IPTC/XMP üst verisi,
   platform içi üretim etiketi. Burada kesinlik iddia edilebilir: manifest
   "bu görsel yapay zekâ ile üretildi" diyorsa bu bir imzalı beyandır.

2. ZAYIF SİNYAL — görsel adli bulgular (sıkıştırma izleri, gürültü
   tutarsızlığı). P2'ye ertelendi. Tek başına ASLA etiket üretmez.

3. ÇEKİMSERLİK — üst veri yok ve sinyal belirsizse hiçbir şey gösterilmez.

RAPORA GİRECEK DÜRÜST BULGU (platform tasarım önerisi):
Sosyal medya sıkıştırması üst verinin büyük kısmını siler. Yani köken bilgisi
platformun kendisi tarafından korunmadıkça, üçüncü taraf bir katman bu bilgiyi
güvenilir biçimde geri getiremez. Bu, NSosyal'in kendi işleme hattında üretim
etiketini KORUMASI gerektiğini gösteren somut bir platform tasarım önerisidir —
ve MİHENK'in NSosyal'e sunduğu katkılardan biridir.

Prototipte gerçek dosya okunmaz; `MediaRef.provenance_manifest` alanı üst
verinin sentetik karşılığıdır. Gerçek dağıtımda bu fonksiyonun girdisi bir
C2PA okuyucusundan gelir; arayüz aynı kalır.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from app.models import MediaRef

ProvenanceStatus = Literal[
    "yz_uretimi",  # Manifest açıkça YZ üretimi diyor
    "kamera_kaydi",  # Manifest cihaz kaydı diyor
    "belirsiz",  # Üst veri yok veya eksik -> çekimserlik
]


class ProvenanceResult(BaseModel):
    """Tek bir medya öğesinin köken denetimi sonucu."""

    media_id: str
    status: ProvenanceStatus
    # Kullanıcıya gösterilecek mi. "belirsiz" durumunda FALSE: boş alan bırakılır,
    # belirsizlik rozete dönüştürülmez (spec 6.9 tasarım kuralı).
    display: bool
    # Kesinlik iddiası hangi kaynağa dayanıyor.
    evidence: str | None = None
    detail: dict[str, Any] | None = None
    # Kullanıcıya gösterilecek açıklama; "belirsiz" durumunda None.
    label: str | None = None


def check_media(media: MediaRef) -> ProvenanceResult:
    """Medya öğesinin köken bilgisini değerlendirir.

    Karar sırası:
      1. Manifest yoksa veya boşsa -> belirsiz (gösterme).
      2. Manifest `ai_generated: True` diyorsa -> yz_uretimi (göster).
      3. Manifest var ve YZ demiyorsa -> kamera_kaydi (göster).

    NEDEN BOŞ MANİFEST DE BELİRSİZ: Sıkıştırma sırasında alanları silinmiş bir
    manifest, "bu görsel YZ değildir" anlamına gelmez; yalnızca bilginin
    kaybolduğu anlamına gelir. Yokluğu kanıt saymak, İlke 2'yi ihlal eder.
    """
    manifest = media.provenance_manifest
    if not manifest:
        return ProvenanceResult(
            media_id=media.media_id,
            status="belirsiz",
            display=False,
            evidence=None,
            detail={"neden": "ust_veri_yok"},
        )

    if manifest.get("ai_generated") is True:
        return ProvenanceResult(
            media_id=media.media_id,
            status="yz_uretimi",
            display=True,
            evidence="c2pa" if manifest.get("c2pa") else "iptc",
            detail={"generator": manifest.get("generator"), "issued_at": manifest.get("issued_at")},
            label="Yapay zekâ ile üretildi (üretici beyanı)",
        )

    if manifest.get("ai_generated") is False:
        return ProvenanceResult(
            media_id=media.media_id,
            status="kamera_kaydi",
            display=True,
            evidence="c2pa" if manifest.get("c2pa") else "iptc",
            detail={"generator": manifest.get("generator"), "issued_at": manifest.get("issued_at")},
            label="Cihaz kaydı (üretici beyanı)",
        )

    # Manifest var ama üretim bilgisi taşımıyor: yine belirsiz.
    return ProvenanceResult(
        media_id=media.media_id,
        status="belirsiz",
        display=False,
        evidence=None,
        detail={"neden": "manifest_eksik_alan"},
    )


def coverage_report(medyalar: list[MediaRef]) -> dict[str, Any]:
    """Üst veri kapsama oranını hesaplar — raporun platform önerisi bölümü için.

    Bu sayı bir başarım metriği DEĞİLDİR; ekosistemin durumunu gösterir.
    "Görsellerin yalnızca %X'inde köken bilgisi var" cümlesi, platformun bu
    bilgiyi koruması gerektiği önerisinin dayanağıdır.
    """
    sonuclar = [check_media(m) for m in medyalar]
    toplam = len(sonuclar)
    gosterilebilir = sum(1 for s in sonuclar if s.display)
    return {
        "toplam_medya": toplam,
        "kokeni_bilinen": gosterilebilir,
        "kapsama_orani": round(gosterilebilir / toplam, 4) if toplam else 0.0,
        "belirsiz": toplam - gosterilebilir,
        "yz_uretimi": sum(1 for s in sonuclar if s.status == "yz_uretimi"),
        "kamera_kaydi": sum(1 for s in sonuclar if s.status == "kamera_kaydi"),
    }
