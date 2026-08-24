"use client";

import { useState } from "react";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTema } from "./TemaSaglayici";
import {
  Bell, Bookmark, Cloud, Compass, Home, MessagesSquare,
  PenLine, Play, Rocket, SlidersHorizontal, Star, Moon, Sun, ClipboardList, LineChart,
} from "lucide-react";

const MENU = [
  { ad: "Ana Sayfa", ikon: Home, yol: "/" },
  { ad: "Bildirimler", ikon: Bell, yol: "/bildirimler", rozet: 86 },
  { ad: "Mesajlar", ikon: MessagesSquare, yol: "/mesajlar" },
  { ad: "Keşfet", ikon: Compass, yol: "/kesfet" },
  { ad: "Nod Oyna", ikon: Cloud, yol: "/nod", pasif: true },
  { ad: "Topluluklar", ikon: Star, yol: "/topluluklar" },
  { ad: "Kaydedilenler", ikon: Bookmark, yol: "/kaydedilenler" },
  { ad: "Beğeniler", ikon: Rocket, yol: "/begeniler" },
  { ad: "İçerik Üretici", ikon: LineChart, yol: "/uretici" },
  { ad: "Ayarlar", ikon: SlidersHorizontal, yol: "/ayarlar" },
  { ad: "TEKNOFEST Kayıt", ikon: ClipboardList, yol: "/teknofest" },
];

export function Sidebar({ yeniGonderi }: { yeniGonderi?: () => void }) {
  const yol = usePathname();
  const { tema, degistir } = useTema();
  const [medya, setMedya] = useState(false);

  return (
    <aside className="w-[300px] shrink-0 h-screen sticky top-0 flex flex-col px-5 py-6 max-xl:w-[88px] overflow-hidden">
      <Link href="/" className="mb-8 px-3 max-xl:px-0 max-xl:grid max-xl:place-items-center">
        <div className="text-[44px] leading-none font-black gradyan-metin tracking-tight">N</div>
        <div className="text-[10px] tracking-[0.4em] text-metin-sonuk mt-1 max-xl:hidden">BETA</div>
      </Link>

      <nav aria-label="Ana gezinme" className="flex flex-col gap-1 overflow-y-auto min-h-0">
        {MENU.map(({ ad, ikon: Ikon, yol: hedef, rozet, pasif }) => {
          const aktif = yol === hedef;
          return (
            <Link
              key={hedef}
              href={hedef}
              aria-current={aktif ? "page" : undefined}
              aria-disabled={pasif || undefined}
              title={ad}
              className={[
                "flex items-center gap-4 rounded-xl px-3 py-2.5 transition-colors max-xl:justify-center",
                aktif ? "bg-yukseltilmis" : "hover:bg-kart",
                pasif ? "opacity-40" : "",
              ].join(" ")}
            >
              <span className="relative grid place-items-center w-9 h-9 rounded-full shrink-0"
                    style={aktif ? { background: "var(--color-mavi)" } : undefined}>
                <Ikon size={20} strokeWidth={aktif ? 2.4 : 1.9}
                      className={aktif ? "text-white" : "text-metin"} />
                {rozet ? (
                  <span className="absolute -top-1 -right-1 min-w-[20px] h-[20px] px-1 rounded-full
                                   bg-mavi-koyu text-white text-[11px] font-semibold grid place-items-center">
                    {rozet}
                  </span>
                ) : null}
              </span>
              <span className={`text-[17px] max-xl:hidden ${aktif ? "font-semibold" : ""}`}>{ad}</span>
            </Link>
          );
        })}
      </nav>

      <button
        type="button"
        onClick={yeniGonderi}
        className="mt-5 gradyan-marka text-white font-semibold rounded-full py-3 px-5
                   flex items-center justify-center gap-2 hover:brightness-110 transition
                   max-xl:px-0"
      >
        <PenLine size={18} />
        <span className="max-xl:hidden">Yeni Gönderi</span>
      </button>

      <div className="mt-auto pt-4 border-t border-cizgi flex flex-col gap-1 shrink-0 max-xl:hidden">
        <Anahtar ikon={Play} ad="Medya" acik={medya} degistir={() => setMedya((v) => !v)} />
        <Anahtar
          ikon={tema === "koyu" ? Moon : Sun}
          ad={tema === "koyu" ? "Karanlık mod" : "Aydınlık mod"}
          acik={tema === "koyu"}
          degistir={degistir}
        />
      </div>
    </aside>
  );
}

function Anahtar({
  ikon: Ikon, ad, acik, degistir,
}: { ikon: typeof Play; ad: string; acik: boolean; degistir: () => void }) {
  return (
    <button
      type="button"
      onClick={degistir}
      role="switch"
      aria-checked={acik}
      aria-label={ad}
      className="w-full flex items-center gap-4 px-3 py-2.5 rounded-xl hover:bg-kart transition-colors text-left"
    >
      <Ikon size={20} strokeWidth={1.9} className="text-metin shrink-0" />
      <span className="text-[17px] flex-1">{ad}</span>
      <span
        aria-hidden="true"
        className={`w-[46px] h-[26px] rounded-full p-[3px] shrink-0 transition-colors
                    ${acik ? "bg-mavi" : "bg-yukseltilmis"}`}
      >
        <span className={`block w-5 h-5 rounded-full bg-white transition-transform
                          ${acik ? "translate-x-5" : ""}`} />
      </span>
    </button>
  );
}
