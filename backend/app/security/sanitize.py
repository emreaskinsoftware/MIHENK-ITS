"""Güvenilmeyen girdinin temizlenmesi ve enjeksiyon sinyali (spec 6.4, katman 1).

TEHDİT MODELİ ÖZETİ: Gönderi metni ve web içeriği kullanıcıdan değil, ÜÇÜNCÜ
TARAFTAN gelir. Saldırgan gönderiyi yazan kişidir; kurban ise o gönderiyi
özetleten okuyucudur. Yani "kullanıcıya güven" varsayımı burada geçersizdir.

Bu modül tek başına savunma değildir. Kalıp eşleştirme atlatılabilir; asıl
savunma yapısal ayrım (prompt_guard.py) ve çıktı kısıtıdır (output_guard.py).
Buradaki işlevin amacı iki şeydir:
  1) Görünmez karakterlerle gizlenmiş talimatları görünür kılmak,
  2) Şüphe sinyalini ölçülebilir hale getirmek (eval/injection_suite.yaml).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

# Sıfır genişlikli ve yön değiştiren karakterler: gözle görünmez talimat
# gizlemenin en yaygın yolu. Bunları siliyoruz, çünkü meşru Türkçe metinde
# hiçbir işlevleri yok (ZWNJ dahil; Türkçe onu kullanmaz).
_INVISIBLE_RE = re.compile(
    "["
    "​‌‍⁠﻿"  # sıfır genişlikli boşluk/birleştirici
    "‪-‮⁦-⁩"  # çift yönlü metin kontrol karakterleri
    "­"  # yumuşak tire
    "]"
)

# Fazla boşluk/satır: prompt'u aşağı kaydırıp sistem talimatını "unutturma"
# denemelerini etkisizleştirmek için sıkıştırılır.
_WHITESPACE_RE = re.compile(r"[ \t ]{3,}")
_NEWLINES_RE = re.compile(r"\n{3,}")

# Enjeksiyon kalıpları. Türkçe ve İngilizce birlikte taranır: saldırgan modelin
# İngilizce talimatlara daha duyarlı olabileceğini varsayarak İngilizce yazabilir.
_INJECTION_PATTERNS: tuple[tuple[str, str], ...] = (
    ("dogrudan_talimat", r"(önceki|üstteki|yukarıdaki|tüm)\s+(talimat|komut|yönerge)"),
    ("dogrudan_talimat", r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions?"),
    ("dogrudan_talimat", r"(talimatları|kuralları)\s+(yoksay|unut|görmezden gel|boşver)"),
    ("dogrudan_talimat", r"disregard\s+(the\s+)?(rules?|instructions?|system)"),
    ("rol_degistirme", r"(sen\s+artık|bundan\s+sonra\s+sen|şu\s+andan\s+itibaren\s+sen)\b"),
    ("rol_degistirme", r"\b(you\s+are\s+now|act\s+as|pretend\s+to\s+be)\b"),
    ("rol_degistirme", r"\b(dan\s+modu|geliştirici\s+modu|developer\s+mode|jailbreak)\b"),
    ("sistem_sizdirma", r"(sistem\s+(talimat|istem|mesaj)|system\s+prompt)"),
    ("sistem_sizdirma", r"(prompt.?(unu|ını)\s+(yaz|göster|söyle|paylaş))"),
    ("sistem_sizdirma", r"(reveal|print|repeat)\s+(your\s+)?(system|initial)\s+"),
    ("veri_sizdirma", r"(api\s*key|api\s*anahtar|token.?(ını|unu)\s+(yaz|göster))"),
    ("eylem_talebi", r"(şu\s+adrese\s+git|bu\s+linke\s+tıkla|gönder\s+bunu)"),
    ("eylem_talebi", r"\b(curl|wget|rm\s+-rf|http\s+post)\b"),
    ("cikti_yonlendirme", r"(yanıtın(ın)?\s+(başına|sonuna)|cevabına\s+şunu\s+ekle)"),
    ("cikti_yonlendirme", r"(always\s+(say|answer|respond)|her\s+zaman\s+şunu\s+söyle)"),
)

_COMPILED = tuple((ad, re.compile(kalip, re.IGNORECASE)) for ad, kalip in _INJECTION_PATTERNS)


@dataclass
class SanitizeResult:
    """Temizleme çıktısı ve tespit edilen şüphe sinyalleri."""

    text: str
    # Görünmez karakter bulundu mu — tek başına bile güçlü bir sinyaldir,
    # çünkü normal bir gönderide sıfır genişlikli karakter bulunmaz.
    had_invisible: bool = False
    # Eşleşen kalıp adları (tekilleştirilmiş). Boş liste = kalıp tabanlı sinyal yok.
    patterns: list[str] = field(default_factory=list)

    @property
    def suspicious(self) -> bool:
        """Metin enjeksiyon denemesi olarak işaretlensin mi."""
        return bool(self.patterns) or self.had_invisible


def sanitize(text: str) -> SanitizeResult:
    """Güvenilmeyen metni normalize eder ve enjeksiyon sinyali çıkarır.

    Adımlar ve gerekçeleri:
      1. NFKC normalizasyonu — 'ıgnore' benzeri Unicode taklitlerini (homoglif,
         tam genişlikli harfler) kanonik biçime indirger; aksi halde kalıp
         eşleştirme kolayca atlatılır.
      2. Görünmez karakterlerin silinmesi — gizli talimat taşıyıcısıdır.
      3. Aşırı boşluk sıkıştırma — "bağlam taşırma" denemelerini kırar.
      4. Kalıp taraması — sinyal üretir, karar vermez.

    Dikkat: bu fonksiyon metni REDDETMEZ. Reddetme kararı çağıran modüle aittir
    (asistan reddeder, özetleme yalnızca loglar) çünkü şüpheli bir gönderinin
    akıştan tamamen kaybolması sansür etkisi yaratır — biz onu özetleriz ama
    talimatına uymayız.
    """
    normalize_edilmis = unicodedata.normalize("NFKC", text)
    gorunmez_vardi = bool(_INVISIBLE_RE.search(normalize_edilmis))
    temiz = _INVISIBLE_RE.sub("", normalize_edilmis)
    temiz = _WHITESPACE_RE.sub(" ", temiz)
    temiz = _NEWLINES_RE.sub("\n\n", temiz).strip()

    eslesenler: list[str] = []
    for ad, desen in _COMPILED:
        if desen.search(temiz) and ad not in eslesenler:
            eslesenler.append(ad)

    return SanitizeResult(text=temiz, had_invisible=gorunmez_vardi, patterns=eslesenler)
