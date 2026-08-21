"""Test altyapısı: yol ayarı ve her testte temiz durum.

NEDEN OTOMATİK SIFIRLAMA: Önbellek ve sağlayıcı tekil (singleton) nesnelerdir.
Bir testin yazdığı zenginleştirme kaydı diğerine sızarsa testler birbirine
bağımlı hale gelir ve sıraya duyarlı, güvenilmez bir takım oluşur.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import get_settings  # noqa: E402
from app.llm.provider import reset_provider  # noqa: E402
from app.models import Post  # noqa: E402
from app.llm.embedding import reset_embedder  # noqa: E402
from app.store.cache import reset_cache  # noqa: E402
from app.store.feed_repo import FeedRepository, reset_feed  # noqa: E402


@pytest.fixture(autouse=True)
def temiz_durum(monkeypatch: pytest.MonkeyPatch):
    """Her testten önce tekil durumları sıfırlar ve sahte sağlayıcıya sabitler.

    Testler dış servise çağrı YAPMAZ: hem yavaşlık hem de belirlenimsizlik
    getirir. Sağlayıcı her testte "fake" olarak sabitlenir.
    """
    monkeypatch.setenv("MIHENK_LLM_PROVIDER", "fake")
    # Birim testleri gömme modelini indirmez/yüklemez: e5 yüklemesi ~25 saniye
    # sürüyor ve testlerin hızlı koşması, sık koşulmasının ön şartı.
    # Gerçek modelle ölçüm ml/scripts/evaluate.py işidir.
    monkeypatch.setenv("MIHENK_EMBEDDING_BACKEND", "hashing")
    get_settings.cache_clear()
    reset_cache()
    reset_provider()
    reset_embedder()
    reset_feed()
    yield
    reset_cache()
    reset_provider()
    reset_feed()


def _post(
    post_id: str,
    text: str,
    *,
    author: str = "@yazar1",
    category: str = "gundem",
    **eval_alanlari,
) -> Post:
    """Test için kısa yoldan gönderi üretir."""
    return Post(
        id=post_id,
        author_id=author,
        text=text,
        created_at=datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc),
        category=category,  # type: ignore[arg-type]
        **eval_alanlari,
    )


@pytest.fixture
def post_uret():
    """Gönderi üreten yardımcıyı testlere verir."""
    return _post


@pytest.fixture
def kucuk_akis() -> FeedRepository:
    """Küçük, elle kurulmuş akış: iki olay + tek yazarlı bir küme.

    Sentetik akış dosyasına bağımlı olmayan testler bunu kullanır; böylece
    generate_feed.py değiştiğinde ilke testleri kırılmaz.
    """
    gonderiler = [
        _post("p1", "Yaltepe'de köprü açılışı üçüncü kez ertelendi, belediye hava koşullarını gösterdi.", author="@a"),
        _post("p2", "Köprü açılışının ertelenmesi esnafı kızdırdı, ciro düştü diyorlar.", author="@b"),
        _post("p3", "Köprü açılışı ertelendi ama testler bitmeden açmak tehlikeli olurdu.", author="@c"),
        _post("p4", "Su kesintisi üçüncü gününde, ana borudaki arıza gösteriliyor.", author="@d"),
        _post("p5", "Su kesintisi planlı bakımmış, duyuru günler önce yapılmış.", author="@e"),
        _post("p6", "Pazar yeri taşınacak diyorlar, bu benim üçüncü paylaşımım.", author="@tek"),
        _post("p7", "Pazar yeri taşınması konusunda kimse yazmıyor, yine ben yazıyorum.", author="@tek"),
    ]
    return FeedRepository(gonderiler)
