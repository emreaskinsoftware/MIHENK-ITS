import type { CerceveDagilimi } from "@/lib/ozet/cikarimsal";
import { CERCEVE_ETIKET } from "@/lib/tipler";

const RENK: Record<string, string> = {
  notr: "#8a97a6",
  destekleyici: "#22c55e",
  elestirel: "#f5a524",
  soru: "#2e90fa",
  yanlis_bilgi: "#f4525f",
};

/**
 * Özet tarafsızlığı göstergesi.
 * Özetin hangi çerçeve dağılımından üretildiğini kullanıcıya açık eder —
 * MİHENK'in algoritmik önyargıya karşı temel tasarım kararı.
 */
export function DengeCubugu({
  dagilim, dengeSkoru,
}: { dagilim: CerceveDagilimi[]; dengeSkoru: number }) {
  const gorunur = dagilim.filter((d) => d.adet > 0);
  const yuzde = Math.round(dengeSkoru * 100);

  return (
    <div className="mt-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[13px] font-medium text-metin-ikincil">Çerçeve dağılımı</span>
        <span className="text-[13px] text-metin-ikincil">
          Denge <strong className="text-metin tabular-nums">%{yuzde}</strong>
        </span>
      </div>

      <div
        className="flex h-2 rounded-full overflow-hidden bg-yukseltilmis"
        role="img"
        aria-label={
          "Çerçeve dağılımı: " +
          gorunur.map((d) => `${CERCEVE_ETIKET[d.cerceve]} %${Math.round(d.oran * 100)}`).join(", ")
        }
      >
        {gorunur.map((d) => (
          <span
            key={d.cerceve}
            style={{ width: `${d.oran * 100}%`, background: RENK[d.cerceve] }}
          />
        ))}
      </div>

      <ul className="flex flex-wrap gap-x-4 gap-y-1 mt-2.5">
        {gorunur.map((d) => (
          <li key={d.cerceve} className="flex items-center gap-1.5 text-[12px] text-metin-ikincil">
            <span className="w-2 h-2 rounded-full shrink-0" style={{ background: RENK[d.cerceve] }} />
            {CERCEVE_ETIKET[d.cerceve]}
            <span className="tabular-nums">{d.adet}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
