import { MessagesSquare, PenLine, Search } from "lucide-react";
import { BosDurum } from "@/components/layout/BosDurum";

export default function MesajlarSayfasi() {
  return (
    <>
      <header className="flex items-center gap-4 px-5 py-5 border-b border-cizgi">
        <h1 className="text-[22px] font-bold">Mesajlar</h1>
        <div className="ml-auto flex items-center gap-4">
          <button type="button" className="text-[14px] text-mavi hover:underline">Mesaj İstekleri</button>
          <button type="button" aria-label="Mesajlarda ara"
                  className="p-2 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover">
            <Search size={18} />
          </button>
          <button type="button" aria-label="Yeni mesaj"
                  className="p-2 rounded-full text-metin-ikincil hover:text-metin hover:bg-hover">
            <PenLine size={18} />
          </button>
        </div>
      </header>
      <BosDurum
        ikon={<MessagesSquare size={90} strokeWidth={1.2} />}
        baslik="Henüz mesajınız bulunmuyor"
        aciklama="Arkadaşlarınızla sohbet etmeye başlamak için yeni bir mesaj gönderin"
      />
    </>
  );
}
