# ITS MİHENK — Prototip Yol Planı

**Tarih:** 19 Ağustos 2026 · **Rapor teslimi:** 24 Ağustos 17:00 (5 gün)

---

## 0. Konumlandırma kararı (her şeyden önce)

NSosyal kendini **reklamsız, algoritmasız, kronolojik** akış olarak tanımlıyor.
MİHENK bu kimliğe karşı değil, **üstüne** konumlanır:

> Akış kronolojik kalır. MİHENK sıralamaya dokunmaz; akışın üzerine oturan
> bir **anlama ve doğrulama katmanı** sunar.

Rapordaki her cümle bu çizgiyi korumalıdır. "Kişiselleştirilmiş akış",
"öneri algoritması", "sana özel sıralama" ifadeleri **kullanılmayacaktır**.
Bunun yerine: "kategori bazlı özet", "okuma katmanı", "talep üzerine özet".

---

## 1. Sistem mimarisi

```
┌─────────────────────────────────────────────────────────┐
│  İSTEMCİ  (Next.js + TypeScript + Tailwind)             │
│  Akış · Özet paneli · Gönderi detay · Asistan · Üretici │
└───────────────────────┬─────────────────────────────────┘
                        │  REST
┌───────────────────────▼─────────────────────────────────┐
│  UYGULAMA KATMANI  (Next.js API Routes)                 │
│  Kimlik · Akış servisi · Özet orkestrasyonu · Önbellek  │
└───────┬───────────────────────────────┬─────────────────┘
        │                               │
┌───────▼─────────┐          ┌──────────▼──────────────────┐
│  VERİTABANI     │          │  YAPAY ZEKÂ KATMANI         │
│  SQLite/Prisma  │          │                             │
│  kullanıcı      │          │  A) LOKAL (özgün/yerli)     │
│  gönderi        │          │     · Özetleme modeli       │
│  etkileşim      │          │     · Kümeleme (embedding)  │
│  özet önbelleği │          │     · Görsel AI tespiti     │
│  doğrulama kaydı│          │                             │
└─────────────────┘          │  B) API (agentic)           │
                             │     · Doğrulama + web arama │
                             │     · Asistan soru-cevap    │
                             └─────────────────────────────┘
```

**Neden bu ayrım:** Yüksek frekanslı ve dar kapsamlı görevler (özet, kümeleme,
görsel denetim) lokalde — düşük maliyet + yerlilik. Güncel dünya bilgisi
gerektiren görevler (doğrulama) API'de — çünkü küçük bir model bunu yapamaz.
Bu ayrım raporda **3.1** ve **2.2 (yerlilik)** maddelerini birlikte karşılar.

---

## 2. Ekranlar → rapor puanı eşlemesi

Her ekran belirli bir rubrik maddesini beslemek için yapılır. Süs yok.

| # | Ekran | Rapora katkısı | Faz |
|---|---|---|---|
| E1 | Ana akış (kronolojik, NSosyal düzeni) | Prototip kalitesi %15 · 3.3 | **1** |
| E2 | **Özet paneli** — Gündem / Spor / Kişisel sekmeleri | Projenin kalbi · 1.1 · 4.1 | **1** |
| E3 | Gönderi detay + gönderiye özel özet | 3.3 · 4.1 | **1** |
| E4 | **Doğrulama sonucu** — kaynak listesi + güven göstergesi | 2.2 · 5.1 · Problemi Çözme %20 | **1** |
| E5 | Asistan paneli (gönderi hakkında soru-cevap) | 3.1 · Teknik Yeterlilik %35 | 2 |
| E6 | **Tarafsızlık göstergesi** — çerçeve dağılımı | 2.2 özgünlük · Yenilikçilik %20 | 2 |
| E7 | Görsel köken/AI üretim rozeti | 2.2 · yerli bileşen | 2 |
| E8 | İçerik üretici paneli (analitik + öneri) | İçerik Ekonomisi ikincil tema | 3 |
| E9 | Erişilebilirlik ayarları (kontrast, yazı boyutu) | 3.3 erişilebilirlik 2p | 2 |

**Faz 1 = 24 Ağustos raporu için zorunlu.** Faz 2 = yetişirse rapora, yetişmezse
14 Eylül final teslimine. Faz 3 = final aşaması.

---

## 3. Teknoloji seçimi

| Katman | Seçim | Gerekçe |
|---|---|---|
| Arayüz | Next.js 15 + TypeScript + Tailwind | Hızlı kurulum, profesyonel ekran görüntüsü, temiz erişilebilirlik denetimi |
| Backend | Next.js API Routes | Tek repo, tek deploy — 5 günde ayrı servis yönetmek risk |
| Veritabanı | SQLite + Prisma | Gerçek şema = raporda "veritabanı tasarımı" malzemesi; kurulum sıfır |
| ML servisi | Python FastAPI (ayrı, Faz 2) | Emre'nin modelleri buraya bağlanır |
| LLM | API (doğrulama + asistan) | Güncel bilgi ve web araması gerektiği için |
| Test | Playwright (temel akış) | 3.1'de "test" iddiası için somut dayanak |

---

## 4. Beş günlük plan

| Gün | Yapılacak | Kim |
|---|---|---|
| **19 Ağu (bugün)** | Proje kurulumu, veri → SQLite, E1 ana akış | Claude |
| | KYS başvuru + Google Groups | Ümit |
| | Base model seçimi, distillation verisi | Emre |
| **20 Ağu** | E2 özet paneli, E3 gönderi özeti | Claude |
| | Marka/tasarım geçişi, NSosyal düzen uyumu | Ümit |
| | İlk fine-tune koşusu | Emre |
| **21 Ağu** | E4 doğrulama ekranı + API entegrasyonu | Claude |
| | Erişilebilirlik denetimi + sezgisel değerlendirme | Claude |
| | 5 kişilik kullanılabilirlik testi | Ümit |
| **22 Ağu** | Faz 2 ekranları (E5-E7, E9) + ekran görüntüleri | Claude |
| | Bölüm 4, 5, 7, 8 yazımı | Ümit |
| | Bölüm 6 + 3.1/3.2 yazımı | Emre |
| **23 Ağu** | Rapor görselleri, birleştirme, format denetimi | Claude + Ümit |
| **24 Ağu sabah** | Son kontrol → KYS yükleme | Ümit |

---

## 5. Riskler ve kesme noktaları

| Risk | Etki | Önlem |
|---|---|---|
| LLM API anahtarı yok/limitli | E4, E5 çalışmaz | Sabit örnek yanıtlarla demo modu; raporda "API entegrasyonu" olarak gösterilir |
| Model eğitimi yetişmez | 3.2'de metrik olmaz | Etiketli veri üzerinde en az kümeleme + görsel tespit metrikleri çıkarılır |
| Prototip Faz 1'i geçemez | Ekran görüntüsü az olur | Faz 1'in dördü zorunlu; Faz 2 feda edilebilir |
| Rapor yazımı geri kalır | Elenme riski | **Rapor her zaman önceliklidir.** 22 Ağustos akşamı prototip ne durumdaysa dondurulur. |

**Altın kural:** 23 Ağustos'ta prototip değil, rapor bitmiş olacak. Prototip
rapora hizmet eder, tersi değil.

---

## 6. Başlamadan önce netleşmesi gereken 2 şey

1. **LLM API erişimi** — hangi servise anahtarınız var? (Doğrulama ve asistan
   modülleri buna bağlı.)
2. **Gerçek NSosyal ekran görüntüleri** — platform bot erişimini engelliyor
   (403). Arayüzü doğru kopyalamak için akış, gönderi kartı ve profil
   ekranlarının görüntüleri gerekli.
