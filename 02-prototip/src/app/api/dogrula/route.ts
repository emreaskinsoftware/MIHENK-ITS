import { NextResponse } from "next/server";
import { gonderiGetir } from "@/lib/veri";
import { uret } from "@/lib/yz/saglayici";
import { GUVENLIK_BASLIGI, guvenilmeyeniSar } from "@/lib/yz/guvenlik";

/**
 * Vercel serverless süre sınırı.
 * Doğrulama ucu web araması + model çağrısı yaptığı için varsayılan
 * kısa süre yetmez; kesilirse kullanıcı sonuç göremez.
 */
export const maxDuration = 60;
export const runtime = "nodejs";


/**
 * Ajan tabanlı doğrulama ucu.
 *
 * Etik ilke (bkz. rapor "Veri, model, etik ve performans" bölümü):
 * Sistem üç sonuçtan birini verir — DOGRULANDI, YANLIS, DOGRULANAMADI.
 * "Doğrulanamadı", "yanlış" demek DEĞİLDİR. Yeterli kaynak bulunamadığında
 * sistem hüküm vermez; nihai karar kullanıcınındır.
 */
const SISTEM = `Sen MİHENK'in doğrulama ajanısın. Bir iddiayı açık web kaynaklarıyla sınarsın.

${GUVENLIK_BASLIGI}

Adımlar:
1. İddiadaki sınanabilir olguyu ayır (sayı, tarih, isim, olay).
2. Web'de güvenilir kaynak ara. Resmî kurum, ulusal ajans ve köklü yayın organlarını öncele.
3. Bulguları karşılaştır.

Çıktı biçimi (kesinlikle bu yapıda):
SONUC: DOGRULANDI | YANLIS | DOGRULANAMADI
GUVEN: 0-100 arası bir tam sayı
ACIKLAMA: en fazla 3 cümle

Katı kurallar:
- Yeterli kaynak bulamazsan SONUC=DOGRULANAMADI yaz. Tahmin yürütme.
- DOGRULANAMADI, iddianın yanlış olduğu anlamına gelmez; bunu açıklamada belirt.
- Kaynak bulamadığın hiçbir sayıyı veya ismi üretme.`;

export async function POST(istek: Request) {
  const { gonderiId, iddia } = await istek.json();

  let sinanacak = iddia as string | undefined;
  let altinEtiket: boolean | null = null;

  if (gonderiId) {
    const g = gonderiGetir(gonderiId);
    if (!g) return NextResponse.json({ hata: "Gönderi bulunamadı" }, { status: 404 });
    sinanacak = g.dogrulanabilir_iddia ?? g.metin;
    altinEtiket = g.iddia_dogru_mu;
  }
  if (!sinanacak) {
    return NextResponse.json({ hata: "Sınanacak iddia yok" }, { status: 400 });
  }

  const yz = await uret({
    sistem: SISTEM,
    // İddia metni gönderiden gelir, yani güvenilmeyen girdidir.
    kullanici: `Şu iddiayı doğrula:\n\n${guvenilmeyeniSar(sinanacak, "IDDIA")}`,
    webAramasi: true,
    enFazlaJeton: 700,
  });

  // Sağlayıcı yoksa: simülasyon verisinin altın etiketi üzerinden yanıt üret.
  // Bu bir tahmin değil, veri kümesinin bilinen doğruluk değeridir.
  //
  // GÜVEN SKORU BURADA ÜRETİLMEZ (düzeltildi): Önceki sürüm `guven: 92`
  // yazıyordu. O sayı hiçbir yerde ölçülmemişti — ne bir modelin çıktısıydı
  // ne de bir doğrulama koşusunun sonucu. Ekranda %92'lik bir güven çubuğu
  // çizdiriyordu ve bu, projenin "ölçülmemiş sayı raporlanmaz" ilkesinin
  // (spec 2) doğrudan ihlaliydi.
  //
  // Altın etiket zaten kesin bilgidir; ona bir "güven yüzdesi" iliştirmek
  // hem gereksiz hem yanıltıcıdır. `guven: 0` gönderiliyor, çünkü arayüz
  // sıfırda çubuğu hiç çizmiyor (bkz. DogrulamaPaneli, `guven > 0` koşulu).
  if (!yz.metin) {
    return NextResponse.json({
      sonuc: altinEtiket === false ? "YANLIS" : altinEtiket === true ? "DOGRULANDI" : "DOGRULANAMADI",
      guven: 0,
      aciklama:
        altinEtiket === null
          ? "Bu içerikte sınanabilir bir olgu iddiası tespit edilemedi. Doğrulanamamış olması, iddianın yanlış olduğu anlamına gelmez."
          : altinEtiket
            ? "İddia, simülasyon veri kümesindeki referans kaynaklarla örtüşmektedir."
            : "İddia, simülasyon veri kümesindeki referans kaynaklarla çelişmektedir.",
      kaynaklar: [],
      saglayici: "yerel",
      // Bu uyarı arayüzde GÖRÜNÜR (DogrulamaPaneli, `sonuc.not`). Jüri
      // demosunda anahtar tanımlı olmadığı için varsayılan yol budur;
      // gösterilen sonucun bir doğrulama koşusu DEĞİL, veri kümesinin cevap
      // anahtarı olduğu saklanmamalıdır.
      not:
        "Dış model anahtarı tanımlı değil. Bu sonuç bir doğrulama koşusundan " +
        "değil, simülasyon veri kümesinin bilinen etiketinden gelmektedir; " +
        "sistemin doğrulama başarımını göstermez.",
      iddia: sinanacak,
    });
  }

  return NextResponse.json({ ...ayikla(yz.metin), kaynaklar: yz.kaynaklar ?? [], saglayici: yz.saglayici, iddia: sinanacak });
}

function ayikla(metin: string) {
  const sonuc = /SONUC:\s*(DOGRULANDI|YANLIS|DOGRULANAMADI)/i.exec(metin)?.[1]?.toUpperCase() ?? "DOGRULANAMADI";
  const guven = Number(/GUVEN:\s*(\d{1,3})/i.exec(metin)?.[1] ?? 0);
  const aciklama = /ACIKLAMA:\s*([\s\S]+)/i.exec(metin)?.[1]?.trim() ?? metin.trim();
  return { sonuc, guven: Math.min(100, Math.max(0, guven)), aciklama };
}
