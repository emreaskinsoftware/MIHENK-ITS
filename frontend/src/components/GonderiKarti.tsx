/**
 * Akış kartı (spec 6.9, ekran 1).
 *
 * Kart üç şey taşır: gönderi metni, asistan düğmesi, köken ve YZ sinyali.
 * Sinyaller yalnızca gösterilecek bir şey varsa çizilir; çekimserlik durumunda
 * kartın alt şeridi tamamen boş kalır (spec 6.9 tasarım kuralı).
 *
 * ÜRETİCİYİ KORUMA (spec 1, ek kural): Kart, atomik özeti DEĞİL, gönderinin
 * kendi metnini gösterir. Özet yalnızca özet panelindedir ve oradan kaynağa
 * dönülür. Akışta özeti göstermek, kullanıcıyı orijinal gönderiden koparırdı.
 */
import type { Gonderi, KokenSonucu, TespitSonucu } from "../lib/api";
import { KokenGostergesi } from "./KokenGostergesi";
import { YzSinyali } from "./YzSinyali";

interface Ozellikler {
  gonderi: Gonderi;
  tespit: TespitSonucu | null;
  koken: KokenSonucu[];
  vurgulu: boolean;
  itirazVar: boolean;
  onAsistan: (gonderi: Gonderi) => void;
  onItiraz: (postId: string) => void;
}

function saatBicimle(isoTarih: string): string {
  const t = new Date(isoTarih);
  return t.toLocaleString("tr-TR", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

export function GonderiKarti({
  gonderi,
  tespit,
  koken,
  vurgulu,
  itirazVar,
  onAsistan,
  onItiraz,
}: Ozellikler) {
  const gosterilecekKoken = koken.filter((k) => k.display);

  return (
    <article
      id={`gonderi-${gonderi.id}`}
      // tabIndex -1: kaynak çipinden gelindiğinde odaklanabilsin, ama Tab
      // sırasına girip klavye gezinmesini uzatmasın.
      tabIndex={-1}
      className={`rounded-lg border border-mihenk-cizgi bg-white p-4 transition-colors ${
        vurgulu ? "gonderi-vurgulu" : ""
      }`}
      aria-labelledby={`yazar-${gonderi.id}`}
    >
      <header className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
        <div className="flex items-baseline gap-2">
          <span id={`yazar-${gonderi.id}`} className="text-sm font-semibold">
            {gonderi.author_id}
          </span>
          <span className="text-xs text-mihenk-ikincil">{saatBicimle(gonderi.created_at)}</span>
        </div>
        <span className="rounded-full bg-mihenk-zemin px-2 py-0.5 text-xs text-mihenk-ikincil">
          {gonderi.id}
        </span>
      </header>

      <p className="whitespace-pre-wrap text-[15px] leading-relaxed">{gonderi.text}</p>

      {gonderi.media.length > 0 && (
        <p className="mt-2 text-xs text-mihenk-ikincil">
          <span aria-hidden="true">🖼 </span>
          {gonderi.media.length} görsel ekli
        </p>
      )}

      <footer className="mt-3 flex flex-wrap items-center gap-3 border-t border-mihenk-cizgi pt-3">
        <button
          type="button"
          onClick={() => onAsistan(gonderi)}
          className="min-h-dokunma rounded-md border border-mihenk-cizgi px-3 py-2 text-sm font-medium hover:bg-mihenk-zemin"
          aria-label={`${gonderi.id} numaralı gönderi için asistanı aç`}
        >
          <span aria-hidden="true">💬 </span>
          Asistana sor
        </button>

        {gosterilecekKoken.map((k) => (
          <KokenGostergesi key={k.media_id} koken={k} />
        ))}

        <YzSinyali
          postId={gonderi.id}
          tespit={tespit}
          itirazVar={itirazVar}
          onItiraz={onItiraz}
        />
      </footer>
    </article>
  );
}
