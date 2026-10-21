# Ajan değerlendirmesi — yönerge raporu

Yönergenin AI ajanı maddesi için: her sorunun **beklenen test ailesi**, ajanın **doğru seçim** oranı ve aynı soruların **MCP** ve **GUI (ekran görüntüsü)** yollarından token, süre ve doğruluk değerleri. Değerler Claude Code kayıtlarından (`usage`, `duration_ms`) okunur; `python eval/rapor.py` ile yeniden üretilir.

## v3 (son sürüm)

| Soru | Beklenen aile | Doğru seçim | MCP doğru | MCP token | MCP süre | GUI doğru | GUI token | GUI süre |
|------|---------------|:-----------:|:---------:|----------:|---------:|:---------:|----------:|---------:|
| S01 | `anova-oneway` | ✅ | ✅ | 14 244 | 4.7 sn | ❌ | 13 927 | 3.9 sn |
| S02 | `anova-oneway` | ✅ | ✅ | 14 113 | 4.2 sn | ✅ | 13 614 | 2.6 sn |
| S03 | `anova-oneway` | ✅ | ✅ | 14 270 | 4.8 sn | ✅ | 13 596 | 3.5 sn |
| S04 | `anova-oneway` | ✅ | ✅ | 14 208 | 4.6 sn | ✅ | 13 672 | 2.7 sn |
| S05 | `anova-oneway` | ✅ | ✅ | 14 174 | 4.4 sn | ✅ | 13 628 | 4.0 sn |
| S06 | `anova-oneway` | ✅ | ✅ | 14 098 | 3.9 sn | ✅ | 13 584 | 2.4 sn |
| S07 | `anova-oneway` | ✅ | ✅ | 14 269 | 6.4 sn | ✅ | 13 750 | 3.5 sn |
| S08 | `anova-oneway` | ✅ | ✅ | 14 338 | 5.0 sn | ✅ | 14 112 | 4.5 sn |
| S09 | `anova-oneway` | ✅ | ✅ | 14 425 | 6.6 sn | ✅ | 13 773 | 3.2 sn |
| S10 | `chi2-contingency` | ✅ | ✅ | 7 378 | 5.7 sn | — | — | — |

- **Doğru seçim oranı: 10/10** (9 tek yönlü ANOVA sorusunda aracı çağırdı, ki-kare sorusunu çağırmadan reddetti).
- **Doğruluk:** MCP 10/10 · GUI (ekran görüntüsü) 8/9.
- **Karşılaştırılabilir 9 soruda ortalama:** MCP 14 238 token, 5.0 sn · GUI 13 740 token, 3.4 sn.

## v3 tekrar

| Soru | Beklenen aile | Doğru seçim | MCP doğru | MCP token | MCP süre | GUI doğru | GUI token | GUI süre |
|------|---------------|:-----------:|:---------:|----------:|---------:|:---------:|----------:|---------:|
| S01 | `anova-oneway` | ✅ | ✅ | 14 324 | 4.7 sn | ❌ | 14 044 | 5.2 sn |
| S02 | `anova-oneway` | ✅ | ✅ | 14 157 | 4.3 sn | ✅ | 13 607 | 2.1 sn |
| S03 | `anova-oneway` | ✅ | ✅ | 14 160 | 3.4 sn | ✅ | 13 460 | 2.7 sn |
| S04 | `anova-oneway` | ✅ | ✅ | 14 204 | 3.9 sn | ✅ | 13 672 | 2.4 sn |
| S05 | `anova-oneway` | ✅ | ✅ | 14 399 | 4.1 sn | ✅ | 13 654 | 2.4 sn |
| S06 | `anova-oneway` | ✅ | ✅ | 14 093 | 7.0 sn | ✅ | 13 591 | 2.0 sn |
| S07 | `anova-oneway` | ✅ | ✅ | 14 095 | 3.4 sn | ✅ | 13 747 | 2.8 sn |
| S08 | `anova-oneway` | ✅ | ✅ | 14 682 | 4.7 sn | ✅ | 14 046 | 4.0 sn |
| S09 | `anova-oneway` | ✅ | ❌ | 14 542 | 6.1 sn | ✅ | 13 885 | 3.5 sn |
| S10 | `chi2-contingency` | ✅ | ✅ | 7 091 | 2.6 sn | — | — | — |

- **Doğru seçim oranı: 10/10** (9 tek yönlü ANOVA sorusunda aracı çağırdı, ki-kare sorusunu çağırmadan reddetti).
- **Doğruluk:** MCP 9/10 · GUI (ekran görüntüsü) 8/9.
- **Karşılaştırılabilir 9 soruda ortalama:** MCP 14 295 token, 4.6 sn · GUI 13 745 token, 3.0 sn.

## Yorum

- **Seçim:** ajan iki koşuda da 10/10 doğru aileyi seçti; kapsam dışı ki-kare sorusunda aracı hiç çağırmadan "bu araç yalnızca tek yönlü ANOVA'yı destekliyor" dedi.
- **Doğruluk:** MCP yolunda tek hata (v3 tekrar S09) ajanın "tek kollu" soruda grup sayısını kendisi 2 varsaymasıdır (H-08). GUI yolundaki hata S01: grup başı n G*Power ekranında yazmıyor; ajan bunu dürüstçe söyledi ama soruyu tam yanıtlayamadı. MCP çıktısında bu alan yapısal JSON'da hazır gelir.
- **Token ve süre:** bu tabloda GUI kolu ~500 token ve ~1,5 sn daha ucuz görünüyor, çünkü ona **hazır** bir G*Power ekran görüntüsü verildi. O görüntüyü üretmek (G*Power'ı açıp alanları doldurmak, ekran görüntüsü almak) dahil değildir; bu bedel `OZET.md`'de ayrıca hesaplandı (vektör başına ~3 araç çağrısı ve ~1 500 görüntü token'ı). MCP kolunun fazladan token'ı araç şemasının bağlamda durmasından gelir ve sabittir.
- **Değerlendirme notu:** G*Power ekranı 7 basamak (0,3744311), beklenen değer 4 basamak (0,3744) verir; GUI yanıtı beklenen basamağa yuvarlanarak karşılaştırılır.
