"""Değerlendirme alanlarının sızmadığını garanti eden testler (spec 5.1 / 8).

`_eval_*` alanları "doğru cevap"tır. Servis katmanına veya prompt'a sızarlarsa
tüm ölçüm geçersiz olur: model tespit etmiş gibi görünür ama cevabı okumuştur.
Bu, jürinin sorabileceği en can alıcı sorulardan biridir — bu yüzden testle
kanıtlanır, iyi niyete bırakılmaz.
"""

from __future__ import annotations

import json

from app.enrichment import enrich_feed, get_enriched
from app.llm.prompts import assistant_prompt, atomic_summary_prompt, merge_prompt
from app.models import EVAL_FIELD_PREFIX, Post
from app.store.feed_repo import load_feed
from app.summarize import summarize

# Değerlendirme alanlarının adları — prompt metninde hiçbiri geçmemeli.
EVAL_ALAN_ADLARI = (
    "_eval_is_ai_generated",
    "_eval_is_manipulative",
    "_eval_has_injection",
    "_eval_event_id",
    "_eval_length_bucket",
    "eval_is_ai_generated",
    "eval_has_injection",
)


def test_to_service_dict_eval_alanlarini_dislar(post_uret):
    """Servis sözlüğünde hiçbir değerlendirme alanı bulunmamalı."""
    post = post_uret(
        "p1",
        "metin",
        _eval_is_ai_generated=True,
        _eval_has_injection=True,
        _eval_event_id="olay_1",
    )
    servis = post.to_service_dict()
    assert not any(k.startswith(EVAL_FIELD_PREFIX) for k in servis)
    assert "text" in servis and "id" in servis


def test_prompt_metinlerinde_eval_alani_gecmez(post_uret):
    """Üç prompt üreticisinin hiçbiri değerlendirme alanı sızdırmaz."""
    post = post_uret(
        "p1",
        "Köprü açılışı ertelendi, esnaf tepkili.",
        _eval_is_ai_generated=True,
        _eval_is_manipulative=True,
        _eval_has_injection=True,
        _eval_event_id="olay_kopru",
    )

    promptlar = [
        atomic_summary_prompt(post.id, post.text),
        merge_prompt("gundem", [("ulasim", [(post.id, post.text)])], pluralism_required=True),
        assistant_prompt([(post.id, post.text)], "Ne oldu?"),
    ]
    for system, user in promptlar:
        birlesik = f"{system}\n{user}"
        for alan in EVAL_ALAN_ADLARI:
            assert alan not in birlesik, f"prompt'ta değerlendirme alanı geçiyor: {alan}"
        assert "olay_kopru" not in birlesik, "olay kimliği prompt'a sızdı"


def test_zenginlestirme_ciktisi_eval_alani_tasimaz(kucuk_akis, post_uret):
    """EnrichedPost şemasında değerlendirme alanı yoktur ve önbelleğe yazılmaz."""
    etiketli = post_uret("px", "Köprü açılışı ertelendi ve esnaf tepkili.", _eval_is_ai_generated=True)
    enrich_feed([etiketli])
    kayit = get_enriched("px")
    assert kayit is not None
    seri = json.dumps(kayit.model_dump(mode="json"), ensure_ascii=False)
    for alan in EVAL_ALAN_ADLARI:
        assert alan not in seri


def test_ozet_yaniti_eval_alani_tasimaz(kucuk_akis):
    """Kullanıcıya dönen özet yanıtında değerlendirme alanı bulunmaz."""
    enrich_feed(kucuk_akis.posts)
    yanit, _ = summarize("u1", "gundem", [p.id for p in kucuk_akis.posts])
    seri = json.dumps(yanit.model_dump(mode="json"), ensure_ascii=False)
    for alan in EVAL_ALAN_ADLARI:
        assert alan not in seri


def test_sentetik_akis_dosyasinda_eval_alanlari_var():
    """Ters kontrol: alanlar VERİ tarafında gerçekten duruyor olmalı.

    Sızıntı testi, alanlar hiç üretilmediği için de yeşile dönebilirdi. Bu test
    o yanılsamayı engeller: veri dosyasında etiketler vardır, sızmayan şey
    onların servise taşınmasıdır.
    """
    depo = load_feed()
    etiketli = [p for p in depo.posts if p.eval_is_ai_generated]
    enjeksiyonlu = [p for p in depo.posts if p.eval_has_injection]
    assert etiketli, "akışta YZ etiketli gönderi yok"
    assert enjeksiyonlu, "akışta enjeksiyon etiketli gönderi yok"
    assert isinstance(etiketli[0], Post)
