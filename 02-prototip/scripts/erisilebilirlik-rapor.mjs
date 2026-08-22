/**
 * Erişilebilirlik denetiminin Markdown çıktısı.
 *
 * Ölçüm mantığından ayrı tutuldu: denetim betiği "ne ölçtük" sorusunu,
 * bu dosya "nasıl anlatıyoruz" sorusunu yanıtlıyor. Rapor metnini ölçüm
 * döngüsünün içine gömmek, ikisini birlikte değiştirmeye zorlar.
 */

/**
 * @param {object} girdi
 * @param {string} girdi.taban        Ölçülen adres
 * @param {string} girdi.axeSurum     axe-core sürümü (raporda belirtilir)
 * @param {number} girdi.sayfaSayisi  Denetlenen benzersiz sayfa sayısı
 * @param {Array}  girdi.sonuclar     Koşu başına sonuç kayıtları
 * @param {Array}  girdi.kuralOzeti   Kural bazında toplanmış ihlaller
 */
export function markdownUret({ taban, axeSurum, sayfaSayisi, sonuclar, kuralOzeti }) {
  const toplamIhlal = sonuclar.reduce((t, r) => t + r.ihlaller.length, 0);
  const toplamOdaksiz = sonuclar.reduce((t, r) => t + r.klavye.odakGorunmez, 0);
  // Tuzak: gezinti ne başa döndü ne de odak sayfadan çıktı — yani sayfa
  // adım sınırına kadar tarandı ve bitmedi. Tam taranan sayfalarda tuzak yok.
  const taranmayan = sonuclar.filter((r) => !r.klavye.tamTarandi).length;

  const satirlar = sonuclar
    .map(
      (r) =>
        `| ${r.sayfa} | ${r.tema === "dark" ? "karanlık" : "açık"} | ${r.ihlaller.length} | ` +
        `${r.gecen} | ${r.klavye.ulasilan} | ${r.klavye.odakGorunmez} | ` +
        `${r.klavye.bitisNedeni} |`,
    )
    .join("\n");

  const ihlalBolumu =
    kuralOzeti.length === 0
      ? "Bu koşuda WCAG A/AA ihlali bulunmadı."
      : "## İhlaller\n\n" +
        kuralOzeti
          .map(
            (k) =>
              `- **${k.kural}** (${k.etki}) — ${k.toplamDugum} düğüm — ${k.aciklama}\n` +
              `  - Örnek seçici: \`${k.secici}\`\n` +
              `  - Sayfalar: ${k.sayfalar.join(", ")}`,
          )
          .join("\n");

  return `# Erişilebilirlik Denetimi

> \`02-prototip/scripts/erisilebilirlik-denetimi.mjs\` tarafından üretilir. Elle düzenlenmez.

**Araç:** axe-core ${axeSurum} (Deque Systems) · **Ölçüt:** WCAG 2.0/2.1 seviye A + AA
**Ölçülen:** ${taban} — \`next build\` + \`next start\` (üretim derlemesi)
**Kapsam:** ${sayfaSayisi} sayfa × 2 tema = ${sonuclar.length} koşu

## Sonuç

| Ölçüm | Değer |
|---|---|
| WCAG A/AA ihlali (düğüm) | **${toplamIhlal}** |
| Benzersiz ihlal kuralı | **${kuralOzeti.length}** |
| Odak halkası görünmeyen sekme durağı | **${toplamOdaksiz}** |
| Gezinti tamamlanmadan sınıra takılan koşu | **${taranmayan}** |

## Sayfa bazında

| Sayfa | Tema | İhlal | Geçen kural | Sekme durağı | Odaksız | Gezinti bitişi |
|---|---|---|---|---|---|---|
${satirlar}

"Geçen kural", axe'ın o sayfada uygulayıp ihlal bulmadığı kural sayısıdır.

**Gezinti bitişi** klavye tuzağı ölçüsüdür. Tuzak, odağın Tab ile bir bölgeden
ÇIKAMAMASIDIR. Sağlıklı bir sayfada gezinti iki şekilde biter ve ikisi de
temiz sonuçtur:

- \`dongu-kapandi\` — sekme sırası başa döndü,
- \`sayfadan-cikti\` — odak tarayıcı arayüzüne geçti.

\`adim-siniri\` ise ne tuzak ne temiz sonuçtur: sayfa 200 adımda bitmemiştir
ve o koşu için tuzak yokluğu İDDİA EDİLEMEZ.

${ihlalBolumu}

## Bu denetimin GÖREMEDİĞİ

Otomatik denetim, WCAG ihlallerinin yalnızca bir bölümünü yakalar. **"0 ihlal"
"erişilebilir" demek değildir.** Aşağıdakiler bu betikle ölçülmez ve raporda
ölçülmüş gibi sunulmaz:

- **Odak sırasının mantıklı olması.** Betik sıranın kapandığını gösterir;
  sıranın görsel düzeni izlediğini göstermez.
- **Ekran okuyucunun okuduğu metnin anlamlı olması.** Etiketin var olması ile
  anlaşılır olması ayrı şeylerdir.
- **Bilişsel yük.** Çekimserlik mesajının ("sistem hüküm vermiyor") kullanıcı
  tarafından "bozuk" değil "dürüst" okunup okunmadığı; bu, kullanılabilirlik
  testinin sorusudur (\`docs/KULLANILABILIRLIK_TESTI.md\`).
- **Hareket duyarlılığı**, %200 yakınlaştırma, dokunmatik hedef boyutu.

## Düzeltme geçmişi — ve ölçüm aracının kendi hatası

İlk koşuda 46 düğümde kontrast ihlali vardı. Dağınık kusurlar değildi: tamamı
üç renk jetonundan geliyordu — \`metin-sonuk\`, ve dolu zemin olarak
kullanıldığında \`mavi\` ile \`mihenk\`. Bir renk, hem koyu zeminde metin hem de
beyaz metin taşıyan dolu zemin rolünü aynı anda AA seviyesinde taşıyamıyor;
palet bu iki rol ayrılarak düzeltildi.

**Asıl bulgu ise ölçümün kendisindeydi.** İlk koşu açık temayı hiç ölçmemişti:
betik temayı \`prefers-color-scheme\` ile açmaya çalışıyordu, oysa arayüz
\`data-tema\` özniteliğini okuyor. İki koşu da karanlık temayı ölçüyor, sonuç
"iki temada da temiz" gibi görünüyordu. Düzeltildiğinde açık temada
**190 düğümlük** ihlal ortaya çıktı: aksan renklerinin (mor, mavi, amber,
yeşil, camgöbeği) tamamı koyu zemin için seçilmişti ve beyaz üzerinde eşiğin
belirgin biçimde altında kalıyordu — tek başına "Özetle" düğmesinin etiketi
130 düğüm üretiyordu. Açık tema için ayrı bir aksan seti tanımlandı.

Bu, projenin ölçüme dair temel iddiasının somut bir örneğidir: **ölçüm aracı
yanlış ölçtüğünde sonuç kusursuz görünür.** Aynı sebeple tespit modeli kendi
test kümesinde 1,000 veriyordu (rapor Tablo 1) ve gerçek metinde 0,768'e
düştü (Tablo 8).
`;
}
