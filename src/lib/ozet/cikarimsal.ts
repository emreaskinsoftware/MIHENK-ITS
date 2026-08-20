/**
 * MİHENK — Çıkarımsal (extractive) özet temel modeli.
 *
 * Bu modül, dış servise ihtiyaç duymadan çalışan bir TEMEL (baseline)
 * özetleyicidir. İki amacı vardır:
 *   1. Prototipin API erişimi olmadan da uçtan uca çalışması,
 *   2. İnce ayarlanmış üretici modelin başarımının karşılaştırılacağı
 *      referans noktasını oluşturmak (bkz. rapor 3.2).
 *
 * Tarafsızlık yaklaşımı: özet, en çok etkileşim alan gönderileri değil,
 * her ÇERÇEVEDEN en temsili gönderiyi seçer. Böylece baskın çerçevenin
 * özeti tek yönlü sürüklemesi engellenir.
 */
import type { AkisOgesi, Cerceve, Kategori } from "../tipler";
import { KATEGORI_ETIKET } from "../tipler";
import { olaylariGetir } from "../veri";

export interface CerceveDagilimi {
  cerceve: Cerceve;
  adet: number;
  oran: number;
}

export interface OlayOzeti {
  olayId: string;
  baslik: string;
  kategori: Kategori;
  ozet: string;
  gonderiSayisi: number;
  kaynakSayisi: number;
  dagilim: CerceveDagilimi[];
  /** 0-1; 1 = çerçeveler tam dengeli, 0 = tek çerçeve baskın */
  dengeSkoru: number;
  dogrulanmamisIddiaVar: boolean;
}

export interface KategoriOzeti {
  kategori: Kategori;
  baslik: string;
  olaylar: OlayOzeti[];
  toplamGonderi: number;
}

/** Normalleştirilmiş Shannon entropisi — çerçeve dengesinin ölçüsü */
function dengeHesapla(dagilim: CerceveDagilimi[]): number {
  const gecerli = dagilim.filter((d) => d.oran > 0);
  if (gecerli.length <= 1) return 0;
  const entropi = -gecerli.reduce((t, d) => t + d.oran * Math.log(d.oran), 0);
  return entropi / Math.log(gecerli.length);
}

/** Bir gönderiyi çerçevesi içinde temsil gücüne göre puanlar */
function temsilPuani(g: AkisOgesi): number {
  const etkilesim = g.begeni + g.yanit_sayisi * 2 + g.yeniden_paylasim * 3;
  const uzunlukUygunlugu = Math.min(g.metin.length, 160) / 160;
  return Math.log1p(etkilesim) * (0.6 + 0.4 * uzunlukUygunlugu);
}

/** Gönderi metnini özet cümlesine dönüştürür: olay başlığı tekrarını temizler */
function cumleyeIndirge(g: AkisOgesi): string {
  let m = g.metin;
  if (g.olay_basligi) {
    m = m.split(g.olay_basligi).join("bu gelişme");
  }
  m = m.replace(/\s+/g, " ").trim();
  if (m.length > 180) m = m.slice(0, 177).trimEnd() + "…";
  return m;
}

const CERCEVE_GIRIS: Record<Cerceve, string> = {
  notr: "Aktarılana göre",
  destekleyici: "Gelişmeyi olumlu karşılayanlar",
  elestirel: "Eleştirel yaklaşanlar",
  soru: "Doğruluğunu sorgulayanlar",
  yanlis_bilgi: "Kaynak gösterilmeden dolaşan iddialara göre",
};

const CERCEVE_SIRA: Cerceve[] = ["notr", "destekleyici", "elestirel", "soru", "yanlis_bilgi"];

export function olayOzetle(olayId: string, baslik: string, kategori: Kategori, gonderiler: AkisOgesi[]): OlayOzeti {
  const toplam = gonderiler.length;

  const gruplar = new Map<Cerceve, AkisOgesi[]>();
  for (const g of gonderiler) {
    const liste = gruplar.get(g.cerceve) ?? [];
    liste.push(g);
    gruplar.set(g.cerceve, liste);
  }

  const dagilim: CerceveDagilimi[] = CERCEVE_SIRA.map((c) => {
    const adet = gruplar.get(c)?.length ?? 0;
    return { cerceve: c, adet, oran: toplam ? adet / toplam : 0 };
  });

  // Her çerçeveden en temsili gönderiyi seç; sıralama sabit tutulur ki
  // özet, etkileşim hacmine göre tek yöne savrulmasın.
  const parcalar: string[] = [`${baslik}.`];
  for (const c of CERCEVE_SIRA) {
    const grup = gruplar.get(c);
    if (!grup?.length) continue;
    // Doğrulanmamış iddialar özete "iddia" olarak girer, olgu olarak değil.
    const secilen = [...grup].sort((a, b) => temsilPuani(b) - temsilPuani(a))[0];
    parcalar.push(`${CERCEVE_GIRIS[c]}: ${cumleyeIndirge(secilen)}`);
  }

  return {
    olayId,
    baslik,
    kategori,
    ozet: parcalar.join(" "),
    gonderiSayisi: toplam,
    kaynakSayisi: new Set(gonderiler.map((g) => g.yazar_id)).size,
    dagilim,
    dengeSkoru: dengeHesapla(dagilim),
    dogrulanmamisIddiaVar: gonderiler.some((g) => g.iddia_dogru_mu === false),
  };
}

export function kategoriOzetle(kategori: Kategori, olayLimiti = 3): KategoriOzeti {
  const olaylar = olaylariGetir(kategori).slice(0, olayLimiti);
  return {
    kategori,
    baslik: KATEGORI_ETIKET[kategori],
    olaylar: olaylar.map((o) => olayOzetle(o.olayId, o.baslik, o.kategori, o.gonderiler)),
    toplamGonderi: olaylar.reduce((t, o) => t + o.gonderiler.length, 0),
  };
}

/** Kişisel akış: olay kümesi olmayan gönderiler için tematik özet */
export function kisiselOzetle(gonderiler: AkisOgesi[]): string {
  const kisisel = gonderiler.filter((g) => g.kategori === "kisisel");
  if (!kisisel.length) return "Kişisel akışınızda özetlenecek yeni gönderi yok.";
  const enEtkilesimli = [...kisisel].sort((a, b) => temsilPuani(b) - temsilPuani(a)).slice(0, 3);
  const kisiSayisi = new Set(kisisel.map((g) => g.yazar_id)).size;
  return (
    `Takip ettiğiniz ${kisiSayisi} kişiden son ${kisisel.length} kişisel gönderi var. ` +
    `Öne çıkanlar: ${enEtkilesimli.map((g) => cumleyeIndirge(g)).join(" ")}`
  );
}
