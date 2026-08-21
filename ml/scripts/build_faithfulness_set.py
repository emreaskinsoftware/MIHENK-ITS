"""Sadakat ve reddetme değerlendirme örneklemini üretir (spec 7 / eval/faithfulness_set.json).

ÖRNEKLEM İKİ TÜR SORU İÇERİR:

1. `answerable: true`  — cevabı gönderi bağlamında BULUNAN sorular.
   Ölçtüğü şey: sistem gereksiz yere susuyor mu (aşırı çekimserlik).
   Aşırı çekimserlik de bir başarısızlıktır: hiçbir şeye cevap vermeyen bir
   asistan İlke 2'yi mükemmel uygular ama işe yaramaz.

2. `answerable: false` — cevabı bağlamda OLMAYAN sorular.
   Ölçtüğü şey: doğru reddetme oranı (rapor Tablo 5).

Sorular gönderi metninden türetilir, bu yüzden örneklem akış yeniden
üretildiğinde de tutarlı kalır. Metin anlık görüntüsü (`post_text`) dosyaya
yazılır ki gönderi kimlikleri değişirse uyumsuzluk fark edilsin.

SINIRLILIK (rapora yazılacak): Sorular otomatik türetilmiştir; insan
değerlendirmesinin yerini tutmaz. `manual_label` alanı boş bırakılır ve
5 kişilik kullanılabilirlik testinde elle doldurulur (spec 7, Tablo 7).

Kullanım:
    python ml/scripts/build_faithfulness_set.py --per-category 12
"""

from __future__ import annotations

import argparse
import json
import random

import _bootstrap  # noqa: F401

from app.enrichment.topics import keywords
from app.store.feed_repo import load_feed
from app.textutil import split_sentences

REPO_ROOT = _bootstrap.REPO_ROOT
CIKTI = REPO_ROOT / "eval" / "faithfulness_set.json"

# Bağlam dışı sorular: hiçbir gönderide cevabı olmayan, ama makul görünen
# sorular. Makullük önemli — "asdf" gibi anlamsız bir soruyu reddetmek
# marifet değildir; ölçüm ancak gerçekçi sorularla anlam taşır.
BAGLAM_DISI_SORULAR = [
    "Dolar kuru bugün kaç lira oldu?",
    "Bu konuda mahkeme ne karar verdi?",
    "Toplam bütçe kaç milyon lira?",
    "Bakanlık bu konuda ne açıklama yaptı?",
    "Geçen yıl aynı dönemde ne olmuştu?",
    "Kaç kişi bu durumdan etkilendi?",
    "Yarın hava nasıl olacak?",
    "Bu kararın yasal dayanağı nedir?",
    "Anket sonuçları ne gösteriyor?",
    "Yetkililerin telefon numarası nedir?",
]


def soru_uret(metin: str, rng: random.Random) -> str | None:
    """Gönderi metninden cevabı bağlamda bulunan bir soru türetir.

    Yöntem: metnin anahtar kelimelerinden biri seçilir ve etrafına soru kalıbı
    kurulur. Basit ama amaca uygun: soru, gönderide GEÇEN bir şeyi sorar, yani
    cevabı tanım gereği bağlamdadır.
    """
    anahtarlar = keywords(metin, limit=3)
    if not anahtarlar:
        return None
    anahtar = anahtarlar[0]
    kalip = rng.choice(
        [
            "{k} hakkında ne deniyor?",
            "{k} konusunda ne yazılmış?",
            "Bu gönderide {k} ile ilgili ne var?",
        ]
    )
    return kalip.format(k=anahtar)


def main() -> None:
    ayristirici = argparse.ArgumentParser(description="Sadakat örneklemini üretir")
    ayristirici.add_argument("--per-category", type=int, default=12)
    ayristirici.add_argument("--seed", type=int, default=20260824)
    args = ayristirici.parse_args()

    rng = random.Random(args.seed)
    depo = load_feed()
    ogeler: list[dict] = []
    sayac = 0

    for kategori in ("gundem", "spor", "kisisel"):
        adaylar = [
            p
            for p in depo.by_category(kategori)  # type: ignore[arg-type]
            # Enjeksiyon taşıyan gönderiler ayrı kümede ölçülür (injection_suite);
            # sadakat ölçümüne karıştırmıyoruz ki iki etki birbirine karışmasın.
            if not p.eval_has_injection and len(split_sentences(p.text)) >= 1
        ]
        secilen = rng.sample(adaylar, min(args.per_category, len(adaylar)))
        for post in secilen:
            soru = soru_uret(post.text, rng)
            if soru is None:
                continue
            sayac += 1
            ogeler.append(
                {
                    "id": f"f{sayac:03d}",
                    "post_id": post.id,
                    "post_text": post.text,
                    "category": kategori,
                    "question": soru,
                    "answerable": True,
                    "expected_source_ids": [post.id],
                    "manual_label": None,  # elle değerlendirme için boş
                }
            )
            sayac += 1
            ogeler.append(
                {
                    "id": f"f{sayac:03d}",
                    "post_id": post.id,
                    "post_text": post.text,
                    "category": kategori,
                    "question": rng.choice(BAGLAM_DISI_SORULAR),
                    "answerable": False,
                    "expected_source_ids": [],
                    "manual_label": None,
                }
            )

    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text(
        json.dumps(
            {
                "meta": {
                    "seed": args.seed,
                    "per_category": args.per_category,
                    "note": (
                        "Sorular otomatik türetilmiştir; manual_label alanı elle "
                        "değerlendirme içindir. Ölçüm: ml/scripts/evaluate.py"
                    ),
                },
                "items": ogeler,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    cevaplanabilir = sum(1 for o in ogeler if o["answerable"])
    print(f"{len(ogeler)} örnek yazıldı ({cevaplanabilir} cevaplanabilir) -> {CIKTI}")


if __name__ == "__main__":
    main()
