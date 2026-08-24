"""`/api/ozetle/metinler` — depoda olmayan metinler için atıflı özet.

Bu uç, Next.js arayüzünün İlke 1'e (atıf zorunluluğu) erişmesini sağlıyor.
Testler ürünün İDDİASINI sınar, uygulamanın ayrıntısını değil:

  1. Dönen her cümlenin kaynağı vardır ve kaynak ID'leri İSTEKTE GÖNDERİLEN
     kimliklerdir (iç ad alanı sızmaz, uydurma kimlik geçmez).
  2. Tek yazarlı küme bastırılır (İlke 3) ve bu, boş özetle sonuçlansa bile
     hata değildir.
  3. Dışarıdan gelen gövde, backend'in KENDİ gönderisinin zenginleştirme
     kaydını ezemez (önbellek zehirlenmesi).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.enrichment import enrich_post, get_enriched
from app.main import app
from app.store.feed_repo import load_feed

# Aynı olayı üç farklı yazarın anlattığı gövde: çoğulculuk denetimini geçer.
UC_YAZARLI = [
    {
        "id": "arayuz-1",
        "author_id": "kul-1",
        "text": "Sehir merkezindeki kopru projesinde ihale suresi iki hafta uzatildi.",
    },
    {
        "id": "arayuz-2",
        "author_id": "kul-2",
        "text": "Kopru ihalesinin uzatilmasi elestirildi, maliyetin artacagi one suruldu.",
    },
    {
        "id": "arayuz-3",
        "author_id": "kul-3",
        "text": "Yerel yonetim kopru ihalesindeki uzatmanin gerekcesi olarak evrak eksigini gosterdi.",
    },
]


def test_her_cumle_istekte_gonderilen_bir_kimlige_baglanir() -> None:
    """İlke 1: atıfsız cümle dönmez; atıflar çağıranın kimlik uzayındadır."""
    istemci = TestClient(app)
    yanit = istemci.post(
        "/api/ozetle/metinler", json={"category": "gundem", "posts": UC_YAZARLI}
    )
    assert yanit.status_code == 200
    veri = yanit.json()

    gonderilen = {g["id"] for g in UC_YAZARLI}
    assert veri["sentences"], "üç farklı yazarlı küme için özet beklenirdi"
    for cumle in veri["sentences"]:
        assert cumle["source_post_ids"], "atıfsız cümle kullanıcıya gösterilemez"
        # İç ad alanı ("dis:...") dışarı sızmamalı; her kaynak istemcinin
        # gönderdiği bir kimlik olmalı ki arayüzdeki bağlantı çalışsın.
        assert set(cumle["source_post_ids"]) <= gonderilen


def test_tek_yazarli_kume_bastirilir() -> None:
    """İlke 3: tek kaynaktan beslenen içerik gündem gibi sunulmaz.

    Boş `sentences` burada BAŞARIDIR, hata değil — sayaç bunu görünür kılar.
    """
    istemci = TestClient(app)
    tek_yazar = [
        {"id": "tek-1", "author_id": "yalniz", "text": UC_YAZARLI[0]["text"]},
        {"id": "tek-2", "author_id": "yalniz", "text": UC_YAZARLI[2]["text"]},
    ]
    veri = istemci.post(
        "/api/ozetle/metinler", json={"category": "gundem", "posts": tek_yazar}
    ).json()

    assert veri["single_source_cluster_count"] >= 1
    assert veri["sentences"] == []


def test_kisisel_kategoride_cogulculuk_aranmaz() -> None:
    """Kişisel akış gündem değildir: tek yazarlı içerik bastırılmaz."""
    istemci = TestClient(app)
    tek_yazar = [
        {"id": "kis-1", "author_id": "yalniz", "text": UC_YAZARLI[0]["text"]},
        {"id": "kis-2", "author_id": "yalniz", "text": UC_YAZARLI[2]["text"]},
    ]
    veri = istemci.post(
        "/api/ozetle/metinler", json={"category": "kisisel", "posts": tek_yazar}
    ).json()

    assert veri["single_source_cluster_count"] == 0


def test_dis_govde_gercek_gonderinin_onbellegini_ezemez() -> None:
    """Önbellek zehirlenmesi: dış kimlikler ayrı ad alanına yazılır.

    Saldırgan, backend'in gerçek bir gönderi kimliğini kendi metniyle
    gönderirse o gönderinin zenginleştirme kaydı değişmemelidir; aksi hâlde
    sonraki GERÇEK özet saldırganın metniyle üretilirdi.
    """
    depo = load_feed()
    hedef = depo.posts[0]
    # Uygulamanın açılış kancasına (lifespan) güvenmiyoruz: TestClient bağlam
    # yöneticisi olarak kullanılmadığında o kanca çalışmaz ve test, ölçmek
    # istediği şey yerine kurulum eksiğini ölçerdi.
    onceki, _ = enrich_post(hedef)

    istemci = TestClient(app)
    istemci.post(
        "/api/ozetle/metinler",
        json={
            "category": "gundem",
            "posts": [
                {
                    "id": hedef.id,
                    "author_id": "saldirgan",
                    "text": "Bu metin gercek gonderinin yerine gecmeye calisiyor.",
                },
                # İkinci yazar, kümenin çoğulculuk denetimini geçmesi için.
                {"id": "yan", "author_id": "kul-2", "text": UC_YAZARLI[1]["text"]},
            ],
        },
    )

    sonraki = get_enriched(hedef.id)
    assert sonraki is not None
    assert sonraki.atomic_summary == onceki.atomic_summary
    assert sonraki.author_id == onceki.author_id


def test_bos_gonderi_listesi_reddedilir() -> None:
    """Sözleşme doğrulaması: özetlenecek metin yoksa istek geçersizdir."""
    istemci = TestClient(app)
    yanit = istemci.post("/api/ozetle/metinler", json={"category": "gundem", "posts": []})
    assert yanit.status_code == 422
