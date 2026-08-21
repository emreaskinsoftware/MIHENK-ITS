/**
 * Özet paneli ve kaynak çipleri (spec 6.9, ekran 2 ve 3).
 *
 * KAYNAK ÇİPLERİ ÜRÜNÜN KALBİDİR:
 * Her özet cümlesinin altında, dayandığı gönderilere giden çipler bulunur.
 * Çipler "dekorasyon" değil, gezinme aracıdır: tıklanınca akış ilgili
 * gönderiye kayar ve gönderi kısa süre vurgulanır. Konumları da bilinçlidir —
 * cümlenin hemen altında, tıklamayı teşvik edecek biçimde (spec 1, üreticiyi
 * koruma kuralı: özet, gönderinin yerine geçmez, ona götürür).
 *
 * ŞEFFAFLIK ŞERİDİ: Panelin altında kaç küme kuruldu, kaç cümle atıfsız
 * olduğu için silindi, kaç küme tek kaynaklı olduğu için bastırıldı bilgisi
 * gösterilir. Bunlar iç metrikler gibi görünse de kullanıcıya sistemin ne
 * yaptığını ve neyi GÖSTERMEDİĞİNİ anlatır; sistemin sessizliği görünür olur.
 */
import { useState } from "react";
import { api, type Kategori, type OzetYaniti } from "../lib/api";

const SEKMELER: { anahtar: Kategori; etiket: string }[] = [
  { anahtar: "gundem", etiket: "Ülke gündemi" },
  { anahtar: "spor", etiket: "Spor" },
  { anahtar: "kisisel", etiket: "Kişisel akış" },
];

interface Ozellikler {
  kategori: Kategori;
  onKategoriDegis: (k: Kategori) => void;
  onKaynagaGit: (postId: string) => void;
}

export function OzetPaneli({ kategori, onKategoriDegis, onKaynagaGit }: Ozellikler) {
  const [ozetler, setOzetler] = useState<Partial<Record<Kategori, OzetYaniti>>>({});
  const [yukleniyor, setYukleniyor] = useState(false);
  const [hata, setHata] = useState<string | null>(null);

  const ozet = ozetler[kategori];

  async function ozetle() {
    setYukleniyor(true);
    setHata(null);
    try {
      const sonuc = await api.ozetle(kategori);
      setOzetler((o) => ({ ...o, [kategori]: sonuc }));
    } catch (e) {
      setHata(e instanceof Error ? e.message : "Özet alınamadı");
    } finally {
      setYukleniyor(false);
    }
  }

  return (
    <section
      aria-labelledby="ozet-baslik"
      className="rounded-lg border border-mihenk-cizgi bg-white p-4"
    >
      <h2 id="ozet-baslik" className="mb-3 text-base font-semibold">
        Okunmamışların özeti
      </h2>

      {/* Sekmeler: rol=tablist ile klavye ve ekran okuyucu desteği */}
      <div role="tablist" aria-label="Özet kategorisi" className="mb-3 flex flex-wrap gap-2">
        {SEKMELER.map((s) => {
          const secili = s.anahtar === kategori;
          return (
            <button
              key={s.anahtar}
              role="tab"
              type="button"
              aria-selected={secili}
              onClick={() => onKategoriDegis(s.anahtar)}
              className={`min-h-dokunma rounded-md border px-3 py-2 text-sm font-medium ${
                secili
                  ? "border-mihenk-vurgu bg-mihenk-vurgu text-white"
                  : "border-mihenk-cizgi hover:bg-mihenk-zemin"
              }`}
            >
              {s.etiket}
            </button>
          );
        })}
      </div>

      <button
        type="button"
        onClick={ozetle}
        disabled={yukleniyor}
        className="min-h-dokunma w-full rounded-md bg-mihenk-vurgu px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
      >
        {yukleniyor ? "Özet hazırlanıyor…" : "Özetle"}
      </button>

      <div aria-live="polite" className="mt-4">
        {hata && (
          <p className="rounded-md border border-mihenk-uyari bg-mihenk-uyari-acik p-3 text-sm text-mihenk-uyari">
            Özet alınamadı: {hata}
          </p>
        )}

        {ozet && ozet.sentences.length === 0 && !hata && (
          <p className="rounded-md border border-mihenk-cizgi bg-mihenk-zemin p-3 text-sm">
            Bu kategoride gösterilebilecek bir özet çıkmadı. Kaynağına
            bağlanamayan cümleler gösterilmez.
          </p>
        )}

        {ozet && ozet.sentences.length > 0 && (
          <ol className="space-y-4">
            {ozet.sentences.map((cumle, i) => (
              <li key={i} className="border-l-2 border-mihenk-cizgi pl-3">
                <p className="text-[15px] leading-relaxed">{cumle.text}</p>
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <span className="text-xs text-mihenk-ikincil">Kaynak:</span>
                  {cumle.source_post_ids.map((id) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => onKaynagaGit(id)}
                      className="min-h-dokunma rounded-full border border-mihenk-vurgu px-3 py-1 text-xs font-medium text-mihenk-vurgu hover:bg-mihenk-vurgu-acik"
                      aria-label={`Bu cümlenin kaynağı olan ${id} numaralı gönderiye git`}
                    >
                      {id}
                    </button>
                  ))}
                </div>
              </li>
            ))}
          </ol>
        )}

        {ozet && (
          <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-1 border-t border-mihenk-cizgi pt-3 text-xs text-mihenk-ikincil">
            <dt>Konu kümesi</dt>
            <dd className="text-right">{ozet.cluster_count}</dd>

            <dt>Atıfsız olduğu için silinen cümle</dt>
            <dd className="text-right">{ozet.dropped_sentence_count}</dd>

            <dt>Tek kaynaklı olduğu için gösterilmeyen küme</dt>
            <dd className="text-right">{ozet.single_source_cluster_count}</dd>

            <dt>Süre</dt>
            <dd className="text-right">{ozet.latency_ms} ms</dd>
          </dl>
        )}
      </div>
    </section>
  );
}
