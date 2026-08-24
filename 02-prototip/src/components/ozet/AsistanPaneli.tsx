"use client";

import { useState } from "react";
import { Loader2, Send, Sparkles, X } from "lucide-react";
import type { AkisOgesi } from "@/lib/tipler";

const HAZIR_SORULAR = [
  "Bu gönderi ne anlatıyor?",
  "Bu konuda başka hangi görüşler var?",
  "Bu iddianın kaynağı ne?",
];

export function AsistanPaneli({
  gonderi, kapat,
}: { gonderi: AkisOgesi; kapat: () => void }) {
  const [gecmis, setGecmis] = useState<{ rol: "kullanici" | "asistan"; metin: string }[]>([]);
  const [girdi, setGirdi] = useState("");
  const [yukleniyor, setYukleniyor] = useState(false);

  async function sor(soru: string) {
    if (!soru.trim() || yukleniyor) return;
    setGecmis((g) => [...g, { rol: "kullanici", metin: soru }]);
    setGirdi("");
    setYukleniyor(true);
    try {
      const y = await fetch("/api/asistan", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ gonderiId: gonderi.id, soru }),
      });
      const v = await y.json();
      setGecmis((g) => [...g, { rol: "asistan", metin: v.yanit }]);
    } catch {
      setGecmis((g) => [...g, { rol: "asistan", metin: "Yanıt alınamadı." }]);
    } finally {
      setYukleniyor(false);
    }
  }

  return (
    <div className="mt-3 rounded-xl border border-cizgi bg-zemin p-4">
      <header className="flex items-center gap-2.5 mb-3">
        <Sparkles size={17} className="text-mihenk shrink-0" />
        <h3 className="font-semibold text-[14px]">MİHENK Asistan</h3>
        <span className="text-[12px] text-metin-sonuk">bu gönderinin bağlamında</span>
        <button type="button" onClick={kapat} aria-label="Asistan panelini kapat"
                className="ml-auto p-1 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover">
          <X size={16} />
        </button>
      </header>

      {gecmis.length === 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {HAZIR_SORULAR.map((s) => (
            <button key={s} type="button" onClick={() => sor(s)}
                    className="rounded-full bg-yukseltilmis hover:bg-hover px-3 py-1.5 text-[13px] transition-colors">
              {s}
            </button>
          ))}
        </div>
      )}

      {gecmis.length > 0 && (
        <ul className="flex flex-col gap-3 mb-3 max-h-72 overflow-y-auto">
          {gecmis.map((m, i) => (
            <li key={i} className={m.rol === "kullanici" ? "text-right" : ""}>
              <span className={`inline-block rounded-2xl px-3.5 py-2 text-[14px] leading-relaxed max-w-[85%] text-left
                                ${m.rol === "kullanici"
                                  ? "bg-mavi-koyu text-white"
                                  : "bg-yukseltilmis"}`}>
                {m.metin}
              </span>
            </li>
          ))}
          {yukleniyor && (
            <li className="flex items-center gap-2 text-[14px] text-metin-ikincil">
              <Loader2 size={15} className="animate-spin" /> Yanıt hazırlanıyor…
            </li>
          )}
        </ul>
      )}

      <form onSubmit={(e) => { e.preventDefault(); sor(girdi); }} className="flex items-center gap-2">
        <label htmlFor={`asistan-${gonderi.id}`} className="sr-only">Asistana soru sor</label>
        <input
          id={`asistan-${gonderi.id}`}
          value={girdi}
          onChange={(e) => setGirdi(e.target.value)}
          placeholder="Bu gönderi hakkında sor…"
          className="flex-1 rounded-full bg-kart border border-cizgi px-4 py-2.5 text-[14px]
                     placeholder:text-metin-sonuk outline-none focus:border-mavi"
        />
        <button type="submit" disabled={!girdi.trim() || yukleniyor} aria-label="Gönder"
                className="p-2.5 rounded-full bg-mihenk-koyu text-white disabled:opacity-40 hover:brightness-110 transition">
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}
