/**
 * MİHENK — Bot / koordineli manipülasyon tespiti (davranışsal temel model).
 *
 * Bu modül, içeriğe DEĞİL davranışa bakar. Metin analizi yapmaz; hesabın
 * yapısal sinyallerini değerlendirir. Böylece dil bilgisi gerektirmez ve
 * yeni bir manipülasyon dalgasına hızla uyum sağlar.
 *
 * Sinyaller ve gerekçeleri:
 *   1. Hesap yaşı        — çok yeni hesaplar kampanya için toplu açılır
 *   2. Takip dengesizliği — çok takip edip az takipçisi olmak tipik bot örüntüsü
 *   3. Etkileşim tutarsızlığı — takipçiye oranla anormal yüksek/düşük etkileşim
 *
 * ÖNEMLİ: Çıktı bir SUÇLAMA DEĞİL, bir dikkat işaretidir. Hesap engellenmez,
 * gizlenmez; kullanıcıya yalnızca bağlam sunulur. Nihai karar kullanıcınındır.
 * (bkz. rapor — etik çerçeve)
 */
import type { AkisOgesi, Kullanici } from "../tipler";

export type RiskDuzeyi = "dusuk" | "orta" | "yuksek";

export interface HesapRiski {
  puan: number;          // 0-100
  duzey: RiskDuzeyi;
  bulgular: string[];
}

export function hesapRiskiHesapla(k: Kullanici, gonderileri: AkisOgesi[]): HesapRiski {
  const bulgular: string[] = [];
  let puan = 0;

  // 1) Hesap yaşı
  if (k.hesap_yasi_gun < 30) {
    puan += 35;
    bulgular.push(`Hesap ${k.hesap_yasi_gun} günlük — yeni açılmış`);
  } else if (k.hesap_yasi_gun < 90) {
    puan += 15;
    bulgular.push(`Hesap ${Math.round(k.hesap_yasi_gun / 30)} aylık`);
  }

  // 2) Takip dengesizliği
  const oran = k.takipci_sayisi > 0 ? k.takip_edilen_sayisi / k.takipci_sayisi : k.takip_edilen_sayisi;
  if (oran > 8) {
    puan += 30;
    bulgular.push(`Takip ettiği hesap sayısı takipçisinin ${Math.round(oran)} katı`);
  } else if (oran > 3) {
    puan += 12;
    bulgular.push("Takip/takipçi dengesi olağandışı");
  }

  // 3) Paylaşım yoğunluğu
  if (gonderileri.length >= 4 && k.hesap_yasi_gun < 60) {
    puan += 20;
    bulgular.push("Kısa hesap ömrüne göre yoğun paylaşım");
  }

  // 4) Etkileşim tutarsızlığı
  const ortBegeni = gonderileri.length
    ? gonderileri.reduce((t, g) => t + g.begeni, 0) / gonderileri.length
    : 0;
  const beklenen = Math.max(1, k.takipci_sayisi * 0.01);
  if (ortBegeni > beklenen * 12 && k.takipci_sayisi > 50) {
    puan += 15;
    bulgular.push("Takipçi sayısına göre beklenmedik yüksek etkileşim");
  }

  puan = Math.min(100, puan);
  return {
    puan,
    duzey: puan >= 60 ? "yuksek" : puan >= 30 ? "orta" : "dusuk",
    bulgular,
  };
}

/** Bir olay kümesinde koordineli davranış izi arar */
export function koordinasyonIzi(gonderiler: AkisOgesi[]): { koordineli: boolean; not: string } {
  if (gonderiler.length < 4) return { koordineli: false, not: "" };

  const zamanlar = gonderiler
    .map((g) => new Date(g.zaman).getTime())
    .sort((a, b) => a - b);

  // Gönderilerin yarısından fazlası 30 dakikalık pencereye sıkışıyor mu?
  const pencere = 30 * 60 * 1000;
  let enYogun = 0;
  for (let i = 0; i < zamanlar.length; i++) {
    let sayac = 0;
    for (let j = i; j < zamanlar.length && zamanlar[j] - zamanlar[i] <= pencere; j++) sayac++;
    enYogun = Math.max(enYogun, sayac);
  }

  const oran = enYogun / gonderiler.length;
  if (oran > 0.6) {
    return {
      koordineli: true,
      not: `Gönderilerin %${Math.round(oran * 100)}'i 30 dakikalık bir pencerede yoğunlaşıyor`,
    };
  }
  return { koordineli: false, not: "" };
}
