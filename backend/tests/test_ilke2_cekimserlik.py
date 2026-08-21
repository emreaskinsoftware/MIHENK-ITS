"""İlke 2 — çekimserlik testleri (spec 1 / 6.3 / 6.5 / 8).

Çekimserlik bu projede bir hata durumu değil, ürün davranışıdır: sistem emin
değilse hüküm vermez. Bu testler "susmayı" garanti altına alır.
"""

from __future__ import annotations

from app.assistant import ask
from app.config import config
from app.detection.decision import karar_ver
from app.enrichment import enrich_feed


def test_kisa_metinde_cekimser_kalinir():
    """Token eşiğinin altındaki metinde etiket gösterilmez (spec 6.5)."""
    sonuc = karar_ver("çok kısa", olasilik=0.99)
    assert sonuc.abstained is True
    assert sonuc.label is None, "kısa metinde etiket üretildi"
    assert sonuc.reason == "metin_cok_kisa"


def test_belirsizlik_bandinda_cekimser_kalinir():
    """Model kararsızsa (belirsizlik bandı) etiket gösterilmez."""
    uzun_metin = "kelime " * (config.min_detection_tokens + 10)
    orta_olasilik = (config.abstain_low + config.abstain_high) / 2
    sonuc = karar_ver(uzun_metin, olasilik=orta_olasilik)
    assert sonuc.abstained is True
    assert sonuc.label is None
    assert sonuc.reason == "belirsiz"


def test_band_disinda_etiket_uretilir():
    """Eşiklerin dışında model kararlıysa etiket üretilir."""
    uzun_metin = "kelime " * (config.min_detection_tokens + 10)
    yz = karar_ver(uzun_metin, olasilik=config.abstain_high + 0.2)
    insan = karar_ver(uzun_metin, olasilik=config.abstain_low - 0.2)
    assert yz.label == "yz_olasi" and yz.abstained is False
    assert insan.label == "insan_olasi" and insan.abstained is False


def test_esikler_config_den_okunur(monkeypatch):
    """Eşikler kodda gömülü değil; config değişince davranış değişir (spec 8)."""
    from app.config import get_settings

    monkeypatch.setenv("MIHENK_ABSTAIN_HIGH", "0.99")
    get_settings.cache_clear()
    import importlib

    import app.config as config_modulu
    import app.detection.decision as karar_modulu

    importlib.reload(config_modulu)
    importlib.reload(karar_modulu)
    try:
        uzun = "kelime " * 40
        sonuc = karar_modulu.karar_ver(uzun, olasilik=0.9)
        assert sonuc.abstained is True, "yükseltilen eşik dikkate alınmadı"
    finally:
        monkeypatch.delenv("MIHENK_ABSTAIN_HIGH", raising=False)
        get_settings.cache_clear()
        importlib.reload(config_modulu)
        importlib.reload(karar_modulu)


def test_baglam_disi_soruda_reddedilir(kucuk_akis):
    """Cevap bağlamda yoksa asistan tahmin yürütmez (spec 6.3)."""
    enrich_feed(kucuk_akis.posts)
    yanit = ask(kucuk_akis, "p1", "Dolar kuru bugün kaç lira oldu?")
    assert yanit.refused is True
    assert yanit.refusal_reason == "baglamda_yok"
    assert yanit.source_post_ids == []


def test_baglam_ici_soruda_cevap_verilir(kucuk_akis):
    """Çekimserlik aşırıya kaçmamalı: bağlamdaki soru yanıtlanır."""
    yanit = ask(kucuk_akis, "p1", "Köprü açılışı ertelendi mi?")
    assert yanit.refused is False
    assert yanit.source_post_ids, "yanıt kaynaksız döndü"


def test_cekimserlik_oranı_olculebilir():
    """Çekimserlik bir metriktir: sonuç nesnesi sayılabilir alanlar taşır."""
    sonuclar = [
        karar_ver("kısa", 0.9),
        karar_ver("kelime " * 40, (config.abstain_low + config.abstain_high) / 2),
        karar_ver("kelime " * 40, 0.95),
    ]
    oran = sum(1 for s in sonuclar if s.abstained) / len(sonuclar)
    assert 0.0 <= oran <= 1.0
    assert oran == 2 / 3
