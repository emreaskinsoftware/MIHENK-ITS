# ITS MİHENK — Şartname ve Rapor Uyum Denetimi
**Tarih:** 19 Ağustos 2026 · Denetlenen: Şartname v3 (17.08.2026), Proje Teknik Rapor Şablonu, Takım Tanıtım Dosyası

---

## A. UYUMLU OLDUĞUMUZ NOKTALAR ✅

| Koşul | Durum |
|---|---|
| Öğrencilik şartı (lisans) | ✅ Ümit 2. sınıf, Emre 4. sınıf — ikisi de uygun |
| Takım büyüklüğü 2-5 kişi | ✅ 2 kişi (asgari karşılanıyor) |
| Danışman en fazla 1, üye değil | ✅ Doç. Dr. M. Baykara, üye olarak eklenmemiş |
| Takım kaptanı zorunlu | ✅ Ümit Can Çınar |
| Projenin özgün olması | ✅ |
| Tek başvuru | ✅ |
| Çalışan prototiple desteklenmesi | ✅ planlandı (Faz 1) |
| Tema uygunluğu | ✅ "İçerik özetleme teknolojileri", "YZ destekli dijital asistanlar", "spam ve bot tespiti", "duygu analizi" — hepsi şartnamenin Sosyal YZ örnek çözüm alanları listesinde |
| Yerli bileşen | ✅ 3 bileşen (özetleme modeli, görsel tespit modeli, etiketli veri kümesi) |
| Kaynak kod + commit geçmişi | ✅ planlandı |

---

## B. BOŞLUKLAR — CİDDİ 🔴

### 1. Rubrik 3.2'nin 6 puanı tek bir işe bağlı
Şablon notu: *"Projede yapay zeka/veri bileşeni yoksa bu alt kriter değerlendirme
dışı bırakılır..."* — Bizde AI **var**, dolayısıyla 3.2 tam değerlendirilecek ve
veri ön işleme (2p) + model eğitimi (2p) + overfitting önlemi (1p) + performans
metriği (1p) istenecek. Bunların tamamı Emre'nin model eğitimine bağlı.

**Risk:** Eğitim yetişmezse 6 puanın büyük kısmı gider ve bu, şartname
ağırlığında %35 olan "Teknik Yeterlilik" ekseninin de en somut kanıtı.
**Önlem:** Özetleme modeli yetişmese bile, etiketli veri kümesi üzerinde
**kümeleme** ve **görsel tespit** metrikleri çıkarılabilir. En az bir modülün
sayısal sonucu 22 Ağustos akşamına kadar elde olmalı.

### 2. "Etik" dokümanı — hiç ele alınmadı
Şartname beklenen teslimatlar arasında **"Veri, model, etik ve performans
dokümanı"** diyor. Bizde KVKK var ama **etik yok.** Doğruluk hükmü veren bir
sistem için bu ciddi bir eksik. Kapsanması gerekenler:
- Model halüsinasyonu ve yanlış doğrulama riski
- "Doğrulanamadı" ile "yanlış" ayrımı — sistem ne zaman hüküm vermemeli
- Özet tarafsızlığı (bu eksen artık var, etik çerçeveye bağlanmalı)
- Kullanıcının nihai karar verici olması ilkesi
**Sahip:** Emre (KVKK ile aynı bölümde)

### 3. İş/gelir modeli hâlâ yok
Rubrik 6.1: *"Gelir/iş modeli net biçimde tanımlanmış"* (2p) + katma değer (2p)
+ iş ortaklığı potansiyeli (1p) = **5 puan**. Şu an sıfır içerik var.
Not: Şartname ağırlığında Sosyal YZ teması için bu %0, **ama rapor rubriğinde
5 puan** — yazılmak zorunda.

---

## C. BOŞLUKLAR — ORTA 🟡

### 4. Şartnamenin istediği 4 teslimat henüz üretilmedi
- Kullanıcı senaryoları
- Kullanıcı araştırması özeti
- Kullanılabilirlik testi sonuçları *(protokol planlandı)*
- Erişilebilirlik değerlendirmesi *(planlandı)*

Bunların ilk ikisi hızlı üretilir ve 3.3'ü besler.

### 5. Takım 2 kişi — disiplin genişliği zayıf
Rubrik 8.1: *"Farklı disiplinlerden üyelerin projeye katkısı belirtilmiş"* (2p).
Şartname yazılım, YZ, veri bilimi, siber güvenlik, ürün yönetimi, UI/UX, tasarım,
girişimcilik sayıyor — biz 2 kişiyle bunların hepsini iddia edemeyiz.
**Önlem:** 3. kişi (UI/UX veya veri) — üye ekleme 2 Eylül'e kadar açık, ama
rapora yazılacak kadro 24 Ağustos'taki kadro.

### 6. Repo linki ↔ anonimlik gerilimi
Aynı rubrik hem repo linki istiyor (3.1, 1p) hem de *"takım üyelerinin isim ve
fotoğraf gibi kişisel bilgilerine yer verilmemelidir"* diyor. Repo açılınca
commit'lerde isimler görünür.
**Değerlendirme:** Repo linki aynı rubrik tarafından zorunlu tutulduğu için
bu bir ihlal sayılmaz. Yine de düşük maliyetli önlem: repoyu kişisel hesap
yerine **tarafsız isimli bir organizasyon** altında açmak (örn. `its-mihenk`).

### 7. Takım tanıtım dosyası ile rapor tutarsızlığı
- Takım adı dosyada üç farklı biçimde geçiyor: "ITS - AI", "Innovative
  Technological Solutions", "ITS". **KYS'deki kayıtlı ad neyse rapor kapağında
  o kullanılmalı.**
- Dosyada Ümit'in rolü "UI / Frontend Geliştirme" olarak yazılı; oysa planda
  backend + simülasyon + ürün + raporun 65 puanı da onda. Rapordaki rol tablosu
  ile tanıtım dosyası çelişmemeli.
- Dosyadaki "otonom sistemler, robotik, IoT" hedefleri bu yazılım yarışması
  için konu dışı — tanıtım dosyası ayrıca teslim edilecekse sadeleştirilmeli.

---

## D. İDARİ — SÜRE KRİTİK ⏰

| # | Madde | Son tarih |
|---|---|---|
| 8 | KYS başvurusunun tamamlanması | **20 Ağustos (yarın)** |
| 9 | Google Groups üyeliği (şartname: zorunlu) | En kısa sürede |

Ayrıca beyan yükümlülüğü: şartname, *"Daha önce farklı bir yarışmaya katılmış
projeler... teknik raporda belirtmekle yükümlüdür"* diyor. MİHENK veya
bileşenleri daha önce bir yarışmaya sunulduysa **rapora yazılmalı**
(format: Yıl, Yarışma adı, Kategori, Takım adı).

---

## E. GÖZDEN KAÇMAMASI GEREKEN FORMAT KURALLARI

- Kapak + içindekiler + kaynakça + ekler dahil **en fazla 30 sayfa**
- Kapak, İçindekiler, Kaynakça için **3 ayrı sayfa**
- İçindekiler **sayfa numaralı** olacak
- Arial 12pt gövde / Arial Black 14pt başlık / 1.15 satır aralığı / iki yana
  yaslı / 2.5 cm kenar boşluğu
- *"Cümleler birbirinin tekrarı niteliğinde olmamalıdır"* — sayfa doldurmak için
  tekrara düşmek açıkça uyarılmış
- Puanlama sayfası **rapordan silinecek**
- Bu aşamada **video istenmiyor**
- Metin içi atıf köşeli parantez: [1], [4,7], [5-11]

---

## F. ÖNCELİK SIRASI

1. KYS + Google Groups *(yarın son)*
2. En az bir modülün sayısal metriği *(3.2'nin 6 puanı)*
3. İş/gelir modeli metni *(5 puan, sıfırdan)*
4. Etik bölümü *(şartname teslimatı)*
5. Kullanıcı senaryoları + araştırma özeti *(hızlı, 3.3'ü besler)*
6. 3. takım üyesi kararı
7. Tanıtım dosyası ↔ rapor tutarlılığı
