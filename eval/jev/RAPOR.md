# Test ailesi sınıflandırıcısı (Jev yerine etiket kümesi kısıtlı LLM)

**Neden LLM?** Yönerge bu katmanı isteğe bağlı olarak Jev **ya da** etiket kümesi kısıtlı bir LLM ile kurmayı öneriyor. Jev'i kurup eğitmek bu sürede mümkün olmadı; yerine Claude Haiku araçsız, yalnızca 7 etiketten birini ve bir güven değeri döndürecek şekilde kullanıldı (`siniflandir.py`). Sınıflandırıcı **hiç sayı üretmez**; yalnızca hangi motorun çağrılacağına ya da araştırmacıya soru sorulacağına karar verir.

**Karar kuralı.** Etiket `ambiguous`/`unsupported` ya da güven < 0.75 → *araştırmacıya sor*. Etiket `anova-oneway` ve güven ≥ eşik → bu depodaki motor. Diğer aileler → başka araç (bu depoda yok).

İlk koşuda 3 çağrı model yanıtı yerine abonelik eşzamanlılık sınırı ("session limit") döndü; bunlar model hatası olmadığı için `--yeniden` ile tek tek yeniden koşuldu (`sonuclar.json`'da `"yeniden": true`).

**Veri.** 24 klinik soru (`sorular.json`): her aileden 3–4 soru, 4 kapsam dışı, 4 bilerek belirsiz; her biri Türkçe ve İngilizce. Etiketler elle verildi.

## Sonuçlar

| Ölçü | Türkçe | İngilizce | Toplam |
|------|------:|------:|------:|
| Etiket doğruluğu | 24/24 (%100) | 24/24 (%100) | 48/48 (%100) |
| Doğru davranış (belirsizde sormak dahil) | 24/24 (%100) | 24/24 (%100) | 48/48 (%100) |
| ANOVA sorusu motora gitti | 4/4 (%100) | 4/4 (%100) | 8/8 (%100) |
| ANOVA olmayan soru motora **gitmedi** | 20/20 (%100) | 20/20 (%100) | 40/40 (%100) |
| Belirsiz soruda araştırmacıya sordu | 4/4 (%100) | 4/4 (%100) | 8/8 (%100) |
| Karar 'sor' oranı | 8/24 (%33) | 8/24 (%33) | 16/48 (%33) |
| Ortalama güven | 0.94 | 0.95 | 0.94 |
| Geçersiz çıktı | 0 | 0 | 0 |

## Kalibrasyon

Güveni iyi kalibre bir sınıflandırıcıda, örneğin 0,9 güvenle verilen etiketlerin ~%90'ı doğru olmalı.

| Güven kovası | Adet | Ortalama güven | Gerçek doğruluk |
|--------------|-----:|---------------:|----------------:|
| [0.00, 0.50) | 0 | — | — |
| [0.50, 0.75) | 0 | — | — |
| [0.75, 0.90) | 4 | 0.84 | 1.00 |
| [0.90, 1.00] | 44 | 0.95 | 1.00 |

**Beklenen kalibrasyon hatası (ECE): 0.056** (0 = mükemmel).

## Yanlışlar

Yok.

## Yorum ve sınırlılıklar

- **En önemli güvenlik ölçüsü** "ANOVA olmayan soru motora gitmedi" satırıdır: yanlış yönlendirme, yanlış testle hesaplanmış ama inandırıcı görünen bir örneklem büyüklüğü demektir. Tuzak sorular (J13: üç kol ama sonuç iyileşti/iyileşmedi → ki-kare; J19: üç zaman noktası ama aynı hastalar → tekrarlı ölçüm) bu yüzden kondu.
- **Kalibrasyon:** hatalar güven kovalarında değil, model biraz *az güvenli* (0,84 güvenle verdiği etiketlerin hepsi doğru); ECE'nin tamamı bu temkinden gelir ve güvenli yöndedir.
- **Türkçe–İngilizce:** iki dilde de aynı sorular doğru sınıflandı; ortalama güven de neredeyse aynı (0,94 ve 0,95).
- **Sınırlılık:** soru seti küçük (24×2) ve etiketleri yazan biziz, yani ölçüt kolay olabilir; %100, gerçek araştırmacı sorularında da %100 olacağı anlamına gelmez. Tek koşu yapıldı.


## Maliyet

48 çağrı · toplam 268 878 token · 0.028 $ liste maliyeti · ortalama 2.0 sn/soru.

Her çağrının ham yanıtı: `sonuclar.json`.
