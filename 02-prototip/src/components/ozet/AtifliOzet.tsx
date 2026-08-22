"use client";

import { useState } from "react";
import { FileText, Info, ShieldCheck } from "lucide-react";
import type { OzetYaniti } from "@/lib/api/mihenk";

/**
 * Atıflı özet görünümü.
 *
 * Backend'in üç ilkesini kullanıcıya GÖRÜNÜR kılar:
 *   1. Atıf zorunluluğu → her cümlenin yanında kaynak sayısı rozeti
 *   2. Çekimserlik      → silinen cümle sayısı gizlenmez, açıkça yazılır
 *   3. Çoğulculuk       → tek kaynaklı küme bastırıldıysa belirtilir
 */
export function AtifliOzet({ ozet }: { ozet: OzetYaniti }) {
  const [acikCumle, setAcikCumle] = useState<number | null>(null);

  return (
    <div>
      <p className="text-[15px] leading-[1.7]">
        {ozet.sentences.map((c, i) => (
          <span key={i}>
            <span
              className={`transition-colors ${acikCumle === i ? "bg-mihenk/15 rounded" : ""}`}
            >
              {c.text}
            </span>
            <button
              type="button"
              onClick={() => setAcikCumle((v) => (v === i ? null : i))}
              aria-expanded={acikCumle === i}
              aria-label={`Bu cümlenin ${c.source_post_ids.length} kaynağını göster`}
              className="inline-flex items-center gap-0.5 align-super mx-1 rounded px-1
                         text-[11px] font-medium text-mihenk hover:bg-mihenk/10"
            >
              <FileText size={10} />
              {c.source_post_ids.length}
            </button>{" "}
          </span>
        ))}
      </p>

      {acikCumle !== null && (
        <div className="mt-2 rounded-lg bg-yukseltilmis px-3 py-2">
          <p className="text-[12px] font-medium text-metin-ikincil mb-1">
            Bu cümlenin dayandığı gönderiler
          </p>
          <ul className="flex flex-wrap gap-1.5">
            {ozet.sentences[acikCumle].source_post_ids.map((id) => (
              <li key={id}>
                <a
                  href={`/gonderi/${id}`}
                  className="inline-block rounded-full bg-zemin px-2.5 py-1 text-[11px]
                             font-mono text-mavi hover:underline"
                >
                  {id.slice(0, 8)}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[12px] text-metin-ikincil">
        <span className="flex items-center gap-1.5">
          <ShieldCheck size={13} className="text-basari" />
          Her cümle kaynağa bağlı
        </span>
        <span>{ozet.cluster_count} konu kümesi</span>

        {ozet.dropped_sentence_count > 0 && (
          <span className="flex items-center gap-1.5 text-uyari">
            <Info size={13} />
            {ozet.dropped_sentence_count} cümle atıf denetiminden geçemedi, silindi
          </span>
        )}

        {ozet.single_source_cluster_count > 0 && (
          <span className="flex items-center gap-1.5 text-uyari">
            <Info size={13} />
            {ozet.single_source_cluster_count} küme tek kaynaklı olduğu için bastırıldı
          </span>
        )}
      </div>
    </div>
  );
}
