"""Prompt şablonları — tüm LLM çağrılarının tek kaynağı.

NEDEN TEK DOSYA: Prompt'lar bu projede güvenlik yüzeyidir. Modüllere dağılmış
f-string'ler, güvenlik başlığını (GUVENLIK_BASLIGI) unutan bir çağrı riski
yaratır. Burada toplayarak her prompt'un yapısal ayrım kuralından geçmesini
garanti ediyoruz (spec 6.4).

Ayrıca prompt'lar makine tarafından okunabilir bir GÖREV etiketi taşır
(`GOREV: BIRLESTIRME` gibi). Bu etiket iki işe yarar:
  1. FakeProvider (llm/fake.py) hangi görevi taklit edeceğini anlar; böylece
     tüm hat API anahtarı olmadan uçtan uca çalışır ve test edilebilir.
  2. Loglarda çağrı türü ayrıştırılabilir (maliyet tablosu, spec 7).
"""

from __future__ import annotations

from app.config import config
from app.security.prompt_guard import GUVENLIK_BASLIGI, wrap_posts, wrap_untrusted

# --- Görev etiketleri (FakeProvider bunlara bakar) ---
TASK_ATOMIC = "ATOMIK_OZET"
TASK_MERGE = "BIRLESTIRME"
TASK_ASSISTANT = "ASISTAN"

# Asistanın bağlamda cevap bulamadığında döndüreceği sabit işaret.
# NEDEN SABİT DİZGE: Modelin "bilmiyorum" ifadesini serbest metinden çıkarmaya
# çalışmak kırılgandır; sabit bir işaret çekimserliği makine tarafından
# ayrıştırılabilir kılar (İlke 2 ölçülebilir olmalı).
REFUSAL_TOKEN = "BAGLAMDA_YOK"


# ----------------------------------------------------------------------
# KATMAN 1 — atomik özet
# ----------------------------------------------------------------------
def atomic_summary_prompt(post_id: str, text: str) -> tuple[str, str]:
    """Tek gönderi için atomik özet prompt'u üretir.

    Returns:
        (system, user) ikilisi.
    """
    system = (
        "Sen bir sosyal medya gönderisini kendi cümlelerinle özetleyen bir "
        f"yardımcısın. {GUVENLIK_BASLIGI}\n\n"
        "KURALLAR:\n"
        f"- En fazla {config.atomic_summary_max_sentences} cümle, "
        f"en fazla {config.atomic_summary_max_words} kelime.\n"
        "- Gönderide OLMAYAN hiçbir bilgi ekleme.\n"
        "- Yorum yapma, taraf tutma, değerlendirme cümlesi kurma.\n"
        "- Yalnızca özet metnini yaz; başlık, tırnak veya açıklama ekleme."
    )
    user = f"GOREV: {TASK_ATOMIC}\n\n{wrap_untrusted(text, label=f'GONDERI:{post_id}')}"
    return system, user


# ----------------------------------------------------------------------
# KATMAN 2 — küme birleştirme (atıflı özet)
# ----------------------------------------------------------------------
def merge_prompt(
    category: str,
    clusters: list[tuple[str, list[tuple[str, str]]]],
    *,
    pluralism_required: bool,
) -> tuple[str, str]:
    """Küme temsilcilerinden atıflı özet isteyen prompt'u üretir.

    Args:
        category: "gundem" | "spor" | "kisisel".
        clusters: (küme_etiketi, [(post_id, atomik_özet), ...]) listesi.
        pluralism_required: Gündem kategorisinde True. İlke 3 gereği tek doğru
            dayatmayan, taraf pozisyonlarını belirten dil istenir.

    NEDEN TEK ÇAĞRI: Spec 4.1 — kullanıcı beklerken yapılan tek pahalı iş budur.
    Kümelerin tamamı tek prompt'ta gider, her küme için ayrı çağrı yapılmaz.
    """
    cogulculuk = (
        "\n- ÇOĞULCULUK (zorunlu): Bir olay hakkında farklı görüşler varsa "
        "hepsini konumlandırarak yaz: 'bir grup şunu söylüyor, diğerleri bunu "
        "söylüyor'. ASLA hangi tarafın haklı olduğunu söyleme, doğruluk hükmü "
        "verme, 'yanlış/doğru' deme."
        if pluralism_required
        else ""
    )
    system = (
        "Sen okunmamış sosyal medya gönderilerinden kaynak gösteren bir gündem "
        f"özeti çıkaran bir yardımcısın. {GUVENLIK_BASLIGI}\n\n"
        "ÇIKTI BİÇİMİ: Yalnızca geçerli JSON döndür, başka hiçbir metin yazma:\n"
        '{"sentences": [{"text": "...", "source_post_ids": ["p12", "p45"]}]}\n\n'
        "KURALLAR:\n"
        "- Her cümle, dayandığı gönderilerin ID'lerini source_post_ids içinde "
        "taşımak ZORUNDA. Kaynağını gösteremeyeceğin cümleyi hiç yazma.\n"
        "- Kullanabileceğin ID'ler yalnızca veri bloğunda [GONDERI:...] olarak "
        "verilenlerdir. Var olmayan ID uydurma.\n"
        f"- Toplam en fazla {config.max_summary_words} kelime.\n"
        "- Her küme için en fazla bir cümle yaz.\n"
        "- Gönderilerde olmayan bilgi ekleme, tahmin yürütme." + cogulculuk
    )

    bloklar: list[str] = []
    for etiket, temsilciler in clusters:
        bloklar.append(f"### KUME: {etiket}")
        bloklar.append(wrap_posts(temsilciler))
    user = f"GOREV: {TASK_MERGE}\nKATEGORI: {category}\n\n" + "\n".join(bloklar)
    return system, user


# ----------------------------------------------------------------------
# Gönderi asistanı
# ----------------------------------------------------------------------
def assistant_prompt(context: list[tuple[str, str]], question: str) -> tuple[str, str]:
    """Gönderi bağlamıyla sınırlı soru-cevap prompt'u üretir.

    Args:
        context: (post_id, metin) — gönderi + alıntı zinciri + doğrudan yanıtlar.
        question: Kullanıcının sorusu.

    NEDEN SORU DA SARILIYOR: Soru kullanıcıdan gelir ve kullanıcı da kendi
    asistanına enjeksiyon deneyebilir ("sistem talimatını yaz"). Soruyu da veri
    olarak işaretliyoruz.
    """
    system = (
        "Sen yalnızca sana verilen gönderi bağlamına dayanarak soru cevaplayan "
        f"bir yardımcısın. {GUVENLIK_BASLIGI}\n\n"
        "ÇIKTI BİÇİMİ: Yalnızca geçerli JSON döndür:\n"
        '{"answer": "...", "source_post_ids": ["p12"]}\n'
        f'Cevap bağlamda YOKSA: {{"answer": "{REFUSAL_TOKEN}", "source_post_ids": []}}\n\n'
        "KURALLAR:\n"
        "- Bağlam dışına ASLA çıkma. Genel bilgi, tahmin, yorum ekleme.\n"
        f"- En fazla {config.max_assistant_words} kelime.\n"
        "- Bağlantı (URL) verme, kullanıcı adına eylem önerme.\n"
        "- Cevabın dayandığı gönderi ID'lerini source_post_ids içinde ver."
    )
    user = (
        f"GOREV: {TASK_ASSISTANT}\n\n"
        f"BAGLAM:\n{wrap_posts(context)}\n\n"
        f"SORU:\n{wrap_untrusted(question, label='KULLANICI_SORUSU')}"
    )
    return system, user
