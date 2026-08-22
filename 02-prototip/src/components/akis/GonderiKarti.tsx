"use client";

import { useState } from "react";
import Link from "next/link";
import { BarChart3, Bookmark, MessageCircle, MoreHorizontal, Quote, Rocket, Share2, ShieldQuestion, Sparkles } from "lucide-react";
import { DogrulamaPaneli } from "../ozet/DogrulamaPaneli";
import { AsistanPaneli } from "../ozet/AsistanPaneli";
import { Avatar } from "../layout/Avatar";
import { OnayliRozet } from "../layout/OnayliRozet";
import { goreliZaman, metniParcala, sayiBicimle } from "@/lib/bicim";
import { hesapRiskiHesapla } from "@/lib/analiz/hesapRiski";
import { akisGetir } from "@/lib/veri";
import { RiskRozeti } from "./RiskRozeti";
import type { AkisOgesi } from "@/lib/tipler";

/** NSosyal eylem çubuğu: yorum · alıntı · beğeni(roket) · görüntülenme */
function Eylem({
  ikon: Ikon, sayi, etiket, etkin, tiklandi, renk,
}: {
  ikon: typeof Rocket; sayi: number; etiket: string;
  etkin?: boolean; tiklandi?: () => void; renk?: string;
}) {
  return (
    <button
      type="button"
      onClick={tiklandi}
      aria-label={`${etiket}: ${sayi}`}
      aria-pressed={etkin}
      className="flex items-center gap-2 rounded-full bg-kart hover:bg-hover
                 px-4 py-2 transition-colors"
      style={{ color: etkin && renk ? renk : "var(--color-metin-ikincil)" }}
    >
      <Ikon size={17} strokeWidth={etkin ? 2.3 : 1.8} fill={etkin && renk ? renk : "none"} />
      <span className="text-[13px] tabular-nums">{sayiBicimle(sayi)}</span>
    </button>
  );
}

type Panel = "yok" | "ozet" | "dogrula" | "asistan";

export function GonderiKarti({ gonderi }: { gonderi: AkisOgesi }) {
  const [panel, setPanel] = useState<Panel>("yok");
  const [begenildi, setBegenildi] = useState(false);
  const [paylasildi, setPaylasildi] = useState(false);
  const [kaydedildi, setKaydedildi] = useState(false);
  const [ozet, setOzet] = useState<string | null>(null);
  const [ozetYukleniyor, setOzetYukleniyor] = useState(false);
  const { yazar } = gonderi;
  const risk = hesapRiskiHesapla(yazar, akisGetir().filter((g) => g.yazar_id === yazar.id));

  async function ozetle() {
    if (panel === "ozet") { setPanel("yok"); return; }
    setPanel("ozet");
    if (ozet) return;
    setOzetYukleniyor(true);
    try {
      const y = await fetch("/api/ozet", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ tur: "gonderi", gonderiId: gonderi.id }),
      });
      const v = await y.json();
      setOzet(v.ozet);
    } finally {
      setOzetYukleniyor(false);
    }
  }
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
            <RiskRozeti risk={risk} />
            <button
              type="button"
              aria-label="Gönderi menüsü"
              className="ml-auto text-metin-ikincil hover:text-metin p-1 rounded-full hover:bg-hover"
            >
              <MoreHorizontal size={18} />
            </button>
          </header>

          <Link href={`/gonderi/${gonderi.id}`} className="block">
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
          </Link>

          {gonderi.gorsel_var && (
            <GorselAlani yapayUretim={gonderi.gorsel_yapay_uretim} />
          )}

          <div className="mt-3 flex items-center gap-2 flex-wrap">
            <Eylem ikon={MessageCircle} sayi={gonderi.yanit_sayisi} etiket="Yanıt"
                   tiklandi={() => setPanel((p) => (p === "asistan" ? "yok" : "asistan"))} />
            <Eylem ikon={Quote} sayi={gonderi.yeniden_paylasim + (paylasildi ? 1 : 0)}
                   etiket="Alıntı" etkin={paylasildi} renk="var(--color-basari)"
                   tiklandi={() => setPaylasildi((v) => !v)} />
            <Eylem ikon={Rocket} sayi={gonderi.begeni + (begenildi ? 1 : 0)}
                   etiket="Beğeni" etkin={begenildi} renk="var(--color-mavi)"
                   tiklandi={() => setBegenildi((v) => !v)} />
            <Eylem ikon={BarChart3} sayi={goruntulenme} etiket="Görüntülenme" />

            <div className="ml-auto flex items-center gap-1">
              <button
                type="button" onClick={ozetle}
                aria-pressed={panel === "ozet"}
                aria-label="Bu gönderiyi MİHENK ile özetle"
                className="flex items-center gap-1.5 rounded-full px-3 py-2 text-[13px] font-medium
                           text-mihenk hover:bg-mihenk/10 transition-colors"
              >
                <Sparkles size={16} /><span className="max-sm:hidden">Özetle</span>
              </button>

              {gonderi.dogrulanabilir_iddia && (
                <button
                  type="button"
                  onClick={() => setPanel((p) => (p === "dogrula" ? "yok" : "dogrula"))}
                  aria-pressed={panel === "dogrula"}
                  aria-label="Bu gönderideki iddiayı doğrula"
                  className="flex items-center gap-1.5 rounded-full px-3 py-2 text-[13px] font-medium
                             text-mihenk hover:bg-mihenk/10 transition-colors"
                >
                  <ShieldQuestion size={16} /><span className="max-sm:hidden">Doğrula</span>
                </button>
              )}

              <button
                type="button"
                onClick={() => setPanel((p) => (p === "asistan" ? "yok" : "asistan"))}
                aria-pressed={panel === "asistan"}
                aria-label="Bu gönderi hakkında asistana sor"
                className="flex items-center gap-1.5 rounded-full px-3 py-2 text-[13px] font-medium
                           text-mihenk hover:bg-mihenk/10 transition-colors"
              >
                <MessageCircle size={16} /><span className="max-sm:hidden">Sor</span>
              </button>
              <button type="button" aria-label="Kaydet" aria-pressed={kaydedildi}
                      onClick={() => setKaydedildi((v) => !v)}
                      className="p-2 rounded-full hover:bg-hover transition-colors"
                      style={{ color: kaydedildi ? "var(--color-mavi)" : "var(--color-metin-ikincil)" }}>
                <Bookmark size={17} fill={kaydedildi ? "var(--color-mavi)" : "none"} />
              </button>
              <button type="button" aria-label="Paylaş"
                      onClick={() => navigator.clipboard?.writeText(`${location.origin}/gonderi/${gonderi.id}`)}
                      className="p-2 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover">
                <Share2 size={17} />
              </button>
            </div>
          </div>

          {panel === "ozet" && (
            <div className="mt-3 rounded-xl border border-cizgi bg-zemin p-4">
              <header className="flex items-center gap-2.5 mb-2">
                <Sparkles size={17} className="text-mihenk shrink-0" />
                <h3 className="font-semibold text-[14px]">MİHENK Özeti</h3>
              </header>
              <p className="text-[14px] leading-relaxed text-metin-ikincil">
                {ozetYukleniyor ? "Özet hazırlanıyor…" : ozet}
              </p>
            </div>
          )}

          {panel === "dogrula" && (
            <DogrulamaPaneli gonderi={gonderi} kapat={() => setPanel("yok")} />
          )}

          {panel === "asistan" && (
            <AsistanPaneli gonderi={gonderi} kapat={() => setPanel("yok")} />
          )}
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
