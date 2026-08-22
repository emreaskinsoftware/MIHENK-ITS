import { Cloud } from "lucide-react";
import { BosDurum } from "@/components/layout/BosDurum";
import { SayfaBasligi } from "@/components/layout/SayfaBasligi";

export default function NodSayfasi() {
  return (
    <>
      <SayfaBasligi baslik="Nod Oyna" />
      <BosDurum
        ikon={<Cloud size={80} strokeWidth={1.2} />}
        baslik="Bu bölüm kapsam dışında"
        aciklama="Nod Oyna, NSosyal'in oyunlaştırma modülüdür. MİHENK bu alana müdahale etmez; prototipte yalnızca gezinme bütünlüğü için yer alır."
      />
    </>
  );
}
