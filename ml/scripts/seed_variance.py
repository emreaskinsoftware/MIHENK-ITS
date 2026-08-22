"""Tohum değişkenliğini AKTARIM kümesinde ölçer (spec 7).

NEDEN BU BETİK VAR — DOĞRULAMA KÜMESİ DEĞİŞKENLİĞİ GÖREMİYOR:
`train_detector.py --seeds 5` doğrulama kümesinde 1.000 ± 0.000 raporluyor.
Bu sayı, modelin kararlı olduğunu DEĞİL, doğrulama kümesinin doyduğunu
gösteriyor. Aynı beş model akış üzerinde ölçüldüğünde aktarım doğruluğu
0.31 ile 0.69 arasında salınıyor. "± 0.000" yazıp geçmek, olmayan bir
kararlılık iddia etmek olurdu (spec 2).

ÖLÇÜLEN İKİNCİ SORU — KALİBRASYON BU SALINIMI TOPARLIYOR MU:
Evet, ve nereye taşıdığı önemli. Sabit bantla "etiketlendiğinde doğruluk"
tohuma göre savruluyor; kalibre bantla neredeyse sabitleniyor, salınım
KAPSAMA (etiketlenen gönderi oranı) geçiyor. Ürün açısından doğru takas
budur: kötü tohum yanlış etiketlemek yerine susar (İlke 2).

Her tohum için model sıfırdan eğitilir; betik sonunda BELGELENMİŞ VARSAYILAN
TOHUM geri yüklenir, yani diskte kalan model her koşuda aynıdır.

Kullanım:
    python ml/scripts/seed_variance.py
    python ml/scripts/seed_variance.py --seeds 20260824 20260825
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from typing import Sequence

import _bootstrap  # noqa: F401

from app.config import config
from app.detection.calibration import kalibrasyon_bolmesi
from app.detection.detector import BerturkDetector, reset_detector
from app.store.feed_repo import load_feed

REPO_ROOT = _bootstrap.REPO_ROOT
CIKTI = REPO_ROOT / "ml" / "artifacts" / "seed_variance_berturk.json"

VARSAYILAN_TOHUMLAR = [20260824, 20260825, 20260826, 20260827, 20260828]
# Diskte bırakılacak model bu tohuma ait olur. Aktarım başarımına bakarak
# tohum SEÇMİYORUZ: seçim ölçtüğümüz kümede yapılırsa rapor edilen sayı
# artık o modelin başarımı değil, seçimin kendisidir.
VARSAYILAN_TOHUM = 20260824


def _egit(tohum: int) -> None:
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "ml" / "scripts" / "train_detector.py"),
         "--backend", "berturk", "--seed", str(tohum), "--bastan"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _auroc(etiketler: Sequence[int], skorlar: Sequence[float]) -> float:
    """Sıra tabanlı AUROC (beraberlikler ortalama sıra alır)."""
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


def main() -> None:
    ayristirici = argparse.ArgumentParser(description="Tohum değişkenliğini aktarımda ölçer")
    ayristirici.add_argument("--seeds", type=int, nargs="+", default=VARSAYILAN_TOHUMLAR)
    ayristirici.add_argument("--hedef-kesinlik", type=float, default=0.95)
    args = ayristirici.parse_args()

    # calibrate_threshold içindeki eşik arama ve bant ölçme mantığını tekrar
    # yazmıyoruz: iki betik ayrışırsa sayılar sessizce kayar.
    sys.path.insert(0, str(REPO_ROOT / "ml" / "scripts"))
    from calibrate_threshold import (
        _esik_ara,
        akis_verisi,
        bant_olc,
        uzunluk_gecenler,
    )

    metinler, etiketler = akis_verisi()
    (kx, ky), (ox, oy) = kalibrasyon_bolmesi(metinler, etiketler)
    print(
        f"akış={len(etiketler)} | kalibrasyon={len(ky)} ölçüm={len(oy)} | "
        f"tohum={len(args.seeds)} hedef kesinlik={args.hedef_kesinlik}"
    )

    kosular = []
    for tohum in args.seeds:
        _egit(tohum)
        reset_detector()
        model = BerturkDetector()
        pk, po = model.predict_proba(kx), model.predict_proba(ox)

        ham_dogruluk = sum((p >= 0.5) == bool(e) for p, e in zip(po, oy)) / len(oy)
        gp, ge = uzunluk_gecenler(kx, pk, ky)
        alt = _esik_ara(gp, ge, args.hedef_kesinlik, yon="alt")
        ust = _esik_ara(gp, ge, args.hedef_kesinlik, yon="ust")
        sabit_oran, sabit_dogruluk = bant_olc(
            ox, po, oy, config.abstain_low, config.abstain_high
        )
        kalib_oran, kalib_dogruluk = bant_olc(ox, po, oy, alt, ust)

        kosular.append({
            "seed": tohum,
            "transfer_accuracy_at_0.5": round(ham_dogruluk, 4),
            "transfer_auroc": round(_auroc(oy, po), 4),
            "fixed_band": {
                "labeled_rate": round(sabit_oran, 4),
                "accuracy_when_labeled": round(sabit_dogruluk, 4),
            },
            "calibrated_band": {
                "band": [alt, ust],
                "labeled_rate": round(kalib_oran, 4),
                "accuracy_when_labeled": round(kalib_dogruluk, 4),
            },
        })
        print(
            f"  tohum {tohum}: aktarım(0.5)={ham_dogruluk:.3f} "
            f"| sabit bant doğruluk={sabit_dogruluk:.3f} (kapsam {sabit_oran:.0%}) "
            f"| kalibre [{alt},{ust}] doğruluk={kalib_dogruluk:.3f} (kapsam {kalib_oran:.0%})",
            flush=True,
        )

    def _ozet(cikar) -> dict[str, float]:
        degerler = [cikar(k) for k in kosular]
        return {
            "mean": round(statistics.mean(degerler), 4),
            "std": round(statistics.pstdev(degerler), 4),
            "min": round(min(degerler), 4),
            "max": round(max(degerler), 4),
        }

    ozet = {
        "transfer_accuracy_at_0.5": _ozet(lambda k: k["transfer_accuracy_at_0.5"]),
        "transfer_auroc": _ozet(lambda k: k["transfer_auroc"]),
        "fixed_band_accuracy_when_labeled": _ozet(
            lambda k: k["fixed_band"]["accuracy_when_labeled"]
        ),
        "calibrated_band_accuracy_when_labeled": _ozet(
            lambda k: k["calibrated_band"]["accuracy_when_labeled"]
        ),
        "calibrated_band_labeled_rate": _ozet(
            lambda k: k["calibrated_band"]["labeled_rate"]
        ),
    }
    print()
    for ad, d in ozet.items():
        print(f"  {ad:<42} {d['mean']:.3f} ± {d['std']:.3f}  [{d['min']:.3f}, {d['max']:.3f}]")

    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text(
        json.dumps(
            {
                "seeds": args.seeds,
                "target_precision": args.hedef_kesinlik,
                "holdout_size": len(oy),
                "runs": kosular,
                "summary": ozet,
                "note": (
                    "Doğrulama kümesinde aynı tohumlar 1.000 ± 0.000 verir; "
                    "değişkenlik yalnızca aktarımda görünür."
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nkayıt -> {CIKTI}")

    _egit(VARSAYILAN_TOHUM)
    reset_detector()
    print(f"diskteki model geri yüklendi: tohum {VARSAYILAN_TOHUM} (belgelenmiş varsayılan)")


if __name__ == "__main__":
    main()
