"use client";

import { GonderiKarti } from "@/components/akis/GonderiKarti";
import { SayfaBasligi } from "@/components/layout/SayfaBasligi";
import { akisGetir } from "@/lib/veri";

export default function BegenilerSayfasi() {
  const begenilenler = akisGetir().filter((g) => g.begeni > 30).slice(0, 12);
  return (
    <>
      <SayfaBasligi baslik="Beğeniler" />
      {begenilenler.map((g) => <GonderiKarti key={g.id} gonderi={g} />)}
    </>
  );
}
