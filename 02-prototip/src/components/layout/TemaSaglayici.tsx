"use client";

import { useCallback, useSyncExternalStore } from "react";

type Tema = "koyu" | "acik";

/** Tercihin saklandığı anahtar. `TEMA_BETIGI` ile aynı olmak ZORUNDA. */
export const TEMA_ANAHTARI = "mihenk-tema";

/**
 * Sayfa boyanmadan ÖNCE çalışan tema betiği.
 *
 * --- DÜZELTİLEN KUSUR ----------------------------------------------------
 * Tema tercihi yalnızca `useEffect` içinde okunuyordu. Effect ilk boyamadan
 * SONRA çalışır; dolayısıyla teması "açık" olan bir kullanıcı her sayfa
 * yüklemesinde önce koyu ekranı görüyor, sonra ekran beyaza dönüyordu
 * (flash of wrong theme). Sunucuda üretilen HTML her zaman koyu olduğu için
 * bu, yavaş bağlantıda göz alıcı bir yanıp sönmeye dönüşüyordu.
 *
 * Bu betik `<head>` içinde SENKRON çalışır ve `data-tema` özniteliğini React
 * hiç devreye girmeden yazar.
 *
 * `<html>` üzerinde `suppressHydrationWarning` gerekir: betik, sunucunun
 * gönderdiği işaretlemeyi hidrasyondan önce değiştiriyor ve React bunu
 * uyumsuzluk sanardı. Bastırma yalnızca o öğenin ÖZNİTELİKLERİNİ kapsar,
 * ağacın geri kalanını değil.
 */
export const TEMA_BETIGI = `
(function () {
  try {
    var t = localStorage.getItem(${JSON.stringify(TEMA_ANAHTARI)});
    if (t === "acik") document.documentElement.dataset.tema = "acik";
  } catch (e) {
    /* localStorage kapalı olabilir (gizli sekme kısıtı, kurumsal politika).
       Tema tercihi kritik değil; sessizce varsayılana düşülür. */
  }
})();
`;

/**
 * --- NEDEN CONTEXT + useState DEĞİL, useSyncExternalStore ----------------
 *
 * Temanın TEK DOĞRU KAYNAĞI React state'i değil, `<html data-tema>`
 * özniteliğidir: onu React'ten önce `TEMA_BETIGI` yazıyor. Aynı bilgiyi bir
 * de React state'inde tutmak iki kopya demekti ve ikisini eşitlemek için
 * effect içinde `setState` çağırmak gerekiyordu — React'in
 * `set-state-in-effect` kuralının uyardığı zincirleme render tam olarak bu.
 *
 * `useSyncExternalStore`, React 18 ile bu sorun için eklenen API'dir:
 * dış bir kaynağa abone olur, istemcide anlık değeri okur, sunucuda ise ayrı
 * bir "sunucu anlık görüntüsü" kullanır. Böylece kopya da effect de kalmıyor.
 *
 * Sağlayıcı bileşenine de gerek kalmadı: üç ayrı bileşen aynı DOM
 * özniteliğini okuduğu için değerleri zaten aynı; araya bir context koymak
 * yalnızca dolaylılık eklerdi.
 */

/** Değişiklikten haberdar olmak isteyen bileşenler. */
const aboneler = new Set<() => void>();

function abone(bildir: () => void): () => void {
  aboneler.add(bildir);
  return () => {
    aboneler.delete(bildir);
  };
}

/** İstemcideki anlık değer — tek doğru kaynak DOM özniteliğidir. */
function anlikDeger(): Tema {
  return document.documentElement.dataset.tema === "acik" ? "acik" : "koyu";
}

/**
 * Sunucudaki değer. Sunucu localStorage'ı göremez, bu yüzden HER ZAMAN koyu
 * döner ve sunucu HTML'i de koyu üretilir. Açık temayı `TEMA_BETIGI` daha
 * hidrasyondan önce uygular; React bu farkı görmez.
 */
function sunucuDegeri(): Tema {
  return "koyu";
}

function temaYaz(yeni: Tema): void {
  if (yeni === "acik") document.documentElement.dataset.tema = "acik";
  else delete document.documentElement.dataset.tema;
  try {
    localStorage.setItem(TEMA_ANAHTARI, yeni);
  } catch {
    // Tercih saklanamadı; oturum boyunca geçerli kalır.
  }
  for (const bildir of aboneler) bildir();
}

/**
 * Tema durumunu ve değiştiriciyi verir.
 *
 * ADI `use` İLE BAŞLAMAK ZORUNDA. Önceki adı `temaKullan` idi ve bu, React'in
 * `rules-of-hooks` denetimini bu fonksiyon ve TÜM çağıranları için devre dışı
 * bırakıyordu: eklenti, `use` ile başlamayan bir fonksiyonu kanca saymadığı
 * için içindeki kanca çağrısını ve çağıranlardaki koşullu kullanımları
 * denetleyemiyordu. Türkçe adlandırma tercihine rağmen bu ön ek bir üslup
 * meselesi değil, React'in doğrulama mekanizmasının koşuludur.
 */
export function useTema(): { tema: Tema; degistir: () => void } {
  const tema = useSyncExternalStore(abone, anlikDeger, sunucuDegeri);
  const degistir = useCallback(() => {
    temaYaz(anlikDeger() === "koyu" ? "acik" : "koyu");
  }, []);
  return { tema, degistir };
}
