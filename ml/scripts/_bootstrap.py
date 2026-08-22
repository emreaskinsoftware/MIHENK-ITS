"""ml/scripts altındaki betiklerin backend paketini görebilmesi için yol ayarı.

NEDEN BÖYLE: Betikler `python ml/scripts/xxx.py` şeklinde doğrudan çalıştırılıyor;
backend bir paket olarak kurulmadığı için (kurulum adımı demoyu zorlaştırırdı)
`backend` dizinini sys.path'e ekliyoruz. Tek yerde yapılıp her betikten içe
aktarılıyor ki yol mantığı kopyalanmasın.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND = REPO_ROOT / "backend"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# --- Windows'ta torch/scikit-learn OpenMP çakışması ---
#
# SORUN: scikit-learn ve torch, Windows tekerleklerinde kendi OpenMP çalışma
# zamanlarını taşır. Hangisi önce yüklenirse süreçte o kalır; scikit-learn
# önce gelirse torch'un `c10.dll` başlatması `OSError [WinError 1114]` ile
# düşer. Ölçüm betiğinde bu sessiz bir kayıp üretiyordu: `evaluate.py` önce
# TF-IDF temel çizgisini (joblib -> scikit-learn) kuruyor, ardından BERTurk
# yüklenemiyor ve Tablo 4'ün ana model satırı "[  ]" olarak yazılıyordu.
# Yani hata, ölçümü durdurmak yerine raporu eksik üretiyordu — spec 2'nin
# tersi: eksikliğin nedeni görünmüyordu.
#
# ÇÖZÜM: torch'u her şeyden önce, betik içi sıralamadan bağımsız olarak
# yükle. Burada yapılıyor çünkü her ölçüm betiği ilk satırında `_bootstrap`
# içe aktarıyor; sıralama sorumluluğunu betiklere dağıtmak, ileride eklenen
# bir betikte aynı sessiz kaybı geri getirirdi.
#
# torch kurulu değilse hiçbir şey yapılmaz: TF-IDF hattı torch'suz çalışır.
try:  # pragma: no cover - ortama bağlı
    import torch  # noqa: F401
except Exception:
    pass
