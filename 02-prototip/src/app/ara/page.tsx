"use client";

import { Suspense, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Hash, SearchX } from "lucide-react";
import { SayfaBasligi } from "@/components/layout/SayfaBasligi";
import { BosDurum } from "@/components/layout/BosDurum";
import { GonderiKarti } from "@/components/akis/GonderiKarti";
import { Avatar } from "@/components/layout/Avatar";
import { OnayliRozet } from "@/components/layout/OnayliRozet";
import { ara } from "@/lib/arama";
import { sayiBicimle } from "@/lib/bicim";

function Sonuclar() {
  const parametreler = useSearchParams();
  const sorgu = parametreler.get("q") ?? "";
  const sonuc = useMemo(() => ara(sorgu), [sorgu]);
  const toplam = sonuc.gonderiler.length + sonuc.hesaplar.length + sonuc.etiketler.length;

  return (
    <>
      <SayfaBasligi baslik={sorgu ? `“${sorgu}” için sonuçlar` : "Arama"} />

      {toplam === 0 ? (
        <BosDurum
          ikon={<SearchX size={80} strokeWidth={1.2} />}
          baslik="Sonuç bulunamadı"
          aciklama={sorgu.length < 2 ? "En az iki karakter yazın." : "Farklı bir arama deneyin."}
        />
      ) : (
        <>
          {sonuc.hesaplar.length > 0 && (
            <section aria-labelledby="hesap-baslik">
              <h2 id="hesap-baslik" className="px-5 py-3 font-bold text-[17px] border-b border-cizgi">
                Hesaplar
              </h2>
              <ul>
                {sonuc.hesaplar.map((k) => (
                  <li key={k.id}>
                    <Link href={`/profil/${k.kullanici_adi}`}
                          className="flex items-center gap-3 px-5 py-3.5 border-b border-cizgi hover:bg-kart/40">
                      <Avatar ad={k.kullanici_adi} boyut={44} />
                      <div className="min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className="font-bold truncate">{k.kullanici_adi.replace(/_/g, " ")}</span>
                          {k.dogrulanmis && <OnayliRozet />}
                        </div>
                        <p className="text-[14px] text-metin-ikincil">
                          @{k.kullanici_adi} · {sayiBicimle(k.takipci_sayisi)} takipçi
                        </p>
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {sonuc.etiketler.length > 0 && (
            <section aria-labelledby="etiket-baslik">
              <h2 id="etiket-baslik" className="px-5 py-3 font-bold text-[17px] border-b border-cizgi">
                Konular
              </h2>
              <ul>
                {sonuc.etiketler.map((e) => (
                  <li key={e.baslik} className="flex items-start gap-3 px-5 py-3.5 border-b border-cizgi">
                    <Hash size={20} className="text-metin-ikincil mt-0.5 shrink-0" />
                    <div>
                      <p className="font-semibold text-[15px]">{e.baslik}</p>
                      <p className="text-[13px] text-metin-ikincil">{e.sayi} gönderi</p>
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {sonuc.gonderiler.length > 0 && (
            <section aria-labelledby="gonderi-baslik">
              <h2 id="gonderi-baslik" className="px-5 py-3 font-bold text-[17px] border-b border-cizgi">
                Gönderiler ({sonuc.gonderiler.length})
              </h2>
              {sonuc.gonderiler.map((g) => <GonderiKarti key={g.id} gonderi={g} />)}
            </section>
          )}
        </>
      )}
    </>
  );
}

export default function AramaSayfasi() {
  return (
    <Suspense fallback={<div className="p-8 text-metin-ikincil">Yükleniyor…</div>}>
      <Sonuclar />
    </Suspense>
  );
}
