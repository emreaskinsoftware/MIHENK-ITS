/**
 * MİHENK — Ton ve toksisite analizi (sözlük tabanlı TEMEL model).
 *
 * Bu, çıkarımsal özetleyiciyle aynı rolü oynar: dış servise ihtiyaç duymadan
 * çalışan bir referans noktasıdır. Eğitilecek Türkçe sınıflandırıcının
 * başarımı buna karşı ölçülecektir (bkz. rapor 3.2).
 *
 * Sözlük tabanlı yaklaşımın bilinen sınırı: bağlamı ve ironiyi kaçırır.
 * Bu sınır raporda açıkça belirtilmekte, üretici model ile aşılması
 * hedeflenmektedir.
 */
import type { AkisOgesi } from "../tipler";

const OLUMSUZ = [
  "sorun", "eksik", "yetersiz", "muğlak", "temkinli", "sonuçsuz", "kimse",
  "maliyet", "asıl", "yine", "iddia", "belirsiz", "tartışma", "kaygı",
];
const OLUMLU = [
  "teşekkür", "sevindim", "iyi", "doğru", "somut", "beklenen", "güzel",
  "keyif", "rahatlama", "başarı", "gelişme", "destek",
];
const KESKINLIK = ["!", "?!", "kesin", "asla", "hemen", "acil"];

export type Ton = "olumlu" | "notr" | "olumsuz";

export interface TonSonucu {
  ton: Ton;
  puan: number;        // -1 (olumsuz) .. +1 (olumlu)
  keskinlik: number;   // 0..1 — üslup sertliği
}

export function tonCozumle(metin: string): TonSonucu {
  const kucuk = metin.toLocaleLowerCase("tr-TR");
  const say = (liste: string[]) => liste.reduce((t, k) => t + (kucuk.includes(k) ? 1 : 0), 0);

  const eksi = say(OLUMSUZ);
  const arti = say(OLUMLU);
  const toplam = eksi + arti;
  const puan = toplam === 0 ? 0 : (arti - eksi) / toplam;

  return {
    ton: puan > 0.25 ? "olumlu" : puan < -0.25 ? "olumsuz" : "notr",
    puan,
    keskinlik: Math.min(1, say(KESKINLIK) / 3),
  };
}

/** Bir olay kümesinin genel duygu dağılımı — içerik üretici paneli kullanır */
export function kumeTonDagilimi(gonderiler: AkisOgesi[]) {
  const sayim = { olumlu: 0, notr: 0, olumsuz: 0 };
  for (const g of gonderiler) sayim[tonCozumle(g.metin).ton]++;
  const toplam = gonderiler.length || 1;
  return {
    ...sayim,
    oranlar: {
      olumlu: sayim.olumlu / toplam,
      notr: sayim.notr / toplam,
      olumsuz: sayim.olumsuz / toplam,
    },
  };
}
