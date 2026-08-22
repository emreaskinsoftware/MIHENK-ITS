"use client";

import { useState } from "react";
import { Sidebar } from "./Sidebar";
import { SagRay } from "./SagRay";
import { MobilGezinme } from "./MobilGezinme";
import { GonderiModali } from "../akis/GonderiModali";

export function Kabuk({ children }: { children: React.ReactNode }) {
  const [modal, setModal] = useState(false);

  return (
    <>
      <MobilGezinme yeniGonderi={() => setModal(true)} />
      <div className="mx-auto flex max-w-[1500px] gap-2">
        <div className="max-lg:hidden">
          <Sidebar yeniGonderi={() => setModal(true)} />
        </div>
        <main id="ana-icerik" className="flex-1 min-w-0 border-x border-cizgi min-h-screen max-lg:border-x-0 max-lg:pb-20">
          {children}
        </main>
        <SagRay />
      </div>
      {modal && <GonderiModali kapat={() => setModal(false)} />}
    </>
  );
}
