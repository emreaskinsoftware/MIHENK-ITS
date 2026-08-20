/**
 * Kurgusal kullanıcılar için deterministik gradyan avatar.
 * Gerçek kişi fotoğrafı kullanılmaz; simülasyon verisi kurgusaldır.
 */
const PALET = [
  ["#2e90fa", "#22c7e8"],
  ["#7c5cf0", "#a78bfa"],
  ["#f5a524", "#f97316"],
  ["#22c55e", "#14b8a6"],
  ["#f4525f", "#ec4899"],
  ["#0ea5e9", "#6366f1"],
];

function tohumla(anahtar: string) {
  let t = 0;
  for (let i = 0; i < anahtar.length; i++) t = (t * 31 + anahtar.charCodeAt(i)) >>> 0;
  return t;
}

export function Avatar({
  ad,
  boyut = 44,
  halka = false,
}: {
  ad: string;
  boyut?: number;
  halka?: boolean;
}) {
  const [a, b] = PALET[tohumla(ad) % PALET.length];
  const bashari = ad.replace(/[^\p{L}]/gu, "").slice(0, 2).toLocaleUpperCase("tr-TR");
  return (
    <div
      className={halka ? "rounded-full p-[2px] gradyan-marka shrink-0" : "shrink-0"}
      style={halka ? { width: boyut + 6, height: boyut + 6 } : undefined}
    >
      <div
        aria-hidden="true"
        className="rounded-full grid place-items-center font-semibold text-white select-none"
        style={{
          width: boyut,
          height: boyut,
          fontSize: boyut * 0.36,
          backgroundImage: `linear-gradient(135deg, ${a}, ${b})`,
          border: halka ? "2px solid var(--color-zemin)" : undefined,
        }}
      >
        {bashari}
      </div>
    </div>
  );
}
