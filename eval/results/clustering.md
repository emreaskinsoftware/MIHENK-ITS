# Kümeleme Kalitesi ve Eşik Kalibrasyonu

> `ml/scripts/evaluate.py` tarafından üretilir. Elle düzenlenmez.

Gömme arka ucu: `hashing-word-char` · Değerlendirilen gönderi: 37 · Gerçek olay sayısı: 5

## Kullanılan eşik

| Eşik | ARI | Homojenlik | Bütünlük | V-ölçüsü | Küme |
|---|---|---|---|---|---|
| **0.89** (config) | 0.2794 | 0.8368 | 0.5391 | 0.6557 | 12 |
| 0.89 (taramada en iyi ARI) | 0.2794 | 0.8368 | 0.5391 | 0.6557 | 12 |

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
| 0.11 | 0.2226 | 1.0 | 0.5375 | 18 |
| 0.21 | 0.2226 | 1.0 | 0.5375 | 18 |
| 0.31 | 0.2226 | 1.0 | 0.5375 | 18 |
| 0.41 | 0.2226 | 1.0 | 0.5375 | 18 |
| 0.51 | 0.2226 | 1.0 | 0.5375 | 18 |
| 0.61 | 0.2226 | 1.0 | 0.5375 | 18 |
| 0.71 | 0.2226 | 1.0 | 0.5375 | 18 |
| 0.81 | 0.2334 | 0.9034 | 0.5266 | 15 |
| 0.91 | 0.1841 | 0.576 | 0.4634 | 8 |
| 1.01 | 0.0 | 0.0 | 1.0 | 1 |
| 1.11 | 0.0 | 0.0 | 1.0 | 1 |
| 1.21 | 0.0 | 0.0 | 1.0 | 1 |
| 1.31 | 0.0 | 0.0 | 1.0 | 1 |
