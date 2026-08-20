import { NextResponse } from "next/server";
import { kategoriOzetle, kisiselOzetle, olayOzetle } from "@/lib/ozet/cikarimsal";
import { akisGetir, gonderiGetir, olayKumesiGetir } from "@/lib/veri";
import { uret } from "@/lib/yz/saglayici";
import type { Kategori } from "@/lib/tipler";

const SISTEM = `Sen MİHENK'sin: Türkçe sosyal medya akışını özetleyen bir okuma katmanı.

Kurallar:
- Yalnızca sana verilen gönderilere dayan. Dışarıdan bilgi ekleme.
- Bir olayın farklı bakış açıları varsa HEPSİNİ dengeli biçimde yansıt.
  Tek bir çerçeveyi öne çıkarma; en çok etkileşim alan görüş "doğru" değildir.
- Kaynağı belirsiz iddiaları olgu gibi aktarma; "iddia edildi", "doğrulanmadı"
  gibi ifadelerle işaretle.
- Sade, kısa, gazete diline yakın Türkçe kullan. En fazla 4 cümle.
- Emin olmadığın hiçbir sayıyı veya ismi yazma.`;

export async function POST(istek: Request) {
  const { tur, kategori, olayId, gonderiId } = await istek.json();

  // ---- Gönderi bazlı özet ----
  if (tur === "gonderi" && gonderiId) {
    const g = gonderiGetir(gonderiId);
    if (!g) return NextResponse.json({ hata: "Gönderi bulunamadı" }, { status: 404 });

    const yz = await uret({
      sistem: SISTEM,
      kullanici: `Şu gönderiyi tek cümlede özetle:\n\n"${g.metin}"`,
      enFazlaJeton: 200,
    });
    return NextResponse.json({
      ozet: yz.metin || g.metin.slice(0, 160),
      saglayici: yz.saglayici,
      kaynakGonderiSayisi: 1,
    });
  }

  // ---- Kişisel akış ----
  if (tur === "kisisel") {
    const yerel = kisiselOzetle(akisGetir());
    const yz = await uret({
      sistem: SISTEM,
      kullanici: `Kişisel akış özeti üret:\n\n${yerel}`,
      enFazlaJeton: 350,
    });
    return NextResponse.json({ ozet: yz.metin || yerel, saglayici: yz.saglayici });
  }

  // ---- Olay bazlı özet (tarafsızlık dengelemesiyle) ----
  if (tur === "olay" && olayId) {
    const gonderiler = olayKumesiGetir(olayId);
    if (!gonderiler.length) {
      return NextResponse.json({ hata: "Olay bulunamadı" }, { status: 404 });
    }
    const yerel = olayOzetle(olayId, gonderiler[0].olay_basligi!, gonderiler[0].kategori, gonderiler);

    // Modele çerçeve etiketleriyle birlikte veriyoruz ki dengeyi koruyabilsin
    const girdi = gonderiler
      .map((g) => `[${g.cerceve}] ${g.metin}`)
      .join("\n");

    const yz = await uret({
      sistem: SISTEM,
      kullanici:
        `Olay: ${yerel.baslik}\n\nAşağıda bu olay hakkındaki gönderiler, köşeli parantez içinde ` +
        `bakış açısı etiketleriyle veriliyor. Tüm bakış açılarını dengeli yansıtan bir özet yaz:\n\n${girdi}`,
      enFazlaJeton: 400,
    });

    return NextResponse.json({
      ...yerel,
      ozet: yz.metin || yerel.ozet,
      saglayici: yz.saglayici,
      yontem: yz.metin ? "uretici" : "cikarimsal",
    });
  }

  // ---- Kategori özeti ----
  if (tur === "kategori" && kategori) {
    const sonuc = kategoriOzetle(kategori as Kategori);
    return NextResponse.json({ ...sonuc, yontem: "cikarimsal" });
  }

  return NextResponse.json({ hata: "Geçersiz istek türü" }, { status: 400 });
}
