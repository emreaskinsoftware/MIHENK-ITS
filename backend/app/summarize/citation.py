"""Atıf denetimi — İlke 1'in uygulandığı yer (spec 6.2 adım 5).

BU DOSYA PROJENİN ANA TEZİDİR. "Söylediği her cümleyi kaynağına bağlayan"
iddiası, model çıktısına güvenerek değil, çıktıyı DENETLEYEREK sağlanır.

Denetim üç şeyi kontrol eder:
  1. Cümlenin kaynak listesi var mı ve boş değil mi?
  2. Gösterilen ID'ler GERÇEKTEN girdi kümesinde mi (uydurma ID değil mi)?
  3. Cümle metni boş değil mi?

Bu kontrollerden geçemeyen cümle SİLİNİR ve `dropped_sentence_count` artırılır.
Silinen cümle kullanıcıya hiçbir biçimde gösterilmez, "kaynak bulunamadı" notu
bile eklenmez — o not da atıfsız bir iddia olurdu.

Denetim UI'da değil serviste yapılır: UI'ya zaten temiz veri gider (İlke 1).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field

from app.models import SummarySentence

logger = logging.getLogger(__name__)

# LLM bazen JSON'u kod bloğu içinde döndürür; sarmalayıcıyı temizlemek için.
_CODE_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


@dataclass
class AuditReport:
    """Atıf denetimi çıktısı ve silme gerekçeleri.

    Gerekçelerin ayrı sayılması ölçüm için önemlidir: modelin "kaynak vermeyi
    unutması" ile "kaynak uydurması" farklı sorunlardır ve farklı çözümler
    gerektirir (prompt düzeltmesi vs. daha güçlü denetim).
    """

    sentences: list[SummarySentence] = field(default_factory=list)
    dropped_empty_source: int = 0
    dropped_unknown_id: int = 0
    dropped_empty_text: int = 0
    parse_failed: bool = False
    # Uydurma olduğu için atılan ID'ler — hata ayıklama ve rapor için.
    hallucinated_ids: list[str] = field(default_factory=list)

    @property
    def dropped_total(self) -> int:
        return self.dropped_empty_source + self.dropped_unknown_id + self.dropped_empty_text


def parse_llm_json(raw: str) -> dict | None:
    """Model çıktısındaki JSON'u ayrıştırır; başarısızsa None.

    NEDEN TOLERANSLI AYRIŞTIRMA: Model bazen JSON'un başına açıklama cümlesi
    ekler ya da kod bloğuna sarar. Bunlar biçim hatasıdır, içerik hatası değil;
    tüm özeti düşürmek yerine JSON gövdesini kurtarmayı deniyoruz.

    NEDEN SINIRLI TOLERANS: Gövde bulunamıyorsa uydurma bir yapı ÜRETMİYORUZ.
    Ayrıştırılamayan çıktı boş özet demektir; kullanıcıya yanlış veri
    göstermektense hiçbir şey göstermemek doğrudur (İlke 2).
    """
    temiz = _CODE_FENCE_RE.sub("", raw.strip())
    try:
        return json.loads(temiz)
    except json.JSONDecodeError:
        pass
    # İlk '{' ile son '}' arasını denemek: açıklama cümlesiyle sarılmış JSON.
    ilk, son = temiz.find("{"), temiz.rfind("}")
    if ilk != -1 and son > ilk:
        try:
            return json.loads(temiz[ilk : son + 1])
        except json.JSONDecodeError:
            return None
    return None


def audit_citations(raw_output: str, allowed_ids: set[str]) -> AuditReport:
    """Model çıktısını atıf kurallarına göre denetler.

    Args:
        raw_output: LLM'in ham metin çıktısı (JSON bekleniyor).
        allowed_ids: Prompt'a GERÇEKTEN verilmiş gönderi ID'leri. Bu küme
            dışındaki her ID uydurmadır.

    Returns:
        AuditReport — yalnızca denetimden geçen cümleler ve sayaçlar.
    """
    rapor = AuditReport()
    veri = parse_llm_json(raw_output)
    if not isinstance(veri, dict) or not isinstance(veri.get("sentences"), list):
        rapor.parse_failed = True
        logger.warning("Birleştirme çıktısı ayrıştırılamadı; özet boş döndürülüyor.")
        return rapor

    for ham_cumle in veri["sentences"]:
        if not isinstance(ham_cumle, dict):
            rapor.dropped_empty_text += 1
            continue
        metin = str(ham_cumle.get("text", "")).strip()
        kaynaklar = ham_cumle.get("source_post_ids") or []
        if not isinstance(kaynaklar, list):
            kaynaklar = []

        if not metin:
            rapor.dropped_empty_text += 1
            continue

        temiz_kaynaklar = [str(k).strip() for k in kaynaklar if str(k).strip()]
        if not temiz_kaynaklar:
            # İlke 1: kaynağı boş dönen cümle çıktıdan silinir.
            rapor.dropped_empty_source += 1
            logger.info("Atıfsız cümle silindi: %s", metin[:60])
            continue

        gecerli = [k for k in temiz_kaynaklar if k in allowed_ids]
        uydurma = [k for k in temiz_kaynaklar if k not in allowed_ids]
        if uydurma:
            rapor.hallucinated_ids.extend(uydurma)
            logger.info("Uydurma kaynak ID'leri: %s", uydurma)

        if not gecerli:
            # Tüm kaynaklar uydurma: cümle tamamen dayanaksız.
            rapor.dropped_unknown_id += 1
            continue

        # Kısmi uydurma durumunda geçerli ID'lerle devam ediyoruz: cümlenin
        # dayanağı vardır, yalnızca fazladan ID uydurulmuştur. Fazlalık atılır.
        rapor.sentences.append(SummarySentence(text=metin, source_post_ids=gecerli))

    return rapor
