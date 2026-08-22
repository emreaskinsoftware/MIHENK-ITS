import { MinusCircle } from "lucide-react";

/**
 * Çekimserlik göstergesi.
 *
 * Sistem hüküm vermediğinde bunu bir HATA gibi değil, bilinçli bir karar
 * olarak sunar. "Doğrulanamadı", "yanlış" demek değildir.
 */
const GEREKCE_METNI: Record<string, string> = {
  low_confidence: "Model yeterli güven düzeyine ulaşamadı.",
  short_text: "Metin, güvenilir bir değerlendirme için fazla kısa.",
  insufficient_sources: "Yeterli bağımsız kaynak bulunamadı.",
  out_of_scope: "Bu içerik değerlendirme kapsamı dışında.",
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
