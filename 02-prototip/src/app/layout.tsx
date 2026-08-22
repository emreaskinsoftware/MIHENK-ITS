import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Kabuk } from "@/components/layout/Kabuk";
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
          <Kabuk>{children}</Kabuk>
        </TemaSaglayici>
      </body>
    </html>
  );
}
