# 04 — Modeller

> **Bu dosya klasör değil, harita.** Model kodu bu klasörün altında değil;
> servis kodu `backend/app/` içinde, eğitim ve ölçüm betikleri `ml/scripts/`
> içinde yaşıyor. Sebep basit: ölçüm betikleri servis fonksiyonlarını
> **doğrudan çağırıyor** (`ml/scripts/evaluate.py`). Modeli ayrı bir ağaca
> taşısaydık ölçtüğümüz kod ile kullanıcının çalıştırdığı kod ayrışabilirdi.
>
> Model ağırlıkları depoya alınmaz (`.gitignore`: `ml/artifacts/`). Eğitim
> betikleri ve ölçüm çıktıları (`eval/results/`) depoda tutulur.

## Durum

| Bileşen | Nerede | Durum |
|---|---|---|
| **Yapay metin tespiti** — BERTurk ince ayarı | `backend/app/detection/`, `ml/scripts/train_detector.py` | **Eğitildi, kalibre edildi, ölçüldü** |
| **Yapay metin tespiti** — TF-IDF temel çizgi | aynı | **Eğitildi, ölçüldü** |
| **Gömme + kümeleme** — `multilingual-e5-base` + aglomeratif | `backend/app/summarize/clustering.py` | **Çalışıyor, ölçüldü** |
| **Atıflı özetleme** — küme → tek çağrı → atıf denetimi | `backend/app/summarize/` | **Çalışıyor, ölçüldü** |
| **Görsel köken denetimi** — C2PA/IPTC üretim etiketi | `backend/app/provenance/` | **Çalışıyor** (kanıt yoksa çekimser) |
| **Görsel yapay üretim sınıflandırıcısı** | — | **Yapılmadı** |
| **Özetleme modelinin ince ayarı** | — | **Yapılmadı** (aşağıya bakınız) |

## Planlanandan sapmalar ve gerekçeleri

Bu tablo başlangıçta üç satırdı ve üçü de "Planlandı" diyordu. Yön üç yerde
değişti; değişiklikleri gizlemek yerine gerekçesiyle yazıyoruz.

**1. Kümeleme HDBSCAN ile değil, aglomeratif kümeleme ile yapıldı.**
Küme sayısı önceden bilinmiyor ve gömmeler L2-normalize; kosinüs mesafesi +
ortalama bağlantı doğrudan çalışıyor. Asıl belirleyici şu oldu: mesafe eşiği
**savunulabilir** bir parametredir — "bu kadar benzer olanlar aynı olaydır"
cümlesi doğrudan bir sayıya çevrilir ve raporda gerekçelendirilebilir.
HDBSCAN'in min_cluster_size'ı bu kadar doğrudan yorumlanamıyordu.
Ayrıntı: `backend/app/summarize/clustering.py` başlığı.

**2. Özetleme için ayrı bir model ince ayarlanmadı.**
Özet üretimi dış bir dil modeline (API) ya da anahtar yokken yerel çıkarımsal
bir yedeğe bırakıldı. Sebep, projenin ana iddiasının nerede olduğuyla ilgili:
iddia "daha iyi özet üretiyoruz" değil, **"ürettiğimiz her cümleyi kaynağına
bağlıyoruz"**. O garanti üretici modelden değil, çıktıyı denetleyen koddan
geliyor (`backend/app/summarize/citation.py`). Sınırlı sürede ince ayar
yapmak, denetim katmanını zayıf bırakıp modeli güçlendirmek olurdu — yanlış
takas. Çıkarımsal temel model karşılaştırma çizgisi olarak duruyor
(`02-prototip/src/lib/ozet/cikarimsal.ts`).

**3. Görsel yapay üretim sınıflandırıcısı yapılmadı.**
Yapılan şey **köken denetimi**: görselin C2PA/IPTC üretim etiketi taşıyıp
taşımadığına bakılıyor; kanıt yoksa sistem `display=false` ile susuyor.
Sınıflandırıcı yerine köken denetimi seçildi çünkü yanlış pozitifin bedeli
burada metin tarafından daha ağır: bir kişinin gerçek fotoğrafını "yapay"
diye işaretlemek geri alınamaz bir itibar zararıdır. Arayüzdeki görsel
denetim ucu bu yüzden **olasılık üretmiyor**; simülasyon etiketini, etiket
olduğunu söyleyerek gösteriyor (`02-prototip/src/app/api/gorsel-denetim/`).

## Ölçüm

Sonuçlar `eval/results/` altında; hepsi betikle üretilir, elle düzenlenmez.

| Dosya | İçerik |
|---|---|
| `detection.md` | Tespit başarımı, aktarım testi, tohum değişkenliği |
| `real_text.md` | **Gerçek insan metni** üzerinde tespit (üslup bazında kaçış dahil) |
| `clustering.md` | ARI, homojenlik, bütünlük, eşik taraması |
| `summarization.md` | Kaynağa sadakat, atıf doğruluğu, gecikme, maliyet |
| `injection.md` | İstem enjeksiyonu savunması, saldırı türü bazında |

**Okunma sırası önemli.** `detection.md`'nin ilk tablosu kendi sentetik test
kümemizdedir ve **1,000 çıkar**; o sayı bir üst sınırdır, ürün başarımı
değildir. Sırasıyla:

| Ölçüm kümesi | BERTurk AUROC |
|---|---|
| Kendi test kümemiz | 1,000 |
| Şablon paylaşmayan akış (aktarım) | 0,980 |
| **Gerçek insan metni** | **0,768** |

Raporun dayandığı sayı sonuncusudur. Ayrıntı: rapor 3.2, Tablo 7 ve Tablo 8.

## Eğitimin yeniden üretilmesi

```bash
python ml/scripts/train_detector.py --backend tfidf --seeds 5
python ml/scripts/train_detector.py --backend berturk
python ml/scripts/calibrate_threshold.py
python ml/scripts/seed_variance.py
MIHENK_EMBEDDING_BACKEND=e5 python ml/scripts/evaluate.py
```

Diskte kalan model **belgelenmiş varsayılan tohuma** (`20260824`) aittir.
Tohum, aktarım başarımına bakılarak SEÇİLMEZ: seçim ölçtüğümüz kümede
yapılırsa raporlanan sayı artık modelin değil, seçimin başarımı olur.

Ayrıntılı çalıştırma yönergesi: `docs/CALISTIRMA.md`.
Model kartı (kullanım sınırları, bilinen başarısızlık kipleri):
`docs/MODEL_KARTI.md`.
