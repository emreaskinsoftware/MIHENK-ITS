/**
 * YZ metin sinyali rozeti ve itiraz akışı (spec 6.5 / 6.9).
 *
 * ÜÇ DURUM, ÜÇ DAVRANIŞ:
 *   1. `label === null` (çekimserlik)  -> HİÇBİR ŞEY gösterilmez.
 *   2. İtiraz edilmiş gönderi          -> sinyal gizlenir, "inceleniyor" denir.
 *   3. Etiket var                      -> rozet + itiraz düğmesi gösterilir.
 *
 * NEDEN İTİRAZ DÜĞMESİ ROZETİN YANINDA: Bir sistem insanları etiketliyorsa,
 * itiraz yolu etiketin kendisi kadar görünür olmalıdır. İtirazı ayarlar
 * menüsüne gömmek, hakkı kâğıt üzerinde bırakmak olur.
 *
 * NEDEN "OLASI" DİLİ: Rozet metni "yapay zekâ üretimi" değil, "yapay zekâ
 * üretimi olabilir" der. Sistem bir olasılık hesaplar, hüküm vermez; arayüz
 * dili bu belirsizliği saklamaz.
 */
import { useState } from "react";
import { api, type TespitSonucu } from "../lib/api";

interface Ozellikler {
  postId: string;
  tespit: TespitSonucu | null;
  itirazVar: boolean;
  onItiraz: (postId: string) => void;
}

export function YzSinyali({ postId, tespit, itirazVar, onItiraz }: Ozellikler) {
  const [acik, setAcik] = useState(false);
  const [gerekce, setGerekce] = useState("");
  const [durum, setDurum] = useState<"bos" | "gonderiliyor" | "gonderildi">("bos");

  // 1) Çekimserlik veya sinyal yok: boş alan bırak.
  if (!tespit || tespit.label === null) {
    return null;
  }

  // 2) İtiraz edilmişse sinyali gizle: inceleme sürerken etiket göstermek
  //    itiraz hakkını anlamsızlaştırır.
  if (itirazVar) {
    return (
      <span className="text-xs text-mihenk-ikincil" role="status">
        ⏳ Sinyal itiraz üzerine incelemede — gösterilmiyor
      </span>
    );
  }

  const yz = tespit.label === "yz_olasi";
  const metin = yz ? "Yapay zekâ üretimi olabilir" : "İnsan yazımı olabilir";
  const simge = yz ? "◆" : "◎";
  const stil = yz
    ? "bg-mihenk-uyari-acik text-mihenk-uyari border-mihenk-uyari"
    : "bg-mihenk-vurgu-acik text-mihenk-vurgu border-mihenk-vurgu";

  async function gonder() {
    if (!gerekce.trim()) return;
    setDurum("gonderiliyor");
    try {
      await api.itiraz(postId, gerekce.trim());
      setDurum("gonderildi");
      onItiraz(postId);
    } catch {
      setDurum("bos");
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span
        className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs font-medium ${stil}`}
        aria-label={`${metin}. Model güveni: ${
          tespit.confidence ? Math.round(tespit.confidence * 100) : "?"
        } yüzde. Bu bir kesin hüküm değildir.`}
      >
        <span aria-hidden="true">{simge}</span>
        <span>{metin}</span>
      </span>

      <button
        type="button"
        onClick={() => setAcik((a) => !a)}
        aria-expanded={acik}
        aria-controls={`itiraz-${postId}`}
        className="min-h-dokunma rounded-md px-2 py-1 text-xs underline underline-offset-2 text-mihenk-ikincil hover:text-mihenk-metin"
      >
        Bu etikete itiraz et
      </button>

      {acik && (
        <div
          id={`itiraz-${postId}`}
          className="mt-2 w-full rounded-md border border-mihenk-cizgi bg-white p-3"
        >
          {durum === "gonderildi" ? (
            <p className="text-sm text-mihenk-vurgu" role="status">
              ✓ İtirazınız alındı. İnceleme sonuçlanana kadar bu gönderide sinyal
              gösterilmeyecek.
            </p>
          ) : (
            <>
              <label
                htmlFor={`itiraz-alan-${postId}`}
                className="block text-sm font-medium"
              >
                İtiraz gerekçeniz
              </label>
              <p className="mb-2 mt-1 text-xs text-mihenk-ikincil">
                Bu etiket otomatik bir olasılık hesabıdır. Yanlış olduğunu
                düşünüyorsanız gerekçenizi yazın; kayıt insan incelemesine gider.
              </p>
              <textarea
                id={`itiraz-alan-${postId}`}
                value={gerekce}
                onChange={(e) => setGerekce(e.target.value)}
                rows={3}
                className="w-full rounded-md border border-mihenk-cizgi p-2 text-sm"
                placeholder="Örnek: Bu metni ben yazdım, herhangi bir araç kullanmadım."
              />
              <button
                type="button"
                onClick={gonder}
                disabled={!gerekce.trim() || durum === "gonderiliyor"}
                className="mt-2 min-h-dokunma rounded-md bg-mihenk-vurgu px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                {durum === "gonderiliyor" ? "Gönderiliyor…" : "İtirazı gönder"}
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
