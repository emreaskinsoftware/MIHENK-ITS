"""Veri yönetişim testleri (spec 5.3 / 8).

Bu testler, raporun 6.2 bölümündeki KVKK uyumlu tasarım iddiasının kod
karşılığını doğrular. Jüri "bunu nerede uyguluyorsunuz" diye sorarsa cevap
bu dosya ve app/governance/ paketidir.
"""

from __future__ import annotations

import time

import pytest

from app.governance import (
    ConsentError,
    aggregate_with_k_threshold,
    assert_consent,
    contains_pii,
    filter_for_training,
    forget_user,
    mask_pii,
    purge_expired,
)
from app.governance.retention import PREFIX_READ_STATE
from app.store.cache import get_cache


# ----------------------------------------------------------------------
# PII maskeleme
# ----------------------------------------------------------------------
@pytest.mark.parametrize(
    "metin,beklenen_etiket",
    [
        ("Bana ornek.kisi@ornek.com adresinden yazın", "EPOSTA"),
        ("Numaram 0532 111 22 33, arayın", "TELEFON"),
        ("Detaylar https://ornek.test/sayfa adresinde", "URL"),
        ("Hesap: TR33 0006 1005 1978 6457 8413 26", "IBAN"),
        ("@kullanici_adi bunu görmeli", "KULLANICI"),
    ],
)
def test_pii_maskelenir(metin: str, beklenen_etiket: str):
    """Kişisel veri kalıpları yer tutucuyla değiştirilir."""
    sonuc = mask_pii(metin)
    assert f"[{beklenen_etiket}]" in sonuc.text
    assert sonuc.counts.get(beklenen_etiket, 0) >= 1
    assert not contains_pii(sonuc.text), "maskeleme sonrası hâlâ kişisel veri var"


def test_maskelemede_cumle_yapisi_korunur():
    """Silme değil yer tutucu: metin okunabilir kalmalı."""
    sonuc = mask_pii("Sorularınız için ornek@test.com adresine yazabilirsiniz.")
    assert sonuc.text.startswith("Sorularınız için")
    assert sonuc.text.endswith("adresine yazabilirsiniz.")


def test_temiz_metin_degismez():
    """Yanlış pozitif kontrolü: sıradan metin bozulmamalı."""
    metin = "Köprü açılışı üçüncü kez ertelendi, esnaf tepkili."
    sonuc = mask_pii(metin)
    assert sonuc.text == metin
    assert sonuc.masked_any is False


# ----------------------------------------------------------------------
# İzin kapısı
# ----------------------------------------------------------------------
def test_izinsiz_kayit_egitim_havuzuna_giremez():
    """Varsayılan reddetme: alan yoksa veya False ise kayıt alınmaz."""
    kayitlar = [
        {"id": "1", "text": "a", "training_consent": True},
        {"id": "2", "text": "b", "training_consent": False},
        {"id": "3", "text": "c"},  # alan yok
        {"id": "4", "text": "d", "training_consent": "true"},  # dizge: reddedilir
    ]
    sonuc = filter_for_training(kayitlar)
    assert [k["id"] for k in sonuc.accepted] == ["1"]
    assert sonuc.rejected_missing_field == 1
    assert sonuc.rejected_no_consent == 2
    assert sonuc.rejected_total == 3


def test_assert_consent_hata_firlatir():
    """Sert kapı: izinsiz kayıt hattı durdurur."""
    with pytest.raises(ConsentError):
        assert_consent({"id": "9", "text": "x"})


# ----------------------------------------------------------------------
# k eşikli toplulaştırma
# ----------------------------------------------------------------------
def test_toplulastirma_k_esigi_altinda_dondurmez():
    """Eşiğin altındaki grup sonuçta HİÇ görünmez (anahtarı bile)."""
    kayitlar = [{"sehir": "A", "kisi": f"u{i}"} for i in range(25)]
    kayitlar += [{"sehir": "B", "kisi": f"v{i}"} for i in range(3)]

    sonuc = aggregate_with_k_threshold(
        kayitlar, key_fn=lambda r: r["sehir"], identity_fn=lambda r: r["kisi"], k=20
    )
    assert "A" in sonuc.groups
    assert "B" not in sonuc.groups, "eşik altındaki grup döndürüldü"
    assert sonuc.suppressed_group_count == 1
    assert sonuc.suppressed_item_count == 3


def test_toplulastirmada_kisi_sayisi_esas_alinir():
    """Aynı kişinin çok kaydı grubu eşiğin üstüne çıkarmamalı.

    k-anonimlik kişi sayısıyla ilgilidir; tek kişinin 40 gönderisi hâlâ tek
    kişidir ve o grubu göstermek doğrudan tekilleştirme olur.
    """
    kayitlar = [{"konu": "X", "kisi": "tek_kisi"} for _ in range(40)]
    sonuc = aggregate_with_k_threshold(
        kayitlar, key_fn=lambda r: r["konu"], identity_fn=lambda r: r["kisi"], k=20
    )
    assert sonuc.groups == {}
    assert sonuc.suppressed_group_count == 1


def test_k_esigi_configden_gelir():
    """Eşik kodda gömülü değil (spec 8)."""
    from app.config import config

    kayitlar = [{"g": "A", "k": f"u{i}"} for i in range(config.aggregation_k_threshold)]
    sonuc = aggregate_with_k_threshold(kayitlar, key_fn=lambda r: r["g"], identity_fn=lambda r: r["k"])
    assert sonuc.k == config.aggregation_k_threshold
    assert "A" in sonuc.groups


# ----------------------------------------------------------------------
# Saklama sınırı
# ----------------------------------------------------------------------
def test_suresi_dolan_kayit_okunamaz_ve_temizlenir():
    """TTL gerçekten uygulanır: süre dolunca kayıt hem okunamaz hem silinir."""
    onbellek = get_cache()
    onbellek.set("enriched:gecici", {"a": 1}, ttl_s=1)
    assert onbellek.get("enriched:gecici") is not None

    # Zamanı beklemek yerine kaydın son kullanma anını geriye çekiyoruz:
    # test süresi uzamasın (bir saniye beklemek 100 testte 100 saniyedir).
    onbellek._veri["enriched:gecici"].expires_at = time.time() - 1

    assert onbellek.get("enriched:gecici") is None, "süresi dolan kayıt okunabildi"


def test_purge_expired_okunmayan_kayitlari_da_siler():
    """Hiç okunmayan süresi dolmuş kayıt bellekte kalmamalı."""
    onbellek = get_cache()
    onbellek.set("enriched:a", 1, ttl_s=1)
    onbellek.set("enriched:b", 2, ttl_s=1)
    onbellek.set("enriched:c", 3, ttl_s=3600)
    for anahtar in ("enriched:a", "enriched:b"):
        onbellek._veri[anahtar].expires_at = time.time() - 1

    rapor = purge_expired()
    assert rapor.removed == 2
    assert rapor.remaining == 1


def test_kullanici_durumu_silinebilir():
    """Unutulma hakkı: kullanıcıya ait durum tek çağrıyla silinir."""
    onbellek = get_cache()
    onbellek.set(f"{PREFIX_READ_STATE}u1:gundem", ["p1"], ttl_s=3600)
    onbellek.set(f"{PREFIX_READ_STATE}u1:spor", ["p2"], ttl_s=3600)
    onbellek.set(f"{PREFIX_READ_STATE}u2:gundem", ["p3"], ttl_s=3600)

    silinen = forget_user("u1")
    assert silinen == 2
    assert onbellek.get(f"{PREFIX_READ_STATE}u2:gundem") is not None
