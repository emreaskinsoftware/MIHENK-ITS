/**
 * MİHENK backend istemcisi.
 *
 * Bu katman, Next.js arayüzünü FastAPI servisine bağlar.
 * Sözleşme: `backend/app/main.py` (uç noktalar) + `backend/app/models/*.py`
 * (Pydantic şemaları). Alan adları TÜRKÇE değil, backend'deki hâliyle
 * taşınır — çeviri yapmak, sözleşmenin iki yerde yaşamasına ve sessizce
 * ayrışmasına yol açar.
 *
 * --- TASARIM KARARI: "SUSTU" ile "ÇÖKTÜ" AYNI ŞEY DEĞİLDİR ---------------
 * Bu istemcinin ilk sürümü her başarısızlıkta `null` dönüyordu ve arayüz
 * `null` görünce yerel motora düşüyordu. Bu, ilkeli bir sessizliği uydurma
 * bir cevapla değiştirmek demekti: backend "emin değilim, hüküm vermiyorum"
 * dediğinde (İlke 2) arayüz bunu "backend yok" sanıp yerel bir sonuç
 * uyduruyordu.
 *
 * Artık sonuç ayrıştırılmış bir tip: `veri` geldiyse backend KONUŞTU ve
 * söylediği aynen gösterilir — çekimser kaldıysa çekimserliği gösterilir.
 * `durum` alanı yalnızca gerçekten ulaşılamadığında "erisilemedi" olur.
 */

const TABAN = process.env.NEXT_PUBLIC_MIHENK_API ?? "http://localhost:8000";

/** İstek zaman aşımı. Tespit modeli ilk çağrıda GPU'ya yüklenebilir. */
const ZAMAN_ASIMI_MS = 20_000;

/** Özet cümlesi — her cümle en az bir kaynağa bağlıdır (İlke 1) */
export interface OzetCumlesi {
  text: string;
  source_post_ids: string[];
}

export interface OzetYaniti {
  category: string;
  sentences: OzetCumlesi[];
  cluster_count: number;
  /** Atıf denetiminden geçemediği için SİLİNEN cümle sayısı */
  dropped_sentence_count: number;
  /** Çoğulculuk: tek kaynağa dayandığı için bastırılan küme sayısı (İlke 3) */
  single_source_cluster_count: number;
  skipped_post_count: number;
  latency_ms: number;
  cache_hit_ratio: number;
}

export interface TespitSonucu {
  /** null ise arayüz HİÇBİR ROZET göstermez (spec 6.9) */
  label: "yz_olasi" | "insan_olasi" | null;
  confidence: number | null;
  /** Çekimserlik: sistem hüküm vermediyse true (İlke 2) */
  abstained: boolean;
  /** "metin_cok_kisa" | "belirsiz" | "model_yok" */
  reason: string | null;
  token_count: number;
  length_bucket: "K1" | "K2" | "K3" | null;
}

export interface AsistanYaniti {
  answer: string;
  source_post_ids: string[];
  /** Çekimserlik: asistan yanıtlamayı reddettiyse true */
  refused: boolean;
  refusal_reason: string | null;
  latency_ms: number;
}

export interface SaglikYaniti {
  /** Backend "calisiyor" döner — alan adı Türkçe, backend'deki hâliyle */
  durum: string;
  llm_saglayici: string;
  gomme_modeli: string;
  tespit_modeli: string | null;
}

/**
 * Ayrıştırılmış sonuç. `durum` üç değer alır:
 *   "tamam"        -> backend yanıt verdi, `veri` dolu
 *   "erisilemedi"  -> ağ/zaman aşımı/servis kapalı; yerel yedeğe düşülebilir
 *   "hata"         -> backend yanıt verdi ama hata kodu döndü (sözleşme
 *                     uyuşmazlığı veya doğrulama hatası). Yerel yedeğe
 *                     DÜŞÜLMEZ; bu bir hatadır ve görünür olmalıdır.
 */
export type Sonuc<T> =
  | { durum: "tamam"; veri: T }
  | { durum: "erisilemedi" }
  | { durum: "hata"; kod: number };

async function istek<T>(yol: string, secenekler?: RequestInit): Promise<Sonuc<T>> {
  try {
    const yanit = await fetch(`${TABAN}${yol}`, {
      ...secenekler,
      headers: { "content-type": "application/json", ...secenekler?.headers },
      signal: AbortSignal.timeout(ZAMAN_ASIMI_MS),
    });
    if (!yanit.ok) return { durum: "hata", kod: yanit.status };
    return { durum: "tamam", veri: (await yanit.json()) as T };
  } catch {
    // Ağ hatası / zaman aşımı / servis kapalı.
    return { durum: "erisilemedi" };
  }
}

export const mihenkApi = {
  /** Backend erişilebilir mi ve hangi modellerle çalışıyor */
  saglik: () => istek<SaglikYaniti>("/api/saglik"),

  /**
   * Kategori özeti.
   *
   * DİKKAT — alan adları: backend `unread_post_ids` bekler, `post_ids` değil.
   * Yanlış alan adı Pydantic tarafından SESSİZCE yok sayılır ve özet, istenen
   * gönderiler yerine tüm akış üzerinden üretilir. Hata alınmaz, yanlış sonuç
   * alınır — bu yüzden alan adı burada birebir yazılıdır.
   */
  ozetle: (kategori: "gundem" | "spor" | "kisisel", okunmamisIdler?: string[], kullaniciId = "demo") =>
    istek<OzetYaniti>("/api/ozetle", {
      method: "POST",
      body: JSON.stringify({
        user_id: kullaniciId,
        category: kategori,
        unread_post_ids: okunmamisIdler ?? null,
      }),
    }),

  /** Gönderi bağlamında soru-cevap. `gonderiId` ZORUNLUDUR (backend şeması). */
  sor: (gonderiId: string, soru?: string) =>
    istek<AsistanYaniti>("/api/sor", {
      method: "POST",
      body: JSON.stringify({ post_id: gonderiId, question: soru ?? null }),
    }),

  /**
   * Serbest metin için YZ sinyali — kimlik gerektirmez.
   *
   * NEDEN KİMLİKSİZ UÇ: Bu arayüzün simülasyon verisi backend'in akışıyla
   * aynı değil; gönderi kimlikleri uyuşmuyor (`6713e74b02d6` ↔ `p0411`).
   * Kimliğe dayalı `/api/tespit/{id}` buradan çağrılırsa her istek 404 döner.
   * Ayrıca kullanıcının henüz paylaşmadığı taslağın kimliği zaten yoktur.
   */
  tespitMetin: (metin: string) =>
    istek<TespitSonucu>("/api/tespit", {
      method: "POST",
      body: JSON.stringify({ text: metin }),
    }),

  /** Kimliğe dayalı tespit — yalnızca backend'in KENDİ akışı için geçerli. */
  tespit: (gonderiId: string) =>
    istek<TespitSonucu>(`/api/tespit/${encodeURIComponent(gonderiId)}`),

  koken: (gonderiId: string) =>
    istek<Record<string, unknown>>(`/api/koken/${encodeURIComponent(gonderiId)}`),

  itiraz: (gonderiId: string, gerekce: string) =>
    istek<Record<string, unknown>>("/api/itiraz", {
      method: "POST",
      body: JSON.stringify({ post_id: gonderiId, reason: gerekce }),
    }),
};
