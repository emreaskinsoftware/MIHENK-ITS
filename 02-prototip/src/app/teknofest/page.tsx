import { Rocket } from "lucide-react";
import { SayfaBasligi } from "@/components/layout/SayfaBasligi";

export default function TeknofestSayfasi() {
  return (
    <>
      <SayfaBasligi baslik="TEKNOFEST Köşesi" />
      <div className="px-5 pb-10">
        <div className="rounded-2xl gradyan-marka p-6 text-white mb-5">
          <Rocket size={30} className="mb-3" />
          <h2 className="text-[22px] font-bold mb-1.5">TEKNOFEST 2026</h2>
          <p className="text-[15px] opacity-90">
            Yarışmalar, etkinlik takvimi ve duyurular bu bölümde toplanır.
          </p>
        </div>
        <p className="text-[15px] text-metin-ikincil">
          Bu bölüm NSosyal platformunun kendi içeriğiyle beslenir. MİHENK katmanı
          buradaki gönderilere de özet ve doğrulama hizmeti sunar.
        </p>
      </div>
    </>
  );
}
