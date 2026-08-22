# ITS MİHENK — Adım Adım Kurulum ve Yayınlama Kılavuzu

Bu belge hiçbir şey bilmediğini varsayar. Sırayla takip et, atlama.

---

## BÖLÜM 1 — Projeyi kendi bilgisayarında çalıştırma

### Adım 1.1 — Terminali aç
Mac'te `Cmd + Boşluk` → "Terminal" yaz → Enter.

### Adım 1.2 — Proje klasörüne gir
```bash
cd ~/Desktop/ITS/MIHENK/02-prototip
```

### Adım 1.3 — Bağımlılıkları kur (sadece ilk seferde)
```bash
npm install
```
Bir-iki dakika sürer. Bittiğinde bir sürü satır yazıp durur, normal.

### Adım 1.4 — Çalıştır
```bash
npm run dev
```
Şu satırı görmelisin: `Local: http://localhost:3000`

### Adım 1.5 — Tarayıcıda aç
`http://localhost:3000` adresine git. Site açılmalı.

**Durdurmak için:** Terminalde `Ctrl + C`.

---

## BÖLÜM 2 — Vercel'e yayınlama (canlıya alma)

### Adım 2.1 — Vercel hesabı aç
1. https://vercel.com adresine git
2. **"Sign Up"** → **"Continue with GitHub"** seç
3. GitHub hesabınla giriş yap, izin ver

### Adım 2.2 — Vercel'e repoyu görme izni ver
Repo **private** olduğu için Vercel'in onu görmesi gerekiyor.
1. Vercel giriş yaptıktan sonra **"Add New..."** → **"Project"**
2. **"Import Git Repository"** listesinde `ITS-AI-MIHENK` görünmüyorsa:
   - **"Adjust GitHub App Permissions"** bağlantısına tıkla
   - `ITS-AI-MIHENK` reposunu seç → **Save**
3. Listeye dönünce repo görünecek → **"Import"**

### Adım 2.3 — ⚠️ EN KRİTİK AYAR: Root Directory
Proje deponun kökünde değil, `02-prototip` klasörünün içinde.
**Bunu ayarlamazsan yayınlama BAŞARISIZ olur.**

Import ekranında:
1. **"Root Directory"** satırının yanındaki **"Edit"** düğmesine bas
2. Açılan listeden **`02-prototip`** klasörünü seç
3. **"Continue"**

Framework otomatik **Next.js** olarak algılanacak — doğru, dokunma.

### Adım 2.4 — Şimdilik ortam değişkeni EKLEME
API anahtarını sonra ekleyeceğiz. Sistem anahtarsız da çalışır
(özet motoru yerel çalışır, doğrulama "yerel" modda cevap verir).

### Adım 2.5 — Deploy
**"Deploy"** düğmesine bas. 1-3 dakika sürer.

Bitince sana bir adres verir:
`https://its-ai-mihenk-XXXX.vercel.app`

**Bu adresi rapora yazacağız.**

---

## BÖLÜM 3 — Azure OpenAI anahtarını bağlama

### Adım 3.1 — Azure'dan bilgileri al
1. https://portal.azure.com → **"benim-ajan-beyni"** kaynağına tıkla
   (zaten var, yenisini oluşturma)
2. Sol menüden **"Anahtarlar ve Uç Nokta"** (Keys and Endpoint)
3. Şu ikisini kopyala:
   - **KEY 1** → uzun bir harf-rakam dizisi
   - **Endpoint** → `https://benim-ajan-beyni.openai.azure.com` gibi

### Adım 3.2 — Dağıtım (deployment) adını öğren
1. Aynı kaynakta **"Model dağıtımları"** → **"Azure AI Foundry'yi aç"**
2. Sol menüden **"Deployments"**
3. Listede bir dağıtım varsa **adını** not et
4. Yoksa: **"Deploy model"** → **"gpt-4o-mini"** seç → bir ad ver (örn. `mihenk-model`) → Deploy

### Adım 3.3 — Vercel'e ekle
1. Vercel'de projene gir
2. Üstten **"Settings"** → sol menüden **"Environment Variables"**
3. Şu **dört** değişkeni tek tek ekle:

| Name (isim) | Value (değer) |
|---|---|
| `YZ_SAGLAYICI` | `azure` |
| `AZURE_OPENAI_API_KEY` | Adım 3.1'deki KEY 1 |
| `AZURE_OPENAI_ENDPOINT` | Adım 3.1'deki Endpoint |
| `AZURE_OPENAI_DEPLOYMENT` | Adım 3.2'deki dağıtım adı |

Her birinde **"Save"** de.

### Adım 3.4 — Yeniden yayınla
Ortam değişkenleri sadece yeni yayınlamada devreye girer.
1. Üstten **"Deployments"** sekmesi
2. En üstteki yayının sağındaki **"..."** → **"Redeploy"** → **"Redeploy"**

### Adım 3.5 — Test et
Siteye gir → herhangi bir gönderide **"Doğrula"** düğmesine bas.
Artık gerçek model cevap vermeli.

---

## BÖLÜM 4 — Kendi bilgisayarında anahtar kullanmak (isteğe bağlı)

```bash
cd ~/Desktop/ITS/MIHENK/02-prototip
cp .env.example .env.local
open -e .env.local
```

Açılan dosyada şu satırları doldur, kaydet:
```
YZ_SAGLAYICI=azure
AZURE_OPENAI_API_KEY=buraya_key1
AZURE_OPENAI_ENDPOINT=https://benim-ajan-beyni.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=dagitim_adin
```

Sonra `npm run dev` ile yeniden başlat.

> **UYARI:** `.env.local` dosyası asla GitHub'a gitmez (`.gitignore` engelliyor).
> Anahtarını kimseyle paylaşma, ekran görüntüsüne alma.

---

## BÖLÜM 5 — Kod değişikliği yapınca

```bash
cd ~/Desktop/ITS/MIHENK
git add -A
git commit -m "ne değiştirdiysen kısaca yaz"
git push
```

Vercel bunu otomatik algılar ve siteyi kendiliğinden günceller.

---

## SORUN GİDERME

| Belirti | Sebep | Çözüm |
|---|---|---|
| Vercel'de "No Next.js version detected" | Root Directory ayarlanmamış | Settings → General → Root Directory → `02-prototip` |
| Site açılıyor ama Doğrula cevap vermiyor | Anahtar eklenmemiş veya redeploy yapılmamış | Bölüm 3.3 ve 3.4'ü tekrarla |
| `npm run dev` hata veriyor | Bağımlılıklar kurulmamış | `npm install` çalıştır |
| Doğrula "yerel" diyor | Anahtar yok — bu bir hata değil | Sistem bilerek yerel motora düşüyor |
| Azure 401 hatası | Anahtar yanlış kopyalanmış | KEY 1'i baştan kopyala, boşluk olmasın |
| Azure 404 hatası | Dağıtım adı yanlış | Foundry → Deployments'taki adı birebir yaz |

---

## Projenin haritası

```
MIHENK/
├── README.md         ← jüriye gösterilecek proje tanıtımı
├── KURULUM.md        ← bu belge
├── OKUBENI.md        ← ekip içi dizin
├── 01-rapor/         rapor bölümleri ve denetimler
├── 02-prototip/      ⭐ ÇALIŞAN UYGULAMA BURADA
├── 03-veri/          simülasyon verisi üreticisi
├── 04-model/         model çalışmaları (Emre)
├── 05-gorseller/     rapor görselleri
└── 06-kaynak-belgeler/ şartname ve rapor şablonu
```
