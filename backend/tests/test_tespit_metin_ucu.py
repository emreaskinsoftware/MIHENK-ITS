"""Kimliksiz metin tespiti ucu testleri (`POST /api/tespit`).

NEDEN AYRI UÇ: Arayüz prototipi (`02-prototip/`) kendi simülasyon veri
kümesiyle çalışıyor ve gönderi kimlikleri bu servisinkiyle uyuşmuyor.
Ayrıca kullanıcının henüz paylaşmadığı bir taslağın tanımı gereği kimliği
yoktur. Bu uç ikisini de çözer.

TESTLERİN GÖREVİ: Yeni ucun çekimserlik kurallarını ATLAMADIĞINI garanti
etmek. Kimliğe dayalı uçta uygulanan her kural burada da geçerli olmalı;
aksi hâlde arayüz, ilkeleri baypas eden bir yan kapı bulmuş olur.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import config
from app.main import app

istemci = TestClient(app)


def test_kisa_metinde_cekimser_kalinir():
    """Uzunluk eşiğinin altındaki metinde etiket üretilmez."""
    yanit = istemci.post("/api/tespit", json={"text": "çok kısa"})
    assert yanit.status_code == 200
    veri = yanit.json()
    assert veri["abstained"] is True
    assert veri["label"] is None, "kısa metinde etiket üretildi"
    assert veri["reason"] == "metin_cok_kisa"


def test_uzun_metin_karar_uretir_veya_cekimser_kalir():
    """Uzun metinde ya etiket ya da gerekçeli çekimserlik döner.

    Hangisinin döneceği modelin varlığına ve kalibre banda bağlıdır, o yüzden
    etiketin DEĞERİNİ test etmiyoruz. Test edilen şey sözleşme: yanıt her
    zaman ya bir etiket ya da bir gerekçe taşır, ikisi birden boş kalamaz.
    """
    uzun = "kelime " * (config.min_detection_tokens + 20)
    veri = istemci.post("/api/tespit", json={"text": uzun}).json()
    assert veri["token_count"] >= config.min_detection_tokens
    assert veri["length_bucket"] in ("K1", "K2", "K3")
    if veri["abstained"]:
        assert veri["label"] is None
        assert veri["reason"], "çekimser kalındı ama gerekçe yok"
    else:
        assert veri["label"] in ("yz_olasi", "insan_olasi")


def test_bos_metin_reddedilir():
    """Boş gövde doğrulama hatası verir; sessizce 'insan' varsayılmaz."""
    assert istemci.post("/api/tespit", json={"text": ""}).status_code == 422


def test_asiri_uzun_metin_reddedilir():
    """Üst sınır: model zaten kırpıyor, sınırsız gövde kabul etmiyoruz."""
    assert istemci.post("/api/tespit", json={"text": "a" * 10_001}).status_code == 422


def test_metin_alani_zorunlu():
    assert istemci.post("/api/tespit", json={}).status_code == 422


def test_kimlikli_ve_kimliksiz_uc_ayni_karari_verir():
    """İki uç aynı metinde ayrışmamalı.

    Ayrışırlarsa arayüzün hangi ucu çağırdığına göre kullanıcıya farklı rozet
    gösterilir. Bu, ölçümü de geçersiz kılar: rapor kimlikli uçla ölçülür,
    kullanıcı kimliksiz ucu görür.
    """
    from app.store.feed_repo import load_feed

    depo = load_feed()
    post = next((p for p in depo.posts if len(p.text.split()) > 30), None)
    assert post is not None, "yeterince uzun gönderi bulunamadı"

    kimlikli = istemci.get(f"/api/tespit/{post.id}").json()
    kimliksiz = istemci.post("/api/tespit", json={"text": post.text}).json()
    assert kimlikli == kimliksiz
