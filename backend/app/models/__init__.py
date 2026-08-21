"""Pydantic şemaları — servis katmanının veri sözleşmesi.

Buradaki tipler hem API yanıtlarını hem de modüller arası veri akışını tanımlar.
Şemaların tek yerde toplanmasının sebebi: MİHENK'in üç ilkesi (atıf, çekimserlik,
çoğulculuk) büyük ölçüde veri şekliyle zorlanıyor. Örneğin SummarySentence'ın
source_post_ids alanı boş olamaz — bu bir doğrulayıcı ile garanti altına alınmıştır,
yani İlke 1 sadece bir konvansiyon değil, tip sisteminin parçasıdır.
"""

from app.models.assistant import AssistantResponse, RefusalReason
from app.models.detection import DetectionLabel, DetectionResult, LengthBucket
from app.models.enriched import EnrichedPost
from app.models.post import EVAL_FIELD_PREFIX, MediaRef, Post, PostCategory
from app.models.summary import SummaryResponse, SummarySentence

__all__ = [
    "EVAL_FIELD_PREFIX",
    "AssistantResponse",
    "DetectionLabel",
    "DetectionResult",
    "EnrichedPost",
    "LengthBucket",
    "MediaRef",
    "Post",
    "PostCategory",
    "RefusalReason",
    "SummaryResponse",
    "SummarySentence",
]
