"""Doğrulama ajanı — P1 (kavram kanıtı) → P2 (tam sürüm). Spec 6.7.

DURUM: Bu modülde henüz çalışan kod yoktur. `schema.py` içindeki tipler ve
buradaki tasarım notu, P1'de yazılacak uygulamanın sözleşmesidir. Boş bir
klasör bırakmak yerine sözleşmeyi yazıyoruz: raporda İP olarak planlanan işin
ne olduğu kodda görünür olmalı, aksi halde iddia boşta kalır.

--- TASARIM ---------------------------------------------------------------

ÇIKTI ÜÇ DURUMLUDUR, ASLA KESİN HÜKÜM DEĞİLDİR:
    DESTEKLEYEN / CELISEN / KAYNAK_YOK
`DOGRU` veya `YANLIS` diye bir durum yoktur (İlke 3). Bir iddianın doğruluğuna
karar vermek bu sistemin işi değildir; kaynakların ne söylediğini göstermek
işidir.

AJAN DÖNGÜSÜ:
    plan → araç seç → çalıştır → kaynakları denetle → üç durumlu çıktı

DEĞİŞMEZ KISITLAR (hepsi güvenlik gereği, hiçbiri isteğe bağlı değil):
  1. Adım sayısı `config.agent_max_steps` ile sınırlıdır (sonsuz döngü koruması).
  2. Ajanın YAZMA YETKİSİ YOKTUR. Yalnızca okur ve kaynak gösterir.
  3. Yalnızca `config.allowed_domains` içindeki kaynaklara gider (izin listesi).
  4. Her araç çağrısı loglanır (denetlenebilirlik).
  5. Web'den çekilen metin GÜVENİLMEYEN GİRDİDİR: gönderi metniyle aynı
     savunma zincirinden geçer (sanitize → prompt_guard → output_guard).
     Kaynak zehirleme, ajan akışının birincil tehdididir (bkz.
     docs/TEHDIT_MODELI.md bölüm 7).
  6. Uzun alıntı yapılmaz; kendi cümlesiyle özetlenir ve kaynağa link verilir
     (telif — spec 2, madde 5).

ÇELİŞKİ DURUMU: Kaynaklar birbiriyle çelişiyorsa `CELISEN` döner ve
`disagreement_note` alanında çelişkinin ne olduğu açıklanır. Çelişkiyi
"çözmek" — yani bir tarafı seçmek — açıkça yasaktır.

P1 HEDEFİ: Tek senaryo uçtan uca çalışsın, yeterli.
P2 HEDEFİ: Çok kaynaklı toplama + kaynak itibar puanlaması.
"""

from app.agent.schema import SourceRef, VerificationResult, VerificationStatus

__all__ = ["SourceRef", "VerificationResult", "VerificationStatus"]
