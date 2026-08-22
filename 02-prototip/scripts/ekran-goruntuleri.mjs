/**
 * Rapor için ekran görüntüsü üretici.
 *
 * NEDEN BETİK: Elle alınan görüntüler her seferinde farklı pencere boyutunda,
 * farklı temada ve farklı veriyle çıkar; rapor güncellenince yeniden almak
 * gerekir ve hangisinin güncel olduğu bilinmez. Betik, arayüz değiştiğinde
 * tek komutla hepsini yeniler.
 *
 * ÖNEMLİ: Görüntüler ÜRETİM DERLEMESİNDEN alınır (`next build` + `next start`).
 * Geliştirme sunucusu kendi araç katmanını sayfaya bindiriyor ve o katman
 * görüntüye giriyor — rapora ürünün değil geliştirme ortamının resmi girerdi.
 *
 * Çalıştırma:
 *     npx next build && npx next start -p 3000
 *     node scripts/ekran-goruntuleri.mjs
 */

import { chromium } from "playwright";
import { readFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const BURASI = dirname(fileURLToPath(import.meta.url));
const CIKTI = join(BURASI, "..", "..", "docs", "gorseller");
const TABAN = process.env.MIHENK_UI ?? "http://localhost:3000";

/** Masaüstü ve mobil: rapor 3.3 duyarlı tasarım iddiasını da taşıyor. */
const OLCULER = {
  masaustu: { width: 1440, height: 900 },
  mobil: { width: 390, height: 844 },
};

/**
 * Ekran görüntüsünde kullanılacak gönderiyi seçer.
 *
 * Görseli VE doğrulanabilir iddiası olan bir gönderi aranır: rapora girecek
 * kare, en çok bileşeni aynı anda gösterendir (YZ sinyali, görsel köken,
 * doğrulama paneli). Bulunamazsa ilk gönderiye düşülür.
 */
function zenginGonderiSec() {
  const g = JSON.parse(readFileSync(join(BURASI, "..", "data", "gonderiler.json"), "utf-8"));
  return g.find((x) => x.gorsel_var && x.dogrulanabilir_iddia) ?? g[0];
}

/**
 * Rıza bandını kapatır.
 *
 * Band sabit konumludur ve kadrajın ortasına biner; rapor görselinde
 * anlatılmak istenen bileşenin üstünü örter. "Yalnızca zorunlu" seçilir —
 * ürünün varsayılan duruşu da budur (rıza gerektiren her şey kapalı başlar),
 * yani görüntü ürünü olduğundan farklı göstermiyor.
 *
 * Rıza akışının KENDİSİ ayrı bir görselde gösterilir; orada kapatılmaz.
 */
async function rizaKapat(sayfa) {
  const dugme = sayfa.getByRole("button", { name: "Yalnızca zorunlu" });
  if (await dugme.count()) {
    await dugme.first().click();
    await sayfa.waitForTimeout(400); // kapanma geçişi
  }
}

async function main() {
  mkdirSync(CIKTI, { recursive: true });
  const zengin = zenginGonderiSec();
  const tarayici = await chromium.launch();

  /**
   * Her görüntü bir RAPOR İDDİASINA karşılık gelir. İddiası olmayan ekran
   * görüntüsü rapora sayfa doldurmaktan başka bir şey katmaz.
   */
  const kareler = [
    {
      ad: "01-ana-akis",
      yol: "/",
      olcu: "masaustu",
      tema: "dark",
      aciklama: "Akış sırası değişmez; MİHENK üstte bir okuma katmanıdır",
    },
    {
      ad: "02-atifli-ozet",
      yol: "/",
      olcu: "masaustu",
      tema: "dark",
      aciklama: "İlke 1 — her cümlenin yanında kaynak rozeti, açılınca gönderiler",
      hazirla: async (s) => {
        await s.waitForSelector('button[aria-label^="Bu cümlenin"]', { timeout: 30_000 });
        await s.locator('button[aria-label^="Bu cümlenin"]').first().click();
        // Panelin tamamı görünsün: alt kısmı kırpılmasın diye kadraj daraltılır.
        await s.locator('section[aria-label="MİHENK özet paneli"]').scrollIntoViewIfNeeded();
      },
      kirp: 'section[aria-label="MİHENK özet paneli"]',
    },
    {
      ad: "03-atifli-ozet-acik-tema",
      yol: "/",
      olcu: "masaustu",
      tema: "light",
      aciklama: "Aynı panel açık temada — erişilebilirlik denetimi iki temada da koşar",
      hazirla: async (s) => {
        await s.waitForSelector('button[aria-label^="Bu cümlenin"]', { timeout: 30_000 });
        await s.locator('button[aria-label^="Bu cümlenin"]').first().click();
      },
      kirp: 'section[aria-label="MİHENK özet paneli"]',
    },
    {
      ad: "04-gonderi-ayrinti",
      yol: `/gonderi/${zengin.id}`,
      olcu: "masaustu",
      tema: "dark",
      aciklama: "Gönderi ayrıntısı — YZ sinyali rozeti ve doğrulama paneli",
    },
    {
      ad: "05-ana-akis-mobil",
      yol: "/",
      olcu: "mobil",
      tema: "dark",
      aciklama: "Duyarlı tasarım — aynı arayüz mobil genişlikte",
    },
    {
      ad: "06-riza-akisi",
      yol: "/",
      olcu: "masaustu",
      tema: "dark",
      aciklama: "Rıza akışı — her kullanım varsayılan olarak KAPALI başlar",
      rizayiKapatma: true,
      kirp: 'div[role="dialog"][aria-labelledby="riza-baslik"] > div',
    },
    {
      ad: "07-kesfet",
      yol: "/kesfet",
      olcu: "masaustu",
      tema: "dark",
      aciklama: "Keşfet — olay kümeleri ve çerçeve dağılımı",
    },
  ];

  for (const k of kareler) {
    const baglam = await tarayici.newContext({
      viewport: OLCULER[k.olcu],
      colorScheme: k.tema,
      locale: "tr-TR",
      deviceScaleFactor: 2, // Baskıda bulanıklaşmasın
    });
    const sayfa = await baglam.newPage();
    // Tema `data-tema` özniteliğiyle açılıyor; ilk boyamadan önce yazılır.
    await sayfa.addInitScript((t) => {
      if (t === "light") document.documentElement.dataset.tema = "acik";
    }, k.tema);
    await sayfa.goto(TABAN + k.yol, { waitUntil: "networkidle", timeout: 60_000 });
    await sayfa.evaluate((t) => {
      if (t === "light") document.documentElement.dataset.tema = "acik";
      else delete document.documentElement.dataset.tema;
    }, k.tema);

    if (!k.rizayiKapatma) await rizaKapat(sayfa);
    if (k.hazirla) await k.hazirla(sayfa).catch(() => {});

    const hedef = k.kirp ? sayfa.locator(k.kirp) : sayfa;
    await hedef.screenshot({ path: join(CIKTI, `${k.ad}.png`) });
    console.log(`${k.ad.padEnd(28)} ${k.olcu.padEnd(9)} ${k.tema.padEnd(5)} — ${k.aciklama}`);
    await baglam.close();
  }

  await tarayici.close();
  console.log(`\n${kareler.length} görüntü -> docs/gorseller/`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
