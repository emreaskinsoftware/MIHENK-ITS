export function BosDurum({
  ikon, baslik, aciklama,
}: { ikon: React.ReactNode; baslik: string; aciklama: string }) {
  return (
    <div className="grid place-items-center py-24 px-8 text-center">
      <div className="text-metin-sonuk/40 mb-5">{ikon}</div>
      <h2 className="text-[19px] font-semibold mb-1.5">{baslik}</h2>
      <p className="text-[15px] text-metin-ikincil max-w-sm">{aciklama}</p>
    </div>
  );
}
