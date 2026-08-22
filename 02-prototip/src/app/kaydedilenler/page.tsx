import { Bookmark } from "lucide-react";
import { BosDurum } from "@/components/layout/BosDurum";
import { SayfaBasligi } from "@/components/layout/SayfaBasligi";

export default function KaydedilenlerSayfasi() {
  return (
    <>
      <SayfaBasligi baslik="Kaydedilenler" />
      <BosDurum
        ikon={<Bookmark size={80} strokeWidth={1.2} />}
        baslik="Henüz kaydedilmiş gönderi yok"
        aciklama="Beğendiğiniz gönderileri kaydederek burada görebilirsiniz"
      />
    </>
  );
}
