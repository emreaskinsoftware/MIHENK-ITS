"use client";

import { Plus } from "lucide-react";
import { Avatar } from "../layout/Avatar";
import { kullanicilar } from "@/lib/veri";

export function HikayeSeridi() {
  const hikayeliler = kullanicilar.filter((k) => k.rol === "uretici").slice(0, 12);

  return (
    <div className="border-b border-cizgi px-5 py-4">
      <ul className="flex gap-4 overflow-x-auto pb-1">
        <li className="shrink-0 flex flex-col items-center gap-1.5 w-[68px]">
          <button type="button" aria-label="Hikaye oluştur"
                  className="w-[58px] h-[58px] rounded-full border-2 border-mavi grid place-items-center
                             text-mavi hover:bg-mavi/10 transition-colors">
            <Plus size={24} />
          </button>
          <span className="text-[12px] text-metin-ikincil">Yeni</span>
        </li>
        {hikayeliler.map((k) => (
          <li key={k.id} className="shrink-0 flex flex-col items-center gap-1.5 w-[68px]">
            <button type="button" aria-label={`${k.kullanici_adi} hikayesi`}>
              <Avatar ad={k.kullanici_adi} boyut={54} halka />
            </button>
            <span className="text-[12px] text-metin-ikincil truncate w-full text-center">
              {k.kullanici_adi.split("_")[0]}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
