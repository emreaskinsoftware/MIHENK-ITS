/**
 * Gönderi asistanı çekmecesi (spec 6.3 / 6.9).
 *
 * ÜRÜN KARARI — REDDETME BİR HATA GİBİ GÖSTERİLMEZ:
 * Asistan "bu gönderiden çıkarılamıyor" dediğinde bunu kırmızı bir hata
 * kutusunda göstermek, kullanıcıya sistemin bozulduğunu düşündürür. Oysa bu
 * doğru davranıştır ve ürünün ayırt edici özelliğidir. Bu yüzden reddetme
 * nötr bir bilgi kutusunda, gerekçesiyle birlikte sunulur.
 *
 * ERİŞİLEBİLİRLİK: Çekmece açıldığında odak içeri taşınır, Escape ile kapanır,
 * yanıt alanı `aria-live` ile duyurulur.
 */
import { useEffect, useRef, useState } from "react";
import { api, type AsistanYaniti, type Gonderi } from "../lib/api";

interface Ozellikler {
  gonderi: Gonderi;
  onKapat: () => void;
  onKaynagaGit: (postId: string) => void;
}

const RED_ACIKLAMALARI: Record<string, string> = {
  baglamda_yok: "Bu sorunun cevabı gönderide ve alıntı zincirinde bulunmuyor.",
  enjeksiyon_supheli: "Bu istek, asistanın kurallarını değiştirmeye yönelik göründü.",
  cikti_kisiti: "Üretilen yanıt güvenlik kısıtlarına takıldı (bağlantı veya talimat içeriyordu).",
  atifsiz: "Yanıt kaynağa bağlanamadı, bu yüzden gösterilmiyor.",
};

export function AsistanCekmecesi({ gonderi, onKapat, onKaynagaGit }: Ozellikler) {
  const [soru, setSoru] = useState("");
  const [yanit, setYanit] = useState<AsistanYaniti | null>(null);
  const [yukleniyor, setYukleniyor] = useState(false);
  const girdiRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Çekmece açılınca odak içeri: klavye kullanıcısı arka plandaki akışta
    // kaybolmasın.
    girdiRef.current?.focus();
    function tusla(olay: KeyboardEvent) {
      if (olay.key === "Escape") onKapat();
    }
    window.addEventListener("keydown", tusla);
    return () => window.removeEventListener("keydown", tusla);
  }, [onKapat]);

  async function sor(metin?: string) {
    setYukleniyor(true);
    try {
      setYanit(await api.sor(gonderi.id, metin ?? soru));
    } finally {
      setYukleniyor(false);
    }
  }

  return (
    <aside
      role="dialog"
      aria-modal="true"
      aria-labelledby="asistan-baslik"
      className="fixed inset-y-0 right-0 z-30 flex w-full max-w-md flex-col border-l border-mihenk-cizgi bg-white shadow-xl"
    >
      <header className="flex items-center justify-between border-b border-mihenk-cizgi p-4">
        <h2 id="asistan-baslik" className="text-base font-semibold">
          Gönderi asistanı
        </h2>
        <button
          type="button"
          onClick={onKapat}
          className="min-h-dokunma min-w-dokunma rounded-md px-3 text-sm text-mihenk-ikincil hover:text-mihenk-metin"
          aria-label="Asistan çekmecesini kapat"
        >
          ✕
        </button>
      </header>

      <div className="flex-1 overflow-y-auto p-4">
        <p className="mb-1 text-xs font-medium uppercase tracking-wide text-mihenk-ikincil">
          Bağlam
        </p>
        <blockquote className="mb-4 rounded-md border border-mihenk-cizgi bg-mihenk-zemin p-3 text-sm">
          {gonderi.text}
        </blockquote>

        <p className="mb-2 text-xs text-mihenk-ikincil">
          Asistan yalnızca bu gönderi, alıntı zinciri ve doğrudan yanıtlarla
          sınırlıdır. Bağlam dışına çıkmaz, tahmin yürütmez.
        </p>

        <div className="mb-4 flex flex-wrap gap-2">
          {["Bu gönderi ne diyor?", "Kim ne iddia ediyor?"].map((h) => (
            <button
              key={h}
              type="button"
              onClick={() => {
                setSoru(h);
                void sor(h);
              }}
              className="min-h-dokunma rounded-full border border-mihenk-cizgi px-3 py-1 text-xs hover:bg-mihenk-zemin"
            >
              {h}
            </button>
          ))}
        </div>

        <div aria-live="polite">
          {yukleniyor && <p className="text-sm text-mihenk-ikincil">Yanıt hazırlanıyor…</p>}

          {yanit && !yukleniyor && (
            <div
              className={`rounded-md border p-3 ${
                yanit.refused
                  ? "border-mihenk-cizgi bg-mihenk-zemin"
                  : "border-mihenk-vurgu bg-mihenk-vurgu-acik"
              }`}
            >
              <p className="text-sm">{yanit.answer}</p>

              {yanit.refused && yanit.refusal_reason && (
                <p className="mt-2 text-xs text-mihenk-ikincil">
                  <span aria-hidden="true">ℹ </span>
                  {RED_ACIKLAMALARI[yanit.refusal_reason] ?? yanit.refusal_reason}
                </p>
              )}

              {!yanit.refused && yanit.source_post_ids.length > 0 && (
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <span className="text-xs text-mihenk-ikincil">Kaynak:</span>
                  {yanit.source_post_ids.map((id) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => onKaynagaGit(id)}
                      className="min-h-dokunma rounded-full border border-mihenk-vurgu px-3 py-1 text-xs font-medium text-mihenk-vurgu hover:bg-white"
                      aria-label={`${id} numaralı kaynak gönderiye git`}
                    >
                      {id}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <form
        className="border-t border-mihenk-cizgi p-4"
        onSubmit={(e) => {
          e.preventDefault();
          if (soru.trim()) void sor();
        }}
      >
        <label htmlFor="asistan-soru" className="block text-sm font-medium">
          Sorunuz
        </label>
        <div className="mt-1 flex gap-2">
          <input
            id="asistan-soru"
            ref={girdiRef}
            value={soru}
            onChange={(e) => setSoru(e.target.value)}
            className="min-h-dokunma flex-1 rounded-md border border-mihenk-cizgi px-3 py-2 text-sm"
            placeholder="Bu gönderide ne anlatılıyor?"
          />
          <button
            type="submit"
            disabled={!soru.trim() || yukleniyor}
            className="min-h-dokunma min-w-dokunma rounded-md bg-mihenk-vurgu px-4 text-sm font-medium text-white disabled:opacity-50"
          >
            Sor
          </button>
        </div>
      </form>
    </aside>
  );
}
