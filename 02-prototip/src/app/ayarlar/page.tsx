"use client";

import { useState } from "react";
import {
  Accessibility, Bell, Contrast, LogOut, MessageSquareWarning, Moon,
  ShieldCheck, Sun, Type, UserCheck, UserCog,
} from "lucide-react";
import { SayfaBasligi } from "@/components/layout/SayfaBasligi";
import { temaKullan } from "@/components/layout/TemaSaglayici";

const BOLUMLER = [
  { ad: "Hesap Ayarları", ikon: UserCog },
  { ad: "Bildirim Ayarları", ikon: Bell },
  { ad: "Erişilebilirlik ve Görünüm", ikon: Accessibility },
  { ad: "Gizlilik ve Güvenlik", ikon: ShieldCheck },
  { ad: "Geri Bildirim", ikon: MessageSquareWarning },
  { ad: "Onaylı Hesap Talebi", ikon: UserCheck },
  { ad: "Çıkış Yap", ikon: LogOut },
] as const;

export default function AyarlarSayfasi() {
  const [aktif, setAktif] = useState<string>("Erişilebilirlik ve Görünüm");

  return (
    <div className="flex max-lg:flex-col">
      <nav aria-label="Ayarlar bölümleri"
           className="w-[280px] shrink-0 border-r border-cizgi py-5 px-3 max-lg:w-full max-lg:border-r-0 max-lg:border-b">
        {BOLUMLER.map(({ ad, ikon: Ikon }) => {
          const secili = ad === aktif;
          return (
            <button
              key={ad}
              onClick={() => setAktif(ad)}
              aria-current={secili ? "true" : undefined}
              className={`w-full flex items-center gap-4 rounded-xl px-3 py-3 text-left transition-colors
                          ${secili ? "bg-yukseltilmis" : "hover:bg-kart"}`}
            >
              <span className="grid place-items-center w-9 h-9 rounded-full shrink-0"
                    style={secili ? { background: "var(--color-mavi)" } : undefined}>
                <Ikon size={19} className={secili ? "text-white" : "text-metin"} />
              </span>
              <span className={`text-[16px] ${secili ? "font-semibold" : ""}`}>{ad}</span>
            </button>
          );
        })}
      </nav>

      <div className="flex-1 min-w-0">
        <SayfaBasligi baslik={aktif} />
        {aktif === "Erişilebilirlik ve Görünüm" ? <ErisilebilirlikBolumu /> : <GenelBolum ad={aktif} />}
      </div>
    </div>
  );
}

/**
 * Erişilebilirlik ayarları — rapor 3.3'teki "erişilebilirlik yaklaşımı"
 * maddesinin somut karşılığı.
 */
function ErisilebilirlikBolumu() {
  const { tema, degistir } = temaKullan();
  const [yaziBoyutu, setYaziBoyutu] = useState(100);
  const [yuksekKontrast, setYuksekKontrast] = useState(false);
  const [hareketAzalt, setHareketAzalt] = useState(false);

  return (
    <div className="px-6 pb-10 flex flex-col gap-8 max-w-2xl">
      <section>
        <h2 className="font-semibold text-[17px] mb-1">Görünüm</h2>
        <p className="text-[14px] text-metin-ikincil mb-4">
          Arayüzün renk temasını seçin. Tercihiniz cihazınızda saklanır.
        </p>
        <div role="radiogroup" aria-label="Tema seçimi" className="flex gap-3">
          {([
            { deger: "koyu", etiket: "Karanlık", ikon: Moon },
            { deger: "acik", etiket: "Aydınlık", ikon: Sun },
          ] as const).map(({ deger, etiket, ikon: Ikon }) => {
            const secili = tema === deger;
            return (
              <button
                key={deger}
                role="radio"
                aria-checked={secili}
                onClick={() => { if (!secili) degistir(); }}
                className={`flex items-center gap-2.5 rounded-xl px-5 py-3 transition-colors
                            ${secili ? "bg-mavi text-white" : "bg-kart hover:bg-yukseltilmis"}`}
              >
                <Ikon size={18} /> {etiket}
              </button>
            );
          })}
        </div>
      </section>

      <section>
        <h2 className="font-semibold text-[17px] mb-1 flex items-center gap-2">
          <Type size={18} /> Yazı boyutu
        </h2>
        <p className="text-[14px] text-metin-ikincil mb-4">
          Metinleri büyüterek okumayı kolaylaştırın. Şu an: %{yaziBoyutu}
        </p>
        <input
          type="range" min={85} max={150} step={5} value={yaziBoyutu}
          onChange={(e) => {
            const d = Number(e.target.value);
            setYaziBoyutu(d);
            document.documentElement.style.fontSize = `${d}%`;
          }}
          aria-label="Yazı boyutu yüzdesi"
          className="w-full accent-[var(--color-mavi)]"
        />
      </section>

      <Anahtar
        ikon={Contrast} baslik="Yüksek kontrast"
        aciklama="Metin ve arka plan arasındaki kontrastı artırır (WCAG 2.2 AAA hedefi)."
        acik={yuksekKontrast} degistir={() => setYuksekKontrast((v) => !v)}
      />
      <Anahtar
        ikon={Accessibility} baslik="Hareketi azalt"
        aciklama="Animasyon ve geçişleri kapatır. Vestibüler duyarlılığı olan kullanıcılar için."
        acik={hareketAzalt} degistir={() => setHareketAzalt((v) => !v)}
      />
    </div>
  );
}

function Anahtar({
  ikon: Ikon, baslik, aciklama, acik, degistir,
}: {
  ikon: typeof Contrast; baslik: string; aciklama: string;
  acik: boolean; degistir: () => void;
}) {
  return (
    <section className="flex items-start gap-4">
      <Ikon size={20} className="mt-0.5 shrink-0 text-metin-ikincil" />
      <div className="flex-1 min-w-0">
        <h2 className="font-semibold text-[17px]">{baslik}</h2>
        <p className="text-[14px] text-metin-ikincil mt-0.5">{aciklama}</p>
      </div>
      <button
        type="button" role="switch" aria-checked={acik} aria-label={baslik}
        onClick={degistir}
        className={`w-[52px] h-[30px] rounded-full p-[3px] shrink-0 transition-colors
                    ${acik ? "bg-mavi" : "bg-yukseltilmis"}`}
      >
        <span className={`block w-6 h-6 rounded-full bg-white transition-transform
                          ${acik ? "translate-x-[22px]" : ""}`} />
      </button>
    </section>
  );
}

function GenelBolum({ ad }: { ad: string }) {
  return (
    <div className="px-6 pb-10 max-w-2xl">
      <p className="text-[15px] text-metin-ikincil">
        {ad} bölümü, NSosyal altyapısıyla entegrasyon aşamasında platformun kendi
        ayar servislerine bağlanacaktır. Bu prototipte simülasyon amaçlı yer tutucu
        olarak bulunmaktadır.
      </p>
    </div>
  );
}
