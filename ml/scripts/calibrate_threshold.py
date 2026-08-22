"""Karar bandını dağıtım dağılımında kalibre eder (spec 6.5, İlke 2).

NEDEN BU BETİK VAR — ÖLÇÜLEN SORUN:
Eğitim ve doğrulama kümesi sınıf-dengelidir (pozitif oran ~0.49). Sistemin
gerçekte üzerinde çalıştığı akışta ise gönderilerin yalnızca ~%18'i yapay
zekâ ürünüdür. Model olasılıkları birinci dağılıma göre kalibredir; sabit
`[0.35, 0.65]` bandı ikincisinde yanlış yerdedir. Ölçüldü: TF-IDF akışta
0.50 eşiğiyle 0.709 doğruluk verirken, akıştan seçilen eşikle 0.966 veriyor.

NEDEN DOĞRULAMA KÜMESİNDE KALİBRE ETMİYORUZ (denendi, işe yaramadı):
Doğrulama kümesinde model doyuma ulaşmış durumda (5 tohumda 1.000 ± 0.000),
yani orada her eşik aynı görünüyor. Orada seçilen eşik akışa taşınmıyor —
ölçüldü: doğrulamada seçilen 0.46 eşiği akışta 0.684 veriyor, akıştan
seçilen 0.86 ise 0.966.

DÜRÜSTLÜK NOTU (rapora girer): Bu kalibrasyon, AKIŞTAN ETİKETLİ VERİ ister.
Akış iki ayrık yarıya bölünür; eşik birinci yarıda seçilir, sonuç ikinci
yarıda ölçülür. Eşiği ölçtüğü kümede aramak, olmayan bir başarım iddia
etmek olurdu. Gerçek dağıtımda bu, "az miktarda etiketli üretim verisi
gerekir" demektir ve bu bir maliyet kalemidir, bedava değildir.

BANT NEYE GÖRE SEÇİLİR: "Etiket gösterildiğinde ne kadar doğru olduğu"
hedefine göre. Bu, kullanıcının gördüğü tek sayıdır. Hedefi sağlayan eşik
yoksa o yön `null` bırakılır: o yönde hiç etiket gösterilmez. Uydurma bir
eşik koymaktansa çekimser kalmak İlke 2'nin gereğidir.

Kullanım:
    python ml/scripts/calibrate_threshold.py
    python ml/scripts/calibrate_threshold.py --hedef-kesinlik 0.90
"""

from __future__ import annotations

import argparse
import json
from typing import Sequence

import _bootstrap  # noqa: F401

from app.config import config
from app.detection.calibration import kalibrasyon_bolmesi, kalibrasyon_yolu, sifirla
from app.detection.decision import karar_ver
from app.detection.detector import BerturkDetector, TfidfDetector
from app.store.feed_repo import load_feed
from app.textutil import count_tokens

REPO_ROOT = _bootstrap.REPO_ROOT

# Eşik taraması adımı. 0.01, olasılık ölçeğinde ayırt edici olacak kadar
# ince; daha ince ızgara kalibrasyon kümesinin gürültüsüne oturmaya başlar.
ADIM = 0.01


def akis_verisi() -> tuple[list[str], list[int]]:
    """Akıştan etiketli gönderileri toplar (evaluate._aktarim_verisi ile aynı süzgeç)."""
    metinler, etiketler = [], []
    for post in load_feed().posts:
        if post.eval_is_ai_generated is None or post.eval_has_injection:
            continue
        metinler.append(post.text)
        etiketler.append(1 if post.eval_is_ai_generated else 0)
    return metinler, etiketler


def uzunluk_gecenler(
    metinler: Sequence[str],
    olasiliklar: Sequence[float],
    etiketler: Sequence[int],
) -> tuple[list[float], list[int]]:
    """Uzunluk eşiğini geçen örnekleri süzer.

    NEDEN: `min_detection_tokens` altındaki gönderiler karar katmanında zaten
    hiç etiketlenmez. Eşiği bu gönderileri de sayarak seçmek, hiçbir zaman
    etiketlenmeyecek örneklerin kesinliğe katkı yapması demektir; seçilen
    eşik o zaman gerçekte olan davranışa göre kalibre olmaz.
    """
    p, e = [], []
    for metin, olasilik, etiket in zip(metinler, olasiliklar, etiketler):
        if count_tokens(metin) >= config.min_detection_tokens:
            p.append(olasilik)
            e.append(etiket)
    return p, e


def _esik_ara(
    olasiliklar: Sequence[float],
    etiketler: Sequence[int],
    hedef: float,
    *,
    yon: str,
) -> float | None:
    """Hedef kesinliği sağlayan en tutucu eşiği bulur.

    yon="ust": p > eşik olanlar arasında 'yapay zekâ' kesinliği >= hedef olan
        EN KÜÇÜK eşik (mümkün olduğunca çok gönderi etiketlensin).
    yon="alt": p < eşik olanlar arasında 'insan' kesinliği >= hedef olan
        EN BÜYÜK eşik.
    """
    basamaklar = [i * ADIM for i in range(1, int(1 / ADIM))]
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


def bant_olc(
    metinler: Sequence[str],
    olasiliklar: Sequence[float],
    etiketler: Sequence[int],
    alt: float | None,
    ust: float | None,
) -> tuple[float, float]:
    """(etiketlenen oranı, etiketlendiğinde doğruluk) döndürür.

    Ölçüm `karar_ver` ÜZERİNDEN yapılır, bandı elle uygulamıyoruz: uzunluk
    eşiği ve çakışan bant kuralı da devreye girsin. Aksi hâlde bu betiğin
    yazdığı sayı ile `evaluate.py`nin ürettiği tablo birbirini tutmaz —
    aynı ada sahip iki farklı metrik, raporun yapabileceği en kötü hatadır.
    """
    etiketli = []
    for metin, olasilik, etiket in zip(metinler, olasiliklar, etiketler):
        karar = karar_ver(metin, olasilik, bant=(alt, ust))
        if not karar.abstained:
            etiketli.append((karar.label == "yz_olasi", etiket))
    if not etiketli:
        return 0.0, float("nan")
    dogru = sum(1 for yz, e in etiketli if yz == bool(e))
    return len(etiketli) / len(etiketler), dogru / len(etiketli)


def main() -> None:
    ayristirici = argparse.ArgumentParser(description="Karar bandını akışta kalibre eder")
    ayristirici.add_argument("--hedef-kesinlik", type=float, default=0.95)
    args = ayristirici.parse_args()

    metinler, etiketler = akis_verisi()
    (kx, ky), (ox, oy) = kalibrasyon_bolmesi(metinler, etiketler)
    print(
        f"akış={len(etiketler)} (pozitif {sum(etiketler)/len(etiketler):.3f}) | "
        f"kalibrasyon={len(ky)} ölçüm={len(oy)} | hedef kesinlik={args.hedef_kesinlik}"
    )

    for arka_uc, ad, sinif in (
        ("tfidf", "TF-IDF temel çizgi", TfidfDetector),
        ("berturk", "BERTurk ince ayar", BerturkDetector),
    ):
        try:
            model = sinif()
        except Exception as hata:
            print(f"  {ad}: model yok ({hata.__class__.__name__}) — kalibre edilmedi")
            continue

        pk = model.predict_proba(kx)
        po = model.predict_proba(ox)
        # Eşik yalnızca etiketlenebilir (uzunluk eşiğini geçen) örneklerde aranır.
        gp, ge = uzunluk_gecenler(kx, pk, ky)
        alt = _esik_ara(gp, ge, args.hedef_kesinlik, yon="alt")
        ust = _esik_ara(gp, ge, args.hedef_kesinlik, yon="ust")

        eski_oran, eski_dogruluk = bant_olc(ox, po, oy, config.abstain_low, config.abstain_high)
        yeni_oran, yeni_dogruluk = bant_olc(ox, po, oy, alt, ust)

        veri = {
            "backend": arka_uc,
            "model": model.name,
            "abstain_low": alt,
            "abstain_high": ust,
            "target_precision": args.hedef_kesinlik,
            "fitted_on": "akış (synthetic_feed) — kalibrasyon yarısı",
            "calibration_size": len(ky),
            "calibration_positive_rate": round(sum(ky) / len(ky), 4),
            # Aşağıdaki sayılar KALİBRASYONDA KULLANILMAYAN yarıda ölçüldü.
            "measured_on_holdout": {
                "size": len(oy),
                "labeled_rate": round(yeni_oran, 4),
                "accuracy_when_labeled": None if yeni_dogruluk != yeni_dogruluk else round(yeni_dogruluk, 4),
                "baseline_fixed_band": {
                    "band": [0.35, 0.65],
                    "labeled_rate": round(eski_oran, 4),
                    "accuracy_when_labeled": None if eski_dogruluk != eski_dogruluk else round(eski_dogruluk, 4),
                },
            },
        }
        yol = kalibrasyon_yolu(arka_uc)
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")

        def _g(x: float) -> str:
            return "[  ]" if x != x else f"{x:.3f}"

        print(f"  {ad}: bant=[{alt}, {ust}] -> {yol.name}")
        print(
            f"      sabit  [0.35, 0.65]: etiketlenen {eski_oran:.1%}, "
            f"etiketlendiğinde doğruluk {_g(eski_dogruluk)}"
        )
        print(
            f"      kalibre [{alt}, {ust}]: etiketlenen {yeni_oran:.1%}, "
            f"etiketlendiğinde doğruluk {_g(yeni_dogruluk)}"
        )

    sifirla()
    print("NOT: Nihai tablolar için: python ml/scripts/evaluate.py --only detection")


if __name__ == "__main__":
    main()
