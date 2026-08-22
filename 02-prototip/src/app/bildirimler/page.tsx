"use client";

import { useState } from "react";
import { UstSekmeler } from "@/components/layout/UstSekmeler";
import { Avatar } from "@/components/layout/Avatar";
import { OnayliRozet } from "@/components/layout/OnayliRozet";
import { SayfaBasligi } from "@/components/layout/SayfaBasligi";
import { akisGetir } from "@/lib/veri";
import { goreliZaman } from "@/lib/bicim";

const SEKMELER = ["Tümü", "Etkileşimler"] as const;

export default function BildirimlerSayfasi() {
  const [aktif, setAktif] = useState<(typeof SEKMELER)[number]>("Tümü");
  const bildirimler = akisGetir()
    .filter((g) => (aktif === "Etkileşimler" ? g.begeni > 20 : true))
    .slice(0, 20);

  return (
    <>
      <UstSekmeler sekmeler={SEKMELER} aktif={aktif} degistir={setAktif} />
      <SayfaBasligi baslik="Bildirimler" />
      <ul>
        {bildirimler.map((g) => (
          <li key={g.id} className="px-5 py-4 border-b border-cizgi hover:bg-kart/40">
            <div className="flex gap-3">
              <Avatar ad={g.yazar.kullanici_adi} boyut={40} />
              <div className="min-w-0 flex-1">
                <p className="text-[15px]">
                  <span className="font-bold">{g.yazar.kullanici_adi.replace(/_/g, " ")}</span>
                  {g.yazar.dogrulanmis && (
                    <span className="inline-flex align-middle mx-1"><OnayliRozet boyut={15} /></span>
                  )}
                  <span className="text-metin-ikincil"> bir gönderi paylaştı</span>
                  <span className="text-metin-ikincil"> · {goreliZaman(g.zaman)}</span>
                </p>
                <p className="text-[15px] text-metin-ikincil mt-1.5 line-clamp-3">{g.metin}</p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </>
  );
}
