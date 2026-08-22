"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, ExternalLink, HelpCircle, Loader2, ShieldQuestion, X } from "lucide-react";
import type { AkisOgesi } from "@/lib/tipler";

interface DogrulamaSonucu {
  sonuc: "DOGRULANDI" | "YANLIS" | "DOGRULANAMADI";
  guven: number;
  aciklama: string;
  kaynaklar: { baslik: string; url: string }[];
  saglayici: string;
  not?: string;
  iddia: string;
}

const GORUNUM = {
  DOGRULANDI: { ikon: CheckCircle2, renk: "var(--color-basari)", etiket: "Doğrulandı" },
  YANLIS: { ikon: AlertTriangle, renk: "var(--color-tehlike)", etiket: "Yanlış" },
  DOGRULANAMADI: { ikon: HelpCircle, renk: "var(--color-metin-ikincil)", etiket: "Doğrulanamadı" },
} as const;

export function DogrulamaPaneli({
  gonderi, kapat,
}: { gonderi: AkisOgesi; kapat: () => void }) {
  const [sonuc, setSonuc] = useState<DogrulamaSonucu | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [hata, setHata] = useState<string | null>(null);

  useEffect(() => {
    let iptal = false;
    fetch("/api/dogrula", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ gonderiId: gonderi.id }),
    })
      .then((y) => y.json())
      .then((v) => { if (!iptal) { setSonuc(v); setYukleniyor(false); } })
      .catch(() => { if (!iptal) { setHata("Doğrulama şu anda yapılamadı."); setYukleniyor(false); } });
    return () => { iptal = true; };
  }, [gonderi.id]);

  const g = sonuc ? GORUNUM[sonuc.sonuc] : null;
  const Ikon = g?.ikon ?? ShieldQuestion;

  return (
    <div className="mt-3 rounded-xl border border-cizgi bg-zemin p-4">
      <header className="flex items-center gap-2.5 mb-3">
        <ShieldQuestion size={17} className="text-mihenk shrink-0" />
        <h3 className="font-semibold text-[14px]">MİHENK Doğrulama</h3>
        <button type="button" onClick={kapat} aria-label="Doğrulama panelini kapat"
                className="ml-auto p-1 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover">
          <X size={16} />
        </button>
      </header>

      {yukleniyor && (
        <div className="flex items-center gap-2.5 text-[14px] text-metin-ikincil py-2">
          <Loader2 size={16} className="animate-spin" />
          Kaynaklar taranıyor…
        </div>
      )}

      {hata && <p className="text-[14px] text-tehlike">{hata}</p>}

      {sonuc && !yukleniyor && (
        <>
          <div className="flex items-center gap-2.5 mb-2">
            <Ikon size={20} style={{ color: g!.renk }} className="shrink-0" />
            <span className="font-semibold text-[15px]" style={{ color: g!.renk }}>
              {g!.etiket}
            </span>
            {sonuc.guven > 0 && (
              <span className="ml-auto text-[13px] text-metin-ikincil">
                Güven <strong className="text-metin tabular-nums">%{sonuc.guven}</strong>
              </span>
            )}
          </div>

          {sonuc.guven > 0 && (
            <div className="h-1.5 rounded-full bg-yukseltilmis overflow-hidden mb-3"
                 role="img" aria-label={`Güven düzeyi yüzde ${sonuc.guven}`}>
              <span className="block h-full rounded-full transition-[width]"
                    style={{ width: `${sonuc.guven}%`, background: g!.renk }} />
            </div>
          )}

          <p className="text-[13px] text-metin-ikincil italic mb-2 line-clamp-2">
            Sınanan iddia: “{sonuc.iddia}”
          </p>
          <p className="text-[14px] leading-relaxed">{sonuc.aciklama}</p>

          {sonuc.sonuc === "DOGRULANAMADI" && (
            <p className="mt-2.5 text-[13px] text-metin-ikincil bg-yukseltilmis rounded-lg px-3 py-2">
              <strong>Not:</strong> “Doğrulanamadı”, iddianın yanlış olduğu anlamına gelmez.
              Yeterli kaynak bulunamadığında sistem hüküm vermez; nihai karar sizindir.
            </p>
          )}

          {sonuc.kaynaklar.length > 0 && (
            <div className="mt-3">
              <p className="text-[13px] font-medium text-metin-ikincil mb-1.5">
                Kaynaklar ({sonuc.kaynaklar.length})
              </p>
              <ul className="flex flex-col gap-1.5">
                {sonuc.kaynaklar.slice(0, 5).map((k) => (
                  <li key={k.url}>
                    <a href={k.url} target="_blank" rel="noopener noreferrer"
                       className="flex items-start gap-1.5 text-[13px] text-mavi hover:underline">
                      <ExternalLink size={13} className="mt-0.5 shrink-0" />
                      <span className="line-clamp-1">{k.baslik}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {sonuc.not && (
            <p className="mt-3 text-[12px] text-metin-sonuk border-t border-cizgi pt-2">
              {sonuc.not}
            </p>
          )}
        </>
      )}
    </div>
  );
}
