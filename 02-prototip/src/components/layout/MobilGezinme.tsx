"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bell, Bookmark, Cloud, Compass, Home, Menu, MessagesSquare,
  Moon, PenLine, Play, Rocket, Search, SlidersHorizontal, Star, Sun, X, ClipboardList,
} from "lucide-react";
import { Avatar } from "./Avatar";
import { temaKullan } from "./TemaSaglayici";

const ALT_SEKME = [
  { ad: "Ana Sayfa", ikon: Home, yol: "/" },
  { ad: "Keşfet", ikon: Search, yol: "/kesfet" },
  { ad: "Medya", ikon: Play, yol: "/kesfet" },
  { ad: "Mesajlar", ikon: MessagesSquare, yol: "/mesajlar" },
];

const CEKMECE = [
  { ad: "Bildirimler", ikon: Bell, yol: "/bildirimler" },
  { ad: "Keşfet", ikon: Compass, yol: "/kesfet" },
  { ad: "Topluluklar", ikon: Star, yol: "/topluluklar" },
  { ad: "Kaydedilenler", ikon: Bookmark, yol: "/kaydedilenler" },
  { ad: "Beğeniler", ikon: Rocket, yol: "/begeniler" },
  { ad: "Nod Oyna", ikon: Cloud, yol: "/nod", pasif: true },
  { ad: "TEKNOFEST Köşesi", ikon: ClipboardList, yol: "/teknofest" },
  { ad: "Ayarlar", ikon: SlidersHorizontal, yol: "/ayarlar" },
];

export function MobilGezinme({ yeniGonderi }: { yeniGonderi: () => void }) {
  const [cekmece, setCekmece] = useState(false);
  const yol = usePathname();
  const { tema, degistir } = temaKullan();

  return (
    <>
      {/* Üst çubuk — hamburger + logo */}
      <header className="lg:hidden sticky top-0 z-30 flex items-center gap-3 px-4 py-3
                         bg-zemin/90 backdrop-blur-md border-b border-cizgi">
        <button type="button" onClick={() => setCekmece(true)} aria-label="Menüyü aç"
                className="p-2 -ml-2 rounded-full hover:bg-hover">
          <Menu size={22} />
        </button>
        <div className="mx-auto text-[26px] leading-none font-black gradyan-metin">N</div>
        <div className="w-8" />
      </header>

      {/* Çekmece */}
      {cekmece && (
        <div className="lg:hidden fixed inset-0 z-50 flex" role="dialog" aria-modal="true" aria-label="Gezinme menüsü">
          <div className="w-[80%] max-w-[340px] h-full overflow-y-auto"
               style={{ backgroundImage: "linear-gradient(160deg, var(--color-yukseltilmis), var(--color-zemin) 55%)" }}>
            <div className="p-5">
              <div className="flex items-start justify-between">
                <Avatar ad="mihenk kullanici" boyut={64} halka />
                <button type="button" onClick={() => setCekmece(false)} aria-label="Menüyü kapat"
                        className="p-2 rounded-full hover:bg-hover">
                  <X size={20} />
                </button>
              </div>
              <p className="font-bold text-[18px] mt-3">MİHENK Kullanıcı</p>
              <p className="text-[14px] text-metin-ikincil">@mihenk</p>
              <p className="text-[14px] text-metin-ikincil mt-2">
                <strong className="text-metin">4</strong> Takip Edilen{" "}
                <strong className="text-metin ml-2">1</strong> Takipçi
              </p>
            </div>

            <nav className="px-3 pb-4">
              {CEKMECE.map(({ ad, ikon: Ikon, yol: hedef, pasif }) => (
                <Link key={ad} href={hedef} onClick={() => setCekmece(false)}
                      aria-disabled={pasif || undefined}
                      className={`flex items-center gap-4 rounded-xl px-3 py-3.5 hover:bg-hover
                                  ${pasif ? "opacity-40" : ""}`}>
                  <Ikon size={22} strokeWidth={1.8} />
                  <span className="text-[17px]">{ad}</span>
                </Link>
              ))}
            </nav>

            <div className="px-5 pb-8">
              <div className="inline-flex rounded-full bg-kart p-1">
                {([
                  { deger: "koyu", ikon: Moon, etiket: "Karanlık tema" },
                  { deger: "acik", ikon: Sun, etiket: "Aydınlık tema" },
                ] as const).map(({ deger, ikon: Ikon, etiket }) => {
                  const secili = tema === deger;
                  return (
                    <button key={deger} type="button" aria-label={etiket} aria-pressed={secili}
                            onClick={() => { if (!secili) degistir(); }}
                            className={`grid place-items-center w-11 h-11 rounded-full transition-colors
                                        ${secili ? "bg-yukseltilmis" : ""}`}>
                      <Ikon size={20} />
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
          <button className="flex-1 bg-black/50" onClick={() => setCekmece(false)} aria-label="Menüyü kapat" />
        </div>
      )}

      {/* Kayan eylem düğmesi */}
      <button type="button" onClick={yeniGonderi} aria-label="Yeni gönderi oluştur"
              className="lg:hidden fixed right-5 bottom-24 z-30 w-14 h-14 rounded-full gradyan-marka
                         text-white grid place-items-center shadow-lg hover:brightness-110 transition">
        <PenLine size={22} />
      </button>

      {/* Alt sekme çubuğu */}
      <nav aria-label="Alt gezinme"
           className="lg:hidden fixed bottom-0 inset-x-0 z-30 flex bg-kart/95 backdrop-blur-md
                      border-t border-cizgi pb-[env(safe-area-inset-bottom)]">
        {ALT_SEKME.map(({ ad, ikon: Ikon, yol: hedef }) => {
          const aktif = yol === hedef;
          return (
            <Link key={ad} href={hedef} aria-label={ad} aria-current={aktif ? "page" : undefined}
                  className="flex-1 grid place-items-center py-3.5">
              <Ikon size={24} strokeWidth={aktif ? 2.3 : 1.8}
                    className={aktif ? "text-mavi" : "text-metin-ikincil"} />
            </Link>
          );
        })}
        <Link href="/profil/yaz_kalem1" aria-label="Profil" className="flex-1 grid place-items-center py-2.5">
          <Avatar ad="mihenk kullanici" boyut={28} />
        </Link>
      </nav>
    </>
  );
}
