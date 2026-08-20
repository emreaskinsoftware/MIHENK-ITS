# 04 — Modeller

Bu klasör, MİHENK'in yerel yapay zekâ bileşenlerini barındırır.

| Modül | Görev | Durum |
|---|---|---|
| `ozetleme/` | Türkçe özetleme modelinin ince ayarı (temel model + distillation verisi) | Planlandı |
| `gorsel-tespit/` | Görselin yapay zekâ ile üretilip üretilmediğini sınıflandıran model | Planlandı |
| `kumeleme/` | Türkçe embedding + HDBSCAN ile olay kümeleme | Planlandı |

## Değerlendirme

Modeller `03-veri/cikti/` altındaki **etiketli** veri kümesi üzerinde ölçülür:

- Özetleme → ROUGE-1 / ROUGE-2 / ROUGE-L, çıkarımsal temel modele karşı
- Kümeleme → `olay_id` altın etiketine karşı homojenlik ve tamlık
- Görsel tespit → `gorsel_yapay_uretim` etiketine karşı doğruluk / F1
- Doğrulama → `iddia_dogru_mu` etiketine karşı doğruluk

Model ağırlıkları depoya alınmaz (bkz. `.gitignore`); eğitim betikleri ve
değerlendirme sonuçları buraya işlenir.
