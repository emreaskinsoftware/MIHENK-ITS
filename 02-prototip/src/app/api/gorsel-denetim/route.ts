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

  // --- DÜZELTİLDİ: BU UÇ GÖRSELİ ANALİZ ETMİYOR ---------------------------
  // Önceki sürüm, simülasyon verisinin altın etiketini okuyup şunları
  // UYDURUYORDU:
  //   · `olasilik: 0.87` — hiçbir yerde ölçülmemiş sabit bir sayı
  //   · "Doku ve kenar geçişlerinde üretici model izlerine benzer örüntü"
  //     — hiç çalıştırılmamış bir adli analizin bulgusu gibi sunulan cümle
  //   · `kaynak: "yerel-siniflandirici"` — var olmayan bir sınıflandırıcı
  // Üstelik `dogrula` ucundaki gibi bir uyarı alanı da yoktu; arayüz bunları
  // gerçek analiz sonucu olarak gösteriyordu.
  //
  // Uydurma bir kanıt, kanıt yokluğundan kötüdür: jüri "bunu nasıl tespit
  // ettiniz?" diye sorduğunda cevap "cevap anahtarını okuduk" olur ve bu,
  // ölçülmüş diğer bulguların da güvenilirliğini götürür (spec 2).
  //
  // GERÇEK KÖKEN DENETİMİ BACKEND'DE VAR: `backend/app/provenance/`
  // (`GET /api/koken/{post_id}`) C2PA/IPTC üretim etiketi denetimini gerçekten
  // yapıyor ve kanıt yoksa `display=false` ile ÇEKİMSER kalıyor. Bu arayüzün
  // simülasyon verisi backend'in akışıyla eşleşmediği için o uç buradan
  // çağrılamıyor; kimliksiz bir köken ucu açılana kadar burada yalnızca
  // veri kümesinin etiketi, ETİKET OLDUĞU SÖYLENEREK döndürülür.
  return NextResponse.json({
    gonderiId: g.id,
    sonuc: yapay ? "YAPAY_URETIM_OLASILIGI_YUKSEK" : "KOKEN_DOGRULANDI",
    // Olasılık üretilmiyor: ölçülmemiş bir sayı raporlanmaz.
    olasilik: null,
    // Adli bulgu üretilmiyor: çalıştırılmamış bir analizin sonucu yazılmaz.
    sinyaller: null,
    uyari: yapay
      ? "Bu görsel, simülasyon veri kümesinde yapay üretim olarak etiketlidir. Bu bir kesin hüküm değildir; nihai değerlendirme size aittir."
      : null,
    kaynak: "simulasyon-etiketi",
    not:
      "Bu sonuç bir görsel analizinden DEĞİL, simülasyon veri kümesinin bilinen " +
      "etiketinden gelmektedir. Görsel köken sınıflandırıcısı henüz bu arayüze " +
      "bağlı değildir; sistemin görsel tespit başarımını göstermez.",
  });
}
