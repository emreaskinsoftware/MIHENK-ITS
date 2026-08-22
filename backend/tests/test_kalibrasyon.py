"""Kalibre edilmiş karar bandı testleri (spec 6.5, İlke 2).

NEDEN AYRI TEST DOSYASI: Kalibrasyon, çekimserlik kuralına yeni bir uç
davranış ekliyor — bir eşiğin `None` olabilmesi ve iki eşiğin çakışabilmesi.
Bu iki durumda da sistemin SUSMASI gerekir; sessizce etiket üretmesi İlke 2'yi
çiğner ve ölçümde görünmez. Testler bunu garanti altına alır.
"""

from __future__ import annotations

import json

from app.config import config
from app.detection import calibration
from app.detection.decision import karar_ver

UZUN = "kelime " * (config.min_detection_tokens + 10)


def test_bant_verilmezse_config_kullanilir():
    """Geriye dönük uyum: bant geçilmediğinde davranış değişmemeli."""
    orta = (config.abstain_low + config.abstain_high) / 2
    assert karar_ver(UZUN, orta).reason == "belirsiz"
    assert karar_ver(UZUN, config.abstain_high + 0.2).label == "yz_olasi"
    assert karar_ver(UZUN, config.abstain_low - 0.2).label == "insan_olasi"


def test_ust_esik_yoksa_yz_etiketi_hic_gosterilmez():
    """Hedef kesinliği sağlayan üst eşik bulunamadıysa o yönde susulur.

    Bu, kalibrasyonun gerçekten ürettiği bir durumdur: BERTurk'ün akış
    kalibrasyon yarısında %95 kesinliği sağlayan bir üst eşiği yoktu.
    """
    sonuc = karar_ver(UZUN, 0.999, bant=(0.30, None))
    assert sonuc.abstained is True
    assert sonuc.label is None, "üst eşik yokken YZ etiketi üretildi"
    assert sonuc.reason == "belirsiz"
    # Alt yön hâlâ çalışmalı.
    assert karar_ver(UZUN, 0.01, bant=(0.30, None)).label == "insan_olasi"


def test_alt_esik_yoksa_insan_etiketi_hic_gosterilmez():
    sonuc = karar_ver(UZUN, 0.001, bant=(None, 0.70))
    assert sonuc.abstained is True
    assert sonuc.label is None
    assert karar_ver(UZUN, 0.99, bant=(None, 0.70)).label == "yz_olasi"


def test_cakisan_bantta_cekimser_kalinir():
    """alt > üst olduğunda çakışma bölgesinde hüküm verilmez.

    Kalibrasyon iki eşiği bağımsız seçer; TF-IDF'te alt=0.86, üst=0.85 çıktı.
    Aradaki dar bölgede iki iddia da doğru görünür — hangisi olduğunu
    söyleyemeyiz, susarız.
    """
    sonuc = karar_ver(UZUN, 0.855, bant=(0.86, 0.85))
    assert sonuc.abstained is True
    assert sonuc.reason == "belirsiz"
    # Çakışma bölgesinin dışında karar üretilmeye devam eder.
    assert karar_ver(UZUN, 0.95, bant=(0.86, 0.85)).label == "yz_olasi"
    assert karar_ver(UZUN, 0.10, bant=(0.86, 0.85)).label == "insan_olasi"


def test_kalibrasyon_dosyasi_yoksa_config_bandina_dusulur(tmp_path, monkeypatch):
    """Kalibrasyon yoksa sistem çalışmaya devam eder, yalnızca bant ölçülmemiştir."""
    monkeypatch.setattr(calibration, "ARTIFACT_DIR", tmp_path)
    calibration.sifirla()
    assert calibration.aktif_bant("berturk-finetuned[cuda]") == (
        config.abstain_low,
        config.abstain_high,
    )
    calibration.sifirla()


def test_kalibrasyon_dosyasi_okunur(tmp_path, monkeypatch):
    """Dosya varsa bant oradan gelir ve cihaz eki adı bozmaz."""
    monkeypatch.setattr(calibration, "ARTIFACT_DIR", tmp_path)
    calibration.sifirla()
    (tmp_path / "calibration_berturk.json").write_text(
        json.dumps({"abstain_low": 0.2, "abstain_high": 0.9}), encoding="utf-8"
    )
    assert calibration.aktif_bant("berturk-finetuned[cuda]") == (0.2, 0.9)
    # Tanınmayan model adı config yedeğine düşer.
    assert calibration.aktif_bant("bilinmeyen-model") == (
        config.abstain_low,
        config.abstain_high,
    )
    calibration.sifirla()
