"""Konu kümeleme — KATMAN 2 adım 2 (spec 6.2).

YÖNTEM: Aglomeratif kümeleme, kosinüs mesafesi, ortalama bağlantı (average
linkage), mesafe eşiği config.cluster_distance_threshold.

NEDEN AGLOMERATİF (k-means değil):
  1. Küme sayısı önceden bilinmiyor. Gündemde kaç ayrı olay olduğunu kullanıcı
     "Özetle" demeden önce bilemeyiz; k-means k'yı girdi olarak ister.
  2. Kosinüs mesafesiyle doğrudan çalışır. Gömmeler L2-normalize olduğu için
     kosinüs anlamsal yakınlığın doğru ölçütüdür; k-means Öklid varsayar.
  3. Mesafe eşiği yorumlanabilir bir parametredir: "bu kadar benzer olanlar aynı
     olaydır" cümlesi doğrudan eşiğe çevrilir ve raporda savunulabilir.

NEDEN ORTALAMA BAĞLANTI: Tek bağlantı (single) zincirleme yapar — birbirine
uzak iki olayı, aradaki tek bir köprü gönderi yüzünden birleştirir. Tam bağlantı
(complete) ise aşırı parçalar. Ortalama bağlantı ikisinin arasındadır ve kısa
metinlerdeki gürültüye karşı daha dayanıklıdır.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.config import config
from app.llm.embedding import HashingEmbedder, get_embedder
from app.models import EnrichedPost


def active_distance_threshold() -> float:
    """Etkin gömme arka ucuna uygun kümeleme eşiğini döndürür.

    NEDEN ARKA UCA BAĞLI: Eşik, gömme uzayının benzerlik dağılımına göre
    anlam kazanır. Aynı sayıyı iki farklı gömücüde kullanmak, birinde her şeyi
    tek kümede toplar, diğerinde hiçbir şeyi birleştirmez. Eşiğin hangi modelle
    ölçüldüğü raporda belirtilir (spec 2: uydurma metrik yok).
    """
    return (
        config.cluster_distance_threshold_fallback
        if isinstance(get_embedder(), HashingEmbedder)
        else config.cluster_distance_threshold
    )


@dataclass
class Cluster:
    """Bir konu kümesi."""

    label: str
    members: list[EnrichedPost] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.members)

    @property
    def distinct_authors(self) -> set[str]:
        """Kümedeki farklı yazarlar — İlke 3 (çoğulculuk) kontrolünün girdisi."""
        return {u.author_id for u in self.members}

    def centroid(self) -> list[float]:
        """Küme merkezi (ortalama vektör, L2 normalize).

        Normalize etmemizin sebebi: merkeze uzaklık kosinüsle ölçülecek ve
        normalize edilmemiş merkez, büyük kümelerde yönü koruyup büyüklüğü
        bozarak sıralamayı etkiler.
        """
        if not self.members:
            return []
        boyut = len(self.members[0].embedding)
        toplam = [0.0] * boyut
        for uye in self.members:
            for i, deger in enumerate(uye.embedding):
                toplam[i] += deger
        norm = math.sqrt(sum(x * x for x in toplam)) or 1.0
        return [x / norm for x in toplam]

    def representatives(self, k: int | None = None) -> list[EnrichedPost]:
        """Merkeze en yakın k gönderiyi döndürür (spec 6.2 adım 3).

        NEDEN TEMSİLCİ: Kümedeki tüm gönderileri LLM'e vermek, tek çağrı
        kuralını korusa bile prompt boyutunu ve maliyeti gönderi sayısıyla
        doğrusal büyütür. Merkeze en yakın birkaç gönderi kümenin ortak
        içeriğini zaten taşır.

        YAN ETKİ (bilinçli): Kümenin uç görüşleri temsilciye girmeyebilir.
        Çoğulculuk bu yüzden temsilci seçimine değil, KÜMELEME ÇÖZÜNÜRLÜĞÜNE
        bırakılmıştır: farklı açılar farklı kümelere düşecek kadar farklıysa
        ayrı kümelerde temsil edilirler.
        """
        adet = k or config.cluster_representatives
        merkez = self.centroid()
        if not merkez:
            return self.members[:adet]
        sirali = sorted(
            self.members,
            key=lambda u: -sum(x * y for x, y in zip(u.embedding, merkez)),
        )
        return sirali[:adet]


def _cosine_distance_matrix(vektorler: list[list[float]]) -> list[list[float]]:
    """Kosinüs mesafe matrisi (1 - kosinüs benzerliği).

    Küçük N (bir kullanıcının okunmamış gönderileri, tipik olarak < 300) için
    O(N^2) matris kabul edilebilir. Ölçek testinde (P2) bu adım yaklaşık en
    yakın komşu yapısıyla değiştirilecektir.
    """
    n = len(vektorler)
    matris = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            benzerlik = sum(x * y for x, y in zip(vektorler[i], vektorler[j]))
            mesafe = 1.0 - benzerlik
            matris[i][j] = matris[j][i] = mesafe
    return matris


def agglomerative(
    items: list[EnrichedPost], *, distance_threshold: float | None = None
) -> list[list[int]]:
    """Ortalama bağlantılı aglomeratif kümeleme, indeks listeleri döndürür.

    Kendi uygulamamızı yazmamızın sebebi ideolojik değil pratiktir: scikit-learn
    bağımlılığı ML tarafında zaten var, ancak servis katmanının ağır bir
    bilimsel kütüphaneyi içe aktarmadan çalışabilmesi başlangıç süresini ve
    dağıtım boyutunu düşürüyor. Algoritma standarttır ve adım adım yorumludur.
    """
    esik = distance_threshold if distance_threshold is not None else active_distance_threshold()
    n = len(items)
    if n == 0:
        return []
    if n == 1:
        return [[0]]

    mesafe = _cosine_distance_matrix([i.embedding for i in items])
    # Başlangıçta her öğe kendi kümesi.
    kumeler: dict[int, list[int]] = {i: [i] for i in range(n)}

    while len(kumeler) > 1:
        # 1) En yakın küme çiftini bul (ortalama bağlantı mesafesi).
        en_yakin: tuple[int, int] | None = None
        en_kucuk = float("inf")
        anahtarlar = sorted(kumeler)  # belirlenimci sıra: aynı girdi aynı çıktı
        for idx_a in range(len(anahtarlar)):
            for idx_b in range(idx_a + 1, len(anahtarlar)):
                a, b = anahtarlar[idx_a], anahtarlar[idx_b]
                uyeler_a, uyeler_b = kumeler[a], kumeler[b]
                ortalama = sum(mesafe[i][j] for i in uyeler_a for j in uyeler_b) / (
                    len(uyeler_a) * len(uyeler_b)
                )
                if ortalama < en_kucuk:
                    en_kucuk, en_yakin = ortalama, (a, b)

        # 2) En yakın çift bile eşikten uzaksa birleştirme biter.
        if en_yakin is None or en_kucuk > esik:
            break

        # 3) Birleştir.
        a, b = en_yakin
        kumeler[a] = kumeler[a] + kumeler[b]
        del kumeler[b]

    return [kumeler[k] for k in sorted(kumeler)]


def build_clusters(
    items: list[EnrichedPost], *, distance_threshold: float | None = None
) -> list[Cluster]:
    """Zenginleştirilmiş gönderileri kümelere ayırır ve etiketler.

    Hedef küme sayısı config.min_clusters..max_clusters aralığıdır; daha fazla
    küme çıkarsa EN BÜYÜK N tanesi alınır (spec 6.2 adım 2).

    NEDEN EN BÜYÜKLER: Kullanıcı okunmamış akışının ana hatlarını görmek
    istiyor. Tek gönderilik kümeler (bir kişinin tek paylaşımı) gündem değildir;
    onları özete sokmak hem gürültü hem maliyettir. Dışarıda kalan kümelerin
    sayısı yanıtta raporlanır, sessizce kaybolmaz.
    """
    gruplar = agglomerative(items, distance_threshold=distance_threshold)
    kumeler: list[Cluster] = []
    for grup in gruplar:
        uyeler = [items[i] for i in grup]
        # Küme etiketi: üyelerin en sık konu etiketi. Beraberlikte alfabetik
        # sıra (belirlenimci davranış).
        sayim: dict[str, int] = {}
        for u in uyeler:
            sayim[u.topic_label] = sayim.get(u.topic_label, 0) + 1
        etiket = sorted(sayim.items(), key=lambda t: (-t[1], t[0]))[0][0]
        kumeler.append(Cluster(label=etiket, members=uyeler))

    # SIRALAMA ÖLÇÜTÜ: önce FARKLI YAZAR sayısı, sonra gönderi sayısı,
    # eşitlikte etiket adı (belirlenimcilik).
    #
    # NEDEN YAZAR SAYISI ÖNCE (spec 6.2 "en büyük N" kuralının okunuşu):
    # Bir konuyu 10 kişi konuşuyorsa o gündemdir; aynı konuda 10 gönderi tek
    # kişiden geliyorsa o kişinin ısrarıdır. Gönderi sayısına göre sıralamak,
    # çok paylaşan tek bir hesabın gündemi belirlemesine izin verir — bu hem
    # çoğulculuğa (İlke 3) aykırıdır hem de manipülasyona açık bir kaldıraçtır.
    # Yazar çeşitliliğini önce koymak, tek kaynaklı kümeleri bastırma kuralıyla
    # (service.py) aynı gerekçeye dayanır ve onu tamamlar.
    kumeler.sort(key=lambda c: (-len(c.distinct_authors), -c.size, c.label))
    return kumeler[: config.max_clusters]
