# 1. PROJE ÖZETİ

> Rubrikte **15 puan** (1.1: 7p + 1.2: 8p). Köşeli notlar rapora aktarılırken
> **silinecektir**.

---

## 1.1. Proje Konusu ve Amacı

Projenin konusu, sosyal medya ekosisteminde bilgi aşırı yüklenmesi ve
doğrulama maliyeti sorunudur. Türkiye İstatistik Kurumu'nun 2025 verilerine
göre ülkede internet kullanım oranı %90,9'a ulaşmış, 62,3 milyon sosyal medya
kullanıcı kimliği tespit edilmiştir [1][2]. Ancak bu erişim genişliği bilgiye
dönüşmemektedir: Reuters Institute'un 2026 Dijital Haber Raporu'na göre
Türkiye, haberden kaçınma oranının %60'ı aştığı dört ülkeden biridir; habere
duyulan güven ise %37 ile 2015'ten bu yana en düşük seviyededir [3].

Bu projenin nihai amacı, kullanıcının akıştan kopmadan gündemi kavramasını ve
gördüğü bir iddiayı kaynağıyla birlikte sınayabilmesini sağlamaktır. Proje,
**Sosyal Yapay Zekâ** temasına hitap etmektedir; şartnamenin bu tema için
örnek çözüm alanı olarak saydığı "içerik özetleme teknolojileri", "yapay zekâ
destekli dijital asistanlar", "spam ve bot tespit sistemleri" ve "duygu
analizi" başlıklarının doğrudan karşılığını oluşturmaktadır. Proje ikincil
olarak İçerik Ekonomisi (içerik üretici öneri modülü) ve Kullanıcı Katılımı &
Arayüz (özet paneli, erişilebilirlik) temalarına da hizmet etmektedir.

## 1.2. Proje Kapsamı ve Yöntemi

Projenin kapsamı, NSosyal deneyimini simüle eden bir web prototipi üzerinde
çalışan bir **anlama ve doğrulama katmanı** geliştirmekle sınırlıdır; yeni bir
sosyal ağ kurmak kapsam dışındadır. NSosyal kendini reklamsız, algoritmasız
ve kronolojik bir platform olarak tanımlamaktadır; bu nedenle proje akışın
sıralamasına müdahale etmemekte, yalnızca akışın üzerine oturan bir okuma
katmanı sunmaktadır.

İzlenecek yöntem iki katmanlı bir mimariye dayanmaktadır. Yüksek frekanslı ve
dar kapsamlı görevler (özetleme, olay kümeleme, görsel ve metin tespiti) yerel
olarak, ince ayarlı açık kaynak modellerle yürütülmekte; güncel dünya bilgisi
gerektiren doğrulama görevi ise agentik bir mimariyle açık web kaynaklarını
tarayan bir dış modelle yürütülmektedir. Bu ayrım, sistemin üç ilkesinin
(atıf zorunluluğu, çekimserlik, çoğulculuk) yanıt şemasına kodlanmasıyla
desteklenmekte ve test edilebilir kılınmaktadır.

Çalışmanın seçilen tematik alanla doğrudan ilişkisi, sistemin her modülünün
şartnamede sayılan örnek çözüm alanlarından en az birine karşılık gelmesiyle
kurulmuştur. Projenin gelecekte yeni çalışmalara zemin hazırlama potansiyeli,
üretilen etiketli Türkçe değerlendirme veri kümesi ve izinli/anonimleştirilmiş
etkileşim verisi üzerinden yerli model geliştirme hattı ile mevcuttur.

Proje yalnızca fikir düzeyinde kalmayıp çalışan bir prototiple
desteklenmektedir: NSosyal arayüzünü birebir simüle eden, 14 sayfadan oluşan,
açık/koyu tema ve mobil görünüm destekleyen bir web uygulaması; dört uç
noktalı bir uygulama servisi; ve etiketli sentetik veri kümesi üzerinde
çalışan değerlendirilebilir modüller (özetleme, kümeleme, metin/görsel tespiti)
hâlihazırda geliştirilmiş durumdadır. Kaynak kod GitHub üzerinde sürüm kontrolü
altındadır ve depo bağlantısı 3.1 bölümünde paylaşılmıştır.

*[Kontrol maddeleri — 1.1: konu tanımı (2p) + amaç (2p) + tema beyanı (2p) +
yarışma hedefleriyle tutarlılık (1p). 1.2: kapsam/sınırlar (2p) + yöntem (2p)
+ seçilen temayla ilişki (2p) + prototip vurgusu (1p) + yeni çalışmalara zemin
(1p)]*
