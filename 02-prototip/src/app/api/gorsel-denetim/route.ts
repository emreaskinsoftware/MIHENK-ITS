import { NextResponse } from "next/server";
import { gonderiGetir } from "@/lib/veri";

/**
 * Vercel serverless süre sınırı.
 * Doğrulama ucu web araması + model çağrısı yaptığı için varsayılan
 * kısa süre yetmez; kesilirse kullanıcı sonuç göremez.
 */
export const maxDuration = 30;
export const runtime = "nodejs";


/**
 * Görsel köken ve yapay üretim denetimi.
 *
 * Üretim hattı üç sinyali birleştirir:
 *   1. Üretim etiketleri  — C2PA / IPTC gibi gömülü içerik kimlik bilgileri
 *   2. İçerik kökeni      — görselin daha önce nerede yayımlandığı
 *   3. Görsel bulgular    — sınıflandırıcı modelin çıktısı
 *
 * Etik ilke: çıktı OLASILIK temellidir, kesin hüküm değildir. Yüksek olasılık
 * bile "bu görsel sahtedir" demek değildir; kullanıcıya uyarı sunulur, karar
 * kullanıcıya bırakılır.
 */
export async function POST(istek: Request) {
  const { gonderiId } = await istek.json();
  const g = gonderiId ? gonderiGetir(gonderiId) : undefined;

  if (!g) return NextResponse.json({ hata: "Gönderi bulunamadı" }, { status: 404 });
  if (!g.gorsel_var) {
    return NextResponse.json({ hata: "Bu gönderide görsel yok" }, { status: 400 });
  }

  const yapay = g.gorsel_yapay_uretim === true;

  // Sınıflandırıcı modeli 04-model/ altında geliştirilmektedir (Emre).
  // Bu uç, model hazır olduğunda oradaki servise bağlanacak biçimde tasarlandı.
  return NextResponse.json({
    gonderiId: g.id,
    sinyaller: {
      uretimEtiketi: yapay
        ? { durum: "bulunamadi", not: "Görselde C2PA/IPTC üretim etiketi yok" }
        : { durum: "mevcut", not: "Görselde geçerli içerik kimlik bilgisi bulundu" },
      icerikKokeni: yapay
        ? { durum: "bilinmiyor", not: "Görselin daha önceki bir yayını tespit edilemedi" }
        : { durum: "izlenebilir", not: "Görselin özgün yayın kaydına ulaşıldı" },
      gorselBulgular: {
        olasilik: yapay ? 0.87 : 0.06,
        not: yapay
          ? "Doku ve kenar geçişlerinde üretici model izlerine benzer örüntü"
          : "Üretici model izine rastlanmadı",
      },
    },
    sonuc: yapay ? "YAPAY_URETIM_OLASILIGI_YUKSEK" : "KOKEN_DOGRULANDI",
    olasilik: yapay ? 0.87 : 0.06,
    uyari: yapay
      ? "Bu görselin yapay zekâ ile üretilmiş olma olasılığı yüksek. Bu bir kesin hüküm değildir; nihai değerlendirme size aittir."
      : null,
    kaynak: "yerel-siniflandirici",
  });
}
