"""İlke 1 — atıf zorunluluğu testleri (spec 1 / 6.2 / 8).

Bu testler projenin ana tezini korur. Biri kırmızıya dönerse ürün, "söylediği
her cümleyi kaynağına bağlar" iddiasını kaybeder.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from app.enrichment import enrich_feed
from app.llm.fake import HallucinatingFakeProvider
from app.llm.provider import get_provider
from app.models import SummarySentence
from app.summarize import audit_citations, summarize


def test_kaynaksiz_cumle_olusturulamaz():
    """Tip düzeyinde koruma: kaynaksız SummarySentence yaratılamaz."""
    with pytest.raises(ValidationError):
        SummarySentence(text="Kaynaksız iddia.", source_post_ids=[])
    with pytest.raises(ValidationError):
        # Boş dizgelerden oluşan liste de atıf sayılmaz.
        SummarySentence(text="Kaynaksız iddia.", source_post_ids=["", "   "])


def test_atifsiz_cumle_silinir():
    """Denetim, kaynağı boş dönen cümleyi çıktıdan siler."""
    ham = json.dumps(
        {
            "sentences": [
                {"text": "Kaynaklı cümle.", "source_post_ids": ["p1"]},
                {"text": "Kaynaksız cümle.", "source_post_ids": []},
            ]
        }
    )
    rapor = audit_citations(ham, allowed_ids={"p1", "p2"})
    assert len(rapor.sentences) == 1
    assert rapor.sentences[0].text == "Kaynaklı cümle."
    assert rapor.dropped_empty_source == 1
    assert rapor.dropped_total == 1


def test_uydurma_kaynakli_cumle_silinir():
    """Girdi kümesinde olmayan ID gösteren cümle silinir."""
    ham = json.dumps(
        {"sentences": [{"text": "Uydurma kaynak.", "source_post_ids": ["p_yok_1"]}]}
    )
    rapor = audit_citations(ham, allowed_ids={"p1"})
    assert rapor.sentences == []
    assert rapor.dropped_unknown_id == 1
    assert "p_yok_1" in rapor.hallucinated_ids


def test_kismi_uydurma_kaynakta_gecerli_idler_kalir():
    """Cümlenin bir dayanağı varsa cümle kalır, uydurma ID atılır.

    NEDEN BÖYLE: Cümle gerçekten p1'e dayanıyorsa onu silmek bilgi kaybıdır.
    Ama kullanıcıya gösterilen kaynak çipleri yalnızca doğrulanmış ID'leri
    içermelidir; uydurma çip, kullanıcıyı var olmayan bir gönderiye yollar.
    """
    ham = json.dumps(
        {"sentences": [{"text": "Karma kaynak.", "source_post_ids": ["p1", "hayali"]}]}
    )
    rapor = audit_citations(ham, allowed_ids={"p1"})
    assert len(rapor.sentences) == 1
    assert rapor.sentences[0].source_post_ids == ["p1"]
    assert "hayali" in rapor.hallucinated_ids


def test_ayristirilamayan_cikti_bos_ozet_uretir():
    """Bozuk JSON serbest metin olarak gösterilmez; özet boş döner."""
    rapor = audit_citations("Buyurun özetiniz: ...", allowed_ids={"p1"})
    assert rapor.parse_failed is True
    assert rapor.sentences == []


def test_uydurma_saglayici_ile_uctan_uca_denetim(kucuk_akis, monkeypatch):
    """Kasten uydurma yapan sağlayıcıyla bile çıktı temiz kalır.

    Bu test denetimin GERÇEKTEN çalıştığını gösterir: sağlayıcı iki bozuk cümle
    ekler, ikisi de kullanıcıya ulaşmaz ve sayaç artar.
    """
    enrich_feed(kucuk_akis.posts)
    monkeypatch.setattr(
        "app.llm.provider.get_provider", lambda force=None: HallucinatingFakeProvider()
    )
    monkeypatch.setattr("app.summarize.service.get_provider", lambda: HallucinatingFakeProvider())

    yanit, _ = summarize("u1", "gundem", [p.id for p in kucuk_akis.posts])

    assert yanit.dropped_sentence_count >= 2, "bozuk cümleler silinmedi"
    for cumle in yanit.sentences:
        assert cumle.source_post_ids, "atıfsız cümle kullanıcıya ulaştı"
        for kaynak in cumle.source_post_ids:
            assert kaynak in {p.id for p in kucuk_akis.posts}, "uydurma kaynak sızdı"
    _ = get_provider  # içe aktarımın kullanıldığını belirtmek için
