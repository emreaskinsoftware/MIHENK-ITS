"""Konu etiketleme — KATMAN 1'in ucuz bileşeni (spec 6.1).

NEDEN LLM KULLANMIYORUZ: Konu etiketi, kümeleme sonrası kümeye insan tarafından
okunabilir bir ad vermek ve kategori içi kaba filtreleme için kullanılıyor.
Bu iş için ayrı bir LLM çağrısı yapmak, KATMAN 1'in maliyet mantığını bozar:
akışa düşen HER gönderi için ek çağrı demektir. Sözlük tabanlı etiketleme
maliyetsizdir ve yanlış etiketin bedeli düşüktür (küme adı yanlış olur, özetin
içeriği değil).

Etiket bulunamazsa "diger" döner — uydurma etiket üretmiyoruz (İlke 2'nin küçük
ölçekteki karşılığı).
"""

from __future__ import annotations

import re

from app.llm.embedding import turkish_lower

# Konu -> anahtar kök listesi. Kökler bilinçli olarak EK ALMADAN yazılmıştır;
# Türkçe sondan eklemeli bir dil olduğu için "köprü" kökü "köprünün",
# "köprüde" biçimlerini de yakalar (startswith yerine "içinde geçiyor mu"
# kontrolü yapılır).
KONU_SOZLUGU: dict[str, tuple[str, ...]] = {
    "ulasim": ("köprü", "metro", "otobüs", "trafik", "güzergâh", "güzergah", "durak", "yol", "otopark"),
    "altyapi": ("su kesinti", "boru", "arıza", "kanalizasyon", "elektrik", "altyapı"),
    "egitim": ("okul", "öğrenci", "öğretmen", "yemek", "kütüphane", "sınav", "üniversite"),
    "yerel_yonetim": ("belediye", "kurum", "müdürlüğü", "idare", "başvuru", "kamulaştırma", "pazar yeri"),
    "futbol": ("maç", "gol", "penaltı", "hakem", "derbi", "deplasman", "kaleci", "tribün", "beraber"),
    "kulup": ("transfer", "kulüp", "yönetim", "altyapıdan", "stat", "kadro", "sezon"),
    "gundelik": ("kahve", "kedi", "yürüyüş", "market", "yemek", "kargo", "uyku", "hava"),
    "tuketici": ("fiyat", "zam", "kafe", "servis", "sipariş", "ürün", "kulaklık"),
}

_KELIME_RE = re.compile(r"[\wçğıöşü]+", re.UNICODE)


def topic_label(text: str, category: str) -> str:
    """Metne konu etiketi atar.

    Args:
        text: Gönderi metni (ham veya atomik özet).
        category: Gönderi kategorisi; eşleşme yoksa yedek etiket buradan gelir.

    Yöntem: her konu için sözlükteki köklerin metinde kaç kez geçtiği sayılır,
    en yüksek skorlu konu seçilir. Beraberlikte sözlük sırası belirleyicidir
    (belirlenimci davranış: aynı metin her zaman aynı etiketi alır).
    """
    kucuk = turkish_lower(text)
    en_iyi, en_iyi_skor = "diger", 0
    for konu, kokler in KONU_SOZLUGU.items():
        skor = sum(kucuk.count(kok) for kok in kokler)
        if skor > en_iyi_skor:
            en_iyi, en_iyi_skor = konu, skor
    if en_iyi_skor == 0:
        # Konu çıkarılamadı: kategoriyi etiket olarak kullan. Uydurma bir konu
        # adı üretmek, kullanıcıya olmayan bir yapı varmış izlenimi verirdi.
        return f"{category}_diger"
    return en_iyi


def keywords(text: str, limit: int = 5) -> list[str]:
    """Metnin en uzun anlamlı kelimelerini döndürür (küme adlandırma yedeği).

    Uzunluk basit ama işe yarar bir bilgi taşıyıcılığı ölçütüdür: Türkçe'de
    ekler bilgi taşır ve uzun kelimeler genellikle içerik kelimeleridir.
    """
    kelimeler = {k for k in _KELIME_RE.findall(turkish_lower(text)) if len(k) > 5}
    return sorted(kelimeler, key=len, reverse=True)[:limit]
