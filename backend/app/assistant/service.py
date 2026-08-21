"""Gönderi asistanı — bağlam sınırlı soru-cevap (spec 6.3).

BAĞLAM SINIRI: gönderi + alıntı zinciri + doğrudan yanıtlar. Bunun dışına
çıkılmaz. Model genel bilgisini kullanmaz; kullanırsa cevap kaynağa
bağlanamaz ve İlke 1 çiğnenir.

BEŞ KAPI (hepsi geçilmeden yanıt kullanıcıya ulaşmaz):
  1. Soru enjeksiyon sinyali taşıyor mu?        -> reddet (enjeksiyon_supheli)
  2. Model bağlamda cevap bulamadı mı?          -> reddet (baglamda_yok)
  3. Yanıt URL/komut/talimat içeriyor mu?       -> reddet (cikti_kisiti)
  4. Yanıtın kaynağı bağlamda gerçekten var mı? -> reddet (atifsiz)
  5. Kelime sınırı                              -> kırp

REDDETME BİR HATA DEĞİL, ÖLÇÜLEN BİR DAVRANIŞTIR: "bağlam dışı soruda doğru
reddetme oranı" raporun Tablo 5'inde yer alır (spec 7).
"""

from __future__ import annotations

import json
import logging
import time

from app.config import config
from app.llm.prompts import REFUSAL_TOKEN, assistant_prompt
from app.llm.provider import get_provider
from app.models import AssistantResponse, Post
from app.security.output_guard import check_output
from app.security.sanitize import sanitize
from app.store.feed_repo import FeedRepository
from app.summarize.citation import parse_llm_json
from app.textutil import truncate_words

logger = logging.getLogger(__name__)

# Soruda görüldüğünde asistanın doğrudan reddettiği kalıp aileleri.
# NEDEN SADECE BU ÜÇÜ: Kullanıcının kendi asistanına "önceki talimatları yoksay"
# demesi meşru bir soru değildir. Buna karşılık "eylem_talebi" gibi kalıplar
# masum bir soruda da geçebilir (örn. "bu linke tıklamalı mıyım?"), o yüzden
# reddetme listesine alınmadı — onları çıktı kısıtı zaten yakalar.
_RED_KALIPLARI = frozenset({"dogrudan_talimat", "rol_degistirme", "sistem_sizdirma"})

# Bağlama alınacak en fazla yanıt sayısı. Sınırsız yanıt zinciri hem prompt'u
# şişirir hem de saldırı yüzeyini büyütür (her yanıt güvenilmeyen girdidir).
MAX_YANIT = 5


def build_context(repo: FeedRepository, post_id: str) -> list[Post]:
    """Asistanın görebileceği gönderi kümesini kurar.

    Sıra anlamlıdır: önce gönderinin kendisi, sonra alıntı zinciri (eskiye
    doğru), sonra doğrudan yanıtlar. Model, ilk sırayı ana konu olarak okur.
    """
    ana = repo.get(post_id)
    if ana is None:
        return []
    baglam = [ana]
    baglam.extend(repo.quote_chain(post_id))
    baglam.extend(repo.replies_to(post_id)[:MAX_YANIT])
    return baglam


def ask(repo: FeedRepository, post_id: str, question: str | None = None) -> AssistantResponse:
    """Gönderi bağlamında soruyu yanıtlar.

    Args:
        repo: Akış deposu.
        post_id: Bağlamın merkezindeki gönderi.
        question: Kullanıcının sorusu. None ise "bu gönderi ne diyor" varsayılır.

    Returns:
        AssistantResponse — reddetme durumunda `refused=True` ve gerekçe.
    """
    baslangic = time.perf_counter()

    def _sonuc(**alanlar) -> AssistantResponse:
        return AssistantResponse(
            latency_ms=int((time.perf_counter() - baslangic) * 1000), **alanlar
        )

    baglam = build_context(repo, post_id)
    if not baglam:
        return _sonuc(
            answer="Bu gönderi bulunamadı.", refused=True, refusal_reason="baglamda_yok"
        )

    soru = (question or "").strip()

    # --- Kapı 1: soruda enjeksiyon sinyali ---
    if soru:
        sinyal = sanitize(soru)
        if set(sinyal.patterns) & _RED_KALIPLARI or sinyal.had_invisible:
            logger.info("Asistan sorusu reddedildi post=%s kalıplar=%s", post_id, sinyal.patterns)
            return _sonuc(
                answer=(
                    "Bu isteği yerine getiremem. Yalnızca gönderinin içeriğiyle "
                    "ilgili sorulara yanıt veriyorum."
                ),
                refused=True,
                refusal_reason="enjeksiyon_supheli",
            )

    system, user = assistant_prompt([(p.id, p.text) for p in baglam], soru)
    try:
        ham = get_provider().complete(system, user, max_tokens=400)
    except Exception as hata:
        logger.error("Asistan çağrısı başarısız post=%s: %s", post_id, hata)
        return _sonuc(
            answer="Şu anda yanıt üretemiyorum.", refused=True, refusal_reason="baglamda_yok"
        )

    veri = parse_llm_json(ham)
    if not isinstance(veri, dict):
        # Ayrıştırılamayan çıktıyı serbest metin olarak GÖSTERMİYORUZ: kaynağı
        # doğrulanamayan bir yanıt İlke 1'i çiğner.
        logger.warning("Asistan çıktısı ayrıştırılamadı post=%s", post_id)
        return _sonuc(
            answer="Bu gönderiden çıkarılamıyor.", refused=True, refusal_reason="atifsiz"
        )

    cevap = str(veri.get("answer", "")).strip()
    kaynaklar = [str(k).strip() for k in (veri.get("source_post_ids") or []) if str(k).strip()]

    # --- Kapı 2: model bağlamda cevap bulamadı ---
    if not cevap or cevap == REFUSAL_TOKEN:
        return _sonuc(
            answer="Bu gönderiden çıkarılamıyor.", refused=True, refusal_reason="baglamda_yok"
        )

    # --- Kapı 3: çıktı kısıtı (URL / komut / talimat / sistem sızıntısı) ---
    denetim = check_output(cevap)
    if not denetim.allowed:
        logger.warning("Asistan yanıtı çıktı kısıtına takıldı post=%s ihlal=%s", post_id, denetim.violation)
        return _sonuc(
            answer="Bu isteğe güvenli bir yanıt üretemedim.",
            refused=True,
            refusal_reason="cikti_kisiti",
        )

    # --- Kapı 4: atıf denetimi (İlke 1) ---
    izinli = {p.id for p in baglam}
    gecerli = [k for k in kaynaklar if k in izinli]
    if not gecerli:
        logger.info("Asistan yanıtı atıfsız/uydurma kaynaklı post=%s kaynaklar=%s", post_id, kaynaklar)
        return _sonuc(
            answer="Bu gönderiden çıkarılamıyor.", refused=True, refusal_reason="atifsiz"
        )

    # --- Kapı 5: kelime sınırı ---
    return _sonuc(
        answer=truncate_words(cevap, config.max_assistant_words),
        source_post_ids=gecerli,
    )
