"""Çıktı kısıtı — istem enjeksiyonuna karşı son savunma hattı (spec 6.4, katman 2).

NEDEN ÇIKTI TARAFINDA DA KONTROL VAR: Girdi tarafındaki kalıp taraması ve
yapısal ayrım atlatılabilir. Ama saldırının KULLANICIYA ULAŞMASI için modelin
çıktısında bir taşıyıcı olması gerekir: bir bağlantı (kimlik avı), bir komut
(kullanıcıyı kandırma) ya da kullanıcıya verilmiş bir emir. Çıktıyı bu üç
taşıyıcı için tarayıp reddetmek, saldırının etki yüzeyini kapatır.

Bu kontrol UI'da değil serviste yapılır: UI'ya zaten temiz veri gider (İlke 1
ile aynı mantık).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Bağlantı: asistan link üretemez (spec 6.3). Markdown linki ve çıplak URL.
_URL_RE = re.compile(r"(https?://|www\.|\[[^\]]*\]\([^)]*\))", re.IGNORECASE)

# Kabuk/komut kalıpları: modelin kullanıcıya çalıştırması için komut vermesi.
_COMMAND_RE = re.compile(
    r"\b(curl|wget|rm\s+-rf|sudo|pip\s+install|npm\s+i(nstall)?|powershell|cmd\.exe)\b",
    re.IGNORECASE,
)

# Kullanıcıya emir veren kalıplar. Asistan bilgi verir, yönlendirme yapmaz.
# Dikkat: "şunu yap" gibi ifadeler meşru bir özet içinde de geçebileceği için
# bu kalıplar kasten dar tutulmuştur (yanlış pozitif maliyeti yüksek).
_IMPERATIVE_RE = re.compile(
    r"(hemen\s+(tıkla|gir|indir|gönder|ara)|şu\s+adrese\s+git|bu\s+numarayı\s+ara"
    r"|şifreni\s+(gir|paylaş)|hesabına\s+giriş\s+yap)",
    re.IGNORECASE,
)

# Sistem talimatının sızdığına işaret eden kalıplar.
_SYSTEM_LEAK_RE = re.compile(
    r"(GÜVENLİK KURALI:|<<<VERI_BASLANGIC>>>|<<<VERI_BITIS>>>|sistem talimatım)",
    re.IGNORECASE,
)


@dataclass
class OutputCheck:
    """Çıktı denetimi sonucu."""

    allowed: bool
    violation: str | None = None


def check_output(text: str) -> OutputCheck:
    """Model çıktısını yayımlanabilirlik açısından denetler.

    Returns:
        `allowed=False` ise yanıt kullanıcıya gösterilmez; çağıran modül
        reddetme yanıtı üretir (`refusal_reason="cikti_kisiti"`).

    NEDEN REDDETME, TEMİZLEME DEĞİL: Şüpheli kısmı silip kalanı göstermek,
    saldırganın kısmi kontrolü altındaki bir metni kullanıcıya sunmak demektir.
    Emin olmadığımızda susuyoruz (İlke 2).
    """
    if _SYSTEM_LEAK_RE.search(text):
        return OutputCheck(allowed=False, violation="sistem_sizinti")
    if _URL_RE.search(text):
        return OutputCheck(allowed=False, violation="baglanti")
    if _COMMAND_RE.search(text):
        return OutputCheck(allowed=False, violation="komut")
    if _IMPERATIVE_RE.search(text):
        return OutputCheck(allowed=False, violation="talimat")
    return OutputCheck(allowed=True)
