# Kullanılabilirlik Testi — Protokol ve Formlar

> Raporun **Tablo 10**'unun kaynağıdır. Bu test elle yapılır; `evaluate.py`
> üretmez (spec 7). Sonuçlar bu belgenin 6. bölümüne yazılır.
>
> **Sonuç bölümü şu an boştur ve `[  ]` içerir. Test yapılmadan doldurulmaz.**

## 1. Amaç

Ölçülecek üç şey:

1. **Zaman kazancı.** Okunmamış akışı elle okumak ile özetle okumak arasında
   görev süresi farkı var mı?
2. **Kavrama doğruluğu.** Özetle okuyan kullanıcı, akışın içeriğini doğru
   anlıyor mu? (Hız, doğruluk pahasına gelmemeli.)
3. **Güven ve anlaşılırlık.** Kaynak çipleri ve çekimserlik davranışı
   kullanıcıya ne anlatıyor?

Üçüncüsü bu proje için en kritiğidir: sistem bilinçli olarak bazen susuyor.
Kullanıcı bunu "bozuk" mu yoksa "dürüst" mü okuyor?

## 2. Katılımcılar

**5 katılımcı.** (Nielsen'in kullanılabilirlik sorunlarının çoğunun 5
katılımcıda ortaya çıktığı bulgusuna dayanır; bu bir istatistiksel örneklem
değil, keşifsel testtir ve raporda öyle sunulur.)

Profil dağılımı:

| # | Profil | Not |
|---|---|---|
| K1 | Yoğun sosyal medya kullanıcısı (günde 1+ saat) | |
| K2 | Orta düzey kullanıcı | |
| K3 | Az kullanan / seçici okuyucu | |
| K4 | Haber okuma alışkanlığı yüksek | |
| K5 | Teknik olmayan kullanıcı | Jargon anlaşılırlığı için |

Ekip üyeleri katılımcı olamaz.

## 3. Görevler

Her katılımcı iki koşulu da yapar. **Sıra dengelenir** (yarısı A-B, yarısı B-A):
aynı sırada yapılırsa ikinci koşul, birinciden öğrenilen bilgiyle kolaylaşır ve
zaman kazancı olduğundan büyük ölçülür.

Farklı kategoriler kullanılır (biri gündem, diğeri spor) ki içerik ezberi
sonucu bozmasın.

### Görev A — Elle okuma
> "Bu kategorideki okunmamış gönderileri okuyun. Bittiğinde haber verin.
> Ardından size ne olup bittiğini soracağım."

Ölçülen: süre (saniye).

### Görev B — Özetle okuma
> "Özetle düğmesine basın ve özeti okuyun. Bittiğinde haber verin."

Ölçülen: süre (saniye), kaynak çipine tıklama sayısı.

### Görev C — Kaynak doğrulama
> "Özetteki şu cümlenin dayandığı gönderiyi bulun."

Ölçülen: başarı (evet/hayır), süre.

### Görev D — Çekimserlik yorumu
Katılımcıya YZ sinyali **gösterilmeyen** bir gönderi gösterilir.
> "Bu gönderi hakkında sistem ne söylüyor? Sizce neden?"

Ölçülen: açık uçlu yanıt. Aranan: kullanıcı boşluğu "sistem emin değil" diye mi,
"sistem bozuk/eksik" diye mi okuyor?

### Görev E — Asistan reddi
Katılımcıdan bağlam dışı bir soru sorması istenir.
> "Asistana, gönderide cevabı olmayan bir şey sorun."

Ölçülen: reddetme yanıtına tepki (açık uçlu).

## 4. Kavrama soruları

Her koşuldan sonra 4 soru (kategoriye göre önceden hazırlanır):

1. Bu kategoride kaç farklı konu konuşuluyordu? (sayı)
2. En çok tartışılan konu neydi? (açık uçlu)
3. Şu olay hakkında **farklı görüşler** var mıydı, varsa neler? (çoğulculuk kontrolü)
4. Şu bilgiyi hangi gönderiden öğrendiniz? (atıf kontrolü)

**Puanlama:** her soru 0 / 0.5 / 1. Kavrama doğruluğu = toplam / 4.

Puanlamayı testi yürüten kişi **değil**, ikinci bir ekip üyesi yapar (yürütücü
kendi tasarımını kayırma eğilimindedir).

## 5. SUS (System Usability Scale)

10 madde, 1-5 arası (1 = kesinlikle katılmıyorum, 5 = kesinlikle katılıyorum).

| # | Madde |
|---|---|
| 1 | Bu sistemi sık kullanmak isterim. |
| 2 | Sistemi gereksiz yere karmaşık buldum. |
| 3 | Sistemin kullanımı kolaydı. |
| 4 | Bu sistemi kullanabilmek için teknik destek gerekirdi. |
| 5 | Sistemdeki işlevler iyi bütünleşmişti. |
| 6 | Sistemde çok fazla tutarsızlık vardı. |
| 7 | Çoğu insanın bu sistemi hızla öğrenebileceğini düşünüyorum. |
| 8 | Sistemi kullanmak zahmetliydi. |
| 9 | Sistemi kullanırken kendime güvendim. |
| 10 | Bu sistemi kullanmaya başlamadan önce çok şey öğrenmem gerekti. |

**SUS puanı hesabı:** Tek numaralı maddeler için (puan − 1), çift numaralı
maddeler için (5 − puan). Toplam × 2.5 → 0-100 arası puan.

### Ek maddeler (SUS'a dahil edilmez, ayrı raporlanır)

Bu maddeler ürünün tezine özgüdür ve standart SUS puanını bozmamak için ayrı
tutulur:

| # | Madde |
|---|---|
| E1 | Özetteki bilgilerin nereden geldiğini anlayabildim. |
| E2 | Sistemin bazı durumlarda bilgi göstermemesi bana güven verdi. |
| E3 | Kaynak çiplerine tıklamak kolaydı ve işe yaradı. |

## 6. Sonuçlar

> Bu bölüm `02-prototip/scripts/kullanilabilirlik-hesapla.mjs` tarafından
> `docs/kullanilabilirlik/veri-girisi.json` üzerinden üretilir. Elle
> düzenlenmez. Doldurulmamış her hücre `[  ]` kalır ve ortalamaya katılmaz.

**Tamamlanan katılımcı: 0/5** — eksik katılımcı var; aşağıdaki ortalamalar yalnızca tamamlananlar üzerindendir.

### Tablo 10 — Görev süresi ve kavrama

| Katılımcı | Elle okuma (sn) | Özetle okuma (sn) | Kazanç | Kavrama (elle) | Kavrama (özet) | SUS |
|---|---|---|---|---|---|---|
| K1 | [  ] | [  ] | [  ] | [  ] | [  ] | [  ] |
| K2 | [  ] | [  ] | [  ] | [  ] | [  ] | [  ] |
| K3 | [  ] | [  ] | [  ] | [  ] | [  ] | [  ] |
| K4 | [  ] | [  ] | [  ] | [  ] | [  ] | [  ] |
| K5 | [  ] | [  ] | [  ] | [  ] | [  ] | [  ] |
| **Ortalama** | **[  ]** | **[  ]** | **[  ]** | **[  ]** | **[  ]** | **[  ]** |

**Kavrama sütunları birlikte okunmalıdır.** Hız, doğruluk pahasına gelmemeli:
özetle okuyan kullanıcının kavrama puanı elle okuyandan belirgin düşükse
zaman kazancı bir başarı değil, bilgi kaybıdır.

### Ek maddeler

| Madde | Ortalama (1-5) |
|---|---|
| E1 — Özetteki bilgilerin nereden geldiğini anlayabildim | [  ] |
| E2 — Sistemin bazı durumlarda bilgi göstermemesi bana güven verdi | [  ] |
| E3 — Kaynak çiplerine tıklamak kolaydı ve işe yaradı | [  ] |

E2, ürünün en ayırt edici davranışına (İlke 2 — çekimserlik) dair tek doğrudan
ölçüdür.

### Görev C — Kaynak doğrulama

| Ölçüm | Değer |
|---|---|
| Başarı | [  ] |
| Ortalama süre (sn) | [  ] |
| Görev B'de kaynak rozetine tıklama (ortalama) | [  ] |

Son satır, atıfın **kullanılıp kullanılmadığını** gösterir. Sıfıra yakınsa
atıf bir güven aracı değil görsel gürültüdür ve rapor bunu yazmalıdır.

### Görev D — Çekimserlik nasıl okundu

| Katılımcının okuması | Kişi |
|---|---|
| "Sistem emin değil / karar vermiyor" | [  ] |
| "Bu gönderi temiz / insan yazmış" ⚠️ | [  ] |
| "Sistem bozuk / eksik" ⚠️ | [  ] |
| Anlamadı | [  ] |

### Nitel bulgular

[  ] — test yapıldığında doldurulur.

### Yapılacak düzeltmeler

[  ] — test yapıldığında doldurulur.

## 7. Etik ve veri

- Katılımcılardan **kişisel veri toplanmaz**; kayıtlar `K1`-`K5` kodlarıyla tutulur.
- Ekran veya ses kaydı **alınmaz**; yürütücü not tutar.
- Katılım gönüllüdür, istenildiği an bırakılabilir.
- Toplanan tek veri: süre, kavrama puanı, SUS yanıtları, açık uçlu notlar.
- Notlar rapor teslim edildikten sonra silinir.
