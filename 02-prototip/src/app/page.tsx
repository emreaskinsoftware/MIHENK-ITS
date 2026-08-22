"use client";

import { useState } from "react";
import { Olusturucu } from "@/components/akis/Olusturucu";
import { HikayeSeridi } from "@/components/akis/HikayeSeridi";
import { GonderiKarti } from "@/components/akis/GonderiKarti";
import { OzetPaneli } from "@/components/ozet/OzetPaneli";
import { OzetTetikleyici } from "@/components/ozet/OzetTetikleyici";
import { akisGetir } from "@/lib/veri";

export default function AnaSayfa() {
  const [ozetAcik, setOzetAcik] = useState(true);
  const [sekme, setSekme] = useState<"akis" | "medya">("akis");
  const akis = akisGetir(30);

  return (
    <>
      <div className="sticky top-0 z-20 bg-zemin/80 backdrop-blur-md border-b border-cizgi">
        <div role="tablist" aria-label="Akış görünümü" className="flex">
          <button role="tab" aria-selected={sekme === "akis"} onClick={() => setSekme("akis")}
                  className={`flex-1 py-4 relative ${sekme === "akis" ? "font-semibold text-metin" : "font-medium text-metin-ikincil hover:text-metin"}`}>
            Akış
            {sekme === "akis" && <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[70%] h-[3px] rounded-full bg-mavi" />}
          </button>
          <button role="tab" aria-selected={sekme === "medya"} onClick={() => setSekme("medya")}
                  className={`flex-1 py-4 relative ${sekme === "medya" ? "font-semibold text-metin" : "font-medium text-metin-ikincil hover:text-metin"}`}>
            Medya
            {sekme === "medya" && <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[70%] h-[3px] rounded-full bg-mavi" />}
          </button>
        </div>
      </div>

      <Olusturucu />
      <HikayeSeridi />

      {ozetAcik
        ? <OzetPaneli kapat={() => setOzetAcik(false)} />
        : <OzetTetikleyici ac={() => setOzetAcik(true)} />}

      <div>
        {akis
          .filter((g) => (sekme === "medya" ? g.gorsel_var : true))
          .map((g) => <GonderiKarti key={g.id} gonderi={g} />)}
      </div>
    </>
  );
}
