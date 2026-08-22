"use client";

import { useEffect, useState } from "react";
import { Sparkles, User } from "lucide-react";
import { mihenkApi, type TespitSonucu } from "@/lib/api/mihenk";

/**
 * Yapay zekâ üretimi metin sinyali.
 *
 * NEDEN BU BİLEŞEN EKLENDİ: Projenin ölçülen ana yeteneği YZ metin tespiti
 * (rapor Tablo 1/4) ama bu prototipte hiçbir görsel karşılığı yoktu. Ölçülen
 * bir yeteneğin jüriye gösterilecek arayüzde görünmemesi, ölçümü de
 * anlamsızlaştırır.
 *
 * --- ÜÇ DURUM, ÜÇÜ DE FARKLI GÖRÜNÜR ------------------------------------
 *   1. Backend çekimser  -> HİÇBİR ŞEY gösterilmez (spec 6.9). Boş alan,
 *      "insan yazımı" demek DEĞİLDİR; hüküm verilmediği anlamına gelir.
 *      Bunu bir rozetle belirtmek de yanlış olurdu: kullanıcı ekranda bir
 *      şey görünce onu bir yargı sanır.
 *   2. Backend etiket verdi -> etiket + güven, tıklanınca gerekçe.
 *   3. Backend erişilemedi  -> yine HİÇBİR ŞEY. Yerel bir tahmin
 *      ÜRETİLMEZ. Uydurma bir sinyal, sinyal yokluğundan kötüdür.
 *
 * Bu bileşen bilinçli olarak yerel yedeğe düşmez. Yerel yedek özet için
 * savunulabilir (metin zaten ortada, kaynağına bağlanabilir); tespit için
 * savunulamaz, çünkü model yoksa üretilecek olasılık uydurmadır (spec 2).
 */

/** Backend'in döndürdüğü gerekçe kodları (bkz. detection/decision.py) */
const GEREKCE_METNI: Record<string, string> = {
  metin_cok_kisa:
    "Metin, güvenilir bir değerlendirme için fazla kısa. Kısa metinlerde üslup sinyali yok denecek kadar azdır.",
  belirsiz:
    "Model kararsız kaldı. Belirsizlik bandına düşen bir olasılık için hüküm verilmez.",
  model_yok: "Tespit modeli yüklü değil; sinyal üretilmiyor.",
};

/**
 * "İnsan yazımı olabilir" rozeti gösterilsin mi?
 *
 * VARSAYILAN: HAYIR. Gerekçesi ölçüme dayanıyor, estetiğe değil.
 *
 * 1. GÜRÜLTÜ: Kalibre bantla akıştaki gönderilerin ~%88'i "insan_olasi"
 *    etiketi alıyor (ölçüldü: 33 gönderinin 29'u). Neredeyse her gönderide
 *    duran bir rozet bilgi taşımaz, yalnızca ekranı doldurur.
 *
 * 2. DAYANAĞIMIZ YOK: Gerçek metin ölçümünde modelin AUROC'u 0.768
 *    (bkz. eval/results/real_text.md). Bu, "bu metni insan yazdı" diye
 *    OLUMLU bir belge vermeye yetmez. Rozet, taşıyamadığı bir güvence
 *    veriyor.
 *
 * 3. ASİMETRİ: Yanlış "yapay zekâ" etiketi bir yazarı haksız yere damgalar;
 *    yanlış "insan" etiketi ise yapay içeriği meşrulaştırır. İkincisi
 *    sessizce gerçekleşir ve kullanıcı itiraz edemez — çünkü lehine görünür.
 *
 * Rozet yokluğu bir iddia değildir: "hüküm yok" demektir. Bunu ekranda
 * belirtmek yerine, arayüzün genelinde MİHENK'in ne yaptığı anlatılır.
 */
const INSAN_ROZETI_GOSTER = false;

export function YzSinyali({ metin }: { metin: string }) {
  const [sonuc, setSonuc] = useState<TespitSonucu | null>(null);
  const [acik, setAcik] = useState(false);

  useEffect(() => {
    // İptal bayrağı: bileşen sökülürse geç gelen yanıt state'e yazmasın.
    let gecerli = true;
    mihenkApi.tespitMetin(metin).then((y) => {
      if (gecerli && y.durum === "tamam") setSonuc(y.veri);
      // "erisilemedi" ve "hata" durumlarında bilinçli olarak hiçbir şey
      // yapılmıyor: sonuc null kalır, rozet çizilmez.
    });
    return () => {
      gecerli = false;
    };
  }, [metin]);

  // Çekimserlik, erişilememe ve henüz yüklenmemiş durumların hepsi aynı
  // görünür: boş alan. Yükleniyor iskeleti bile göstermiyoruz, çünkü sonuç
  // çoğu zaman "hüküm yok" oluyor ve titreşen bir yer tutucu, olmayan bir
  // yargı beklentisi yaratıyor.
  if (!sonuc || sonuc.abstained || !sonuc.label) return null;

  const yz = sonuc.label === "yz_olasi";
  // "insan_olasi" varsayılan olarak çizilmez — gerekçe yukarıda.
  if (!yz && !INSAN_ROZETI_GOSTER) return null;
  const renk = yz ? "var(--color-uyari)" : "var(--color-metin-ikincil)";
  const yuzde =
    sonuc.confidence === null ? null : Math.round(sonuc.confidence * 100);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setAcik((v) => !v)}
        aria-expanded={acik}
        aria-label={
          yz ? "Yapay zekâ üretimi olabilir işareti" : "İnsan yazımı olabilir işareti"
        }
        className="flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium"
        style={{ color: renk, background: `color-mix(in srgb, ${renk} 14%, transparent)` }}
      >
        {yz ? <Sparkles size={12} /> : <User size={12} />}
        {yz ? "Yapay zekâ üretimi olabilir" : "İnsan yazımı olabilir"}
      </button>

      {acik && (
        <div className="absolute z-20 top-7 left-0 w-72 rounded-xl border border-cizgi bg-zemin p-3 shadow-xl">
          <p className="text-[13px] font-semibold mb-1.5">
            Metin kökeni değerlendirmesi
            {yuzde !== null && (
              <span className="ml-1.5 font-normal text-metin-ikincil tabular-nums">
                (%{yuzde} güven)
              </span>
            )}
          </p>
          <p className="text-[12px] text-metin-ikincil leading-relaxed">
            Bu değerlendirme metnin üslubuna dayanır, içeriğinin doğruluğuna
            değil. {sonuc.token_count} kelimelik metin
            {sonuc.length_bucket ? ` (${sonuc.length_bucket} uzunluk kovası)` : ""}{" "}
            üzerinde yapılmıştır.
          </p>
          <p className="text-[11px] text-metin-sonuk border-t border-cizgi pt-2 mt-2">
            Kesin bir tespit değildir; sistem yanılabilir. Etiketin yanlış
            olduğunu düşünüyorsanız itiraz edebilirsiniz — itiraz süresince
            bu gönderide sinyal gösterilmez.
          </p>
        </div>
      )}
    </div>
  );
}

/** Gerekçe kodunu okunabilir metne çevirir (panel görünümleri için). */
export function gerekceMetni(gerekce: string | null): string {
  return (
    (gerekce && GEREKCE_METNI[gerekce]) ??
    "Değerlendirme için yeterli dayanak bulunamadı."
  );
}
