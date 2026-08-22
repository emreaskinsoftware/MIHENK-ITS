import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Kabuk } from "@/components/layout/Kabuk";
import { TEMA_BETIGI } from "@/components/layout/TemaSaglayici";
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
    // `suppressHydrationWarning`: aşağıdaki betik, React hidrasyona başlamadan
    // önce `data-tema` özniteliğini yazıyor. Bastırma yalnızca bu öğenin
    // ÖZNİTELİKLERİNİ kapsar, ağacın içeriğini değil.
    <html lang="tr" className={inter.variable} suppressHydrationWarning>
      <head>
        {/* Tema tercihi ilk boyamadan ÖNCE uygulanır; yanlış temanın bir kare
            görünüp değişmesini (flash of wrong theme) engeller. */}
        <script dangerouslySetInnerHTML={{ __html: TEMA_BETIGI }} />
      </head>
      <body>
        <a
          href="#ana-icerik"
          className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50
                     focus:bg-mavi-koyu focus:text-white focus:px-4 focus:py-2 focus:rounded-lg"
        >
          Ana içeriğe geç
        </a>
        {/* Tema için sağlayıcı bileşeni yok: `useTema` durumu doğrudan
            `<html data-tema>` özniteliğinden okuyor (bkz. TemaSaglayici.tsx).
            Araya context koymak yalnızca ikinci bir kopya ve dolaylılık
            eklerdi. */}
        <Kabuk>{children}</Kabuk>
      </body>
    </html>
  );
}
