# Sentetik Akış İstatistikleri

> Bu dosya `ml/scripts/generate_feed.py` tarafından üretilir. Elle düzenlenmez.

- Toplam gönderi: **420**
- Farklı yazar (takma ad): **75**
- Medya içeren gönderi: **65**

## Kategori dağılımı

| Kategori | Gönderi | Hedef (spec 5.1) |
|---|---|---|
| Ülke gündemi | 147 (%35.0) | %35 |
| Spor gündemi | 105 (%25.0) | %25 |
| Kişisel akış | 168 (%40.0) | %40 |

## Uzunluk kovaları

| Kova | Token aralığı | Gönderi |
|---|---|---|
| K1 | 0-50 | 316 (%75.2) |
| K2 | 50-100 | 86 (%20.5) |
| K3 | 100+ | 18 (%4.3) |

## Gömülü tuzaklar (yalnızca değerlendirme için)

| Tuzak | Gönderi |
|---|---|
| YZ üretimi (`_eval_is_ai_generated`) | 75 (%17.9) |
| Manipülatif (`_eval_is_manipulative`) | 6 (%1.4) |
| İstem enjeksiyonu (`_eval_has_injection`) | 7 (%1.7) |

## Olay grupları (çoğulculuk testi)

| Olay | Gönderi | Not |
|---|---|---|
| `olay_derbi` | 8 |  |
| `olay_kopru` | 10 |  |
| `olay_metro_hatti` | 8 |  |
| `olay_okul_yemek` | 8 |  |
| `olay_stat` | 6 |  |
| `olay_su_kesintisi` | 8 |  |
| `olay_tek_kaynak` | 3 | tek yazarlı — özet ÜRETİLMEMELİ (İlke 3) |
| `olay_transfer` | 8 |  |
