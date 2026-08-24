"use client";

import { CalendarClock, Image as ImageIkon, Info, PenLine, Smile, Vote } from "lucide-react";
import { Avatar } from "../layout/Avatar";

const ARACLAR = [
  { ikon: ImageIkon, etiket: "Görsel ekle" },
  { ikon: Vote, etiket: "Anket ekle" },
  { ikon: Info, etiket: "Bilgi ekle" },
  { ikon: Smile, etiket: "Emoji ekle" },
  { ikon: CalendarClock, etiket: "Zamanla" },
];

export function Olusturucu() {
  return (
    <div className="px-5 py-4 border-b border-cizgi">
      <div className="flex gap-3">
        <Avatar ad="mihenk kullanici" boyut={44} />
        <div className="flex-1">
          <label htmlFor="gonderi-metni" className="sr-only">Gönderi metni</label>
          <input
            id="gonderi-metni"
            placeholder="Gönderi oluşturmak için..."
            className="w-full bg-transparent text-[18px] placeholder:text-metin-sonuk
                       outline-none py-2"
          />
          <div className="flex items-center gap-1 mt-2 max-sm:gap-0">
            {ARACLAR.map(({ ikon: Ikon, etiket }) => (
              <button key={etiket} type="button" aria-label={etiket}
                      className="p-2 max-sm:p-1.5 rounded-full text-mavi hover:bg-mavi/10 transition-colors">
                <Ikon size={19} strokeWidth={1.9} className="max-sm:w-[17px] max-sm:h-[17px]" />
              </button>
            ))}
            <button
              type="button"
              aria-label="Gönder"
              className="ml-auto shrink-0 flex items-center gap-2 rounded-full bg-yukseltilmis text-metin-ikincil
                         px-5 py-2 max-sm:px-3 text-[15px] font-semibold"
            >
              <PenLine size={16} />
              <span className="max-sm:hidden">Gönder</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
