/**
 * MİHENK — İçerik üretici öneri motoru.
 *
 * KVKK ilkesi: Bu modül tekil kullanıcı davranışını İZLEMEZ. Yalnızca
 * kişisel bilgilerden arındırılmış, toplulaştırılmış etkileşim sinyallerini
 * (saat, gün, kategori, segment, takipçi aralığı) kullanır. Hiçbir çıktı
 * tek bir kişiye geri izlenemez.
 */
import type { Etkilesim, Kategori } from "../tipler";
import { etkilesimler, olaylariGetir } from "../veri";
import { kumeTonDagilimi } from "../analiz/tonAnalizi";

const GUN_ADI = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"];

export interface ZamanOnerisi {
  gun: number;
  gunAdi: string;
  saat: number;
  etkilesimSayisi: number;
}

/** Toplulaştırılmış etkileşimlerden en verimli paylaşım pencerelerini çıkarır */
export function zamanOnerileri(kategori?: Kategori, adet = 3): ZamanOnerisi[] {
  const kaynak: Etkilesim[] = kategori
    ? etkilesimler.filter((e) => e.kategori === kategori)
    : etkilesimler;

  const izgara = new Map<string, number>();
  for (const e of kaynak) {
    const anahtar = `${e.gun}-${e.saat}`;
    izgara.set(anahtar, (izgara.get(anahtar) ?? 0) + 1);
  }

  return [...izgara.entries()]
    .map(([anahtar, sayi]) => {
      const [gun, saat] = anahtar.split("-").map(Number);
      return { gun, gunAdi: GUN_ADI[gun], saat, etkilesimSayisi: sayi };
    })
    .sort((a, b) => b.etkilesimSayisi - a.etkilesimSayisi)
    .slice(0, adet);
}

/** Saatlik etkileşim yoğunluğu — ısı grafiği için */
export function saatlikYogunluk(kategori?: Kategori): number[] {
  const kaynak = kategori ? etkilesimler.filter((e) => e.kategori === kategori) : etkilesimler;
  const dizi = new Array(24).fill(0);
  for (const e of kaynak) dizi[e.saat]++;
  return dizi;
}

export interface KonuOnerisi {
  baslik: string;
  kategori: Kategori;
  gonderiSayisi: number;
  ilgi: number;          // 0-1
  tonNotu: string;
}

/** Gündemdeki olaylardan konu önerisi üretir */
export function konuOnerileri(adet = 5): KonuOnerisi[] {
  const olaylar = olaylariGetir();
  const enYuksek = Math.max(...olaylar.map((o) => o.gonderiler.length), 1);

  return olaylar.slice(0, adet).map((o) => {
    const ton = kumeTonDagilimi(o.gonderiler);
    const baskin = ton.oranlar.olumsuz > 0.45
      ? "Tartışma eleştirel bir tonda ilerliyor — dengeli bir bakış öne çıkabilir."
      : ton.oranlar.olumlu > 0.45
        ? "Konuya ilgi olumlu — açıklayıcı içerik iyi karşılanabilir."
        : "Ton dengeli — bilgilendirici içerik için uygun zemin.";

    return {
      baslik: o.baslik,
      kategori: o.kategori,
      gonderiSayisi: o.gonderiler.length,
      ilgi: o.gonderiler.length / enYuksek,
      tonNotu: baskin,
    };
  });
}

/** Takipçi tabanının anonim segment dağılımı */
export function kitleDagilimi() {
  const araliklar = new Map<string, number>();
  for (const e of etkilesimler) {
    araliklar.set(e.takipci_araligi, (araliklar.get(e.takipci_araligi) ?? 0) + 1);
  }
  const toplam = etkilesimler.length || 1;
  return [...araliklar.entries()]
    .map(([aralik, sayi]) => ({ aralik, sayi, oran: sayi / toplam }))
    .sort((a, b) => b.sayi - a.sayi);
}
