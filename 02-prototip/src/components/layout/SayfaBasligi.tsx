"use client";

import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";

export function SayfaBasligi({
  baslik, sagEylem,
}: { baslik: string; sagEylem?: React.ReactNode }) {
  const yonlendirici = useRouter();
  return (
    <header className="flex items-center gap-4 px-5 py-4">
      <button
        type="button"
        onClick={() => yonlendirici.back()}
        aria-label="Geri dön"
        className="p-1.5 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover"
      >
        <ArrowLeft size={20} />
      </button>
      <h1 className="text-[20px] font-bold">{baslik}</h1>
      {sagEylem && <div className="ml-auto">{sagEylem}</div>}
    </header>
  );
}
