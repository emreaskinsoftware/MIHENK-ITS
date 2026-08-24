# MİHENK — Mimari

> Bu belge raporun 3.1 bölümüne **Şekil 1** olarak girer.
> Şemalar Mermaid ile yazılmıştır; GitHub üzerinde doğrudan render edilir.

## 1. Problem ve mimari karar

Kullanıcı "Özetle" düğmesine bastığında 200 okunmamış gönderiyi tek bir prompt'a
doldurmak iki sorun üretir:

1. **Gecikme.** Uzun bağlam, p95 yanıt süresini 20 saniyenin üzerine çıkarır.
   Kullanıcı akışta beklemez.
2. **Maliyet.** Her kullanıcı kendi akışının tamamını yeniden işletir; maliyet
   kullanıcı sayısıyla **doğrusal** büyür.

MİHENK bu yüzden işi ikiye böler. Ayrım pazarlama değil, maliyet ve gecikme
kararıdır.

```mermaid
flowchart TB
    subgraph K1["KATMAN 1 — Eşzamansız zenginleştirme (akış hızında)"]
        direction LR
        A["Gönderi akışa düşer"] --> B["Kuyruk"]
        B --> C["İşçi: enrichment/worker.py"]
        C --> D["Atomik özet<br/>(1-2 cümle, ≤40 kelime)"]
        C --> E["Vektör gömme<br/>(multilingual-e5-base)"]
        C --> F["Konu etiketi<br/>(sözlük tabanlı)"]
        D & E & F --> G[("Önbellek<br/>enriched:{post_id}<br/>TTL 24 saat")]
    end

    subgraph K2["KATMAN 2 — Talep anında birleştirme (kullanıcı hızında)"]
        direction TB
        H["Kullanıcı: Özetle"] --> I["Okunmamış gönderilerin<br/>HAZIR kayıtlarını çek"]
        I --> J["Eksik olanı ATLA<br/>(senkron üretme)"]
        I --> K["Kümele<br/>aglomeratif, kosinüs"]
        K --> L["Küme temsilcileri<br/>(merkeze en yakın 3)"]
        L --> M["TEK LLM çağrısı<br/>atıflı özet iste"]
        M --> N{"ATIF DENETİMİ<br/>citation.py"}
        N -->|"kaynak geçerli"| O["Özet cümlesi + kaynak çipleri"]
        N -->|"kaynak boş/uydurma"| P["SİL<br/>dropped_sentence_count++"]
    end

    G -.->|"paylaşılan önbellek"| I

    subgraph AJ["AJAN AKIŞI — yalnızca kullanıcı açıkça isterse (P1/P2)"]
        Q["doğrula / araştır"] --> R["Plan → araç → kaynak"]
        R --> S["Üç durumlu çıktı<br/>DESTEKLEYEN / CELISEN / KAYNAK_YOK"]
    end

    O --> T["Arayüz"]
    S -.-> T
```

### Neden bu ayrım maliyeti düşürür

Atomik özet **kullanıcıdan bağımsızdır**: aynı gönderiyi 1000 kişi görse de bir
kez üretilir ve önbellekte paylaşılır. Kullanıcı başına tekrarlanan tek pahalı
işlem, özet başına **tek** birleştirme çağrısıdır.

Ölçülen değerler (`eval/results/summarization.md`):

| Ölçüm | Değer |
|---|---|
| Akıştaki gönderi | 420 |
| Yapılan atomik özet çağrısı | 227 |
| Kısa olduğu için çağrı yapılmayan gönderi | 193 |
| Zenginleştirmede çağrı tasarrufu | ~%46 |
| Özet başına birleştirme çağrısı | 1 |

15 kelimeden kısa gönderilerde özet üretilmez (metnin kendisi zaten özettir);
bu tek kural, çağrı sayısını gönderi sayısının yarısına indirir.

## 2. Katmanlar ve sorumlulukları

```mermaid
flowchart LR
    subgraph UI["Arayüz — frontend/"]
        U1["Akış kartı"]
        U2["Özet paneli"]
        U3["Asistan çekmecesi"]
        U4["İtiraz akışı"]
    end

    subgraph API["API — backend/app/main.py"]
        direction TB
        E1["/api/akis"]
        E2["/api/ozetle<br/>+ /api/ozetle/metinler"]
        E3["/api/sor"]
        E4["/api/tespit<br/>(kimlikli + kimliksiz)"]
        E5["/api/koken"]
        E6["/api/itiraz"]
    end

    subgraph SRV["Servis katmanı — ilkeler BURADA uygulanır"]
        S1["enrichment/<br/>KATMAN 1"]
        S2["summarize/<br/>KATMAN 2 + atıf denetimi"]
        S3["assistant/<br/>bağlam sınırı + 5 kapı"]
        S4["detection/<br/>model + çekimserlik"]
        S5["provenance/<br/>üç katmanlı köken"]
        S6["security/<br/>enjeksiyon savunması"]
        S7["governance/<br/>PII, izin, k-eşiği, TTL"]
    end

    subgraph ALT["Altyapı"]
        L1["llm/provider.py<br/>soyutlama"]
        L2["llm/embedding.py"]
        L3["store/cache.py<br/>TTL önbellek"]
        L4["store/feed_repo.py"]
    end

    UI --> API --> SRV --> ALT
```

**Kritik kural:** İlkeler API katmanında değil, servis katmanında uygulanır.
Arayüze zaten temiz veri gider. Bunun sebebi ölçümdür: `ml/scripts/evaluate.py`
servis fonksiyonlarını doğrudan çağırır; mantık uç noktalara sızsaydı ölçtüğümüz
kod ile kullanıcının çalıştırdığı kod farklı olurdu.

## 3. Üç ilkenin kod karşılığı

```mermaid
flowchart TB
    subgraph I1["İlke 1 — Atıf zorunluluğu"]
        A1["models/summary.py<br/>SummarySentence:<br/>source_post_ids boş olamaz<br/>(tip düzeyinde)"]
        A2["summarize/citation.py<br/>audit_citations():<br/>uydurma ID = cümle silinir"]
        A3["assistant/service.py<br/>Kapı 4: atıfsız yanıt reddedilir"]
    end

    subgraph I2["İlke 2 — Çekimserlik"]
        B1["detection/decision.py<br/>karar_ver():<br/>kısa metin / belirsizlik bandı<br/>→ label=None"]
        B2["assistant/service.py<br/>Kapı 2: bağlamda yoksa reddet"]
        B3["provenance/service.py<br/>üst veri yok → display=false"]
        B4["frontend YzSinyali.tsx<br/>label=null → hiçbir rozet yok"]
    end

    subgraph I3["İlke 3 — Çoğulculuk"]
        C1["summarize/service.py<br/>_kume_secimi():<br/>tek yazarlı küme bastırılır"]
        C2["llm/prompts.py<br/>gündem prompt'u doğruluk<br/>hükmünü yasaklar"]
        C3["clustering.py<br/>sıralama önce YAZAR ÇEŞİTLİLİĞİ,<br/>sonra gönderi sayısı"]
    end
```

Her ilkenin en az bir koruyucu testi vardır:
`backend/tests/test_ilke1_atif.py`, `test_ilke2_cekimserlik.py`,
`test_ilke3_cogulculuk.py`.

## 4. İstem enjeksiyonu savunma zinciri

Gönderi metni ve web içeriği **güvenilmeyen girdidir**. Saldırgan gönderiyi
yazan üçüncü kişidir; kurban onu özetleten okuyucudur.

```mermaid
flowchart LR
    X["Güvenilmeyen metin"] --> S1["1. sanitize.py<br/>görünmez karakter temizliği<br/>+ kalıp sinyali"]
    S1 --> S2["2. prompt_guard.py<br/>veri bloğu sınırlayıcıları<br/>+ sınırlayıcı kaçış"]
    S2 --> M["LLM"]
    M --> S3["3. output_guard.py<br/>URL / komut / talimat /<br/>sistem sızıntısı denetimi"]
    S3 -->|"temiz"| OK["Kullanıcıya göster"]
    S3 -->|"ihlal"| RED["Reddet<br/>refusal_reason=cikti_kisiti"]
    M -.->|"4. yetki kısıtı"| Y["Ajan yalnızca okur;<br/>yazma yetkisi yok,<br/>izin listesi dışına çıkmaz"]
```

Ölçüm: `eval/injection_suite.yaml` (40 senaryo, 9 saldırı türü) →
`eval/results/injection.md`.

## 5. Sağlayıcı soyutlaması

```mermaid
flowchart TB
    P["LLMProvider protokolü<br/>complete() / embed()"]
    P --> F["FakeProvider<br/>çıkarımsal, dış çağrısız<br/>(test + CI)"]
    P --> A["APIProvider<br/>Anthropic Messages"]
    P --> V["LocalVLLMProvider<br/>yerel OpenAI-uyumlu uç"]

    E["Embedder protokolü"] --> E1["SentenceTransformer<br/>multilingual-e5-base"]
    E --> E2["HashingEmbedder<br/>bağımlılıksız yedek"]
```

Kod hiçbir yerde belirli bir sağlayıcıya doğrudan bağlanmaz; geçiş tek dosyada
olur. Bu, raporun 6.2 (Teknik Sürdürülebilirlik) bölümünde iddia edilen dış
bağımlılıktan çıkabilme yeteneğinin kod karşılığıdır.

## 6. Veri akışı ve yönetişim sınırı

```mermaid
flowchart TB
    D1["Sentetik akış<br/>ml/data/synthetic_feed/feed.json"] --> D2["FeedRepository"]
    D2 -->|"to_service_dict()"| D3["Servis katmanı"]
    D2 -.->|"_eval_* alanları<br/>YALNIZCA buraya"| D4["ml/scripts/evaluate.py"]

    D5["Eğitim havuzuna girecek metin"] --> G1["governance/consent.py<br/>izin yoksa GİRMEZ"]
    G1 --> G2["governance/pii.py<br/>kişisel veri maskeleme"]
    G2 --> D6["ml/data/detection/*.jsonl"]

    D7["Toplulaştırma talebi"] --> G3["governance/aggregation.py<br/>k<20 ise grup HİÇ dönmez"]
    D8["Önbellek"] --> G4["governance/retention.py<br/>TTL + aktif süpürme"]

    style D4 fill:#fdf1e3
    style D3 fill:#e6f2ef
```

`_eval_*` alanları (YZ etiketi, enjeksiyon etiketi, olay kimliği) **hiçbir zaman**
servis katmanına veya prompt'a girmez. Bu, `backend/tests/test_eval_sizinti.py`
ile test edilerek garanti altına alınmıştır — iyi niyete bırakılmamıştır.

## 7. Dizin haritası

```
mihenk/
├── backend/app/
│   ├── main.py           FastAPI uç noktaları (ince katman)
│   ├── config.py         TÜM eşik değerleri (kodda gömülü sayı yok)
│   ├── models/           Pydantic şemaları — ilkeler tip düzeyinde
│   ├── llm/              Sağlayıcı soyutlaması + prompt'lar
│   ├── enrichment/       KATMAN 1
│   ├── summarize/        KATMAN 2 + kümeleme + atıf denetimi
│   ├── assistant/        Bağlam sınırlı soru-cevap (5 kapı)
│   ├── detection/        YZ sinyali + çekimserlik kuralları
│   ├── provenance/       C2PA / IPTC köken denetimi
│   ├── security/         İstem enjeksiyonu savunması
│   ├── governance/       PII, izin, k-eşiği, saklama sınırı
│   └── store/            TTL önbellek + akış deposu
├── ml/
│   ├── data/             Sentetik akış + tespit veri seti
│   ├── scripts/          Üretim, eğitim, ÖLÇÜM betikleri
│   └── artifacts/        Model ağırlıkları (git'e girmez)
├── frontend/src/         React + Vite + TypeScript + Tailwind
└── eval/                 Kırmızı takım kümesi + ölçüm çıktıları
```
