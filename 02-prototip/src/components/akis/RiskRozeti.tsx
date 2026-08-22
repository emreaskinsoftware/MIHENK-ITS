"use client";

import { useState } from "react";
import { ShieldAlert } from "lucide-react";
import type { HesapRiski } from "@/lib/analiz/hesapRiski";

export function RiskRozeti({ risk }: { risk: HesapRiski }) {
  const [acik, setAcik] = useState(false);
  if (risk.duzey === "dusuk") return null;

  const yuksek = risk.duzey === "yuksek";
  const renk = yuksek ? "var(--color-tehlike)" : "var(--color-uyari)";

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setAcik((v) => !v)}
        aria-expanded={acik}
        aria-label={`Hesap davranış işareti: ${yuksek ? "yüksek" : "orta"} düzey`}
        className="flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium"
        style={{ color: renk, background: `color-mix(in srgb, ${renk} 14%, transparent)` }}
      >
        <ShieldAlert size={12} />
        {yuksek ? "Davranış işareti" : "İnceleme"}
      </button>

      {acik && (
        <div className="absolute z-20 top-7 left-0 w-72 rounded-xl border border-cizgi bg-zemin p-3 shadow-xl">
          <p className="text-[13px] font-semibold mb-1.5">
            Hesap davranış işareti
            <span className="ml-1.5 font-normal text-metin-ikincil tabular-nums">
              ({risk.puan}/100)
            </span>
          </p>
          <ul className="flex flex-col gap-1 mb-2">
            {risk.bulgular.map((b) => (
              <li key={b} className="text-[12px] text-metin-ikincil flex gap-1.5">
                <span aria-hidden="true">·</span>{b}
              </li>
            ))}
          </ul>
          <p className="text-[11px] text-metin-sonuk border-t border-cizgi pt-2">
            Bu bir suçlama değildir. İçerik gizlenmez veya sıralaması düşürülmez;
            yalnızca bağlam sunulur. Değerlendirme size aittir.
          </p>
        </div>
      )}
    </div>
  );
}
