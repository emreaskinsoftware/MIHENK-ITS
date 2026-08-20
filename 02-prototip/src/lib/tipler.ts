export type Kategori = "gundem" | "spor" | "ekonomi" | "teknoloji" | "kultur" | "kisisel";

export type Cerceve = "destekleyici" | "elestirel" | "notr" | "soru" | "yanlis_bilgi";

export interface Kullanici {
  id: string;
  kullanici_adi: string;
  rol: "uretici" | "kullanici";
  takipci_sayisi: number;
  takip_edilen_sayisi: number;
  hesap_yasi_gun: number;
  ilgi_alanlari: string[];
  dogrulanmis: boolean;
}

export interface Gonderi {
  id: string;
  yazar_id: string;
  metin: string;
  kategori: Kategori;
  olay_id: string | null;
  olay_basligi: string | null;
  cerceve: Cerceve;
  zaman: string;
  begeni: number;
  yeniden_paylasim: number;
  yanit_sayisi: number;
  gorsel_var: boolean;
  gorsel_yapay_uretim: boolean | null;
  dogrulanabilir_iddia: string | null;
  iddia_dogru_mu: boolean | null;
}

export interface Etkilesim {
  gonderi_id: string;
  tur: "begeni" | "yanit" | "paylasim" | "kaydetme";
  zaman: string;
  saat: number;
  gun: number;
  kategori: Kategori;
  segment: string;
  takipci_araligi: string;
}

/** Gönderi + çözümlenmiş yazar — arayüzün tükettiği biçim */
export interface AkisOgesi extends Gonderi {
  yazar: Kullanici;
}

export const KATEGORI_ETIKET: Record<Kategori, string> = {
  gundem: "Gündem",
  spor: "Spor",
  ekonomi: "Ekonomi",
  teknoloji: "Teknoloji",
  kultur: "Kültür",
  kisisel: "Kişisel",
};

export const CERCEVE_ETIKET: Record<Cerceve, string> = {
  destekleyici: "Destekleyici",
  elestirel: "Eleştirel",
  notr: "Nötr",
  soru: "Soru soran",
  yanlis_bilgi: "Doğrulanmamış",
};
