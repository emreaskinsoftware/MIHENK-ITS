# Arayüz ↔ Backend Entegrasyonu

Bu belge, Next.js arayüzünün (`02-prototip`) FastAPI backend'ine
(`emreaskinsoftware/MIHENK-ITS → backend/`) nasıl bağlandığını tanımlar.

## Çalıştırma

```bash
# 1) Backend (Emre'nin deposu)
cd MIHENK-ITS/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2) Arayüz (bu depo)
cd MIHENK/02-prototip
echo "NEXT_PUBLIC_MIHENK_API=http://localhost:8000" >> .env.local
npm run dev
```

Backend'e **erişilemezse** arayüz yerel çıkarımsal motora düşer ve çalışmaya
devam eder; düştüğünü ekranda yazar ("bu metin atıf içermez"). Gösterim hiçbir
koşulda kesilmez.

Backend **erişilebilir ama çekimser kaldıysa** yerel motora DÜŞÜLMEZ.
Sistemin sustuğu an (İlke 2) yerel bir metinle doldurulursa, ilkeli sessizlik
ekranda hiç görünmez ve ürünün en ayırt edici davranışı gizlenmiş olur.

## Uç nokta eşlemesi

| Backend ucu | Arayüzde nerede | İstemci fonksiyonu |
|---|---|---|
| `GET /api/saglik` | Bağlantı denetimi | `mihenkApi.saglik()` |
| `GET /api/akis` | Ana akış | *(şimdilik yerel veri)* |
| `POST /api/ozetle` | *(backend'in kendi akışı için — bu arayüzden çağrılmaz)* | `mihenkApi.ozetle()` |
| `POST /api/ozetle/metinler` | MİHENK Özet paneli — atıflı özet | `mihenkApi.ozetleMetinler()` |
| `POST /api/sor` | Asistan paneli | `mihenkApi.sor()` |
| `POST /api/tespit` | Gönderi kartındaki YZ sinyali rozeti | `mihenkApi.tespitMetin()` |
| `GET /api/tespit/{id}` | *(backend'in kendi akışı için)* | `mihenkApi.tespit()` |
| `GET /api/koken/{id}` | Görsel köken rozeti | `mihenkApi.koken()` |
| `POST /api/itiraz` | İtiraz akışı | `mihenkApi.itiraz()` |

**Neden iki ayrı özet ve tespit ucu var:** Bu prototip kendi simülasyon veri
kümesiyle çalışıyor ve gönderi kimlikleri backend'in deposundakilerle
uyuşmuyor (`ebfc698985c6` ↔ `p0411`). Kimliğe dayalı uçlar buradan çağrılırsa
her istek boş sonuç ya da 404 döner. `metinler` / `tespit` uçları metni
gövdede alır ve AYNI servis kodundan geçirir; arayüzün gördüğü davranış,
`ml/scripts/evaluate.py`'nin ölçtüğü davranışla aynı kalır.

## Üç ilkenin arayüzdeki karşılığı

Backend'in ilkeleri yanıt şemasında kodlanmıştır. Arayüz bu alanları
**yok saymaz** — her birinin görsel karşılığı vardır:

| İlke | Şema alanı | Arayüz bileşeni |
|---|---|---|
| **Atıf zorunluluğu** | `sentences[].source_post_ids` | `AtifliOzet` — her cümlenin yanında kaynak rozeti, tıklanınca kaynak gönderiler listelenir |
| | `dropped_sentence_count` | Aynı bileşende: "N cümle atıf denetiminden geçemedi, silindi" |
| **Çekimserlik** | `abstained` / `refused` | `CekimserlikRozeti` — "Sistem hüküm vermiyor", gerekçesiyle |
| **Çoğulculuk** | `single_source_cluster_count` | `AtifliOzet` — "N küme tek kaynaklı olduğu için bastırıldı" |

**Tasarım ilkesi:** Bu sayılar gizlenmez. Sistemin ne yapmadığını göstermek,
ne yaptığını göstermek kadar önemlidir.

## Veri modeli farkı — çözülmesi gereken

| Konu | Arayüz (bu depo) | Backend (Emre) |
|---|---|---|
| Gönderi kimliği | `id` | `id` ✅ |
| Yazar | `yazar_id` | `author_id` |
| Metin | `metin` | `text` |
| Kategori | `kategori` (tr) | `category` (PostCategory) |
| Altın etiket | `olay_id`, `cerceve` | `_eval_event_id`, `_eval_length_bucket` |

**Karar gerekiyor:** Tek veri kümesinde birleşilecek. Öneri — backend'in
şeması esas alınsın (Pydantic ile tip güvenli ve değerlendirme alanları
zaten orada), arayüz tarafında ince bir çeviri katmanı yazılsın.
