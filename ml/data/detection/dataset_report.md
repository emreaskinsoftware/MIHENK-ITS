# YZ Tespiti Veri Seti

> `ml/scripts/build_dataset.py` tarafından üretilir. Elle düzenlenmez.

## Kurulum özeti

- Üretilen ham örnek: **1320**
- Birebir yineleme nedeniyle çıkarılan: **1**
- Yakın-yineleme (Jaccard ≥ 0.8) nedeniyle çıkarılan: **1**
- İzin kapısında elenen: **0**
- Kişisel veri maskelenen kayıt: **0**
- Nihai toplam: **1318**

## Bölme × sınıf × kova dağılımı

| Bölme | Sınıf | K1 (0-50) | K2 (50-100) | K3 (100+) | Toplam |
|---|---|---|---|---|---|
| train | insan | 142 | 142 | 141 | 425 |
| train | yapay_zeka | 136 | 152 | 123 | 411 |
| val | insan | 41 | 40 | 41 | 122 |
| val | yapay_zeka | 45 | 27 | 43 | 115 |
| test | insan | 37 | 38 | 38 | 113 |
| test | yapay_zeka | 37 | 41 | 54 | 132 |

## Sızıntı denetimi (spec 5.2 adım 6)

| Denetim | Sonuç |
|---|---|
| Bölmeler arası birebir aynı metin | 0 |
| Test-train yakın-yineleme (Jaccard ≥ 0.8) | 0 |
| Bölmeler arası ortak şablon grubu | YOK |

### Bölme yöntemi

Bölme **şablon-ayrıktır**: kaynak şablon grupları önce train/val/test'e
dağıtılır, örnekler sonra üretilir. Test kümesindeki hiçbir örnek,
eğitimde görülmüş bir şablondan gelmez. Rastgele bölme, aynı kalıbın
iki tarafta birden bulunmasına ve modelin ezberi genelleme gibi
göstermesine yol açardı.

### Sınırlılık (dürüstlük notu)

Veri sentetiktir ve YZ sınıfı, dil modellerinin bilinen yüzey
özelliklerini (temkinli dil, kalıplaşmış bağlaçlar, kişisel deneyim
yokluğu) taklit eden şablonlardan üretilmiştir. Ölçülen başarım, gerçek
dağılımda beklenecek başarımın üst sınırı olarak okunmalıdır.
