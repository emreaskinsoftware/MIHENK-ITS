"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

type Tema = "koyu" | "acik";
const Baglam = createContext<{ tema: Tema; degistir: () => void }>({
  tema: "koyu",
  degistir: () => {},
});

export const temaKullan = () => useContext(Baglam);

export function TemaSaglayici({ children }: { children: React.ReactNode }) {
  const [tema, setTema] = useState<Tema>("koyu");

  useEffect(() => {
    const kayitli = localStorage.getItem("mihenk-tema") as Tema | null;
    if (kayitli) {
      setTema(kayitli);
      document.documentElement.dataset.tema = kayitli;
    }
  }, []);

  const degistir = useCallback(() => {
    setTema((onceki) => {
      const yeni = onceki === "koyu" ? "acik" : "koyu";
      document.documentElement.dataset.tema = yeni;
      localStorage.setItem("mihenk-tema", yeni);
      return yeni;
    });
  }, []);

  return <Baglam.Provider value={{ tema, degistir }}>{children}</Baglam.Provider>;
}
