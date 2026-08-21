# MİHENK

Sosyal medya akışını kısaltan, ama söylediği her cümleyi kaynağına bağlayan;
emin olmadığında susan bir yapay zekâ katmanı.

**TEKNOFEST 2026 — NSosyal İnovasyon Yarışması projesi.**

---

## Üç ilke

Bu üç ilke ürünün kimliğidir; "nice to have" değildir ve kodda karşılıkları
vardır.

| İlke | Ne demek | Kod karşılığı | Testi |
|---|---|---|---|
| **1. Atıf zorunluluğu** | Kaynağına bağlanmayan hiçbir özet cümlesi gösterilmez | `summarize/citation.py` — atıfsız/uydurma kaynaklı cümle silinir | `test_ilke1_atif.py` |
| **2. Çekimserlik** | Sistem emin değilse hüküm vermez, susar | `detection/decision.py`, asistanın 5 kapısı, köken `display=false` | `test_ilke2_cekimserlik.py` |
| **3. Çoğulculuk** | Tek doğru dayatılmaz; taraflar konumlandırılır | `summarize/service.py` — tek kaynaklı küme bastırılır | `test_ilke3_cogulculuk.py` |

Çekimserlik bir hata değil, **raporlanan bir metriktir**. Aktarım testinde
model kısa metinlerde (K1) %67 oranında susuyor — çünkü orada doğruluğu 0.65'e
düşüyor (bkz. `eval/results/detection.md`).

## Mimari — iki katman

```
KATMAN 1 (akış hızında, kullanıcıdan bağımsız)
  Gönderi → atomik özet + gömme + konu etiketi → TTL'li önbellek
  Çıktı kullanıcılar ARASINDA paylaşılır.

KATMAN 2 (kullanıcı hızında)
  "Özetle" → hazır kayıtlar → kümele → temsilciler → TEK LLM çağrısı
           → ATIF DENETİMİ → atıflı özet
```

Maliyet kullanıcı sayısıyla doğrusal büyümez: kullanıcı başına tekrarlanan tek
pahalı işlem, özet başına **bir** birleştirme çağrısıdır.

Ayrıntı ve diyagramlar: [`docs/MIMARI.md`](docs/MIMARI.md)

## Kurulum

```bash
# 1) Python bağımlılıkları
pip install -r backend/requirements.txt

# torch CPU kurulumu (platforma göre):
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

```bash
# 2) Ön yüz
cd frontend && npm install
```

## Çalıştırma

```bash
# 1) Sentetik akışı üret (300-500 gönderi, tuzaklar dahil)
python ml/scripts/generate_feed.py --count 420

# 2) Arka uç (http://127.0.0.1:8000)
cd backend && uvicorn app.main:app --reload

# 3) Ön yüz (http://localhost:5173)
cd frontend && npm run dev
```

Sistem varsayılan olarak `FakeProvider` ile çalışır — dış çağrı yapmaz, anahtar
gerektirmez. Gerçek LLM için:

```bash
export ANTHROPIC_API_KEY=...
export MIHENK_LLM_PROVIDER=api
```

## Test

```bash
python -m pytest backend/tests -q      # 38 test
cd frontend && npm test                # 7 test
```

Testler dış servise çağrı yapmaz ve gömme modelini yüklemez; saniyeler içinde
koşarlar.

## Ölçüm — raporun tabloları

```bash
python ml/scripts/build_dataset.py            # tespit veri seti + sızıntı denetimi
python ml/scripts/train_detector.py --backend tfidf     # temel çizgi
python ml/scripts/train_detector.py --backend berturk   # ana model
python ml/scripts/build_faithfulness_set.py   # sadakat örneklemi
python ml/scripts/evaluate.py                 # TÜM tablolar
```

Çıktılar `eval/results/` altına hem JSON hem Markdown yazılır:

| Dosya | Rapor yeri |
|---|---|
| `detection.md` | Tablo 4 — tespit başarımı + aktarım testi |
| `summarization.md` | Tablo 5 — sadakat, atıf, gecikme, maliyet |
| `injection.md` | Güvenlik — enjeksiyon savunma oranı |
| `clustering.md` | Kümeleme kalitesi ve eşik kalibrasyonu |

**Rapora elle sayı girilmez.** Bir metrik ölçülemiyorsa tabloya `[  ]` yazılır.

## Belgeler

| Belge | İçerik |
|---|---|
| [`docs/MIMARI.md`](docs/MIMARI.md) | Katmanlar, veri akışı, ilkelerin kod haritası (Şekil 1) |
| [`docs/MODEL_KARTI.md`](docs/MODEL_KARTI.md) | Modeller, sürüm, lisans, hiperparametre, sınırlılıklar |
| [`docs/VERI_YONETISIMI.md`](docs/VERI_YONETISIMI.md) | KVKK sınırları, dört yönetişim kapısı, veri akışı |
| [`docs/TEHDIT_MODELI.md`](docs/TEHDIT_MODELI.md) | İstem enjeksiyonu tehdit modeli ve savunma zinciri |
| [`docs/KULLANILABILIRLIK_TESTI.md`](docs/KULLANILABILIRLIK_TESTI.md) | 5 katılımcılı test protokolü ve SUS formu |

## Ne yapmıyoruz (bilinçli sınırlar)

- **Gerçek platformlardan veri kazımıyoruz.** Tüm veri sentetiktir.
- **Doğruluk hükmü vermiyoruz.** Doğrulama çıktısı üç durumludur:
  `DESTEKLEYEN` / `CELISEN` / `KAYNAK_YOK`. `DOGRU`/`YANLIS` diye bir durum yok.
- **Özet, gönderinin yerine geçmiyor.** Uzunluk üst sınırlıdır ve kaynak çipleri
  kullanıcıyı orijinal gönderiye götürecek biçimde konumlanır.
- **Belirsizliği rozete dönüştürmüyoruz.** Emin olmadığımızda arayüzde boş alan
  bırakılır.

## Durum

| Aşama | Kapsam | Durum |
|---|---|---|
| P0 | Sentetik akış, iki katmanlı hat, atıf denetimi, asistan, güvenlik, tespit + çekimserlik, yönetişim, ön yüz, ölçüm | Tamamlandı |
| P1 | Görsel köken (C2PA/IPTC), doğrulama ajanı (tek senaryo), eşik iyileştirmesi | Köken tamam; ajan bekliyor |
| P2 | Çok kaynaklı ajan, içerik üreticisi modülü, ölçek testi | Planlandı |
