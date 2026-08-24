# Erişilebilirlik Denetimi

> `02-prototip/scripts/erisilebilirlik-denetimi.mjs` tarafından üretilir. Elle düzenlenmez.

**Araç:** axe-core 4.13.0 (Deque Systems) · **Ölçüt:** WCAG 2.0/2.1 seviye A + AA
**Ölçülen:** http://localhost:3000 — `next build` + `next start` (üretim derlemesi)
**Kapsam:** 6 sayfa × 2 tema = 12 koşu

## Sonuç

| Ölçüm | Değer |
|---|---|
| WCAG A/AA ihlali (düğüm) | **0** |
| Benzersiz ihlal kuralı | **0** |
| Odak halkası görünmeyen sekme durağı | **0** |
| Gezinti tamamlanmadan sınıra takılan koşu | **4** |

## Sayfa bazında

| Sayfa | Tema | İhlal | Geçen kural | Sekme durağı | Odaksız | Gezinti bitişi |
|---|---|---|---|---|---|---|
| Ana akış + özet paneli | açık | 0 | 29 | 200 | 0 | adim-siniri |
| Gönderi ayrıntısı | açık | 0 | 27 | 109 | 0 | sayfadan-cikti |
| Keşfet | açık | 0 | 28 | 200 | 0 | adim-siniri |
| Ayarlar | açık | 0 | 26 | 37 | 0 | sayfadan-cikti |
| İçerik üretici | açık | 0 | 27 | 25 | 0 | sayfadan-cikti |
| TEKNOFEST kayıt | açık | 0 | 26 | 25 | 0 | sayfadan-cikti |
| Ana akış + özet paneli | karanlık | 0 | 29 | 200 | 0 | adim-siniri |
| Gönderi ayrıntısı | karanlık | 0 | 27 | 109 | 0 | sayfadan-cikti |
| Keşfet | karanlık | 0 | 28 | 200 | 0 | adim-siniri |
| Ayarlar | karanlık | 0 | 26 | 37 | 0 | sayfadan-cikti |
| İçerik üretici | karanlık | 0 | 27 | 25 | 0 | sayfadan-cikti |
| TEKNOFEST kayıt | karanlık | 0 | 26 | 25 | 0 | sayfadan-cikti |

"Geçen kural", axe'ın o sayfada uygulayıp ihlal bulmadığı kural sayısıdır.

**Gezinti bitişi** klavye tuzağı ölçüsüdür. Tuzak, odağın Tab ile bir bölgeden
ÇIKAMAMASIDIR. Sağlıklı bir sayfada gezinti iki şekilde biter ve ikisi de
temiz sonuçtur:

- `dongu-kapandi` — sekme sırası başa döndü,
- `sayfadan-cikti` — odak tarayıcı arayüzüne geçti.

`adim-siniri` ise ne tuzak ne temiz sonuçtur: sayfa 200 adımda bitmemiştir
ve o koşu için tuzak yokluğu İDDİA EDİLEMEZ.

Bu koşuda WCAG A/AA ihlali bulunmadı.

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
  testinin sorusudur (`docs/KULLANILABILIRLIK_TESTI.md`).
- **Hareket duyarlılığı**, %200 yakınlaştırma, dokunmatik hedef boyutu.

## Düzeltme geçmişi — ve ölçüm aracının kendi hatası

İlk koşuda 46 düğümde kontrast ihlali vardı. Dağınık kusurlar değildi: tamamı
üç renk jetonundan geliyordu — `metin-sonuk`, ve dolu zemin olarak
kullanıldığında `mavi` ile `mihenk`. Bir renk, hem koyu zeminde metin hem de
beyaz metin taşıyan dolu zemin rolünü aynı anda AA seviyesinde taşıyamıyor;
palet bu iki rol ayrılarak düzeltildi.

**Asıl bulgu ise ölçümün kendisindeydi.** İlk koşu açık temayı hiç ölçmemişti:
betik temayı `prefers-color-scheme` ile açmaya çalışıyordu, oysa arayüz
`data-tema` özniteliğini okuyor. İki koşu da karanlık temayı ölçüyor, sonuç
"iki temada da temiz" gibi görünüyordu. Düzeltildiğinde açık temada
**190 düğümlük** ihlal ortaya çıktı: aksan renklerinin (mor, mavi, amber,
yeşil, camgöbeği) tamamı koyu zemin için seçilmişti ve beyaz üzerinde eşiğin
belirgin biçimde altında kalıyordu — tek başına "Özetle" düğmesinin etiketi
130 düğüm üretiyordu. Açık tema için ayrı bir aksan seti tanımlandı.

Bu, projenin ölçüme dair temel iddiasının somut bir örneğidir: **ölçüm aracı
yanlış ölçtüğünde sonuç kusursuz görünür.** Aynı sebeple tespit modeli kendi
test kümesinde 1,000 veriyordu (rapor Tablo 1) ve gerçek metinde 0,768'e
düştü (Tablo 8).
