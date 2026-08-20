import kullanicilarHam from "../../data/kullanicilar.json";
import gonderilerHam from "../../data/gonderiler.json";
import etkilesimlerHam from "../../data/etkilesimler.json";
import type { AkisOgesi, Etkilesim, Gonderi, Kategori, Kullanici } from "./tipler";

export const kullanicilar = kullanicilarHam as Kullanici[];
export const gonderiler = gonderilerHam as Gonderi[];
export const etkilesimler = etkilesimlerHam as Etkilesim[];

const kullaniciDizini = new Map(kullanicilar.map((k) => [k.id, k]));

export function yazarGetir(id: string): Kullanici {
  const k = kullaniciDizini.get(id);
  if (!k) throw new Error(`Kullanıcı bulunamadı: ${id}`);
  return k;
}

/**
 * Kronolojik akış. NSosyal algoritmasız bir platformdur; MİHENK sıralamaya
 * müdahale etmez, yalnızca üzerine bir okuma katmanı ekler.
 */
export function akisGetir(limit?: number): AkisOgesi[] {
  const liste = gonderiler.map((g) => ({ ...g, yazar: yazarGetir(g.yazar_id) }));
  return typeof limit === "number" ? liste.slice(0, limit) : liste;
}

export function gonderiGetir(id: string): AkisOgesi | undefined {
  const g = gonderiler.find((x) => x.id === id);
  return g ? { ...g, yazar: yazarGetir(g.yazar_id) } : undefined;
}

export function kategoriyeGoreGetir(kategori: Kategori): AkisOgesi[] {
  return akisGetir().filter((g) => g.kategori === kategori);
}

/** Bir olay kümesindeki tüm gönderiler — özet ve tarafsızlık modülünün girdisi */
export function olayKumesiGetir(olayId: string): AkisOgesi[] {
  return akisGetir().filter((g) => g.olay_id === olayId);
}

/** Akıştaki olay kümeleri, gönderi sayısına göre azalan */
export function olaylariGetir(kategori?: Kategori) {
  const harita = new Map<string, { olayId: string; baslik: string; kategori: Kategori; gonderiler: AkisOgesi[] }>();
  for (const g of akisGetir()) {
    if (!g.olay_id || !g.olay_basligi) continue;
    if (kategori && g.kategori !== kategori) continue;
    const mevcut = harita.get(g.olay_id);
    if (mevcut) mevcut.gonderiler.push(g);
    else harita.set(g.olay_id, { olayId: g.olay_id, baslik: g.olay_basligi, kategori: g.kategori, gonderiler: [g] });
  }
  return [...harita.values()].sort((a, b) => b.gonderiler.length - a.gonderiler.length);
}

/** Sağ raydaki "Popüler" etiket listesi */
export function populerEtiketler() {
  return olaylariGetir()
    .slice(0, 5)
    .map((o) => ({
      etiket: o.baslik.split(" ").slice(0, 2).join(""),
      baslik: o.baslik,
      sayi: o.gonderiler.reduce((t, g) => t + g.begeni + g.yanit_sayisi, 0),
    }));
}
