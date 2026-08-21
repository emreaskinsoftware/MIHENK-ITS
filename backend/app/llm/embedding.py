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
    """Bağımlılıksız, deterministik karakter n-gram gömmesi.

    Yöntem: metin Türkçe kurallarıyla küçültülür, kelimelere ayrılır, her kelime
    için 3 ve 4 karakterlik n-gramlar çıkarılır, her n-gram sabit bir hash ile
    vektörün bir boyutuna eşlenir (hashing trick) ve ağırlığı artırılır. Vektör
    L2 normalize edilir ki nokta çarpımı doğrudan kosinüs benzerliği versin.

    NEDEN HASHING TRICK: Sözlük tutmadan sabit boyutlu vektör üretir; yeni
    gönderi geldiğinde sözlüğü yeniden kurmak gerekmez (akış hızı kısıtı).
    """

    name = "hashing-char-ngram"

    def __init__(self, dim: int | None = None) -> None:
        # Yedek arka uçta boyutu küçük tutuyoruz: 768 boyut seyrek n-gram
        # sayımıyla doldurulamaz, gereksiz bellek ve gürültü olur.
        self.dim = dim or 256

    def _ngrams(self, text: str) -> list[str]:
        parcalar: list[str] = []
        for kelime in _TOKEN_RE.findall(turkish_lower(text)):
            # Kelime sınırlarını işaretle: "spor" kelimesinin başı ile
            # "raporspor" içindeki "spor" aynı n-gram'a düşmesin.
            isaretli = f"^{kelime}$"
            for n in _NGRAM_SIZES:
                if len(isaretli) < n:
                    parcalar.append(isaretli)
                    continue
                parcalar.extend(isaretli[i : i + n] for i in range(len(isaretli) - n + 1))
        return parcalar

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Metinleri L2-normalize edilmiş vektörlere çevirir."""
        cikti: list[list[float]] = []
        for metin in texts:
            vektor = [0.0] * self.dim
            for gram in self._ngrams(metin):
                sayisal = int(hashlib.blake2b(gram.encode("utf-8"), digest_size=8).hexdigest(), 16)
                indeks = sayisal % self.dim
                # İşaret bitini hash'ten alıyoruz: farklı n-gramların aynı
                # boyuta düşmesi durumunda birikimli sapmayı azaltır.
                isaret = 1.0 if (sayisal >> 63) & 1 else -1.0
                vektor[indeks] += isaret
            norm = math.sqrt(sum(x * x for x in vektor))
            if norm == 0.0:
                # Boş veya yalnızca noktalama içeren metin: sıfır vektör yerine
                # sabit bir yön veriyoruz ki kosinüs hesabı tanımsız kalmasın.
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
