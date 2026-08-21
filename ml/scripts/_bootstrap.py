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
