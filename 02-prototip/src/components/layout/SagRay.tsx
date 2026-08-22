"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronDown, ChevronRight, Hash, PenLine, Search } from "lucide-react";
import { Avatar } from "./Avatar";
import { populerEtiketler } from "@/lib/veri";
import { sayiBicimle } from "@/lib/bicim";

export function SagRay() {
  const etiketler = populerEtiketler();
  const yonlendirici = useRouter();
  const [sorgu, setSorgu] = useState("");

  function gonder(e: React.FormEvent) {
    e.preventDefault();
    if (sorgu.trim().length >= 2) yonlendirici.push(`/ara?q=${encodeURIComponent(sorgu.trim())}`);
  }

  return (
    <aside className="w-[360px] shrink-0 h-screen sticky top-0 py-6 px-5 flex flex-col gap-5 max-lg:hidden">
      <div className="flex items-center gap-3">
        <form onSubmit={gonder} className="flex-1 relative">
          <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-metin-ikincil" />
          <label htmlFor="arama" className="sr-only">Arama yap</label>
          <input
            id="arama"
            value={sorgu}
            onChange={(e) => setSorgu(e.target.value)}
            placeholder="Arama yap"
            className="w-full rounded-full bg-transparent border border-mavi/60 pl-11 pr-4 py-2.5
                       text-[15px] placeholder:text-metin-ikincil outline-none
                       focus:border-mavi"
          />
        </form>
        <button type="button" className="flex items-center gap-1" aria-label="Hesap menüsü">
          <Avatar ad="mihenk kullanici" boyut={38} />
          <ChevronDown size={16} className="text-metin-ikincil" />
        </button>
      </div>

      <section className="bg-kart rounded-[var(--radius-kart)] p-5" aria-labelledby="populer-baslik">
        <header className="flex items-center justify-between mb-4">
          <h2 id="populer-baslik" className="text-[20px] font-bold">Popüler</h2>
          <button type="button" className="flex items-center gap-0.5 text-[13px] text-metin-ikincil hover:text-metin">
            Tümünü gör <ChevronRight size={14} />
          </button>
        </header>
        <ul className="flex flex-col gap-4">
          {etiketler.map((e) => (
            <li key={e.etiket} className="flex items-start gap-3">
              <Hash size={20} className="text-metin-ikincil mt-0.5 shrink-0" />
              <div className="min-w-0">
                <p className="font-semibold text-[15px] truncate">{e.etiket}</p>
                <p className="text-[13px] text-metin-ikincil">{sayiBicimle(e.sayi)} gönderi</p>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <div className="mt-auto">
        <div className="bg-kart rounded-t-[var(--radius-kart)] px-5 py-3 flex items-center justify-between">
          <span className="font-semibold">Mesajlar</span>
          <PenLine size={18} className="text-metin-ikincil" />
        </div>
      </div>
    </aside>
  );
}
