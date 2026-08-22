# 2. KATMA DEĞER VE YENİLİKÇİLİK

> Bu bölüm rubrikte **15 puan** değerindedir. Aşağıdaki metin doğrudan rapora
> aktarılabilir; her alt başlığın sonunda hangi kontrol maddesini karşıladığı
> köşeli notla belirtilmiştir (rapora aktarırken **bu notlar silinecektir**).

---

## 2.1. Problem Tanımı ve Mevcut Çözümler

### Problemin niteliği

Sosyal medya, Türkiye'de artık marjinal bir iletişim kanalı değil, bilgiye erişimin
birincil altyapısıdır. Türkiye İstatistik Kurumu'nun 2025 yılı Hanehalkı Bilişim
Teknolojileri Kullanım Araştırması'na göre 16-74 yaş grubunda internet kullanım oranı
%90,9'a ulaşmış; bu oran bir önceki yıl %88,8 düzeyindeydi [1]. Aynı dönemde Türkiye'de
62,3 milyon sosyal medya kullanıcı kimliği tespit edilmiş olup bu sayı toplam nüfusun
%70,9'una karşılık gelmektedir [2]. Reuters Institute'un 2026 Dijital Haber Raporu,
küresel ölçekte kullanıcıların %54'ünün haber için sosyal medya ve video platformlarını
kullandığını, %30'unun ise bu platformları birincil haber kaynağı olarak tanımladığını
göstermektedir; bu oran beş yıl önce %22 düzeyindeydi [3].

Ancak bu erişim genişliği, doğrudan bilgi edinmeye dönüşmemektedir. Sorun iki eksende
birikmektedir.

**Birinci eksen — bilgi aşırı yüklenmesi ve kaçınma.** Kullanıcı, gündemi kavramak için
sınırsız uzunlukta bir akışı elle taramak zorunda kalmakta; bu yük zamanla katılımı
artırmak yerine geri çekilmeye yol açmaktadır. Reuters Institute 2026 verilerine göre
haberden kaçınma küresel ortalaması %42 iken **Türkiye, bu oranın %60 ve üzerinde
seyrettiği dört ülkeden biridir** [3]. Yani Türkiye'de sorun, kullanıcının bilgiye
erişememesi değil, erişebildiği bilgi hacmini işleyememesi ve bunun sonucunda gündemden
bütünüyle uzaklaşmasıdır.

**İkinci eksen — güven erozyonu ve doğrulama yükü.** Aynı rapor, habere duyulan güvenin
%37 ile 2015'ten bu yana en düşük seviyeye indiğini; internetteki içeriğin gerçekliğine
ilişkin kaygının küresel ortalamada %62'ye yükseldiğini ortaya koymaktadır [3]. Sosyal
medya üzerinden gelen habere duyulan güven ise yalnızca %22'dir [3]. Kullanıcı, gördüğü
bir iddianın doğruluğunu sınamak için akıştan çıkıp bağımsız arama yapmak zorunda
kalmakta; bu maliyet nedeniyle çoğu zaman doğrulama hiç yapılmamaktadır.

Bu iki eksen birbirini beslemektedir: aşırı yük doğrulamayı pahalı hale getirmekte,
doğrulanmamış içeriğin yaygınlaşması ise güveni daha da aşındırarak kaçınmayı
derinleştirmektedir.

*[Kontrol maddesi: gerçek ve nesnel problem tanımı (2p) + problemin büyüklüğünü gösteren
istatistik (1p) + resmî/akademik kaynak desteği (2p) — TÜİK resmî kaynak, Reuters
Institute akademik araştırma kuruluşu.]*

### Mevcut çözümler ve yetersizlikleri

Piyasada bu iki eksene kısmî yanıtlar veren çözümler bulunmakta, ancak hiçbiri
Türkçe sosyal medya bağlamında bütünsel bir karşılık üretmemektedir.

**Platform içi yapay zekâ özetleri (X/Grok tabanlı gündem özetleri).** Akış içinde özet
sunması bakımından en yakın örnektir. Buna karşılık tek bir platforma kilitlidir,
özetleri kullanıcının ilgi alanlarına göre kategori bazında ayrıştırmaz ve üretilen
özetin hangi kaynaklara dayandığı ile ne düzeyde güvenilir olduğu kullanıcıya sistematik
biçimde gösterilmez. Türkçe içerikte ise özet kalitesi, dilin sondan eklemeli yapısı ve
yerel bağlam bilgisi gerektiren ifadeler nedeniyle İngilizce içeriğin gerisinde
kalmaktadır.

**Haber kaynağı karşılaştırma servisleri (Ground News vb.).** Aynı olayın farklı
yayın çizgilerindeki sunumunu karşılaştırması yönüyle değerlidir. Ancak girdi olarak
kurumsal haber makalelerini almakta, sosyal medya akışının kendisini işlememektedir;
Türkçe kaynak kapsaması sınırlıdır ve kullanıcının kişisel akışıyla hiçbir bağı yoktur.

**Topluluk temelli doğrulama (Community Notes benzeri mekanizmalar).** Ölçeklenebilir ve
şeffaf bir yaklaşımdır; buna karşılık insan katkısına bağlı olduğu için gecikmelidir.
Bir içerik en yüksek yayılım hızına ulaştığı ilk saatlerde çoğunlukla henüz not
almamış olur ve kapsama oranı, üretilen içerik hacminin çok altında kalır.

**Genel amaçlı yapay zekâ asistanları (ChatGPT, Perplexity vb.).** Doğrulama ve
açıklama kabiliyeti güçlüdür, ancak kullanıcının akışından kopuktur. Kullanıcı, sormak
istediği içeriği manuel olarak kopyalayıp ayrı bir uygulamaya taşımak zorundadır; bu
bağlam kaybı, doğrulamanın günlük kullanım alışkanlığına dönüşmesini engellemektedir.
Ayrıca Reuters Institute verilerine göre kullanıcıların yapay zekâ tarafından üretilen
cevaplara duyduğu güven yalnızca %20'dir [3]; bu bulgu, bir çözümün sadece "yapay zekâ
ile özetlemesinin" yeterli olmadığını, çıktının kaynak ve güven göstergeleriyle birlikte
sunulmasının zorunlu olduğunu göstermektedir.

**Ortak boşluk.** Mevcut çözümlerin hiçbiri; kategori bazlı kişiselleştirilmiş özet,
gönderi düzeyinde açıklama, kaynak gösterimli doğrulama ve görsel köken denetimini
tek bir Türkçe akış deneyimi içinde birleştirmemektedir.

*[Kontrol maddesi: mevcut alternatif çözümler ele alınmış (1p) + eksik/yetersiz yönleri
açıkça belirtilmiş (1p).]*

---

## 2.2. Çözüm Fikri, Özgünlük ve Yerlilik

### Çözümün tanımı

ITS MİHENK, adını bir değerin gerçekliğini sınayan "mihenk taşı" kavramından alan;
NSosyal deneyimini simüle eden, yapay zekâ destekli bir akış anlama ve doğrulama
katmanıdır. Sistem, kullanıcının önüne çıkan içerik yığınını dört işlevle
işlenebilir hale getirir:

1. **Kategori bazlı özet katmanı.** Kullanıcı akışın en üstünden tek bir etkileşimle
   ülke gündemi, spor gündemi ve kişisel akış başlıklarında ayrı özetlere ulaşır.
   Özetler, kullanıcının ilgi alanları ve etkileşim geçmişine göre kişiselleştirilir.
2. **Gönderi düzeyinde özet ve açıklama.** Herhangi bir gönderi, bağlamından kopmadan
   özetlenebilir; entegre dijital asistan gönderi hakkındaki soruları yanıtlar.
3. **Ajan tabanlı doğrulama.** Sistem, sınanabilir bir iddia tespit ettiğinde gerekli
   adımları planlayan, uygun araçları devreye alan ve açık web kaynaklarını tarayan
   agentic bir akış yürütür. Çıktı, kullanıcıya **kaynaklar ve güven göstergesiyle
   birlikte** sunulur; bu tasarım kararı, yapay zekâ çıktılarına duyulan %20'lik
   güven düzeyine [3] doğrudan verilmiş bir yanıttır.
4. **Görsel köken ve üretim denetimi.** Görsel içeriklerde üretim etiketleri, içerik
   kökeni ve görsel bulgular üzerinden olasılık temelli uyarılar üretilir.

Buna ek olarak **içerik üreticisi modülü**, takipçi eğilimlerini ve etkileşim verilerini
kişisel bilgilerden arındırılmış biçimde analiz ederek içerik fikri, konu ve paylaşım
zamanı önerileri sunar.

*[Kontrol maddesi: çözüm fikri probleme/amaca uygun ve net biçimde ifade edilmiş (2p).]*

### Yenilikçi yönler

Çözümün özgünlüğü tekil bir işlevde değil, dört tasarım kararının birleşiminde
yoğunlaşmaktadır.

**Özet tarafsızlığı ve çok kaynaklı dengeleme.** Gündem özeti üreten her sistem örtük
bir editoryal karar verir: aynı olayı hangi çerçeveden anlatacağını seçer. Literatürde
algoritmik önyargı olarak tanımlanan bu risk, mevcut özetleme çözümlerinde büyük ölçüde
ele alınmamaktadır. MİHENK, bir olay etrafındaki gönderileri çerçevelerine göre
ayrıştırarak özetin tek bir bakış açısına savrulmasını engelleyen bir dengeleme adımı
uygular ve kullanıcıya özetin hangi çerçeve dağılımından üretildiğini gösterir.

**Doğrulamanın akış içine gömülmesi.** Doğrulama, ayrı bir uygulamaya geçiş gerektiren
bir eylem olmaktan çıkarılıp gönderinin bulunduğu bağlamda, tek etkileşimle
erişilebilir hale getirilmektedir.

**Hibrit model mimarisi.** Özetleme ve görsel denetim gibi yüksek frekanslı, dar
kapsamlı görevler yerel olarak çalıştırılan özgün modellerle; güncel dünya bilgisi ve
web taraması gerektiren doğrulama görevleri ise dış servislerle yürütülür. Bu ayrım,
hem birim maliyeti düşürmekte hem de dış servis bağımlılığını azaltmaktadır.

**İzinli ve anonimleştirilmiş veri döngüsü.** Kullanıcı rızasıyla elde edilen etkileşim
sinyalleri kişisel bilgilerden arındırılarak toplulaştırılır; ortaya çıkan Türkçe sosyal
medya eğilimleri, yerel bağlamı anlayan modellerin geliştirilmesinde kullanılır.

*[Kontrol maddesi: çözümün güçlü ve yenilikçi yönleri belirtilmiş (2p).]*

### Mevcut çözümlerle karşılaştırma

| Yetenek | Platform içi AI özeti | Ground News | Community Notes | Genel amaçlı LLM | **ITS MİHENK** |
|---|---|---|---|---|---|
| Kategori bazlı kişisel özet | Kısmî | Yok | Yok | Yok | **Var** |
| Gönderi düzeyinde özet | Kısmî | Yok | Yok | Manuel | **Var** |
| Akış içinde doğrulama | Sınırlı | Yok | Gecikmeli | Bağlam dışı | **Var** |
| Kaynak + güven göstergesi | Sınırlı | Var | Var | Değişken | **Var** |
| Özet tarafsızlığı dengelemesi | Yok | Kısmî | Yok | Yok | **Var** |
| Görsel köken/AI üretim denetimi | Yok | Yok | Yok | Kısmî | **Var** |
| İçerik üreticisi öneri modülü | Yok | Yok | Yok | Yok | **Var** |
| Türkçe için özel eğitilmiş model | Yok | Yok | — | Yok | **Var** |

*[Kontrol maddesi: mevcut çözümlerden farkı somut piyasa kıyaslarıyla gösterilmiş (2p).]*

### Pazarda uygulanabilirlik

Çözüm, sıfırdan bir sosyal ağ kurmayı değil, mevcut bir platformun üzerine oturan bir
katman sunmayı hedeflemektedir. Bu konumlandırma, kullanıcı kazanımı maliyetini ortadan
kaldırmakta ve ürünün doğrudan NSosyal altyapısıyla entegre edilebilir olmasını
sağlamaktadır. İlk aşamada NSosyal deneyimini simüle eden çalışan bir web prototipi
geliştirilmekte; prototip, gerçek platform verisi yerine kontrollü ve etiketli bir
simülasyon veri kümesi üzerinde çalışmaktadır. Bu yaklaşım, entegrasyon öncesinde tüm
modüllerin ölçülebilir biçimde doğrulanmasına imkân vermektedir.

*[Kontrol maddesi: çözümün pazarda uygulanabilir olduğu gösterilmiş (1p).]*

### Yerli bileşenler

Proje kapsamında geliştirilen ve doğrudan proje ekibine ait olan yerli bileşenler
şunlardır:

- **Türkçe özetleme modeli.** Türkçe için ön eğitimden geçirilmiş açık kaynaklı bir
  temel model, proje kapsamında oluşturulan Türkçe sosyal medya veri kümesi üzerinde
  ince ayarlanarak (fine-tuning) sisteme özgü bir özetleme modeli elde edilmektedir.
  Model yerel donanımda çalıştırılmakta, dış servise ihtiyaç duymamaktadır.
- **Görsel üretim tespit modeli.** Görsellerin yapay zekâ ile üretilip üretilmediğini
  sınıflandıran model yerel olarak çalıştırılmaktadır.
- **Etiketli Türkçe değerlendirme veri kümesi.** Olay kümesi, çerçeve türü, sınanabilir
  iddia ve görsel köken etiketlerini içeren; kümeleme, özet tarafsızlığı, doğrulama ve
  görsel tespit modüllerinin başarımının ölçülmesini sağlayan özgün bir veri kümesi
  proje kapsamında üretilmiştir.

*[Kontrol maddesi: en az bir yerli bileşen/teknoloji kullanıldığı/geliştirildiği
belirtilmiş (1p) — üç ayrı bileşenle fazlasıyla karşılanmaktadır.]*

---

## Bu bölümde kullanılan kaynaklar

> Nihai raporda bunlar **9. Kaynakça** bölümüne, diğer bölümlerin kaynaklarıyla
> birlikte tek numaralandırma altında taşınacaktır.

[1] Türkiye İstatistik Kurumu, Hanehalkı Bilişim Teknolojileri (BT) Kullanım
Araştırması 2025, 27.08.2025, Erişim: 19.08.2026, https://www.tuik.gov.tr

[2] Kemp, S., Digital 2026: Turkey, DataReportal, 2026, Erişim: 19.08.2026,
https://datareportal.com/reports/digital-2026-turkey

[3] Reuters Institute for the Study of Journalism, Digital News Report 2026 —
Overview and Key Findings, University of Oxford, 2026, Erişim: 19.08.2026,
https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2026/dnr-executive-summary
