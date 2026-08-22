"use client";

import { use, useState } from "react";
import { MoreHorizontal, Send, UserPlus } from "lucide-react";
import { UstSekmeler } from "@/components/layout/UstSekmeler";
import { Avatar } from "@/components/layout/Avatar";
import { OnayliRozet } from "@/components/layout/OnayliRozet";
import { GonderiKarti } from "@/components/akis/GonderiKarti";
import { BosDurum } from "@/components/layout/BosDurum";
import { akisGetir, kullanicilar } from "@/lib/veri";
import { sayiBicimle } from "@/lib/bicim";
import { FileText } from "lucide-react";

const SEKMELER = ["Zaman Çizelgesi", "Medya", "Yanıtlar", "Hakkında"] as const;

export default function ProfilSayfasi({ params }: { params: Promise<{ kullanici: string }> }) {
  const { kullanici } = use(params);
  const [aktif, setAktif] = useState<(typeof SEKMELER)[number]>("Zaman Çizelgesi");

  const k = kullanicilar.find((x) => x.kullanici_adi === decodeURIComponent(kullanici)) ?? kullanicilar[0];
  const gonderileri = akisGetir().filter((g) => g.yazar_id === k.id);

  return (
    <>
      <div className="h-44 gradyan-marka opacity-80" />

      <div className="px-5">
        <div className="flex items-end justify-between -mt-14 mb-3">
          <div className="rounded-full p-1 bg-zemin">
            <Avatar ad={k.kullanici_adi} boyut={108} />
          </div>
          <div className="flex items-center gap-2 mb-2">
            <button type="button" aria-label="Profili paylaş"
                    className="p-2.5 rounded-full border border-cizgi hover:bg-hover">
              <Send size={17} />
            </button>
            <button type="button"
                    className="rounded-full bg-metin text-zemin font-semibold px-6 py-2.5 text-[15px] hover:opacity-90">
              Takip Et
            </button>
            <button type="button" aria-label="Diğer seçenekler"
                    className="p-2.5 rounded-full border border-cizgi hover:bg-hover">
              <MoreHorizontal size={17} />
            </button>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <h1 className="text-[22px] font-bold">{k.kullanici_adi.replace(/_/g, " ")}</h1>
          {k.dogrulanmis && <OnayliRozet boyut={19} />}
        </div>
        <p className="text-[15px] text-metin-ikincil">@{k.kullanici_adi}</p>

        <p className="text-[15px] mt-3">
          {k.ilgi_alanlari.join(", ")} üzerine paylaşım yapıyor.
        </p>

        <div className="flex items-center gap-5 mt-3 text-[15px] flex-wrap">
          <span><strong>{sayiBicimle(k.takip_edilen_sayisi)}</strong>{" "}
            <span className="text-metin-ikincil">Takip Edilen</span></span>
          <span><strong>{sayiBicimle(k.takipci_sayisi)}</strong>{" "}
            <span className="text-metin-ikincil">Takipçi</span></span>
          <span><strong>{sayiBicimle(gonderileri.length)}</strong>{" "}
            <span className="text-metin-ikincil">Gönderi</span></span>
        </div>

        <div className="flex items-center gap-2 mt-3 mb-4 text-[14px] text-metin-ikincil">
          <UserPlus size={15} />
          Hesap yaşı: {Math.round(k.hesap_yasi_gun / 30)} ay
        </div>
      </div>

      <UstSekmeler sekmeler={SEKMELER} aktif={aktif} degistir={setAktif} />

      {aktif === "Hakkında" ? (
        <div className="px-5 py-6 text-[15px] text-metin-ikincil">
          <p>İlgi alanları: {k.ilgi_alanlari.join(" · ")}</p>
          <p className="mt-2">Hesap türü: {k.rol === "uretici" ? "İçerik üreticisi" : "Kullanıcı"}</p>
          <p className="mt-2">Onaylı hesap: {k.dogrulanmis ? "Evet" : "Hayır"}</p>
        </div>
      ) : gonderileri.length === 0 ? (
        <BosDurum
          ikon={<FileText size={70} strokeWidth={1.2} />}
          baslik="Henüz gönderi bulunmamaktadır."
          aciklama="İlk gönderinizi paylaşmaya başlayın"
        />
      ) : (
        gonderileri
          .filter((g) => (aktif === "Medya" ? g.gorsel_var : true))
          .map((g) => <GonderiKarti key={g.id} gonderi={g} />)
      )}
    </>
  );
}
