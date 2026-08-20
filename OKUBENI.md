# ITS MİHENK — Proje Kök Dizini

NSosyal İnovasyon Yarışması 2026 · Takım: ITS · Tematik alan: **Sosyal Yapay Zekâ**

> **Teslim:** Teknik rapor — 24 Ağustos 2026, 17:00 (TSİ), KYS üzerinden.

---

## Klasör düzeni

| Klasör | İçerik | Sahip |
|---|---|---|
| `01-rapor/` | Rapor bölümleri, uyum denetimi, yol planı | Ümit + Emre |
| `02-prototip/` | Next.js web prototipi (frontend + backend) | Claude + Ümit |
| `03-veri/` | Sentetik platform verisi üreticisi ve çıktısı | Claude |
| `04-model/` | Özetleme ve görsel tespit modelleri | Emre |
| `05-gorseller/` | Rapora girecek şema, diyagram, ekran görüntüleri | Claude + Ümit |
| `06-kaynak-belgeler/` | Şartname, rapor şablonu, takım tanıtım dosyası | — |

---

## 01-rapor

| Dosya | Ne işe yarar |
|---|---|
| `uyum_denetimi.md` | Şartname v3 + rapor şablonu karşılaştırması. **Önce bunu oku** — 9 açık boşluk listeli. |
| `yol_plani_prototip.md` | Mimari, ekran→puan eşlemesi, günlük takvim, risk planı |
| `bolum2_katma_deger.md` | Rapor Bölüm 2 (15 puan) — yazılmış, rapora aktarılmaya hazır |

## 02-prototip

Next.js 16 + React 19 + TypeScript + Tailwind 4.

```bash
cd 02-prototip
npm install     # ilk kurulumda
npm run dev     # http://localhost:3000
```

Kaynak düzeni:

```
src/
  app/          sayfalar (App Router) + globals.css (NSosyal tasarım belirteçleri)
  components/
    layout/     Sidebar, SagRay, Avatar, OnayliRozet
    akis/       GonderiKarti, Olusturucu
    ozet/       OzetPaneli, OzetTetikleyici, DengeCubugu
  lib/
    tipler.ts   ortak tip tanımları
    veri.ts     veri erişim katmanı (kümeleme, olay grupları)
    bicim.ts    Türkçe sayı/zaman biçimlendirme (2B, 44dk)
    ozet/
      cikarimsal.ts   çıkarımsal özet TEMEL modeli + denge skoru
data/           simülasyon verisi (03-veri'den kopyalanır)
```

## 03-veri

```bash
cd 03-veri
python3 seed_uret.py    # cikti/ altına üretir
```

Üretilen veri **etiketlidir** — her gönderide dört altın etiket vardır:

| Etiket | Hangi modülü ölçer |
|---|---|
| `olay_id` | Kümeleme doğruluğu (13 gerçek küme) |
| `cerceve` | Özet tarafsızlığı (çerçeve dağılımı) |
| `gorsel_yapay_uretim` | Görsel AI tespiti (15 pozitif örnek) |
| `iddia_dogru_mu` | Doğrulama motoru (46 iddia, 11'i yanlış) |

Bu etiketler sayesinde rapor 3.2'nin istediği **performans metrikleri** gerçek
ölçümle üretilebilir. Veri kurgusaldır; gerçek kişi, kurum veya olay içermez.

---

## Tasarım kararı — değişmez ilke

NSosyal kendini **reklamsız, algoritmasız, kronolojik** akış olarak tanımlar.
MİHENK bu kimliğe karşı değil, üstüne konumlanır:

> Akış sırası değişmez. MİHENK sıralamaya dokunmaz; akışın üzerine oturan bir
> **anlama ve doğrulama katmanı** sunar.

Raporda ve arayüzde "kişiselleştirilmiş akış", "öneri algoritması", "sana özel
sıralama" ifadeleri **kullanılmaz**.
