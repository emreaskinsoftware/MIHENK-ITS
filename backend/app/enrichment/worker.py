"""KATMAN 1 — eşzamansız zenginleştirme işçisi (spec 4.1 / 6.1).

BU KATMANIN VARLIK SEBEBİ (mimarinin kalbi): Kullanıcı "Özetle" dediğinde 200
gönderiyi tek prompt'a doldurmak p95 gecikmeyi 20 saniyenin üstüne çıkarır ve
maliyeti kullanıcı sayısıyla doğrusal büyütür. Bunun yerine gönderi akışa
düştüğü anda (kullanıcıdan bağımsız) atomik özeti ve gömmesi üretilir. Bu
çıktı kullanıcılar ARASINDA paylaşılır: aynı gönderiyi 1000 kişi görse de
zenginleştirme bir kez yapılır.

Bu dosyada Celery yoktur; işçi arayüzü senkron bir fonksiyondur ve
`enrich_feed()` toplu çalıştırma yapar. NEDEN: Celery+Redis kurulumu demo
riskini artırıyor ve tek makinede tek işçi zaten yeterli (spec 3: "yerel
geliştirmede tek işçi yeterli"). Kuyruk davranışının önemli olan kısmı —
yeniden deneme sınırı ve sonsuz döngü koruması — burada uygulanmıştır.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.config import config
from app.enrichment.topics import keywords, topic_label
from app.llm.prompts import atomic_summary_prompt
from app.llm.provider import get_provider
from app.models import EnrichedPost, Post
from app.security.sanitize import sanitize
from app.store.cache import get_cache
from app.textutil import split_sentences, truncate_words

logger = logging.getLogger(__name__)

# Önbellek anahtarı biçimi (spec 6.1): enriched:{post_id}
KEY_PREFIX = "enriched:"


def cache_key(post_id: str) -> str:
    """Gönderi için önbellek anahtarı."""
    return f"{KEY_PREFIX}{post_id}"


@dataclass
class EnrichmentStats:
    """Toplu zenginleştirme sayaçları — maliyet tablosunun girdisi (spec 7)."""

    processed: int = 0
    cached_skipped: int = 0  # Zaten önbellekte olduğu için işlenmeyen
    llm_calls: int = 0  # Gerçekten LLM'e giden çağrı sayısı
    short_post_skips: int = 0  # Kısa olduğu için özet çağrısı yapılmayan
    failures: int = 0
    injection_flagged: int = 0  # Enjeksiyon sinyali taşıyan gönderi sayısı
    failed_ids: list[str] = field(default_factory=list)

    @property
    def llm_call_saving_ratio(self) -> float:
        """Kaç gönderide LLM çağrısından tasarruf edildi (oran).

        Bu sayı raporun maliyet bölümünde doğrudan kullanılır: kısa gönderi
        kuralı ve önbellek paylaşımı sayesinde çağrı sayısı gönderi sayısından
        küçüktür.
        """
        toplam = self.processed + self.cached_skipped
        return 1.0 - (self.llm_calls / toplam) if toplam else 0.0


def _atomik_ozet_uret(post: Post) -> tuple[str, bool, int]:
    """Gönderi için atomik özeti üretir.

    Returns:
        (özet, özet_atlandı_mı, yapılan_llm_çağrısı_sayısı)

    KISA GÖNDERİ KURALI (spec 6.1): 15 kelimeden kısa gönderide özet üretmeyiz;
    metnin kendisi zaten özettir. Özet üretmek hem anlamsız (özet metinden uzun
    olabilir) hem de maliyetlidir. Sosyal medyada gönderilerin büyük bölümü bu
    sınırın altındadır, dolayısıyla bu kural maliyet üzerinde en büyük etkiye
    sahip tek karardır.
    """
    if post.word_count < config.min_words_for_summary:
        return sanitize(post.text).text, True, 0

    saglayici = get_provider()
    system, user = atomic_summary_prompt(post.id, post.text)

    son_hata: Exception | None = None
    for deneme in range(config.enrichment_max_retries):
        try:
            ham = saglayici.complete(system, user, max_tokens=200)
            break
        except Exception as hata:  # ağ/servis hatası
            son_hata = hata
            logger.warning(
                "Zenginleştirme denemesi başarısız (%s/%s) post=%s: %s",
                deneme + 1,
                config.enrichment_max_retries,
                post.id,
                hata,
            )
    else:
        # Sonsuz döngü koruması (spec 6.1): deneme hakkı bitti, gönderi kuyrukta
        # sonsuza kadar dönmez. Hata yukarı bildirilir, çağıran sayaca yazar.
        raise RuntimeError(f"post={post.id} zenginleştirilemedi") from son_hata

    # Çıktı kısıtları: en fazla N cümle ve N kelime. Model kuralı çiğnerse
    # kırpma servis katmanında yapılır — UI'ya zaten kurallı veri gider.
    cumleler = split_sentences(ham)[: config.atomic_summary_max_sentences]
    ozet = truncate_words(" ".join(cumleler) or ham, config.atomic_summary_max_words)
    return ozet, False, 1


def enrich_post(post: Post, *, force: bool = False) -> tuple[EnrichedPost, bool]:
    """Tek gönderiyi zenginleştirir ve önbelleğe yazar.

    Args:
        post: Ham gönderi.
        force: True ise önbellekteki kayıt yok sayılır (yeniden üretim).

    Returns:
        (EnrichedPost, önbellekten_mi_geldi)

    Enjeksiyon notu: Şüpheli metin BURADA REDDEDİLMEZ, yalnızca loglanır ve
    etiketlenir. Sebebi spec 6.4'te: şüpheli bir gönderiyi akıştan tamamen
    çıkarmak sansür etkisi yaratır. Biz onu özetleriz ama talimatına uymayız —
    talimata uymamayı sağlayan şey prompt_guard'daki yapısal ayrımdır.
    """
    onbellek = get_cache()
    anahtar = cache_key(post.id)
    if not force:
        mevcut = onbellek.get(anahtar)
        if mevcut is not None:
            return EnrichedPost.model_validate(mevcut), True

    ozet, atlandi, _ = _atomik_ozet_uret(post)
    saglayici = get_provider()
    # Gömme ham metinden üretilir, özetten değil: özet bilgi kaybeder ve
    # kümeleme kalitesi düşer. Maliyet farkı yok (gömme yereldir).
    gomme = saglayici.embed([sanitize(post.text).text])[0]

    zenginlestirilmis = EnrichedPost(
        post_id=post.id,
        author_id=post.author_id,
        atomic_summary=ozet,
        embedding=gomme,
        topic_label=topic_label(post.text, post.category),
        enriched_at=datetime.now(timezone.utc),
        summary_skipped=atlandi,
        provider=getattr(saglayici, "name", "bilinmiyor"),
        tags=keywords(post.text),
    )
    onbellek.set(anahtar, zenginlestirilmis.model_dump(mode="json"), ttl_s=config.enrichment_ttl_s)
    return zenginlestirilmis, False


def enrich_feed(posts: list[Post], *, force: bool = False) -> EnrichmentStats:
    """Akıştaki gönderileri toplu zenginleştirir.

    Hata alan gönderi tüm partiyi düşürmez: sayaca yazılır ve devam edilir.
    Akış hızını korumak, tek bir gönderiyi kurtarmaktan önemlidir.
    """
    istatistik = EnrichmentStats()
    for post in posts:
        sinyal = sanitize(post.text)
        if sinyal.suspicious:
            istatistik.injection_flagged += 1
            logger.info("Enjeksiyon sinyali post=%s kalıplar=%s", post.id, sinyal.patterns)
        try:
            zenginlestirilmis, onbellekten = enrich_post(post, force=force)
        except Exception:
            istatistik.failures += 1
            istatistik.failed_ids.append(post.id)
            continue
        if onbellekten:
            istatistik.cached_skipped += 1
            continue
        istatistik.processed += 1
        if zenginlestirilmis.summary_skipped:
            istatistik.short_post_skips += 1
        else:
            istatistik.llm_calls += 1
    return istatistik


def get_enriched(post_id: str) -> EnrichedPost | None:
    """Önbellekten zenginleştirilmiş kaydı okur; yoksa None.

    KATMAN 2 bu fonksiyonu kullanır ve None dönen gönderiyi ATLAR — senkron
    zenginleştirme yapmaz (spec 6.2 adım 1). Akış hızını korumak, tek bir
    gönderinin özete girmesinden önemlidir.
    """
    ham = get_cache().get(cache_key(post_id))
    return EnrichedPost.model_validate(ham) if ham is not None else None
