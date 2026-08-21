"""YZ tespiti veri seti kurulumu ve ön işleme (spec 5.2).

İki sınıf: `insan` / `yapay_zeka`. Uzunluk kovalarına (K1/K2/K3) ayrılmış,
her kovada her sınıftan dengeli örnek.

--- EN ÖNEMLİ TASARIM KARARI: ŞABLON-AYRIK BÖLME -----------------------------
Sentetik veride train/test bölmesini rastgele yapmak ÖLÇÜMÜ GEÇERSİZ KILAR.
Aynı şablondan üretilmiş iki cümle, farklı kelimelerle de olsa aynı kalıbı
taşır; biri eğitimde biri testte olursa model kalıbı ezberler ve test
başarımı gerçek genelleme değil, ezber ölçer.

Bu yüzden şablonlar (kaynak kalıplar) önce gruplara ayrılır, GRUPLAR
train/val/test'e dağıtılır. Test kümesindeki hiçbir örnek, eğitimde görülmüş
bir şablondan üretilmemiştir. Bu, ölçülen başarımı düşürür — ama ölçtüğü şey
gerçektir. Rapora bu bölme yöntemi ve gerekçesi yazılır.
-----------------------------------------------------------------------------

Ön işleme adımları (spec 5.2):
  1. Türkçe karakter normalizasyonu (turkish_lower — str.lower() Türkçe'de yanlış)
  2. Yinelenen ve yakın-yinelenen ayıklama (normalize-hash + shingle Jaccard)
  3. Kişisel veri maskeleme (governance/pii.py üzerinden)
  4. Sınıf dengesi kontrolü
  5. Katmanlı (kova × sınıf) train/val/test ayrımı — şablon-ayrık
  6. Sızıntı denetimi: aynı/benzer metin iki kümede birden olmamalı

Kullanım:
    python ml/scripts/build_dataset.py --per-cell 220 --seed 20260824
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

import _bootstrap  # noqa: F401

from app.governance.consent import CONSENT_FIELD, filter_for_training
from app.governance.pii import mask_pii
from app.llm.embedding import turkish_lower
from app.textutil import count_tokens

REPO_ROOT = _bootstrap.REPO_ROOT
CIKTI_DIZINI = REPO_ROOT / "ml" / "data" / "detection"

KOVALAR = ("K1", "K2", "K3")
SINIFLAR = ("insan", "yapay_zeka")

# ----------------------------------------------------------------------
# ŞABLON HAVUZLARI
# ----------------------------------------------------------------------
# Her şablon bir "grup" kimliği taşır (`g1`, `g2`, ...). Bölme bu gruplara
# göre yapılır. Aynı gruptaki şablonlar birbirine benzer kalıplar içerir;
# farklı gruplar farklı yazım kalıplarını temsil eder.
#
# NEDEN ELLE YAZILMIŞ ŞABLONLAR: Gerçek veri kazımak yasak (spec 2). Gerçek
# LLM'den örnek üretmek mümkün ama o zaman veri seti tek bir modelin üslubunu
# ölçer. Elle yazılan kalıplar, YZ metinlerinin RAPOR EDİLEN yüzey özelliklerini
# (temkinli dil, bağlaç yoğunluğu, kalıplaşmış kapanış, kişisel deneyim
# yokluğu, yazım hatası ve emoji yokluğu) bilinçli olarak temsil eder.
#
# SINIRLILIK (rapora yazılacak): Bu bir üslup sınıflandırma görevidir, gerçek
# "YZ tespiti" değildir. Ölçülen başarım, gerçek dağılımda beklenecek başarımın
# ÜST SINIRI olarak okunmalıdır.

INSAN_SABLONLARI: list[tuple[str, str]] = [
    # (grup, şablon) — {x} yer tutucuları varyasyonla doldurulur
    ("g1", "bugün {sey} yüzünden geç kaldım, sabah trafiği yine berbattı"),
    ("g1", "{sey} için üç kere aradım, kimse açmadı ya"),
    ("g1", "sabah {sey} yaparken kendimi çok yorgun hissettim, kahve de fayda etmedi"),
    ("g2", "{sey} konusunda ne desem bilemedim, valla şaşırdım"),
    ("g2", "yıllardır aynı şey, {sey} değişmiyor bir türlü"),
    ("g2", "bana kalırsa {sey} abartılıyor, ben pek etkilenmedim"),
    ("g3", "{sey} aldım, fena değil ama fiyatı biraz tuzlu geldi"),
    ("g3", "{sey} denedim, beklediğim gibi çıkmadı açıkçası"),
    ("g3", "arkadaşın önerdiği {sey} işe yaradı, teşekkür ettim"),
    ("g4", "{sey} hakkında düşündükçe sinirleniyorum, kimse hesap sormuyor"),
    ("g4", "{sey} olayında haklı olan taraf belli ama tartışıyoruz hâlâ"),
    ("g4", "{sey} için imza topluyorlar, ben de attım"),
    ("g5", "dün akşam {sey} izledim, yarısında uyuyakalmışım"),
    ("g5", "{sey} çok komikti, akşama kadar güldük"),
    ("g5", "{sey} yaparken elimi kestim, dikkatsizlik işte"),
    ("g6", "{sey} nerede bulabilirim, bilen var mı acaba"),
    ("g6", "{sey} tavsiye eder misiniz, karar veremedim"),
    ("g6", "{sey} kaç para, fikri olan yazsın"),
    # --- ZOR ÖRNEKLER: RESMÎ ÜSLUPLA YAZAN İNSAN ---------------------------
    # NEDEN GEREKLİ: İlk kurulumda doğrulama doğruluğu 1.00 çıktı. Sebebi,
    # iki sınıfın yalnızca ÜSLUP KAYDIYLA (resmî vs. konuşma dili) ayrışmasıydı.
    # Böyle bir veri setinde ölçülen başarım, "resmî yazı ile sohbet ayırt
    # edilebiliyor" demektir; YZ tespiti hakkında bilgi vermez ve çekimserlik
    # mekanizmasının hiç devreye girmediği yapay bir dünya kurar.
    # Gerçek hayatta insanlar da resmî yazar (esnaf odası duyurusu, apartman
    # yönetimi, dernek açıklaması). Bu şablonlar o bölgeyi doldurur.
    ("g13", "Sayın komşular, {sey} ile ilgili çalışma yarın sabah başlayacaktır, bilgilerinize sunarım"),
    ("g13", "Apartman yönetimi olarak {sey} konusundaki talepleri değerlendirdik, sonucu duyuracağız"),
    ("g13", "{sey} hakkındaki başvurular bu hafta içinde alınacaktır, ilgililere duyurulur"),
    ("g14", "Dernek olarak {sey} konusunda yaptığımız görüşmeyi üyelerimizle paylaşmak isteriz"),
    ("g14", "Esnaf odası toplantısında {sey} gündeme alındı, kararlar tutanağa geçirildi"),
    ("g14", "{sey} için oluşturulan komisyon çalışmalarına başlamıştır, takip edeceğiz"),
    ("g15", "Bilgilendirme: {sey} nedeniyle hizmet saatlerinde değişikliğe gidilmiştir"),
    ("g15", "{sey} konusunda yanlış bilgi dolaşıyor, doğrusunu yazma gereği duydum"),
    ("g15", "Kayıt için gerekli belgeler ve {sey} ile ilgili ayrıntılar aşağıda sıralanmıştır"),
    # Zor katmanın grup sayısı, kolay katmanla eşitlendi (6 grup).
    # NEDEN: Katman başına 3 grupla bölme yapıldığında eğitimde her zor
    # katmandan yalnızca 1 grup kalıyordu; model tek bir kalıptan genelleme
    # yapmak zorunda kaldı ve doğrulama doğruluğu şansa (0.51) düştü. Bu,
    # modelin yeteneğini değil veri çeşitliliğinin yetersizliğini ölçen bir
    # kuruluma işaret ediyordu.
    ("g19", "{sey} ile ilgili toplantı tutanağını paylaşıyorum, kararlar özetle şöyle"),
    ("g19", "Site sakinlerinin bilgisine: {sey} çalışması için geçici düzenleme yapılacaktır"),
    ("g19", "{sey} başvuru süreci hakkında sıkça sorulan soruları derledim"),
    ("g20", "Veli olarak {sey} konusundaki görüşümü resmî kanallardan ilettim"),
    ("g20", "{sey} hakkında yazılı başvuru yaptım, gelen cevabı buraya ekliyorum"),
    ("g20", "İlgili birimle görüştüm, {sey} için izlenecek adımlar netleşti"),
    ("g21", "Kooperatif üyelerine duyuru: {sey} ödemeleri bu ay sonuna kadar yapılacaktır"),
    ("g21", "{sey} nedeniyle oluşan mağduriyet için dilekçe örneği hazırladım"),
    ("g21", "Mahalle toplantısında {sey} maddesi görüşüldü, katılım yüksekti"),
]

YZ_SABLONLARI: list[tuple[str, str]] = [
    ("g7", "{konu} konusu, günümüzde giderek daha fazla önem kazanan çok boyutlu bir mesele olarak öne çıkmaktadır"),
    ("g7", "{konu} alanında yaşanan gelişmeler, hem bireysel hem de toplumsal düzeyde etkiler doğurmaktadır"),
    ("g7", "{konu} bağlamında atılacak adımların, uzun vadeli bir bakış açısıyla planlanması büyük önem taşımaktadır"),
    ("g8", "{konu} değerlendirilirken, farklı paydaşların beklentilerinin dengeli biçimde gözetilmesi gerekmektedir"),
    ("g8", "{konu} ile ilgili kararların veriye dayalı biçimde alınması, sürecin etkinliğini artıracaktır"),
    ("g8", "{konu} konusunda şeffaflığın sağlanması, kamuoyu güveninin tesisi açısından belirleyicidir"),
    ("g9", "{konu} sürecinde dikkat edilmesi gereken başlıca hususlar arasında planlama, izleme ve değerlendirme yer almaktadır"),
    ("g9", "{konu} kapsamında kurumlar arası eşgüdümün güçlendirilmesi, uygulamanın başarısına katkı sunacaktır"),
    ("g9", "{konu} için belirlenecek ölçülebilir hedefler, ilerlemenin takip edilmesini kolaylaştıracaktır"),
    ("g10", "{konu} meselesi, tek bir bakış açısıyla ele alınamayacak kadar katmanlı bir yapıya sahiptir"),
    ("g10", "{konu} tartışmalarında yapıcı bir zemin oluşturulması, ortak çözümlerin geliştirilmesine olanak tanır"),
    ("g10", "{konu} hakkında yürütülen çalışmaların düzenli olarak raporlanması, hesap verebilirliği güçlendirir"),
    ("g11", "{konu} açısından bakıldığında, mevcut durumun kapsamlı biçimde analiz edilmesi öncelikli bir ihtiyaçtır"),
    ("g11", "{konu} alanındaki iyi uygulama örneklerinin incelenmesi, yol haritasının belirlenmesine katkı sağlar"),
    ("g11", "{konu} ile bağlantılı riskler önceden tespit edilerek gerekli önlemler alınmalıdır"),
    ("g12", "{konu} konusunda kapsayıcı bir yaklaşımın benimsenmesi, sürdürülebilir sonuçlar açısından kritiktir"),
    ("g12", "{konu} süreçlerinde katılımcılığın artırılması, kararların benimsenmesini kolaylaştırmaktadır"),
    ("g12", "{konu} bakımından atılan adımların etkisi, orta ve uzun vadede daha net biçimde görülecektir"),
    # --- ZOR ÖRNEKLER: SAMİMİ ÜSLUP TAKLİDİ YAPAN YZ -----------------------
    # Dil modellerinden "sosyal medya gönderisi gibi yaz" istendiğinde çıkan
    # tipik metin: konuşma dili kaydında ama pürüzsüz, yazım hatasız, kişisel
    # ayrıntısı olmayan, ölçülü duygu ifadesi taşıyan cümleler. Tespit bu
    # bölgede zorlaşır — ve İlke 2'nin (çekimserlik) gerçekten devreye girmesi
    # gereken yer burasıdır.
    ("g16", "bugün {konu} üzerine düşündüm ve küçük adımların da fark yarattığını hatırladım"),
    ("g16", "{konu} hakkında okuduklarım bana farklı bir bakış açısı kazandırdı, paylaşmak istedim"),
    ("g16", "{konu} ile ilgili yaşadıklarım bana sabrın önemini bir kez daha gösterdi"),
    ("g17", "sabah sabah {konu} konusu aklıma geldi, bazen en basit şeyler en çok düşündürüyor"),
    ("g17", "{konu} deyince akla ilk gelen zorluklar oluyor ama fırsatları da görmek gerek"),
    ("g17", "{konu} üzerine kısa bir not: dinlemek, konuşmaktan daha çok şey öğretiyor"),
    ("g18", "{konu} hakkında herkesin bir fikri var, ben dinlemeyi tercih ediyorum bugünlerde"),
    ("g18", "{konu} ile ilgili küçük bir gözlem: değişim yavaş oluyor ama oluyor"),
    ("g18", "{konu} konusunda aceleci davranmamak gerektiğini deneyimlerimle öğrendim"),
    # Samimi üslup taklidi yapan YZ — bu katman da 6 gruba çıkarıldı.
    ("g22", "{konu} ile ilgili bugün küçük bir şey fark ettim ve paylaşmak istedim"),
    ("g22", "{konu} hakkında konuşurken çoğu zaman aynı noktaya geliyoruz, ilginç"),
    ("g22", "{konu} üzerine düşününce insanın bakış açısı değişebiliyor"),
    ("g23", "{konu} bazen karmaşık görünüyor ama temelde basit bir mesele aslında"),
    ("g23", "{konu} konusunda herkesin deneyimi farklı, bu da zenginlik sayılır"),
    ("g23", "{konu} ile ilgili sabırlı olmak çoğu zaman en iyi yaklaşım oluyor"),
    ("g24", "{konu} hakkında dün bir sohbet ettik, güzel bir noktaya değinildi"),
    ("g24", "{konu} deyince herkesin aklına başka bir şey geliyor, doğal olan da bu"),
    ("g24", "{konu} üzerine küçük adımların zamanla fark yarattığını görüyorum"),
]

SEYLER = [
    "kargo", "otobüs", "market alışverişi", "elektrik faturası", "yeni kulaklık",
    "internet bağlantısı", "randevu", "toplantı", "servis", "yemek siparişi",
    "kitap", "bisiklet", "komşunun matkabı", "asansör", "sıra beklemek",
    "banka işlemi", "kirası", "tadilat", "sınav sonucu", "aşı randevusu",
]
KONULAR = [
    "kentsel ulaşım planlaması", "su kaynaklarının yönetimi", "eğitimde fırsat eşitliği",
    "dijital dönüşüm", "gençlerin istihdamı", "yerel yönetim hizmetleri",
    "enerji verimliliği", "kültürel mirasın korunması", "afet hazırlığı",
    "sağlık hizmetlerine erişim", "tarımsal üretim planlaması", "atık yönetimi",
]

# Resmî üslupta yazan gruplar: insan tarafında g13-g15, YZ tarafında g7-g12.
# Samimi üslupta yazanlar: insan g1-g6, YZ g16-g18. Ek havuzu bu ayrıma göre
# seçilir (bkz. _metin_uret), sınıfa göre değil.
RESMI_USLUP_GRUPLARI = frozenset(
    {
        # YZ resmî (kolay YZ katmanı)
        "g7", "g8", "g9", "g10", "g11", "g12",
        # İnsan resmî (zor insan katmanı)
        "g13", "g14", "g15", "g19", "g20", "g21",
    }
)

# Uzunluk ayarlayıcı ekler: aynı şablondan K1/K2/K3 örneği üretmeye yarar.
SAMIMI_EKLER = [
    "hem de tam işe yetişmem gereken gün",
    "neyse artık alıştım diyeyim",
    "sonra bir baktım saat olmuş",
    "yanımdaki de aynı şeyden dert yanıyordu",
    "en azından hava güzeldi",
    "geçen hafta da benzeri olmuştu",
    "kimseye de anlatamıyorum tabii",
    "bir dahakine daha dikkatli olacağım",
    "arkadaşlar da aynı şeyi söylüyor",
    "yorumlarda benzer şeyler yazılmış",
]
RESMI_EKLER = [
    "Bu doğrultuda paydaş katılımının güçlendirilmesi önem arz etmektedir",
    "Söz konusu yaklaşım, uygulamanın etkinliğini artırma potansiyeli taşımaktadır",
    "Ayrıca izleme ve değerlendirme mekanizmalarının işletilmesi gerekmektedir",
    "Bu kapsamda düzenli bilgilendirme faaliyetleri yürütülmesi faydalı olacaktır",
    "Elde edilecek çıktıların kamuoyuyla paylaşılması şeffaflığı destekleyecektir",
    "Uzun vadede sürdürülebilirliğin sağlanması temel hedef olmalıdır",
    "İlgili tarafların görüşlerinin alınması, sürecin sahiplenilmesini kolaylaştırır",
    "Bu çerçevede kaynakların etkin kullanımı gözetilmelidir",
]


@dataclass
class Ornek:
    """Veri seti kaydı."""

    id: str
    text: str
    label: str  # "insan" | "yapay_zeka"
    bucket: str  # K1 | K2 | K3
    token_count: int
    template_group: str
    # Yönetişim kapısı: eğitim havuzuna girecek her kaydın izni olmalı (spec 5.3).
    # Sentetik veri için izin tanım gereği vardır (gerçek kişi verisi değil),
    # ama alan yine de taşınır ve kapı yine de işletilir.
    training_consent: bool = True
    split: str = ""


@dataclass
class Rapor:
    """Veri seti kurulum raporu — rapor 3.1 için sayılar."""

    total_generated: int = 0
    removed_exact_duplicate: int = 0
    removed_near_duplicate: int = 0
    removed_no_consent: int = 0
    masked_records: int = 0
    counts: dict[str, int] = field(default_factory=dict)
    leakage_exact: int = 0
    leakage_near: int = 0
    template_overlap: dict[str, list[str]] = field(default_factory=dict)


# ----------------------------------------------------------------------
# Üretim
# ----------------------------------------------------------------------
def _hedef_uzunluk(kova: str, rng: random.Random) -> int:
    """Kovanın token aralığından bir hedef uzunluk seçer."""
    return {"K1": rng.randint(22, 46), "K2": rng.randint(55, 95), "K3": rng.randint(105, 170)}[kova]


def _metin_uret(sinif: str, kova: str, rng: random.Random) -> tuple[str, str]:
    """Sınıf ve kovaya uygun metin üretir.

    Returns:
        (metin, şablon_grubu)

    Uzunluk, hedef token sayısına ulaşana kadar sınıfa uygun ek cümleler
    eklenerek ayarlanır. Ekler de sınıfın üslubunu taşır; aksi halde uzunluk
    tek başına sınıf sinyali olurdu ve model uzunluğa bakarak "tespit" ederdi.
    """
    if sinif == "insan":
        grup, sablon = rng.choice(INSAN_SABLONLARI)
        govde = sablon.format(sey=rng.choice(SEYLER))
    else:
        grup, sablon = rng.choice(YZ_SABLONLARI)
        govde = sablon.format(konu=rng.choice(KONULAR))

    # Uzatma cümleleri ÜSLUBA göre seçilir, SINIFA göre değil.
    # NEDEN: Ekleri sınıfa bağlamak, uzun metinlerde sınıfı ele veren ikinci bir
    # sinyal yaratır ve zor örnekleri (resmî yazan insan / samimi yazan YZ)
    # kolaylaştırıp anlamsızlaştırırdı. Model, gövdeyle aynı kayıttaki
    # eklerden ipucu almamalı; ayrım gövdedeki kalıptan gelmelidir.
    resmi_uslup = grup in RESMI_USLUP_GRUPLARI
    ekler = RESMI_EKLER if resmi_uslup else SAMIMI_EKLER
    ayirici = ". " if resmi_uslup else ", "

    hedef = _hedef_uzunluk(kova, rng)
    parcalar = [govde]
    guvenlik = 0
    while count_tokens(ayirici.join(parcalar)) < hedef and guvenlik < 12:
        parcalar.append(rng.choice(ekler))
        guvenlik += 1
    metin = ayirici.join(parcalar)
    if sinif == "yapay_zeka" and not metin.endswith("."):
        metin += "."
    return metin, grup


# ----------------------------------------------------------------------
# Ön işleme
# ----------------------------------------------------------------------
_BOSLUK_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Yineleme tespiti için kanonik biçim.

    Noktalama ve boşluk farkları yinelemeyi gizler; karşılaştırmayı bu
    kanonik biçim üzerinden yapıyoruz. Türkçe küçültme kritik: "Bugün" ile
    "BUGÜN" aynı metindir ama str.lower() 'İ' harfinde yanlış sonuç verir.
    """
    kucuk = turkish_lower(text)
    yalin = re.sub(r"[^\wçğıöşü\s]", " ", kucuk)
    return _BOSLUK_RE.sub(" ", yalin).strip()


def metin_hash(text: str) -> str:
    """Kanonik metnin hash'i (birebir yineleme tespiti)."""
    return hashlib.blake2b(normalize(text).encode("utf-8"), digest_size=16).hexdigest()


def shingles(text: str, n: int = 4) -> set[str]:
    """Kelime n-gram kümesi (yakın-yineleme tespiti için).

    MinHash yerine doğrudan Jaccard kullanıyoruz: veri seti birkaç bin kayıt
    düzeyinde ve doğrudan hesap hem kesin hem de yeterince hızlı. MinHash
    yaklaşıklığı ancak yüz binlerce kayıtta gerekli olur.
    """
    kelimeler = normalize(text).split()
    if len(kelimeler) < n:
        return {" ".join(kelimeler)}
    return {" ".join(kelimeler[i : i + n]) for i in range(len(kelimeler) - n + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    """İki shingle kümesi arasındaki Jaccard benzerliği."""
    if not a or not b:
        return 0.0
    kesisim = len(a & b)
    return kesisim / (len(a) + len(b) - kesisim)


# Yakın-yineleme eşiği. 0.8: dörtlü kelime n-gramlarının %80'i ortaksa iki metin
# pratikte aynıdır. Daha düşük eşik meşru benzer cümleleri de siler ve veri
# setini gereksiz daraltır.
NEAR_DUP_ESIK = 0.80


def yinelenenleri_ayikla(ornekler: list[Ornek], rapor: Rapor) -> list[Ornek]:
    """Birebir ve yakın yinelenenleri ayıklar.

    Yakın-yineleme karşılaştırması aynı (sınıf, kova) hücresi içinde yapılır:
    farklı sınıflardan iki metnin yakın olması zaten olmaz, tüm çiftleri
    karşılaştırmak ise gereksiz maliyettir.
    """
    gorulen_hash: set[str] = set()
    tekil: list[Ornek] = []
    for ornek in ornekler:
        h = metin_hash(ornek.text)
        if h in gorulen_hash:
            rapor.removed_exact_duplicate += 1
            continue
        gorulen_hash.add(h)
        tekil.append(ornek)

    sonuc: list[Ornek] = []
    hucre_shingles: dict[tuple[str, str], list[set[str]]] = {}
    for ornek in tekil:
        anahtar = (ornek.label, ornek.bucket)
        sh = shingles(ornek.text)
        if any(jaccard(sh, mevcut) >= NEAR_DUP_ESIK for mevcut in hucre_shingles.get(anahtar, [])):
            rapor.removed_near_duplicate += 1
            continue
        hucre_shingles.setdefault(anahtar, []).append(sh)
        sonuc.append(ornek)
    return sonuc


def _grup_bolmesi(
    gruplar_katman_bazli: dict[tuple[str, str], list[str]], rng: random.Random
) -> dict[str, str]:
    """Şablon gruplarını train/val/test'e dağıtır (şablon-ayrık, katmanlı).

    Args:
        gruplar_katman_bazli: (sınıf, üslup) -> o katmana ait şablon grupları.

    İKİ KATMAN, İKİ AYRI DERS:

    1) SINIF katmanı: Tüm grupları tek havuzda karıştırıp bölmek şablon-ayrıklığı
       sağlar ama sınıf dengesini yok eder. İlk denemede tüm YZ grupları eğitime,
       tüm insan grupları teste düştü; val ve test tek sınıflı kaldı, ölçüm
       imkânsız hale geldi.

    2) ÜSLUP katmanı: Sınıf içinde bölmek de yetmedi. İkinci denemede test
       kümesine yalnızca KOLAY gruplar (konuşma dilindeki insan + resmî YZ)
       düştü ve test doğruluğu 1.00 çıktı — oysa doğrulama kümesinde 0.80'di.
       Aynı modelin iki bölmede bu kadar farklı görünmesi, bölmenin ölçtüğü
       şeyin model değil, o bölmeye düşen grupların zorluğu olduğunu gösterir.
       Bu yüzden zor gruplar (resmî yazan insan / samimi yazan YZ) her bölmeye
       ayrı ayrı dağıtılır.

    Oranlar yaklaşık %60/%20/%20'dir; grup sayısı az olduğu için tam tutmaz.
    Değişmez kural: hiçbir grup iki bölmede birden bulunmaz.
    """
    atama: dict[str, str] = {}
    for _katman, gruplar in sorted(gruplar_katman_bazli.items()):
        karisik = sorted(gruplar)
        rng.shuffle(karisik)
        n = len(karisik)
        if n < 3:
            raise ValueError(
                f"{_katman} katmanında yalnızca {n} şablon grubu var; şablon-ayrık "
                "bölme için katman başına en az 3 grup gerekir."
            )
        n_test = max(1, round(n * 0.2))
        n_val = max(1, round(n * 0.2))
        for i, grup in enumerate(karisik):
            if i < n_test:
                atama[grup] = "test"
            elif i < n_test + n_val:
                atama[grup] = "val"
            else:
                atama[grup] = "train"
    return atama


def sizinti_denetimi(bolmeler: dict[str, list[Ornek]], rapor: Rapor) -> None:
    """Aynı veya yakın metnin iki bölmede birden olmadığını doğrular (spec 5.2/6).

    Bu denetim raporlanır: "sızıntı yok" demek yetmez, ölçülüp yazılması gerekir.
    """
    hashler = {ad: {metin_hash(o.text) for o in liste} for ad, liste in bolmeler.items()}
    adlar = list(bolmeler)
    for i in range(len(adlar)):
        for j in range(i + 1, len(adlar)):
            ortak = hashler[adlar[i]] & hashler[adlar[j]]
            rapor.leakage_exact += len(ortak)

    # Yakın-yineleme sızıntısı: test kümesindeki her örnek, eğitimdekilerle
    # karşılaştırılır. Maliyet O(|test| x |train|); birkaç bin kayıtta kabul
    # edilebilir ve denetimin kesin olması yaklaşıklıktan önemlidir.
    train_sh = [shingles(o.text) for o in bolmeler.get("train", [])]
    for o in bolmeler.get("test", []):
        sh = shingles(o.text)
        if any(jaccard(sh, t) >= NEAR_DUP_ESIK for t in train_sh):
            rapor.leakage_near += 1

    # Şablon örtüşmesi: bölme yönteminin gerçekten şablon-ayrık olduğunu kanıtlar.
    grup_haritasi: dict[str, set[str]] = {ad: {o.template_group for o in liste} for ad, liste in bolmeler.items()}
    for i in range(len(adlar)):
        for j in range(i + 1, len(adlar)):
            ortak = grup_haritasi[adlar[i]] & grup_haritasi[adlar[j]]
            if ortak:
                rapor.template_overlap[f"{adlar[i]}-{adlar[j]}"] = sorted(ortak)


def veri_seti_kur(per_cell: int, seed: int) -> tuple[dict[str, list[Ornek]], Rapor]:
    """Veri setini uçtan uca kurar.

    Args:
        per_cell: Her (sınıf × kova) hücresi için üretilecek ham örnek sayısı.
        seed: Rastgelelik tohumu.
    """
    rng = random.Random(seed)
    rapor = Rapor()
    ham: list[Ornek] = []
    sayac = 0

    for sinif in SINIFLAR:
        for kova in KOVALAR:
            for _ in range(per_cell):
                metin, grup = _metin_uret(sinif, kova, rng)
                sayac += 1
                ham.append(
                    Ornek(
                        id=f"d{sayac:05d}",
                        text=metin,
                        label=sinif,
                        bucket=kova,
                        token_count=count_tokens(metin),
                        template_group=grup,
                    )
                )
    rapor.total_generated = len(ham)

    # --- Adım 3: kişisel veri maskeleme (yönetişim kapısı) ---
    for ornek in ham:
        sonuc = mask_pii(ornek.text)
        if sonuc.masked_any:
            rapor.masked_records += 1
            ornek.text = sonuc.text

    # --- İzin kapısı: alanı olmayan kayıt eğitim havuzuna giremez ---
    kayitlar = [dict(asdict(o), **{CONSENT_FIELD: o.training_consent}) for o in ham]
    izin_sonucu = filter_for_training(kayitlar)
    rapor.removed_no_consent = izin_sonucu.rejected_total
    izinli_idler = {k["id"] for k in izin_sonucu.accepted}
    ham = [o for o in ham if o.id in izinli_idler]

    # --- Adım 2: yinelenen ayıklama ---
    temiz = yinelenenleri_ayikla(ham, rapor)

    # --- Adım 5: şablon-ayrık, katmanlı bölme ---
    # Katman = (sınıf, üslup). Üslup bilgisi RESMI_USLUP_GRUPLARI'ndan gelir.
    gruplar_katman_bazli: dict[tuple[str, str], list[str]] = {}
    for o in temiz:
        uslup = "resmi" if o.template_group in RESMI_USLUP_GRUPLARI else "samimi"
        anahtar = (o.label, uslup)
        gruplar_katman_bazli.setdefault(anahtar, [])
        if o.template_group not in gruplar_katman_bazli[anahtar]:
            gruplar_katman_bazli[anahtar].append(o.template_group)
    atama = _grup_bolmesi(gruplar_katman_bazli, rng)
    bolmeler: dict[str, list[Ornek]] = {"train": [], "val": [], "test": []}
    for ornek in temiz:
        ornek.split = atama[ornek.template_group]
        bolmeler[ornek.split].append(ornek)

    # --- Adım 4: sınıf dengesi sayımı ---
    for ad, liste in bolmeler.items():
        for sinif in SINIFLAR:
            for kova in KOVALAR:
                anahtar = f"{ad}/{sinif}/{kova}"
                rapor.counts[anahtar] = sum(1 for o in liste if o.label == sinif and o.bucket == kova)

    # --- Adım 6: sızıntı denetimi ---
    sizinti_denetimi(bolmeler, rapor)
    return bolmeler, rapor


def rapor_yaz(bolmeler: dict[str, list[Ornek]], rapor: Rapor, yol: Path) -> None:
    """Veri seti raporunu Markdown olarak yazar (rapor 3.1 tablosu)."""
    satirlar = [
        "# YZ Tespiti Veri Seti",
        "",
        "> `ml/scripts/build_dataset.py` tarafından üretilir. Elle düzenlenmez.",
        "",
        "## Kurulum özeti",
        "",
        f"- Üretilen ham örnek: **{rapor.total_generated}**",
        f"- Birebir yineleme nedeniyle çıkarılan: **{rapor.removed_exact_duplicate}**",
        f"- Yakın-yineleme (Jaccard ≥ {NEAR_DUP_ESIK}) nedeniyle çıkarılan: "
        f"**{rapor.removed_near_duplicate}**",
        f"- İzin kapısında elenen: **{rapor.removed_no_consent}**",
        f"- Kişisel veri maskelenen kayıt: **{rapor.masked_records}**",
        f"- Nihai toplam: **{sum(len(v) for v in bolmeler.values())}**",
        "",
        "## Bölme × sınıf × kova dağılımı",
        "",
        "| Bölme | Sınıf | K1 (0-50) | K2 (50-100) | K3 (100+) | Toplam |",
        "|---|---|---|---|---|---|",
    ]
    for ad in ("train", "val", "test"):
        for sinif in SINIFLAR:
            hucreler = [rapor.counts.get(f"{ad}/{sinif}/{k}", 0) for k in KOVALAR]
            satirlar.append(
                f"| {ad} | {sinif} | {hucreler[0]} | {hucreler[1]} | {hucreler[2]} | {sum(hucreler)} |"
            )
    satirlar += [
        "",
        "## Sızıntı denetimi (spec 5.2 adım 6)",
        "",
        "| Denetim | Sonuç |",
        "|---|---|",
        f"| Bölmeler arası birebir aynı metin | {rapor.leakage_exact} |",
        f"| Test-train yakın-yineleme (Jaccard ≥ {NEAR_DUP_ESIK}) | {rapor.leakage_near} |",
        f"| Bölmeler arası ortak şablon grubu | "
        f"{'YOK' if not rapor.template_overlap else rapor.template_overlap} |",
        "",
        "### Bölme yöntemi",
        "",
        "Bölme **şablon-ayrıktır**: kaynak şablon grupları önce train/val/test'e",
        "dağıtılır, örnekler sonra üretilir. Test kümesindeki hiçbir örnek,",
        "eğitimde görülmüş bir şablondan gelmez. Rastgele bölme, aynı kalıbın",
        "iki tarafta birden bulunmasına ve modelin ezberi genelleme gibi",
        "göstermesine yol açardı.",
        "",
        "### Sınırlılık (dürüstlük notu)",
        "",
        "Veri sentetiktir ve YZ sınıfı, dil modellerinin bilinen yüzey",
        "özelliklerini (temkinli dil, kalıplaşmış bağlaçlar, kişisel deneyim",
        "yokluğu) taklit eden şablonlardan üretilmiştir. Ölçülen başarım, gerçek",
        "dağılımda beklenecek başarımın üst sınırı olarak okunmalıdır.",
        "",
    ]
    yol.write_text("\n".join(satirlar), encoding="utf-8")


def main() -> None:
    ayristirici = argparse.ArgumentParser(description="YZ tespiti veri setini kurar")
    ayristirici.add_argument("--per-cell", type=int, default=220, help="Sınıf × kova başına örnek")
    ayristirici.add_argument("--seed", type=int, default=20260824)
    args = ayristirici.parse_args()

    bolmeler, rapor = veri_seti_kur(args.per_cell, args.seed)
    CIKTI_DIZINI.mkdir(parents=True, exist_ok=True)
    for ad, liste in bolmeler.items():
        (CIKTI_DIZINI / f"{ad}.jsonl").write_text(
            "\n".join(json.dumps(asdict(o), ensure_ascii=False) for o in liste) + "\n",
            encoding="utf-8",
        )
    rapor_yaz(bolmeler, rapor, CIKTI_DIZINI / "dataset_report.md")

    print(f"train={len(bolmeler['train'])} val={len(bolmeler['val'])} test={len(bolmeler['test'])}")
    print(f"birebir yineleme={rapor.removed_exact_duplicate} yakın={rapor.removed_near_duplicate}")
    print(f"sızıntı: birebir={rapor.leakage_exact} yakın={rapor.leakage_near} "
          f"şablon örtüşmesi={rapor.template_overlap or 'YOK'}")
    print(f"rapor -> {CIKTI_DIZINI / 'dataset_report.md'}")


if __name__ == "__main__":
    main()
