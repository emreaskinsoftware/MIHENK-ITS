# Etik Çerçeve

> Şartnamenin beklediği "veri, model, etik ve performans dokümanı"nın **etik**
> ayağıdır. Veri ve KVKK tarafı `docs/VERI_YONETISIMI.md`, başarım tarafı
> `eval/results/` ve rapor 3.2'dedir; burada tekrar edilmez.
>
> **Bu belgedeki her ilkenin karşılığı çalışan kod ve geçen testtir.** Etik
> bölümü, ürünün yapamadıklarını yazmadığı sürece bir niyet beyanıdır. Bu
> yüzden her başlıkta "bunu nasıl ihlal edebiliriz" sorusu da yanıtlanır.

---

## 1. Etik sorunun kaynağı: bu sistem ne yapıyor

MİHENK bir okuma katmanıdır. Üç şey yapar ve üçü de etik olarak yüklüdür:

| İşlev | Etik yük |
|---|---|
| **Özetler** | Neyi özete alıp neyi dışarıda bıraktığı, kullanıcının gördüğü gerçekliği şekillendirir. |
| **Yapay üretim sinyali verir** | Bir insanı "bot" ya da "yapay" diye işaretlemek itibar zararıdır ve geri alınamaz. |
| **İddia doğrular** | "Yanlış" hükmü vermek, bir görüşü kamusal tartışmadan dışlamak anlamına gelebilir. |

Üçünün ortak riski aynıdır: **sistem yanılırsa zarar kullanıcıya değil, hakkında
konuşulan kişiye gelir.** Bu asimetri, aşağıdaki bütün kararların dayanağıdır.

---

## 2. Temel duruş: hüküm veren değil, gösteren sistem

**Kullanıcı nihai karar vericidir.** Sistem hiçbir yerde "bu doğrudur",
"bu yalandır", "bu kişi bot" demez. Ne yapar:

- Kaynağı **gösterir** (İlke 1 — her cümle atıflıdır),
- Farklı bakış açılarını **yan yana koyar** (İlke 3 — çoğulculuk),
- Emin olmadığında **susar** (İlke 2 — çekimserlik).

Bu üçü ürünün pazarlama sloganı değil, kodda zorlanan kurallardır:

| İlke | Nerede zorlanıyor | Ne olur ihlal edilirse |
|---|---|---|
| Atıf | `backend/app/summarize/citation.py` | Kaynaksız cümle **silinir**, kullanıcıya hiç ulaşmaz |
| Çekimserlik | `backend/app/detection/decision.py` | Eşiği geçmeyen metne rozet **gösterilmez** |
| Çoğulculuk | `backend/app/summarize/service.py` | Tek yazarlı küme için özet **üretilmez** |

Atıf denetimi arayüzde değil serviste yapılır. Sebebi mimari değil etik:
arayüz katmanı değiştirilebilir, atlanabilir, başka bir istemci yazılabilir.
Garanti, en dıştaki katmanda duramaz.

---

## 3. Yapay üretim tespiti — en tehlikeli işlev

### 3.1 Ölçülen gerçek

Sentetik test kümemizde tespit modeli 1,000 AUROC veriyor. **Gerçek insan
metninde 0,768.** Üslup bazında bakıldığında tablo daha da ciddi:

| Üslup | BERTurk yakalama oranı |
|---|---|
| Düz asistan dili | 0,061 |
| Samimi | 0,037 |
| Pazarlama | 0,000 |
| **Yazım hatalı** | **0,000** |

(Ayrıntı: rapor Tablo 8, kaynak `eval/results/real_text.md`.)

**Yazım hatası eklemek tespitten kaçmak için yeterlidir.** Bu, modelin
kusuru değil, işin doğasıdır ve gizlenmesi etik dışı olurdu.

### 3.2 Bu ölçümün doğurduğu üç karar

**a) Tespit bir *sinyal*dir, *hüküm* değildir.** Arayüzde gösterilen şey
"bu metin yapay üretim olabilir" uyarısıdır; hesap kapatma, görünürlük
düşürme veya sıralama değiştirme gibi hiçbir yaptırıma bağlı değildir.
MİHENK akış sırasına dokunmaz.

**b) "İnsan yazmış" rozeti HİÇ gösterilmez.** Bu, bilinçli bir eksikliktir
(`02-prototip/src/components/akis/YzSinyali.tsx`, `INSAN_ROZETI_GOSTER = false`).
Üç gerekçe:

1. Akıştaki gönderilerin %86'sı bu rozeti alırdı — bilgi taşımayan bir gürültü.
2. 0,768 AUROC bir metnin yapay *olabileceğine* işaret etmeye yeter, bir metnin
   insan elinden çıktığını **belgelemeye yetmez**.
3. Zararlar simetrik değildir. "Yapay olabilir" uyarısı yanlışsa kullanıcı
   kaynağa bakar; "insan yazmış" damgası yanlışsa kullanıcı **yanlış bir
   güvenle** okur. İkincisi daha tehlikelidir.

**c) Sessizliğin bedeli kabul edilmiştir.** Gerçek metinde hedef kesinliği
(≥0,95) tutturmak için sistem gönderilerin **%98'inde susmak** zorunda kalıyor.
Bu, ürünü daha az etkileyici gösteriyor ve öyle raporlanıyor. Alternatif —
eşiği düşürüp daha çok etiket göstermek — masum kullanıcıları damgalamak
demekti.

### 3.3 İtiraz hakkı

Otomatik bir karar, itiraz edilemiyorsa keyfîdir. `POST /api/itiraz`
(`backend/app/main.py`) sinyale itiraz kaydı açar. Prototipte kayıt TTL'li
önbelleğe yazılır; **gerçek sistemde insan incelemesine gitmelidir** ve
bu, ürünleşme için pazarlık konusu olmayan bir gereksinimdir.

**Dürüstlük notu:** Prototipte itirazı inceleyen bir insan yoktur. İtiraz
akışı arayüz ve kayıt düzeyinde vardır, karar düzeyinde yoktur.

---

## 4. Doğrulama — "doğrulanamadı" ile "yanlış" aynı şey değildir

Doğrulama ucu üç sonuçtan birini verir: `DOGRULANDI`, `YANLIS`,
`DOGRULANAMADI`. Üçüncüsü en çok yanlış anlaşılan ve en çok korunması gereken
sonuçtur.

**`DOGRULANAMADI`, iddianın yanlış olduğu anlamına GELMEZ.** Yeterli kaynak
bulunamamıştır; o kadar. Bu ayrım üç yerde birden zorlanır:

- İstem, kaynak bulunamadığında tahmin yürütmeyi **yasaklar** ve ayrımı
  açıklamada yazmayı **zorunlu** kılar (`02-prototip/src/app/api/dogrula/route.ts`).
- Arayüz üç sonucu üç ayrı görsel dille gösterir; "doğrulanamadı" kırmızı
  değildir.
- Kaynak gösterilemeyen hiçbir sayı veya isim üretilmez.

Bu ayrım neden bu kadar önemli: "doğrulanamadı"yı "yanlış" gibi sunan bir
sistem, henüz haberleşmemiş doğru bir iddiayı susturur. Yanlış bilgiyle
mücadele adına yapılan sansür, mücadele edilen şeyden daha kalıcı zarar verir.

### Bilinen sınır

Demo koşusunda dış model anahtarı tanımlı olmadığında doğrulama sonucu bir
doğrulama koşusundan değil, **simülasyon veri kümesinin bilinen etiketinden**
gelir. Bu, ekranda kullanıcıya **açıkça yazılır**. Erken bir sürümde bu yol
`guven: 92` gibi hiçbir yerde ölçülmemiş bir güven yüzdesi gösteriyordu;
kaldırıldı. Aynı şekilde görsel denetim ucu uydurma adli bulgular
("doku geçişlerinde üretici model izleri") üretiyordu; o da kaldırıldı ve
yerine hiçbir şey konmadı.

**Uydurma bir kanıt, kanıt yokluğundan kötüdür.**

---

## 5. Özet tarafsızlığı

Bir özetleyici, hangi cümleyi alacağını seçerek taraf tutabilir. Üç önlem:

**a) Çoğulculuk zorunluluğu (İlke 3).** Tek yazarlı küme için özet
üretilmez. Tek kaynaktan beslenen bir olay "gündem" değildir; onu gündem gibi
sunmak, tek kişinin iddiasını topluma mal etmektir.

**b) Etkileşime göre değil, çerçeveye göre seçim.** Yerel çıkarımsal
özetleyici her *çerçeveden* (nötr, destekleyici, eleştirel, soru soran,
doğrulanmamış) en temsili gönderiyi alır — en çok beğeni alandan değil.
En çok etkileşim alan görüş "doğru" değildir.

**c) Doğruluk hükmü yasağı.** Birleştirme istemi, modelden taraf
pozisyonlarını belirtmesini ister ve hangi tarafın haklı olduğunu söylemeyi
**yasaklar** (`backend/app/llm/prompts.py`).

### Ölçülmeyen taraf

Özetin tarafsızlığı **sayısal olarak ölçülmemiştir.** Kaynağa sadakat
(0,937) ve atıf doğruluğu (1,000) ölçüldü; "özet, olayı dengeli anlatıyor
mu" sorusu insan değerlendirmesi gerektirir ve bu prototipte yapılmadı.
Arayüzdeki denge çubuğu bir **girdi** ölçüsüdür (kaç çerçeveden kaç gönderi
var), özetin kendisinin dengesini ölçmez.

---

## 6. Model halüsinasyonu

Üretici model uydurabilir. Bu bir olasılık değil, beklenen davranıştır.
Savunma modele güvenmek değil, **çıktıyı denetlemektir**:

| Halüsinasyon türü | Denetim | Sonuç |
|---|---|---|
| Kaynaksız cümle | `citation.py` | Cümle silinir, sayacı artar |
| Uydurma gönderi kimliği | `citation.py` — izin listesi | Kimlik atılır; hepsi uydurmaysa cümle silinir |
| Bozuk JSON | `parse_llm_json` | Özet boş döner; uydurma yapı **üretilmez** |
| Kelime sınırını aşma | `service.py` | Cümle kırpılmaz, **tamamen çıkarılır** |

Silinen cümlenin yerine "kaynak bulunamadı" notu bile eklenmez — o not da
atıfsız bir iddia olurdu.

Bu sayaçlar gizlenmez: `dropped_sentence_count` ve
`single_source_cluster_count` API yanıtında döner ve **arayüzde gösterilir**.
Sistemin ne kadar sildiği kullanıcıdan saklanan bir hata değil, raporlanan
bir ölçüdür.

---

## 7. Kötüye kullanım ve istem enjeksiyonu

Gönderi metnini üçüncü kişiler yazar; güvenilmeyen girdidir. Saldırgan,
gönderisine "önceki talimatları yoksay" yazarak özetleyiciyi yönlendirmeye
çalışabilir. Savunma dört katmanlıdır (yapısal ayrım, girdi temizleme, çıktı
kısıtı, yetki kısıtı) ve 40 senaryoda 40/40 ölçülmüştür
(`eval/results/injection.md`).

**Şüpheli gönderi akıştan ÇIKARILMAZ.** Yalnızca işaretlenir ve özetlenir,
ama talimatına uyulmaz. Sebebi etik: şüpheli bir gönderiyi tamamen kaldırmak
sansür etkisi yaratır ve yanlış pozitifin bedelini masum kullanıcı öder.

### Sınır

%100 savunma **bizim yazdığımız 40 senaryo** üzerindedir. Gerçek saldırganların
deneyeceği türlerin tamamını kapsadığı iddia edilemez. O sayı "bilinen saldırı
türlerine dayanıklıyız" demektir, "saldırılamaz" demek değildir.

---

## 8. Şeffaflık — sistemin kendi hakkında söyledikleri

Kullanıcıya gösterilen her sonuç, **nereden geldiğini** söyler:

- Özet yerel çıkarımsal yedekle üretildiyse bu yazılır (`provider` alanı).
- Sonuç veri kümesinin bilinen etiketinden geliyorsa bu yazılır.
- Backend'e erişilemediği için yerel bir metin gösteriliyorsa, o metnin
  **atıf içermediği** yazılır.
- Sistem çekimser kaldıysa gerekçesi gösterilir; sessizlik "hata" gibi
  sunulmaz.

Bu, ürünün en kolay ihlal edilebilecek ilkesidir: her disclosure satırı
arayüzü daha az cilalı gösterir. Kaldırılması bir satırlık iştir, ve
kaldırıldığında hiçbir test kırılmaz — bunu bilerek yazıyoruz.

---

## 9. Yapılmayanlar

Bu bölüm, belgenin geri kalanının güvenilir olması için vardır.

| Konu | Durum |
|---|---|
| İtirazı inceleyen insan süreci | **Yok** — kayıt var, karar yok |
| Özet tarafsızlığının sayısal ölçümü | **Yok** — insan değerlendirmesi gerekir |
| Görsel yapay üretim sınıflandırıcısı | **Yok** — yalnızca köken denetimi var |
| Farklı demografik gruplarda tespit yanlılığı ölçümü | **Yok** — veri kümesi buna elvermiyor |
| Kullanılabilirlik testi (çekimserliğin nasıl okunduğu) | **Yapılmadı** — protokol hazır |
| Gerçek NSosyal akışında ölçüm | **Yok** — kazıma yasak, mentörlük sürecine bırakıldı |

Özellikle dördüncü satır önemlidir: **tespit modelinin belirli yazım
biçimlerine, lehçelere veya dil düzeylerine karşı yanlı olup olmadığını
ölçmedik.** Yazım hatalı metinlerde yakalama oranının 0,000 olması, modelin
"düzgün yazılmış metni yapay sayma" eğiliminde olabileceğine dair bir işarettir
ve bu, resmî dil kullanan kurumsal hesapları haksız yere etkileyebilir.
Ürünleşme öncesinde ölçülmesi gereken ilk şey budur.

---

## 10. Bu belgenin sınırı

Etik bir çerçeve, ihlal edildiğinde bir şeyin kırılmasıyla anlam kazanır.
Yukarıdaki maddelerin bir bölümü testle korunuyor (atıf denetimi, çekimserlik,
enjeksiyon savunması, saklama sınırı); bir bölümü ise yalnızca **yazılı bir
karar** (disclosure satırları, "insan rozeti gösterme" bayrağı). İkinci grup,
kod incelemesi olmadan sessizce kaybolabilir.

Bunu bir eksiklik olarak yazıyoruz, çünkü fark edilmeden kaybolması bu
belgenin tamamını hükümsüz kılardı.
