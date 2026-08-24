# Özetleme ve Asistan

> `ml/scripts/evaluate.py` tarafından üretilir. Elle düzenlenmez.

Sağlayıcı: `fake-extractive` · Gömme: `intfloat/multilingual-e5-base` · Akış: 420 gönderi · Koşu: 9

## Atıf ve sadakat

| Metrik | Değer |
|---|---|
| Kaynağa sadakat (sözcüksel örtüşme, ortalama) | 0.937 |
| Sadakat ≥ 0.80 olan cümle oranı | 1.000 |
| Atıf doğruluğu (gösterilen kaynak gerçekten var) | 1.000 |
| Atıfsız üretim (özet başına silinen cümle, ort.) | 0 |
| Üretilen toplam cümle | 90 |
| Tek kaynaklı olduğu için bastırılan küme (İlke 3) | 0 |

## Asistan davranışı

| Metrik | Değer |
|---|---|
| Örneklem büyüklüğü | 72 |
| Bağlam dışı soruda doğru reddetme | 0.972 |
| Bağlam içi soruda yanıt verme | 1.000 |
| Aşırı çekimserlik (yanıtlanabilirken susma) | 0.000 |
| Yanıtın kaynak taşıma oranı | 1.000 |

## Gecikme ve maliyet

| Metrik | Değer |
|---|---|
| Özet gecikmesi p50 | 534 ms |
| Özet gecikmesi p95 | 767 ms |
| Asistan gecikmesi p50 | 0.0 ms |
| Önbellek isabet oranı | 0.750 |
| Zenginleştirmede LLM çağrısından tasarruf | 46.0% |
| 1000 özet için birleştirme çağrısı | 1000 |

### Maliyet mantığı

Akıştaki 420 gönderi için yalnızca 227 atomik özet çağrısı yapıldı (193 gönderi 15 kelime sınırının altında olduğu için çağrı yapılmadan geçildi). Bu çıktı kullanıcılar arasında paylaşılır:
aynı gönderiyi kaç kullanıcı görürse görsün zenginleştirme bir kez yapılır.
Kullanıcı başına tekrarlanan tek pahalı işlem, özet başına **1** birleştirme
çağrısıdır. Maliyet bu nedenle kullanıcı sayısıyla doğrusal büyümez.

### Sınırlılık

Sadakat, sözcüksel örtüşme vekiliyle ölçülmüştür (NLI modeli veya insan
değerlendirmesi değil). Düşük örtüşme kesin olarak sadakatsizliği gösterir;
yüksek örtüşme sadakati garanti etmez. İnsan değerlendirmesi kullanılabilirlik testine aittir (docs/KULLANILABILIRLIK_TESTI.md).

> **UYARI:** Bu koşu `fake-extractive` sağlayıcıyla yapılmıştır. Bu sağlayıcı
> gönderilerden cümle SEÇER, yeni cümle üretmez; bu yüzden sadakat skorları
> yapay olarak yüksektir ve dil kalitesi hakkında bilgi vermez. Rapora girecek
> sayılar için gerçek sağlayıcıyla koşulmalıdır:
> `MIHENK_LLM_PROVIDER=api python ml/scripts/evaluate.py --only summarization`
