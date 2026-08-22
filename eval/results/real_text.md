# Gerçek Metin Ölçümü — sentetik değerlendirmenin şişirdiği pay

> `ml/scripts/evaluate_real.py` tarafından üretilir. Elle düzenlenmez.

## Küme

**374** örnek — yapay_zeka 174, insan 200 (pozitif oran 0.465).

| Sınıf | Kaynak | Köken |
|---|---|---|
| insan | `turkish-nlp-suite/vitamins-supplements-reviews` (CC BY-SA 4.0) | gerçek müşteriler, 2022 derlemi — dil modelleri yaygınlaşmadan önce |
| yapay_zeka | Claude Opus 5 | aynı ürün, aynı uzunluk, aynı yıldız puanı eşleştirmesiyle üretildi |

Eşleştirme zorunluydu: iki sınıf farklı konulardan ya da farklı
duygulardan gelseydi model yazarı değil KONUYU ya da DUYGUYU öğrenirdi.
Üretimde üslup da dağıtıldı (samimi, yazım hatalı, asistan ağzı,
pazarlama dili, dengeli); düz asistan ağzı bilerek azınlıkta tutuldu,
çünkü tespiti yalnızca en kolay üslupta ölçmek kendimizi kandırmak olurdu.

## 1. Ayırt etme gücü (eşikten bağımsız)

| Model | AUROC | FPR@95TPR | Doğruluk (0.5 eşiği) | F1 (0.5) |
|---|---|---|---|---|
| TF-IDF temel çizgi | 0.541 | 0.935 | 0.537 | 0.362 |
| BERTurk ince ayar | 0.768 | 0.640 | 0.548 | 0.056 |

### Uzunluk kovası bazında doğruluk (0.5 eşiği)

| Model | K1 (20-50 token) | K2 (50-100) | K3 (100+) |
|---|---|---|---|
| TF-IDF temel çizgi | 0.517 | 0.598 | 0.500 |
| BERTurk ince ayar | 0.550 | 0.549 | 0.533 |

## 2. Ürünün şu an yaptığı — akış bandı bu kümeye uygulanırsa

Bant akış dağılımında (pozitif oran ~0.18) kalibre edildi; bu küme
farklı bir dağılım (pozitif oran 0.47).
Uyumsuzluk kasıtlı olarak gösteriliyor: **kalibrasyon dağılıma bağlıdır**,
bir dağılımda seçilen eşik başka bir dağılıma taşınamaz.

| Model | Akış bandı | Etiketlenen | Etiketlendiğinde doğruluk |
|---|---|---|---|
| TF-IDF temel çizgi | `[0.92, 0.83]` | 99.7% | 0.536 |
| BERTurk ince ayar | `[0.99, 0.98]` | 100.0% | 0.535 |

## 3. Bu dağılım için kalibre edilseydi

Eşik kümenin bir yarısında seçilir, sonuç **diğer yarısında** ölçülür
(bölme `app/detection/calibration.kalibrasyon_bolmesi`, akışta
kullanılanın aynısı). Hedef: etiket gösterildiğinde doğruluk ≥ 0.95.

| Model | Kalibre bant | Etiketlenen | Etiketlendiğinde doğruluk |
|---|---|---|---|
| TF-IDF temel çizgi | `[None, 0.81]` | 1.1% | 1.000 |
| BERTurk ince ayar | `[None, 0.37]` | 2.1% | 0.750 |

Ölçüm yarısı: 187 örnek (kalibrasyon yarısı 187).

## 4. Üslup bazında yakalanma oranı (yalnızca yapay zekâ sınıfı)

Yapay zekâ metinleri beş farklı üslupta üretildi. Aşağıdaki sayı,
o üsluptaki metinlerin kaçının 0.5 eşiğinde 'yapay zekâ' olarak
işaretlendiğidir. Düşük sayı = o üslup tespitten kaçıyor.

| Üslup | n | TF-IDF temel çizgi | BERTurk ince ayar |
|---|---|---|---|
| `asistan` | 33 | 0.455 | 0.061 |
| `dengeli` | 25 | 0.360 | 0.040 |
| `hatali` | 42 | 0.190 | 0.000 |
| `pazarlama` | 20 | 0.300 | 0.000 |
| `samimi` | 54 | 0.204 | 0.037 |

Ortalama olasılık (yüksek = model daha çok 'yapay zekâ' diyor):

| Üslup | TF-IDF temel çizgi | BERTurk ince ayar |
|---|---|---|
| `asistan` | 0.482 | 0.075 |
| `dengeli` | 0.416 | 0.064 |
| `hatali` | 0.366 | 0.001 |
| `pazarlama` | 0.359 | 0.011 |
| `samimi` | 0.343 | 0.048 |

## Sınırlılıklar

1. **Tek üretici.** Yapay zekâ tarafı yalnızca Claude Opus 5 ile üretildi.
   Bu küme üzerinde EĞİTİM yapılırsa çıkan model 'yapay zekâ tespiti'
   değil 'Claude tespiti' yapar. Buradaki kullanım yalnızca ÖLÇÜMDÜR:
   modeller sentetik veriyle eğitildi, bu küme onlara hiç gösterilmedi.
   Genellenebilir bir iddia için en az üç üretici ve biri sınava saklanmış
   olmalıdır.
2. **Tür kayması.** İnsan tarafı ürün yorumu, eğitim verisi ise sosyal
   medya gönderisi. Mutlak sayılar bu kaymayı da içerir. İnsan/yapay zekâ
   karşılaştırması yine de kontrollüdür: tür kayması iki sınıfı da eşit
   etkiler.
3. **Köken kesinliği tam değil.** 2022 derlemi, dil modellerinin
   yaygınlaşmasından önceye denk gelir ama tek tek her yorumun insan
   yazımı olduğu kanıtlanamaz.
4. **Küme küçük.** ~370 örnek; oranların güven aralığı geniştir.

