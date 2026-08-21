"""Gömme (embedding) arka ucu.

NEDEN AYRI MODÜL: Sohbet üretimi ile vektör gömme farklı sağlayıcılardan gelir.
Anthropic API'si gömme uç noktası sunmaz; gömme ya yerelde çalışan bir
sentence-transformer modelinden ya da deterministik bir yedek işlevden gelir.
Bu ayrım sayesinde LLM sağlayıcısını değiştirmek kümelemeyi bozmaz.

İKİ ARKA UÇ:

1. `SentenceTransformerEmbedder` — MODEL_KARTI.md'de kayıtlı model
   (intfloat/multilingual-e5-base). Gerçek ölçüm ve demo bununla yapılır.
   `sentence-transformers` + `torch` kurulu olmasını gerektirir.

2. `HashingEmbedder` — karakter n-gram tabanlı, deterministik, bağımlılıksız
   yedek. Türkçe morfolojisinde kök paylaşan kelimeler ortak n-gram ürettiği
   için kümeleme yaklaşık olarak çalışır.
   DÜRÜSTLÜK NOTU: Bu bir dil modeli değildir, anlamsal benzerliği yalnızca
   yüzeysel biçim üzerinden yakalar. Raporlanan her metrik hangi arka uçla
   üretildiğini belirtmek zorundadır; `Embedder.name` bu yüzden çıktıya yazılır
   (bkz. ml/scripts/evaluate.py).
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

from app.config import config

# Karakter n-gram uzunluğu. 3-4'lü n-gramlar Türkçe'de kök + ek sınırını
# makul yakalar; daha kısası gürültü, daha uzunu seyreklik üretir.
_NGRAM_SIZES = (3, 4)
_TOKEN_RE = re.compile(r"[\wçğıöşüÇĞİÖŞÜ]+", re.UNICODE)


class Embedder(Protocol):
    """Gömme arka ucu arayüzü."""

    name: str
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Metin listesini birim uzunluğa normalize edilmiş vektörlere çevirir."""
        ...


def turkish_lower(text: str) -> str:
    """Türkçe kurallarına göre küçük harfe çevirir.

    NEDEN GEREKLİ: Python'un `str.lower()` metodu 'I' harfini 'i' yapar, oysa
    Türkçe'de 'I' -> 'ı' ve 'İ' -> 'i' olmalıdır. Bu dönüşüm yanlış yapılırsa
    "İSTANBUL" ile "istanbul" farklı token'lara ayrışır ve hem gömme hem de
    tespit modeli aynı kelimeyi iki ayrı kelime sanır (spec 5.2, ön işleme 1).
    """
    return text.replace("I", "ı").replace("İ", "i").lower()


class HashingEmbedder:
    """Bağımlılıksız, deterministik kelime + karakter n-gram gömmesi.

    Yöntem (hashing trick — sözlük tutmadan sabit boyutlu vektör):
      1. Metin Türkçe kurallarıyla küçültülür ve kelimelere ayrılır.
      2. İşlevsel kelimeler (durak kelimeler) atılır: "bir", "için", "ama" gibi
         kelimeler her metinde geçtiği için benzerliği yapay olarak şişirir.
      3. Kelime köküne yakın bir parça (ilk 6 karakter) ayrı bir özellik olarak
         eklenir. NEDEN: Türkçe sondan eklemelidir; "köprünün", "köprüde",
         "köprüyü" aynı kökü paylaşır ve aynı olayı anlatan gönderilerde farklı
         eklerle görünür. Kök parçası olmadan bu kelimeler tamamen farklı
         özelliklere düşer ve aynı olay iki ayrı kümeye ayrılır.
      4. Uzunluk temelli ağırlık: uzun kelimeler Türkçe'de daha çok içerik
         taşır (IDF'nin ucuz bir vekili). Gerçek IDF için korpus istatistiği
         gerekir; akış hızında gönderi tek tek gömüldüğü için korpus yoktur.
      5. Karakter n-gramları düşük ağırlıkla eklenir: yazım hatası ve çekim
         farklarına dayanıklılık sağlar.
      6. Vektör L2 normalize edilir; nokta çarpımı doğrudan kosinüs benzerliği.

    SINIRLILIK (rapora girecek): Bu yöntem anlamsal değil, biçimseldir. Eş
    anlamlı ama farklı yazılan kelimeleri yakalayamaz ("zam" ile "fiyat artışı").
    Gerçek ölçüm MODEL_KARTI.md'deki e5 modeliyle yapılır.
    """

    name = "hashing-word-char"

    # Türkçe yüksek frekanslı işlev kelimeleri. Kısa liste bilinçli: agresif
    # durak kelime ayıklaması kısa gönderilerde metni boşaltır.
    _STOPWORDS = frozenset(
        """ve veya ile bir bu şu o da de ki mi mı mu mü için gibi ama fakat ancak
        çok az daha en her hiç ne nasıl neden kim var yok olan olarak ise değil
        sonra önce kadar dedi diyor bende bana beni sen ben biz siz onlar""".split()
    )

    def __init__(self, dim: int | None = None) -> None:
        # 512 boyut: kelime + kök + n-gram özellikleri için 256 dar kalıyordu
        # (çakışma oranı yükselip alakasız metinleri benzer gösteriyordu).
        self.dim = dim or 512

    @staticmethod
    def _hash_indeks(parca: str, dim: int) -> tuple[int, float]:
        """Özelliği (indeks, işaret) çiftine eşler."""
        sayisal = int(hashlib.blake2b(parca.encode("utf-8"), digest_size=8).hexdigest(), 16)
        # İşaret bitini hash'ten alıyoruz: farklı özelliklerin aynı boyuta
        # düşmesi durumunda birikimli sapmayı azaltır (signed hashing).
        isaret = 1.0 if (sayisal >> 63) & 1 else -1.0
        return sayisal % dim, isaret

    def _ozellikler(self, text: str) -> list[tuple[str, float]]:
        """Metinden (özellik, ağırlık) çiftleri çıkarır."""
        ozellikler: list[tuple[str, float]] = []
        for kelime in _TOKEN_RE.findall(turkish_lower(text)):
            if kelime in self._STOPWORDS or len(kelime) < 2:
                continue
            # Uzunluk temelli ağırlık, 1.0 ile 2.0 arasında sınırlandırılır.
            agirlik = min(2.0, 0.6 + len(kelime) / 6.0)
            ozellikler.append((f"w:{kelime}", agirlik))
            if len(kelime) > 5:
                ozellikler.append((f"k:{kelime[:6]}", agirlik * 1.4))  # kök vekili
            isaretli = f"^{kelime}$"
            for n in _NGRAM_SIZES:
                if len(isaretli) < n:
                    continue
                for i in range(len(isaretli) - n + 1):
                    ozellikler.append((f"c:{isaretli[i : i + n]}", 0.35))
        return ozellikler

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Metinleri L2-normalize edilmiş vektörlere çevirir."""
        cikti: list[list[float]] = []
        for metin in texts:
            vektor = [0.0] * self.dim
            for parca, agirlik in self._ozellikler(metin):
                indeks, isaret = self._hash_indeks(parca, self.dim)
                vektor[indeks] += isaret * agirlik
            norm = math.sqrt(sum(x * x for x in vektor))
            if norm == 0.0:
                # Boş veya yalnızca durak kelimelerden oluşan metin: sıfır vektör
                # yerine sabit bir yön veriyoruz ki kosinüs tanımsız kalmasın.
                vektor[0] = 1.0
                norm = 1.0
            cikti.append([x / norm for x in vektor])
        return cikti


class SentenceTransformerEmbedder:
    """MODEL_KARTI.md'de kayıtlı çok dilli gömme modeli.

    e5 ailesi girdilerin "query: " / "passage: " öneki ile verilmesini bekler.
    Akıştaki gönderiler pasaj olduğu için "passage: " kullanıyoruz; bu önek
    modelin eğitim dağılımıyla uyumlu olduğundan benzerlik kalitesini artırır.
    """

    name = "multilingual-e5-base"

    def __init__(self, model_name: str | None = None) -> None:
        from sentence_transformers import SentenceTransformer  # yerel içe aktarım: ağır bağımlılık

        self.name = model_name or config.embedding_model
        self._model = SentenceTransformer(self.name)
        self.dim = int(self._model.get_sentence_embedding_dimension())

    def embed(self, texts: list[str]) -> list[list[float]]:
        vektorler = self._model.encode(
            [f"passage: {t}" for t in texts],
            normalize_embeddings=True,  # kosinüs için L2 normalize
            show_progress_bar=False,
        )
        return [[float(x) for x in v] for v in vektorler]


_embedder: Embedder | None = None


def get_embedder(force_fallback: bool = False) -> Embedder:
    """Kullanılabilir en iyi gömme arka ucunu döndürür (tekil).

    Sıralama: yapılandırmadaki gerçek model varsa o, yoksa deterministik yedek.
    Yedeğe düşerken sessiz kalmıyoruz — çağıran taraf `name` alanını ölçüm
    çıktısına yazar, böylece raporda hangi modelle ölçtüğümüz belli olur.
    """
    global _embedder
    if _embedder is not None and not force_fallback:
        return _embedder
    if force_fallback:
        return HashingEmbedder()
    try:
        _embedder = SentenceTransformerEmbedder()
    except Exception:  # ImportError veya model indirilememesi
        _embedder = HashingEmbedder()
    return _embedder


def cosine(a: list[float], b: list[float]) -> float:
    """İki vektör arasındaki kosinüs benzerliği.

    Vektörler zaten normalize geldiği için nokta çarpımı yeterli olurdu, ancak
    dışarıdan normalize edilmemiş vektör gelme ihtimaline karşı bölme yapıyoruz.
    """
    nokta = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return nokta / (na * nb)
