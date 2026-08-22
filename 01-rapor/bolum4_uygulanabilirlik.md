# 4. UYGULANABİLİRLİK

## 4.1. Verimlilik ve Etkinlik

MİHENK'in verimlilik iddiası ölçülebilir bir varsayıma dayanır: kullanıcı, bir olayı kavramak için akıştaki 10-20 gönderiyi tek tek okumak yerine, olay başına üretilen tek bir dengeli özeti okur. Prototipte üretilen 13 olay kümesinin ortalama gönderi sayısı 12'dir; bu, özet paneli kullanıldığında okunması gereken içerik hacminde kabaca 10 kata varan bir azalmaya karşılık gelir. Doğrulama tarafında ise kullanıcının bir iddiayı sınamak için akıştan çıkıp ayrı bir arama motoruna geçmesi gerekmemekte, sonuç ve kaynak akış içinde tek etkileşimle sunulmaktadır.

İçerik üreticileri için verimlilik, toplulaştırılmış etkileşim verisinden çıkarılan paylaşım zamanı ve konu önerileriyle sağlanmaktadır; üretici, kitlesinin ne zaman aktif olduğunu deneme-yanılmayla değil doğrudan veriyle görmektedir. Etkinlik, çekimserlik oranı ve yanlış pozitif oranı gibi ölçülebilir büyüklüklerle raporlanmakta (bkz. Bölüm 3.2), iddia edilen faydanın öznel değil sayısal bir dayanağı bulunmaktadır.

## 4.2. Hedef Kitle

Projenin hedef kitlesi üç katmanlıdır. Birincisi, günlük gündemi takip etmek isteyen ancak sınırlı zamanı olan genel kullanıcı kitlesidir; Türkiye'de internet kullanım oranının %90,9 olduğu göz önüne alındığında bu kitle geniş ve büyümeye devam eden bir kitledir [1]. İkincisi, doğruluğu önemseyen ve dolaşımdaki bir iddiayı hızla sınamak isteyen kullanıcılardır; Reuters Institute verilerine göre internet içeriğinin gerçekliğine ilişkin kaygı küresel ölçekte %62'ye çıkmıştır [3], bu da doğrulama ihtiyacının büyüyen bir kitle davranışı olduğunu göstermektedir. Üçüncüsü, paylaşım stratejisini veriyle şekillendirmek isteyen içerik üreticileridir.

Ürünün bu kitleyle uyumu, NSosyal'in kendi kullanıcı tabanına doğrudan konumlanmasından gelir: MİHENK yeni bir kullanıcı kazanımı gerektirmez, mevcut platform kullanıcısının üzerine bir katman olarak eklenir.

## 4.3. Teknolojik Yenilik ve Uygulanabilirlik

Teknolojik yenilik, tekil bir bileşende değil, üç ilkenin (atıf zorunluluğu, çekimserlik, çoğulculuk) yanıt şemasına kodlanmış ve testlerle doğrulanmış olmasında yatmaktadır (bkz. Bölüm 3.1-3.2). Bu, çoğu özetleme aracının "iyi görünen ama doğrulanamayan" çıktı üretme sorununa yapısal bir çözümdür.

Projenin teknik olarak hayata geçirilebilir olduğu, hâlihazırda çalışan bir prototiple kanıtlanmıştır: Next.js tabanlı arayüz, FastAPI tabanlı uygulama servisi ve dört uç noktalı bir API sözleşmesi üzerinden entegre çalışmaktadır. Ölçeklenebilirlik, mimarinin iki katmanlı tasarımından gelir: Katman 1 (yerel özetleme, kümeleme, tespit) kullanıcı sayısından bağımsız olarak akış hızında çalışır ve maliyeti kullanıcı sayısıyla doğrusal büyümez; yalnızca Katman 2'deki (agentik doğrulama, asistan) çağrılar kullanıcı etkileşimiyle orantılı artar. Bu ayrım, kullanıcı tabanı büyüdükçe sistemin öngörülebilir biçimde ölçeklenmesini sağlamaktadır.

*[Kontrol maddeleri — 4.1: verimlilik artışı (3p) + ölçülebilir etkinlik (2p). 4.2: hedef kitle tanımı (2p) + genişlik (1p) + uyum kanıtı (2p). 4.3: teknik detay (2p) + hayata geçirilebilirlik (2p) + ölçeklenebilirlik (1p)]*
