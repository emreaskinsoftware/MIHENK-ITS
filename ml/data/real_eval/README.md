# Gerçek metin ölçüm kümesi

Bu klasör, sentetik değerlendirmenin **kapalı döngüsünü** kırmak için kurulan
ölçüm kümesini üretir. Sentetik tespit veri setinde iki sınıfı da biz yazdık:
"insan" sınıfı gerçek bir insanın metni değil, *"insan böyle yazar"*
hipotezimizin taklidi. Bu küme iki tarafı da gerçek yapar.

| Sınıf | Kaynak |
|---|---|
| `insan` | Gerçek müşteri yorumları — `turkish-nlp-suite/vitamins-supplements-reviews` |
| `yapay_zeka` | Claude Opus 5 çıktısı, insan örneklemiyle eşleştirilerek üretildi |

## Depoda ne var, ne yok

| Dosya | Depoda? | Neden |
|---|---|---|
| `ai_raw.jsonl` | **var** | Bizim ürettiğimiz metinler; yeniden üretilemez, korunmalı |
| `_kaynak_yorumlar.parquet` | yok | 13 MB üçüncü taraf derlem; betik indiriyor |
| `gen_brief.json` | yok | İçinde insan metinleri var (bkz. lisans) |
| `dataset.jsonl` | yok | İçinde insan metinleri var (bkz. lisans) |

**Lisans gerekçesi:** İnsan tarafı CC BY-SA 4.0 lisanslıdır. Metinleri depoya
koyup dağıtmak paylaşımlı-lisans (share-alike) yükümlülüğü doğururdu. Bunun
yerine yeniden üretilebilirliği betikle sağlıyoruz: aynı tohum, aynı derlem,
aynı örneklem.

## Yeniden üretmek

```bash
python ml/scripts/build_real_eval.py --brief      # derlemi indirir, örnekler
python ml/scripts/build_real_eval.py --assemble   # ai_raw.jsonl ile birleştirir
python ml/scripts/evaluate_real.py                # eval/results/real_text.md
```

## Atıf

İnsan tarafı:

> Duygu Altinok. 2023. *A Diverse Set of Freely Available Linguistic Resources
> for Turkish.* Proceedings of the 61st Annual Meeting of the Association for
> Computational Linguistics, 13739–13750.
> <https://aclanthology.org/2023.acl-long.768/>

Derlem CC BY-SA 4.0 ile yayımlanmıştır. Derlemi hazırlayanlar kişi adlarını
(müşteri ve tanıtıcı adları) önceden temizlemiştir.

**Köken güvenilirliği:** Derlem 2022'de, dil modelleri yaygınlaşmadan önce
toplanmıştır. 2023 sonrası toplanmış bir web derlemi zaten yapay zekâ metni
içerebilir ve onu "insan" diye etiketlemek veri setini sessizce zehirlerdi.
Yine de tek tek her yorumun insan yazımı olduğu kanıtlanamaz; bu bir
sınırlılıktır.

## Bu küme EĞİTİM için kullanılmaz

Yapay zekâ tarafı tek bir üreticiden geliyor. Bu kümede eğitilen bir model
"yapay zekâ tespiti" değil "Claude tespiti" yapar. Buradaki kullanım yalnızca
**ölçümdür**: modeller sentetik veriyle eğitildi, bu küme onlara hiç
gösterilmedi. Genellenebilir bir iddia için en az üç üretici gerekir ve
bunlardan biri sınava saklanmalıdır (`ml/scripts/seed_variance.py` içindeki
saklanan-tohum mantığının üretici karşılığı).
