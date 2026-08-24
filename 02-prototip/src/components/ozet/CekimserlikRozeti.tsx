import { MinusCircle } from "lucide-react";

/**
 * Çekimserlik göstergesi.
 *
 * Sistem hüküm vermediğinde bunu bir HATA gibi değil, bilinçli bir karar
 * olarak sunar. "Doğrulanamadı", "yanlış" demek değildir.
 */
// Anahtarlar backend'in DÖNDÜRDÜĞÜ gerekçe kodlarıdır.
// Kaynak: backend/app/detection/decision.py (tespit) ve
//         backend/app/assistant/service.py (asistanın beş kapısı).
//
// DÜZELTİLDİ: Önceki sürümde anahtarlar İngilizceydi (short_text,
// low_confidence...). Backend hiçbir zaman o kodları döndürmüyor, dolayısıyla
// eşleşme hiç tutmuyor ve her çekimserlik genel yedek metne düşüyordu —
// yani kullanıcı sistemin NEDEN sustuğunu hiç öğrenemiyordu. Gerekçeyi
// göstermek çekimserliğin ürün değerinin yarısıdır.
const GEREKCE_METNI: Record<string, string> = {
  // --- tespit (detection/decision.py) ---
  metin_cok_kisa:
    "Metin, güvenilir bir değerlendirme için fazla kısa. Kısa metinlerde üslup sinyali yok denecek kadar azdır.",
  belirsiz:
    "Model kararsız kaldı. Belirsizlik bandına düşen bir olasılık için hüküm verilmez.",
  model_yok: "Tespit modeli yüklü değil; sinyal üretilmiyor.",
  // --- asistan (assistant/service.py) ---
  baglamda_yok:
    "Sorunun cevabı bu gönderide ve alıntı zincirinde bulunamadı. Asistan bağlam dışına çıkmaz.",
  enjeksiyon_supheli:
    "Soru, sistemin talimatlarını değiştirmeye yönelik bir kalıp taşıyor; yanıtlanmadı.",
  cikti_kisiti:
    "Üretilen yanıt çıktı denetiminden geçemedi (bağlantı, komut veya talimat taşıyordu).",
  atifsiz:
    "Yanıtın dayandığı kaynak doğrulanamadı. Kaynağa bağlanamayan bir cevap gösterilmez (İlke 1).",
};

export function CekimserlikRozeti({
  gerekce, baglam,
}: { gerekce: string | null; baglam?: string }) {
  return (
    <div className="rounded-xl border border-cizgi bg-yukseltilmis/50 p-3.5">
      <div className="flex items-start gap-2.5">
        <MinusCircle size={18} className="text-metin-ikincil shrink-0 mt-0.5" />
        <div className="min-w-0">
          <p className="font-semibold text-[14px]">Sistem hüküm vermiyor</p>
          <p className="text-[13px] text-metin-ikincil mt-0.5 leading-relaxed">
            {(gerekce && GEREKCE_METNI[gerekce]) ??
              "Değerlendirme için yeterli dayanak bulunamadı."}
            {baglam ? ` ${baglam}` : ""}
          </p>
          <p className="text-[12px] text-metin-sonuk mt-2">
            Bu, içeriğin yanlış olduğu anlamına gelmez. Çekimserlik bilinçli bir
            tasarım kararıdır; nihai değerlendirme size aittir.
          </p>
        </div>
      </div>
    </div>
  );
}
