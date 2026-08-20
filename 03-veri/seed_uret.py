# -*- coding: utf-8 -*-
"""
MİHENK — NSosyal simülasyonu için sentetik platform verisi üreticisi.

Üretilen veri KURGUSALDIR. Gerçek kişi, kurum, marka veya haber kuruluşu
temsil etmez; gerçek olaylara atıfta bulunmaz.

Tasarım notu: Gönderiler rastgele değil, OLAY KÜMELERİ etrafında üretilir.
Her olayın çevresinde farklı çerçevelerden (destekleyici / eleştirel / nötr /
soru soran / yanlış bilgi) gönderiler bulunur. Bu yapı üç modülü aynı anda besler:
  1. Kümeleme modülü  -> bulunacak gerçek kümeler var
  2. Özet tarafsızlığı -> aynı olayın çoklu çerçevesi var
  3. Doğrulama motoru  -> işaretli iddialar ve çelişkiler var
"""

import json, random, hashlib
from datetime import datetime, timedelta
from pathlib import Path

RASTGELE_TOHUM = 42
random.seed(RASTGELE_TOHUM)

CIKTI = Path(__file__).parent / "veri"
SIMDI = datetime(2026, 8, 19, 12, 0, 0)

KATEGORILER = ["gundem", "spor", "ekonomi", "teknoloji", "kultur", "kisisel"]

# --- Kurgusal olaylar: (kategori, baslik, anahtar kelimeler, dogrulanabilir iddia) ---
OLAYLAR = [
    ("gundem", "Büyükşehirde yeni toplu ulaşım hattı açıldı",
     ["metro", "ulaşım", "hat", "belediye"],
     "Yeni hattın günlük 400 bin yolcu taşıyacağı açıklandı."),
    ("gundem", "Kuraklık nedeniyle su kısıtlaması tartışması",
     ["kuraklık", "su", "baraj", "kısıtlama"],
     "Baraj doluluk oranının yüzde 18'e düştüğü öne sürüldü."),
    ("gundem", "Eğitimde yeni müfredat taslağı kamuoyuna açıldı",
     ["müfredat", "eğitim", "okul", "taslak"],
     "Taslakta ders saatlerinin yüzde 12 azaltıldığı iddia edildi."),
    ("spor", "Ligde şampiyonluk yarışı son haftaya kaldı",
     ["lig", "şampiyonluk", "puan", "maç"],
     "İki takım arasındaki averaj farkının 3 olduğu belirtildi."),
    ("spor", "Genç sporcu uluslararası turnuvada finale yükseldi",
     ["turnuva", "final", "sporcu", "madalya"],
     "Sporcunun kendi rekorunu 1.4 saniye geliştirdiği aktarıldı."),
    ("spor", "Stat yenileme projesi ertelendi",
     ["stat", "yenileme", "proje", "erteleme"],
     "Projenin maliyetinin iki katına çıktığı ileri sürüldü."),
    ("ekonomi", "Küçük işletmelere yönelik yeni destek paketi",
     ["destek", "işletme", "kredi", "paket"],
     "Paketten 120 bin işletmenin yararlanacağı açıklandı."),
    ("ekonomi", "Tarım ürünlerinde fiyat dalgalanması",
     ["tarım", "fiyat", "hasat", "market"],
     "Hasat veriminin geçen yıla göre yüzde 22 düştüğü öne sürüldü."),
    ("teknoloji", "Yerli dil modeli için açık veri seti duyuruldu",
     ["yapay zeka", "dil modeli", "veri seti", "açık kaynak"],
     "Veri setinin 40 milyon cümle içerdiği belirtildi."),
    ("teknoloji", "Sosyal platformlarda içerik etiketleme zorunluluğu tartışılıyor",
     ["etiketleme", "içerik", "yapay zeka", "düzenleme"],
     "Düzenlemenin altı ay içinde yürürlüğe gireceği iddia edildi."),
    ("teknoloji", "Kampüste öğrenci girişimlerine hızlandırma programı",
     ["girişim", "kampüs", "hızlandırma", "öğrenci"],
     "Programa 300'den fazla başvuru yapıldığı aktarıldı."),
    ("kultur", "Bağımsız film festivali programı açıklandı",
     ["festival", "film", "program", "gösterim"],
     "Festivalde 64 filmin gösterileceği duyuruldu."),
    ("kultur", "Tarihi yapının restorasyonu tamamlandı",
     ["restorasyon", "tarihi", "yapı", "miras"],
     "Restorasyonun 3 yıl sürdüğü belirtildi."),
]

CERCEVELER = {
    "destekleyici": [
        "{olay} — uzun zamandır beklenen bir adımdı, emeği geçen herkese teşekkürler.",
        "{olay} haberine sevindim açıkçası. {kw} konusunda nihayet somut bir şey görüyoruz.",
        "Bugünün en iyi haberi: {olay}. Bu tür işler daha çok konuşulmalı.",
        "{olay}. Eleştirenler var ama bence doğru yönde atılmış bir adım.",
    ],
    "elestirel": [
        "{olay} deniyor da, {kw} tarafındaki asıl sorun hiç konuşulmuyor.",
        "{olay} — kulağa hoş geliyor, peki sürdürülebilir mi? Detaylar çok muğlak.",
        "Herkes {olay} diye paylaşıyor ama kimse maliyetini sormuyor.",
        "{olay} konusunda temkinliyim. Geçmişte benzer açıklamalar sonuçsuz kalmıştı.",
    ],
    "notr": [
        "{olay}. Açıklamanın tam metni kurumun sitesinde yayımlandı.",
        "{olay} — konuya dair ilk değerlendirmeler bugün paylaşıldı.",
        "Gelişme: {olay}. Ayrıntılar netleştikçe paylaşacağım.",
        "{olay} hakkında bilgi notu: {kw} başlıklarında güncelleme var.",
    ],
    "soru": [
        "{olay} diyorlar da bunun {kw} tarafına etkisi ne olacak, bilen var mı?",
        "{olay} — bu konuda güvenilir bir kaynak paylaşabilecek biri var mı?",
        "Cidden {olay} mı oldu, yoksa yine yanlış mı okudum?",
        "{olay} haberini üç farklı yerde üç farklı şekilde gördüm. Hangisi doğru?",
    ],
    "yanlis_bilgi": [
        "{olay}! Kaynak: bir tanıdığım söyledi ama kesin bilgi, yayın.",
        "{olay} — resmi açıklama gelmeden söylüyorum, rakamlar açıklananın üç katı.",
        "{olay} olayında kimsenin konuşmadığı bir detay var, hemen kaydedin silinmeden.",
    ],
}

KISISEL_GONDERILER = [
    "Sabah 6'da kalkıp çalışmaya başlamak gerçekten işe yarıyormuş, üçüncü hafta.",
    "Bu hafta okuduğum kitabı bitirdim, uzun zamandır bu kadar keyif almamıştım.",
    "Kahve makinesi bozuldu, sabah rutinim çöktü. Öneriye açığım.",
    "Yeni bir şeyler öğrenmenin en zor kısmı başlamak değil, ikinci hafta devam etmek.",
    "Bugün 12 km yürüdüm, telefonun adım sayacı yalan söylemiyorsa.",
    "Akşam yemeğinde ilk kez denediğim tarif tutmadı ama deneyeceğim yine.",
    "Uzun süredir ertelediğim işi bugün hallettim, tarifsiz bir rahatlama.",
    "Şehirde sonbahar başladı sanki, hava bir anda değişti.",
    "Bir arkadaşımla 4 saat konuştuk, telefona hiç bakmadık. Nadir bir şey artık.",
    "Notlarımı düzenlemek için üç farklı sistem denedim, en basit olanı kazandı.",
]

AD_PARCA_1 = ["yaz", "deniz", "kuzey", "sessiz", "gece", "mavi", "yalın", "uzak",
              "derin", "kara", "ince", "geniş", "yeni", "eski", "hızlı", "yavaş"]
AD_PARCA_2 = ["kalem", "defter", "pusula", "fener", "liman", "tepe", "yol", "kapı",
              "orman", "vadi", "köprü", "adım", "iz", "kıyı", "dal", "taş"]

ILGI_HAVUZU = {
    "gundem": 0.9, "spor": 0.6, "ekonomi": 0.5,
    "teknoloji": 0.7, "kultur": 0.4, "kisisel": 0.8,
}


def kullanici_uret(n=60):
    kullanicilar, kullanilan = [], set()
    for i in range(n):
        while True:
            k = f"{random.choice(AD_PARCA_1)}_{random.choice(AD_PARCA_2)}{random.randint(1, 99)}"
            if k not in kullanilan:
                kullanilan.add(k)
                break
        # Takipçi dağılımı gerçekçi olsun: çoğu küçük, birkaçı çok büyük (uzun kuyruk)
        takipci = int(random.paretovariate(1.3) * 120)
        rol = "uretici" if takipci > 5000 else "kullanici"
        ilgi = random.sample(KATEGORILER, k=random.randint(2, 4))
        kullanicilar.append({
            "id": f"u{i+1:03d}",
            "kullanici_adi": k,
            "rol": rol,
            "takipci_sayisi": takipci,
            "takip_edilen_sayisi": random.randint(30, 900),
            "hesap_yasi_gun": random.randint(12, 2600),
            "ilgi_alanlari": ilgi,
            "dogrulanmis": takipci > 20000,
        })
    return kullanicilar


def _id(*parcalar):
    return hashlib.sha1("|".join(map(str, parcalar)).encode()).hexdigest()[:12]


def gonderi_uret(kullanicilar):
    gonderiler = []
    uretici_havuz = [u for u in kullanicilar if u["rol"] == "uretici"] or kullanicilar[:5]

    # 1) Olay kümeleri
    for olay_no, (kat, baslik, kws, iddia) in enumerate(OLAYLAR):
        olay_id = f"olay{olay_no+1:02d}"
        # Olay bir zaman noktasında patlar, gönderiler etrafına dağılır
        olay_ani = SIMDI - timedelta(hours=random.randint(6, 130))
        adet = random.randint(6, 14)
        cerceve_dagilim = (["notr"] * 3 + ["destekleyici"] * 3 +
                           ["elestirel"] * 3 + ["soru"] * 2 + ["yanlis_bilgi"] * 1)
        for j in range(adet):
            cerceve = random.choice(cerceve_dagilim)
            sablon = random.choice(CERCEVELER[cerceve])
            metin = sablon.format(olay=baslik, kw=random.choice(kws))
            yazar = random.choice(kullanicilar)
            zaman = olay_ani + timedelta(minutes=random.randint(0, 60 * 40))
            if zaman > SIMDI:
                zaman = SIMDI - timedelta(minutes=random.randint(5, 240))
            gorsel_var = random.random() < 0.35
            gonderiler.append({
                "id": _id("g", olay_id, j),
                "yazar_id": yazar["id"],
                "metin": metin,
                "kategori": kat,
                "olay_id": olay_id,              # kümeleme için altın etiket
                "olay_basligi": baslik,
                "cerceve": cerceve,              # tarafsızlık modülü için altın etiket
                "zaman": zaman.isoformat(),
                "begeni": max(0, int(random.paretovariate(1.5) * 14)),
                "yeniden_paylasim": max(0, int(random.paretovariate(1.8) * 5)),
                "yanit_sayisi": random.randint(0, 40),
                "gorsel_var": gorsel_var,
                # Görsel AI-tespit modülü için altın etiket
                "gorsel_yapay_uretim": (random.random() < 0.3) if gorsel_var else None,
                # Doğrulama motoru için: bu gönderi sınanabilir bir iddia içeriyor mu
                "dogrulanabilir_iddia": iddia if cerceve in ("yanlis_bilgi", "notr") else None,
                "iddia_dogru_mu": (False if cerceve == "yanlis_bilgi"
                                   else (True if cerceve == "notr" else None)),
            })

    # 2) Kişisel akış gönderileri (kümesiz, gündem dışı)
    for j in range(90):
        yazar = random.choice(kullanicilar)
        zaman = SIMDI - timedelta(minutes=random.randint(10, 60 * 24 * 6))
        gonderiler.append({
            "id": _id("k", j),
            "yazar_id": yazar["id"],
            "metin": random.choice(KISISEL_GONDERILER),
            "kategori": "kisisel",
            "olay_id": None,
            "olay_basligi": None,
            "cerceve": "notr",
            "zaman": zaman.isoformat(),
            "begeni": max(0, int(random.paretovariate(2.0) * 8)),
            "yeniden_paylasim": random.randint(0, 6),
            "yanit_sayisi": random.randint(0, 12),
            "gorsel_var": random.random() < 0.2,
            "gorsel_yapay_uretim": None,
            "dogrulanabilir_iddia": None,
            "iddia_dogru_mu": None,
        })

    gonderiler.sort(key=lambda g: g["zaman"], reverse=True)
    return gonderiler


def etkilesim_uret(kullanicilar, gonderiler):
    """İçerik üretici öneri modülü için anonim etkileşim olayları."""
    olaylar = []
    for g in gonderiler:
        n = min(g["begeni"], 60)
        for _ in range(n):
            k = random.choice(kullanicilar)
            t = datetime.fromisoformat(g["zaman"]) + timedelta(minutes=random.randint(1, 900))
            if t > SIMDI:
                continue
            olaylar.append({
                "gonderi_id": g["id"],
                "tur": random.choices(["begeni", "yanit", "paylasim", "kaydetme"],
                                      weights=[70, 15, 10, 5])[0],
                "zaman": t.isoformat(),
                "saat": t.hour,
                "gun": t.weekday(),
                "kategori": g["kategori"],
                # KVKK: kullanıcı kimliği taşınmaz, yalnızca toplulaştırılabilir segment
                "segment": random.choice(["A", "B", "C", "D"]),
                "takipci_araligi": ("0-1k" if k["takipci_sayisi"] < 1000
                                    else "1k-10k" if k["takipci_sayisi"] < 10000
                                    else "10k+"),
            })
    return olaylar


def main():
    CIKTI.mkdir(exist_ok=True)
    kullanicilar = kullanici_uret()
    gonderiler = gonderi_uret(kullanicilar)
    etkilesimler = etkilesim_uret(kullanicilar, gonderiler)

    for ad, veri in [("kullanicilar", kullanicilar),
                     ("gonderiler", gonderiler),
                     ("etkilesimler", etkilesimler)]:
        yol = CIKTI / f"{ad}.json"
        yol.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")

    kume_sayisi = len({g["olay_id"] for g in gonderiler if g["olay_id"]})
    iddiali = sum(1 for g in gonderiler if g["dogrulanabilir_iddia"])
    yanlis = sum(1 for g in gonderiler if g["iddia_dogru_mu"] is False)
    ai_gorsel = sum(1 for g in gonderiler if g["gorsel_yapay_uretim"])

    print(f"kullanicilar : {len(kullanicilar):>5}")
    print(f"gonderiler   : {len(gonderiler):>5}  ({kume_sayisi} olay kümesi)")
    print(f"etkilesimler : {len(etkilesimler):>5}")
    print(f"iddia iceren : {iddiali:>5}  (yanlis: {yanlis})")
    print(f"AI gorsel    : {ai_gorsel:>5}")
    print(f"\ncikti -> {CIKTI}")


if __name__ == "__main__":
    main()
