"use client";

import { use } from "react";
import { Layers } from "lucide-react";
import { SayfaBasligi } from "@/components/layout/SayfaBasligi";
import { GonderiKarti } from "@/components/akis/GonderiKarti";
import { BosDurum } from "@/components/layout/BosDurum";
import { DengeCubugu } from "@/components/ozet/DengeCubugu";
import { gonderiGetir, olayKumesiGetir } from "@/lib/veri";
import { olayOzetle } from "@/lib/ozet/cikarimsal";
import { FileQuestion } from "lucide-react";

export default function GonderiDetay({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const gonderi = gonderiGetir(id);

  if (!gonderi) {
    return (
      <>
        <SayfaBasligi baslik="Gönderi" />
        <BosDurum
          ikon={<FileQuestion size={80} strokeWidth={1.2} />}
          baslik="Gönderi bulunamadı"
          aciklama="Bu gönderi kaldırılmış veya bağlantı hatalı olabilir."
        />
      </>
    );
  }

  const kume = gonderi.olay_id ? olayKumesiGetir(gonderi.olay_id) : [];
  const digerleri = kume.filter((g) => g.id !== gonderi.id);
  const ozet = gonderi.olay_id && kume.length
    ? olayOzetle(gonderi.olay_id, gonderi.olay_basligi!, gonderi.kategori, kume)
    : null;

  return (
    <>
      <SayfaBasligi baslik="Gönderi" />
      <GonderiKarti gonderi={gonderi} />

      {ozet && (
        <section className="px-5 py-5 border-b border-cizgi bg-kart/40" aria-labelledby="baglam-baslik">
          <h2 id="baglam-baslik" className="flex items-center gap-2 font-bold text-[16px] mb-1">
            <Layers size={17} className="text-mihenk" /> Bu gönderinin bağlamı
          </h2>
          <p className="text-[13px] text-metin-ikincil mb-3">
            Aynı olay hakkında {kume.length} gönderi var. MİHENK, hepsini birlikte değerlendirir.
          </p>
          <div className="rounded-xl bg-zemin border border-cizgi p-4">
            <h3 className="font-semibold text-[15px] mb-2">{ozet.baslik}</h3>
            <p className="text-[14px] leading-relaxed text-metin-ikincil">{ozet.ozet}</p>
            <DengeCubugu dagilim={ozet.dagilim} dengeSkoru={ozet.dengeSkoru} />
          </div>
        </section>
      )}

      {digerleri.length > 0 && (
        <section aria-labelledby="digerleri-baslik">
          <h2 id="digerleri-baslik" className="px-5 py-3 font-bold text-[16px] border-b border-cizgi">
            Aynı olay hakkındaki diğer gönderiler
          </h2>
          {digerleri.map((g) => <GonderiKarti key={g.id} gonderi={g} />)}
        </section>
      )}
    </>
  );
}
