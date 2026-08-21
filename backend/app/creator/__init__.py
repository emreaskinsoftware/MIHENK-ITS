"""İçerik üreticisi modülü — P2 (spec 6.8).

DURUM: Tasarım sözleşmesi. Uygulama 7-12 Eylül (İP-9) aralığında yazılacak.
Bu dosya, raporda gelir modelinin ikinci kalemi olarak duran iddianın kod
tarafındaki karşılığıdır: modülün NE YAPACAĞI ve — daha önemlisi — NE
YAPMAYACAĞI burada nettir.

--- TEMEL YAKLAŞIM --------------------------------------------------------

"POPÜLER İÇERİKLERİ GÖSTER" DEĞİL, "İÇERİK BOŞLUĞU ANALİZİ".

Popüler olanı göstermek kopyacılığı teşvik eder: herkes aynı konuya koşar,
akış tekilleşir, üretici de kalabalığın arasında kaybolur. Ayrıca bu, ölçmesi
kolay ama değeri düşük bir öneridir — jüri "bunu zaten trend listesi yapıyor"
diye sorar ve haklı olur.

Boşluk analizi ters soruyu sorar: hangi konuda TALEP var ama ARZ yok?

    talep_sinyali(konu)  = o konuda sorulan sorular
                         + arama hacmi
                         + yanıtsız kalmış gönderiler
    arz_sinyali(konu)    = o konuda üretilmiş mevcut içerik hacmi
    bosluk_skoru(konu)   = normalize(talep) - normalize(arz)

    öneri = kitlesinin ilgi vektörüne YAKIN  VE  bosluk_skoru YÜKSEK konular

İki koşul birlikte gerekir: yalnızca boşluk skoruna bakmak, üreticinin hiç
bilmediği bir alanı önermek olur.

--- ÇIKTI SÖZLEŞMESİ ------------------------------------------------------

    { konu, bosluk_skoru, gerekce, onerilen_format, onerilen_zaman }

`gerekce` ZORUNLUDUR. Kullanıcı, önerinin neden geldiğini görmeden ona
güvenemez; açıklanamayan öneri, üreticinin kendi yargısını bir kara kutuya
devretmesi demektir. Bu modülde açıklanabilirlik bir özellik değil, giriş
şartıdır.

`onerilen_zaman`, üreticinin kitlesinin geçmiş etkileşim saat dağılımından
çıkarılır — genel bir "en iyi paylaşım saati" tablosundan değil.

--- YÖNETİŞİM SINIRI ------------------------------------------------------

Bu modül kitle davranışı üzerinde çalışır, yani en fazla kişisel veri temas
eden bileşendir. Bu yüzden:
  - Tüm toplulaştırmalar `governance/aggregation.py` üzerinden geçer;
    `k` eşiğinin altındaki gruplar hiç döndürülmez. Üreticiye "kitlenizin
    3 kişisi şunu sordu" denmez.
  - Bireysel kullanıcı davranışı üreticiye HİÇBİR biçimde gösterilmez.

--- ÖLÇÜM -----------------------------------------------------------------

    nDCG@10   : sıralama kalitesi
    kapsam    : önerilerin konu uzayının ne kadarını gördüğü
    çeşitlilik: öneriler birbirine benzemesin (aynı konunun varyasyonları
                değil, farklı boşluklar önerilmeli)

Çeşitlilik metriği bilinçli olarak eklendi: boşluk skoruna göre sıralayan naif
bir sistem, birbirine çok benzeyen on öneri üretme eğilimindedir.
"""

__all__: list[str] = []
