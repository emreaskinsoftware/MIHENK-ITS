# 6. İŞ MODELİ — TASLAK

> **Bu bir taslaktır ve stratejik kararlar takımındır.** Aşağıda varsayım
> olan her yer `[VARSAYIM]` ile işaretlenmiştir; bunlar doğrulanmadan rapora
> girmemelidir. Ölçülmüş sayılar ise kaynağıyla verilmiştir.
>
> Bu belgede **pazar büyüklüğü tahmini yoktur.** Kaynağını gösteremeyeceğimiz
> bir "X milyar dolarlık pazar" cümlesi, raporun geri kalanındaki ölçüm
> titizliğini de şüpheli hâle getirir. Rakam gerekiyorsa kaynağı bulunup
> eklenmelidir; bulunamıyorsa yazılmamalıdır.

---

## 6.1. Değer önerisi — kime, ne satıyoruz

MİHENK bağımsız bir sosyal medya uygulaması değildir. **NSosyal üzerine
eklenen bir okuma katmanıdır** ve akış sırasına dokunmaz. Bu, iş modelinin
de belirleyicisidir: rakip bir platform kurmuyoruz, var olan bir platformun
kullanım süresini ve güvenilirliğini artıran bir bileşen sunuyoruz.

| Taraf | Aldığı değer |
|---|---|
| **Kullanıcı** | Biriken akışı, kaynağını kaybetmeden okuyabilme |
| **Platform (NSosyal)** | Yanlış bilgi yükünü sansüre başvurmadan azaltma; kullanıcıyı platformda tutan bir okuma aracı |
| **İçerik üreticisi** | Özetin kaynağa yönlendirmesi — özet, gönderinin yerine geçmez |

Üçüncü satır bir yan etki değil, **tasarım kısıtıdır**. Özetleyici, kelime
üst sınırını aşan cümleyi kırpmaz, tamamen çıkarır; hedeflenen davranış
kullanıcının kaynağa tıklamasıdır (`backend/app/summarize/service.py`).
Üreticiyi ikame eden bir özet katmanı, platformun içerik ekosistemini
kurutur — bu, uzun vadede platformun da aleyhinedir.

---

## 6.2. Gelir modeli

### Birincil model: B2B lisanslama (platform entegrasyonu)

Müşteri NSosyal'dir; ürün, platforma entegre edilen bir okuma katmanı olarak
lisanslanır. Bunun tercih edilme sebebi teknik: **maliyet yapımız kullanıcı
başına değil, gönderi başına ölçekleniyor.**

**Ölçülmüş dayanak** (`eval/results/summarization.md`):

| Ölçüm | Değer |
|---|---|
| 420 gönderi için yapılan atomik özet çağrısı | 227 (193'ü kısa gönderi kuralıyla atlandı) |
| Zenginleştirmede LLM çağrısı tasarrufu | **%46,0** |
| Önbellek isabet oranı | 0,750 |
| Kullanıcı başına tekrarlanan pahalı işlem | özet başına **1** çağrı |
| Özet gecikmesi (p50 / p95) | 962 ms / 1.101 ms |

Mimarinin can alıcı noktası: bir gönderinin atomik özeti ve gömmesi
**kullanıcıdan bağımsız** üretilir ve kullanıcılar arasında paylaşılır. Aynı
gönderiyi 1.000 kişi görse de zenginleştirme bir kez yapılır. Maliyet bu
nedenle kullanıcı sayısıyla **doğrusal büyümez**; gönderi hacmiyle büyür.

Bu, kullanıcı başına ücretlendirmeyi (B2C abonelik) verimsiz kılar: kullanıcı
eklemenin marjinal maliyeti düşükken kullanıcı başına fiyatlamak, ürünü
yayılmaktan alıkoyar. Doğru eşleşme **hacim tabanlı platform lisansıdır**.

`[VARSAYIM]` Fiyatlandırma birimi: aylık işlenen gönderi hacmi kademeleri.
Kademe eşikleri ve birim fiyat belirlenmemiştir; gerçek altyapı maliyeti
(GPU/API) ölçülmeden belirlenmemelidir. Prototipte dış model çağrısı
yapılmadığı için **birim maliyetimiz henüz ölçülmemiştir** — bu, bu bölümün
en büyük boşluğudur ve öyle yazılmalıdır.

### İkincil model: kurumsal okuma katmanı

Aynı teknoloji, kamu kurumları ve haber kuruluşları için "kendi alanındaki
gündemi kaynağa bağlı özetleme" aracına dönüşür. Ayırt edici özellik yine
aynıdır: **kaynak gösteremediğinde susan** bir sistem, kurumsal kullanımda
zorunluluktur.

`[VARSAYIM]` Bu segmentin varlığı doğrulanmadı; görüşme yapılmadı.

### Bilinçli olarak DIŞARIDA bırakılanlar

| Model | Neden dışarıda |
|---|---|
| Reklam geliri | Gelir, kullanıcının akışta geçirdiği süreye bağlanırsa ürün **özetlememeye** teşvik edilir. Amaçla çelişir. |
| Kullanıcı verisi satışı | `docs/VERI_YONETISIMI.md` — kişisel veri işlenmiyor; model buna dayanamaz. |
| "Doğruluk damgası" satışı | Hesaplara doğruluk rozeti satmak, sistemi hüküm veren konuma sokar (`docs/ETIK.md` §2). |

Üçünün de reddedilmesi bir kısıt değil, konumlandırmadır: ürünün tek
savunulabilir farkı **güvenilirliğidir**; güvenilirliği bozan bir gelir
kalemi ürünü değersizleştirir.

---

## 6.3. Katma değer

**a) Sansüre başvurmadan yanlış bilgi yükünü azaltma.** Şüpheli gönderi
akıştan çıkarılmaz; işaretlenir ve özetlenir, ama talimatına uyulmaz. Bir
platform için içerik kaldırmanın siyasi ve hukuki maliyeti yüksektir;
"kaynağı göster ve emin değilsen sus" yaklaşımı bu maliyeti doğurmaz.

**b) Yerli ve Türkçeye özgü.** Tespit modeli BERTurk üzerine ince ayarlıdır;
gömme modeli çok dilli, kümeleme eşiği Türkçe akış üzerinde kalibre
edilmiştir. Türkçe sondan eklemeli yapı, konu etiketleme sözlüğünde de
doğrudan hesaba katılmıştır.

**c) Ölçülmüş dürüstlük.** Rapor 3.2, sentetik ölçümün başarımı ne kadar
şişirdiğini sayıyla gösteriyor (AUROC 1,000 → 0,768). Bu bir zayıflık
beyanı gibi görünse de ticari olarak tersidir: bir platform, başarımını
abartan bir tedarikçiyle entegrasyona giremez.

---

## 6.4. İş ortaklığı potansiyeli

| Ortak türü | Ortaklığın konusu | Durum |
|---|---|---|
| **NSosyal** | Platform entegrasyonu, gerçek akış üzerinde ölçüm | Birincil hedef; `[VARSAYIM]` görüşme yapılmadı |
| **Üniversite / NLP grubu** | Türkçe tespit modelinin yanlılık ölçümü | Danışman kanalı mevcut |
| **Doğrulama kuruluşları** | Doğrulama katmanının kaynak havuzu | `[VARSAYIM]` temas kurulmadı |
| **Kamu kurumları** | Kurumsal okuma katmanı pilotu | `[VARSAYIM]` |

**Gerçek akışa erişim, ortaklığın ön koşulu değil, ürünün ön koşuludur.**
Prototip, veri kazımayı ilke olarak reddediyor (`docs/VERI_YONETISIMI.md`);
gerçek dağılımda ölçüm ancak platformla kurulacak resmî bir kanaldan
mümkündür. Bu, iş geliştirmenin ilk maddesidir.

---

## 6.5. Bu bölümün eksikleri

Raporun geri kalanı ölçülmemiş sayı yazmama kuralına uyuyor; bu bölümün de
uyması için aşağıdakiler açıkça belirtilmelidir:

1. **Birim maliyet ölçülmedi.** Prototip dış model çağrısı yapmadan çalışıyor;
   gerçek API/GPU maliyeti bilinmiyor. Fiyat kademesi bu ölçüm olmadan
   yazılamaz.
2. **Pazar büyüklüğü tahmini yok.** Kaynaksız bir rakam yazılmadı.
3. **Müşteri görüşmesi yapılmadı.** Platform tarafının bu katmanı isteyip
   istemediği doğrulanmadı.
4. **Fiyat kabulü test edilmedi.**

Bu dört madde, ürünleşme yol haritasının ilk çeyreğinin işidir.
