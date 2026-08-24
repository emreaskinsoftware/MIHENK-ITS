"""Depoda olmayan gönderiler için atıflı özet (kimliksiz giriş kapısı).

NEDEN BU MODÜL VAR
------------------
`/api/ozetle` yalnızca BACKEND'İN KENDİ akışını özetler: gönderi kimliklerini
`store/feed_repo` üzerinden çözer ve zenginleştirmeyi önbellekte HAZIR bulmayı
bekler. Next.js arayüzü ise kendi simülasyon veri kümesiyle çalışıyor —
kimlikler uyuşmuyor (`ebfc698985c6` ↔ `p0411`) ve o gönderiler backend'in
zenginleştirme kuyruğundan hiç geçmedi. Sonuç: arayüz, projenin ana tezini
(İlke 1 — her cümle kaynağına bağlı) uygulayan koda ERİŞEMİYORDU ve ekranda
atıfsız, yerel bir çıkarımsal özet gösteriyordu.

Bu modül o boşluğu, atıf mantığını arayüzde YENİDEN YAZMADAN kapatır. Metinler
buradan girer, `enrichment` → `clustering` → tek LLM çağrısı → `citation.audit`
zincirinin AYNISINDAN geçer. İki ayrı özetleyici tutmak, ikisinin sessizce
ayrışması ve raporda ölçtüğümüz davranışın kullanıcının gördüğü davranış
olmaması demekti.

KİMLİK ÇAKIŞMASI VE ÖNBELLEK ZEHİRLENMESİ
-----------------------------------------
Zenginleştirme önbelleği `enriched:{post_id}` anahtarını kullanır. Dışarıdan
gelen bir gövde, backend'in gerçek bir gönderi kimliğini kullanarak o gönderinin
önbellek kaydını KENDİ metniyle değiştirebilirdi; sonraki gerçek özet, saldırgan
metniyle üretilirdi. Bu yüzden dışarıdan gelen her gönderi, içeriğinden türetilen
ayrı bir ad alanına yazılır:

    dis:{sha256(id | yazar | metin)[:12]}

`dis:` öneki gerçek kimliklerle çakışmayı imkânsız kılar; içerik özeti ise aynı
gönderi tekrar gönderildiğinde önbelleğin İSABET etmesini sağlar (metin
değişirse anahtar da değişir, bayat özet dönmez). Yanıt üretilirken kimlikler
çağıranın verdiği hâline geri çevrilir — kullanıcı ekranda kendi gönderi
kimliğini görür ve bağlantı çalışır.
"""

from __future__ import annotations

import hashlib
import logging
import time
from datetime import datetime, timezone

from app.enrichment import enrich_feed
from app.models import Post, SummaryResponse
from app.summarize.service import summarize

logger = logging.getLogger(__name__)

# Dış kaynaklı gönderilerin önbellek ad alanı. Backend'in kendi kimlikleri
# ("p0411") bu öneki asla taşımaz, dolayısıyla iki uzay kesişmez.
DIS_ONEK = "dis:"

# `Post.category` üç değerli bir Literal'dır (spec 5.1). Arayüzün kategori
# kümesi daha geniş; burada YALNIZCA zenginleştirmenin konu etiketi için
# gereken eşleme yapılır. Kullanıcıya dönen `category` alanı çağıranın
# gönderdiği özgün adı taşır, bu eşlemeyi değil.
_KATEGORI_ESLEME = {
    "gundem": "gundem",
    "spor": "spor",
    "kisisel": "kisisel",
    # Ekonomi, teknoloji ve kültür de olay merkezli, çok taraflı akışlardır;
    # zenginleştirme açısından gündem gibi davranırlar.
    "ekonomi": "gundem",
    "teknoloji": "gundem",
    "kultur": "gundem",
}


def _anahtar(post_id: str, author_id: str, text: str) -> str:
    """Dış gönderi için çakışmaz, içerik adresli önbellek kimliği üretir."""
    ozet = hashlib.sha256(f"{post_id}\x00{author_id}\x00{text}".encode("utf-8"))
    return f"{DIS_ONEK}{ozet.hexdigest()[:12]}"


def cogulculuk_gerekli_mi(category: str) -> bool:
    """İlke 3'ün bu kategoride uygulanıp uygulanmayacağını söyler.

    Kişisel akış dışındaki her kategoride tek kaynaklı küme bastırılır. Backend'in
    kendi ucu bu kuralı yalnızca "gundem" için uygular; arayüzün ekonomi, spor ve
    teknoloji akışları da olay merkezli olduğu için burada kural DAHA GENİŞ
    tutulmuştur.

    Bu değer istek gövdesinden ALINMAZ: çağıran, kategori adını değiştirerek
    çoğulculuk denetimini kapatabilseydi İlke 3 bir tercih hâline gelirdi.
    """
    return category != "kisisel"


def summarize_texts(
    category: str,
    posts: list[tuple[str, str, str]],
    *,
    user_id: str = "demo",
) -> SummaryResponse:
    """Ham metinlerden atıflı özet üretir.

    Args:
        category: Çağıranın kategori adı; yanıtta aynen geri döner.
        posts: (gonderi_id, yazar_id, metin) üçlüleri. Kimlikler çağıranın
            kendi uzayındadır; backend deposunda bulunmaları gerekmez.
        user_id: Günlük ve önbellek ölçümü için; kalıcı kayıt tutulmaz.

    Returns:
        SummaryResponse — `sentences` içindeki kaynak kimlikleri çağıranın
        verdiği kimliklerdir.

    Not: Gönderiler burada SENKRON zenginleştirilir. `/api/ozetle`'de bunu
    bilinçli olarak yapmıyoruz (spec 6.2 adım 1: akış hızı korunur), çünkü orada
    zenginleştirme akışa düştüğü anda yapılmış olur. Burada gönderiler sisteme
    ilk kez istek anında giriyor; atlamak, her seferinde boş özet döndürmek
    demek olurdu. Bedeli ölçülebilir kalsın diye uç noktada gönderi sayısı
    sınırlıdır.
    """
    # --- Adım 1: ad alanına taşı, sırayı ve tekilliği koru ---
    esleme: dict[str, str] = {}  # iç anahtar -> çağıranın kimliği
    idler: list[str] = []
    ham_gonderiler: list[Post] = []
    simdi = datetime.now(timezone.utc)
    ic_kategori = _KATEGORI_ESLEME.get(category, "gundem")

    for gonderi_id, yazar_id, metin in posts:
        anahtar = _anahtar(gonderi_id, yazar_id, metin)
        if anahtar in esleme:
            # Aynı gönderi iki kez geldi: kümede iki kez sayılmasın.
            continue
        esleme[anahtar] = gonderi_id
        idler.append(anahtar)
        ham_gonderiler.append(
            Post(
                id=anahtar,
                # Yazar kimliği çoğulculuk denetiminin girdisidir (İlke 3):
                # kümedeki farklı yazar sayısı buradan sayılır. Karıştırmıyoruz.
                author_id=yazar_id,
                text=metin,
                created_at=simdi,
                category=ic_kategori,
            )
        )

    # --- Adım 2: zenginleştir (önbellekte varsa çağrı yapılmaz) ---
    zenginlestirme_baslangic = time.perf_counter()
    istatistik = enrich_feed(ham_gonderiler)
    zenginlestirme_ms = int((time.perf_counter() - zenginlestirme_baslangic) * 1000)

    # --- Adım 3: mevcut KATMAN 2 hattını olduğu gibi çalıştır ---
    yanit, hata_ayikla = summarize(
        user_id,
        category,
        idler,
        pluralism_required=cogulculuk_gerekli_mi(category),
    )

    # --- Adım 4: kimlikleri çağıranın uzayına geri çevir ---
    #
    # Eşlemede olmayan bir kimlik kalırsa cümle DÜŞÜRÜLÜR: kullanıcıya
    # çözemediğimiz bir kaynağı göstermek, atıfı doğrulanamaz kılar (İlke 1).
    #
    # Bu dalın normalde ERİŞİLMEZ olması beklenir: `citation.audit` yalnızca
    # izin listesindeki kimlikleri geçiriyor, o liste de `idler`den geliyor ve
    # `idler`in tamamı `esleme` içinde. Yani buraya düşmek bir veri hatası
    # değil, bizim bir hatamızdır — sessizce yutulmaz, uyarı basılır ve
    # düşen cümle sayacına eklenir. Sayaç yalan söylerse ölçüm de söyler.
    cevrilmis = []
    cozulemeyen = 0
    for cumle in yanit.sentences:
        kaynaklar = [esleme[k] for k in cumle.source_post_ids if k in esleme]
        if not kaynaklar:
            cozulemeyen += 1
            logger.warning(
                "Çözülemeyen kaynak kimliği, cümle düşürüldü: %r (kaynaklar=%s)",
                cumle.text[:60],
                cumle.source_post_ids,
            )
            continue
        cevrilmis.append(cumle.model_copy(update={"source_post_ids": kaynaklar}))

    logger.info(
        "Dış özet: kategori=%s gönderi=%s llm=%s küme=%s cümle=%s silinen=%s "
        "bastırılan=%s zenginleştirme=%sms toplam=%sms",
        category,
        len(idler),
        istatistik.llm_calls,
        yanit.cluster_count,
        len(cevrilmis),
        yanit.dropped_sentence_count,
        len(hata_ayikla.suppressed_single_author_labels),
        zenginlestirme_ms,
        zenginlestirme_ms + yanit.latency_ms,
    )

    # --- Adım 5: ölçüm alanlarını BU YOLA göre düzelt ---
    #
    # NEDEN: `summarize()` yalnızca kendi süresini ölçer, çünkü kendi
    # bağlamında (`/api/ozetle`) zenginleştirme çok önce, akış hızında
    # yapılmıştır. BU yolda ise zenginleştirme istek anında ve senkron
    # yapılıyor ve toplam sürenin neredeyse tamamını o kaplıyor:
    # ölçümde 5 ms raporlanırken isteğin kendisi 2.446 ms sürüyordu.
    # 500 kat sapan bir gecikme sayısı, raporlanabilir olmaktan çıkar.
    #
    # `cache_hit_ratio` ise bu yolda ANLAMSIZ: gönderileri özetlemeden hemen
    # önce zenginleştirdiğimiz için önbellek yapı gereği %100 isabet eder.
    # Ölçtüğü bir şey yok; 1.0 yazmak, olmayan bir başarımı raporlamaktır.
    # Alan şemadan kaldırılamaz (aynı model iki uçta da dönüyor), bu yüzden
    # 0.0 verilir ve uç noktanın belgesinde neden olduğu yazılıdır.
    return yanit.model_copy(
        update={
            "sentences": cevrilmis,
            "latency_ms": zenginlestirme_ms + yanit.latency_ms,
            "cache_hit_ratio": 0.0,
            "dropped_sentence_count": yanit.dropped_sentence_count + cozulemeyen,
        }
    )
