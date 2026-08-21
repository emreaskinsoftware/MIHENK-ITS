"""Akış deposu — gönderilerin okunduğu tek kapı.

NEDEN DEPO KATMANI: Servis modülleri JSON dosyasını doğrudan okusaydı,
PostgreSQL'e geçiş her modülü değiştirmeyi gerektirirdi. Ayrıca — daha
önemlisi — `_eval_*` alanlarının servis katmanına sızmaması ancak tek bir
okuma kapısı varsa denetlenebilir. Depo `Post` nesnesi döndürür; değerlendirme
alanları nesnede durur ama servis katmanı onları hiçbir yerde kullanmaz ve
`to_service_dict()` dışarı vermez (bkz. tests/test_eval_sizinti.py).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.config import config
from app.models import Post, PostCategory


@dataclass
class FeedRepository:
    """Bellek içi gönderi deposu.

    Akış boyutu (300-500 gönderi) tamamen bellekte tutulabilir. Ölçek testinde
    (P2) bu sınıfın arayüzü korunarak veritabanı destekli bir uygulama
    yazılacaktır.
    """

    posts: list[Post]

    def __post_init__(self) -> None:
        self._by_id: dict[str, Post] = {p.id: p for p in self.posts}
        # Yanıt zinciri dizini: bir gönderiye gelen doğrudan yanıtlar.
        self._replies: dict[str, list[Post]] = {}
        for p in self.posts:
            if p.reply_to_post_id:
                self._replies.setdefault(p.reply_to_post_id, []).append(p)

    # -- okuma ---------------------------------------------------------
    def get(self, post_id: str) -> Post | None:
        return self._by_id.get(post_id)

    def by_category(self, category: PostCategory) -> list[Post]:
        return [p for p in self.posts if p.category == category]

    def replies_to(self, post_id: str) -> list[Post]:
        """Gönderiye gelen doğrudan yanıtlar (asistan bağlamının parçası)."""
        return self._replies.get(post_id, [])

    def quote_chain(self, post_id: str, max_depth: int = 3) -> list[Post]:
        """Alıntı zincirini yukarı doğru takip eder.

        max_depth sınırı bilinçlidir: uzun zincirler hem bağlamı şişirir hem de
        döngüsel veri durumunda sonsuz döngü riski taşır. Zincir kopukluğu
        (silinmiş gönderi) sessizce durdurur.
        """
        zincir: list[Post] = []
        gorulen: set[str] = {post_id}
        mevcut = self.get(post_id)
        while mevcut and mevcut.quoted_post_id and len(zincir) < max_depth:
            sonraki = self.get(mevcut.quoted_post_id)
            if sonraki is None or sonraki.id in gorulen:
                break
            zincir.append(sonraki)
            gorulen.add(sonraki.id)
            mevcut = sonraki
        return zincir

    def __len__(self) -> int:
        return len(self.posts)


_repo: FeedRepository | None = None


def load_feed(path: Path | None = None) -> FeedRepository:
    """Akışı dosyadan yükler (tekil).

    Dosya yoksa açık hata verilir: sessizce boş akışla çalışmak, demoda
    "hiçbir şey görünmüyor" gibi teşhisi zor bir duruma yol açar.
    """
    global _repo
    if _repo is not None and path is None:
        return _repo
    yol = path or config.feed_path
    if not yol.exists():
        raise FileNotFoundError(
            f"Akış dosyası bulunamadı: {yol}\n"
            "Önce üretin: python ml/scripts/generate_feed.py --count 420"
        )
    ham = json.loads(yol.read_text(encoding="utf-8"))
    depo = FeedRepository([Post.model_validate(p) for p in ham])
    if path is None:
        _repo = depo
    return depo


def reset_feed() -> None:
    """Tekil depoyu sıfırlar (testler için)."""
    global _repo
    _repo = None
