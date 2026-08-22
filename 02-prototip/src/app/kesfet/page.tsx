"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Hash, Search } from "lucide-react";
import { UstSekmeler } from "@/components/layout/UstSekmeler";
import { GonderiKarti } from "@/components/akis/GonderiKarti";
import { Avatar } from "@/components/layout/Avatar";
import { OnayliRozet } from "@/components/layout/OnayliRozet";
import { akisGetir, kullanicilar, olaylariGetir } from "@/lib/veri";
import { goreliZaman, sayiBicimle } from "@/lib/bicim";
import { KATEGORI_ETIKET } from "@/lib/tipler";

const SEKMELER = ["Keşfet", "Trendler", "Etiketler", "Haberler", "Senin İçin"] as const;

export default function KesfetSayfasi() {
  const [aktif, setAktif] = useState<(typeof SEKMELER)[number]>("Keşfet");
  const [sorgu, setSorgu] = useState("");
  const yonlendirici = useRouter();
  const akis = akisGetir();
  const olaylar = olaylariGetir();

  return (
    <>
      <UstSekmeler sekmeler={SEKMELER} aktif={aktif} degistir={setAktif} />

      <div className="px-5 py-4 border-b border-cizgi">
        <form onSubmit={(e) => { e.preventDefault(); if (sorgu.trim().length >= 2) yonlendirici.push(`/ara?q=${encodeURIComponent(sorgu.trim())}`); }} className="relative">
          <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-metin-ikincil" />
          <label htmlFor="kesfet-arama" className="sr-only">Etiketleri ve kullanıcıları ara</label>
          <input
            id="kesfet-arama"
            value={sorgu}
            onChange={(e) => setSorgu(e.target.value)}
            placeholder="Etiketleri ve kullanıcıları ara..."
            className="w-full rounded-full bg-kart border border-cizgi pl-11 pr-4 py-3
                       text-[15px] placeholder:text-metin-ikincil outline-none focus:border-mavi"
          />
        </form>
      </div>

      {(aktif === "Keşfet" || aktif === "Trendler") && (
        <div>
          {akis
            .filter((g) => (aktif === "Trendler" ? g.begeni > 12 : true))
            .slice(0, 25)
            .map((g) => <GonderiKarti key={g.id} gonderi={g} />)}
        </div>
      )}

      {aktif === "Etiketler" && (
        <ul>
          {olaylar.map((o) => (
            <li key={o.olayId} className="px-5 py-4 border-b border-cizgi hover:bg-kart/40">
              <div className="flex items-start gap-3">
                <Hash size={20} className="text-metin-ikincil mt-0.5 shrink-0" />
                <div className="min-w-0">
                  <p className="font-semibold text-[16px]">
                    {o.baslik.split(" ").slice(0, 3).join("")}
                  </p>
                  <p className="text-[13px] text-metin-ikincil mt-0.5">
                    Son 2 gündeki {o.gonderiler.length} gönderi · {KATEGORI_ETIKET[o.kategori]}
                  </p>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      {aktif === "Haberler" && (
        <ul>
          {olaylar.map((o) => {
            const ilk = o.gonderiler[0];
            return (
              <li key={o.olayId} className="px-5 py-4 border-b border-cizgi hover:bg-kart/40">
                <div className="flex items-center gap-2 text-[13px] text-metin-ikincil mb-1.5">
                  <span>@{ilk.yazar.kullanici_adi}</span>
                  <span>·</span>
                  <time dateTime={ilk.zaman}>{goreliZaman(ilk.zaman)}</time>
                </div>
                <h2 className="font-bold text-[17px] leading-snug">{o.baslik}</h2>
                <p className="text-[14px] text-metin-ikincil mt-1.5 line-clamp-2">{ilk.metin}</p>
                <p className="text-[13px] text-metin-ikincil mt-2">
                  Kaynak: {o.gonderiler.length} gönderi, {new Set(o.gonderiler.map(g => g.yazar_id)).size} hesap
                </p>
              </li>
            );
          })}
        </ul>
      )}

      {aktif === "Senin İçin" && (
        <ul>
          {kullanicilar
            .filter((k) => k.rol === "uretici")
            .slice(0, 12)
            .map((k) => (
              <li key={k.id} className="px-5 py-4 border-b border-cizgi flex items-center gap-3">
                <Avatar ad={k.kullanici_adi} boyut={48} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <span className="font-bold truncate">{k.kullanici_adi.replace(/_/g, " ")}</span>
                    {k.dogrulanmis && <OnayliRozet />}
                  </div>
                  <p className="text-[14px] text-metin-ikincil truncate">@{k.kullanici_adi}</p>
                  <p className="text-[13px] text-metin-sonuk mt-0.5">
                    {sayiBicimle(k.takipci_sayisi)} takipçi
                  </p>
                </div>
                <button type="button"
                        className="gradyan-marka text-white font-semibold rounded-full px-5 py-2 text-[14px]
                                   hover:brightness-110 transition shrink-0">
                  Takip Et
                </button>
              </li>
            ))}
        </ul>
      )}
    </>
  );
}
