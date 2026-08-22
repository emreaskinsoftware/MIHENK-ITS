import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Sidebar } from "@/components/layout/Sidebar";
import { SagRay } from "@/components/layout/SagRay";
import { TemaSaglayici } from "@/components/layout/TemaSaglayici";
import "./globals.css";

const inter = Inter({ subsets: ["latin", "latin-ext"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "MİHENK — NSosyal Simülasyon Prototipi",
  description:
    "Yapay zekâ destekli kategori bazlı özet, doğrulama ve görsel köken denetimi katmanı. " +
    "NSosyal deneyimini simüle eden çalışan prototip.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr" className={inter.variable}>
      <body>
        <a
          href="#ana-icerik"
          className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50
                     focus:bg-mavi focus:text-white focus:px-4 focus:py-2 focus:rounded-lg"
        >
          Ana içeriğe geç
        </a>
        <TemaSaglayici>
        <div className="mx-auto flex max-w-[1500px] gap-2">
          <Sidebar />
          <main id="ana-icerik" className="flex-1 min-w-0 border-x border-cizgi min-h-screen">
            {children}
          </main>
          <SagRay />
        </div>
        </TemaSaglayici>
      </body>
    </html>
  );
}
