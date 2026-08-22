"""FastAPI giriş noktası (spec 4.2).

TASARIM KURALI: Bu katman İNCE olmalıdır. İş mantığı servis modüllerindedir;
burada yalnızca istek doğrulama, servis çağrısı ve yanıt biçimlendirme vardır.
Sebebi ölçümdür: `ml/scripts/evaluate.py` servis fonksiyonlarını doğrudan
çağırır. Mantık uç noktalara sızsaydı, ölçtüğümüz kod ile kullanıcının
çalıştırdığı kod farklı olurdu.

İLKELER BU KATMANDA DEĞİL, SERVİSTE UYGULANIR:
  - Atıf denetimi -> summarize/citation.py
  - Çekimserlik   -> detection/decision.py, assistant/service.py
  - Çoğulculuk    -> summarize/service.py
UI'ya zaten temiz veri gider; buradaki hiçbir uç nokta ilke kontrolü yapmaz.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, Literal

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.assistant import ask
from app.config import config
from app.detection.service import detect
from app.enrichment import enrich_feed, get_enriched
from app.governance.retention import PREFIX_READ_STATE, forget_user, purge_expired
from app.models import AssistantResponse, DetectionResult, SummaryResponse
from app.provenance import check_media
from app.store.cache import get_cache
from app.store.feed_repo import load_feed
from app.summarize import summarize, summarize_texts

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Açılışta akışı yükler ve zenginleştirmeyi başlatır.

    NEDEN AÇILIŞTA: KATMAN 1 akış hızında, kullanıcıdan bağımsız çalışır.
    Demo tek süreçte koştuğu için "akışa düşen gönderi" anını uygulama
    açılışıyla eşliyoruz. Gerçek dağıtımda bu iş kuyruğa alınır ve işçiler
    tarafından yapılır; arayüz aynı kalır.
    """
    depo = load_feed()
    logger.info("Akış yüklendi: %s gönderi", len(depo))
    istatistik = enrich_feed(depo.posts)
    logger.info(
        "Zenginleştirme bitti: işlenen=%s llm_çağrısı=%s kısa_atlama=%s enjeksiyon_sinyali=%s",
        istatistik.processed,
        istatistik.llm_calls,
        istatistik.short_post_skips,
        istatistik.injection_flagged,
    )
    yield


app = FastAPI(
    title="MİHENK API",
    description=(
        "Sosyal medya akışını kısaltan, söylediği her cümleyi kaynağına bağlayan, "
        "emin olmadığında susan yapay zekâ katmanı."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# Geliştirme sunucuları farklı portlarda çalışıyor:
#   5173 -> frontend/ (Vite referans arayüzü)
#   3000 -> 02-prototip/ (Next.js jüri prototipi)
# İki arayüz de aynı servisi tüketiyor; ikisi de listede olmak zorunda.
# Liste AÇIKÇA yazılıdır, joker (*) kullanılmaz: joker origin, tarayıcının
# aynı-köken korumasını tamamen kaldırır ve üretime sızarsa herhangi bir
# sitenin bu servise kullanıcı adına istek atmasına izin verir.
# NOT: Üretimde bu liste gerçek alan adıyla değiştirilir.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
# Şemalar
# ----------------------------------------------------------------------
class PostView(BaseModel):
    """Akış kartında gösterilen gönderi.

    `_eval_*` alanları burada YOKTUR ve olamaz: veri `Post.to_service_dict()`
    üzerinden gelir (bkz. tests/test_eval_sizinti.py).
    """

    id: str
    author_id: str
    text: str
    created_at: str
    category: str
    media: list[dict[str, Any]] = Field(default_factory=list)
    atomic_summary: str | None = None
    topic_label: str | None = None


class SummarizeRequest(BaseModel):
    """Özet isteği."""

    user_id: str = "demo"
    category: Literal["gundem", "spor", "kisisel"]
    # Okunmamış gönderi listesi istemciden gelir. NEDEN: okuma durumu kullanıcı
    # cihazında tutulur; sunucu tarafında kalıcı okuma geçmişi saklamak, saklama
    # sınırı ilkesine (spec 5.3) aykırı olurdu.
    unread_post_ids: list[str] | None = None


class HamGonderi(BaseModel):
    """Depoda bulunmayan, istemcinin kendi akışından gelen tek gönderi.

    `author_id` ZORUNLUDUR ve boş geçilemez: çoğulculuk denetimi (İlke 3)
    kümedeki FARKLI YAZAR sayısını sayar. Hepsi aynı sabit değeri taşısaydı her
    küme tek kaynaklı görünür ve özet hiç üretilmezdi; boş bırakılıp istemci
    tarafında uydurulsaydı da tam tersi olur, tek kişinin iddiası çok sesli
    gibi görünürdü.
    """

    id: str = Field(min_length=1, max_length=64)
    author_id: str = Field(min_length=1, max_length=64)
    text: str = Field(min_length=1, max_length=10000)


class MetinOzetRequest(BaseModel):
    """Kimliksiz atıflı özet isteği.

    `posts` üst sınırı kasıtlıdır. Bu uçta gönderiler istek anında SENKRON
    zenginleştirilir; kümeleme de O(N²) mesafe matrisi kurar. Sınırsız bir
    liste, tek istekle hem gecikmeyi hem LLM çağrı sayısını kullanıcı başına
    büyütürdü; KATMAN 1/KATMAN 2 ayrımı tam olarak bunu önlemek için var.

    `category` serbest metindir çünkü istemcinin kategori kümesi backend'in üç
    değerli kümesinden geniş. Çoğulculuk kuralı bu alandan TÜRETİLİR, istek
    gövdesinden okunmaz (bkz. summarize.adhoc.cogulculuk_gerekli_mi).
    """

    user_id: str = "demo"
    category: str = Field(min_length=1, max_length=32)
    posts: list[HamGonderi] = Field(min_length=1, max_length=80)


class AskRequest(BaseModel):
    """Asistan isteği."""

    post_id: str
    question: str | None = None


class DetectRequest(BaseModel):
    """Serbest metin tespit isteği (kimliksiz).

    Uzunluk sınırı kasıtlıdır: tespit modeli `detection_max_length` jetonda
    kırpıyor, bunun çok üstündeki bir gövde yalnızca ağ ve bellek harcar.
    Alt sınır yok — kısa metin hata değildir, karar katmanı zaten
    `metin_cok_kisa` gerekçesiyle çekimser kalır.
    """

    text: str = Field(min_length=1, max_length=10000)


class AppealRequest(BaseModel):
    """YZ sinyaline itiraz (spec 6.9, itiraz akışı)."""

    post_id: str
    reason: str = Field(min_length=1, max_length=1000)
    contact: str | None = None


# ----------------------------------------------------------------------
# Uç noktalar
# ----------------------------------------------------------------------
@app.get("/api/saglik")
def saglik() -> dict[str, Any]:
    """Sistem durumu — demo öncesi hızlı kontrol için.

    Hangi sağlayıcı ve modellerin etkin olduğunu gösterir; jüri demosunda
    "hangi modelle çalışıyor" sorusuna tek çağrıyla cevap verir.
    """
    from app.detection.detector import get_detector
    from app.llm.embedding import get_embedder
    from app.llm.provider import get_provider

    tespit = get_detector()
    return {
        "durum": "calisiyor",
        "llm_saglayici": getattr(get_provider(), "name", "?"),
        "gomme_modeli": getattr(get_embedder(), "name", "?"),
        "tespit_modeli": getattr(tespit, "name", None),
        "onbellek_kayit": len(get_cache()),
        "onbellek_isabet_orani": round(get_cache().hit_ratio, 4),
        "esikler": {
            "min_detection_tokens": config.min_detection_tokens,
            "abstain_band": [config.abstain_low, config.abstain_high],
            "cluster_distance_threshold": config.cluster_distance_threshold,
            "aggregation_k": config.aggregation_k_threshold,
        },
    }


@app.get("/api/akis", response_model=list[PostView])
def akis(
    category: Literal["gundem", "spor", "kisisel"] | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[PostView]:
    """Akıştaki gönderileri döndürür (zenginleştirme varsa ekli)."""
    depo = load_feed()
    gonderiler = depo.by_category(category) if category else depo.posts  # type: ignore[arg-type]
    dilim = gonderiler[offset : offset + limit]

    sonuc: list[PostView] = []
    for post in dilim:
        temiz = post.to_service_dict()
        zengin = get_enriched(post.id)
        sonuc.append(
            PostView(
                **{k: temiz[k] for k in ("id", "author_id", "text", "created_at", "category", "media")},
                atomic_summary=zengin.atomic_summary if zengin else None,
                topic_label=zengin.topic_label if zengin else None,
            )
        )
    return sonuc


@app.post("/api/ozetle", response_model=SummaryResponse)
def ozetle(istek: SummarizeRequest = Body(...)) -> SummaryResponse:
    """Okunmamış gönderilerden atıflı özet üretir (KATMAN 2).

    `unread_post_ids` verilmezse kategorideki tüm gönderiler okunmamış sayılır
    (demo kolaylığı).
    """
    depo = load_feed()
    idler = istek.unread_post_ids or [p.id for p in depo.by_category(istek.category)]
    if not idler:
        raise HTTPException(status_code=400, detail="Özetlenecek gönderi yok.")

    yanit, hata_ayikla = summarize(istek.user_id, istek.category, idler)
    logger.info(
        "Özet: kategori=%s küme=%s cümle=%s silinen=%s bastırılan=%s",
        istek.category,
        yanit.cluster_count,
        len(yanit.sentences),
        yanit.dropped_sentence_count,
        len(hata_ayikla.suppressed_single_author_labels),
    )
    return yanit


@app.post("/api/ozetle/metinler", response_model=SummaryResponse)
def ozetle_metinler(istek: MetinOzetRequest = Body(...)) -> SummaryResponse:
    """Gövdede gelen gönderilerden atıflı özet üretir — depo gerektirmez.

    NEDEN AYRI UÇ: `/api/ozetle` gönderi kimliklerini backend'in kendi
    deposunda arar. Next.js arayüzü kendi simülasyon akışıyla çalıştığı için o
    uçtan hiçbir zaman sonuç alamıyordu ve ekranda atıfsız bir yerel özet
    gösteriyordu. Bu uç, aynı özetleme ve atıf denetimi hattını (İlke 1)
    kimliği depoda olmayan metinlere açar.

    Boş `sentences` bir HATA DEĞİLDİR: bütün cümleler atıf denetiminden düştüyse
    ya da bütün kümeler tek kaynaklıysa sistem susar (İlke 2/3). Sayaçlar
    yanıtta durur, istemci sessizliğin gerekçesini gösterebilir.
    """
    yanit = summarize_texts(
        istek.category,
        [(g.id, g.author_id, g.text) for g in istek.posts],
        user_id=istek.user_id,
    )
    return yanit


@app.post("/api/sor", response_model=AssistantResponse)
def sor(istek: AskRequest = Body(...)) -> AssistantResponse:
    """Gönderi bağlamında soru yanıtlar (reddetme dahil).

    Reddetme HTTP hatası DEĞİLDİR: 200 döner ve `refused=True` taşır.
    Çekimserlik ürünün normal davranışıdır, istisna değil.
    """
    depo = load_feed()
    if depo.get(istek.post_id) is None:
        raise HTTPException(status_code=404, detail="Gönderi bulunamadı.")
    return ask(depo, istek.post_id, istek.question)


@app.get("/api/tespit/{post_id}", response_model=DetectionResult)
def tespit(post_id: str) -> DetectionResult:
    """Gönderi için YZ metin sinyali.

    `label=None` ise arayüz HİÇBİR ROZET göstermez (spec 6.9 tasarım kuralı).
    """
    depo = load_feed()
    post = depo.get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Gönderi bulunamadı.")
    return detect(post.text)


@app.post("/api/tespit", response_model=DetectionResult)
def tespit_metin(istek: DetectRequest = Body(...)) -> DetectionResult:
    """Serbest metin için YZ sinyali — kimlik gerektirmez.

    NEDEN KİMLİKSİZ BİR UÇ GEREKTİ: `/api/tespit/{post_id}` yalnızca bu
    servisin kendi akışındaki gönderileri tanır (`p0411` gibi). Arayüz
    prototipi (`02-prototip/`) kendi simülasyon veri kümesiyle çalışıyor ve
    kimlikleri farklı (`6713e74b02d6` gibi); kimliğe dayalı uç oradan
    çağrılamaz. Ayrıca kullanıcının HENÜZ PAYLAŞMADIĞI bir taslağı (içerik
    üretici panelindeki metin) tespit etmenin başka yolu yok — o metnin
    tanımı gereği kimliği yoktur.

    Çekimserlik kuralları aynen uygulanır: karar `detect()` üzerinden geçer,
    yani uzunluk eşiği, kalibre edilmiş bant ve model yokluğu burada da
    geçerlidir. `label=None` dönerse arayüz HİÇBİR ROZET göstermemelidir
    (spec 6.9).

    Metin saklanmaz: istek gövdesi yanıtla birlikte düşer. Kalıcı kayıt
    tutmak, saklama sınırı ilkesine (spec 5.3) aykırı olurdu.
    """
    return detect(istek.text)


@app.get("/api/koken/{post_id}")
def koken(post_id: str) -> dict[str, Any]:
    """Gönderiye ekli görsellerin köken bilgisi (spec 6.6)."""
    depo = load_feed()
    post = depo.get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Gönderi bulunamadı.")
    return {
        "post_id": post_id,
        "media": [check_media(m).model_dump(mode="json") for m in post.media],
    }


@app.post("/api/itiraz")
def itiraz(istek: AppealRequest = Body(...)) -> dict[str, Any]:
    """YZ sinyaline itiraz kaydı (spec 6.9, itiraz akışı).

    NEDEN İTİRAZ AKIŞI ZORUNLU: Bir sistem insanları etiketliyorsa, etiketlenen
    kişinin itiraz edebileceği bir yol olmak zorundadır. Otomatik kararın
    kendisi kadar, karara karşı başvuru hakkı da tasarımın parçasıdır.

    Prototipte itiraz TTL'li önbelleğe yazılır; gerçek sistemde kalıcı bir
    inceleme kuyruğuna düşer ve insan denetimine açılır.
    """
    depo = load_feed()
    if depo.get(istek.post_id) is None:
        raise HTTPException(status_code=404, detail="Gönderi bulunamadı.")

    onbellek = get_cache()
    anahtar = f"itiraz:{istek.post_id}"
    mevcut = onbellek.get(anahtar) or []
    mevcut.append({"reason": istek.reason, "contact": istek.contact})
    onbellek.set(anahtar, mevcut, ttl_s=config.enrichment_ttl_s)
    logger.info("İtiraz kaydedildi post=%s (toplam %s)", istek.post_id, len(mevcut))
    return {
        "kaydedildi": True,
        "post_id": istek.post_id,
        "mesaj": "İtirazınız alındı. İnceleme sonuçlanana kadar bu gönderide sinyal gösterilmeyecek.",
    }


@app.get("/api/itiraz/{post_id}")
def itiraz_durumu(post_id: str) -> dict[str, Any]:
    """Gönderi için itiraz var mı.

    İtiraz varsa arayüz sinyali gizler: inceleme sürerken etiket göstermek,
    itiraz hakkını anlamsızlaştırırdı.
    """
    kayitlar = get_cache().get(f"itiraz:{post_id}") or []
    return {"post_id": post_id, "itiraz_var": bool(kayitlar), "adet": len(kayitlar)}


@app.post("/api/yonetisim/temizlik")
def temizlik() -> dict[str, Any]:
    """Süresi dolmuş kayıtları siler (spec 5.3 saklama sınırı).

    Uç nokta olarak açık olmasının sebebi gösterilebilirliktir: jüri
    "saklama sınırı gerçekten işliyor mu" diye sorduğunda çalıştırılıp
    sonucu gösterilebilir.
    """
    rapor = purge_expired()
    return {"silinen": rapor.removed, "kalan": rapor.remaining}


@app.post("/api/yonetisim/unut/{user_id}")
def unut(user_id: str) -> dict[str, Any]:
    """Kullanıcıya ait durumu siler (unutulma hakkı, KVKK md. 7)."""
    silinen = forget_user(user_id)
    return {"user_id": user_id, "silinen_anahtar": silinen, "onek": PREFIX_READ_STATE}
