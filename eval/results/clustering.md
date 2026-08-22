# Kümeleme Kalitesi ve Eşik Kalibrasyonu

> `ml/scripts/evaluate.py` tarafından üretilir. Elle düzenlenmez.

Gömme arka ucu: `intfloat/multilingual-e5-base` · Değerlendirilen gönderi: 37 · Gerçek olay sayısı: 5

## Kullanılan eşik

| Eşik | ARI | Homojenlik | Bütünlük | V-ölçüsü | Küme |
|---|---|---|---|---|---|
| **0.13** (config) | 0.2501 | 0.8447 | 0.5252 | 0.6477 | 13 |
| 0.13 (taramada en iyi ARI) | 0.2501 | 0.8447 | 0.5252 | 0.6477 | 13 |

## Yorum

Homojenlik bütünlükten yüksektir: aynı olay birden çok kümeye bölünür ama
farklı olaylar birbirine karışmaz. Bu denge bilinçlidir — bölünme özette
aynı olay hakkında iki cümle üretir (fazlalık, ama her cümle kaynağına
bağlıdır); birleşme ise iki olayı tek cümlede toplar ve kaynağa
bağlanamayan bir iddia doğurur, bu da İlke 1'i çiğner.

## Eşik taraması

| Eşik | ARI | Homojenlik | Bütünlük | Küme |
|---|---|---|---|---|
| 0.01 | 0.1811 | 1.0 | 0.511 | 22 |
| 0.11 | 0.2081 | 0.9517 | 0.5252 | 17 |
| 0.21 | 0.0 | 0.0 | 1.0 | 1 |
| 0.31 | 0.0 | 0.0 | 1.0 | 1 |
| 0.41 | 0.0 | 0.0 | 1.0 | 1 |
| 0.51 | 0.0 | 0.0 | 1.0 | 1 |
| 0.61 | 0.0 | 0.0 | 1.0 | 1 |
| 0.71 | 0.0 | 0.0 | 1.0 | 1 |
| 0.81 | 0.0 | 0.0 | 1.0 | 1 |
| 0.91 | 0.0 | 0.0 | 1.0 | 1 |
| 1.01 | 0.0 | 0.0 | 1.0 | 1 |
| 1.11 | 0.0 | 0.0 | 1.0 | 1 |
| 1.21 | 0.0 | 0.0 | 1.0 | 1 |
| 1.31 | 0.0 | 0.0 | 1.0 | 1 |
