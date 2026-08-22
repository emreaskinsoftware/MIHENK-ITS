"use client";

export function UstSekmeler<T extends string>({
  sekmeler, aktif, degistir,
}: { sekmeler: readonly T[]; aktif: T; degistir: (s: T) => void }) {
  return (
    <div
      role="tablist"
      className="sticky top-0 z-20 flex bg-zemin/85 backdrop-blur-md border-b border-cizgi overflow-x-auto"
    >
      {sekmeler.map((s) => {
        const secili = s === aktif;
        return (
          <button
            key={s}
            role="tab"
            aria-selected={secili}
            onClick={() => degistir(s)}
            className={`flex-1 min-w-[110px] py-4 text-[15px] relative transition-colors
                        ${secili ? "font-semibold text-metin" : "font-medium text-metin-ikincil hover:text-metin"}`}
          >
            {s}
            {secili && (
              <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[60%] h-[3px] rounded-full bg-mavi" />
            )}
          </button>
        );
      })}
    </div>
  );
}
