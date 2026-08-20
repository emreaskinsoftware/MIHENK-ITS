<div align="center">

# ITS MİHENK

**Sosyal medya akışını kısa, dengeli ve doğrulanabilir özetlere dönüştüren yapay zekâ katmanı**

NSosyal İnovasyon Yarışması 2026 · Tematik Alan: **Sosyal Yapay Zekâ**

[Problem](#problem) · [Çözüm](#çözüm) · [Mimari](#mimari) · [Kurulum](#kurulum) · [Depo Düzeni](#depo-düzeni)

</div>

---

## Proje Adı Nereden Geliyor?

**Mihenk taşı**, bir madenin gerçek değerini ortaya çıkarmak için sürtüldüğü taştır.
MİHENK de aynı işi bilgi için yapar: akışta dolaşan bir iddiayı kaynaklarıyla sınar,
gerçek değerini görünür kılar.

---

## Problem

Türkiye'de sosyal medya, bilgiye erişimin birincil altyapısı hâline geldi. TÜİK 2025
verilerine göre 16-74 yaş grubunda internet kullanım oranı **%90,9**; ülkede
**62,3 milyon** sosyal medya kullanıcı kimliği bulunuyor.

Ancak bu erişim genişliği bilgiye dönüşmüyor. Sorun iki eksende birikiyor:

**1. Bilgi aşırı yüklenmesi → kaçınma.**
Reuters Institute 2026 Dijital Haber Raporu'na göre haberden kaçınma küresel ortalaması
%42 iken **Türkiye, bu oranın %60'ı aştığı dört ülkeden biri.** Kullanıcı bilgiye
erişemediği için değil, eriştiği hacmi işleyemediği için gündemden uzaklaşıyor.

**2. Güven erozyonu → doğrulama yükü.**
Habere duyulan güven %37 ile 2015'ten bu yana en düşük seviyede. Sosyal medya
üzerinden gelen habere güven ise yalnızca %22. Kullanıcı bir iddiayı sınamak için
akıştan çıkmak zorunda kalıyor; bu maliyet nedeniyle doğrulama çoğu zaman hiç yapılmıyor.

> Kritik bulgu: Yapay zekâ tarafından üretilen cevaplara duyulan güven de yalnızca **%20**.
> Bu, bir çözümün sadece "yapay zekâ ile özetlemesinin" yetmediğini; çıktının **kaynak ve
> güven göstergeleriyle** sunulmasının zorunlu olduğunu gösteriyor. MİHENK'in temel
> tasarım kararı buradan doğdu.

---

## Çözüm

MİHENK, NSosyal deneyimini simüle eden bir web prototipi üzerinde çalışan bir
**anlama ve doğrulama katmanıdır.**

### Değişmez tasarım ilkesi

NSosyal kendini **reklamsız, algoritmasız, kronolojik** akış olarak tanımlar.
MİHENK bu kimliğe karşı değil, üstüne konumlanır:

> **Akış sırası değişmez.** MİHENK sıralamaya dokunmaz; akışın üzerine oturan bir
> okuma katmanı sunar. Özet, akışın yerine geçmez — akışı okunabilir kılar.

Bu nedenle projede "kişiselleştirilmiş akış", "öneri algoritması" veya "sana özel
sıralama" gibi kavramlar bilinçli olarak **kullanılmamaktadır.**

### Modüller

| # | Modül | Ne yapar | Katman |
|---|---|---|---|
| 1 | **Kategori bazlı özet** | Ülke gündemi, spor, teknoloji, ekonomi ve kişisel akış için ayrı özetler | Yerel |
| 2 | **Gönderi bazlı özet** | Tek bir gönderiyi bağlamından kopmadan özetler | Yerel |
| 3 | **Olay kümeleme** | Aynı olayla ilgili gönderileri gruplar, özetin girdisini hazırlar | Yerel |
| 4 | **Özet tarafsızlığı** | Özetin hangi çerçeve dağılımından üretildiğini görünür kılar | Yerel |
| 5 | **Görsel köken denetimi** | Üretim etiketi, içerik kökeni ve görsel bulguları birleştirir | Yerel |
| 6 | **Ajan tabanlı doğrulama** | İddiayı açık web kaynaklarıyla sınar, kaynak + güven göstergesi sunar | Uzak |
| 7 | **Akış içi asistan** | Gönderi hakkındaki soruları bağlam içinde yanıtlar | Uzak |
| 8 | **İçerik üretici paneli** | Anonim etkileşim verisinden konu ve zamanlama önerisi üretir | Yerel |

---

## Özet Tarafsızlığı — Projenin Ayrışma Noktası

Gündem özeti üreten her sistem örtük bir editoryal karar verir: **aynı olayı hangi
çerçeveden anlatacağını seçer.** Literatürde algoritmik önyargı olarak tanımlanan bu
risk, mevcut özetleme çözümlerinde büyük ölçüde ele alınmamaktadır.

MİHENK'in yaklaşımı:

1. Bir olay etrafındaki gönderiler çerçevelerine ayrıştırılır
   (nötr · destekleyici · eleştirel · soru soran · doğrulanmamış)
2. Özet, **en çok etkileşim alan** gönderilerden değil, **her çerçeveden en temsili**
   gönderiden üretilir
3. Çerçeve dağılımı ve **denge skoru** kullanıcıya açık edilir

Denge skoru, çerçeve dağılımının normalleştirilmiş Shannon entropisidir:
`1` tam dengeli, `0` tek çerçeve baskın.

---

## Mimari

```
┌──────────────────────────────────────────────────────────┐
│  İSTEMCİ  · Next.js 16 + React 19 + TypeScript + Tailwind│
│  Akış · Özet paneli · Gönderi detay · Asistan · Üretici  │
└────────────────────────┬─────────────────────────────────┘
                         │ REST
┌────────────────────────▼─────────────────────────────────┐
│  UYGULAMA KATMANI · Next.js API Routes                   │
│  /api/ozet · /api/dogrula · /api/asistan                 │
│  /api/gorsel-denetim                                     │
└────────┬──────────────────────────────┬──────────────────┘
         │                              │
┌────────▼─────────┐        ┌───────────▼──────────────────┐
│  VERİ KATMANI    │        │  YAPAY ZEKÂ KATMANI          │
│  Etiketli        │        │                              │
│  simülasyon      │        │  A) YEREL  (özgün / yerli)   │
│  · kullanıcı     │        │     · Özetleme modeli        │
│  · gönderi       │        │     · Olay kümeleme          │
│  · etkileşim     │        │     · Görsel AI tespiti      │
│  · olay kümesi   │        │                              │
│                  │        │  B) UZAK   (agentic)         │
│                  │        │     · Doğrulama + web arama  │
│                  │        │     · Asistan soru-cevap     │
└──────────────────┘        └──────────────────────────────┘
```

### Neden hibrit?

Yüksek frekanslı ve dar kapsamlı görevler (özetleme, kümeleme, görsel denetim)
**yerel** olarak çalıştırılır — düşük birim maliyet ve dış servis bağımsızlığı sağlar,
yerli bileşen olarak geliştirilir. Güncel dünya bilgisi ve web taraması gerektiren
görevler (doğrulama) **uzak** modelle yürütülür, çünkü küçük bir yerel model bu görevi
karşılayamaz.

**Anahtar tanımlı değilse sistem sessizce yerel katmana düşer.** Bu, gösterim sırasında
ağ veya kota sorununun demoyu kesmemesi için bilinçli bir tasarım kararıdır.

---

## Yerli Bileşenler

| Bileşen | Durum |
|---|---|
| **Türkçe özetleme modeli** — Türkçe için ön eğitimli açık kaynaklı temel modelin, proje kapsamında üretilen veri kümesiyle ince ayarlanması | Geliştiriliyor |
| **Görsel üretim tespit modeli** — yerel olarak çalışan sınıflandırıcı | Geliştiriliyor |
| **Etiketli Türkçe değerlendirme veri kümesi** — olay kümesi, çerçeve, iddia ve görsel köken etiketleriyle | ✅ Üretildi |

---

## Veri Kümesi

`03-veri/seed_uret.py` betiği, platformu simüle eden **kurgusal** veri üretir.
Veri gerçek kişi, kurum, marka veya olay içermez.

Verinin ayırt edici yanı **etiketli** olmasıdır — her gönderide dört altın etiket bulunur:

| Etiket | Hangi modülün başarımını ölçer |
|---|---|
| `olay_id` | Olay kümeleme doğruluğu — 13 gerçek küme |
| `cerceve` | Özet tarafsızlığı — çerçeve dağılımı |
| `gorsel_yapay_uretim` | Görsel AI tespiti — 15 pozitif örnek |
| `iddia_dogru_mu` | Doğrulama motoru — 46 iddia, 11'i yanlış |

Bu etiketler sayesinde modüllerin başarımı **gerçek ölçümle** raporlanabilmektedir.

Gönderiler rastgele değil, **olay kümeleri** etrafında üretilir: her olayın çevresinde
farklı çerçevelerden gönderiler bulunur. Böylece kümeleme modülünün bulacağı gerçek
kümeler, tarafsızlık modülünün dengeleyeceği çoklu çerçeveler ve doğrulama motorunun
sınayacağı iddialar aynı veriden çıkar.

```bash
cd 03-veri && python3 seed_uret.py
```

---

## Etik Çerçeve

Doğruluk hükmü veren bir sistem, hüküm vermediği anı da tanımlamak zorundadır.

- **"Doğrulanamadı" ≠ "Yanlış".** Yeterli kaynak bulunamadığında sistem hüküm vermez.
  Doğrulama ucu üç sonuçtan birini verir: `DOGRULANDI` · `YANLIS` · `DOGRULANAMADI`.
- **Görsel denetim olasılık temellidir**, kesin hüküm değildir. Yüksek olasılık bile
  "bu görsel sahtedir" anlamına gelmez; kullanıcıya uyarı sunulur.
- **Nihai karar kullanıcınındır.** Sistem karar vermez, karar için gereken bağlamı sunar.
- **Model halüsinasyonuna karşı**: özet ve asistan yalnızca verilen bağlama dayanır;
  bağlam dışına çıkması istem düzeyinde kısıtlanmıştır.

### KVKK ve veri mahremiyeti

- Etkileşim sinyalleri kullanıcı rızasıyla toplanır ve **kişisel bilgilerden arındırılarak**
  toplulaştırılır.
- Simülasyon verisinde kullanıcı kimliği taşınmaz; yalnızca toplulaştırılabilir segment
  ve takipçi aralığı tutulur.
- API anahtarları depoya **hiçbir koşulda** girmez (`.gitignore` ile korunur).

---

## Kurulum

### Gereksinimler
Node.js 20+ · Python 3.10+ (veri üreticisi için)

### Prototip

```bash
cd 02-prototip
npm install
cp .env.example .env.local   # anahtarınızı girin (opsiyonel)
npm run dev                  # http://localhost:3000
```

**Anahtar olmadan da çalışır.** Doğrulama ve asistan modülleri yerel katmana düşer,
özet motoru çıkarımsal temel modeli kullanır.

### Yapay zekâ sağlayıcı yapılandırması

`.env.local` içinde:

```env
YZ_SAGLAYICI=claude          # claude | openai | gemini
ANTHROPIC_API_KEY=sk-ant-...
```

Sistem üç sağlayıcıyı da destekler; tercih belirtilmezse tanımlı olan ilk anahtarı seçer.

---

## API Uçları

| Uç | Yöntem | Açıklama |
|---|---|---|
| `/api/ozet` | POST | Kategori, olay, gönderi veya kişisel akış özeti |
| `/api/dogrula` | POST | Ajan tabanlı iddia doğrulama, kaynak + güven skoru |
| `/api/asistan` | POST | Gönderi bağlamında soru-cevap |
| `/api/gorsel-denetim` | POST | Görsel köken ve yapay üretim denetimi |

---

## Depo Düzeni

```
MIHENK/
├── 01-rapor/            Rapor bölümleri, uyum denetimi, yol planı
├── 02-prototip/         Next.js web prototipi (frontend + backend)
│   ├── src/app/         Sayfalar + API uçları
│   ├── src/components/  Arayüz bileşenleri
│   ├── src/lib/         Veri katmanı, özet motoru, YZ soyutlaması
│   └── data/            Simülasyon verisi
├── 03-veri/             Veri üreticisi ve etiketli çıktı
├── 04-model/            Özetleme ve görsel tespit modelleri
├── 05-gorseller/        Rapor şemaları ve ekran görüntüleri
└── 06-kaynak-belgeler/  Şartname ve rapor şablonu
```

---

## Teknoloji Yığını

| Katman | Seçim |
|---|---|
| Arayüz | Next.js 16 · React 19 · TypeScript · Tailwind CSS 4 |
| Backend | Next.js API Routes |
| Veri | Etiketli JSON simülasyon kümesi |
| YZ (yerel) | Çıkarımsal özet motoru · Türkçe embedding tabanlı kümeleme |
| YZ (uzak) | Claude · OpenAI · Gemini (değiştirilebilir sağlayıcı katmanı) |
| İkonlar | Lucide |

---

## Takım

Değerlendirme esasları gereği takım üyelerinin kişisel bilgileri bu belgede
paylaşılmamaktadır.

| Rol | Sorumluluk |
|---|---|
| Takım Kaptanı · Ürün ve Arayüz | UI/UX tasarımı, frontend, simülasyon altyapısı, ürün kurgusu |
| Yapay Zekâ Geliştirme ve Entegrasyon | Model eğitimi, YZ mimarisi, veri doğrulama, KVKK ve güvenlik |
| Akademik Danışman | Teknik ve akademik yönlendirme |

---

## Yol Haritası

- [x] NSosyal simülasyon kabuğu ve kronolojik akış
- [x] Kategori bazlı özet paneli
- [x] Özet tarafsızlığı göstergesi ve denge skoru
- [x] Etiketli simülasyon veri kümesi
- [x] Çok sağlayıcılı YZ soyutlaması ve API uçları
- [ ] Keşfet, Bildirimler, Profil, Topluluklar, Ayarlar ekranları
- [ ] Açık tema ve mobil görünüm
- [ ] Asistan ve doğrulama arayüzleri
- [ ] İçerik üretici paneli
- [ ] Türkçe özetleme modelinin ince ayarı ve ROUGE değerlendirmesi
- [ ] Görsel üretim tespit modelinin entegrasyonu
- [ ] Erişilebilirlik denetimi (WCAG 2.2 AA)

---

## Kaynaklar

[1] Türkiye İstatistik Kurumu, *Hanehalkı Bilişim Teknolojileri Kullanım Araştırması 2025*,
27.08.2025 · https://www.tuik.gov.tr

[2] Kemp, S., *Digital 2026: Turkey*, DataReportal, 2026 ·
https://datareportal.com/reports/digital-2026-turkey

[3] Reuters Institute for the Study of Journalism, *Digital News Report 2026*,
University of Oxford, 2026 ·
https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2026/dnr-executive-summary

---

<div align="center">

**ITS** · NSosyal İnovasyon Yarışması 2026

</div>
