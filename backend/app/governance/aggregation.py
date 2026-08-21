"""k-eşikli toplulaştırma (spec 5.3).

KURAL: `k` eşiğinin altındaki gruplar HİÇ döndürülmez. Maskelenmez, "az" diye
işaretlenmez, yuvarlanmaz — sonuçtan tamamen çıkarılır.

NEDEN BU KADAR SERT: Küçük gruplar üzerinden yapılan istatistik, tekilleştirmeye
(re-identification) kapı açar. "Yaltepe'de bu konuyu konuşan 2 kişi var" bilgisi,
o iki kişiyi tanıyan biri için kimlik bilgisidir. Ayrıca sayıyı yuvarlamak veya
"<5" göstermek de sızıntıdır: farklı sorguların kesişimi gerçek sayıyı geri
verir (diferansiyel saldırı). Tek güvenli davranış, grubu hiç göstermemektir.

k varsayılanı config.aggregation_k_threshold (20) üzerinden gelir; kodda gömülü
sabit yoktur (spec 8).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Hashable, Iterable, TypeVar

from app.config import config

T = TypeVar("T")


@dataclass
class AggregationResult:
    """Toplulaştırma çıktısı ve gizlilik nedeniyle bastırılan grupların özeti."""

    groups: dict[Hashable, int] = field(default_factory=dict)
    # Eşiğin altında kaldığı için döndürülmeyen grup sayısı.
    # DİKKAT: Bastırılan grupların ANAHTARLARI da döndürülmez; yalnızca kaç adet
    # bastırıldığı bilgisi verilir. Anahtar listesi tek başına sızıntıdır
    # ("Yaltepe grubu bastırıldı" -> orada az kişi var demektir).
    suppressed_group_count: int = 0
    suppressed_item_count: int = 0
    k: int = 0

    @property
    def total_reported(self) -> int:
        return sum(self.groups.values())


def aggregate_with_k_threshold(
    items: Iterable[T],
    key_fn: Callable[[T], Hashable],
    *,
    k: int | None = None,
    identity_fn: Callable[[T], Hashable] | None = None,
) -> AggregationResult:
    """Öğeleri gruplayıp yalnızca k eşiğini geçen grupları döndürür.

    Args:
        items: Toplulaştırılacak kayıtlar.
        key_fn: Her kaydın hangi gruba gireceğini belirler.
        k: Eşik. Verilmezse config.aggregation_k_threshold kullanılır.
        identity_fn: Grup büyüklüğü sayılırken TEKİL KİŞİ sayısını verir.
            NEDEN GEREKLİ: Aynı kişinin 30 gönderisi bir grubu eşiğin üstüne
            çıkarmamalı; k-anonimlik kişi sayısıyla ilgilidir, kayıt sayısıyla
            değil. Verilmezse her kayıt ayrı kişi sayılır (güvenli taraf değil,
            bu yüzden çağıranın vermesi beklenir).

    Returns:
        AggregationResult — yalnızca k >= eşik olan gruplar.
    """
    esik = k if k is not None else config.aggregation_k_threshold
    kovalar: dict[Hashable, list[T]] = defaultdict(list)
    for oge in items:
        kovalar[key_fn(oge)].append(oge)

    sonuc = AggregationResult(k=esik)
    for anahtar, grup in kovalar.items():
        if identity_fn is not None:
            buyukluk = len({identity_fn(o) for o in grup})
        else:
            buyukluk = len(grup)
        if buyukluk < esik:
            sonuc.suppressed_group_count += 1
            sonuc.suppressed_item_count += len(grup)
            continue
        sonuc.groups[anahtar] = buyukluk
    return sonuc
