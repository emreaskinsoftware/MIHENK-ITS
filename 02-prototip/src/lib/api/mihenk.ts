/**
 * MİHENK backend istemcisi.
 *
 * Bu katman, Next.js arayüzünü ekip arkadaşımızın FastAPI servisine bağlar.
 * Sözleşme: backend/app/models/*.py (Pydantic şemaları)
 *
 * Tasarım notu — neden ayrı bir istemci katmanı:
 * Backend'in üç ilkesi (atıf zorunluluğu, çekimserlik, çoğulculuk) yanıt
 * ŞEMASINDA kodlanmıştır. Arayüz bu alanları yok sayarsa ilkeler görünmez
 * kalır. Bu yüzden istemci, alanları olduğu gibi taşır; yorumlamaz.
 */

const TABAN =
  process.env.NEXT_PUBLIC_MIHENK_API ?? "http://localhost:8000";

/** Özet cümlesi — her cümle en az bir kaynağa bağlıdır (atıf zorunluluğu) */
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
  /** Çoğulculuk: tek kaynağa dayandığı için bastırılan küme sayısı */
  single_source_cluster_count: number;
  skipped_post_count: number;
  latency_ms: number;
  cache_hit_ratio: number;
}

export interface TespitSonucu {
  label: string | null;
  confidence: number | null;
  /** Çekimserlik: sistem hüküm vermediyse true */
  abstained: boolean;
  reason: string | null;
  token_count: number;
  length_bucket: string | null;
}

export interface AsistanYaniti {
  answer: string;
  source_post_ids: string[];
  /** Çekimserlik: asistan yanıtlamayı reddettiyse true */
  refused: boolean;
  refusal_reason: string | null;
  latency_ms: number;
}

async function istek<T>(yol: string, secenekler?: RequestInit): Promise<T | null> {
  try {
    const yanit = await fetch(`${TABAN}${yol}`, {
      ...secenekler,
      headers: { "content-type": "application/json", ...secenekler?.headers },
      signal: AbortSignal.timeout(20000),
    });
    if (!yanit.ok) return null;
    return (await yanit.json()) as T;
  } catch {
    // Backend ayakta değilse arayüz yerel motora düşer; gösterim kesilmez.
    return null;
  }
}

export const mihenkApi = {
  /** Backend erişilebilir mi */
  saglik: () => istek<{ status?: string }>("/api/saglik"),

  ozetle: (kategori: string, gonderiIdler?: string[]) =>
    istek<OzetYaniti>("/api/ozetle", {
      method: "POST",
      body: JSON.stringify({ category: kategori, post_ids: gonderiIdler }),
    }),

  sor: (soru: string, gonderiId?: string) =>
    istek<AsistanYaniti>("/api/sor", {
      method: "POST",
      body: JSON.stringify({ question: soru, post_id: gonderiId }),
    }),

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
