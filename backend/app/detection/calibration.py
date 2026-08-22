"""Karar bandının kalibrasyonu — eşiği elle değil ölçerek koymak (spec 6.5).

SORUN (ölçüldü, rapora girer): Model olasılıkları eğitim dağılımına göre
kalibredir. Eğitim/doğrulama kümesi sınıf-dengelidir (pozitif oran ~0.49),
dağıtım dağılımı ise değildir: sosyal medya akışında gönderilerin yalnızca
~%18'i yapay zekâ ürünüdür. Aynı olasılık eşiği bu iki dağılımda aynı şeyi
ifade etmez. Sabit `[0.35, 0.65]` bandı bu yüzden akışta yanlış yerde durur.

NEDEN DOĞRULAMA KÜMESİNDE KALİBRE EDİLEMEZ: Doğrulama kümesi eğitimle aynı
dağılımdan gelir ve model orada doyuma ulaşmıştır (5 tohumda 1.000 ± 0.000).
Orada seçilen eşik, akışta işe yaramaz — ölçüldü. Kalibrasyon, DAĞITIM
DAĞILIMINDAN etiketli veri ister; bu verinin bir yarısı eşiği seçmek, diğer
yarısı ölçmek için kullanılır (`ml/scripts/calibrate_threshold.py`).

BANT NE GARANTİ EDER: Eşikler, "etiket gösterildiğinde ne kadar doğru
olduğu" hedefine göre seçilir. Bu, projenin zaten kullanıcıya gösterdiği tek
sayıdır (Tablo 4, "etiketlendiğinde doğruluk"). Kesinlik hedefi tutmuyorsa
o yönde HİÇ etiket gösterilmez (eşik None kalır) — uydurma bir eşik
koymaktansa çekimser kalmak İlke 2'nin gereğidir.

Kalibrasyon dosyası yoksa `config` içindeki sabit bant kullanılır; sistem
kalibrasyonsuz da çalışır, yalnızca bandı ölçülmemiş olur.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Sequence, TypeVar

from app.config import REPO_ROOT, config

logger = logging.getLogger(__name__)

T = TypeVar("T")

ARTIFACT_DIR = REPO_ROOT / "ml" / "artifacts"

# Model adı -> kalibrasyon dosyası anahtarı. Model adı cihaz ekiyle gelir
# ("berturk-finetuned[cuda]"); kalibrasyon cihazdan bağımsızdır, o yüzden
# arka uç adına indirgiyoruz.
_ARKA_UCLAR = ("berturk", "tfidf")

_onbellek: dict[str, tuple[float | None, float | None] | None] = {}


def _anahtar(model_adi: str) -> str | None:
    """Model adından kalibrasyon anahtarını çıkarır."""
    for arka_uc in _ARKA_UCLAR:
        if arka_uc in model_adi:
            return arka_uc
    return None


def kalibrasyon_yolu(arka_uc: str) -> Path:
    return ARTIFACT_DIR / f"calibration_{arka_uc}.json"


def bant_yukle(arka_uc: str) -> tuple[float | None, float | None] | None:
    """Kalibre edilmiş bandı okur; dosya yoksa None.

    Dönen ikilinin bir ucu None olabilir: o yönde hedef kesinliği sağlayan
    hiçbir eşik bulunamadı demektir ve o yönde etiket gösterilmez.
    """
    if arka_uc in _onbellek:
        return _onbellek[arka_uc]

    yol = kalibrasyon_yolu(arka_uc)
    bant: tuple[float | None, float | None] | None = None
    if yol.exists():
        try:
            veri = json.loads(yol.read_text(encoding="utf-8"))
            bant = (veri.get("abstain_low"), veri.get("abstain_high"))
        except Exception as hata:  # bozuk dosyaya güvenmiyoruz
            logger.warning("Kalibrasyon dosyası okunamadı %s: %s", yol, hata)
            bant = None
    _onbellek[arka_uc] = bant
    return bant


def aktif_bant(model_adi: str | None) -> tuple[float | None, float | None]:
    """Verilen model için kullanılacak bandı döndürür.

    Kalibrasyon yoksa `config` içindeki sabit bant döner. Bu durum bir hata
    değildir ama raporda belirtilir: bant ölçülmemiştir.
    """
    if model_adi:
        arka_uc = _anahtar(model_adi)
        if arka_uc:
            bant = bant_yukle(arka_uc)
            if bant is not None:
                return bant
    return (config.abstain_low, config.abstain_high)


def sifirla() -> None:
    """Önbelleği temizler (testler ve yeniden kalibrasyon sonrası)."""
    _onbellek.clear()


def kalibrasyon_bolmesi(
    ogeler: Sequence[T], etiketler: Sequence[int]
) -> tuple[tuple[list[T], list[int]], tuple[list[T], list[int]]]:
    """Akışı (kalibrasyon, ölçüm) olarak ikiye böler.

    NEDEN BURADA — SIZINTIYI ÖNLEMEK İÇİN: Bandı akışın bir yarısında seçip
    sonucu akışın TAMAMINDA ölçmek, eşiği ölçtüğü veriye uydurmak olurdu ve
    aktarım tablosundaki çekimserlik sayıları olduğundan iyi görünürdü.
    Bölme mantığı bu yüzden tek yerde durur: hem `calibrate_threshold.py` hem
    `evaluate.py` aynı bölmeyi kullanır, ikisi kaymaz.

    Bölme deterministiktir (tohum yok): aynı akış her koşuda aynı bölünsün ki
    kalibrasyon ve ölçüm tekrar üretilebilir olsun. Sınıf içinde dönüşümlü
    dağıtım iki yarıda da pozitif oranı korur (katmanlı bölme).

    Returns:
        ((kalibrasyon_ögeleri, kalibrasyon_etiketleri),
         (ölçüm_ögeleri, ölçüm_etiketleri))
    """
    kalib: tuple[list[T], list[int]] = ([], [])
    olcum: tuple[list[T], list[int]] = ([], [])
    sayac = {0: 0, 1: 0}
    for oge, etiket in zip(ogeler, etiketler):
        hedef = kalib if sayac[etiket] % 2 == 0 else olcum
        hedef[0].append(oge)
        hedef[1].append(etiket)
        sayac[etiket] += 1
    return kalib, olcum
