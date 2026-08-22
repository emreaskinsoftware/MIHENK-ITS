/**
 * Kullanılabilirlik testi — sonuç hesaplayıcı.
 *
 * `docs/kullanilabilirlik/veri-girisi.json` dosyasındaki ham kayıtları okur,
 * SUS puanını ve kavrama ortalamalarını hesaplar, sonucu
 * `docs/KULLANILABILIRLIK_TESTI.md` §6 bölümüne YAZAR.
 *
 * NEDEN BETİK:
 *   1. SUS formülü (tek maddeler `puan−1`, çift maddeler `5−puan`, toplam
 *      ×2,5) elle yapıldığında en sık hata kaynağıdır ve yanlış bir SUS
 *      puanı raporda düzeltilemez.
 *   2. EKSİK VERİ GİZLENMEZ. Doldurulmamış her alan `[  ]` olarak yazılır ve
 *      ortalamaya katılmaz. Üç kişiyle yapılmış bir testi beş kişiymiş gibi
 *      sunmak, bu raporun bütün ölçüm iddiasını götürürdü (spec 2).
 *
 * Çalıştırma:
 *     node scripts/kullanilabilirlik-hesapla.mjs
 */

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const BURASI = dirname(fileURLToPath(import.meta.url));
const DEPO = join(BURASI, "..", "..");
const GIRDI = join(DEPO, "docs", "kullanilabilirlik", "veri-girisi.json");
const PROTOKOL = join(DEPO, "docs", "KULLANILABILIRLIK_TESTI.md");

const BOS = "[  ]";

/** Sayı ise biçimlendirir, değilse boş hücre işareti döner. */
const h = (deger, basamak = 0) =>
  typeof deger === "number" && Number.isFinite(deger) ? deger.toFixed(basamak) : BOS;

/** null/undefined olmayan sayıların ortalaması; hiç yoksa null. */
function ortalama(degerler) {
  const gecerli = degerler.filter((d) => typeof d === "number" && Number.isFinite(d));
  return gecerli.length ? gecerli.reduce((t, d) => t + d, 0) / gecerli.length : null;
}

/**
 * SUS puanı (0-100).
 *
 * Tek numaralı maddeler olumlu, çift numaralı maddeler olumsuz ifadelerdir;
 * bu yüzden çiftler ters çevrilir. On maddenin HEPSİ dolu değilse puan
 * hesaplanmaz — eksik maddeyi ortalamayla doldurmak, verilmemiş bir cevabı
 * uydurmak olurdu.
 */
function susPuani(maddeler) {
  if (!Array.isArray(maddeler) || maddeler.length !== 10) return null;
  if (maddeler.some((m) => typeof m !== "number")) return null;
  let toplam = 0;
  maddeler.forEach((puan, i) => {
    const tekNumarali = i % 2 === 0; // dizi 0-tabanlı: index 0 = madde 1
    toplam += tekNumarali ? puan - 1 : 5 - puan;
  });
  return toplam * 2.5;
}

/** Dört kavrama sorusunun ortalaması (0-1). Eksik soru varsa null. */
function kavramaPuani(sorular) {
  if (!Array.isArray(sorular) || sorular.length !== 4) return null;
  if (sorular.some((s) => typeof s !== "number")) return null;
  return sorular.reduce((t, s) => t + s, 0) / 4;
}

const veri = JSON.parse(readFileSync(GIRDI, "utf-8"));
const katilimcilar = veri.katilimcilar ?? [];

// --- Sıra dengeleme denetimi ------------------------------------------------
// Hepsi aynı sırayla yapıldıysa ikinci koşul birinciden öğrenilenle kolaylaşır
// ve zaman kazancı OLDUĞUNDAN BÜYÜK ölçülür. Bu, sonucu geçersiz kılan bir
// tasarım hatasıdır; sessizce geçilmez.
const elleOnce = katilimcilar.filter((k) => k.once === "elle").length;
const ozetOnce = katilimcilar.filter((k) => k.once === "ozet").length;
const dengeUyarisi =
  Math.abs(elleOnce - ozetOnce) > 1
    ? `**Sıra dengelemesi bozuk** (${elleOnce} katılımcı elle-önce, ${ozetOnce} özet-önce). ` +
      "Zaman kazancı olduğundan büyük ölçülmüş olabilir; sonuç bu uyarıyla okunmalıdır."
    : null;

// --- Katılımcı satırları ----------------------------------------------------
const satirlar = katilimcilar.map((k) => {
  const elleSure = k.elle?.sure_sn ?? null;
  const ozetSure = k.ozet?.sure_sn ?? null;
  const kazanc =
    typeof elleSure === "number" && typeof ozetSure === "number" && elleSure > 0
      ? ((elleSure - ozetSure) / elleSure) * 100
      : null;
  return {
    kod: k.kod,
    elleSure,
    ozetSure,
    kazanc,
    kavramaElle: kavramaPuani(k.elle?.kavrama),
    kavramaOzet: kavramaPuani(k.ozet?.kavrama),
    sus: susPuani(k.sus),
    tiklama: k.ozet?.kaynak_tiklama ?? null,
    gorevC: k.gorev_c ?? {},
    gorevD: k.gorev_d?.okuma ?? null,
  };
});

const tamamlanan = satirlar.filter((s) => s.sus !== null || s.elleSure !== null).length;

// --- Tablo 7 ----------------------------------------------------------------
const tablo7 = satirlar
  .map(
    (s) =>
      `| ${s.kod} | ${h(s.elleSure)} | ${h(s.ozetSure)} | ${
        s.kazanc === null ? BOS : `%${s.kazanc.toFixed(0)}`
      } | ${h(s.kavramaElle, 2)} | ${h(s.kavramaOzet, 2)} | ${h(s.sus, 1)} |`,
  )
  .join("\n");

const ortSatir =
  `| **Ortalama** | **${h(ortalama(satirlar.map((s) => s.elleSure)))}** ` +
  `| **${h(ortalama(satirlar.map((s) => s.ozetSure)))}** ` +
  `| **${(() => {
    const o = ortalama(satirlar.map((s) => s.kazanc));
    return o === null ? BOS : `%${o.toFixed(0)}`;
  })()}** ` +
  `| **${h(ortalama(satirlar.map((s) => s.kavramaElle)), 2)}** ` +
  `| **${h(ortalama(satirlar.map((s) => s.kavramaOzet)), 2)}** ` +
  `| **${h(ortalama(satirlar.map((s) => s.sus)), 1)}** |`;

// --- Ek maddeler ------------------------------------------------------------
const ekSatirlar = [
  ["E1 — Özetteki bilgilerin nereden geldiğini anlayabildim", "E1"],
  ["E2 — Sistemin bazı durumlarda bilgi göstermemesi bana güven verdi", "E2"],
  ["E3 — Kaynak çiplerine tıklamak kolaydı ve işe yaradı", "E3"],
]
  .map(([etiket, anahtar]) => {
    const o = ortalama(katilimcilar.map((k) => k.ek?.[anahtar] ?? null));
    return `| ${etiket} | ${h(o, 2)} |`;
  })
  .join("\n");

// --- Görev C ve D -----------------------------------------------------------
const cBasarili = satirlar.filter((s) => s.gorevC.basari === true).length;
const cDenendi = satirlar.filter((s) => typeof s.gorevC.basari === "boolean").length;
const cSure = ortalama(satirlar.map((s) => s.gorevC.sure_sn ?? null));

const dOkumalari = { durust: 0, yanlis_guven: 0, bozuk: 0, belirsiz: 0 };
for (const s of satirlar) if (s.gorevD in dOkumalari) dOkumalari[s.gorevD]++;
const dToplam = Object.values(dOkumalari).reduce((t, n) => t + n, 0);

// Ürünün en kritik bulgusu: sessizliği "temiz" diye okumak, tam olarak
// kaçınmak için "insan yazmış" rozetini kaldırdığımız yanlış güvendir.
const dUyari =
  dOkumalari.yanlis_guven > 0
    ? `\n> **Tasarım bulgusu:** ${dOkumalari.yanlis_guven} katılımcı, sistemin ` +
      "sessizliğini \"bu gönderi temiz\" diye okudu. Bu, `docs/ETIK.md` §3.2'de " +
      "\"insan yazmış\" rozetini kaldırma gerekçesi olarak yazılan **yanlış güvenin** " +
      "kendisidir ve rozetin kaldırılmış olması bunu tek başına önlemiyor. " +
      "Çekimserliğin görünür biçimde anlatılması gerekiyor.\n"
    : "";

const nitel = (veri.nitel_bulgular ?? []).length
  ? veri.nitel_bulgular.map((n) => `- ${n}`).join("\n")
  : `${BOS} — test yapıldığında doldurulur.`;

const duzeltmeler = (veri.yapilacak_duzeltmeler ?? []).length
  ? veri.yapilacak_duzeltmeler.map((d) => `- ${d}`).join("\n")
  : `${BOS} — test yapıldığında doldurulur.`;

// --- §6 bölümünü kur --------------------------------------------------------
const bolum = `## 6. Sonuçlar

> Bu bölüm \`02-prototip/scripts/kullanilabilirlik-hesapla.mjs\` tarafından
> \`docs/kullanilabilirlik/veri-girisi.json\` üzerinden üretilir. Elle
> düzenlenmez. Doldurulmamış her hücre \`${BOS}\` kalır ve ortalamaya katılmaz.

**Tamamlanan katılımcı: ${tamamlanan}/${katilimcilar.length}**${
  tamamlanan < katilimcilar.length
    ? " — eksik katılımcı var; aşağıdaki ortalamalar yalnızca tamamlananlar üzerindendir."
    : ""
}
${dengeUyarisi ? `\n> ⚠️ ${dengeUyarisi}\n` : ""}
### Tablo 7 — Görev süresi ve kavrama

| Katılımcı | Elle okuma (sn) | Özetle okuma (sn) | Kazanç | Kavrama (elle) | Kavrama (özet) | SUS |
|---|---|---|---|---|---|---|
${tablo7}
${ortSatir}

**Kavrama sütunları birlikte okunmalıdır.** Hız, doğruluk pahasına gelmemeli:
özetle okuyan kullanıcının kavrama puanı elle okuyandan belirgin düşükse
zaman kazancı bir başarı değil, bilgi kaybıdır.

### Ek maddeler

| Madde | Ortalama (1-5) |
|---|---|
${ekSatirlar}

E2, ürünün en ayırt edici davranışına (İlke 2 — çekimserlik) dair tek doğrudan
ölçüdür.

### Görev C — Kaynak doğrulama

| Ölçüm | Değer |
|---|---|
| Başarı | ${cDenendi ? `${cBasarili}/${cDenendi}` : BOS} |
| Ortalama süre (sn) | ${h(cSure)} |
| Görev B'de kaynak rozetine tıklama (ortalama) | ${h(ortalama(satirlar.map((s) => s.tiklama)), 1)} |

Son satır, atıfın **kullanılıp kullanılmadığını** gösterir. Sıfıra yakınsa
atıf bir güven aracı değil görsel gürültüdür ve rapor bunu yazmalıdır.

### Görev D — Çekimserlik nasıl okundu

| Katılımcının okuması | Kişi |
|---|---|
| "Sistem emin değil / karar vermiyor" | ${dToplam ? dOkumalari.durust : BOS} |
| "Bu gönderi temiz / insan yazmış" ⚠️ | ${dToplam ? dOkumalari.yanlis_guven : BOS} |
| "Sistem bozuk / eksik" ⚠️ | ${dToplam ? dOkumalari.bozuk : BOS} |
| Anlamadı | ${dToplam ? dOkumalari.belirsiz : BOS} |
${dUyari}
### Nitel bulgular

${nitel}

### Yapılacak düzeltmeler

${duzeltmeler}
`;

// --- Protokol dosyasının §6 bölümünü değiştir -------------------------------
const protokol = readFileSync(PROTOKOL, "utf-8");
const bas = protokol.indexOf("## 6. Sonuçlar");
const son = protokol.indexOf("## 7.", bas);
if (bas === -1 || son === -1) {
  console.error("HATA: protokol dosyasında '## 6. Sonuçlar' ile '## 7.' arası bulunamadı.");
  process.exit(1);
}
writeFileSync(PROTOKOL, protokol.slice(0, bas) + bolum + "\n" + protokol.slice(son), "utf-8");

console.log(`Tamamlanan katılımcı : ${tamamlanan}/${katilimcilar.length}`);
console.log(`SUS ortalaması       : ${h(ortalama(satirlar.map((s) => s.sus)), 1)}`);
console.log(`Zaman kazancı        : ${(() => {
  const o = ortalama(satirlar.map((s) => s.kazanc));
  return o === null ? BOS : `%${o.toFixed(0)}`;
})()}`);
console.log(`Kavrama elle / özet  : ${h(ortalama(satirlar.map((s) => s.kavramaElle)), 2)} / ${h(
  ortalama(satirlar.map((s) => s.kavramaOzet)),
  2,
)}`);
if (dengeUyarisi) console.log(`\nUYARI: ${dengeUyarisi}`);
console.log(`\nyazıldı -> docs/KULLANILABILIRLIK_TESTI.md §6`);
