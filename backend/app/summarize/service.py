"""KATMAN 2 — talep anında birleştirme (spec 4.1 / 6.2).

AKIŞ:
  1. Okunmamış gönderilerin HAZIR zenginleştirme kayıtlarını önbellekten çek.
     Eksik olanı senkron üretme, ATLA ve say (akış hızını koru).
  2. Gömmeleri kümele (clustering.py).
  3. Her kümeden merkeze en yakın temsilcileri seç.
  4. TEK LLM çağrısı ile atıflı özet iste.
  5. Atıf denetimi (citation.py) — İlke 1.
  6. Kelime üst sınırını uygula (üreticiyi koruma).

ÇOĞULCULUK KURALLARI (İlke 3), gündem kategorisinde:
  - Tek yazarlı küme için özet ÜRETİLMEZ. Tek kaynaktan beslenen bir olay
    "gündem" değildir; onu gündem gibi sunmak, tek kişinin iddiasını topluma
    mal etmektir.
  - Prompt, taraf pozisyonlarını belirtmeyi zorunlu kılar ve doğruluk hükmü
    vermeyi yasaklar.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from app.config import config
from app.enrichment.worker import get_enriched
from app.llm.prompts import merge_prompt
from app.llm.provider import get_provider
from app.models import EnrichedPost, SummaryResponse, SummarySentence
from app.store.cache import get_cache
from app.summarize.citation import audit_citations
from app.summarize.clustering import Cluster, build_clusters
from app.textutil import word_count

logger = logging.getLogger(__name__)


@dataclass
class SummaryDebug:
    """Ölçüm ve hata ayıklama için ek bilgi (API yanıtında dönmez)."""

    clusters: list[Cluster]
    suppressed_single_author_labels: list[str]
    hallucinated_ids: list[str]
    parse_failed: bool
    llm_calls: int


def _kume_secimi(kumeler: list[Cluster], *, pluralism_required: bool) -> tuple[list[Cluster], list[str]]:
    """Özete girecek kümeleri süzer (İlke 3).

    Returns:
        (özete girecek kümeler, çoğulculuk gereği bastırılan küme etiketleri)
    """
    if not pluralism_required:
        return kumeler, []
    secilen: list[Cluster] = []
    bastirilan: list[str] = []
    for kume in kumeler:
        if len(kume.distinct_authors) < config.min_distinct_authors_for_agenda:
            # Tek kaynaklı küme: gündem özeti üretilmez (spec 6.2 ek kural).
            bastirilan.append(kume.label)
            logger.info(
                "Tek kaynaklı küme bastırıldı: etiket=%s yazar=%s",
                kume.label,
                next(iter(kume.distinct_authors), "?"),
            )
            continue
        secilen.append(kume)
    return secilen, bastirilan


def _kelime_siniri_uygula(cumleler: list[SummarySentence], sinir: int) -> list[SummarySentence]:
    """Toplam kelime sınırını uygular (üreticiyi koruma kuralı, spec 1).

    NEDEN CÜMLE ATIYORUZ, KIRPMIYORUZ: Cümlenin ortasından kesmek, atıfı hâlâ
    duran ama anlamı bozulmuş bir metin üretir. Sınırı aşan cümle tamamen
    çıkarılır; kalanlar bütünlüğünü korur. Özet, orijinal gönderinin yerine
    geçmemeli — kullanıcının kaynağa tıklaması hedeflenen davranıştır.
    """
    toplam = 0
    sonuc: list[SummarySentence] = []
    for cumle in cumleler:
        adet = word_count(cumle.text)
        if toplam + adet > sinir:
            break
        sonuc.append(cumle)
        toplam += adet
    return sonuc


def summarize(
    user_id: str,
    category: str,
    unread_post_ids: list[str],
    *,
    pluralism_required: bool | None = None,
) -> tuple[SummaryResponse, SummaryDebug]:
    """Okunmamış gönderilerden atıflı özet üretir.

    Args:
        user_id: Özet isteyen kullanıcı (önbellek anahtarı ve loglama için).
        category: "gundem" | "spor" | "kisisel".
        unread_post_ids: Kullanıcının okumadığı gönderi ID'leri.
        pluralism_required: İlke 3'ün bu çağrıda uygulanıp uygulanmayacağı.
            None (varsayılan) ise kural kategoriden türetilir ve davranış
            değişmez. Açıkça verildiğinde ÇAĞIRAN sorumludur.

            NEDEN GEÇERSİZ KILINABİLİR: `adhoc.summarize_texts`, kendi kategori
            kümesi olan bir istemciye hizmet ediyor ve orada çoğulculuk kuralı
            yalnızca "gundem" için değil, kişisel akış DIŞINDAKİ her kategori
            için geçerli — yani kuralı gevşetmek için değil, GENİŞLETMEK için
            kullanılıyor. Bu bayrak HTTP gövdesinden okunmaz; okunsaydı çağıran
            tek bir alanla İlke 3'ü kapatabilirdi.

    Returns:
        (SummaryResponse, SummaryDebug)
    """
    baslangic = time.perf_counter()
    onbellek = get_cache()
    isabet_baslangic = (onbellek.hits, onbellek.misses)

    # --- Adım 1: hazır zenginleştirmeleri topla ---
    hazir: list[EnrichedPost] = []
    atlanan = 0
    for post_id in unread_post_ids:
        kayit = get_enriched(post_id)
        if kayit is None:
            # Senkron zenginleştirme YAPMIYORUZ (spec 6.2 adım 1): kullanıcı
            # beklerken akış hızında yapılması gereken işi yapmak, iki katmanlı
            # mimarinin varlık sebebini ortadan kaldırırdı.
            atlanan += 1
            continue
        hazir.append(kayit)

    if not hazir:
        gecikme = int((time.perf_counter() - baslangic) * 1000)
        return (
            SummaryResponse(
                category=category,
                sentences=[],
                cluster_count=0,
                skipped_post_count=atlanan,
                latency_ms=gecikme,
            ),
            SummaryDebug([], [], [], False, 0),
        )

    # --- Adım 2: kümele ---
    kumeler = build_clusters(hazir)
    cogulculuk_gerekli = (
        category == "gundem" if pluralism_required is None else pluralism_required
    )
    secilen_kumeler, bastirilan = _kume_secimi(kumeler, pluralism_required=cogulculuk_gerekli)

    if not secilen_kumeler:
        gecikme = int((time.perf_counter() - baslangic) * 1000)
        return (
            SummaryResponse(
                category=category,
                sentences=[],
                cluster_count=len(kumeler),
                single_source_cluster_count=len(bastirilan),
                skipped_post_count=atlanan,
                latency_ms=gecikme,
            ),
            SummaryDebug(kumeler, bastirilan, [], False, 0),
        )

    # --- Adım 3: temsilcileri seç ---
    prompt_kumeleri: list[tuple[str, list[tuple[str, str]]]] = []
    izin_verilen_idler: set[str] = set()
    for kume in secilen_kumeler:
        temsilciler = kume.representatives()
        ogeler = [(t.post_id, t.atomic_summary) for t in temsilciler]
        izin_verilen_idler.update(t.post_id for t in temsilciler)
        prompt_kumeleri.append((kume.label, ogeler))

    # --- Adım 4: TEK LLM çağrısı ---
    system, user = merge_prompt(category, prompt_kumeleri, pluralism_required=cogulculuk_gerekli)
    saglayici = get_provider()
    try:
        ham = saglayici.complete(system, user, max_tokens=1000)
        llm_cagrisi = 1
    except Exception as hata:
        # Birleştirme başarısızsa boş özet döneriz; uydurma özet üretmeyiz.
        logger.error("Birleştirme çağrısı başarısız: %s", hata)
        ham, llm_cagrisi = "", 1

    # --- Adım 5: atıf denetimi (İlke 1) ---
    rapor = audit_citations(ham, izin_verilen_idler)

    # --- Adım 6: kelime sınırı ---
    cumleler = _kelime_siniri_uygula(rapor.sentences, config.max_summary_words)
    # Sınır yüzünden düşen cümleler atıf ihlali değildir; ayrı sayılır ve
    # dropped_sentence_count'a KATILMAZ (metrik anlamını korumalı).
    gecikme = int((time.perf_counter() - baslangic) * 1000)

    isabet = onbellek.hits - isabet_baslangic[0]
    kacirma = onbellek.misses - isabet_baslangic[1]
    oran = isabet / (isabet + kacirma) if (isabet + kacirma) else 0.0

    yanit = SummaryResponse(
        category=category,
        sentences=cumleler,
        cluster_count=len(secilen_kumeler),
        dropped_sentence_count=rapor.dropped_total,
        single_source_cluster_count=len(bastirilan),
        skipped_post_count=atlanan,
        latency_ms=gecikme,
        cache_hit_ratio=round(oran, 4),
        provider=getattr(saglayici, "name", "bilinmiyor"),
    )
    hata_ayikla = SummaryDebug(
        clusters=secilen_kumeler,
        suppressed_single_author_labels=bastirilan,
        hallucinated_ids=rapor.hallucinated_ids,
        parse_failed=rapor.parse_failed,
        llm_calls=llm_cagrisi,
    )
    logger.info(
        "Özet üretildi user=%s kategori=%s küme=%s cümle=%s silinen=%s gecikme=%sms",
        user_id,
        category,
        len(secilen_kumeler),
        len(cumleler),
        rapor.dropped_total,
        gecikme,
    )
    return yanit, hata_ayikla
