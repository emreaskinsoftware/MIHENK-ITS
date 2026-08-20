"use client";

import { BarChart3, Bookmark, MessageCircle, MoreHorizontal, Quote, Rocket, Share2, Sparkles } from "lucide-react";
import { Avatar } from "../layout/Avatar";
import { OnayliRozet } from "../layout/OnayliRozet";
import { goreliZaman, metniParcala, sayiBicimle } from "@/lib/bicim";
import type { AkisOgesi } from "@/lib/tipler";

/** NSosyal eylem çubuğu: yorum · alıntı · beğeni(roket) · görüntülenme */
function Eylem({
  ikon: Ikon, sayi, etiket,
}: { ikon: typeof Rocket; sayi: number; etiket: string }) {
  return (
    <button
      type="button"
      aria-label={`${etiket}: ${sayi}`}
      className="flex items-center gap-2 rounded-full bg-kart hover:bg-hover
                 px-4 py-2 text-metin-ikincil hover:text-metin transition-colors"
    >
      <Ikon size={17} strokeWidth={1.8} />
      <span className="text-[13px] tabular-nums">{sayiBicimle(sayi)}</span>
    </button>
  );
}

export function GonderiKarti({
  gonderi,
  ozetIste,
}: {
  gonderi: AkisOgesi;
  ozetIste?: (g: AkisOgesi) => void;
}) {
  const { yazar } = gonderi;
  const goruntulenme = gonderi.begeni * 21 + gonderi.yanit_sayisi * 7 + 143;

  return (
    <article className="border-b border-cizgi px-5 py-4 hover:bg-kart/40 transition-colors">
      <div className="flex gap-3">
        <Avatar ad={yazar.kullanici_adi} boyut={44} />

        <div className="min-w-0 flex-1">
          <header className="flex items-center gap-1.5 text-[15px]">
            <span className="font-bold truncate">
              {yazar.kullanici_adi.replace(/_/g, " ")}
            </span>
            {yazar.dogrulanmis && <OnayliRozet />}
            <span className="text-metin-ikincil truncate">@{yazar.kullanici_adi}</span>
            <span className="text-metin-ikincil">·</span>
            <time dateTime={gonderi.zaman} className="text-metin-ikincil shrink-0">
              {goreliZaman(gonderi.zaman)}
            </time>
            <button
              type="button"
              aria-label="Gönderi menüsü"
              className="ml-auto text-metin-ikincil hover:text-metin p-1 rounded-full hover:bg-hover"
            >
              <MoreHorizontal size={18} />
            </button>
          </header>

          <p className="mt-1 text-[15px] leading-[1.5] whitespace-pre-wrap break-words">
            {metniParcala(gonderi.metin).map((p) =>
              p.tur === "metin" ? (
                <span key={p.anahtar}>{p.deger}</span>
              ) : (
                <span key={p.anahtar} className="text-mavi hover:underline cursor-pointer">
                  {p.deger}
                </span>
              ),
            )}
          </p>

          {gonderi.gorsel_var && (
            <GorselAlani yapayUretim={gonderi.gorsel_yapay_uretim} />
          )}

          <div className="mt-3 flex items-center gap-2 flex-wrap">
            <Eylem ikon={MessageCircle} sayi={gonderi.yanit_sayisi} etiket="Yanıt" />
            <Eylem ikon={Quote} sayi={gonderi.yeniden_paylasim} etiket="Alıntı" />
            <Eylem ikon={Rocket} sayi={gonderi.begeni} etiket="Beğeni" />
            <Eylem ikon={BarChart3} sayi={goruntulenme} etiket="Görüntülenme" />

            <div className="ml-auto flex items-center gap-1">
              {ozetIste && (
                <button
                  type="button"
                  onClick={() => ozetIste(gonderi)}
                  className="flex items-center gap-1.5 rounded-full px-3 py-2 text-[13px] font-medium
                             text-mihenk hover:bg-mihenk/10 transition-colors"
                  aria-label="Bu gönderiyi MİHENK ile özetle"
                >
                  <Sparkles size={16} />
                  <span>Özetle</span>
                </button>
              )}
              <button type="button" aria-label="Kaydet"
                      className="p-2 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover">
                <Bookmark size={17} />
              </button>
              <button type="button" aria-label="Paylaş"
                      className="p-2 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover">
                <Share2 size={17} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </article>
  );
}

/**
 * Görsel yer tutucu. Telif nedeniyle gerçek görsel kullanılmaz;
 * MİHENK'in görsel köken rozeti burada gösterilir.
 */
function GorselAlani({ yapayUretim }: { yapayUretim: boolean | null }) {
  return (
    <div className="mt-3 relative rounded-xl overflow-hidden border border-cizgi">
      <div
        className="h-56 grid place-items-center text-metin-sonuk text-sm"
        style={{ backgroundImage: "linear-gradient(135deg, #182130, #101725)" }}
      >
        görsel içerik
      </div>
      {yapayUretim !== null && (
        <div
          className={`absolute bottom-3 left-3 flex items-center gap-1.5 rounded-full px-3 py-1.5
                      text-[12px] font-medium backdrop-blur
                      ${yapayUretim
                        ? "bg-uyari/20 text-uyari ring-1 ring-uyari/40"
                        : "bg-basari/15 text-basari ring-1 ring-basari/30"}`}
        >
          <Sparkles size={13} />
          {yapayUretim ? "Yapay üretim olasılığı yüksek" : "Köken doğrulandı"}
        </div>
      )}
    </div>
  );
}
