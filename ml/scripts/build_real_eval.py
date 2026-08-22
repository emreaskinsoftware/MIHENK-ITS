"""GERÇEK metin değerlendirme kümesi — sentetik değerlendirmenin kapalı döngüsünü kırar.

NEDEN BU KÜME VAR (projenin en büyük açığı buydu):
`build_dataset.py` iki sınıfı da BİZİM yazdığımız şablonlardan üretiyor.
"İnsan" sınıfı gerçek bir insanın yazdığı metin değil, "insan böyle yazar"
hipotezimizin taklidi; "yapay_zeka" sınıfı da gerçek bir model çıktısı değil,
"model böyle yazar" hipotezimizin taklidi. Model bu ikisini %100 ayırıyor ama
bu bir başarı değil: iki şablon ailesi ayrılabilir olsun diye tasarlanmıştı.
Aktarım testi bile döngüyü kırmıyor, çünkü ikinci şablon havuzunu da aynı
kalem yazdı.

Bu küme iki tarafı da GERÇEK yapar:
  insan       -> gerçek müşterilerin yazdığı ürün yorumları (aşağıdaki derlem)
  yapay_zeka  -> gerçek bir dil modelinin (Claude Opus 5) ürettiği yorumlar

--- İNSAN TARAFI: KAYNAK VE LİSANS -------------------------------------------
turkish-nlp-suite/vitamins-supplements-reviews — CC BY-SA 4.0
Duygu Altinok, "A Diverse Set of Freely Available Linguistic Resources for
Turkish", ACL 2023. https://aclanthology.org/2023.acl-long.768/

KÖKEN GÜVENİLİRLİĞİ: Derlem 2022'de, dil modelleri yaygınlaşmadan önce
toplanmıştır. 2023 sonrası toplanmış bir web derlemi zaten yapay zekâ metni
içerebilir ve onu "insan" diye etiketlemek veri setini sessizce zehirlerdi.
Derlemi hazırlayanlar kişi adlarını ayrıca temizlemiştir.

METİNLER DEPOYA İŞLENMEZ: Bu betik derlemi indirir ve deterministik olarak
örnekler. Paylaşımlı-lisans (share-alike) yükümlülüğü doğurmamak için insan
metinleri repoya konmaz; yeniden üretilebilirlik betiğin kendisiyle sağlanır.

--- YAPAY ZEKÂ TARAFI: EŞLEŞTİRME --------------------------------------------
Her yapay zekâ metni bir insan metniyle EŞLEŞTİRİLİR: aynı ürün, aynı uzunluk
kovası, aynı yıldız puanı. Eşleştirme olmasaydı model yazarı değil KONUYU ya
da DUYGUYU öğrenirdi — alanın klasik tuzağı budur. Eşleştirmeyle tek değişken
yazar olarak kalır.

Üslup çeşitliliği zorunludur: modele düz "yorum yaz" dersen hep asistan
ağzıyla yazar ve tespit yapay olarak kolaylaşır. Şartname bu yüzden üslubu da
dağıtır (samimi, yazım hatalı, pazarlama dili...), ağırlık ZOR olanlarda.

Kullanım:
    python ml/scripts/build_real_eval.py --brief     # 1) üretim şartnamesi
    #    (yapay zekâ metinleri ai_raw.jsonl'e yazılır)
    python ml/scripts/build_real_eval.py --assemble  # 2) nihai küme
"""

from __future__ import annotations

import argparse
import json
import random
import urllib.request
from pathlib import Path

import _bootstrap  # noqa: F401

from app.textutil import count_tokens

REPO_ROOT = _bootstrap.REPO_ROOT
DIZIN = REPO_ROOT / "ml" / "data" / "real_eval"
PARQUET = DIZIN / "_kaynak_yorumlar.parquet"
BRIEF = DIZIN / "gen_brief.json"
AI_HAM = DIZIN / "ai_raw.jsonl"
CIKTI = DIZIN / "dataset.jsonl"

PARQUET_URL = (
    "https://huggingface.co/api/datasets/turkish-nlp-suite/"
    "vitamins-supplements-reviews/parquet/default/train/0.parquet"
)

# Kova başına hedef örnek sayısı. K3 derlemede zaten seyrek (216 aday), o
# yüzden küçük tutuldu; olmayan örnek uydurmuyoruz.
HEDEF = {"K1": 130, "K2": 55, "K3": 15}

# Üslup dağılımı. ASISTAN (düz asistan ağzı) bilerek AZINLIKTA: gerçek bir
# kötüye kullanım senaryosunda saldırgan modele "samimi yaz" der. Tespiti
# yalnızca asistan ağzında ölçmek, kendimizi kandırmak olurdu.
USLUPLAR = (
    ("samimi", 30),
    ("hatali", 25),
    ("asistan", 20),
    ("pazarlama", 13),
    ("dengeli", 12),
)

USLUP_TARIFI = {
    "samimi": "gündelik, sohbet eder gibi, kısa cümleler",
    "hatali": "samimi + yazım/noktalama hataları, küçük harfle başlama",
    "asistan": "düzgün, dengeli, kurallı yapay zekâ asistanı üslubu",
    "pazarlama": "abartılı övgü, ünlem, tavsiye dili",
    "dengeli": "artı ve eksileri sıralayan ölçülü değerlendirme",
}


def _kova(token_sayisi: int) -> str:
    if token_sayisi < 50:
        return "K1"
    if token_sayisi < 100:
        return "K2"
    return "K3"


def _parquet_indir() -> None:
    if PARQUET.exists():
        return
    DIZIN.mkdir(parents=True, exist_ok=True)
    print(f"derlem indiriliyor -> {PARQUET.name}")
    urllib.request.urlretrieve(PARQUET_URL, PARQUET)


def insan_ornekle(tohum: int) -> list[dict]:
    """Derlemden deterministik, kova-katmanlı, ürün-çeşitli örnekleme."""
    import pyarrow.parquet as pq

    _parquet_indir()
    tablo = pq.read_table(PARQUET)
    metinler = tablo.column("text").to_pylist()
    urunler = tablo.column("product_name").to_pylist()
    yildizlar = tablo.column("star").to_pylist()

    adaylar: dict[str, list[dict]] = {"K1": [], "K2": [], "K3": []}
    gorulen: set[str] = set()
    for metin, urun, yildiz in zip(metinler, urunler, yildizlar):
        metin = (metin or "").strip()
        if not metin:
            continue
        n = count_tokens(metin)
        if n < 20:  # min_detection_tokens altı zaten hiç etiketlenmez
            continue
        anahtar = " ".join(metin.lower().split())
        if anahtar in gorulen:  # birebir yineleme
            continue
        gorulen.add(anahtar)
        adaylar[_kova(n)].append(
            {"text": metin, "product": urun, "star": yildiz, "tokens": n}
        )

    rng = random.Random(tohum)
    secilen: list[dict] = []
    for kova, hedef in HEDEF.items():
        havuz = adaylar[kova]
        rng.shuffle(havuz)
        # Ürün başına en fazla 2: tek bir ürünün yorum üslubu kümeye hâkim olmasın.
        sayac: dict[str, int] = {}
        for aday in havuz:
            if len(secilen) >= sum(HEDEF[k] for k in list(HEDEF)[: list(HEDEF).index(kova) + 1]):
                break
            if sayac.get(aday["product"], 0) >= 2:
                continue
            sayac[aday["product"]] = sayac.get(aday["product"], 0) + 1
            aday["bucket"] = kova
            secilen.append(aday)
    return secilen


def brief_uret(tohum: int) -> None:
    """İnsan örneklemini seçer ve yapay zekâ tarafı için şartname yazar."""
    insanlar = insan_ornekle(tohum)
    rng = random.Random(tohum + 1)
    havuz = [u for u, agirlik in USLUPLAR for _ in range(agirlik)]

    kayitlar = []
    for i, insan in enumerate(insanlar):
        uslup = rng.choice(havuz)
        kayitlar.append(
            {
                "id": f"r{i:04d}",
                "product": insan["product"],
                "star": insan["star"],
                "target_tokens": insan["tokens"],
                "bucket": insan["bucket"],
                "style": uslup,
                "style_desc": USLUP_TARIFI[uslup],
            }
        )

    DIZIN.mkdir(parents=True, exist_ok=True)
    BRIEF.write_text(
        json.dumps(
            {
                "seed": tohum,
                "n": len(kayitlar),
                "human_sample": insanlar,
                "items": kayitlar,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    dagilim: dict[str, int] = {}
    for k in kayitlar:
        dagilim[k["style"]] = dagilim.get(k["style"], 0) + 1
    kova_dag: dict[str, int] = {}
    for k in kayitlar:
        kova_dag[k["bucket"]] = kova_dag.get(k["bucket"], 0) + 1
    print(f"insan örneklemi: {len(insanlar)} | kova {kova_dag}")
    print(f"üslup dağılımı: {dagilim}")
    print(f"şartname -> {BRIEF}")
    print(f"SONRAKİ ADIM: yapay zekâ metinlerini {AI_HAM.name} içine yaz "
          '(satır başına {"id": "...", "text": "..."}), sonra --assemble.')


def birlestir() -> None:
    """İnsan örneklemi + üretilen yapay zekâ metinlerini tek kümede toplar."""
    if not BRIEF.exists():
        raise SystemExit(f"Şartname yok: {BRIEF} — önce --brief çalıştırın.")
    if not AI_HAM.exists():
        raise SystemExit(f"Yapay zekâ metinleri yok: {AI_HAM}")

    brief = json.loads(BRIEF.read_text(encoding="utf-8"))
    uslup_by_id = {k["id"]: k for k in brief["items"]}

    ai_by_id: dict[str, str] = {}
    for satir in AI_HAM.read_text(encoding="utf-8").splitlines():
        if not satir.strip():
            continue
        kayit = json.loads(satir)
        ai_by_id[kayit["id"]] = kayit["text"].strip()

    ornekler = []
    for i, insan in enumerate(brief["human_sample"]):
        ornekler.append(
            {
                "id": f"h{i:04d}",
                "text": insan["text"],
                "label": "insan",
                "bucket": insan["bucket"],
                "token_count": insan["tokens"],
                "source": "turkish-nlp-suite/vitamins-supplements-reviews (CC BY-SA 4.0)",
            }
        )

    atlanan = 0
    for kimlik, metin in sorted(ai_by_id.items()):
        n = count_tokens(metin)
        if n < 20:  # kısa metin karar katmanında zaten etiketlenmez
            atlanan += 1
            continue
        ornekler.append(
            {
                "id": kimlik,
                "text": metin,
                "label": "yapay_zeka",
                "bucket": _kova(n),
                "token_count": n,
                "source": "Claude Opus 5",
                "style": uslup_by_id.get(kimlik, {}).get("style"),
            }
        )

    CIKTI.write_text(
        "\n".join(json.dumps(o, ensure_ascii=False) for o in ornekler) + "\n",
        encoding="utf-8",
    )
    insan = sum(1 for o in ornekler if o["label"] == "insan")
    yz = len(ornekler) - insan
    print(f"küme -> {CIKTI}")
    print(f"  insan={insan} yapay_zeka={yz} (20 token altı atlanan yz: {atlanan})")
    kova: dict[str, int] = {}
    for o in ornekler:
        kova[o["bucket"]] = kova.get(o["bucket"], 0) + 1
    print(f"  kova dağılımı: {kova}")


def main() -> None:
    a = argparse.ArgumentParser(description="Gerçek metin değerlendirme kümesi")
    a.add_argument("--brief", action="store_true", help="İnsan örneklemi + üretim şartnamesi")
    a.add_argument("--assemble", action="store_true", help="Nihai kümeyi birleştir")
    a.add_argument("--seed", type=int, default=20260824)
    args = a.parse_args()

    if args.brief:
        brief_uret(args.seed)
    elif args.assemble:
        birlestir()
    else:
        a.error("--brief veya --assemble verin")


if __name__ == "__main__":
    main()
