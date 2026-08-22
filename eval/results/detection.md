# Tablo 4 — YZ Metin Tespiti

> `ml/scripts/evaluate.py` tarafından üretilir. Elle düzenlenmez.

Test kümesi: **245** örnek (YZ 132, insan 113). Bölme şablon-ayrıktır: test örnekleri eğitimde görülmemiş kalıplardan gelir.

## Genel başarım

| Model | Doğruluk | F1 | AUROC | **FPR@95TPR** |
|---|---|---|---|---|
| TF-IDF temel çizgi | 0.984 | 0.985 | 1.000 | **0.000** |
| BERTurk ince ayar | 1.000 | 1.000 | 1.000 | **0.000** |

FPR@95TPR en kritik metriktir: YZ metinlerinin %95'ini yakalayacak eşikte
kaç insan metninin haksız yere etiketlendiğini gösterir.

## Uzunluk kovası bazında doğruluk

| Model | K1 (0-50 token) | K2 (50-100) | K3 (100+) |
|---|---|---|---|
| TF-IDF temel çizgi | 0.959 | 1.000 | 0.989 |
| BERTurk ince ayar | 1.000 | 1.000 | 1.000 |

## Çekimserlik (İlke 2)

Eşikler: `min_detection_tokens=20`, belirsizlik bandı `[0.35, 0.65]` (config sabiti).

Bu tabloda **kalibre bant kullanılmaz**: kalibrasyon akış dağılımında
yapılır, bu test kümesi ise eğitim dağılımından gelir ve sınıf-dengelidir.
Bandı ait olmadığı dağılıma taşımak ölçümü bozar (bkz. aktarım tablosu).

| Model | Çekimserlik oranı | K1 | K2 | K3 | Etiketlenen örnek | Etiketlendiğinde doğruluk |
|---|---|---|---|---|---|---|
| TF-IDF temel çizgi | 17.1% | 6.8% | 16.5% | 26.1% | 203/245 | 1.000 |
| BERTurk ince ayar | 0.0% | 0.0% | 0.0% | 0.0% | 245/245 | 1.000 |

Çekimserlik bir hata değil, ürün davranışıdır: sistem emin olmadığında
hiçbir rozet göstermez. Son sütun, gösterdiği etiketlerin ne kadar
güvenilir olduğunu verir — kullanıcının gördüğü tek sayı budur.

## Aktarım testi — farklı kaynaktan gelen metinler

Yukarıdaki test kümesi, modelin eğitildiği şablon havuzundan gelir
(farklı şablon grupları, ama aynı kalem). Aşağıdaki ölçüm ise
**sosyal medya akışı üretecinden** (`generate_feed.py`) gelen ve tespit
veri setiyle hiçbir şablon paylaşmayan gönderiler üzerindedir.
**Rapora girecek asıl sayı budur**: kendi yazdığımız test kümesindeki
başarım, sınıfları biz tasarladığımız için yapay olarak yüksektir.

Aktarım kümesi: **206** gönderi (YZ 37, insan 169).

Bu, akışın **ölçüm yarısıdır**. Diğer yarı karar bandını kalibre
etmekte kullanılır ve bu tabloya hiç girmez; aynı gönderilerde hem
eşik seçip hem ölçüm yapmak, olmayan bir başarım iddia etmek olurdu.

| Model | Doğruluk | F1 | AUROC | FPR@95TPR | K1 | K2 | K3 | Çekimserlik |
|---|---|---|---|---|---|---|---|---|
| TF-IDF temel çizgi | 0.709 | 0.538 | 0.965 | 0.361 | 0.647 | 0.864 | 1.000 | 55.3% |
| BERTurk ince ayar | 0.675 | 0.525 | 0.980 | 0.118 | 0.634 | 0.864 | 0.444 | 54.4% |

### Kullanıcının gördüğü sayı

Yukarıdaki `Doğruluk` sütunu 0.5 eşiğiyle hesaplanır ve ürün
davranışını YANSITMAZ: sistem 0.5 eşiğiyle etiket göstermez,
kalibre edilmiş bantla gösterir. Kullanıcıya verilen garanti budur:

| Model | Kullanılan bant | Kaynağı | Etiketlenen | Etiketlendiğinde doğruluk |
|---|---|---|---|---|
| TF-IDF temel çizgi | `[0.92, 0.83]` | akışın kalibrasyon yarısında ölçüldü | 92/206 | **1.000** |
| BERTurk ince ayar | `[0.99, 0.98]` | akışın kalibrasyon yarısında ölçüldü | 94/206 | **1.000** |

Bandın bir ucu `None` ise o yönde hiç etiket gösterilmez: hedef
kesinliği (0.95) sağlayan bir eşik bulunamamıştır ve uydurma bir
eşik koymaktansa susmak İlke 2'nin gereğidir.

## Tohum değişkenliği — doğrulama kümesinin göremediği şey

`ml/scripts/seed_variance.py` ile 5 tohumda ölçüldü (aynı veri, aynı hiperparametreler, yalnızca tohum değişiyor; ölçüm yarısı 206 gönderi).

Doğrulama kümesinde bu beş model **1.000 ± 0.000** verir. O sayı modelin
kararlı olduğunu değil, doğrulama kümesinin doyduğunu gösterir:

| Metrik (aktarım) | Ortalama ± std | En düşük | En yüksek |
|---|---|---|---|
| Doğruluk (0.5 eşiği) | 0.511 ± 0.148 | 0.335 | 0.699 |
| AUROC | 0.917 ± 0.038 | 0.873 | 0.980 |
| Etiketlendiğinde doğruluk — sabit bant | 0.586 ± 0.170 | 0.380 | 0.875 |
| Etiketlendiğinde doğruluk — kalibre bant | 1.000 ± 0.000 | 1.000 | 1.000 |
| Etiketlenen oran — kalibre bant | 0.304 ± 0.129 | 0.136 | 0.456 |

Son iki satır birlikte okunur: kalibrasyon, tohumdan gelen salınımı
DOĞRULUKTAN KAPSAMA taşır. Kötü bir tohum artık yanlış etiket üretmek
yerine daha çok susar — İlke 2'nin istediği takas budur. Kullanıcıya
verilen garanti ("etiket gösterildiğinde doğruluk") tohumdan bağımsız
hâle gelir; bedeli, o modelde daha az gönderiye etiket gösterilmesidir.

Model seçimi aktarım başarımına BAKILARAK yapılmaz: diskteki model
belgelenmiş varsayılan tohuma (`20260824`) aittir. Ölçtüğümüz
kümede tohum seçseydik, rapor edilen sayı modelin değil seçimin başarımı olurdu.

## Sınırlılık

Veri seti sentetiktir (spec 2: gerçek platformdan veri kazınmaz) ve iki
sınıfın kalıpları elle yazılmıştır. Sınıfları tasarlayan taraf ile ölçen
taraf aynı olduğunda, kendi test kümesindeki başarım gerçek başarımın
üst sınırıdır — bu yüzden aktarım testi eklenmiştir. Gerçek dağılımda
beklenecek başarım, aktarım satırından da düşük olacaktır; model kararı
her durumda çekimserlik kurallarıyla (İlke 2) sınırlanır.

**"Etiketlendiğinde doğruluk = 1.000" nasıl okunmalı:** Bu sayı ~200
gönderilik bir ölçüm yarısında, etiketlenen ~90 örnek üzerinden gelir.
Hedef kesinlik 0.95 iken gözlenen 1.000, eşik aramasının tutucu
davrandığını ve örneklemin küçük olduğunu gösterir; "sistem hiç
yanılmıyor" demek DEĞİLDİR. Daha büyük bir ölçüm kümesinde bu sayının
hedefe (0.95) doğru inmesi beklenir. Güven aralığı verilmiyor çünkü
kalibrasyon ve ölçüm tek bir bölmeden geliyor.

**Kalibrasyonun görünmeyen maliyeti:** Bant, akıştan ETİKETLİ VERİ ile
seçilir. Gerçek bir dağıtımda bu, üretim dağılımından etiketli örnek
toplamak demektir; bedava değildir ve dağılım kaydıkça tekrarlanır.

**Olasılıklar sıkışık:** BERTurk'ün kalibre bandı `[0.99, 0.98]`
civarına oturuyor — model neredeyse her gönderiye 1'e yakın olasılık
veriyor. Eşik kaydırmak bunu işler hâle getiriyor ama asıl çözüm
olasılık kalibrasyonudur (sıcaklık/Platt ölçekleme). Ölçülmedi.
