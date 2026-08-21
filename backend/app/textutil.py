"""Türkçe metin yardımcıları — cümleleme, kelime/token sayımı, kısaltma.

NEDEN AYRI MODÜL: Aynı işlemler zenginleştirme, özetleme, tespit ve ölçüm
tarafında tekrarlanıyor. Farklı yerlerde farklı cümleleme kullanmak, "en fazla
2 cümle" gibi kuralların modülden modüle farklı davranmasına yol açardı.

Türkçe'ye özgü iki tuzağa dikkat edilmiştir:
  1. `str.lower()` Türkçe'de yanlıştır (I/ı, İ/i) — turkish_lower kullanılır.
  2. Kısaltmalar ("vb.", "Dr.", "TL.") cümle sonu sanılırsa cümle sayısı şişer.
"""

from __future__ import annotations

import re

from app.llm.embedding import turkish_lower

__all__ = ["turkish_lower", "split_sentences", "word_count", "count_tokens", "truncate_words"]

# Cümle sonu adayı: nokta/soru/ünlem + boşluk + büyük harf (veya metin sonu).
_SENTENCE_END_RE = re.compile(r"(?<=[.!?…])\s+(?=[A-ZÇĞİÖŞÜ0-9\"'(])")

# Cümle sonu SAYILMAYACAK kısaltmalar. Liste kısa tutuldu: sentetik akışta ve
# haber dilinde en sık geçenler. Genişletilebilir.
_ABBREVIATIONS = ("vb", "vs", "dr", "prof", "doç", "sn", "av", "no", "bkz", "örn", "tl", "hz")


def split_sentences(text: str) -> list[str]:
    """Metni cümlelere ayırır.

    Basit ama Türkçe kısaltmalara karşı korumalı bir bölücü. Ağır bir NLP
    bağımlılığı (spaCy/stanza) eklemiyoruz: bu iş için maliyeti değmez ve
    kurulum yükü demoyu zorlaştırır.
    """
    if not text.strip():
        return []
    parcalar = _SENTENCE_END_RE.split(text.strip())

    # Kısaltma düzeltmesi: bir parça kısaltmayla bitiyorsa sonrakiyle birleştir.
    birlesik: list[str] = []
    for parca in parcalar:
        onceki_kisaltma = False
        if birlesik:
            son_kelime = turkish_lower(birlesik[-1].split()[-1].rstrip(".")) if birlesik[-1].split() else ""
            onceki_kisaltma = son_kelime in _ABBREVIATIONS
        if onceki_kisaltma:
            birlesik[-1] = f"{birlesik[-1]} {parca}"
        else:
            birlesik.append(parca)
    return [c.strip() for c in birlesik if c.strip()]


def word_count(text: str) -> int:
    """Kelime sayısı."""
    return len(text.split())


def count_tokens(text: str) -> int:
    """Kaba token sayısı.

    NEDEN KABA SAYIM: Tespit eşiği (config.min_detection_tokens) için gereken
    şey mutlak doğruluk değil, tutarlılıktır. Gerçek tokenizer kullanmak,
    tespit modeli değiştiğinde eşiğin anlamını değiştirirdi. Burada token =
    kelime + noktalama grubu olarak tanımlıdır ve tüm modüllerde aynıdır.

    Not: Tespit modeli eğitilirken kendi tokenizer'ı kullanılır; bu fonksiyon
    yalnızca ÇEKİMSERLİK EŞİĞİ ve uzunluk kovası için kullanılır (spec 5.2).
    """
    return len(re.findall(r"[\wçğıöşüÇĞİÖŞÜ]+|[^\w\s]", text, re.UNICODE))


def truncate_words(text: str, max_words: int) -> str:
    """Metni kelime sınırına kırpar; kırpılmışsa üç nokta ekler."""
    kelimeler = text.split()
    if len(kelimeler) <= max_words:
        return text
    return " ".join(kelimeler[:max_words]).rstrip(",;:") + "…"
