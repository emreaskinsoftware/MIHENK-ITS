"""İlke 3 — çoğulculuk testleri (spec 1 / 6.2).

İki güvence:
  1. Tek kaynaktan beslenen küme için gündem özeti ÜRETİLMEZ.
  2. Gündem prompt'u doğruluk hükmü vermeyi yasaklar ve taraf pozisyonlarını
     belirtmeyi zorunlu kılar.
"""

from __future__ import annotations

from app.enrichment import enrich_feed
from app.llm.prompts import merge_prompt
from app.summarize import summarize
from app.summarize.clustering import Cluster
from app.summarize.service import _kume_secimi


def _kume(etiket: str, yazarlar: list[str]) -> Cluster:
    """Verilen yazarlara sahip sahte küme üretir (gömme gerekmeden)."""
    from datetime import datetime, timezone

    from app.models import EnrichedPost

    uyeler = [
        EnrichedPost(
            post_id=f"{etiket}-{i}",
            author_id=yazar,
            atomic_summary="özet",
            embedding=[1.0, 0.0],
            topic_label=etiket,
            enriched_at=datetime.now(timezone.utc),
        )
        for i, yazar in enumerate(yazarlar)
    ]
    return Cluster(label=etiket, members=uyeler)


def test_tek_yazarli_kume_gundemde_bastirilir():
    """Tek kaynaktan beslenen küme gündem özetine giremez."""
    kumeler = [_kume("tek", ["@a", "@a", "@a"]), _kume("cok", ["@a", "@b", "@c"])]
    secilen, bastirilan = _kume_secimi(kumeler, pluralism_required=True)
    assert [k.label for k in secilen] == ["cok"]
    assert bastirilan == ["tek"]


def test_kisisel_akista_tek_yazar_kurali_uygulanmaz():
    """Kişisel akış gündem değildir; tek yazarlı küme orada meşrudur.

    NEDEN: Çoğulculuk kuralı kamusal iddialar içindir. Kullanıcının kendi
    takip ettiği kişinin gönderilerini özetlemek bir hüküm üretmez.
    """
    kumeler = [_kume("tek", ["@a", "@a"])]
    secilen, bastirilan = _kume_secimi(kumeler, pluralism_required=False)
    assert len(secilen) == 1
    assert bastirilan == []


def test_gundem_prompt_dogruluk_hukmu_yasaklar():
    """Gündem prompt'u 'doğru/yanlış' hükmünü açıkça yasaklamalı."""
    system, _ = merge_prompt("gundem", [("ulasim", [("p1", "özet")])], pluralism_required=True)
    metin = system.lower()
    assert "çoğulculuk" in metin
    assert "doğruluk hükmü" in metin
    assert "hangi tarafın haklı" in metin


def test_spor_ve_kisisel_promptunda_cogulculuk_zorunlu_degil():
    """Çoğulculuk dili yalnızca gündem kategorisinde zorunludur."""
    system, _ = merge_prompt("kisisel", [("gundelik", [("p1", "özet")])], pluralism_required=False)
    assert "ÇOĞULCULUK" not in system


def test_tek_kaynakli_olay_uctan_uca_ozete_girmez(kucuk_akis):
    """Uçtan uca: tek yazarlı 'pazar yeri' olayı gündem özetine girmemeli."""
    enrich_feed(kucuk_akis.posts)
    yanit, hata_ayikla = summarize("u1", "gundem", [p.id for p in kucuk_akis.posts])

    tek_yazarli_idler = {"p6", "p7"}
    kullanilan = {kaynak for c in yanit.sentences for kaynak in c.source_post_ids}
    assert not (kullanilan & tek_yazarli_idler), "tek kaynaklı olay özete sızdı"
    assert yanit.single_source_cluster_count >= 1
    assert hata_ayikla.suppressed_single_author_labels
