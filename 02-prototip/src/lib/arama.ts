import { akisGetir, kullanicilar, olaylariGetir } from "./veri";
import type { AkisOgesi, Kullanici } from "./tipler";

/** Türkçe duyarlı normalleştirme — büyük/küçük ve aksan farkını yok sayar */
function normalize(s: string): string {
  return s
    .toLocaleLowerCase("tr-TR")
    .replace(/ı/g, "i").replace(/İ/g, "i")
    .replace(/ş/g, "s").replace(/ğ/g, "g")
    .replace(/ü/g, "u").replace(/ö/g, "o").replace(/ç/g, "c")
    .trim();
}

export interface AramaSonucu {
  gonderiler: AkisOgesi[];
  hesaplar: Kullanici[];
  etiketler: { baslik: string; sayi: number }[];
}

export function ara(sorgu: string): AramaSonucu {
  const q = normalize(sorgu);
  if (q.length < 2) return { gonderiler: [], hesaplar: [], etiketler: [] };

  const gonderiler = akisGetir().filter(
    (g) => normalize(g.metin).includes(q) || normalize(g.olay_basligi ?? "").includes(q),
  );

  const hesaplar = kullanicilar.filter((k) => normalize(k.kullanici_adi).includes(q));

  const etiketler = olaylariGetir()
    .filter((o) => normalize(o.baslik).includes(q))
    .map((o) => ({ baslik: o.baslik, sayi: o.gonderiler.length }));

  return { gonderiler: gonderiler.slice(0, 30), hesaplar: hesaplar.slice(0, 10), etiketler };
}
