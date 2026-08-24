# 3. TEKNOLOJİ KULLANIMI

> Rubrikte **20 puan** — raporun en ağır bölümü. Şartname ağırlığında Sosyal
> Yapay Zekâ teması için "Teknik Yeterlilik ve Uygulanabilirlik" %35 ile en
> yüksek paya sahiptir. Köşeli notlar rapora aktarılırken **silinecektir**.

---

## 3.1. İzlenecek Yöntem, Altyapı ve Sürüm Kontrolü

### Sistem mimarisi

MİHENK, sorumluluk ayrımı net iki katmandan oluşur. Bu ayrım, maliyetin
kullanıcı sayısıyla doğrusal büyümesini engellemek için tasarlanmıştır.

**Katman 1 — akış hızında, kullanıcıdan bağımsız.** Platforma düşen her gönderi,
kullanıcıdan bağımsız olarak bir kez işlenir: atomik özeti çıkarılır, gömme
(embedding) vektörü hesaplanır ve konu etiketi atanır. Sonuç, yaşam süreli
(TTL) bir önbellekte tutulur ve **tüm kullanıcılar arasında paylaşılır**.

**Katman 2 — kullanıcı hızında.** Kullanıcı "Özetle" dediğinde sistem sıfırdan
başlamaz; hazır kayıtları alır, kümeler, her kümeden temsilci seçer ve **tek bir
birleştirme çağrısı** yapar. Böylece kullanıcı başına tekrarlanan pahalı işlem
sayısı, özet başına bire iner.

### Yazılım dilleri ve teknolojiler

| Katman | Teknoloji | Gerekçe |
|---|---|---|
| Arayüz | Next.js 16 · React 19 · TypeScript · Tailwind CSS 4 | Sunucu tarafı işleme ile hızlı ilk yükleme; tip güvenliği |
| Uygulama servisi | FastAPI (Python 3.11+) · Pydantic | Şema doğrulaması tip düzeyinde; ML kütüphaneleriyle aynı çalışma zamanı |
| Gömme | `intfloat/multilingual-e5-base` | Türkçe dâhil çok dilli; sondan eklemeli yapıda güçlü başarım |
| Metin sınıflandırma | BERTurk ince ayar · TF-IDF temel çizgi | Türkçe için ön eğitimli; temel çizgiyle karşılaştırmalı raporlama |
| Kümeleme | Eşik tabanlı bağlantı, kalibre edilmiş eşik | Küme sayısı önceden bilinmediği için k gerektiren yöntemler elenmiştir |
| Veri | Etiketli sentetik külliyat (Pydantic şemalı) | Altın etiketler sayesinde başarım gerçek ölçümle raporlanabilir |

### Uygulama servisi uç noktaları

| Uç nokta | İşlev |
|---|---|
| `GET /api/akis` | Kronolojik akış |
| `POST /api/ozetle` | Kategori/olay özeti — cümle bazlı atıflı |
| `POST /api/sor` | Akış içi asistan |
| `GET /api/tespit/{id}` | Yapay üretim metin tespiti |
| `GET /api/koken/{id}` | Görsel köken ve üretim denetimi |
| `POST /api/itiraz` | Kullanıcı itiraz kaydı |
| `POST /api/yonetisim/unut/{id}` | KVKK — unutulma hakkı |

Arayüz bu servise tiplenmiş bir istemci katmanı üzerinden bağlanır. Servise
erişilemediğinde arayüz **yerel çıkarımsal motora düşer**; gösterim hiçbir
koşulda kesilmez. Bu, ağ veya kota kesintisinin ürünü kullanılamaz hâle
getirmemesi için alınmış bilinçli bir dayanıklılık kararıdır.

### Üç ilkenin koddaki karşılığı

Projenin üç tasarım ilkesi belge düzeyinde kalmamış, **yanıt şemasına
kodlanmıştır**. Bu, ilkelerin test edilebilir olmasını sağlar.

| İlke | Şemadaki karşılığı | Doğrulayan test |
|---|---|---|
| **Atıf zorunluluğu** — kaynağa bağlanmayan cümle gösterilmez | `sentences[].source_post_ids` (en az 1 zorunlu) | `test_ilke1_atif.py` |
| **Çekimserlik** — sistem emin değilse hüküm vermez | `abstained`, `refused`, `refusal_reason` | `test_ilke2_cekimserlik.py` |
| **Çoğulculuk** — tek doğru dayatılmaz | `single_source_cluster_count` | `test_ilke3_cogulculuk.py` |

Arayüz bu alanları yok saymaz; her birinin görsel karşılığı vardır. Atıf
denetiminden geçemeyip silinen cümle sayısı ve bastırılan tek kaynaklı küme
sayısı kullanıcıya **açıkça gösterilir**. Sistemin ne yapmadığını göstermek,
ne yaptığını göstermek kadar önemli görülmüştür.

### Kod reposu ve sürüm kontrolü

Kaynak kodlar GitHub üzerinde sürüm kontrolü altında tutulmakta, geliştirme
adımları anlamlı commit'lerle takip edilmektedir. Depo, arayüz, uygulama
servisi, model betikleri, değerlendirme takımı ve dokümantasyonu tek çatı
altında barındırır.

> **Depo bağlantısı:** https://github.com/emreaskinsoftware/MIHENK-ITS

API anahtarları hiçbir koşulda depoya girmez; `.gitignore` ile engellenir ve
yalnızca ortam değişkeni olarak sağlanır. Model ağırlıkları da depo dışında
tutulur.

*[Kontrol maddeleri: diller/teknolojiler (1p) · veri setleri ve analiz yöntemleri
(2p) · teknik altyapı (2p) · repo bağlantısı (1p) · commit geçmişi (1p)]*

---

## 3.2. Model ve Veri Doğrulama

### Veri ön işleme

Değerlendirme külliyatı, platformu simüle eden **etiketli sentetik veriden**
oluşur. Veri rastgele değil, **olay kümeleri** etrafında üretilir: her olayın
çevresinde farklı çerçevelerden (nötr, destekleyici, eleştirel, soru soran,
doğrulanmamış) gönderiler bulunur.

Her gönderi dört altın etiket taşır:

| Etiket | Ölçtüğü modül |
|---|---|
| Olay kimliği | Kümeleme doğruluğu |
| Çerçeve türü | Özet çoğulculuğu |
| Yapay üretim | Metin ve görsel tespiti |
| İddia doğruluğu | Doğrulama motoru |

**Sızıntı önlemi:** Tespit modelinin eğitim/test bölmesi **şablon-ayrıktır** —
test örnekleri, eğitimde hiç görülmemiş kalıplardan üretilir. Aynı şablonun
farklı örneklerinin iki tarafa dağılması engellenerek ezberin başarım gibi
görünmesinin önüne geçilmiştir.

### Model eğitimi ve karşılaştırma

Her modül için önce **temel çizgi (baseline)** kurulmuş, ince ayarlı model
ona karşı raporlanmıştır. Temel çizgisiz bir başarım sayısı yorumlanamaz.

### Aşırı öğrenme (overfitting) önlemleri

1. **Şablon-ayrık bölme** — test kümesi eğitimde görülmemiş kalıplardan gelir
2. **Eşik taraması** — kümeleme eşiği tek bir değerde sabitlenmeyip taranmış,
   seçilen değer gerekçesiyle raporlanmıştır
3. **Dağılım ayrımı** — belirsizlik bandı kalibrasyonu akış dağılımında
   yapılır; test kümesi sınıf-dengeli olduğu için bandın oraya taşınması
   ölçümü bozacağından bilinçle kaçınılmıştır
4. **Temel çizgi karşılaştırması** — ince ayarlı model her zaman basit bir
   yöntemle birlikte raporlanır

### Performans metrikleri

**Tablo 1 — Yapay üretim metin tespiti** (245 örnek: 132 yapay, 113 insan)

| Model | Doğruluk | F1 | AUROC | FPR@95TPR |
|---|---|---|---|---|
| TF-IDF temel çizgi | 0,984 | 0,985 | 1,000 | **0,000** |
| BERTurk ince ayar | 1,000 | 1,000 | 1,000 | **0,000** |

FPR@95TPR bu tablodaki en kritik metriktir: yapay metinlerin %95'ini yakalayan
eşikte, **kaç insan metninin haksız yere etiketlendiğini** gösterir. Ürün
açısından yanlış pozitif, kaçırılan pozitiften daha maliyetlidir; masum bir
kullanıcıyı damgalamak güveni doğrudan zedeler.

> **Bu tablo bir üst sınırdır, ürün başarımı değildir.** Test kümesi, modelin
> eğitildiği şablon havuzundan gelir; sınıfları tasarlayan taraf ile ölçen
> taraf aynıdır. Sistemin şablon paylaşmayan veri üzerindeki davranışı
> **Tablo 7**'de, gerçek insan metni üzerindeki davranışı **Tablo 8**'dedir.
> Raporun dayandığı sayılar onlardır.

**Tablo 2 — Çekimserlik davranışı**

| Model | Çekimserlik oranı | Etiketlendiğinde doğruluk |
|---|---|---|
| TF-IDF temel çizgi | %17,1 | 1,000 |
| BERTurk ince ayar | %0,0 | 1,000 |

Çekimserlik bir başarısızlık değil, **raporlanan bir ürün davranışıdır**.
Sistem emin olmadığında hiçbir rozet göstermez. Son sütun, kullanıcının
gördüğü etiketlerin ne kadar güvenilir olduğunu verir — kullanıcı açısından
anlamlı olan tek sayı budur.

**Tablo 3 — Kümeleme kalitesi** (gömme: `multilingual-e5-base`, eşik 0,13)

| Metrik | Değer |
|---|---|
| ARI | 0,250 |
| Homojenlik | 0,845 |
| Bütünlük | 0,525 |
| V-ölçüsü | 0,648 |

Homojenliğin bütünlükten yüksek olması **bilinçli bir tercihtir**. Aynı olayın
birden çok kümeye bölünmesi, özette aynı konu hakkında iki cümle üretir —
fazlalıktır, ama her cümle kaynağına bağlıdır. Buna karşılık iki farklı olayın
tek kümede birleşmesi, kaynağa bağlanamayan bir iddia doğurur ve atıf
zorunluluğu ilkesini çiğner. Bu nedenle eşik, birleşme yerine bölünme
yönünde kalibre edilmiştir.

**Tablo 4 — Özetleme sadakati** (420 gönderi, 90 üretilen cümle)

| Metrik | Değer |
|---|---|
| Kaynağa sadakat (ortalama) | 0,937 |
| Sadakat ≥ 0,80 olan cümle oranı | 1,000 |
| Atıf doğruluğu | 1,000 |
| Atıfsız üretim (silinen cümle) | 0 |
| Özet gecikmesi (p50) | 962 ms |

**Tablo 5 — Asistan davranışı** (72 örnek)

| Metrik | Değer |
|---|---|
| Bağlam dışı soruda doğru reddetme | 0,972 |
| Bağlam içi soruda yanıt verme | 1,000 |
| Aşırı çekimserlik (yanıtlanabilirken susma) | 0,000 |
| Yanıtın kaynak taşıma oranı | 1,000 |

Son iki satır birlikte okunmalıdır: sistem yalnızca susmayı öğrenmiş değildir.
Yanıtlanabilir sorularda susma oranı sıfırdır; yani çekimserlik seçicidir.

**Tablo 6 — İstem enjeksiyonu savunması** (40 senaryo, 9 saldırı türü)

| Saldırı türü | Savunulan / Toplam |
|---|---|
| Doğrudan talimat | 8/8 |
| Kaynak zehirleme | 6/6 |
| Rol değiştirme | 6/6 |
| Gizli metin | 5/5 |
| Sınırlayıcı kaçırma | 4/4 |
| Sistem sızdırma | 4/4 |
| Atıf saldırısı | 3/3 |
| Çoğulculuk saldırısı | 2/2 |
| Veri sızdırma | 2/2 |
| **Toplam** | **40/40 (%100)** |

Savunma dört katmanlıdır: yapısal ayrım, girdi temizleme, çıktı kısıtı ve
yetki kısıtı. Asistanın yazma yetkisi yoktur; ajan yalnızca izin listesindeki
araçları çağırabilir.

**Tablo 7 — Aktarım testi: şablon paylaşmayan veri** (206 gönderi: 37 yapay, 169 insan)

Tablo 1'in test kümesi tespit modelinin eğitildiği şablon havuzundan gelir.
Aşağıdaki ölçüm ise sosyal medya akışı üretecinden gelen ve tespit veri
setiyle **hiçbir şablon paylaşmayan** gönderiler üzerindedir.

| Model | Doğruluk (0,5 eşiği) | AUROC | FPR@95TPR | Çekimserlik |
|---|---|---|---|---|
| TF-IDF temel çizgi | 0,709 | 0,965 | 0,361 | %55,3 |
| BERTurk ince ayar | 0,675 | 0,980 | 0,118 | %54,4 |

Doğruluğun 1,000'den 0,675'e inmesi, Tablo 1'deki sayının ne kadarının
şablon ezberinden geldiğini gösterir.

**Kullanıcının gördüğü sayı.** Yukarıdaki doğruluk 0,5 eşiğiyle hesaplanır ve
ürün davranışını yansıtmaz: sistem 0,5 eşiğiyle etiket göstermez, **akış
dağılımında kalibre edilmiş bantla** gösterir. Akışın yarısı bandı seçmekte,
diğer yarısı ölçmekte kullanılır; aynı gönderilerde hem eşik seçip hem ölçüm
yapmak, olmayan bir başarım iddia etmek olurdu.

| Model | Kalibre bant | Etiketlenen | Etiketlendiğinde doğruluk |
|---|---|---|---|
| TF-IDF temel çizgi | `[0,92 · 0,83]` | 92/206 | **1,000** |
| BERTurk ince ayar | `[0,99 · 0,98]` | 94/206 | **1,000** |

**Tohum değişkenliği.** Aynı veri, aynı hiperparametreler, yalnızca rastgelelik
tohumu değişiyor — 5 tohum. Doğrulama kümesinde bu beş model **1,000 ± 0,000**
verir; o sayı modelin kararlı olduğunu değil, doğrulama kümesinin doyduğunu
gösterir. Aktarım kümesinde:

| Metrik | Ortalama ± std | En düşük | En yüksek |
|---|---|---|---|
| Doğruluk (0,5 eşiği) | 0,511 ± 0,148 | 0,335 | 0,699 |
| AUROC | 0,917 ± 0,038 | 0,873 | 0,980 |
| Etiketlendiğinde doğruluk — sabit bant | 0,586 ± 0,170 | 0,380 | 0,875 |
| Etiketlendiğinde doğruluk — kalibre bant | **1,000 ± 0,000** | 1,000 | 1,000 |
| Etiketlenen oran — kalibre bant | 0,304 ± 0,129 | 0,136 | 0,456 |

Son iki satır birlikte okunmalıdır: kalibrasyon, tohumdan gelen salınımı
**doğruluktan kapsamaya** taşır. Kötü bir tohum artık yanlış etiket üretmek
yerine daha çok susar. İlke 2'nin istediği takas budur; kullanıcıya verilen
garanti tohumdan bağımsız hâle gelir, bedeli daha az gönderiye etiket
gösterilmesidir.

**Tablo 8 — Gerçek insan metni üzerinde tespit** (374 örnek: 174 yapay, 200 insan)

Yukarıdaki her ölçüm, iki sınıfı da bizim ürettiğimiz veri üzerindedir. Bu
tabloda insan sınıfı **gerçek kişilerin yazdığı metinlerden** gelir:
`turkish-nlp-suite/vitamins-supplements-reviews` (CC BY-SA 4.0), 2022 derlemi
— yani dil modelleri yaygınlaşmadan önce yazılmış ürün yorumları. Yapay sınıf
aynı ürün, aynı yıldız puanı ve aynı uzunluk eşleştirmesiyle üretildi.
Eşleştirme zorunluydu: iki sınıf farklı konulardan gelseydi model yazarı değil
**konuyu** öğrenirdi.

| Model | AUROC | FPR@95TPR | Doğruluk (0,5) | F1 (0,5) |
|---|---|---|---|---|
| TF-IDF temel çizgi | 0,541 | 0,935 | 0,537 | 0,362 |
| BERTurk ince ayar | **0,768** | 0,640 | 0,548 | 0,056 |

Bu tablo iki şey söylüyor:

1. **Sentetik değerlendirme başarımı şişiriyor.** AUROC 1,000 → 0,980
   (aktarım) → 0,768 (gerçek metin). Sentetik veride ölçülen sayının yaklaşık
   dörtte biri, sınıfları bizim yazmış olmamızdan geliyor.
2. **Temel çizgi ile ince ayarın sırası ilk kez ayrışıyor.** Sentetik veride
   TF-IDF ile BERTurk arasında anlamlı fark yoktu (ikisi de 1,000); gerçek
   metinde TF-IDF **rastgeleye yakın** (0,541), BERTurk ise bilgi taşıyor
   (0,768). Yani ince ayarın karşılığı ancak gerçek veride görünüyor.

**Üslup bazında kaçış** (yalnızca yapay sınıf, 0,5 eşiği). Yapay metinler beş
üslupta üretildi; düz "asistan ağzı" bilerek azınlıkta tutuldu, çünkü tespiti
yalnızca en kolay üslupta ölçmek kendimizi kandırmak olurdu.

| Üslup | n | TF-IDF | BERTurk |
|---|---|---|---|
| `asistan` (düz yardımcı dili) | 33 | 0,455 | 0,061 |
| `dengeli` | 25 | 0,360 | 0,040 |
| `pazarlama` | 20 | 0,300 | 0,000 |
| `samimi` | 54 | 0,204 | 0,037 |
| `hatali` (yazım hatalı) | 42 | 0,190 | **0,000** |

Yazım hatası eklemek tespitten kaçmak için yeterlidir. Bu, tespit modelinin
tek başına bir savunma olamayacağının doğrudan kanıtıdır.

**Bu dağılım için kalibre edilseydi ne olurdu.** Eşik kümenin bir yarısında
seçilip diğer yarısında ölçüldü; hedef, etiket gösterildiğinde doğruluk ≥ 0,95.

| Model | Etiketlenen | Etiketlendiğinde doğruluk |
|---|---|---|
| TF-IDF temel çizgi | %1,1 | 1,000 |
| BERTurk ince ayar | %2,1 | 0,750 |

Sistem, gerçek metinde hedef kesinliği tutturmak için gönderilerin **%98'inde
susmak zorunda kalıyor**. Ürünün bugünkü dürüst konumu budur: yapay zekâ
metni tespiti bir *sinyal* olarak sunulabilir, bir *hüküm* olarak sunulamaz.

### Ölçümlerin sınırları

> **Bu bölüm bilinçli olarak yazılmıştır.** Kusursuz sonuçları kayıtsız sunmak,
> değerlendirmenin ciddiyetine gölge düşürür.

**Sentetik veride ölçülen başarımın ne kadarı gerçek değildi — ölçüldü.**
Tablo 1'deki %100 doğruluk, sentetik veri üzerinde elde edilmiş bir üst
sınırdır. Şablon-ayrık bölme ezberi engeller, ancak şablondan üretilmiş
metinler gerçek kullanıcı diline kıyasla daha türdeştir. Bu bölüm önceki
sürümde "gerçek veride başarımın düşmesi beklenmektedir" diyordu; artık
beklenti değil ölçüm var:

| Ölçüm kümesi | BERTurk AUROC | Ne anlama geliyor |
|---|---|---|
| Kendi test kümemiz (Tablo 1) | 1,000 | Sınıfları biz yazdık |
| Şablon paylaşmayan akış (Tablo 7) | 0,980 | Kalem aynı, şablon farklı |
| Gerçek insan metni (Tablo 8) | **0,768** | İnsan tarafını biz yazmadık |

Düşüşün büyük kısmı ikinci adımda değil üçüncüde oluyor: sorun şablon
ezberi değil, **insan metninin bizim yazdığımızdan farklı olması**.

**Gerçek metin ölçümünün kendi sınırı.** Tablo 8'de insan tarafı gerçektir,
yapay taraf hâlâ bize aittir; tek bir modelle (Claude Opus 5) üretilmiştir.
Farklı bir modelin metni farklı sonuç verebilir. Ayrıca alan tektir (ürün
yorumları), sosyal medya gönderisi değil. Yani Tablo 8, gerçek başarımın
kendisi değil, sentetik ölçümden **daha yakın bir alt sınırıdır**.

**Enjeksiyon savunması hâlâ sentetiktir.** Tablo 6'daki %100, bizim
yazdığımız 40 senaryo üzerindedir. Gerçek saldırganların deneyeceği türlerin
tamamını kapsadığı iddia edilemez; o sayı "bilinen saldırı türlerine karşı
dayanıklıyız" demektir, "saldırılamaz" demek değildir.

**Bu ölçümlerin ürün tasarımına etkisi.** Sistem, yüksek başarıma değil
**düşük yanlış pozitife ve çekimserliğe** yaslanacak biçimde tasarlanmıştır:
model yanıldığında zarar, sustuğunda yalnızca eksik bilgi doğar. Tablo 8'in
son satırı bunun bedelini de gösteriyor — gerçek metinde hedef kesinliği
tutturmak, gönderilerin %98'inde susmak demek. Arayüz bu yüzden yapay zekâ
etiketini yalnızca eşiği geçen gönderide gösterir ve **"insan yazmış" rozetini
hiç göstermez**: 0,768 AUROC bir metnin yapay olabileceğine işaret etmeye
yeter, bir metnin insan elinden çıktığını **belgelemeye yetmez**.

Mentörlük sürecinde (2-7 Eylül) ölçümlerin gerçek NSosyal akış örneği üzerinde
yinelenmesi hedeflenmektedir.

*[Kontrol maddeleri: veri ön işleme (2p) · model eğitimi (2p) · overfitting
önlemleri (1p) · performans metrikleri (1p)]*

---

## 3.3. Kullanıcı Deneyimi (UI/UX) Tasarımı

### Tasarım kısıtı — platform kimliğine sadakat

NSosyal kendini **reklamsız, algoritmasız ve kronolojik** akış olarak tanımlar.
MİHENK bu kimliğe karşı değil, üstüne konumlanır:

> **Akış sırası değişmez.** MİHENK sıralamaya müdahale etmez; akışın üzerine
> oturan bir okuma ve doğrulama katmanı sunar.

Bu kısıt bir sınırlama değil, ürünün ayırt edici tarafıdır. Arayüzde "kişiselleştirilmiş
akış", "öneri algoritması" gibi kavramlar bilinçli olarak kullanılmamış; özet
paneli kendi başlığında **"Akış sırası değişmez — bu yalnızca bir okuma
katmanıdır"** ifadesini taşımaktadır.

### Kullanıcı akışları

**Akış 1 — Gündemi kavrama.** Ana sayfa → üstteki özet paneli → kategori sekmesi
seç (Ülke Gündemi / Spor / Teknoloji / Ekonomi / Kişisel) → olay özeti →
çerçeve dağılımı → istenirse kaynak gönderilere geçiş.

**Akış 2 — Bir iddiayı sınama.** Akışta gönderi → "Doğrula" → sonuç (Doğrulandı /
Yanlış / Doğrulanamadı) + güven göstergesi + kaynak listesi.

**Akış 3 — Bağlamı anlama.** Gönderiye tıkla → detay sayfası → aynı olaydaki
tüm gönderiler ve çerçeve dengesi bir arada.

**Akış 4 — İçerik üretici.** İçerik Üretici paneli → en verimli paylaşım
zamanları → gün içi etkileşim dağılımı → gündemden konu önerileri.

### Arayüz tasarım kararları ve gerekçeleri

| Karar | Gerekçe |
|---|---|
| Özet paneli akışın **üstünde**, kapatılabilir | Kullanıcı akışı terk etmeden gündemi kavrar; istemeyenin önünü tıkamaz |
| MİHENK eylemleri **mor aksan** ile ayrıştırıldı | Platformun mavi kimliğinden ayrışır; hangi işlevin katmana ait olduğu bakışta anlaşılır |
| "Doğrula" yalnızca **sınanabilir iddia içeren** gönderilerde | Her gönderiye doğrulama düğmesi koymak, doğrulamayı anlamsızlaştırır |
| Kaynak sayısı **her cümlenin yanında** | Atıf, dipnot değil ürünün kendisidir; okurken görünür olmalıdır |
| Silinen cümle ve bastırılan küme sayısı **gizlenmez** | Sistemin ne yapmadığını göstermek güveni artırır |
| Bot işareti içeriği **gizlemez, sıralamayı düşürmez** | Platformun algoritmasız kimliğiyle çelişmemek; karar kullanıcıda kalır |

### Erişilebilirlik yaklaşımı

Erişilebilirlik, sonradan eklenen bir katman değil tasarım kısıtı olarak ele
alınmıştır. Ayarlar → Erişilebilirlik ve Görünüm bölümünde kullanıcıya sunulan
denetimler:

- **Tema seçimi** (açık/koyu), tercih cihazda kalıcı
- **Yazı boyutu** %85-150 aralığında ayarlanabilir
- **Yüksek kontrast** modu
- **Hareketi azalt** — animasyon ve geçişleri kapatır; vestibüler duyarlılık için

Kod düzeyinde uygulananlar:

- Tüm etkileşimli ögelerde ARIA rolleri ve `aria-label`
- Görünür klavye odak halkaları (`:focus-visible`)
- "Ana içeriğe geç" atlama bağlantısı
- Sekme ve anahtarlarda `role="tab"`, `role="switch"`, `aria-checked`
- Grafiklerde `role="img"` ve metinsel eşdeğer
- `prefers-reduced-motion` sistem tercihine uyum

**Bu liste bir iddia değil, ölçülmüş bir sonuçtur.** Denetim
`02-prototip/scripts/erisilebilirlik-denetimi.mjs` ile yapılır; jüri aynı
komutu çalıştırıp aynı sonucu alabilir. Araç **axe-core 4.13** (Deque Systems),
ölçüt **WCAG 2.0/2.1 seviye A + AA**. Ölçüm üretim derlemesi üzerinde koşar.

**Tablo 9 — Erişilebilirlik denetimi** (6 sayfa × 2 tema = 12 koşu)

| Ölçüm | Değer |
|---|---|
| WCAG A/AA ihlali | **0** |
| Odak halkası görünmeyen sekme durağı | **0** |
| Klavye tuzağı | **bulunmadı** |

Bu tablo ilk koşuda böyle değildi ve düzeltme süreci raporlanmaya değer:

1. **46 düğümde kontrast ihlali** çıktı. Dağınık kusurlar değildi; üçü de renk
   jetonuydu. `metin-sonuk` kart yüzeyinde 3,21:1 veriyordu (gereken 4,50).
   `mavi` ve `mihenk` ise *dolu zemin* olarak kullanıldığında batıyordu — bir
   renk, hem koyu zeminde metin hem de beyaz metin taşıyan dolu zemin rolünü
   aynı anda AA seviyesinde taşıyamaz. Palet iki rol ayrılarak düzeltildi.

2. **Asıl bulgu ölçüm aracının kendisindeydi.** İlk koşu açık temayı hiç
   ölçmemişti: betik temayı `prefers-color-scheme` ile açmaya çalışıyordu, oysa
   arayüz `data-tema` özniteliğini okuyor. İki koşu da karanlık temayı ölçüyor,
   sonuç "iki temada da temiz" görünüyordu. Düzeltilince açık temada **190
   düğümlük** ihlal ortaya çıktı: aksan renklerinin tamamı koyu zemin için
   seçilmişti. Açık tema için ayrı bir aksan seti tanımlandı.

İkinci madde, bu raporun Tablo 1 ile Tablo 8 arasındaki farkın da açıklamasıdır:
**ölçüm aracı yanlış ölçtüğünde sonuç kusursuz görünür.**

**Otomatik denetimin göremediği.** "0 ihlal", "erişilebilir" demek değildir.
Odak sırasının mantıklı olması, ekran okuyucunun okuduğu metnin anlamlı olması
ve çekimserlik mesajının bilişsel olarak nasıl okunduğu bu araçla ölçülmez;
sonuncusu kullanılabilirlik testinin sorusudur. Bu sınır
`eval/results/erisilebilirlik.md` içinde de yazılıdır.

### Kullanılabilirlik testi

Test protokolü, katılımcı profilleri, görev listesi ve ölçüm formları
hazırlanmıştır (`docs/KULLANILABILIRLIK_TESTI.md`). **Test rapor teslimi
itibarıyla henüz uygulanmamıştır; sonuç tablosu boştur ve öyle bırakılmıştır.**
Ölçülmemiş bir sayıyı rapora yazmamak, bu projede modeller için uygulanan
kuralın (bkz. 3.2) tasarım tarafındaki karşılığıdır.

Uygulandığında ölçülecek büyüklükler protokolde tanımlıdır: görev tamamlama
oranı, görev süresi (elle okuma ile özetle okuma karşılaştırmalı), kavrama
doğruluğu ve SUS puanı. Katılımcı sayısı 5'tir ve bu **istatistiksel bir
örneklem değil, keşifsel bir testtir**; raporda da öyle sunulacaktır.

Testin cevaplaması hedeflenen asıl soru hız değildir: sistem bilinçli olarak
bazen susuyor (İlke 2). Kullanıcı bu sessizliği **"bozuk"** mu yoksa
**"dürüst"** mü okuyor? Otomatik hiçbir denetim bu soruyu yanıtlamaz.

*[Kontrol maddeleri: kullanıcı akışları (2p) · arayüz kararlarının
gerekçelendirilmesi (2p) · erişilebilirlik yaklaşımı (2p) · kullanılabilirlik
testi (1p)]*

---

## Bu bölümde atıf yapılan çalışmalar

[4] Schweter, S., BERTurk — BERT models for Turkish, 2020, Erişim: 22.08.2026,
https://doi.org/10.5281/zenodo.3770924

[5] Wang, L. ve diğerleri, (2024) Multilingual E5 Text Embeddings: A Technical
Report, arXiv:2402.05672, https://doi.org/10.48550/arXiv.2402.05672
