"""Deterministik, dış çağrısız LLM sağlayıcısı.

NE İŞE YARAR: Tüm hattın (zenginleştirme → kümeleme → birleştirme → atıf
denetimi → asistan) API anahtarı olmadan uçtan uca çalışmasını sağlar. Testler,
sürekli tümleştirme ve enjeksiyon değerlendirmesi bu sağlayıcıyla koşar.

BU BİR DİL MODELİ DEĞİLDİR — ÇIKARIMSAL DEĞİL, ÇIKARIMCIDIR (extractive):
gönderilerden cümle seçer, yeni cümle üretmez. Bu bilinçli bir karardır:
  - Sahte bir "üretim" taklidi yapsaydı, atıf denetimi ve sadakat ölçümü
    yanıltıcı biçimde mükemmel görünürdü.
  - Çıkarımsal davranış, hattın DOĞRU KURULDUĞUNU gösterir; dil kalitesini
    değil. Dil kalitesi ölçümü APIProvider ile yapılır ve raporda hangi
    sağlayıcıyla ölçüldüğü belirtilir (spec 2: uydurma metrik yok).

Kasıtlı olarak İLKELERİ İHLAL ETMEZ: kaynak ID uydurmaz, bağlam dışına çıkmaz.
Atıf denetiminin gerçekten çalıştığını göstermek için ayrıca
`HallucinatingFakeProvider` vardır; yalnızca testlerde kullanılır.
"""

from __future__ import annotations

import json
import re

from app.config import config
from app.llm.prompts import REFUSAL_TOKEN, TASK_ASSISTANT, TASK_ATOMIC, TASK_MERGE
from app.llm.provider import BaseProvider
from app.security.prompt_guard import DELIM_END, DELIM_START
from app.textutil import split_sentences, truncate_words, turkish_lower

_POST_MARKER_RE = re.compile(r"^\[GONDERI:([^\]]+)\]$")
_QUESTION_MARKER_RE = re.compile(r"^\[KULLANICI_SORUSU\]$")
_CLUSTER_RE = re.compile(r"^### KUME:\s*(.+)$")
_TASK_RE = re.compile(r"^GOREV:\s*(\w+)", re.MULTILINE)

# Anlam taşımayan kelimeler: asistanın örtüşme skorunda gürültü yapmasınlar.
_STOPWORDS = frozenset(
    """ve veya ile bir bu şu o da de mi mı mu mü için gibi ama fakat ancak çok az
    daha en her hiç ki ne nasıl neden kim kime kimin ise değil olarak sonra önce
    üzerine kadar dedi diyor var yok olan olarak""".split()
)


def _kelime_kumesi(metin: str) -> set[str]:
    """Metni anlamlı kelime kümesine indirger (Türkçe küçültme ile)."""
    return {k for k in re.findall(r"[\wçğıöşü]+", turkish_lower(metin)) if k not in _STOPWORDS}


def _veri_bloklarini_ayristir(user: str) -> list[tuple[str | None, list[tuple[str, str]]]]:
    """Prompt'taki veri bloklarını (küme_etiketi, [(post_id, metin)]) olarak çıkarır.

    Küme etiketi yoksa None döner (asistan ve atomik özet görevlerinde).
    Bu ayrıştırıcı, prompt_guard.wrap_posts biçiminin tersidir.
    """
    sonuc: list[tuple[str | None, list[tuple[str, str]]]] = []
    aktif_kume: str | None = None
    aktif_liste: list[tuple[str, str]] | None = None
    aktif_id: str | None = None
    tampon: list[str] = []
    blok_icinde = False

    def _kapat_gonderi() -> None:
        if aktif_id is not None and aktif_liste is not None:
            aktif_liste.append((aktif_id, "\n".join(tampon).strip()))

    for satir in user.splitlines():
        kume_esles = _CLUSTER_RE.match(satir.strip())
        if kume_esles:
            _kapat_gonderi()
            aktif_id, tampon = None, []
            aktif_kume = kume_esles.group(1).strip()
            aktif_liste = []
            sonuc.append((aktif_kume, aktif_liste))
            continue
        if satir.strip() == DELIM_START:
            blok_icinde = True
            if aktif_liste is None:
                aktif_liste = []
                sonuc.append((aktif_kume, aktif_liste))
            continue
        if satir.strip() == DELIM_END:
            _kapat_gonderi()
            aktif_id, tampon = None, []
            blok_icinde = False
            # Blok bittiğinde küme bağlamını koru (aynı kümede tek blok var).
            continue
        if not blok_icinde:
            continue
        gonderi_esles = _POST_MARKER_RE.match(satir.strip())
        if gonderi_esles:
            _kapat_gonderi()
            aktif_id = gonderi_esles.group(1)
            tampon = []
            continue
        if _QUESTION_MARKER_RE.match(satir.strip()):
            _kapat_gonderi()
            aktif_id = "__SORU__"
            tampon = []
            continue
        tampon.append(satir)
    _kapat_gonderi()
    return [(etiket, liste) for etiket, liste in sonuc if liste]


class FakeProvider(BaseProvider):
    """Çıkarımsal, deterministik sağlayıcı."""

    name = "fake-extractive"

    def complete(self, system: str, user: str, max_tokens: int) -> str:
        """Görev etiketine göre deterministik yanıt üretir."""
        gorev_esles = _TASK_RE.search(user)
        gorev = gorev_esles.group(1) if gorev_esles else TASK_ATOMIC
        bloklar = _veri_bloklarini_ayristir(user)

        if gorev == TASK_ATOMIC:
            return self._atomik_ozet(bloklar)
        if gorev == TASK_MERGE:
            return self._birlestir(bloklar)
        if gorev == TASK_ASSISTANT:
            return self._asistan(bloklar)
        return ""

    # ------------------------------------------------------------------
    def _atomik_ozet(self, bloklar: list[tuple[str | None, list[tuple[str, str]]]]) -> str:
        """İlk 1-2 cümleyi kelime sınırına kırparak döndürür.

        Sosyal medya gönderilerinde ana bilgi genellikle ilk cümlededir; baş
        cümle çıkarımı (lead extraction) bu alanda güçlü bir temel yöntemdir.
        """
        if not bloklar or not bloklar[0][1]:
            return ""
        _, metin = bloklar[0][1][0]
        cumleler = split_sentences(metin)[: config.atomic_summary_max_sentences]
        return truncate_words(" ".join(cumleler), config.atomic_summary_max_words)

    # ------------------------------------------------------------------
    def _birlestir(self, bloklar: list[tuple[str | None, list[tuple[str, str]]]]) -> str:
        """Her küme için bir cümle üretir ve kümedeki TÜM ID'leri atıf gösterir.

        Atıf listesi kümedeki tüm temsilcileri içerir: cümle o gönderilerin
        ortak içeriğinden seçildiği için hepsi meşru kaynaktır. Uydurma ID
        üretilmez (İlke 1'i sağlayıcı düzeyinde de bozmuyoruz).
        """
        cumleler: list[dict[str, object]] = []
        kalan_kelime = config.max_summary_words
        for etiket, temsilciler in bloklar:
            if not temsilciler or kalan_kelime <= 0:
                continue
            # Temsilciler arasında en uzun olanı seç: en çok bilgi taşıyan.
            post_id, metin = max(temsilciler, key=lambda t: len(t[1]))
            ilk_cumle = (split_sentences(metin) or [metin])[0]
            pay = min(kalan_kelime, max(12, config.max_summary_words // max(1, len(bloklar))))
            metin_kirpik = truncate_words(ilk_cumle, pay)
            kalan_kelime -= len(metin_kirpik.split())
            cumleler.append(
                {
                    "text": metin_kirpik,
                    "source_post_ids": [pid for pid, _ in temsilciler],
                    "_kume": etiket,
                }
            )
            _ = post_id  # seçim gerekçesi yukarıda; ID listesi tüm temsilcileri kapsar
        return json.dumps({"sentences": cumleler}, ensure_ascii=False)

    # ------------------------------------------------------------------
    def _asistan(self, bloklar: list[tuple[str | None, list[tuple[str, str]]]]) -> str:
        """Soruya bağlamdan çıkarımsal cevap üretir, bulamazsa çekimser kalır.

        Yöntem: soru ile her bağlam cümlesi arasındaki kelime örtüşmesi
        (Jaccard benzeri) hesaplanır. En iyi örtüşme eşiğin altındaysa
        REFUSAL_TOKEN döner — bu, İlke 2'nin sağlayıcı düzeyindeki karşılığıdır.
        """
        soru = ""
        baglam: list[tuple[str, str]] = []
        for _, ogeler in bloklar:
            for pid, metin in ogeler:
                if pid == "__SORU__":
                    soru = metin
                else:
                    baglam.append((pid, metin))

        if not baglam:
            return json.dumps({"answer": REFUSAL_TOKEN, "source_post_ids": []}, ensure_ascii=False)

        soru_kelimeleri = _kelime_kumesi(soru)
        if not soru_kelimeleri:
            # Soru yoksa "bu gönderi ne diyor" varsayılır: ilk gönderinin özeti.
            pid, metin = baglam[0]
            cevap = truncate_words(
                " ".join(split_sentences(metin)[:2]) or metin, config.max_assistant_words
            )
            return json.dumps({"answer": cevap, "source_post_ids": [pid]}, ensure_ascii=False)

        en_iyi_skor = 0.0
        en_iyi: tuple[str, str] | None = None
        for pid, metin in baglam:
            for cumle in split_sentences(metin) or [metin]:
                ortak = soru_kelimeleri & _kelime_kumesi(cumle)
                skor = len(ortak) / len(soru_kelimeleri)
                if skor > en_iyi_skor:
                    en_iyi_skor, en_iyi = skor, (pid, cumle)

        # Eşik 0.34: sorunun anlamlı kelimelerinin en az üçte biri bağlamda
        # geçmiyorsa cevabın bağlamda olmadığını varsayıyoruz. Bu değer
        # çıkarımsal yedeğe özgüdür; gerçek modelde karar modele aittir.
        if en_iyi is None or en_iyi_skor < 0.34:
            return json.dumps({"answer": REFUSAL_TOKEN, "source_post_ids": []}, ensure_ascii=False)

        pid, cumle = en_iyi
        return json.dumps(
            {
                "answer": truncate_words(cumle, config.max_assistant_words),
                "source_post_ids": [pid],
            },
            ensure_ascii=False,
        )


class HallucinatingFakeProvider(FakeProvider):
    """Kasıtlı olarak uydurma kaynak gösteren sağlayıcı — YALNIZCA TESTLER İÇİN.

    NEDEN VAR: Atıf denetiminin (summarize/citation.py) gerçekten çalıştığını
    kanıtlamanın tek yolu, denetime bozuk girdi vermektir. "Denetim var" demek
    yetmez; denetimin bir şeyi GERÇEKTEN eleyip elemediği test edilmelidir
    (spec 8: test_atifsiz_cumle_silinir).
    """

    name = "fake-hallucinating"

    def _birlestir(self, bloklar: list[tuple[str | None, list[tuple[str, str]]]]) -> str:
        temiz = json.loads(super()._birlestir(bloklar))
        temiz["sentences"].append(
            {"text": "Bu cümle var olmayan bir gönderiye atıf yapıyor.", "source_post_ids": ["p_yok_9999"]}
        )
        temiz["sentences"].append(
            {"text": "Bu cümlenin hiç kaynağı yok.", "source_post_ids": []}
        )
        return json.dumps(temiz, ensure_ascii=False)
