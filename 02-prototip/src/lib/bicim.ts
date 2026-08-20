/** NSosyal'in sayı biçimi: 2B, 5,2B, 27,3B (B = bin) */
export function sayiBicimle(n: number): string {
  if (n < 1000) return String(n);
  const bin = n / 1000;
  if (bin < 10) {
    const yuvarlanmis = Math.round(bin * 10) / 10;
    return `${String(yuvarlanmis).replace(".", ",")}B`;
  }
  return `${Math.round(bin)}B`;
}

/** NSosyal'in göreli zaman biçimi: şimdi, 7dk, 3sa, 2g */
export function goreliZaman(isoZaman: string, referans = new Date()): string {
  const fark = referans.getTime() - new Date(isoZaman).getTime();
  const dk = Math.floor(fark / 60000);
  if (dk < 1) return "şimdi";
  if (dk < 60) return `${dk}dk`;
  const sa = Math.floor(dk / 60);
  if (sa < 24) return `${sa}sa`;
  const gun = Math.floor(sa / 24);
  return `${gun}g`;
}

/** Metindeki #etiket ve @bahsetme parçalarını ayırır */
export function metniParcala(metin: string) {
  return metin.split(/(\s+)/).map((parca, i) => {
    if (parca.startsWith("#") && parca.length > 1) {
      return { tur: "etiket" as const, deger: parca, anahtar: i };
    }
    if (parca.startsWith("@") && parca.length > 1) {
      return { tur: "bahsetme" as const, deger: parca, anahtar: i };
    }
    return { tur: "metin" as const, deger: parca, anahtar: i };
  });
}
