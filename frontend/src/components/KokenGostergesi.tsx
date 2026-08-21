/**
 * Görsel köken göstergesi (spec 6.6 / 6.9).
 *
 * TASARIM KURALI — ÇEKİMSERLİKTE HİÇBİR ŞEY GÖSTERME:
 * `display: false` gelen sonuç için bileşen null döner. "Bilinmiyor" rozeti
 * göstermiyoruz; belirsizliği görsel bir işarete dönüştürmek, kullanıcıya
 * "sistem baktı ve bir şey buldu" izlenimi verir. Boş alan bırakmak dürüst
 * olandır (İlke 2).
 *
 * ERİŞİLEBİLİRLİK: Bilgi yalnızca renkle aktarılmaz — her durumun simgesi ve
 * metni vardır. Renk körü bir kullanıcı da simge ve metinden durumu okur.
 */
import type { KokenSonucu } from "../lib/api";

interface Ozellikler {
  koken: KokenSonucu;
}

export function KokenGostergesi({ koken }: Ozellikler) {
  if (!koken.display || !koken.label) {
    // Çekimserlik: hiçbir gösterge çizilmez.
    return null;
  }

  const yzUretimi = koken.status === "yz_uretimi";
  const simge = yzUretimi ? "◆" : "◎";
  const stil = yzUretimi
    ? "bg-mihenk-uyari-acik text-mihenk-uyari border-mihenk-uyari"
    : "bg-mihenk-vurgu-acik text-mihenk-vurgu border-mihenk-vurgu";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs font-medium ${stil}`}
      // Ekran okuyucu için tam açıklama: kanıt kaynağı da söylenir.
      aria-label={`Görsel kökeni: ${koken.label}. Kanıt kaynağı: ${koken.evidence ?? "belirtilmemiş"}.`}
    >
      <span aria-hidden="true">{simge}</span>
      <span>{koken.label}</span>
    </span>
  );
}
