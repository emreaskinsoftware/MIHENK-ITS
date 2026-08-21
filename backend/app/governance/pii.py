"""Kişisel veri maskeleme (spec 5.3).

BU KOD BİR BELGE DEĞİL, KAPIDIR: Eğitim havuzuna giren her metin buradan geçer
(ml/scripts/build_dataset.py). Raporun 6.2'sinde "KVKK uyumlu tasarım" iddiası
ancak bu fonksiyon gerçekten çalışıyorsa savunulabilir.

TASARIM İLKESİ — YANLIŞ TARAFA DÜŞ: Maskeleme fazla agresif olursa metin biraz
bozulur; az agresif olursa kişisel veri sızar. İkinci hatanın maliyeti
kıyaslanamayacak kadar yüksektir, bu yüzden şüpheli kalıpları maskeliyoruz.

KAPSAM SINIRI (dürüstlük notu, rapora girecek): Kalıp tabanlı maskeleme ad-soyad
gibi serbest metin içindeki kişisel verileri yakalayamaz. Prototipte bu bir
sorun değildir çünkü veri sentetiktir ve gerçek kişi içermez; gerçek veriye
geçişte adlandırılmış varlık tanıma (NER) katmanı eklenmelidir. Bu sınır
docs/VERI_YONETISIMI.md dosyasında da yazılıdır.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Maskeleme kalıpları. Sıra önemlidir: e-posta, kullanıcı adından önce gelmeli,
# aksi halde "@" içeren e-posta adresi kullanıcı adı sanılır ve parçalanır.
_KALIPLAR: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("EPOSTA", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b")),
    ("URL", re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE)),
    # Telefon: Türkiye biçimleri (+90, 0 5xx, boşluk/tire/parantezli varyantlar).
    ("TELEFON", re.compile(r"(?:\+90|0)?[\s(-]*5\d{2}[\s)-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}\b")),
    # TC Kimlik No: 11 hane. Yanlış pozitifi azaltmak için kelime sınırı şart.
    ("TCKN", re.compile(r"\b[1-9]\d{10}\b")),
    # IBAN (TR + 24 hane)
    ("IBAN", re.compile(r"\bTR\d{2}[\s]?(?:\d{4}[\s]?){5}\d{2}\b", re.IGNORECASE)),
    ("KULLANICI", re.compile(r"(?<![\w.])@[A-Za-z0-9_]{2,}")),
)


@dataclass
class MaskResult:
    """Maskeleme çıktısı ve hangi türden kaç adet maskelendiği."""

    text: str
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def masked_any(self) -> bool:
        return bool(self.counts)


def mask_pii(text: str) -> MaskResult:
    """Metindeki kişisel veri kalıplarını yer tutucularla değiştirir.

    Yer tutucu biçimi `[EPOSTA]`, `[TELEFON]` gibidir. Silmek yerine yer tutucu
    koymamızın sebebi: metnin cümle yapısı korunur, böylece tespit modeli
    "burada bir şey vardı" bilgisini kaybetmez ama içerik kaybolur.

    Returns:
        MaskResult — maskelenmiş metin ve tür bazında sayaçlar. Sayaçlar
        veri yönetişim raporunda "kaç kayıt maskelendi" satırını üretir.
    """
    sonuc = text
    sayaclar: dict[str, int] = {}
    for etiket, desen in _KALIPLAR:
        sonuc, adet = desen.subn(f"[{etiket}]", sonuc)
        if adet:
            sayaclar[etiket] = sayaclar.get(etiket, 0) + adet
    return MaskResult(text=sonuc, counts=sayaclar)


def contains_pii(text: str) -> bool:
    """Metinde kişisel veri kalıbı var mı (maskelemeden kontrol)."""
    return any(desen.search(text) for _, desen in _KALIPLAR)
