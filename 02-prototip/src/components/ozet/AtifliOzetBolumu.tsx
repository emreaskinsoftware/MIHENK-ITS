"use client";

import { useEffect, useState } from "react";
import { Info, Loader2, PlugZap, ShieldAlert } from "lucide-react";
import { AtifliOzet } from "./AtifliOzet";
import { mihenkApi, type HamGonderi, type OzetYaniti, type Sonuc } from "@/lib/api/mihenk";
import type { AkisOgesi } from "@/lib/tipler";

/**
 * Atıflı özetin arayüzdeki giriş kapısı.
 *
 * --- NEDEN BU BİLEŞEN VAR -----------------------------------------------
 * Prototip, kategori özetini `lib/ozet/cikarimsal.ts` ile YEREL olarak
 * üretiyordu. O özetleyici çalışıyor ama ATIF ÜRETMİYOR: cümleleri hangi
 * gönderilerden çıkardığını taşımıyor. Yani projenin ana iddiası — "söylediği
 * her cümleyi kaynağına bağlar" (İlke 1) — backend'de uygulanmış olmasına
 * rağmen kullanıcının gördüğü ekranda hiç görünmüyordu. `AtifliOzet` bileşeni
 * de bu yüzden hiçbir yerden çağrılmayan ölü koddu.
 *
 * Bu bileşen özeti backend'den ister ve atıf denetiminden GEÇMİŞ cümleleri
 * gösterir. Yerel özetleyici silinmedi; karşılaştırma temeli olarak duruyor
 * (rapor 3.2) ve backend kapalıyken NE OLDUĞU SÖYLENEREK gösteriliyor.
 *
 * --- SESSİZLİK ÇÖKME DEĞİLDİR -------------------------------------------
 * Dört ayrı durum var ve üçü birbirine karıştırılmamalı:
 *   1. Backend konuştu, cümle verdi        -> atıflı özet gösterilir
 *   2. Backend konuştu, cümle VERMEDİ      -> çekimserlik gösterilir (İlke 2/3),
 *                                             yerel özete DÜŞÜLMEZ
 *   3. Backend'e erişilemedi               -> yerel temel özet, "atıfsız"
 *                                             etiketiyle gösterilir
 *   4. Backend hata döndü                  -> hata görünür kılınır, gizlenmez
 * İkinci durumda yerel özete düşmek, ilkeli bir sessizliği atıfsız bir metinle
 * doldurmak olurdu; sistemin sustuğu tam da o an gizlenirdi.
 */

/**
 * Tek istekte gönderilecek en fazla gönderi.
 *
 * Backend bu uçta gönderileri istek anında zenginleştiriyor ve kümeleme O(N²)
 * mesafe matrisi kuruyor; uç noktanın kendi üst sınırı 80. Buradaki sınır ondan
 * küçük tutuldu ki sözleşme ihlali (422) yerine öngörülebilir bir kırpma olsun.
 */
const EN_FAZLA_GONDERI = 60;

/**
 * Gelen sonuç, HANGİ kategori için istendiğiyle birlikte saklanır.
 *
 * NEDEN BİRLİKTE: "yükleniyor" durumu ayrı bir state değil, `sonuc.kategori`
 * ile o anki `kategori` uyuşmuyorsa TÜRETİLİR. İlk sürüm sekme değişince
 * effect içinden senkron `setDurum({asama:"yukleniyor"})` çağırıyordu; bu,
 * React'in `set-state-in-effect` kuralını çiğniyor ve her sekme değişiminde
 * gereksiz bir zincirleme render doğuruyordu. Türetilmiş durumda o çağrıya
 * gerek kalmıyor: yeni kategori istenir istenmez eski sonuç zaten "bu
 * kategoriye ait değil" olur.
 */
type Kayit = { kategori: string; sonuc: Sonuc<OzetYaniti> };

export function AtifliOzetBolumu({
  kategori,
  gonderiler,
  yerelOzet,
}: {
  /** Backend'e gönderilecek kategori adı; çoğulculuk kuralı bundan türetilir. */
  kategori: string;
  /** Bu kategorideki akış gönderileri. */
  gonderiler: AkisOgesi[];
  /** Backend'e erişilemezse gösterilecek yerel (atıfsız) temel özet. */
  yerelOzet: string;
}) {
  const [kayit, setKayit] = useState<Kayit | null>(null);

  // Gönderi yoksa istek atılmaz. Bu bir yükleme durumu değil, bilinen bir
  // sonuçtur ve aşağıda yerel yedek gösterilir.
  const govde: HamGonderi[] = gonderiler
    .slice(0, EN_FAZLA_GONDERI)
    .map((g) => ({ id: g.id, author_id: g.yazar_id, text: g.metin }));
  const gonderiYok = govde.length === 0;

  useEffect(() => {
    if (gonderiYok) return;
    // Kategori değişince eski isteğin geç gelen yanıtı yeni sekmenin üstüne
    // yazmasın: iptal bayrağı olmadan kullanıcı "Spor" sekmesinde "Gündem"
    // özetini görebilir.
    let gecerli = true;
    mihenkApi.ozetleMetinler(kategori, govde).then((sonuc) => {
      if (gecerli) setKayit({ kategori, sonuc });
    });
    return () => {
      gecerli = false;
    };
    // `govde` her render'da yeniden kurulan bir dizidir; bağımlılığa
    // konulursa sonsuz döngü olur. İçeriği tamamen `gonderiler`den türediği
    // için asıl bağımlılık odur.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [kategori, gonderiler, gonderiYok]);

  // Sonuç bu kategoriye ait değilse hâlâ bekliyoruz.
  if (!gonderiYok && kayit?.kategori !== kategori) {
    return (
      <div className="flex items-center gap-2 rounded-xl bg-zemin border border-cizgi p-4
                      text-[13px] text-metin-ikincil">
        <Loader2 size={14} className="animate-spin" />
        Atıflı özet üretiliyor…
      </div>
    );
  }

  // Gönderi yoksa istek hiç atılmadı; yerel yedek gösterilir.
  const sonuc: Sonuc<OzetYaniti> = gonderiYok
    ? { durum: "erisilemedi" }
    : kayit!.sonuc;

  // --- Durum 3: servise erişilemedi -> yerel temel, ne olduğu söylenerek ---
  if (sonuc.durum === "erisilemedi") {
    return (
      <div className="rounded-xl bg-zemin border border-cizgi p-4">
        <p className="text-[15px] leading-[1.7] text-metin">{yerelOzet}</p>
        <p className="mt-3 flex items-start gap-1.5 text-[12px] text-uyari">
          <PlugZap size={13} className="mt-0.5 shrink-0" />
          <span>
            MİHENK servisine erişilemedi. Yukarıdaki metin, arayüzün yerel
            çıkarımsal temel modelinden gelmektedir ve <strong>atıf içermez</strong>;
            sistemin atıflı özet başarımını göstermez.
          </span>
        </p>
      </div>
    );
  }

  // --- Durum 4: servis hata döndü -> gizlenmez ---
  if (sonuc.durum === "hata") {
    return (
      <div className="rounded-xl bg-zemin border border-cizgi p-4">
        <p className="flex items-start gap-1.5 text-[13px] text-uyari">
          <ShieldAlert size={14} className="mt-0.5 shrink-0" />
          <span>
            Özet servisi {sonuc.kod} kodlu bir hata döndürdü. Yerine yerel bir
            özet konmuyor: hatanın üstünü örtmek, sonraki koşularda yanlış
            sonucun fark edilmemesine yol açar.
          </span>
        </p>
      </div>
    );
  }

  const ozet = sonuc.veri;

  // --- Durum 2: backend konuştu ama cümle vermedi -> çekimserlik ---
  if (!ozet.sentences.length) {
    return (
      <div className="rounded-xl bg-zemin border border-cizgi p-4">
        <p className="text-[15px] leading-[1.7] text-metin">
          MİHENK bu kategoride özet üretmedi.
        </p>
        <ul className="mt-2 flex flex-col gap-1 text-[12px] text-metin-ikincil">
          {ozet.single_source_cluster_count > 0 && (
            <li className="flex items-start gap-1.5">
              <Info size={13} className="mt-0.5 shrink-0" />
              {ozet.single_source_cluster_count} konu kümesi tek kaynağa
              dayandığı için bastırıldı — tek kişinin anlattığı bir olay gündem
              olarak sunulmaz.
            </li>
          )}
          {ozet.dropped_sentence_count > 0 && (
            <li className="flex items-start gap-1.5">
              <Info size={13} className="mt-0.5 shrink-0" />
              {ozet.dropped_sentence_count} cümle atıf denetiminden geçemediği
              için silindi.
            </li>
          )}
          {ozet.single_source_cluster_count === 0 &&
            ozet.dropped_sentence_count === 0 && (
              <li className="flex items-start gap-1.5">
                <Info size={13} className="mt-0.5 shrink-0" />
                Kaynağa bağlanabilen bir cümle üretilemedi. Emin olunmayan
                yerde susmak, dayanaksız bir özet yazmaya tercih edilir.
              </li>
            )}
        </ul>
      </div>
    );
  }

  // --- Durum 1: atıflı özet ---
  // Sağlayıcı açıklaması: anahtar tanımlı değilken birleştirmeyi yerel,
  // çıkarımsal bir yedek yapar. Ürettiği metin bir dil modeli çıktısı gibi
  // okunur ama değildir; bunu yazmamak, demoyu izleyen kişinin sistemin üretim
  // başarımı hakkında yanlış bir izlenim edinmesine yol açardı. ATIF DENETİMİ
  // her iki durumda da aynı kodla yapılır — açıklanan şey metnin kaynağıdır,
  // atıfların geçerliliği değil.
  const yerelUretim = ozet.provider.startsWith("fake");

  return (
    <div className="rounded-xl bg-zemin border border-cizgi p-4">
      <AtifliOzet ozet={ozet} />

      {yerelUretim && (
        <p className="mt-3 flex items-start gap-1.5 text-[12px] text-metin-ikincil">
          <Info size={13} className="mt-0.5 shrink-0" />
          <span>
            Dış model anahtarı tanımlı değil. Özet cümleleri yerel çıkarımsal
            yedekle üretildi ({ozet.provider}); atıf denetimi aynı şekilde
            uygulandı, ancak bu metin sistemin üretici model başarımını
            göstermez.
          </span>
        </p>
      )}
    </div>
  );
}
