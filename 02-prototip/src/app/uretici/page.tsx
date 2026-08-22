"use client";

import { Clock, Lightbulb, Lock, TrendingUp, Users } from "lucide-react";
import { SayfaBasligi } from "@/components/layout/SayfaBasligi";
import { kitleDagilimi, konuOnerileri, saatlikYogunluk, zamanOnerileri } from "@/lib/uretici/oneriler";
import { KATEGORI_ETIKET } from "@/lib/tipler";

export default function UreticiSayfasi() {
  const zamanlar = zamanOnerileri();
  const konular = konuOnerileri();
  const yogunluk = saatlikYogunluk();
  const kitle = kitleDagilimi();
  const enYogun = Math.max(...yogunluk, 1);

  return (
    <>
      <SayfaBasligi baslik="İçerik Üretici Paneli" />

      <div className="px-5 pb-10 flex flex-col gap-6">
        {/* KVKK bildirimi — panelin en üstünde, gizlenmeden */}
        <div className="flex items-start gap-3 rounded-xl bg-kart border border-cizgi p-4">
          <Lock size={18} className="text-basari mt-0.5 shrink-0" />
          <p className="text-[13px] text-metin-ikincil leading-relaxed">
            Bu paneldeki tüm çıktılar <strong className="text-metin">toplulaştırılmış ve
            kişisel bilgilerden arındırılmış</strong> etkileşim sinyallerinden üretilir.
            Tekil kullanıcı davranışı izlenmez; hiçbir öneri tek bir kişiye geri izlenemez.
          </p>
        </div>

        {/* Paylaşım zamanı */}
        <section aria-labelledby="zaman-baslik">
          <h2 id="zaman-baslik" className="flex items-center gap-2 font-bold text-[17px] mb-1">
            <Clock size={18} className="text-mihenk" /> En verimli paylaşım zamanları
          </h2>
          <p className="text-[13px] text-metin-ikincil mb-4">
            Kitlenizin etkileşim yoğunluğuna göre hesaplanmıştır.
          </p>

          <div className="grid grid-cols-3 max-sm:grid-cols-1 gap-3 mb-5">
            {zamanlar.map((z, i) => (
              <div key={`${z.gun}-${z.saat}`}
                   className="rounded-xl bg-kart p-4 border border-cizgi">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[13px] text-metin-ikincil">{i + 1}. öneri</span>
                  <span className="text-[12px] text-mihenk tabular-nums">
                    {z.etkilesimSayisi} etkileşim
                  </span>
                </div>
                <p className="font-bold text-[17px]">{z.gunAdi}</p>
                <p className="text-[15px] text-metin-ikincil tabular-nums">
                  {String(z.saat).padStart(2, "0")}:00 – {String((z.saat + 1) % 24).padStart(2, "0")}:00
                </p>
              </div>
            ))}
          </div>

          {/* Saatlik ısı çubuğu */}
          <div>
            <p className="text-[13px] text-metin-ikincil mb-2">Gün içi etkileşim dağılımı</p>
            <div className="flex items-end gap-[3px] h-24" role="img"
                 aria-label="Saatlere göre etkileşim yoğunluğu grafiği">
              {yogunluk.map((v, saat) => (
                <div key={saat} className="flex-1 h-full flex flex-col justify-end items-center gap-1">
                  <div className="w-full rounded-t transition-all"
                       style={{
                         height: `${Math.max(4, (v / enYogun) * 100)}%`,
                         background: v / enYogun > 0.7 ? "var(--color-mihenk)" : "var(--color-yukseltilmis)",
                       }}
                       title={`${saat}:00 — ${v} etkileşim`} />
                  {saat % 6 === 0 && (
                    <span className="text-[10px] text-metin-sonuk tabular-nums">{saat}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Konu önerileri */}
        <section aria-labelledby="konu-baslik">
          <h2 id="konu-baslik" className="flex items-center gap-2 font-bold text-[17px] mb-1">
            <Lightbulb size={18} className="text-mihenk" /> Gündemden konu önerileri
          </h2>
          <p className="text-[13px] text-metin-ikincil mb-4">
            Şu an konuşulan başlıklar ve tartışmanın tonu.
          </p>
          <ul className="flex flex-col gap-3">
            {konular.map((k) => (
              <li key={k.baslik} className="rounded-xl bg-kart border border-cizgi p-4">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <h3 className="font-semibold text-[15px] leading-snug">{k.baslik}</h3>
                  <span className="shrink-0 text-[12px] rounded-full bg-yukseltilmis px-2.5 py-1">
                    {KATEGORI_ETIKET[k.kategori]}
                  </span>
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex-1 h-1.5 rounded-full bg-yukseltilmis overflow-hidden">
                    <span className="block h-full rounded-full bg-mihenk"
                          style={{ width: `${k.ilgi * 100}%` }} />
                  </div>
                  <span className="text-[12px] text-metin-ikincil tabular-nums shrink-0">
                    {k.gonderiSayisi} gönderi
                  </span>
                </div>
                <p className="text-[13px] text-metin-ikincil">{k.tonNotu}</p>
              </li>
            ))}
          </ul>
        </section>

        {/* Kitle dağılımı */}
        <section aria-labelledby="kitle-baslik">
          <h2 id="kitle-baslik" className="flex items-center gap-2 font-bold text-[17px] mb-1">
            <Users size={18} className="text-mihenk" /> Kitle dağılımı
          </h2>
          <p className="text-[13px] text-metin-ikincil mb-4">
            Etkileşim kuran hesapların anonim takipçi aralıkları.
          </p>
          <ul className="flex flex-col gap-2.5">
            {kitle.map((k) => (
              <li key={k.aralik} className="flex items-center gap-3">
                <span className="w-20 text-[14px] shrink-0">{k.aralik}</span>
                <div className="flex-1 h-6 rounded-lg bg-yukseltilmis overflow-hidden">
                  <span className="block h-full gradyan-marka rounded-lg"
                        style={{ width: `${k.oran * 100}%` }} />
                </div>
                <span className="w-12 text-right text-[13px] text-metin-ikincil tabular-nums shrink-0">
                  %{Math.round(k.oran * 100)}
                </span>
              </li>
            ))}
          </ul>
        </section>

        <div className="flex items-center gap-2 text-[13px] text-metin-sonuk border-t border-cizgi pt-4">
          <TrendingUp size={15} />
          Öneriler, etkileşim verisi biriktikçe güncellenir.
        </div>
      </div>
    </>
  );
}
