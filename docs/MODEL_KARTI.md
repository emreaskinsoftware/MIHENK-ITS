# Model Kartı

> Bu belge, MİHENK'te kullanılan modellerin adını, sürümünü, lisansını,
> eğitim verisini, ölçülen başarımını ve **sınırlılıklarını** kaydeder.
> Rapordaki 3.2 bölümünün kaynağıdır. Sayılar `ml/scripts/evaluate.py`
> çıktısından alınır; elle yazılmaz.

## 1. Gömme modeli (kümeleme için)

| Alan | Değer |
|---|---|
| Model | `intfloat/multilingual-e5-base` |
| Sürüm | HuggingFace Hub, ana dal (indirme tarihi: 21 Ağustos 2026) |
| Lisans | MIT |
| Boyut | 768 |
| Dil | Çok dilli (100+ dil, Türkçe dahil) |
| Kullanım | Gönderi gömme → aglomeratif kümeleme (KATMAN 2) |
| Girdi biçimi | `passage: {metin}` öneki (model kartının önerdiği kullanım) |
| İnce ayar | **Yapılmadı** — hazır ağırlıklar kullanılır |

### Neden bu model

- Türkçe içeren çok dilli eğitim korpusu; Türkçe-özel bir gömme modeline göre
  daha geniş dil kapsamı, tek dilli modellere yakın Türkçe başarımı.
- MIT lisansı: ticari kullanım ve dağıtım serbest, yarışma sonrası ürünleşme
  yolunu kapatmıyor.
- 768 boyut, CPU'da kabul edilebilir gecikme: 420 gönderi ~5 saniyede gömülüyor
  (ölçüldü, GPU yok).

### Yedek arka uç

`HashingEmbedder` (kelime + karakter n-gram, hashing trick, bağımlılıksız).
Amacı testlerin ve CI'ın torch kurulumu olmadan koşabilmesidir.
**Bu bir dil modeli değildir**; anlamsal benzerliği yalnızca yüzeysel biçimden
yakalar. Raporlanan kümeleme metrikleri e5 ile üretilir ve hangi arka ucun
kullanıldığı ölçüm çıktısına (`eval/results/clustering.md`) yazılır.

### Ölçülen kümeleme başarımı

Kaynak: `eval/results/clustering.md` (sentetik akışın gündem kategorisinde,
`_eval_event_id` gerçek etiket olarak alınarak).

| Gömme | Eşik | ARI | Homojenlik | Bütünlük |
|---|---|---|---|---|
| e5-base | 0.13 | 0.250 | 0.84 | 0.53 |
| hashing (yedek) | 0.89 | 0.279 | 0.84 | 0.54 |

**Yorum:** Homojenlik bütünlükten yüksektir — aynı olay birden çok kümeye
bölünür ama farklı olaylar karışmaz. Bu denge bilinçlidir: bölünme özette aynı
olay hakkında iki cümle üretir (fazlalık, ama her cümle kaynağına bağlıdır);
birleşme ise iki olayı tek cümlede toplar ve kaynağa bağlanamayan bir iddia
doğurur — İlke 1 ihlali.

---

## 2. YZ metin tespiti modeli

| Alan | Değer |
|---|---|
| Ana model | `dbmdz/bert-base-turkish-cased` (BERTurk), ikili sınıflandırma başlığı ile ince ayarlı |
| Lisans | MIT |
| Parametre | ~110M |
| Temel çizgi | TF-IDF (char_wb 2-5 + word 1-2) + Lojistik Regresyon |
| Eğitim verisi | `ml/data/detection/train.jsonl` — sentetik, şablon üretimli |
| Donanım | NVIDIA GeForce RTX 3050 Laptop GPU (CUDA); kısmî ince ayar sayesinde CPU yolu da desteklenir |

### Neden Türkçe-özel encoder

Türkçe sondan eklemeli bir dildir. Çok dilli tokenizer'lar Türkçe ekleri daha
çok parçaya böler; kısa metinlerde (K1 kovası, 0-50 token) bu parçalanma bilgi
kaybı demektir. Kısa metin bizim en zor bölgemiz olduğu için Türkçe korpusta
eğitilmiş bir tokenizer tercih edildi.

### Hiperparametreler

Kaynak: `ml/artifacts/training_berturk.json` (eğitim betiği yazar).

| Parametre | Değer |
|---|---|
| Epoch | 3 |
| Parti boyutu | 32 |
| Öğrenme oranı | 2e-5 |
| Maksimum uzunluk | 192 token |
| Doldurma | dinamik (parti içi en uzun) |
| İyileştirici | AdamW |
| Gradyan kırpma | 1.0 |
| Karışık hassasiyet (AMP) | açık |
| Dondurulan encoder katmanı | 9 (gömme katmanı dahil) |
| Eğitilen / toplam parametre | 21.855.746 / 110.618.882 (%19,8) |
| Tohum | 20260824 |

### Ölçülen başarım

Kaynak: `eval/results/detection.md`.

**İki ayrı ölçüm vardır ve ikisi farklı şeyi söyler:**

1. **Kendi test kümesi** (aynı şablon havuzu, farklı şablon grupları):
   doğruluk yüksektir. Bu sayı **yanıltıcıdır** — sınıfları tasarlayan taraf ile
   ölçen taraf aynıdır.

2. **Aktarım testi** (sosyal medya akışı üretecinden gelen, tespit veri setiyle
   hiçbir şablon paylaşmayan gönderiler): **rapora girecek asıl sayı budur.**

TF-IDF temel çizgisi için ölçülen aktarım sonuçları:

| Metrik | Değer |
|---|---|
| Doğruluk | 0.722 |
| F1 | 0.559 |
| AUROC | 0.973 |
| **FPR@95TPR** | **0.142** |
| K1 (0-50 token) doğruluk | 0.646 |
| K2 (50-100) doğruluk | 0.929 |
| K3 (100+) doğruluk | 1.000 |
| Çekimserlik oranı | %67.1 |

**En önemli bulgu:** Doğruluk uzunlukla birlikte K1'de 0.65'ten K3'te 1.00'e
çıkıyor. Yani tespit, kısa metinlerde çalışmıyor. Çekimserlik mekanizması
(İlke 2) bu ampirik bulgunun ürün karşılığıdır: kısa metinde hiçbir etiket
gösterilmez.

AUROC'un 0.97 olmasına karşın doğruluğun 0.72'de kalması, 0.5 eşiğinin bu
dağılım için kalibre olmadığını gösterir. Sıralama bilgisi güçlü, mutlak
olasılık kalibrasyonu zayıf. Belirsizlik bandı bu boşluğu kapatır.

### Eşik değerleri (çekimserlik)

`backend/app/config.py` içinde tanımlıdır:

| Eşik | Değer | Anlamı |
|---|---|---|
| `min_detection_tokens` | 20 | Bu sayının altında etiket gösterilmez |
| `abstain_low` | 0.35 | Belirsizlik bandı alt sınırı — **yalnızca yedek** |
| `abstain_high` | 0.65 | Belirsizlik bandı üst sınırı — **yalnızca yedek** |

Bant artık config'ten değil, **modele göre kalibrasyon dosyasından** gelir
(`ml/artifacts/calibration_<arka_uc>.json`, üreten:
`ml/scripts/calibrate_threshold.py`). Config değerleri yalnızca kalibrasyon
dosyası yokken kullanılır ve `detection.md` bu durumu "kalibre edilmedi"
olarak işaretler.

**Neden sabit bant yetmiyor (ölçüldü):** Model olasılıkları eğitim
dağılımına göre kalibredir; eğitim/doğrulama kümesi sınıf-dengelidir
(pozitif oran ~0.49), akış ise değildir (~0.18). Sabit `[0.35, 0.65]` bandı
akışta yanlış yerde durur. Aynı beş model, akışın ölçüm yarısında:

| | Etiketlendiğinde doğruluk | Etiketlenen oran |
|---|---|---|
| Sabit bant `[0.35, 0.65]` | 0.519 ± 0.170 | ~%85 |
| Kalibre bant | **0.959 ± 0.003** | %50–95 (tohuma göre) |

Kalibrasyon, tohumdan gelen salınımı doğruluktan kapsama taşır: zayıf bir
model yanlış etiketlemek yerine daha çok susar. Kalibrasyon eşiği akışın
BİR YARISINDA seçilir, sonuç diğer yarısında ölçülür.

---

## 3. LLM (özetleme ve asistan)

| Alan | Değer |
|---|---|
| Sağlayıcı soyutlaması | `backend/app/llm/provider.py` |
| Uygulamalar | `APIProvider` (Anthropic), `LocalVLLMProvider`, `FakeProvider` |
| Varsayılan (test/CI) | `FakeProvider` — çıkarımsal, dış çağrı yok |
| Ölçüm/demo | `APIProvider` |

`FakeProvider` bir dil modeli değildir: gönderilerden cümle **seçer**, yeni cümle
üretmez. Bu bilinçli bir karardır — sahte bir "üretim" taklidi, sadakat ölçümünü
yanıltıcı biçimde mükemmel gösterirdi. Ölçüm çıktısı hangi sağlayıcıyla
koşulduğunu her zaman yazar ve `fake` ile koşulduysa uyarı basar.

---

## 4. Genel sınırlılıklar (rapora aynen girer)

1. **Veri sentetiktir.** Gerçek platformlardan veri kazınmadı (spec 2. bölüm).
   Bu bir tercih değil, hem kullanım şartları hem de KVKK gereğidir.

2. **Sınıfları biz tasarladık.** Elle yazılmış şablonlarla üretilen bir veri
   setinde iki sınıf tanım gereği ayrılabilir. Bu yüzden aktarım testi
   eklenmiştir; yine de gerçek dağılımda beklenecek başarım aktarım
   satırından da düşük olacaktır.

3. **Tespit bir üslup sınıflandırmasıdır.** "Yapay zekâ üretimi" etiketi bir
   kanıt değil, bir olasılık tahminidir. Arayüz dili bunu saklamaz ("olabilir"),
   ve etiketlenen kullanıcı için itiraz akışı vardır.

4. **Sadakat ölçümü vekil ölçüdür.** Sözcüksel örtüşme kullanılır; NLI modeli
   veya insan değerlendirmesi değildir. Düşük örtüşme kesin olarak sadakatsizliği
   gösterir, yüksek örtüşme sadakati garanti etmez.

5. **Görsel köken ekosisteme bağımlıdır.** Sosyal medya sıkıştırması C2PA/IPTC
   üst verisinin çoğunu siler. Üçüncü taraf bir katman bu bilgiyi geri getiremez;
   platformun kendi işleme hattında koruması gerekir.
