"use client";

import { useState } from "react";
import { CalendarClock, ChevronDown, Globe, Image as ImageIkon, Info, Smile, Vote, X } from "lucide-react";
import { Avatar } from "../layout/Avatar";

const SINIR = 10000;

export function GonderiModali({ kapat }: { kapat: () => void }) {
  const [metin, setMetin] = useState("");

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm grid place-items-center p-4"
         role="dialog" aria-modal="true" aria-label="Yeni gönderi paylaş">
      <div className="w-full max-w-2xl max-h-[85vh] rounded-2xl bg-zemin border border-cizgi flex flex-col">
        <header className="flex items-center justify-between px-5 py-4">
          <h2 className="text-[19px] font-bold">Yeni Gönderi Paylaş</h2>
          <button type="button" onClick={kapat} aria-label="Kapat"
                  className="p-2 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover">
            <X size={20} />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto px-5">
          <div className="rounded-xl border border-cizgi p-4">
            <div className="flex items-center gap-3 mb-3">
              <Avatar ad="mihenk kullanici" boyut={40} />
              <button type="button"
                      className="flex items-center gap-1.5 rounded-full border border-mavi text-mavi
                                 px-3.5 py-1.5 text-[14px] font-medium hover:bg-mavi/10">
                <Globe size={15} /> Herkese Açık <ChevronDown size={14} />
              </button>
            </div>
            <label htmlFor="yeni-gonderi" className="sr-only">Gönderi metni</label>
            <textarea
              id="yeni-gonderi"
              value={metin}
              onChange={(e) => setMetin(e.target.value.slice(0, SINIR))}
              placeholder="Aklında ne var ?"
              rows={9}
              className="w-full bg-transparent text-[17px] placeholder:text-metin-sonuk outline-none resize-none"
            />
            <div className="flex items-center justify-between pt-2 border-t border-cizgi">
              <button type="button"
                      className="flex items-center gap-1.5 text-[14px] text-metin-ikincil hover:text-metin">
                <Globe size={15} /> Herkese Açık <ChevronDown size={13} />
              </button>
              <span className={`text-[13px] tabular-nums ${metin.length > SINIR * 0.95 ? "text-uyari" : "text-metin-sonuk"}`}>
                {metin.length}/{SINIR}
              </span>
            </div>
          </div>
        </div>

        <footer className="flex items-center gap-1 px-5 py-4">
          {[
            { ikon: ImageIkon, etiket: "Görsel ekle" },
            { ikon: Vote, etiket: "Anket ekle" },
            { ikon: Info, etiket: "Bilgi ekle" },
            { ikon: CalendarClock, etiket: "Zamanla" },
            { ikon: Smile, etiket: "Emoji ekle" },
          ].map(({ ikon: Ikon, etiket }) => (
            <button key={etiket} type="button" aria-label={etiket}
                    className="p-2.5 rounded-full text-metin-ikincil hover:text-mavi hover:bg-mavi/10 transition-colors">
              <Ikon size={20} strokeWidth={1.8} />
            </button>
          ))}
          <button
            type="button"
            disabled={!metin.trim()}
            className="ml-auto rounded-full bg-metin text-zemin font-semibold px-7 py-2.5 text-[15px]
                       disabled:opacity-40 hover:opacity-90 transition"
          >
            Gönder
          </button>
        </footer>
      </div>
    </div>
  );
}
