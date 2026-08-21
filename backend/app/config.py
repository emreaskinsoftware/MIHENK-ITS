"""MİHENK yapılandırması — tüm eşik ve sabit değerlerin tek kaynağı.

NEDEN TEK DOSYA: Spec 8. bölüm "sabit değerler config.py'de, kodda gömülü sayı yok"
diyor. Bunun pratik sebebi şu: çekimserlik ve kümeleme eşikleri ölçümle kalibre
edilecek (ml/scripts/evaluate.py çıktısına bakarak). Eşikler koda dağılmış olsaydı
kalibrasyon sonrası güncelleme hem hataya açık olurdu hem de raporda "hangi değeri
kullandık" sorusuna tek bir yerden cevap veremezdik.

Değerler ortam değişkeniyle ezilebilir (MIHENK_ öneki), ama varsayılanlar burada
durur ve rapora bu dosyadan alınır.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Depo kökü: config.py -> app -> backend -> <kök>
REPO_ROOT: Path = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Uygulama ayarları.

    Her alanın yanındaki yorum, o değerin NEDEN o değer olduğunu anlatır.
    Ölçümle kalibre edilmesi gereken alanlar "KALİBRE" etiketiyle işaretlidir;
    bu değerler ilk aşamada makul başlangıç noktalarıdır, nihai değerleri
    evaluate.py çıktısıyla belirlenir ve rapora oradan yazılır.
    """

    model_config = SettingsConfigDict(env_prefix="MIHENK_", env_file=".env", extra="ignore")

    # ------------------------------------------------------------------
    # LLM sağlayıcı seçimi (bkz. app/llm/provider.py)
    # ------------------------------------------------------------------
    # "fake" sağlayıcı deterministiktir ve dış çağrı yapmaz; testler ve CI
    # anahtarsız koşabilsin diye varsayılan odur. Demo ve ölçüm için "api".
    llm_provider: Literal["fake", "api", "vllm"] = "fake"
    llm_model: str = "claude-sonnet-5"
    llm_timeout_s: float = 30.0

    # ------------------------------------------------------------------
    # Gömme modeli — MODEL_KARTI.md ile tutarlı olmalı
    # ------------------------------------------------------------------
    embedding_model: str = "intfloat/multilingual-e5-base"
    embedding_dim: int = 768

    # ------------------------------------------------------------------
    # KATMAN 1 — Zenginleştirme (spec 6.1)
    # ------------------------------------------------------------------
    # 15 kelimenin altındaki gönderiyi özetlemek anlamsız: özet metinden uzun
    # olur ve LLM çağrısı boşa maliyet yazar. Bu eşiğin altında metnin kendisi
    # atomik özet olarak kullanılır.
    min_words_for_summary: int = 15
    atomic_summary_max_words: int = 40
    atomic_summary_max_sentences: int = 2
    enrichment_ttl_s: int = 24 * 60 * 60  # Önbellek 1 gün; spec 5.3 retention kuralı
    enrichment_max_retries: int = 3  # Sonsuz döngü koruması (spec 6.1)

    # ------------------------------------------------------------------
    # KATMAN 2 — Özetleme (spec 6.2)
    # ------------------------------------------------------------------
    # Aglomeratif kümelemede cosine mesafe eşiği. 0.45 ≈ 0.55 cosine benzerlik:
    # çok dilli e5 gömmelerinde aynı olayı anlatan Türkçe gönderiler bu bandın
    # üstünde kalır, farklı konular ayrışır. KALİBRE.
    cluster_distance_threshold: float = 0.45
    min_clusters: int = 5
    max_clusters: int = 10
    cluster_representatives: int = 3  # Küme merkezine en yakın kaç gönderi LLM'e gider
    max_summary_words: int = 120  # Üreticiyi koruma: özet gönderinin yerine geçmez
    # Bir kümede en az kaç FARKLI yazar olmalı ki gündem özeti üretilsin (İlke 3).
    min_distinct_authors_for_agenda: int = 2

    # ------------------------------------------------------------------
    # Asistan (spec 6.3)
    # ------------------------------------------------------------------
    max_assistant_words: int = 60

    # ------------------------------------------------------------------
    # YZ tespiti + çekimserlik (spec 6.5 / İlke 2)
    # ------------------------------------------------------------------
    # Bu üç değer İlke 2'nin sayısal karşılığıdır. Uzunluk eşiği K1 kovasının
    # (0-50 token) alt bölgesini kapsar: orada model başarımı zayıf.
    min_detection_tokens: int = 20  # KALİBRE
    abstain_low: float = 0.35  # KALİBRE — bu bandın içi "kararsız" bölgedir
    abstain_high: float = 0.65  # KALİBRE
    detection_model: str = "dbmdz/bert-base-turkish-cased"

    # ------------------------------------------------------------------
    # Veri yönetişimi (spec 5.3)
    # ------------------------------------------------------------------
    # k-anonimlik eşiği: bu sayıdan az kişiden oluşan grup için toplulaştırma
    # sonucu HİÇ döndürülmez (tekilleştirme riski).
    aggregation_k_threshold: int = 20

    # ------------------------------------------------------------------
    # Ajan (spec 6.7) — P1
    # ------------------------------------------------------------------
    agent_max_steps: int = 6  # Sonsuz döngü koruması
    allowed_domains: tuple[str, ...] = (
        "tr.wikipedia.org",
        "www.resmigazete.gov.tr",
        "data.tuik.gov.tr",
    )

    # ------------------------------------------------------------------
    # Yollar
    # ------------------------------------------------------------------
    @property
    def feed_path(self) -> Path:
        """Sentetik akış dosyası (ml/scripts/generate_feed.py üretir)."""
        return REPO_ROOT / "ml" / "data" / "synthetic_feed" / "feed.json"

    @property
    def eval_results_dir(self) -> Path:
        """Ölçüm çıktıları — rapor tablolarının kaynağı."""
        return REPO_ROOT / "eval" / "results"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Ayarları tekil (singleton) olarak döndürür.

    NEDEN CACHE: Ayar nesnesi süreç boyunca değişmez; her modülün kendi kopyasını
    okuması hem gereksiz hem de testte eşik değiştirmeyi zorlaştırır.
    Testler `get_settings.cache_clear()` ile sıfırlayabilir.
    """
    return Settings()


config = get_settings()
