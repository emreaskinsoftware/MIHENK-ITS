/**
 * Arka uç istemcisi ve tip tanımları.
 *
 * TİPLER ARKA UÇ ŞEMALARIYLA BİREBİR EŞLEŞİR. Özellikle dikkat:
 *   - `DetectionResult.label` null olabilir. Null = ÇEKİMSERLİK; arayüz hiçbir
 *     rozet göstermez (spec 6.9 tasarım kuralı).
 *   - `SummarySentence.source_post_ids` her zaman doludur; arka uç atıfsız
 *     cümleyi zaten silmiştir (İlke 1). Ön yüz bu kontrolü TEKRARLAMAZ —
 *     denetim servis katmanının işidir, UI'ya temiz veri gelir.
 */

const TEMEL = "/api";

export type Kategori = "gundem" | "spor" | "kisisel";

export interface MedyaRef {
  media_id: string;
  kind: string;
  provenance_manifest: Record<string, unknown> | null;
}

export interface Gonderi {
  id: string;
  author_id: string;
  text: string;
  created_at: string;
  category: Kategori;
  media: MedyaRef[];
  atomic_summary: string | null;
  topic_label: string | null;
}

export interface OzetCumlesi {
  text: string;
  source_post_ids: string[];
}

export interface OzetYaniti {
  category: string;
  sentences: OzetCumlesi[];
  cluster_count: number;
  dropped_sentence_count: number;
  latency_ms: number;
  single_source_cluster_count: number;
  skipped_post_count: number;
  cache_hit_ratio: number;
}

export interface AsistanYaniti {
  answer: string;
  source_post_ids: string[];
  refused: boolean;
  refusal_reason: string | null;
  latency_ms: number;
}

export interface TespitSonucu {
  /** null = çekimserlik: arayüzde hiçbir rozet gösterilmez. */
  label: "insan_olasi" | "yz_olasi" | null;
  confidence: number | null;
  abstained: boolean;
  reason: string | null;
  token_count: number;
  length_bucket: "K1" | "K2" | "K3" | null;
}

export interface KokenSonucu {
  media_id: string;
  status: "yz_uretimi" | "kamera_kaydi" | "belirsiz";
  /** false ise hiçbir gösterge çizilmez — belirsizlik rozete dönüştürülmez. */
  display: boolean;
  evidence: string | null;
  label: string | null;
}

async function istek<T>(yol: string, secenekler?: RequestInit): Promise<T> {
  const yanit = await fetch(`${TEMEL}${yol}`, {
    headers: { "Content-Type": "application/json" },
    ...secenekler,
  });
  if (!yanit.ok) {
    throw new Error(`${yanit.status} ${yanit.statusText}`);
  }
  return (await yanit.json()) as T;
}

export const api = {
  saglik: () => istek<Record<string, unknown>>("/saglik"),

  akis: (kategori?: Kategori, limit = 60) =>
    istek<Gonderi[]>(`/akis?limit=${limit}${kategori ? `&category=${kategori}` : ""}`),

  ozetle: (kategori: Kategori, okunmamis?: string[]) =>
    istek<OzetYaniti>("/ozetle", {
      method: "POST",
      body: JSON.stringify({ category: kategori, unread_post_ids: okunmamis ?? null }),
    }),

  sor: (postId: string, soru?: string) =>
    istek<AsistanYaniti>("/sor", {
      method: "POST",
      body: JSON.stringify({ post_id: postId, question: soru ?? null }),
    }),

  tespit: (postId: string) => istek<TespitSonucu>(`/tespit/${postId}`),

  koken: (postId: string) =>
    istek<{ post_id: string; media: KokenSonucu[] }>(`/koken/${postId}`),

  itiraz: (postId: string, gerekce: string) =>
    istek<{ kaydedildi: boolean; mesaj: string }>("/itiraz", {
      method: "POST",
      body: JSON.stringify({ post_id: postId, reason: gerekce }),
    }),

  itirazDurumu: (postId: string) =>
    istek<{ itiraz_var: boolean; adet: number }>(`/itiraz/${postId}`),
};
