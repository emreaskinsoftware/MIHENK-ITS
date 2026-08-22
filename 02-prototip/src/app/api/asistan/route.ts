import { NextResponse } from "next/server";
import { gonderiGetir, olayKumesiGetir } from "@/lib/veri";
import { uret } from "@/lib/yz/saglayici";

/**
 * Vercel serverless süre sınırı.
 * Doğrulama ucu web araması + model çağrısı yaptığı için varsayılan
 * kısa süre yetmez; kesilirse kullanıcı sonuç göremez.
 */
export const maxDuration = 60;
export const runtime = "nodejs";


/**
 * Entegre dijital asistan.
 * Kullanıcı, akıştan çıkmadan bir gönderi hakkında soru sorabilir.
 *
 * Kapsam sınırı: asistan yalnızca gönderinin bağlamı ve olay kümesi üzerinden
 * konuşur. Genel amaçlı bir sohbet aracı değildir; bu, hem odaklı kalmasını
 * hem de bağlam dışına çıkıp uydurma bilgi üretmesini engeller.
 */
const SISTEM = `Sen MİHENK'in akış içi asistanısın. Kullanıcı, gördüğü bir gönderi
hakkında soru sorar. Görevin o gönderiyi ve etrafındaki tartışmayı açıklamaktır.

Kurallar:
- Yalnızca sana verilen gönderi ve olay bağlamına dayan.
- Bağlamda olmayan bir şey sorulursa "Bu gönderinin bağlamında bu bilgi yok" de.
- Bir olayda farklı görüşler varsa hepsini aktar, taraf tutma.
- Kaynağı belirsiz iddiaları olgu gibi sunma.
- Kısa ve sade Türkçe. En fazla 4 cümle.`;

export async function POST(istek: Request) {
  const { gonderiId, soru } = await istek.json();
  if (!soru) return NextResponse.json({ hata: "Soru gerekli" }, { status: 400 });

  const g = gonderiId ? gonderiGetir(gonderiId) : undefined;
  if (gonderiId && !g) {
    return NextResponse.json({ hata: "Gönderi bulunamadı" }, { status: 404 });
  }

  let baglam = "";
  if (g) {
    baglam = `Gönderi: "${g.metin}"\nYazar: @${g.yazar.kullanici_adi}\nKategori: ${g.kategori}`;
    if (g.olay_id) {
      const kume = olayKumesiGetir(g.olay_id);
      baglam +=
        `\n\nBu gönderi "${g.olay_basligi}" olayının parçası. ` +
        `Aynı olay hakkındaki diğer gönderiler (bakış açısı etiketleriyle):\n` +
        kume.filter((k) => k.id !== g.id).map((k) => `[${k.cerceve}] ${k.metin}`).join("\n");
    }
  }

  const yz = await uret({
    sistem: SISTEM,
    kullanici: `${baglam}\n\nKullanıcının sorusu: ${soru}`,
    enFazlaJeton: 500,
  });

  if (!yz.metin) {
    return NextResponse.json({
      yanit:
        "Asistan şu anda çevrimdışı çalışıyor. Dış model anahtarı tanımlandığında " +
        "bu gönderi ve olay bağlamı üzerinden sorunuzu yanıtlayacak.",
      saglayici: "yerel",
      baglamGonderiSayisi: g?.olay_id ? olayKumesiGetir(g.olay_id).length : g ? 1 : 0,
    });
  }

  return NextResponse.json({
    yanit: yz.metin,
    saglayici: yz.saglayici,
    baglamGonderiSayisi: g?.olay_id ? olayKumesiGetir(g.olay_id).length : g ? 1 : 0,
  });
}
