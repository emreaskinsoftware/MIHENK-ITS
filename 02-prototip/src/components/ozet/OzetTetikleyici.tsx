"use client";

import { Sparkles } from "lucide-react";

export function OzetTetikleyici({ ac }: { ac: () => void }) {
  return (
    <div className="px-5 py-3 border-b border-cizgi">
      <button
        type="button"
        onClick={ac}
        className="w-full flex items-center gap-3 rounded-full px-5 py-3
                   bg-mihenk/10 hover:bg-mihenk/15 ring-1 ring-mihenk/25
                   transition-colors text-left"
      >
        <span className="grid place-items-center w-8 h-8 rounded-full bg-mihenk/20 shrink-0">
          <Sparkles size={17} className="text-mihenk" />
        </span>
        <span className="min-w-0">
          <span className="block font-semibold text-[15px]">Gündemi özetle</span>
          <span className="block text-[13px] text-metin-ikincil truncate">
            Kaydırmadan gündemi kavra — ülke, spor, teknoloji ve kişisel akış
          </span>
        </span>
      </button>
    </div>
  );
}
