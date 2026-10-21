# Diferansiyel test ve uyum raporu

Bu rapor `python tools/uyum_raporu.py` ile **testlerin kullandığı aynı karşılaştırma kodundan** (`tests/helpers.py::compare_gui_row`) üretilir. Her satırda G*Power 3.1.9.7'nin GUI'de gösterdiği değer ile temiz odada yazılan motorun aynı girdideki gösterimi alan alan, 7 basamaklı metin olarak karşılaştırılır (sayı yakınlığı değil, ekrandaki dizginin aynısı).

Ortam: Python 3.13.15 · scipy 1.18.1 · Linux.

## Oranlar

| Ölçü | Değer |
|------|------:|
| G*Power GUI vektörü (ekran görüntülü) | 63 (47 sonuç, 4 uyarılı, 12 hata) |
| Bütün alanlar + mesaj birebir | **59/63 (%93,7)** |
| Toplam N birebir (sonuç veren 51 vektör) | **47/51 (%92,2)** |
| Hata mesajı birebir (12 hata vektörü) | 12/12 |
| Bilinen sapma (R-18, açıklamalı) | 4 |
| **Açıklanmamış uyumsuzluk** | **0** |
| statsmodels kütüphane vektörü (bağımsız ikinci oracle) | 1485/1485 uyumlu (post hoc güç farkı en çok 5.0e-07) |

Sapan alan sayısı (yalnızca bilinen sapmalardan): N 4, güç 3, df2 4, λ 4.

## Uyumsuzlukların açıklaması

Dört sapmanın dördü de aşırı küçük etki büyüklüğündedir (f ≤ 0,0002, N ≥ 2,4·10⁸). Bu bölgede çift duyarlıklı her merkezi olmayan F hesabı gürültülüdür; kimin doğru olduğu `mpmath` ile 40 basamakta ayrıca hesaplandı (`oracle/R18_YUKSEK_HASSASIYET.md`, `tests/test_r18_high_precision.py`). Testlerde `xfail(strict=True)` ile işaretlidirler: G*Power ile birden eşleşirlerse test **kırmızı** olur, yani bu liste sessizce eskiyemez.

| Vektör | Açıklama |
|--------|----------|
| V52 | R-18: df2 ≈ 10⁹; G*Power'ın N'i minimum değil (15 kişi fazla) — mpmath 40 basamakla kanıtlı |
| V54 | R-18: G*Power'ın N'i hedef gücü **sağlamıyor** (0,7999999953 < 0,80) — motor 3 kişi fazla, doğru |
| V55 | R-18: G*Power'ın N'i 2 520 kişi fazla — mpmath ile kanıtlı |
| V56 | R-18: N ≈ 9,6·10¹²; G*Power'ın λ'sı 9,6363, doğrusu ≈ 9,63469 |

## Vektör vektör

| Vektör | Girdi | G*Power (N / güç) | Motor (N / güç) | Sonuç |
|--------|-------|-------------------|-----------------|-------|
| V01 | a-priori, f=0.1, α=0.05, güç=0.8, k=3 | 969 / 0.8011010 | 969 / 0.8011010 | ✅ birebir |
| V02 | a-priori, f=0.25, α=0.05, güç=0.8, k=3 | 159 / 0.8048873 | 159 / 0.8048873 | ✅ birebir |
| V03 | a-priori, f=0.4, α=0.05, güç=0.8, k=3 | 66 / 0.8180744 | 66 / 0.8180744 | ✅ birebir |
| V04 | a-priori, f=0.1, α=0.05, güç=0.95, k=3 | 1548 / 0.9500866 | 1548 / 0.9500866 | ✅ birebir |
| V05 | a-priori, f=0.25, α=0.05, güç=0.95, k=3 | 252 / 0.9514888 | 252 / 0.9514888 | ✅ birebir |
| V06 | a-priori, f=0.4, α=0.05, güç=0.95, k=3 | 102 / 0.9547295 | 102 / 0.9547295 | ✅ birebir |
| V07 | a-priori, f=0.25, α=0.01, güç=0.8, k=3 | 228 / 0.8029054 | 228 / 0.8029054 | ✅ birebir |
| V08 | a-priori, f=0.25, α=0.01, güç=0.95, k=3 | 336 / 0.9506719 | 336 / 0.9506719 | ✅ birebir |
| V09 | a-priori, f=0.25, α=0.05, güç=0.9, k=3 | 207 / 0.9022417 | 207 / 0.9022417 | ✅ birebir |
| V10 | a-priori, f=0.25, α=0.1, güç=0.8, k=3 | 126 / 0.8008668 | 126 / 0.8008668 | ✅ birebir |
| V11 | a-priori, f=0.25, α=0.05, güç=0.95, k=2 | 210 / 0.9501287 | 210 / 0.9501287 | ✅ birebir |
| V12 | a-priori, f=0.25, α=0.05, güç=0.95, k=4 | 280 / 0.9509908 | 280 / 0.9509908 | ✅ birebir |
| V13 | a-priori, f=0.25, α=0.05, güç=0.95, k=5 | 305 / 0.9521313 | 305 / 0.9521313 | ✅ birebir |
| V14 | a-priori, f=0.25, α=0.05, güç=0.95, k=10 | 390 / 0.9523634 | 390 / 0.9523634 | ✅ birebir |
| V15 | a-priori, f=0.3, α=0.05, güç=0.85, k=3 | 126 / 0.8548129 | 126 / 0.8548129 | ✅ birebir |
| V16 | a-priori, f=0.17, α=0.05, güç=0.8, k=3 | 339 / 0.8032639 | 339 / 0.8032639 | ✅ birebir |
| V17 | a-priori, f=0.33, α=0.05, güç=0.9, k=4 | 136 / 0.9044891 | 136 / 0.9044891 | ✅ birebir |
| V18 | a-priori, f=0.05, α=0.05, güç=0.95, k=3 | 6183 / 0.9500867 | 6183 / 0.9500867 | ✅ birebir |
| V19 | a-priori, f=0.02, α=0.05, güç=0.8, k=3 | 24090 / 0.8000049 | 24090 / 0.8000049 | ✅ birebir |
| V20 | a-priori, f=0.01, α=0.05, güç=0.8, k=3 | 96351 / 0.8000049 | 96351 / 0.8000049 | ✅ birebir |
| V21 | a-priori, f=1.0, α=0.05, güç=0.8, k=3 | 15 / 0.8695976 | 15 / 0.8695976 | ✅ birebir |
| V22 | a-priori, f=2.0, α=0.05, güç=0.95, k=3 | 9 / 0.9853857 | 9 / 0.9853857 | ✅ birebir |
| V23 | a-priori, f=5.0, α=0.05, güç=0.8, k=3 | 6 / 0.9998838 | 6 / 0.9998838 | ✅ birebir |
| V24 | a-priori, f=0.25, α=0.05, güç=0.05, k=3 | 6 / 0.0622405 | 6 / 0.0622405 | ✅ birebir |
| V25 | a-priori, f=0.25, α=0.05, güç=0.03, k=3 | Power must be greater than or equal to a / — | — / hata: Power must be greater than or equa | ✅ birebir |
| V26 | a-priori, f=0.25, α=0.05, güç=0.99, k=3 | 348 / 0.9904577 | 348 / 0.9904577 | ✅ birebir |
| V27 | a-priori, f=0.25, α=0.001, güç=0.95, k=3 | 450 / 0.9514323 | 450 / 0.9514323 | ✅ birebir |
| V28 | a-priori, f=0, α=0.05, güç=0.95, k=3 | Effect size f is outside the admissible  / — | — / hata: Effect size f is outside the admis | ✅ birebir |
| V29 | a-priori, f=-0.25, α=0.05, güç=0.95, k=3 | Effect size f is outside the admissible  / — | — / hata: Effect size f is outside the admis | ✅ birebir |
| V30 | a-priori, f=0.25, α=0, güç=0.95, k=3 | Alpha is outside the admissible range (1 / — | — / hata: Alpha is outside the admissible ra | ✅ birebir |
| V31 | a-priori, f=0.25, α=1, güç=0.95, k=3 | Alpha is outside the admissible range (1 / — | — / hata: Alpha is outside the admissible ra | ✅ birebir |
| V32 | a-priori, f=0.25, α=0.05, güç=1, k=3 | Power is outside the admissible range (1 / — | — / hata: Power is outside the admissible ra | ✅ birebir |
| V33 | a-priori, f=0.25, α=0.05, güç=0.95, k=1 | There must be at least 2 groups. / — | — / hata: There must be at least 2 groups. | ✅ birebir |
| V34 | post-hoc, f=0.25, α=0.05, N=60, k=3 | 60 / 0.3744311 | 60 / 0.3744311 | ✅ birebir |
| V35 | post-hoc, f=0.4, α=0.05, N=30, k=3 | 30 / 0.4420732 | 30 / 0.4420732 | ✅ birebir |
| V36 | post-hoc, f=0.1, α=0.05, N=300, k=3 | 300 / 0.3186430 | 300 / 0.3186430 | ✅ birebir |
| V37 | post-hoc, f=0.25, α=0.01, N=90, k=3 | 90 / 0.2972804 | 90 / 0.2972804 | ✅ birebir |
| V38 | post-hoc, f=0.25, α=0.05, N=61, k=3 | 61 / 0.3802907 | 61 / 0.3802907 | ✅ birebir |
| V39 | post-hoc, f=0.25, α=0.05, N=4, k=3 | 4 / 0.0530691 | 4 / 0.0530691 | ✅ birebir |
| V40 | post-hoc, f=0.25, α=0.05, N=3, k=3 | Sample size must be greater than the num / — | — / hata: Sample size must be greater than t | ✅ birebir |
| V41 | post-hoc, f=0.25, α=0.05, N=1000, k=3 | 1000 / 1.0000000 | 1000 / 1.0000000 | ✅ birebir |
| V42 | post-hoc, f=0.25, α=0.05, N=210, k=2 | 210 / 0.9501287 | 210 / 0.9501287 | ✅ birebir |
| V43 | post-hoc, f=0, α=0.05, N=60, k=3 | 60 / 0.0500000 | 60 / 0.0500000 | ✅ birebir |
| V44 | post-hoc, f=0.25, α=0.05, N=100, k=5 | 100 / 0.4663312 | 100 / 0.4663312 | ✅ birebir |
| V45 | a-priori, f=0.25, α=0.05, güç=0.95, k=2.5 | 252 / 0.9514888 | 252 / 0.9514888 | ✅ birebir |
| V46 | a-priori, f=0.25, α=0.05, güç=0.95, k=2.4 | 210 / 0.9501287 | 210 / 0.9501287 | ✅ birebir |
| V47 | a-priori, f=50, α=0.05, güç=0.95, k=3 | 6 / 1.0000000 | 6 / 1.0000000 | ✅ birebir |
| V48 | a-priori, f=5.1, α=0.05, güç=0.95, k=3 | 6 / 0.9999216 | 6 / 0.9999216 | ✅ birebir |
| V49 | a-priori, f=50.01, α=0.05, güç=0.95, k=3 | Effect size f is outside the admissible  / — | — / hata: Effect size f is outside the admis | ✅ birebir |
| V50 | post-hoc, f=-0.1, α=0.05, N=60, k=3 | Effect size f is outside the admissible  / — | — / hata: Effect size f is outside the admis | ✅ birebir |
| V51 | a-priori, f=0.001, α=0.05, güç=0.80, k=3 | 9634692 / 0.8000000 | 9634692 / 0.8000000 | ✅ birebir |
| V52 | a-priori, f=0.0001, α=0.05, güç=0.80, k=3 | 963468906 / 0.7999999 | 963468891 / 0.8000000 | ⚠️ bilinen sapma |
| V53 | a-priori, f=0.0005, α=0.05, güç=0.80, k=3 | 38538759 / 0.8000000 | 38538759 / 0.8000000 | ✅ birebir |
| V54 | a-priori, f=0.0002, α=0.05, güç=0.80, k=3 | 240867222 / 0.8000000 | 240867225 / 0.8000000 | ⚠️ bilinen sapma |
| V55 | a-priori, f=0.00005, α=0.05, güç=0.80, k=3 | 3853878072 / 0.7999998 | 3853875552 / 0.8000000 | ⚠️ bilinen sapma |
| V56 | a-priori, f=0.000001, α=0.05, güç=0.80, k=3 | 9.6363e+12 / 0.8000001 | 9.6347e+12 / 0.8000000 | ⚠️ bilinen sapma |
| V57 | a-priori, f=0, α=0.05, güç=0.95, k=1 | There must be at least 2 groups. / — | — / hata: There must be at least 2 groups. | ✅ birebir |
| V58 | post-hoc, f=0.25, α=0.05, N=60.5, k=3 | 61 / 0.3802907 | 61 / 0.3802907 | ✅ birebir |
| V59 | a-priori, f=0.25, α=0.05, güç=0.95, k=1.5 | 210 / 0.9501287 | 210 / 0.9501287 | ✅ birebir |
| V60 | a-priori, f=0.25, α=0.05, güç=0.95, k=1.4 | There must be at least 2 groups. / — | — / hata: There must be at least 2 groups. | ✅ birebir |
| V61 | post-hoc, f=0.5, α=0.05, N=600, k=3 | 600 / 1.0000000 | 600 / 1.0000000 | ✅ birebir |
| V62 | post-hoc, f=0.01, α=0.005, N=30, k=3 | 30 / 0.0050329 | 30 / 0.0050329 | ✅ birebir |
| V63 | a-priori, f=0.25, α=0.05, güç=0.95, k=7 | 343 / 0.9518838 | 343 / 0.9518838 | ✅ birebir |

Ekran görüntüleri: `oracle/screenshots/<Vektör>.png` · ham değerler: `oracle/gpower_gui_vectors.csv` · aynı karşılaştırma tarayıcıda: canlı demodaki **Doğrula** düğmesi.
