"""TTL'li anahtar-değer önbelleği — Redis'in yerel karşılığı.

NEDEN REDIS DEĞİL (şimdilik): Demo ve ölçüm tek makinede koşuyor; Redis bağımlılığı
kurulum riski ekliyor ve jüri demosunda ayağa kalkmayan bir servis en kötü
senaryodur. Arayüz bilinçli olarak Redis'in kullandığımız alt kümesiyle aynı
(get/set/setex/delete/exists/keys/ttl), böylece Redis'e geçiş tek dosyalık bir
uygulama değişikliğidir — LLM sağlayıcı soyutlamasıyla aynı mantık.

TTL BURADA ÜRÜN GEREĞİDİR, teknik detay değil: Özetleme için çekilen içerik
kalıcı saklanmaz (spec 5.3 / retention). Süresi dolan kayıt okunamaz ve
temizlenir.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class _Kayit:
    """Önbellek kaydı: değer + mutlak son kullanma zamanı."""

    value: Any
    expires_at: float | None  # None = süresiz (yalnızca test amaçlı kullanılır)


class TTLCache:
    """İş parçacığı güvenli, süre sınırlı önbellek.

    NEDEN KİLİT VAR: Zenginleştirme işçileri eşzamanlı çalışır (KATMAN 1).
    Sözlük işlemleri CPython'da büyük ölçüde atomiktir ama "kontrol et sonra
    yaz" dizileri değildir; sayaçların bozulmaması için açık kilit kullanıyoruz.
    """

    def __init__(self) -> None:
        self._veri: dict[str, _Kayit] = {}
        self._kilit = threading.RLock()
        # Ölçüm sayaçları: önbellek isabet oranı raporlanan bir metriktir (spec 7).
        self.hits = 0
        self.misses = 0

    # -- temel işlemler ------------------------------------------------
    def set(self, key: str, value: Any, ttl_s: int | None = None) -> None:
        """Değeri yazar; ttl_s verilmişse o süre sonunda geçersiz olur."""
        with self._kilit:
            son = time.time() + ttl_s if ttl_s else None
            self._veri[key] = _Kayit(value=value, expires_at=son)

    def get(self, key: str) -> Any | None:
        """Değeri okur; süresi dolmuşsa siler ve None döner."""
        with self._kilit:
            kayit = self._veri.get(key)
            if kayit is None:
                self.misses += 1
                return None
            if kayit.expires_at is not None and kayit.expires_at <= time.time():
                # Tembel temizleme: okuma anında süresi dolmuş kaydı siliyoruz.
                # Ayrıca periyodik süpürme için sweep_expired() var (retention.py).
                del self._veri[key]
                self.misses += 1
                return None
            self.hits += 1
            return kayit.value

    def delete(self, key: str) -> bool:
        with self._kilit:
            return self._veri.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    def ttl(self, key: str) -> float | None:
        """Kalan süre (saniye). Kayıt yoksa None, süresizse -1."""
        with self._kilit:
            kayit = self._veri.get(key)
            if kayit is None:
                return None
            if kayit.expires_at is None:
                return -1.0
            return max(0.0, kayit.expires_at - time.time())

    def keys(self, prefix: str = "") -> list[str]:
        with self._kilit:
            return [k for k in self._veri if k.startswith(prefix)]

    # -- yönetim -------------------------------------------------------
    def sweep_expired(self) -> int:
        """Süresi dolmuş kayıtları temizler, silinen sayısını döndürür.

        Tembel temizleme yeterli değildir: hiç okunmayan bir kayıt bellekte
        kalırdı. Saklama sınırı (retention) iddiasının gerçek olması için
        aktif süpürme gerekir.
        """
        simdi = time.time()
        with self._kilit:
            dolmus = [k for k, v in self._veri.items() if v.expires_at and v.expires_at <= simdi]
            for k in dolmus:
                del self._veri[k]
            return len(dolmus)

    def clear(self) -> None:
        with self._kilit:
            self._veri.clear()
            self.hits = 0
            self.misses = 0

    @property
    def hit_ratio(self) -> float:
        """Önbellek isabet oranı (rapor Tablo 5)."""
        toplam = self.hits + self.misses
        return self.hits / toplam if toplam else 0.0

    def __len__(self) -> int:
        with self._kilit:
            return len(self._veri)


_cache: TTLCache | None = None


def get_cache() -> TTLCache:
    """Süreç genelinde tek önbellek örneği."""
    global _cache
    if _cache is None:
        _cache = TTLCache()
    return _cache


def reset_cache() -> None:
    """Önbelleği sıfırlar (testler ve ölçüm koşuları arası)."""
    global _cache
    _cache = None
