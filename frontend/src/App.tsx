/**
 * Uygulama kabuğu — akış, özet paneli ve asistan çekmecesini birleştirir.
 *
 * DURUM YÖNETİMİ NOTU (spec 2, madde 6): Kalıcı durum sunucu tarafındadır.
 * Burada tutulan tek şey görüntü durumudur (seçili kategori, açık çekmece,
 * vurgulanan gönderi). Okuma geçmişi gibi kişisel veriler tarayıcıda kalıcı
 * saklanmaz.
 *
 * SİNYALLERİN TEMBEL YÜKLENMESİ: Tespit ve köken bilgisi kart göründüğünde
 * değil, akış yüklendikten sonra toplu olarak istenir. NEDEN: her kart için
 * ayrı istek atmak 60 istek demektir; tek seferde toplamak hem hızlı hem de
 * sunucuya nazik. Gerçek dağıtımda bu veri akış yanıtına gömülür.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { AsistanCekmecesi } from "./components/AsistanCekmecesi";
import { GonderiKarti } from "./components/GonderiKarti";
import { OzetPaneli } from "./components/OzetPaneli";
import { api, type Gonderi, type Kategori, type KokenSonucu, type TespitSonucu } from "./lib/api";

export function App() {
  const [kategori, setKategori] = useState<Kategori>("gundem");
  const [gonderiler, setGonderiler] = useState<Gonderi[]>([]);
  const [tespitler, setTespitler] = useState<Record<string, TespitSonucu>>({});
  const [kokenler, setKokenler] = useState<Record<string, KokenSonucu[]>>({});
  const [itirazlar, setItirazlar] = useState<Set<string>>(new Set());
  const [acikAsistan, setAcikAsistan] = useState<Gonderi | null>(null);
  const [vurgulu, setVurgulu] = useState<string | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const vurguZamanlayici = useRef<number | null>(null);

  // --- Akışı yükle ---
  useEffect(() => {
    let iptal = false;
    setYukleniyor(true);
    api
      .akis(kategori)
      .then((veri) => {
        if (iptal) return;
        setGonderiler(veri);
        setYukleniyor(false);
      })
      .catch(() => !iptal && setYukleniyor(false));
    return () => {
      iptal = true;
    };
  }, [kategori]);

  // --- Sinyalleri topla (tespit + köken) ---
  useEffect(() => {
    let iptal = false;
    if (gonderiler.length === 0) return;
    (async () => {
      const yeniTespit: Record<string, TespitSonucu> = {};
      const yeniKoken: Record<string, KokenSonucu[]> = {};
      for (const g of gonderiler) {
        try {
          yeniTespit[g.id] = await api.tespit(g.id);
          if (g.media.length > 0) {
            yeniKoken[g.id] = (await api.koken(g.id)).media;
          }
        } catch {
          // Sinyal alınamazsa kart sinyalsiz gösterilir: sinyalin yokluğu,
          // yanlış bir sinyal göstermekten iyidir (İlke 2).
        }
      }
      if (iptal) return;
      setTespitler((t) => ({ ...t, ...yeniTespit }));
      setKokenler((k) => ({ ...k, ...yeniKoken }));
    })();
    return () => {
      iptal = true;
    };
  }, [gonderiler]);

  // --- Kaynak çipinden gönderiye gitme ---
  const kaynagaGit = useCallback((postId: string) => {
    const hedef = document.getElementById(`gonderi-${postId}`);
    if (!hedef) return;
    hedef.scrollIntoView({ behavior: "smooth", block: "center" });
    // Odağı da taşıyoruz: klavye ve ekran okuyucu kullanıcısı için kaydırma
    // tek başına yetmez, "neredeyim" bilgisi odakla gelir.
    hedef.focus({ preventScroll: true });
    setVurgulu(postId);
    if (vurguZamanlayici.current) window.clearTimeout(vurguZamanlayici.current);
    vurguZamanlayici.current = window.setTimeout(() => setVurgulu(null), 2500);
  }, []);

  const itirazEkle = useCallback((postId: string) => {
    setItirazlar((s) => new Set(s).add(postId));
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      {/* Klavye kullanıcıları için içeriğe atlama bağlantısı */}
      <a
        href="#akis"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-white focus:px-4 focus:py-2 focus:shadow"
      >
        İçeriğe atla
      </a>

      <header className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">MİHENK</h1>
        <p className="mt-1 max-w-2xl text-sm text-mihenk-ikincil">
          Akışı kısaltır, söylediği her cümleyi kaynağına bağlar, emin
          olmadığında susar.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">
        <main id="akis" aria-label="Akış">
          {yukleniyor ? (
            <p className="text-sm text-mihenk-ikincil">Akış yükleniyor…</p>
          ) : (
            <div className="space-y-3">
              {gonderiler.map((g) => (
                <GonderiKarti
                  key={g.id}
                  gonderi={g}
                  tespit={tespitler[g.id] ?? null}
                  koken={kokenler[g.id] ?? []}
                  vurgulu={vurgulu === g.id}
                  itirazVar={itirazlar.has(g.id)}
                  onAsistan={setAcikAsistan}
                  onItiraz={itirazEkle}
                />
              ))}
            </div>
          )}
        </main>

        <div className="lg:sticky lg:top-6 lg:h-fit">
          <OzetPaneli
            kategori={kategori}
            onKategoriDegis={setKategori}
            onKaynagaGit={kaynagaGit}
          />
        </div>
      </div>

      {acikAsistan && (
        <AsistanCekmecesi
          gonderi={acikAsistan}
          onKapat={() => setAcikAsistan(null)}
          onKaynagaGit={(id) => {
            setAcikAsistan(null);
            kaynagaGit(id);
          }}
        />
      )}
    </div>
  );
}
