# Moderatör Betiği — Kullanılabilirlik Testi

> Protokol `docs/KULLANILABILIRLIK_TESTI.md` içindedir; **bu belge onun
> uygulama yönergesidir.** Buradaki cümleler olduğu gibi okunur. Doğaçlama
> yapılmaz: her katılımcıya farklı sözlerle anlatılan bir görev, farklı bir
> görevdir ve süreleri karşılaştırılamaz hâle getirir.
>
> Süre: katılımcı başına **25-30 dakika**. Beş katılımcı ~2,5 saat.

---

## 0. Hazırlık — teste başlamadan önce (bir kez)

### Neden yerinde, neden yayında değil

Test **kendi bilgisayarınızda, katılımcı yanınızdayken** yapılır. Prototip
Vercel'e çıkarılırsa backend yerelde kaldığı için özet atıfsız yerel yedeğe
düşer ve ekranda "bu metin atıf içermez" uyarısı belirir. Görev C tam olarak
kaynak çipine tıklamayı ölçüyor — yayına almak, ölçmek istediğiniz şeyi
kapatmak olur.

### Kontrol listesi

```bash
# 1) Backend (ayrı terminal, açık kalsın)
.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --port 8000
```

```bash
# 2) Arayüz — ÜRETİM derlemesi (ayrı terminal, açık kalsın)
cd 02-prototip && npx next build && npx next start -p 3000
```

Teste başlamadan **mutlaka** doğrulayın:

- [ ] `http://localhost:3000` açılıyor
- [ ] Özet panelinde cümlelerin yanında **küçük sayı rozetleri** görünüyor
- [ ] Rozete tıklayınca kaynak gönderi kimlikleri açılıyor
- [ ] Panelde "MİHENK servisine erişilemedi" uyarısı **YOK**

Son madde kritik: o uyarı görünüyorsa backend'e ulaşılamıyor demektir ve test
geçersizdir. Uyarı çıkarsa backend terminalini kontrol edin, testi başlatmayın.

- [ ] Kronometre hazır (telefon yeterli)
- [ ] Kayıt formu açık (`docs/kullanilabilirlik/veri-girisi.json` kopyası)
- [ ] Tarayıcı geçmişi/önbelleği her katılımcı arasında temizleniyor
      (gizli sekme en kolayı — rıza bandı yeniden çıkar, bu normaldir)

### Sıra dengeleme — atlanmaması gereken

| Katılımcı | Önce | Sonra |
|---|---|---|
| K1 | **A** Gündem elle | **B** Spor özetle |
| K2 | **B** Gündem özetle | **A** Spor elle |
| K3 | **A** Spor elle | **B** Gündem özetle |
| K4 | **B** Spor özetle | **A** Gündem elle |
| K5 | **A** Gündem elle | **B** Spor özetle |

İki koşul aynı sırada yapılırsa ikincisi, birincisinden öğrenilen bilgiyle
kolaylaşır ve **zaman kazancı olduğundan büyük ölçülür.** Kategoriler de
değişir ki içerik ezberi sonucu bozmasın.

---

## 1. Karşılama (2 dk) — kelimesi kelimesine okuyun

> "Merhaba, katıldığınız için teşekkürler. Bugün bir sosyal medya okuma
> aracının prototipini deneyeceğiz.
>
> **Önemli:** Burada test edilen siz değilsiniz, sistem. Zorlandığınız her
> yer bizim için bir bulgu — yanlış yapmanız mümkün değil.
>
> Sesli düşünmenizi rica ediyorum: aklınızdan geçeni söyleyin. 'Bunun ne
> olduğunu anlamadım' demeniz bize en çok yarayan şey.
>
> Sizden hiçbir kişisel bilgi almıyoruz, ekran veya ses kaydı yapmıyoruz.
> Yalnızca süreler ve yanıtlarınız not edilecek. İstediğiniz an bırakabilirsiniz.
> Devam edelim mi?"

Sözlü onay alın. **Onay olmadan başlamayın.** (Bu, `docs/ETIK.md` ve
`docs/VERI_YONETISIMI.md` ile tutarlıdır: rıza gerektiren her şey kapalı başlar.)

Ardından tek soru sorun ve profili not edin:

> "Sosyal medyada günde ortalama ne kadar vakit geçiriyorsunuz?"

---

## 2. Görev A — Elle okuma

Uygulamayı ilgili kategoride açın, **özet panelini kapatın** (sağ üstteki ×).

> "Bu kategorideki okunmamış gönderileri okuyun. Bitirdiğinizde bana haber
> verin. Ardından ne olup bittiğini soracağım."

Katılımcı "başladım" der demez kronometreyi başlatın. **Süreyi saniye
cinsinden not edin.**

Katılımcı size soru sorarsa: *"Siz nasıl yapardınız, öyle yapın."*

### Kavrama soruları — Görev A'dan hemen sonra

Kategoriye göre **§5'teki cevap anahtarını** kullanın. Yanıtları yazın,
**puanlamayı şimdi yapmayın** (§6'ya bakınız).

---

## 3. Görev B — Özetle okuma

Diğer kategoriye geçin, özet panelini açın.

> "Bu sefer 'MİHENK Özeti' panelini kullanın. Özeti okuyun, bitirdiğinizde
> haber verin."

Kronometre. **Ayrıca sayın:** katılımcı kaynak rozetlerine kaç kez tıkladı?
(Söylemeyin, sadece sayın. Bu, "atıf gerçekten kullanılıyor mu" sorusunun
cevabıdır.)

Ardından aynı biçimde kavrama soruları.

---

## 4. Görev C — Kaynak doğrulama

Katılımcı **Gündem** sekmesindeyken, ekrandaki ilk cümleyi göstererek:

> "Şu cümleyi görüyor musunuz: *'Büyükşehirde yeni toplu ulaşım hattı açıldı
> konusunda temkinliyim.'* Bu cümlenin dayandığı gönderilerden birini bulup
> açın."

**Spor** sekmesindeyseniz aynı görev için:

> "Şu cümleyi görüyor musunuz: *'Stat yenileme projesi ertelendi.'* Bu
> cümlenin dayandığı gönderilerden birini bulup açın."

Ölçün: **başarılı mı (evet/hayır)** ve **süre**.

Doğru davranış: cümlenin yanındaki rozete tıklamak → açılan kimliklerden
birine tıklamak → gönderi sayfasının açılması.

| Kategori | Beklenen kaynak kimlikleri |
|---|---|
| Gündem, 1. cümle | `9c95c88cc17a`, `c78aa94d1190`, `5762b962b02c` |
| Spor, 1. cümle | `2d343e6cede6`, `2aec2bf0790d`, `de0b97ef22c2` |

45 saniye geçtiyse durdurun, "başarısız" yazın ve devam edin. Katılımcıyı
yönlendirmeyin — yönlendirilen bir görev artık ölçüm değildir.

---

## 5. Görev D — Çekimserlik yorumu

**Bu, testin en önemli görevidir.** Ürünün en ayırt edici davranışı burada
sınanıyor: sistem emin olmadığında susuyor. Kullanıcı bunu *dürüstlük* olarak
mı, *bozukluk* olarak mı okuyor?

### D1 — Önce rozetin nasıl göründüğünü gösterin

Adres çubuğuna yazın: `localhost:3000/gonderi/ebfc698985c6`

> "Bu gönderiye bakın. Sistem burada bir şey söylüyor mu?"

(Bu gönderide **yapay üretim rozeti görünür.** Katılımcı rozeti fark etmezse
gösterin — bu bir öğretme adımıdır, ölçüm değil.)

> "Peki bu size ne anlatıyor?"

Yanıtı yazın.

### D2 — Sonra sistemin sustuğu gönderiyi gösterin

Adres çubuğuna yazın: `localhost:3000/gonderi/72a9bd9eee30`

> "Şimdi bu gönderiye bakın. Sistem burada ne söylüyor?"

Yanıtı yazın. Sonra:

> "Sizce neden?"

Yanıtı **kelimesi kelimesine** yazın. Aranan ayrım şudur:

| Katılımcının okuması | Kayıt |
|---|---|
| "Sistem emin değil / karar vermiyor" | `durust` |
| "Bu gönderi temiz / insan yazmış" | `yanlis_guven` ⚠️ |
| "Sistem bozuk / çalışmıyor / eksik" | `bozuk` ⚠️ |
| Anlamadı | `belirsiz` |

İkinci satır en tehlikelisidir: sessizliği "temiz" diye okumak, tam olarak
kaçınmak için "insan yazmış" rozetini kaldırdığımız yanlış güvendir. Çıkarsa
bu bir **tasarım bulgusudur** ve rapora yazılır.

**Katılımcıya doğru cevabı söylemeyin.** Test bittikten sonra anlatabilirsiniz.

---

## 6. Görev E — Asistan reddi

Herhangi bir gönderi sayfasında asistan panelini açın.

> "Asistana, bu gönderide cevabı olmayan bir şey sorun. Örneğin gönderiyle
> hiç ilgisi olmayan bir konu."

Katılımcı takılırsa örnek verin: *"Yarın hava nasıl olacak?"*

Sistem reddedecektir.

> "Ne oldu? Bu size nasıl geldi?"

Yanıtı yazın. Aranan: reddetme **güven mi veriyor**, **yetersizlik mi**
hissettiriyor?

---

## 7. SUS + ek maddeler (5 dk)

`docs/KULLANILABILIRLIK_TESTI.md` §5'teki 10 SUS maddesini ve 3 ek maddeyi
sırayla okuyun; katılımcı 1-5 arası puan versin.

> "Şimdi 13 cümle okuyacağım. Her biri için 1'den 5'e puan verin.
> 1 = kesinlikle katılmıyorum, 5 = kesinlikle katılıyorum. Uzun düşünmeyin,
> ilk hissiniz yeterli."

**Maddeleri yorumlamayın.** "Yani şunu mu soruyorsunuz" derse:
*"Siz nasıl anladıysanız öyle cevaplayın."*

---

## 8. Kapanış

> "Bitti, çok teşekkürler. Eklemek istediğiniz bir şey var mı?"

Serbest yorumları **nitel bulgular** olarak yazın. En değerli veri genellikle
burada çıkar.

---

## 9. Kavrama soruları — cevap anahtarı

> **Puanlamayı testi yürüten kişi YAPMAZ.** İkinci bir ekip üyesi puanlar;
> yürütücü kendi tasarımını kayırma eğilimindedir (protokol §4).
>
> Her soru **0 / 0,5 / 1**. Kavrama = toplam ÷ 4.

### Gündem (30 gönderi, 3 olay)

| # | Soru | Doğru cevap | 0,5 verilir |
|---|---|---|---|
| 1 | Kaç farklı konu konuşuluyordu? | **3** | 2 veya 4 |
| 2 | En çok tartışılan konu neydi? | **Büyükşehirde yeni toplu ulaşım hattı** (12 gönderi) | Konuyu adlandırdı ama en çok tartışılanı seçemedi |
| 3 | Su kısıtlaması hakkında farklı görüşler var mıydı? | **Evet — 5 farklı çerçeve**: nötr, destekleyici, eleştirel, soru soran, doğrulanmamış | "Evet" dedi ama iki taraftan fazlasını söyleyemedi |
| 4 | Şu bilgiyi hangi gönderiden öğrendiniz? | Kaynağı **gösterebildi** | Kategoriyi söyledi, gönderiyi bulamadı |

### Spor (34 gönderi, 3 olay)

| # | Soru | Doğru cevap | 0,5 verilir |
|---|---|---|---|
| 1 | Kaç farklı konu konuşuluyordu? | **3** | 2 veya 4 |
| 2 | En çok tartışılan konu neydi? | **Stat yenileme projesi ertelendi** (13 gönderi) | Konuyu adlandırdı ama en çok tartışılanı seçemedi |
| 3 | Şampiyonluk yarışı hakkında farklı görüşler var mıydı? | **Evet — 5 farklı çerçeve** | "Evet" dedi ama iki taraftan fazlasını söyleyemedi |
| 4 | Şu bilgiyi hangi gönderiden öğrendiniz? | Kaynağı **gösterebildi** | Kategoriyi söyledi, gönderiyi bulamadı |

**3. sorunun ayrı bir anlamı var.** Çoğulculuk (İlke 3) iddiasını sınar:
özetle okuyan kullanıcı, elle okuyandan daha az mı yoksa daha çok mu farklı
görüş fark ediyor? Özet, çok sesliliği koruyorsa bu sayı düşmemelidir.

---

## 10. Sonuçları işleme

Her katılımcıdan sonra kaydı `veri-girisi.json` içine yazın. Beşi bittiğinde:

```bash
cd 02-prototip && node scripts/kullanilabilirlik-hesapla.mjs
```

Betik SUS puanını, kavrama ortalamalarını ve zaman kazancını hesaplar; sonucu
`docs/KULLANILABILIRLIK_TESTI.md` §6'ya **yazar**. Elle hesap yapmayın: SUS
formülü (tek maddeler `puan−1`, çift maddeler `5−puan`, toplam ×2,5) elle
yapıldığında en sık hata kaynağıdır.

**Eksik katılımcı varsa boş bırakın.** Betik eksik kaydı `[  ]` olarak
işaretler ve ortalamaya katmaz; 5 kişi tamamlanamadıysa rapor kaç kişiyle
yapıldığını yazar. Üç kişiyle yapılmış bir testi beş kişiymiş gibi sunmak,
bu raporun bütün ölçüm iddiasını götürür.
