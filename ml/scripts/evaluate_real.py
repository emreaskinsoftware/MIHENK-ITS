"""GERÇEK metin ölçümü — sentetik değerlendirmenin şişirdiği payı sayar.

Sentetik test kümesi ve sentetik aktarım kümesi, iki sınıfı da BİZİM
yazdığımız şablonlardan üretiyor. Bu betik aynı modelleri iki tarafı da
gerçek olan bir kümede ölçer:
  insan       -> gerçek müşteri yorumları (CC BY-SA 4.0, 2022 derlemi)
  yapay_zeka  -> gerçek bir dil modelinin (Claude Opus 5) çıktısı

ÜÇ FARKLI EŞİK REJİMİ RAPORLANIR, ÇÜNKÜ ÜÇÜ DE FARKLI ŞEY SÖYLER:
  1. 0.5 sabit eşik      -> literatürle kıyaslanabilir ham sayı
  2. akış bandı          -> ÜRÜNÜN ŞU AN yaptığı şey. Bant akış dağılımında
                            (pozitif oran ~0.18) kalibre edildi, bu küme ise
                            farklı bir dağılım — uyumsuzluk KASITLI olarak
                            gösterilir: kalibrasyon dağılıma bağlıdır.
  3. bu kümede kalibre   -> "bu dağılım için ayarlansaydı ne olurdu". Eşik
                            kümenin YARISINDA seçilir, sonuç DİĞER yarısında
                            ölçülür.

AUROC ve FPR@95TPR eşikten bağımsızdır; modelin ayırt etme gücünü verir ve
üç rejimde de aynıdır.

Kullanım:
    python ml/scripts/evaluate_real.py
"""

from __future__ import annotations

import json
import statistics
from typing import Sequence

import _bootstrap  # noqa: F401

from app.config import config
from app.detection.calibration import aktif_bant, kalibrasyon_bolmesi
from app.detection.decision import karar_ver
from app.detection.detector import BerturkDetector, TfidfDetector

REPO_ROOT = _bootstrap.REPO_ROOT
VERI = REPO_ROOT / "ml" / "data" / "real_eval" / "dataset.jsonl"
SONUC_DIZINI = REPO_ROOT / "eval" / "results"
OLCULEMEDI = "[  ]"


def _yukle() -> list[dict]:
    if not VERI.exists():
        raise SystemExit(
            f"Küme yok: {VERI}\n"
            "Önce kurun: python ml/scripts/build_real_eval.py --brief / --assemble"
        )
    return [json.loads(s) for s in VERI.read_text(encoding="utf-8").splitlines() if s.strip()]


def _auroc(etiketler: Sequence[int], skorlar: Sequence[float]) -> float:
    ciftler = sorted(zip(skorlar, etiketler))
    poz = sum(etiketler)
    neg = len(etiketler) - poz
    if not poz or not neg:
        return float("nan")
    siralar = [0.0] * len(ciftler)
    i = 0
    while i < len(ciftler):
        j = i
        while j + 1 < len(ciftler) and ciftler[j + 1][0] == ciftler[i][0]:
            j += 1
        ortalama = (i + j) / 2 + 1
        for k in range(i, j + 1):
            siralar[k] = ortalama
        i = j + 1
    toplam = sum(r for r, (_, e) in zip(siralar, ciftler) if e == 1)
    return (toplam - poz * (poz + 1) / 2) / (poz * neg)


def _fpr_at_95tpr(etiketler: Sequence[int], skorlar: Sequence[float]) -> float:
    poz = [s for s, e in zip(skorlar, etiketler) if e == 1]
    neg = [s for s, e in zip(skorlar, etiketler) if e == 0]
    if not poz or not neg:
        return float("nan")
    esik = sorted(poz)[max(0, int(len(poz) * 0.05) - 1)] if len(poz) >= 20 else min(poz)
    return sum(1 for s in neg if s >= esik) / len(neg)


def _esik_ara(olasiliklar, etiketler, hedef: float, *, yon: str) -> float | None:
    basamaklar = [i * 0.01 for i in range(1, 100)]
    if yon == "alt":
        basamaklar = list(reversed(basamaklar))
    for esik in basamaklar:
        if yon == "ust":
            secilen = [e for p, e in zip(olasiliklar, etiketler) if p > esik]
            if secilen and sum(secilen) / len(secilen) >= hedef:
                return round(esik, 4)
        else:
            secilen = [e for p, e in zip(olasiliklar, etiketler) if p < esik]
            if secilen and sum(1 - e for e in secilen) / len(secilen) >= hedef:
                return round(esik, 4)
    return None


def _bant_olc(metinler, olasiliklar, etiketler, alt, ust) -> tuple[float, float]:
    etiketli = []
    for metin, olasilik, etiket in zip(metinler, olasiliklar, etiketler):
        karar = karar_ver(metin, olasilik, bant=(alt, ust))
        if not karar.abstained:
            etiketli.append((karar.label == "yz_olasi", etiket))
    if not etiketli:
        return 0.0, float("nan")
    dogru = sum(1 for yz, e in etiketli if yz == bool(e))
    return len(etiketli) / len(etiketler), dogru / len(etiketli)


def _s(x: float) -> str:
    return OLCULEMEDI if x != x else f"{x:.3f}"


def main() -> None:
    ornekler = _yukle()
    metinler = [o["text"] for o in ornekler]
    etiketler = [1 if o["label"] == "yapay_zeka" else 0 for o in ornekler]
    kovalar = [o["bucket"] for o in ornekler]

    print(
        f"gerçek küme: {len(ornekler)} örnek "
        f"(yapay_zeka {sum(etiketler)}, insan {len(etiketler)-sum(etiketler)}) "
        f"| pozitif oran {sum(etiketler)/len(etiketler):.3f}"
    )

    satirlar = [
        "# Gerçek Metin Ölçümü — sentetik değerlendirmenin şişirdiği pay",
        "",
        "> `ml/scripts/evaluate_real.py` tarafından üretilir. Elle düzenlenmez.",
        "",
        "## Küme",
        "",
        f"**{len(ornekler)}** örnek — yapay_zeka {sum(etiketler)}, "
        f"insan {len(etiketler)-sum(etiketler)} (pozitif oran "
        f"{sum(etiketler)/len(etiketler):.3f}).",
        "",
        "| Sınıf | Kaynak | Köken |",
        "|---|---|---|",
        "| insan | `turkish-nlp-suite/vitamins-supplements-reviews` (CC BY-SA 4.0) | "
        "gerçek müşteriler, 2022 derlemi — dil modelleri yaygınlaşmadan önce |",
        "| yapay_zeka | Claude Opus 5 | aynı ürün, aynı uzunluk, aynı yıldız puanı "
        "eşleştirmesiyle üretildi |",
        "",
        "Eşleştirme zorunluydu: iki sınıf farklı konulardan ya da farklı",
        "duygulardan gelseydi model yazarı değil KONUYU ya da DUYGUYU öğrenirdi.",
        "Üretimde üslup da dağıtıldı (samimi, yazım hatalı, asistan ağzı,",
        "pazarlama dili, dengeli); düz asistan ağzı bilerek azınlıkta tutuldu,",
        "çünkü tespiti yalnızca en kolay üslupta ölçmek kendimizi kandırmak olurdu.",
        "",
    ]

    modeller = []
    for ad, sinif in (("TF-IDF temel çizgi", TfidfDetector), ("BERTurk ince ayar", BerturkDetector)):
        try:
            model = sinif()
        except Exception as hata:
            print(f"  {ad}: model yok ({hata.__class__.__name__}) — tabloda {OLCULEMEDI}")
            continue
        skorlar = model.predict_proba(metinler)
        modeller.append((ad, model, skorlar))
        print(f"  {ad}: ölçüldü")

    if not modeller:
        raise SystemExit("hiçbir model yüklenemedi")

    # --- 1) Eşikten bağımsız ayırt etme gücü ---
    satirlar += [
        "## 1. Ayırt etme gücü (eşikten bağımsız)",
        "",
        "| Model | AUROC | FPR@95TPR | Doğruluk (0.5 eşiği) | F1 (0.5) |",
        "|---|---|---|---|---|",
    ]
    for ad, _model, skorlar in modeller:
        tahmin = [1 if s >= 0.5 else 0 for s in skorlar]
        dog = sum(1 for g, t in zip(etiketler, tahmin) if g == t) / len(etiketler)
        tp = sum(1 for g, t in zip(etiketler, tahmin) if g == 1 and t == 1)
        fp = sum(1 for g, t in zip(etiketler, tahmin) if g == 0 and t == 1)
        fn = sum(1 for g, t in zip(etiketler, tahmin) if g == 1 and t == 0)
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
        satirlar.append(
            f"| {ad} | {_s(_auroc(etiketler, skorlar))} | "
            f"{_s(_fpr_at_95tpr(etiketler, skorlar))} | {_s(dog)} | {_s(f1)} |"
        )

    # --- Uzunluk kovası ---
    satirlar += [
        "",
        "### Uzunluk kovası bazında doğruluk (0.5 eşiği)",
        "",
        "| Model | K1 (20-50 token) | K2 (50-100) | K3 (100+) |",
        "|---|---|---|---|",
    ]
    for ad, _model, skorlar in modeller:
        hucre = []
        for kova in ("K1", "K2", "K3"):
            idx = [i for i, k in enumerate(kovalar) if k == kova]
            hucre.append(
                sum(1 for i in idx if (skorlar[i] >= 0.5) == bool(etiketler[i])) / len(idx)
                if idx
                else float("nan")
            )
        satirlar.append(f"| {ad} | {_s(hucre[0])} | {_s(hucre[1])} | {_s(hucre[2])} |")

    # --- 2) Ürünün ŞU AN yaptığı: akışta kalibre edilmiş bant ---
    satirlar += [
        "",
        "## 2. Ürünün şu an yaptığı — akış bandı bu kümeye uygulanırsa",
        "",
        "Bant akış dağılımında (pozitif oran ~0.18) kalibre edildi; bu küme",
        f"farklı bir dağılım (pozitif oran {sum(etiketler)/len(etiketler):.2f}).",
        "Uyumsuzluk kasıtlı olarak gösteriliyor: **kalibrasyon dağılıma bağlıdır**,",
        "bir dağılımda seçilen eşik başka bir dağılıma taşınamaz.",
        "",
        "| Model | Akış bandı | Etiketlenen | Etiketlendiğinde doğruluk |",
        "|---|---|---|---|",
    ]
    for ad, model, skorlar in modeller:
        alt, ust = aktif_bant(model.name)
        oran, dogruluk = _bant_olc(metinler, skorlar, etiketler, alt, ust)
        satirlar.append(
            f"| {ad} | `[{alt}, {ust}]` | {oran:.1%} | {_s(dogruluk)} |"
        )

    # --- 3) Bu dağılım için kalibre edilseydi ---
    satirlar += [
        "",
        "## 3. Bu dağılım için kalibre edilseydi",
        "",
        "Eşik kümenin bir yarısında seçilir, sonuç **diğer yarısında** ölçülür",
        "(bölme `app/detection/calibration.kalibrasyon_bolmesi`, akışta",
        "kullanılanın aynısı). Hedef: etiket gösterildiğinde doğruluk ≥ 0.95.",
        "",
        "| Model | Kalibre bant | Etiketlenen | Etiketlendiğinde doğruluk |",
        "|---|---|---|---|",
    ]
    (kx, ky), (ox, oy) = kalibrasyon_bolmesi(list(zip(metinler, kovalar)), etiketler)
    kalib_metin = [m for m, _ in kx]
    olcum_metin = [m for m, _ in ox]
    for ad, model, _skorlar in modeller:
        pk = model.predict_proba(kalib_metin)
        po = model.predict_proba(olcum_metin)
        alt = _esik_ara(pk, ky, 0.95, yon="alt")
        ust = _esik_ara(pk, ky, 0.95, yon="ust")
        oran, dogruluk = _bant_olc(olcum_metin, po, oy, alt, ust)
        satirlar.append(f"| {ad} | `[{alt}, {ust}]` | {oran:.1%} | {_s(dogruluk)} |")

    satirlar += [
        "",
        f"Ölçüm yarısı: {len(oy)} örnek (kalibrasyon yarısı {len(ky)}).",
        "",
    ]

    # --- 4) Üslup bazında yakalanma ---
    # RAPORA GİREN EN EYLEME DÖNÜK BULGU: hangi üslup tespitten kaçıyor.
    # Saldırgan modele nasıl yazdırırsa yakalanmaz sorusunun cevabı budur.
    usluplar = sorted({o["style"] for o in ornekler if o.get("style")})
    if usluplar:
        satirlar += [
            "## 4. Üslup bazında yakalanma oranı (yalnızca yapay zekâ sınıfı)",
            "",
            "Yapay zekâ metinleri beş farklı üslupta üretildi. Aşağıdaki sayı,",
            "o üsluptaki metinlerin kaçının 0.5 eşiğinde 'yapay zekâ' olarak",
            "işaretlendiğidir. Düşük sayı = o üslup tespitten kaçıyor.",
            "",
            "| Üslup | n | " + " | ".join(ad for ad, _m, _s in modeller) + " |",
            "|---|---|" + "---|" * len(modeller),
        ]
        for uslup in usluplar:
            idx = [i for i, o in enumerate(ornekler) if o.get("style") == uslup]
            hucreler = []
            for _ad, _model, skorlar in modeller:
                yakalanan = sum(1 for i in idx if skorlar[i] >= 0.5)
                hucreler.append(f"{yakalanan/len(idx):.3f}" if idx else OLCULEMEDI)
            satirlar.append(f"| `{uslup}` | {len(idx)} | " + " | ".join(hucreler) + " |")
        satirlar += [
            "",
            "Ortalama olasılık (yüksek = model daha çok 'yapay zekâ' diyor):",
            "",
            "| Üslup | " + " | ".join(ad for ad, _m, _s in modeller) + " |",
            "|---|" + "---|" * len(modeller),
        ]
        for uslup in usluplar:
            idx = [i for i, o in enumerate(ornekler) if o.get("style") == uslup]
            hucreler = [
                f"{statistics.mean(skorlar[i] for i in idx):.3f}" if idx else OLCULEMEDI
                for _ad, _model, skorlar in modeller
            ]
            satirlar.append(f"| `{uslup}` | " + " | ".join(hucreler) + " |")
        satirlar.append("")

    satirlar += [
        "## Sınırlılıklar",
        "",
        "1. **Tek üretici.** Yapay zekâ tarafı yalnızca Claude Opus 5 ile üretildi.",
        "   Bu küme üzerinde EĞİTİM yapılırsa çıkan model 'yapay zekâ tespiti'",
        "   değil 'Claude tespiti' yapar. Buradaki kullanım yalnızca ÖLÇÜMDÜR:",
        "   modeller sentetik veriyle eğitildi, bu küme onlara hiç gösterilmedi.",
        "   Genellenebilir bir iddia için en az üç üretici ve biri sınava saklanmış",
        "   olmalıdır.",
        "2. **Tür kayması.** İnsan tarafı ürün yorumu, eğitim verisi ise sosyal",
        "   medya gönderisi. Mutlak sayılar bu kaymayı da içerir. İnsan/yapay zekâ",
        "   karşılaştırması yine de kontrollüdür: tür kayması iki sınıfı da eşit",
        "   etkiler.",
        "3. **Köken kesinliği tam değil.** 2022 derlemi, dil modellerinin",
        "   yaygınlaşmasından önceye denk gelir ama tek tek her yorumun insan",
        "   yazımı olduğu kanıtlanamaz.",
        "4. **Küme küçük.** ~370 örnek; oranların güven aralığı geniştir.",
        "",
    ]

    SONUC_DIZINI.mkdir(parents=True, exist_ok=True)
    (SONUC_DIZINI / "real_text.md").write_text("\n".join(satirlar) + "\n", encoding="utf-8")

    veri = {
        "size": len(ornekler),
        "positive": sum(etiketler),
        "models": [
            {
                "model": ad,
                "auroc": _auroc(etiketler, sk),
                "fpr_at_95tpr": _fpr_at_95tpr(etiketler, sk),
                "accuracy_at_0.5": sum(
                    1 for g, s in zip(etiketler, sk) if (s >= 0.5) == bool(g)
                )
                / len(etiketler),
            }
            for ad, _m, sk in modeller
        ],
    }
    (SONUC_DIZINI / "real_text.json").write_text(
        json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  -> eval/results/real_text.md")


if __name__ == "__main__":
    main()
