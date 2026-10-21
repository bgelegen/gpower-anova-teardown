# Oracle — iki katmanlı kâhin

Beklenen değerleri **ajan değil, kara kutu** belirler (slayt 16).

## Katman 1 · G*Power GUI (elle, ≥ 30 vektör)

Dosya: `gpower_gui_vectors.csv` — **63 vektör, hepsi dolduruldu** (48 a priori, 15 post hoc;
51 sayısal sonuç, 12 hata kutusu; 4 sonuçta ayrıca "Please note" uyarısı). Her satırın penceresi `screenshots/Vxx.png`.
Değerler G*Power 3.1.9.7 penceresinden ekranda göründüğü haneyle okundu.

| Sınıf | Vektörler | Sorulan soru |
|-------|-----------|--------------|
| cohen | V01–V06 | f = 0,10 / 0,25 / 0,40 kılavuzla tutarlı mı |
| alfa, guc | V07–V10, V26, V27 | α ve güç değişince N nasıl değişiyor |
| k | V11–V14 | grup sayısı; **V11 (k=2) hocanın t-testi referansıyla aynı olmalı: N=210** |
| yuvarlama | V15–V17 | ham N k'ya bölünmediğinde ne oluyor |
| kucuk_f | V18–V20 | iterasyon yakınsıyor mu, tavan var mı |
| buyuk_f | V21–V23 | N alt sınıra iniyor mu, alt sınır ne |
| guc_alfa | V24–V25 | güç ≤ α: hata mı, sonuç mu |
| gecersiz | V28–V33, V40 | hangi mesaj, hangi alan |
| posthoc | V34–V44 | güç hesabı; N k'ya bölünmezse ne oluyor |
| ek | V45–V52 | kesirli grup sayısı, f üst sınırı (50), λ ≥ 100 gösterimi, post hoc negatif f, f = 0,001 ve 0,0001 |
| SPEC §6 | V53–V63 | sapmanın başladığı f (V53–V56), iki geçersiz girdi (V57), kesirli N ve k (V58–V60), post hoc gösterim (V61, V62), k = 7 (V63) |

### Nasıl doldurulur

G*Power → *Test family: F tests* → *Statistical test: ANOVA: Fixed effects,
omnibus, one-way* → *Type of power analysis* (A priori / Post hoc).

1. Girdileri satırdaki gibi gir, **Calculate**.
2. Pencerenin ekran görüntüsünü `screenshots/Vxx.png` olarak kaydet.
3. Output bölümündeki değerleri **ekranda göründüğü haneyle** `gp_*` sütunlarına yaz
   (Noncentrality parameter λ → `gp_ncp`, Critical F → `gp_critical`,
   Numerator df → `gp_df1`, Denominator df → `gp_df2`,
   Total sample size → `gp_n_total`, Actual power → `gp_actual_power`).
4. Hata/uyarı çıkarsa metnini aynen `gp_mesaj` sütununa yaz.

Kılavuz örneği: kılavuz s. 25 §10.3 (k = 10, f = 0,25, α = 0,05, güç = 0,95 → N = 390)
**V14**'tür; G*Power penceresi kılavuzdaki 6 ondalığı 7 ondalıkla verir (LEDGER L-43).

### Diferansiyel sonuç (motor ↔ G*Power)

| | Sayı |
|---|---:|
| Vektör | 63 |
| Tüm alanları birebir (metin olarak) | **59** |
| Sayısal sonuçlu vektörde N birebir | **47 / 51 (%92,2)** |
| Hata/uyarı metni birebir | 12 / 12 hata, 4 / 4 uyarı |
| Bilinen sapma (`xfail`) | V52, V54, V55, V56 — uç küçük f, df2 ≳ 2·10⁸ |

Bilinen sapmalarda **motorun doğru, G*Power'ın yanlış** olduğu 40 basamaklı bağımsız
hesapla gösterildi: [`R18_YUKSEK_HASSASIYET.md`](R18_YUKSEK_HASSASIYET.md).
Ek ekran görüntüsü `screenshots/ek-posthoc-gecis-int32.png` yalnızca GUI'ye özgü bir
gözlemdir (LEDGER L-54).

## Katman 2 · Kütüphane (otomatik, 1485 vektör)

```bash
pip install statsmodels
python oracle/gen_library_vectors.py
```

`library_vectors.csv`: statsmodels `FTestAnovaPower` (1485 vektör: 495 a priori + 990 post hoc).

- **a priori:** statsmodels kesirli N verir (`lib_n_total_raw`).
  Örn. f=0,25 α=0,05 güç=0,95: k=2 → 209,86 · k=3 → 250,12.
  G*Power'ın N'i nasıl tam sayıya getirdiği (ceil? k'nın katı?) bir **[REA]**
  sorusudur; testler beklenen N'i ham değerden SPEC'teki kuralla türetir.
- **post hoc:** `lib_power` doğrudan karşılaştırılır.

Sonuç: **1485 / 1485** eşleşme (a priori: ham N'den SPEC R-05 kuralıyla türetilen N
birebir; post hoc: |güç farkı| < 1e-6). Kütüphanenin kesirli N'i ile G*Power'ın tam sayı
N'i arasındaki fark (ör. 250,12 → 252) bulgunun kendisidir: G*Power yalnızca yukarı
yuvarlamıyor, **k'nın katına** yuvarlıyor (R-05).
