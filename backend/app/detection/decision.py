"""YZ metin sinyali karar mantığı — İlke 2'nin kodu (spec 6.5).

Bu dosya, tespit modelinden bağımsızdır: model hangi olasılığı üretirse üretsin,
kullanıcıya ne gösterileceğine buradaki kurallar karar verir. Ayrımın sebebi,
model değiştiğinde (BERTurk ince ayarı, farklı bir mimari) ürün davranışının
sabit kalmasıdır.
"""

from __future__ import annotations

from app.config import config
from app.models.detection import DetectionResult, LengthBucket
from app.textutil import count_tokens


def length_bucket(token_sayisi: int) -> LengthBucket:
    """Token sayısını uzunluk kovasına çevirir (spec 5.2).

    Kova sınırları veri seti üretimiyle aynı olmalıdır; aksi halde rapor
    Tablo 4'teki kova bazlı doğruluk, eğitimdeki kovalarla eşleşmez.
    """
    if token_sayisi < 50:
        return "K1"
    if token_sayisi < 100:
        return "K2"
    return "K3"


def karar_ver(
    metin: str,
    olasilik: float | None,
    *,
    bant: tuple[float | None, float | None] | None = None,
) -> DetectionResult:
    """YZ üretimi sinyalini çekimserlik kurallarıyla birlikte değerlendirir.

    NEDEN ÇEKİMSERLİK: Kısa Türkçe metinlerde tespit başarımı hızla düşer.
    Sosyal medya ölçeğinde %3'lük bir yanlış pozitif oranı bile on binlerce
    kullanıcıyı haksız yere etiketlemek demektir. Bu itibar zararı ve hukuki
    risk doğurur. Bu yüzden emin olmadığımızda hiçbir şey göstermiyoruz.

    Args:
        metin: Değerlendirilecek gönderi metni.
        olasilik: Modelin "yapay zekâ ürünü" olasılığı [0,1]. Model yoksa None.
        bant: (alt, üst) karar eşikleri. Verilmezse `config` içindeki sabit
            bant kullanılır. Kalibre edilmiş bandı `detection/calibration.py`
            üretir; bir uç None ise O YÖNDE HİÇ ETİKET GÖSTERİLMEZ (hedef
            kesinliği sağlayan eşik bulunamamıştır).

    Returns:
        DetectionResult — `label=None` ve `abstained=True` ise arayüzde hiçbir
        rozet gösterilmez (boş alan bırakılır, spec 6.9).
    """
    token_sayisi = count_tokens(metin)
    kova = length_bucket(token_sayisi)

    # 0) Model yok: sinyal üretemiyoruz. Uydurma olasılık atamak yerine
    #    çekimser kalıyoruz (spec 2: uydurma metrik yok).
    if olasilik is None:
        return DetectionResult(
            label=None,
            abstained=True,
            reason="model_yok",
            token_count=token_sayisi,
            length_bucket=kova,
        )

    # 1) Uzunluk eşiği — modelin güvenilir olmadığı bölge.
    #    Kısa metinde üslup sinyali yok denecek kadar azdır; model yine de bir
    #    sayı üretir ama o sayı bilgi taşımaz.
    if token_sayisi < config.min_detection_tokens:
        return DetectionResult(
            label=None,
            abstained=True,
            reason="metin_cok_kisa",
            token_count=token_sayisi,
            length_bucket=kova,
        )

    # 2) Belirsizlik bandı — model kararsızsa hüküm verme.
    #    Bant genişliği ölçümle kalibre edilir: bandı genişletmek çekimserlik
    #    oranını artırır ama yanlış pozitifi düşürür. Bu takas raporda
    #    açıkça gösterilir (FPR@95TPR ve çekimserlik oranı birlikte).
    alt, ust = bant if bant is not None else (config.abstain_low, config.abstain_high)
    ust_gecti = ust is not None and olasilik > ust
    alt_gecti = alt is not None and olasilik < alt

    # İki eşik de geçilmişse (kalibrasyon bandı çakışmışsa: alt > üst) hangi
    # yönde olduğumuzu söyleyemeyiz — çekimser kalıyoruz. Sabit bantta bu
    # durum oluşmaz; kalibre bantta iki uç birbirini geçebilir.
    if (not ust_gecti and not alt_gecti) or (ust_gecti and alt_gecti):
        return DetectionResult(
            label=None,
            confidence=olasilik,
            abstained=True,
            reason="belirsiz",
            token_count=token_sayisi,
            length_bucket=kova,
        )

    etiket = "yz_olasi" if ust_gecti else "insan_olasi"
    return DetectionResult(
        label=etiket,
        confidence=olasilik,
        abstained=False,
        token_count=token_sayisi,
        length_bucket=kova,
    )
