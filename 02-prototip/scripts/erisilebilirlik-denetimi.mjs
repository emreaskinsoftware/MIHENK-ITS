/**
 * Erişilebilirlik denetimi — ölçüm betiği.
 *
 * NEDEN BETİK, NEDEN ELLE DEĞİL: Rapor 3.3'te "erişilebilirlik" bir iddia
 * olarak duruyordu. Bu projede ölçülmemiş sayı raporlanmıyor (spec 2);
 * erişilebilirlik de bir istisna değil. Bu betik, denetimi tekrarlanabilir
 * kılar: jüri aynı komutu çalıştırıp aynı sonucu alabilir.
 *
 * YÖNTEM: axe-core (Deque Systems), WCAG 2.0/2.1 A ve AA etiketleri. Kendi
 * kontrol listemizi yazmıyoruz — kendi yazdığımız kontrolden geçmek, kendi
 * yazdığımız test kümesinde %100 almak gibidir (bkz. rapor Tablo 1 uyarısı).
 *
 * SINIR — otomatik denetimin göremediği: axe, WCAG ihlallerinin yaklaşık
 * üçte birini yakalar. Klavye tuzağı, odak sırasının MANTIKLI olması, ekran
 * okuyucunun okuduğu metnin ANLAMLI olması gibi konular elle denetlenir.
 * Bu yüzden betik ayrıca klavye gezinme ve odak görünürlüğü ölçümü yapar,
 * ve rapor bu sınırı açıkça yazar.
 *
 * Çalıştırma (arayüz http://localhost:3000 üzerinde ayakta olmalı):
 *     node scripts/erisilebilirlik-denetimi.mjs
 */

import { chromium } from "playwright";
import { markdownUret } from "./erisilebilirlik-rapor.mjs";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const BURASI = dirname(fileURLToPath(import.meta.url));
const DEPO_KOKU = join(BURASI, "..", "..");
const CIKTI_DIZIN = join(DEPO_KOKU, "eval", "results");

const TABAN = process.env.MIHENK_UI ?? "http://localhost:3000";

// axe-core paketten okunur, CDN'den DEĞİL: dış kaynağa bağlı bir ölçüm,
// ağ kesildiğinde tekrarlanamaz hâle gelir.
const AXE_KAYNAK = readFileSync(require.resolve("axe-core/axe.min.js"), "utf-8");

/** Denetlenen sayfalar. Gönderi kimliği veri kümesinden okunur. */
function sayfalar() {
  const gonderiler = JSON.parse(
    readFileSync(join(BURASI, "..", "data", "gonderiler.json"), "utf-8"),
  );
  // Görseli ve doğrulanabilir iddiası olan bir gönderi: en çok bileşen
  // barındıran sayfa, denetimin en geniş yüzeyi.
  const zengin =
    gonderiler.find((g) => g.gorsel_var && g.dogrulanabilir_iddia) ?? gonderiler[0];
  return [
    { ad: "Ana akış + özet paneli", yol: "/", ozetPaneliniAc: true },
    { ad: "Gönderi ayrıntısı", yol: `/gonderi/${zengin.id}` },
    { ad: "Keşfet", yol: "/kesfet" },
    { ad: "Ayarlar", yol: "/ayarlar" },
    { ad: "İçerik üretici", yol: "/uretici" },
    { ad: "TEKNOFEST kayıt", yol: "/teknofest" },
  ];
}

/** Tek bir sayfada axe çalıştırır. */
async function axeCalistir(sayfa) {
  await sayfa.addScriptTag({ content: AXE_KAYNAK });
  return sayfa.evaluate(async () => {
    // WCAG 2.0/2.1 A + AA. "best-practice" etiketi bilinçli olarak DIŞARIDA:
    // o kural kümesi WCAG uyumu değil, öneri. İkisini karıştırmak ihlal
    // sayısını şişirir ve raporu okunamaz kılar.
    const sonuc = await window.axe.run(document, {
      runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] },
    });
    return {
      ihlaller: sonuc.violations.map((v) => ({
        kural: v.id,
        etki: v.impact,
        aciklama: v.help,
        dugumSayisi: v.nodes.length,
        ornek: v.nodes[0]?.html?.slice(0, 160) ?? "",
        secici: v.nodes[0]?.target?.join(" ") ?? "",
        // Kontrast ihlallerinde renk çiftini ve oranı da taşıyoruz: "46 düğüm
        // battı" bilgisi düzeltmek için yetmez, HANGİ iki renk battığı gerekir.
        // Bir jeton çifti düzeltilince onlarca düğüm birden geçer.
        dugumler: v.nodes.slice(0, 60).map((n) => {
          const veri = n.any?.[0]?.data ?? {};
          return {
            secici: n.target?.join(" ") ?? "",
            html: n.html?.slice(0, 110) ?? "",
            oran: veri.contrastRatio ?? null,
            onPlan: veri.fgColor ?? null,
            arkaPlan: veri.bgColor ?? null,
            beklenen: veri.expectedContrastRatio ?? null,
            puntoBoyutu: veri.fontSize ?? null,
            kalinlik: veri.fontWeight ?? null,
          };
        }),
      })),
      gecen: sonuc.passes.length,
      incelenemeyen: sonuc.incomplete.length,
    };
  });
}

/**
 * Klavye gezinme ölçümü — axe'ın göremediği iki şey.
 *
 * 1. KLAVYE TUZAĞI. Odak, Tab ile bir bölgeden çıkabiliyor mu? Gezinti ya
 *    başa döner ya odak sayfadan çıkar; ikisi de temiz bitiştir. Bitiş
 *    nedeni raporlanır, çünkü "tuzak yok" iddiası ancak gezinti bittiğinde
 *    yapılabilir.
 * 2. ODAK GÖRÜNÜRLÜĞÜ. Odaklanan öğenin outline ya da box-shadow'u var mı?
 *    Görünmez odak, klavye kullanıcısını sayfada kaybeder.
 *
 * Ziyaret edilen öğe DOM üzerinde İŞARETLENİR. İlk sürüm "etiket + metin"
 * anahtarı kullanıyordu; aynı etiketi taşıyan iki buton (özet panelindeki
 * "Bu cümlenin N kaynağını göster" düğmeleri) yan yana geldiğinde betik
 * döngü sanıp duruyor, ana akış için "1 durak" gibi gerçek olmayan bir sayı
 * üretiyordu.
 */
async function klavyeGezintisi(sayfa, adim = 200) {
  let gorunur = 0;
  let gorunmez = 0;
  let ulasilan = 0;
  let bitisNedeni = "adim-siniri";
  const gorunmezOrnekler = [];

  for (let i = 0; i < adim; i++) {
    await sayfa.keyboard.press("Tab");
    const bilgi = await sayfa.evaluate((sira) => {
      const e = document.activeElement;
      if (!e || e === document.body) return { cikti: true };
      // `next dev` kendi geliştirici araç katmanını sayfaya ekliyor ve o
      // katman sekme sırasına giriyor. Üretim derlemesinde YOK; ürünün
      // erişilebilirliği hakkında hiçbir şey söylemez, bu yüzden sayılmaz.
      if (e.tagName.toLowerCase() === "nextjs-portal") return { atla: true };
      // Öğeyi işaretle: aynı öğeye ikinci kez gelmek GERÇEK döngüdür.
      if (e.dataset.a11ySira !== undefined) return { dongu: true };
      e.dataset.a11ySira = String(sira);
      const s = getComputedStyle(e);
      return {
        halka:
          (s.outlineStyle !== "none" && parseFloat(s.outlineWidth) > 0) ||
          s.boxShadow !== "none",
        html: e.outerHTML.slice(0, 120),
      };
    }, i);

    if (bilgi.atla) continue;
    if (bilgi.cikti) {
      // Odak sayfadan çıkıp tarayıcı arayüzüne geçti. Bu SAĞLIKLI bitiştir.
      bitisNedeni = "sayfadan-cikti";
      break;
    }
    if (bilgi.dongu) {
      // Sekme sırası başa döndü. Bu da sağlıklı bitiştir.
      bitisNedeni = "dongu-kapandi";
      break;
    }
    ulasilan++;
    if (bilgi.halka) gorunur++;
    else {
      gorunmez++;
      if (gorunmezOrnekler.length < 3) gorunmezOrnekler.push(bilgi.html);
    }
  }

  // KLAVYE TUZAĞI NEDİR, NE DEĞİLDİR:
  // Tuzak, odağın bir bölgeden Tab ile ÇIKAMAMASIDIR. Sağlıklı bir sayfada
  // gezinti ya başa döner ya da odak sayfadan çıkar; ikisi de bitiştir.
  //
  // İLK SÜRÜMÜN HATASI: "döngü kapanmadı" durumunu tuzak sayıyordu ve odak
  // tarayıcıya geçtiğinde de döngü kapanmadığı için betik 12 sayfada tuzak
  // bildiriyordu. Tuzağın TERSİ bir davranış tuzak olarak raporlanıyordu.
  //
  // Adım sınırına takılmak ise ne tuzak ne temiz sonuçtur: sayfa taranmamıştır
  // ve öyle raporlanır.
  return {
    ulasilan,
    bitisNedeni,
    tamTarandi: bitisNedeni !== "adim-siniri",
    odakGorunur: gorunur,
    odakGorunmez: gorunmez,
    gorunmezOrnekler,
  };
}

async function main() {
  const tarayici = await chromium.launch();
  const sonuclar = [];

  for (const tema of ["light", "dark"]) {
    for (const s of sayfalar()) {
      const baglam = await tarayici.newContext({
        viewport: { width: 1280, height: 900 },
        colorScheme: tema,
        // Türkçe arayüz: ekran okuyucu dil eşleşmesi için
        locale: "tr-TR",
      });
      const sayfa = await baglam.newPage();

      // TEMA `prefers-color-scheme` İLE DEĞİL, `data-tema` İLE AÇILIYOR.
      // Betiğin ilk sürümü yalnızca `colorScheme` veriyordu; arayüz bunu
      // dinlemediği için iki koşu da KARANLIK temayı ölçüyor, "açık tema
      // denetlendi" diye YANLIŞ bir sonuç üretiyordu (iki koşunun birebir
      // aynı sayıları vermesi bunun işaretiydi). Bayrak sayfa yüklenmeden
      // önce yazılır ki ilk boyamada doğru palet uygulansın.
      await sayfa.addInitScript((t) => {
        if (t === "light") document.documentElement.dataset.tema = "acik";
      }, tema);

      await sayfa.goto(TABAN + s.yol, { waitUntil: "networkidle", timeout: 60_000 });

      // Uygulama temayı localStorage'dan geri yükleyebilir; yüklemeden sonra
      // da doğrulayıp gerekirse düzeltiyoruz.
      await sayfa.evaluate((t) => {
        if (t === "light") document.documentElement.dataset.tema = "acik";
        else delete document.documentElement.dataset.tema;
      }, tema);

      if (s.ozetPaneliniAc) {
        // Atıflı özet backend'den gelir; denetimden önce yerleşmesini bekle.
        await sayfa
          .waitForSelector('button[aria-label^="Bu cümlenin"]', { timeout: 30_000 })
          .catch(() => {});
        // Kaynak listesini aç: kapalıyken DOM'da olmayan öğeler denetlenemez.
        await sayfa.locator('button[aria-label^="Bu cümlenin"]').first().click().catch(() => {});
      }

      // Ölçülen paletin gerçekten değiştiğini KANITLA: gövde arka planı iki
      // temada aynı çıkıyorsa tema uygulanmamıştır ve sonuç geçersizdir.
      const govdeZemini = await sayfa.evaluate(
        () => getComputedStyle(document.body).backgroundColor,
      );

      const axe = await axeCalistir(sayfa);
      const klavye = await klavyeGezintisi(sayfa);
      sonuclar.push({ tema, govdeZemini, sayfa: s.ad, yol: s.yol, ...axe, klavye });
      console.log(
        `${tema.padEnd(5)} ${govdeZemini.padEnd(18)} ${s.ad.padEnd(24)} ihlal=${axe.ihlaller.length} ` +
          `gecen=${axe.gecen} sekme=${klavye.ulasilan} odaksiz=${klavye.odakGorunmez} bitis=${klavye.bitisNedeni}`,
      );
      await baglam.close();
    }
  }

  await tarayici.close();

  // --- Kural bazında topla: aynı ihlal 6 sayfada çıkıyorsa 6 ayrı sorun değil ---
  const kurallar = new Map();
  for (const r of sonuclar) {
    for (const i of r.ihlaller) {
      const mevcut = kurallar.get(i.kural) ?? {
        kural: i.kural,
        etki: i.etki,
        aciklama: i.aciklama,
        toplamDugum: 0,
        sayfalar: new Set(),
        ornek: i.ornek,
        secici: i.secici,
      };
      mevcut.toplamDugum += i.dugumSayisi;
      mevcut.sayfalar.add(`${r.sayfa} (${r.tema})`);
      kurallar.set(i.kural, mevcut);
    }
  }
  const ozet = [...kurallar.values()]
    .map((k) => ({ ...k, sayfalar: [...k.sayfalar] }))
    .sort((a, b) => b.toplamDugum - a.toplamDugum);

  mkdirSync(CIKTI_DIZIN, { recursive: true });
  writeFileSync(
    join(CIKTI_DIZIN, "erisilebilirlik.json"),
    JSON.stringify({ taban: TABAN, sayfalar: sonuclar, kuralOzeti: ozet }, null, 2),
    "utf-8",
  );

  // Markdown, ölçüm sonuçlarından türetilir; elle yazılmaz (spec 2).
  writeFileSync(
    join(CIKTI_DIZIN, "erisilebilirlik.md"),
    markdownUret({
      taban: TABAN,
      axeSurum: require("axe-core/package.json").version,
      sayfaSayisi: sayfalar().length,
      sonuclar,
      kuralOzeti: ozet,
    }),
    "utf-8",
  );

  console.log(`\nrapor -> eval/results/erisilebilirlik.md`);
  console.log(`Benzersiz ihlal kuralı: ${ozet.length}`);
  for (const k of ozet) {
    console.log(`  ${k.etki?.padEnd(8)} ${k.kural.padEnd(28)} ${k.toplamDugum} düğüm — ${k.aciklama}`);
    console.log(`      ${k.secici} :: ${k.ornek}`);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
