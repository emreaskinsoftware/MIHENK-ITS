# Tablo 4 — YZ Metin Tespiti

> `ml/scripts/evaluate.py` tarafından üretilir. Elle düzenlenmez.

Test kümesi: **245** örnek (YZ 132, insan 113). Bölme şablon-ayrıktır: test örnekleri eğitimde görülmemiş kalıplardan gelir.

## Genel başarım

| Model | Doğruluk | F1 | AUROC | **FPR@95TPR** |
|---|---|---|---|---|
| TF-IDF temel çizgi | 0.984 | 0.985 | 1.000 | **0.000** |

FPR@95TPR en kritik metriktir: YZ metinlerinin %95'ini yakalayacak eşikte
kaç insan metninin haksız yere etiketlendiğini gösterir.

## Uzunluk kovası bazında doğruluk

| Model | K1 (0-50 token) | K2 (50-100) | K3 (100+) |
|---|---|---|---|
| TF-IDF temel çizgi | 0.959 | 1.000 | 0.989 |

## Çekimserlik (İlke 2)

Eşikler: `min_detection_tokens=20`, belirsizlik bandı `[0.35, 0.65]`.

| Model | Çekimserlik oranı | K1 | K2 | K3 | Etiketlenen örnek | Etiketlendiğinde doğruluk |
|---|---|---|---|---|---|---|
| TF-IDF temel çizgi | 17.1% | 6.8% | 16.5% | 26.1% | 203/245 | 1.000 |

Çekimserlik bir hata değil, ürün davranışıdır: sistem emin olmadığında
hiçbir rozet göstermez. Son sütun, gösterdiği etiketlerin ne kadar
güvenilir olduğunu verir — kullanıcının gördüğü tek sayı budur.

## Aktarım testi — farklı kaynaktan gelen metinler

Yukarıdaki test kümesi, modelin eğitildiği şablon havuzundan gelir
(farklı şablon grupları, ama aynı kalem). Aşağıdaki ölçüm ise
**sosyal medya akışı üretecinden** (`generate_feed.py`) gelen ve tespit
veri setiyle hiçbir şablon paylaşmayan gönderiler üzerindedir.
**Rapora girecek asıl sayı budur**: kendi yazdığımız test kümesindeki
başarım, sınıfları biz tasarladığımız için yapay olarak yüksektir.

Aktarım kümesi: **413** gönderi (YZ 75, insan 338).

| Model | Doğruluk | F1 | AUROC | FPR@95TPR | K1 | K2 | K3 | Çekimserlik |
|---|---|---|---|---|---|---|---|---|
| TF-IDF temel çizgi | 0.722 | 0.559 | 0.973 | 0.142 | 0.646 | 0.929 | 1.000 | 67.1% |

## Sınırlılık

Veri seti sentetiktir (spec 2: gerçek platformdan veri kazınmaz) ve iki
sınıfın kalıpları elle yazılmıştır. Sınıfları tasarlayan taraf ile ölçen
taraf aynı olduğunda, kendi test kümesindeki başarım gerçek başarımın
üst sınırıdır — bu yüzden aktarım testi eklenmiştir. Gerçek dağılımda
beklenecek başarım, aktarım satırından da düşük olacaktır; model kararı
her durumda çekimserlik kurallarıyla (İlke 2) sınırlanır.
