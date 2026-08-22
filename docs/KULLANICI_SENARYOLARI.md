# Kullanıcı Senaryoları ve Araştırma Özeti

> Raporun 3.3 bölümünü besler. Şartnamenin beklediği "kullanıcı senaryoları" ve
> "kullanıcı araştırması özeti" teslimatlarına karşılık gelir.
>
> **Dürüstlük notu — bu belgenin en önemli satırı:** Aşağıdaki personalar
> **birincil kullanıcı araştırmasından gelmiyor.** Görüşme yapılmadı, anket
> uygulanmadı. Personalar iki kaynaktan türetildi: (1) yayımlanmış literatür
> ve sektör raporları, (2) prototipin simülasyon veri kümesinin ölçülebilir
> özellikleri. Hangi iddianın hangi kaynaktan geldiği her başlıkta yazılıdır.
> Doğrulanmamış bir persona, doğrulanmış gibi sunulduğunda tasarım kararlarını
> sahte bir zemine oturtur.

---

## 1. Problemin ölçülebilir yüzü

### Literatürden

Bilgi yükü ve doğrulama davranışına dair bulgular rapor 2.1'de kaynaklarıyla
verilmiştir; burada tekrar edilmez. Tasarımı doğrudan belirleyen üç bulgu:

1. Kullanıcılar akışta gördükleri iddiaların büyük çoğunluğunu **kaynağına
   gitmeden** değerlendiriyor.
2. Doğruluk etiketleri (fact-check rozetleri), etiketlenmeyen içeriğin
   **doğru sanılmasına** yol açabiliyor ("implied truth" etkisi).
3. Yanlış bilgi düzeltmeleri, düzeltilen iddiayı tekrar ettikleri için bazen
   iddiayı pekiştiriyor.

İkinci bulgu, ürünün en somut tasarım kararının gerekçesidir: **MİHENK
"insan yazmış" rozeti göstermez.** Etiketlenmemiş içeriğin temiz sanılmasını
istemiyoruz (bkz. `docs/ETIK.md`, §3.2).

### Simülasyon veri kümesinden

Bunlar ölçülmüş sayılardır; prototipin çalıştığı akışın gerçek dağılımıdır:

| Ölçü | Değer |
|---|---|
| Gönderi | 220 |
| Yazar | 57 (medyan 192 takipçi, en yüksek 2.867) |
| Doğrulanmış hesap | 0 — akışta "otorite" işareti yok |
| Sınanabilir iddia taşıyan gönderi | 46 (%21) |
| Bunlardan veri kümesinde **yanlış** olan | 11 (%24) |
| Görsel içeren gönderi | 71 |
| Bunlardan yapay üretim | 15 (%21) |
| Etkileşim kaydı | 4.172 |

**Doğrulanmış hesabın sıfır olması kasıtlıdır.** Kullanıcı, kimin
söylediğine bakarak karar veremediğinde, sistemin sunduğu tek dayanak
**kaynağa bağlanabilirlik** olur. Ürünün ana iddiası tam da budur.

---

## 2. Personalar

> **Kaynak:** Literatür + simülasyon dağılımı. Görüşmeyle doğrulanmadı.
> Her personada, o personayı **yanlışlayacak** gözlem de yazılıdır — bu,
> kullanılabilirlik testinin sınayacağı hipotezdir.

### P1 — "Akışta boğulan takipçi" (birincil kullanıcı)

- **Durum:** Günde 40-60 dakika akışta; 200+ okunmamış gönderi biriktiriyor.
- **Amaç:** Ne olduğunu hızlıca anlamak, ama önemli bir şeyi kaçırmamak.
- **Engel:** Özet okumak istiyor, fakat özetin "uydurup uydurmadığını"
  bilemiyor.
- **MİHENK karşılığı:** Atıflı özet. Her cümlenin yanındaki kaynak rozeti,
  şüphe duyduğu cümleyi tek tıkla kaynağına götürüyor.
- **Bu personayı yanlışlayacak gözlem:** Kullanıcı kaynak rozetlerine hiç
  tıklamıyorsa, atıf bir güven aracı değil görsel gürültüdür. Kullanılabilirlik
  testinde tıklama sayısı ölçülecektir.

### P2 — "Tereddütlü paylaşımcı"

- **Durum:** Bir iddiayı paylaşmadan önce doğru olup olmadığından emin olmak
  istiyor; ama doğrulama için ayrı bir siteye gitmek istemiyor.
- **Amaç:** Yanlış bir şey paylaşıp mahcup olmamak.
- **Engel:** Doğrulama araçları yavaş ve genellikle İngilizce.
- **MİHENK karşılığı:** Gönderi bağlamında doğrulama; üç sonuçtan biri —
  ve `DOGRULANAMADI`, "yanlış" demek değil.
- **Bu personayı yanlışlayacak gözlem:** Kullanıcı `DOGRULANAMADI` sonucunu
  "yanlış" olarak okuyorsa, ürünün en özenli ayrımı işlemiyor demektir.
  **Bu, kullanılabilirlik testinin en kritik sorusudur.**

### P3 — "Damgalanma riski taşıyan üretici"

- **Durum:** Düzgün, kurumsal bir dille yazan bir hesap sahibi. Belediye,
  okul veya sivil toplum kuruluşu hesabı olabilir.
- **Amaç:** İçeriğinin haksız yere "yapay üretim" diye işaretlenmemesi.
- **Engel:** Yapay metin tespit araçları, düzgün yazılmış metni yapay
  sanmaya eğilimli olabilir.
- **MİHENK karşılığı:** Yüksek eşik + çekimserlik + itiraz akışı. Sistem
  gönderilerin çoğunda hiçbir şey söylemiyor.
- **Ölçülmüş dayanak ve risk:** Gerçek metin ölçümünde yazım hatalı metinlerin
  yakalanma oranı **0,000**; bu, modelin "hatasız yazılmış metni yapay sayma"
  eğiliminde olabileceğine dair bir işarettir. **Bu persona bir tasarım
  hedefi değil, ölçülmüş bir risktir** (bkz. `docs/ETIK.md` §9).

### P4 — Karşı-persona: "Manipülasyon yapmak isteyen"

Personaların çoğu ürünün kime hizmet ettiğini anlatır; bu persona **kime
hizmet etmemesi gerektiğini** anlatır.

- **Amaç:** Kendi çerçevesini "gündem" gibi göstermek; özetleyiciyi kendi
  gönderisini öne çıkarmaya yönlendirmek.
- **Yöntemleri ve karşılıkları:**

| Yöntem | Sistemin cevabı |
|---|---|
| Aynı iddiayı tek hesaptan çok kez paylaşmak | Tek yazarlı küme bastırılır (İlke 3) |
| Gönderiye "önceki talimatları yoksay" yazmak | Sınırlayıcı bloğa sarılır; 40/40 savunma ölçüldü |
| Sahte çerçeve etiketi uydurmak | Etiket veri bölgesine değil blok başlığına yazılır |
| Görünmez karakterle gizli talimat | Sıfır genişlikli ve yön karakterleri temizlenir |

---

## 3. Kullanıcı akışları

Her akış bir ilkeye bağlıdır. İlkeye bağlanamayan ekran prototipe alınmadı.

### A1 — Akışı özetle (İlke 1)

```
Akış (220 okunmamış)
  └─ "Özetle"
      └─ Kategori seç (Gündem / Spor / Teknoloji / Ekonomi / Kişisel)
          └─ Atıflı özet
              ├─ Cümle yanındaki rozete tıkla → kaynak gönderiler
              │   └─ Gönderiye git
              └─ Sistem susmuşsa → gerekçesi görünür
```

**Kritik nokta:** Sistem sustuğunda arayüz yerel bir özetle boşluğu
**doldurmaz**. Sessizlik bir ürün davranışıdır; gizlenirse ürünün en ayırt
edici özelliği görünmez olur.

### A2 — Bir iddiayı doğrula (İlke 2)

```
Gönderi → "Doğrula"
  ├─ DOGRULANDI      → kaynaklarla birlikte
  ├─ YANLIS          → kaynaklarla birlikte
  └─ DOGRULANAMADI   → "bu, iddianın yanlış olduğu anlamına gelmez"
```

### A3 — Yapay üretim sinyali (İlke 2)

```
Gönderi metni → tespit
  ├─ Eşiği geçti  → "yapay üretim olabilir" rozeti + itiraz bağlantısı
  ├─ Geçmedi      → HİÇBİR ŞEY gösterilmez ("insan yazmış" rozeti yok)
  └─ Metin kısa   → çekimser; gerekçe "metin çok kısa"
```

### A4 — Çoğulculuk (İlke 3)

```
Olay kümesi → çerçeve dağılımı çubuğu
  └─ Nötr / Destekleyici / Eleştirel / Soru soran / Doğrulanmamış
      └─ Denge skoru (normalleştirilmiş entropi)
```

**Bu çubuk bir GİRDİ ölçüsüdür**, özetin kendisinin tarafsızlığını ölçmez
(`docs/ETIK.md` §5).

### A5 — İtiraz (etik gereklilik)

```
YZ sinyali rozeti → "İtiraz et" → gerekçe → kayıt
```

Prototipte kayıt TTL'li önbelleğe yazılır; **itirazı inceleyen bir insan
yoktur.** Gerçek sistemde bu zorunludur.

### A6 — Rıza (KVKK)

```
İlk açılış → rıza bandı
  ├─ "Yalnızca zorunlu"  ← varsayılan duruş
  ├─ "Tercihlerimi ayarla"
  └─ "Tümüne izin ver"
```

Rıza gerektiren her kullanım **kapalı başlar**. Ayrıntı:
`docs/VERI_YONETISIMI.md`.

---

## 4. Bu belgenin doğrulanması için gereken

| Eksik | Nasıl kapanır |
|---|---|
| Personalar görüşmeyle doğrulanmadı | 5-8 kişiyle yarı yapılandırılmış görüşme |
| P1'in atıfa gerçekten baktığı varsayımı | Kullanılabilirlik testinde rozet tıklama sayısı |
| P2'nin `DOGRULANAMADI`'yı doğru okuduğu varsayımı | Testte doğrudan sorulacak (protokolde var) |
| P3'ün risk büyüklüğü | Farklı yazım düzeylerinde tespit yanlılığı ölçümü |

İlk üçü `docs/KULLANILABILIRLIK_TESTI.md` protokolüyle, dördüncüsü ayrı bir
ölçüm kümesiyle kapanır. Hiçbiri rapor teslimi itibarıyla yapılmamıştır.
