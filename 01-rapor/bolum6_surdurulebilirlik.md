# 6. SÜRDÜRÜLEBİLİRLİK

## 6.1. Ticarileştirme Potansiyeli ve İş Modeli

MİHENK'in gelir modeli, kullanıcıdan değil ekosistemin diğer paydaşlarından değer üretmeye dayanır; bu tercih, hizmetin nihai kullanıcı için ücretsiz kalmasını ve NSosyal'in reklamsız kimliğiyle çelişmemesini önceler.

**Katman 1 — İçerik üretici analitiği (B2C, isteğe bağlı).** Temel özet ve doğrulama işlevleri tüm kullanıcılara ücretsiz sunulur. İçerik Üretici panelindeki gelişmiş analitik (rakip kıyaslaması, genişletilmiş geçmiş veri, öncelikli işlem sırası) isteğe bağlı bir abonelik katmanına taşınabilir.

**Katman 2 — Kurumsal doğrulama API'si (B2B).** Haber kuruluşları, kamu kurumları ve markalar; kendi içeriklerinin veya kendileriyle ilgili iddiaların MİHENK'in doğrulama motoru üzerinden taranmasını API erişimiyle satın alabilir. Bu, sistemin B2C kullanıcı sayısından bağımsız bir gelir kalemi oluşturur.

**Katman 3 — Platform lisanslama.** MİHENK, NSosyal'e özgü olmayan bir mimariyle tasarlanmıştır (istemci-servis ayrımı, tiplenmiş API sözleşmesi). Bu, ileride başka sosyal platformlara da lisanslanabilir bir "doğrulama katmanı" ürünü olma potansiyeli taşır.

Ürünün mevcut pazar şartlarında üretilebilirliği, prototipin hâlihazırda çalışıyor olmasıyla desteklenmektedir; ek maliyet esas olarak model eğitimi ve sunucu altyapısından oluşmakta, bunlar da yerel katmanın (Katman 1) dış servise bağımlı olmayan tasarımı sayesinde sınırlı tutulmaktadır.

## 6.2. Finansal, Teknik ve Sosyal Sürdürülebilirlik

**Finansal sürdürülebilirlik**, maliyet yapısının kullanıcı sayısıyla doğrusal büyümemesinden gelir. Sistemin en sık çalışan bileşenleri (özetleme, kümeleme, tespit) yerel modellerle yürütüldüğü için birim maliyet düşüktür; yalnızca doğrulama ve asistan gibi daha seyrek çağrılan işlevler dış servis maliyeti taşır.

**Teknik sürdürülebilirlik**, istemci ile uygulama servisinin tiplenmiş bir API sözleşmesi (Pydantic şemaları) üzerinden ayrıştırılmasından gelir; bu, iki tarafın bağımsız olarak geliştirilip bakımının yapılabilmesini sağlar. Model bileşenleri de (özetleme, tespit, kümeleme) birbirinden bağımsız modüller olarak tasarlanmış olup, biri güncellenirken diğerlerinin durması gerekmez.

**Sosyal sürdürülebilirlik**, sistemin değişen kullanıcı ihtiyaçlarına uyum sağlama kapasitesinden gelir. Çekimserlik oranı ve tespit başarımı gibi metrikler düzenli olarak yeniden ölçülebilir; kullanıcı geri bildirimi (itiraz mekanizması, `/api/itiraz`) doğrudan sisteme kanal açar. KVKK kapsamındaki rıza tercihleri kullanıcı tarafından her an değiştirilebilir ve "unutulma hakkı" uç noktası (`/api/yonetisim/unut`) üzerinden veri silme talebi işletilebilir; bu, sistemin yalnızca bugünün değil, değişen mevzuat ve kullanıcı beklentilerinin de karşılanmasını hedefler.

*[Kontrol maddeleri — 6.1: gelir/iş modeli (2p) + katma değer potansiyeli (2p) + iş ortaklığı potansiyeli (1p). 6.2: finansal (2p) + teknik (2p) + değişen ihtiyaçlara uyum (1p)]*

## Bu bölümde atıf yapılan çalışma

[6] 6698 Sayılı Kişisel Verilerin Korunması Kanunu, T.C. Resmî Gazete, 07.04.2016,
Erişim: 22.08.2026, https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5
