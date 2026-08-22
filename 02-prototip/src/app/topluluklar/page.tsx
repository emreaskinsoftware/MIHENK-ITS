"use client";

import { useState } from "react";
import { Plus, Search } from "lucide-react";
import { UstSekmeler } from "@/components/layout/UstSekmeler";
import { olaylariGetir } from "@/lib/veri";
import { KATEGORI_ETIKET } from "@/lib/tipler";

const SEKMELER = ["Topluluklarım", "Keşfet"] as const;

const KAPAK_RENK = [
  ["#2e90fa", "#22c7e8"], ["#7c5cf0", "#a78bfa"], ["#f5a524", "#f97316"],
  ["#22c55e", "#14b8a6"], ["#f4525f", "#ec4899"], ["#0ea5e9", "#6366f1"],
];

export default function TopluluklarSayfasi() {
  const [aktif, setAktif] = useState<(typeof SEKMELER)[number]>("Keşfet");
  const olaylar = olaylariGetir();

  return (
    <>
      <UstSekmeler sekmeler={SEKMELER} aktif={aktif} degistir={setAktif} />

      <div className="flex items-center gap-3 px-5 py-4">
        <h2 className="text-[19px] font-bold flex-1">
          {aktif === "Keşfet" ? "Yeni topluluklar keşfet:" : "Topluluklarım"}
        </h2>
        <button type="button" aria-label="Topluluk ara"
                className="p-2 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover">
          <Search size={18} />
        </button>
        <button type="button" aria-label="Topluluk oluştur"
                className="p-2 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover">
          <Plus size={18} />
        </button>
      </div>

      <div className="grid grid-cols-2 max-xl:grid-cols-1 gap-4 px-5 pb-8">
        {olaylar.map((o, i) => {
          const [a, b] = KAPAK_RENK[i % KAPAK_RENK.length];
          return (
            <article key={o.olayId} className="rounded-xl overflow-hidden bg-kart hover:bg-yukseltilmis transition-colors">
              <div className="h-24" style={{ backgroundImage: `linear-gradient(120deg, ${a}, ${b})` }} />
              <div className="p-4">
                <h3 className="font-semibold text-[15px] leading-snug line-clamp-2">{o.baslik}</h3>
                <p className="text-[13px] text-metin-ikincil mt-1.5">
                  {new Set(o.gonderiler.map(g => g.yazar_id)).size} üye · {KATEGORI_ETIKET[o.kategori]}
                </p>
              </div>
            </article>
          );
        })}
      </div>
    </>
  );
}
