"""Saklama sınırı (retention) — özet için çekilen içerik kalıcı tutulmaz (spec 5.3).

İLKE: MİHENK bir arşiv değildir. Zenginleştirme çıktıları (atomik özet, gömme)
yalnızca akış deneyimini hızlandırmak için tutulur ve süresi dolunca silinir.
Kullanıcının okuma geçmişi de kalıcı değildir.

NEDEN AYRI MODÜL: TTL değerini önbellek çağrısına gömmek, saklama politikasını
koda dağıtır ve denetlenemez hale getirir. Politika burada tek yerde tanımlıdır;
`purge_expired()` çağrısı hem periyodik işçi hem de test tarafından koşulabilir.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import config
from app.store.cache import get_cache

# Anahtar önekleri: hangi veri türünün ne kadar yaşayacağı buradan okunur.
PREFIX_ENRICHED = "enriched:"
PREFIX_READ_STATE = "okundu:"
PREFIX_SUMMARY = "ozet:"


@dataclass
class RetentionPolicy:
    """Veri türü başına saklama süresi (saniye)."""

    enriched_ttl_s: int
    read_state_ttl_s: int
    summary_ttl_s: int

    @classmethod
    def from_config(cls) -> RetentionPolicy:
        """Politikayı config'den kurar.

        Okuma durumu zenginleştirmeden daha kısa yaşar: kullanıcı davranışı en
        hassas veridir, en kısa süre tutulur. Özet çıktısı ise yalnızca kısa
        süreli tekrar isteklerini karşılamak için tutulur (aynı kullanıcı
        butona iki kez basarsa).
        """
        return cls(
            enriched_ttl_s=config.enrichment_ttl_s,
            read_state_ttl_s=config.enrichment_ttl_s // 4,
            summary_ttl_s=300,
        )


@dataclass
class PurgeReport:
    """Temizlik raporu — denetlenebilirlik için (kaç kayıt silindi)."""

    removed: int
    remaining: int


def purge_expired() -> PurgeReport:
    """Süresi dolmuş tüm kayıtları siler.

    Bu fonksiyonun varlığı, "TTL koyduk" demenin ötesine geçer: hiç okunmayan
    kayıtların da gerçekten silindiğini gösterir ve testle kanıtlanır.
    """
    onbellek = get_cache()
    silinen = onbellek.sweep_expired()
    return PurgeReport(removed=silinen, remaining=len(onbellek))


def forget_user(user_id: str) -> int:
    """Bir kullanıcıya ait tüm durumu siler (unutulma hakkı).

    KVKK md. 7 / GDPR md. 17 karşılığı. Prototipte kullanıcı durumu yalnızca
    okuma durumundan ibarettir; gerçek sistemde bu fonksiyon tüm kişisel
    kayıtları kapsayacak biçimde genişletilir.

    Returns:
        Silinen anahtar sayısı.
    """
    onbellek = get_cache()
    hedefler = onbellek.keys(f"{PREFIX_READ_STATE}{user_id}")
    for anahtar in hedefler:
        onbellek.delete(anahtar)
    return len(hedefler)
