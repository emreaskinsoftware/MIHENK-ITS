"use client";

import { useEffect, useState } from "react";
import { Check, Lock, ShieldCheck, X } from "lucide-react";

/**
 * KVKK açık rıza akışı.
 *
 * Tasarım ilkesi: rıza VARSAYILAN OLARAK KAPALIDIR. Kullanıcı hiçbir şey
 * yapmazsa veri toplanmaz. "Kabul et" büyük, "reddet" küçük yazılmaz —
 * iki seçenek de eşit görünürlüktedir (karanlık desen kullanılmaz).
 */
const ANAHTAR = "mihenk-riza";

interface Rizalar {
  temelIslev: boolean;   // zorunlu — hizmetin çalışması için
  gelistirme: boolean;   // isteğe bağlı — anonim etkileşim sinyalleri
  modelEgitimi: boolean; // isteğe bağlı — anonim veriyle model geliştirme
}

const VARSAYILAN: Rizalar = { temelIslev: true, gelistirme: false, modelEgitimi: false };

export function RizaAkisi() {
  const [gorunur, setGorunur] = useState(false);
  const [detay, setDetay] = useState(false);
  const [rizalar, setRizalar] = useState<Rizalar>(VARSAYILAN);

  useEffect(() => {
    // Rıza bandının görünürlüğü localStorage'dan okunur ve bu ancak ilk
    // boyamadan SONRA yapılabilir: sunucu localStorage'ı göremez, render
    // sırasında okumak hidrasyon uyumsuzluğu doğurur.
    //
    // React'in `set-state-in-effect` kuralı burada bilinçli olarak
    // bastırılıyor. Kuralın uyardığı şey (zincirleme render) gerçek, ama
    // alternatifi daha kötü: bandı sunucuda da render edip sonra gizlemek,
    // rızasını çoktan vermiş kullanıcıya her sayfa yüklemesinde bandın bir
    // kare görünmesi demek olurdu. Tema tercihinde aynı sorun bir <head>
    // betiğiyle çözüldü (bkz. TemaSaglayici) çünkü orada değişen şey tek bir
    // öznitelik; burada değişen bir React ağacı, aynı yöntem uygulanamaz.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (!localStorage.getItem(ANAHTAR)) setGorunur(true);
  }, []);

  function kaydet(secim: Rizalar) {
    localStorage.setItem(ANAHTAR, JSON.stringify({ ...secim, tarih: new Date().toISOString() }));
    setGorunur(false);
  }

  if (!gorunur) return null;

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 p-4 max-lg:bottom-20 pointer-events-none"
         role="dialog" aria-modal="false" aria-labelledby="riza-baslik">
      <div className="mx-auto max-w-3xl rounded-2xl border border-cizgi bg-kart shadow-2xl p-5 pointer-events-auto">
        <div className="flex items-start gap-3">
          <ShieldCheck size={22} className="text-basari shrink-0 mt-0.5" />
          <div className="min-w-0 flex-1">
            <h2 id="riza-baslik" className="font-bold text-[16px] mb-1">
              Verileriniz üzerinde söz sahibisiniz
            </h2>
            <p className="text-[14px] text-metin-ikincil leading-relaxed">
              MİHENK, özet ve doğrulama hizmetini sunmak için yalnızca gerekli verileri işler.
              Bunun ötesindeki her kullanım <strong className="text-metin">açık rızanıza</strong> bağlıdır
              ve varsayılan olarak kapalıdır.
            </p>
          </div>
          <button type="button" onClick={() => kaydet(VARSAYILAN)}
                  aria-label="Kapat ve yalnızca zorunlu verileri kabul et"
                  className="p-1.5 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover shrink-0">
            <X size={18} />
          </button>
        </div>

        {detay && (
          <ul className="mt-4 flex flex-col gap-3 border-t border-cizgi pt-4">
            <Secenek
              baslik="Temel işlevler" zorunlu
              aciklama="Akışın gösterilmesi ve özet üretimi için gereklidir. Kapatılamaz."
              secili={true} degistir={() => {}}
            />
            <Secenek
              baslik="Hizmet geliştirme"
              aciklama="Hangi özetlerin okunduğu gibi sinyaller, kişisel bilgilerden arındırılıp toplulaştırılarak arayüzün iyileştirilmesinde kullanılır."
              secili={rizalar.gelistirme}
              degistir={() => setRizalar((r) => ({ ...r, gelistirme: !r.gelistirme }))}
            />
            <Secenek
              baslik="Yerli model geliştirme"
              aciklama="Anonimleştirilmiş etkileşim verisi, Türkçe anlayan açık modellerin eğitilmesinde kullanılır. Verilerde kimliğinize dair hiçbir iz bulunmaz."
              secili={rizalar.modelEgitimi}
              degistir={() => setRizalar((r) => ({ ...r, modelEgitimi: !r.modelEgitimi }))}
            />
          </ul>
        )}

        <div className="mt-4 flex items-center gap-3 flex-wrap">
          <button type="button" onClick={() => kaydet(VARSAYILAN)}
                  className="rounded-full border border-cizgi px-5 py-2.5 text-[14px] font-medium hover:bg-hover">
            Yalnızca zorunlu
          </button>
          <button type="button" onClick={() => kaydet(rizalar)}
                  className="rounded-full border border-cizgi px-5 py-2.5 text-[14px] font-medium hover:bg-hover">
            {detay ? "Seçimimi kaydet" : "Tercihlerimi ayarla"}
            {!detay && <span className="sr-only"> — ayrıntılı seçenekleri aç</span>}
          </button>
          {!detay && (
            <button type="button" onClick={() => setDetay(true)}
                    className="text-[14px] text-mavi hover:underline">
              Ayrıntılar
            </button>
          )}
          <button type="button"
                  onClick={() => kaydet({ temelIslev: true, gelistirme: true, modelEgitimi: true })}
                  className="ml-auto rounded-full gradyan-marka text-white px-6 py-2.5 text-[14px] font-semibold hover:brightness-110">
            Tümüne izin ver
          </button>
        </div>

        <p className="mt-3 flex items-center gap-1.5 text-[12px] text-metin-sonuk">
          <Lock size={12} /> Tercihinizi Ayarlar → Gizlilik ve Güvenlik bölümünden her an değiştirebilirsiniz.
        </p>
      </div>
    </div>
  );
}

function Secenek({
  baslik, aciklama, secili, degistir, zorunlu,
}: {
  baslik: string; aciklama: string; secili: boolean;
  degistir: () => void; zorunlu?: boolean;
}) {
  return (
    <li className="flex items-start gap-3">
      <button
        type="button" role="checkbox" aria-checked={secili} aria-label={baslik}
        disabled={zorunlu} onClick={degistir}
        className={`w-5 h-5 rounded-md grid place-items-center shrink-0 mt-0.5 transition-colors
                    ${secili ? "bg-mavi-koyu" : "border-2 border-metin-ikincil"}
                    ${zorunlu ? "opacity-60 cursor-not-allowed" : ""}`}
      >
        {secili && <Check size={13} className="text-white" strokeWidth={3} />}
      </button>
      <div className="min-w-0">
        <p className="text-[14px] font-medium">
          {baslik}
          {zorunlu && <span className="ml-2 text-[11px] text-metin-sonuk font-normal">zorunlu</span>}
        </p>
        <p className="text-[13px] text-metin-ikincil leading-relaxed">{aciklama}</p>
      </div>
    </li>
  );
}
