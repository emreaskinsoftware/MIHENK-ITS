"use client";

import { useMemo, useState } from "react";
import { AlertTriangle, ChevronDown, FileText, Sparkles, Users, X } from "lucide-react";
import { AtifliOzetBolumu } from "./AtifliOzetBolumu";
import { DengeCubugu } from "./DengeCubugu";
import { kategoriOzetle, kisiselOzetle, type OlayOzeti } from "@/lib/ozet/cikarimsal";
import { akisGetir, kategoriyeGoreGetir } from "@/lib/veri";
import type { Kategori } from "@/lib/tipler";

const SEKMELER: { anahtar: Kategori | "kisisel_akis"; etiket: string }[] = [
  { anahtar: "gundem", etiket: "Ülke Gündemi" },
  { anahtar: "spor", etiket: "Spor" },
  { anahtar: "teknoloji", etiket: "Teknoloji" },
  { anahtar: "ekonomi", etiket: "Ekonomi" },
  { anahtar: "kisisel_akis", etiket: "Kişisel Akış" },
];

export function OzetPaneli({ kapat }: { kapat: () => void }) {
  const [aktif, setAktif] = useState<(typeof SEKMELER)[number]["anahtar"]>("gundem");

  /**
   * Sekme içeriği.
   *
   * `useMemo` yalnızca hesabı ucuzlatmak için değil, KİMLİK KARARLILIĞI için de
   * gerekli: `gonderiler` dizisi `AtifliOzetBolumu` içindeki `useEffect`'in
   * bağımlılığı. Her render'da yeni bir dizi üretilseydi bileşen sonsuz döngüye
   * girip aynı özeti tekrar tekrar isterdi.
   */
  const icerik = useMemo(() => {
    if (aktif === "kisisel_akis") {
      return {
        tur: "kisisel" as const,
        // Backend'in kategori adı; çoğulculuk kuralı burada aranmaz çünkü
        // kişisel akış gündem değildir (bkz. summarize/adhoc.py).
        kategori: "kisisel",
        gonderiler: kategoriyeGoreGetir("kisisel"),
        yerelOzet: kisiselOzetle(akisGetir()),
      };
    }
    const veri = kategoriOzetle(aktif);
    return {
      tur: "kategori" as const,
      kategori: aktif,
      gonderiler: kategoriyeGoreGetir(aktif),
      // Servise erişilemezse gösterilecek yerel temel: en çok gönderi alan
      // olayın çıkarımsal özeti. Atıf taşımaz; bileşen bunu açıkça yazar.
      yerelOzet:
        veri.olaylar[0]?.ozet ?? "Bu kategoride özetlenecek yeterli gönderi yok.",
      veri,
    };
  }, [aktif]);

  return (
    <section
      aria-label="MİHENK özet paneli"
      className="border-b border-cizgi bg-kart/60"
    >
      <header className="flex items-center gap-3 px-5 pt-5 pb-3">
        <span className="grid place-items-center w-9 h-9 rounded-full bg-mihenk/15 shrink-0">
          <Sparkles size={18} className="text-mihenk" />
        </span>
        <div className="min-w-0">
          <h2 className="font-bold text-[17px] leading-tight">MİHENK Özeti</h2>
          <p className="text-[13px] text-metin-ikincil">
            Akış sırası değişmez — bu yalnızca bir okuma katmanıdır
          </p>
        </div>
        <button
          type="button"
          onClick={kapat}
          aria-label="Özet panelini kapat"
          className="ml-auto p-2 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover"
        >
          <X size={18} />
        </button>
      </header>

      <div role="tablist" aria-label="Özet kategorileri"
           className="flex gap-2 px-5 pb-4 overflow-x-auto">
        {SEKMELER.map((s) => {
          const secili = aktif === s.anahtar;
          return (
            <button
              key={s.anahtar}
              role="tab"
              aria-selected={secili}
              onClick={() => setAktif(s.anahtar)}
              className={`shrink-0 rounded-full px-4 py-2 text-[14px] font-medium transition-colors
                          ${secili
                            ? "bg-mihenk-koyu text-white"
                            : "bg-yukseltilmis text-metin-ikincil hover:text-metin"}`}
            >
              {s.etiket}
            </button>
          );
        })}
      </div>

      <div className="px-5 pb-5 flex flex-col gap-3">
        {/*
          Atıflı özet en üstte: bu, ürünün ana iddiasının (İlke 1) kullanıcıya
          göründüğü yerdir. Cümleler backend'in atıf denetiminden geçmiştir;
          yanındaki rozet, o cümlenin dayandığı gönderilere götürür.
        */}
        <AtifliOzetBolumu
          kategori={icerik.kategori}
          gonderiler={icerik.gonderiler}
          yerelOzet={icerik.yerelOzet}
        />

        {/*
          Altındaki olay kartları YEREL olarak hesaplanır ve atıflı özetin
          yerini almaz; çerçeve dağılımını ve denge skorunu gösterirler
          (İlke 3'ün görünür yüzü). İkisi farklı soruları yanıtlar: özet "ne
          oldu", denge çubuğu "kaç farklı açıdan anlatıldı".
        */}
        {icerik.tur === "kategori" &&
          (icerik.veri.olaylar.length === 0 ? (
            <p className="text-[15px] text-metin-ikincil">
              Bu kategoride ayrıştırılabilen bir olay kümesi yok.
            </p>
          ) : (
            icerik.veri.olaylar.map((o) => <OlayKarti key={o.olayId} ozet={o} />)
          ))}
      </div>
    </section>
  );
}

function OlayKarti({ ozet }: { ozet: OlayOzeti }) {
  const [acik, setAcik] = useState(false);

  return (
    <article className="rounded-xl bg-zemin border border-cizgi p-4">
      <h3 className="font-semibold text-[15px] leading-snug">{ozet.baslik}</h3>

      <p className={`mt-2 text-[14px] leading-relaxed text-metin-ikincil ${acik ? "" : "line-clamp-3"}`}>
        {ozet.ozet}
      </p>

      <button
        type="button"
        onClick={() => setAcik((v) => !v)}
        aria-expanded={acik}
        className="mt-1.5 flex items-center gap-1 text-[13px] text-mavi hover:underline"
      >
        {acik ? "Daha az göster" : "Daha fazla göster"}
        <ChevronDown size={14} className={acik ? "rotate-180 transition-transform" : "transition-transform"} />
      </button>

      <div className="mt-3 flex items-center gap-4 text-[12px] text-metin-ikincil flex-wrap">
        <span className="flex items-center gap-1.5">
          <FileText size={13} /> {ozet.gonderiSayisi} gönderi
        </span>
        <span className="flex items-center gap-1.5">
          <Users size={13} /> {ozet.kaynakSayisi} farklı hesap
        </span>
        {ozet.dogrulanmamisIddiaVar && (
          <span className="flex items-center gap-1.5 text-uyari">
            <AlertTriangle size={13} /> Doğrulanmamış iddia içeriyor
          </span>
        )}
      </div>

      <DengeCubugu dagilim={ozet.dagilim} dengeSkoru={ozet.dengeSkoru} />
    </article>
  );
}
