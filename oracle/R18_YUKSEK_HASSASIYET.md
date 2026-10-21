# R-18 · Uç küçük f'de kim doğru? (yüksek hassasiyetli kanıt)

SPEC R-18, G*Power'ın çok küçük f'de (df2 ≳ 10⁸) N ve gerçekleşen gücü sayısal
gürültüyle raporladığını söylüyor ve §5'te "V52'de doğru minimum N" sorusunu
**bilinmeyen** olarak bırakıyordu. Bu dosya o soruyu kapatır.

**Yöntem.** Motordan ve scipy'den bağımsız, `mpmath` ile 40 anlamlı basamakta güç:
k = 3 (df1 = 2) için merkezi F'nin kritik değeri kapalı biçimdedir
(P(Y > y) = (1 − y)^(df2/2) = α), merkezi olmayan F'nin dağılımı ise Poisson
ağırlıklı düzenlenmiş tamamlanmamış beta toplamıdır. Kod:
`tests/test_r18_high_precision.py`. Hedef güç 0,80, α = 0,05, k = 3.

| Vektör | f | G*Power N | Motor N | güç(G*Power N) | güç(Motor N) | güç(Motor N − 3) | Sonuç |
|--------|---|----------:|--------:|---------------:|-------------:|-----------------:|-------|
| V51 | 0,001 | 9 634 692 | 9 634 692 | 0,800000005947 | aynı | 0,799999875045 | ikisi de doğru |
| V53 | 0,0005 | 38 538 759 | 38 538 759 | 0,800000005808 | aynı | 0,799999973082 | ikisi de doğru |
| V54 | 0,0002 | 240 867 222 | **240 867 225** | **0,799999995296** < 0,80 | 0,800000000532 | 0,799999995296 | G*Power hedefin **altında** |
| V52 | 0,0001 | 963 468 906 | **963 468 891** | 0,800000007072 | 0,800000000527 | 0,799999999218 | G*Power 15 kişi **fazla** |
| V55 | 0,00005 | 3 853 878 072 | **3 853 875 552** | 0,800000275093 | 0,800000000198 | 0,799999999871 | G*Power 2 520 kişi **fazla** |
| V56 | 0,000001 | 9,6363e+12 | 9,6347e+12 | — | — | — | G*Power λ = 9,6363 (doğrusu ≈ 9,63469) |

**Sonuç.** df2 ≈ 2·10⁸'e kadar (V51, V53) G*Power ile motor birebir aynı. Daha
büyük df2'de G*Power'ın merkezi olmayan F hesabı kayıyor: V54'te gösterilen N
hedef gücü **sağlamıyor**, V52/V55'te gereğinden büyük. Motor her durumda hedefi
sağlayan en küçük 3'ün katını veriyor. Bu vektörler diferansiyel testte
`xfail(strict=True)` ile "bilinen sayısal sapma" olarak işaretlidir; N eşleşme
oranı hesabında ayrıca raporlanır (README).

Ek gözlem (CLI'yi etkilemez, yalnızca GUI): V56'dan sonra *A priori* → *Post hoc*
geçişinde G*Power toplam N alanına 9,6e12 yerine **2147483647** (32 bit tamsayı
üst sınırı) yazdı → `screenshots/ek-posthoc-gecis-int32.png`.
