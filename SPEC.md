# SPEC — anova-oneway

> **Oturum 1 (söküm) doldurur.** Bu dosya yeniden yazım oturumunun (Oturum 2)
> gördüğü TEK davranış belgesidir. Decompile kodu, adres listesi veya
> fonksiyon gövdesi içermez; yalnızca **gözlenebilir davranış** içerir.
> Her kural `R-xx` kimliği taşır ve LEDGER.md'de en az bir satıra bağlanır.

**Kanıt düzeyi işaretleri** (her kuralda): **[DOK]** = G*Power kılavuzunda yazıyor;
**[REA]** = binary'de gözlendi, kılavuzda yok; **[ORACLE]** = G*Power penceresinde
gözlendi; **[AJAN]** = çıkarım, kesin sayılmamalı. Bu turda oracle'ın 52 vektörü
dolduruldu; kurallardaki "✓ Vxx" ifadeleri oracle ile doğrulandığını gösterir.
Sayısal beklenen değerler bu belgede **verilmez**; onları
`oracle/gpower_gui_vectors.csv` verir.

## 1. Kapsam

- Test: F testi, tek yönlü ANOVA, sabit etkiler, omnibus
- Modlar: a priori (N hesapla), post hoc (güç hesapla)
- Arayüz: [CONTRACT.md](CONTRACT.md)

Gösterim: f = Cohen etki büyüklüğü, α = I. tip hata, k = grup sayısı,
N = toplam örneklem, F(x; d₁, d₂, λ) = merkezi olmayan F dağılımının birikimli
dağılım fonksiyonu (λ = 0 merkezi F).

## 2. Girdiler ve geçerlilik

Uçlar **dahildir** (aralığın içindeki uç değer geçerlidir).

| Girdi | Geçerli aralık | Geçersizse | Kanıt |
|-------|----------------|------------|-------|
| f (a priori) | 1e-6 ≤ f ≤ 50 (f = 50 geçerli ✓ V47; 50,01 hata ✓ V49) | R-10 mesajı | L-17, L-30 |
| f (post hoc) | 0 ≤ f ≤ 50 (**f = 0 geçerli** ✓ V43) | R-10 mesajı | L-17, L-24 |
| α | 1e-7 ≤ α ≤ 0,9999999 | R-11 mesajı | L-18 |
| güç (a priori) | 1e-7 ≤ güç ≤ 0,9999999 ve güç ≥ α (**güç = α geçerli** ✓ V24) | R-11 / R-12 mesajı | L-19, L-20 |
| k (grup) | k ≥ 2 **yuvarlamadan sonra**; kesirli k kabul edilir ve yarım yukarı yuvarlanır (R-17) | R-09 mesajı | L-16, L-35, L-45 |
| N (post hoc) | N > k **yuvarlamadan sonra** (N = k + 1 geçerli; k'nın katı olması **gerekmez**) | R-13 mesajı | L-21, L-22, L-35 |

## 3. Kurallar

### R-01 · Modlar ve çıktılar  [DOK]
- **Kural:** İki mod desteklenir. *A priori*: girdiler f, α, güç, k → çıktılar
  λ, kritik F, df1, df2, toplam N, gerçekleşen güç ("actual power").
  *Post hoc*: girdiler f, α, N, k → çıktılar λ, kritik F, df1, df2, güç.
  Grup başına n = N / k (a priori'de her zaman tamsayı; bkz. R-05).
  Cohen eşikleri (bilgi amaçlı): küçük 0,10, orta 0,25, büyük 0,40.
- **Kanıt:** LEDGER L-01, L-40, L-46
- **Test:** oracle V01–V06, V05, V34

### R-02 · Serbestlik dereceleri  [DOK]
- **Kural:** df1 = k − 1, df2 = N − k (k ve N, R-17'ye göre tamsayıya
  çevrilmiş değerlerdir). A priori aramada N kesirli olabilir; df2 de o zaman
  kesirli kullanılır (bkz. R-04). Gösterilen df2 nihai (yuvarlanmış) N ile
  hesaplanır.
- **Kanıt:** LEDGER L-02, L-03, L-42
- **Test:** oracle V05, V11, V14, V17

### R-03 · λ, kritik F ve güç  [DOK] (hesap kurgusu [REA])
- **Kural:**
  - λ = f² · N  [DOK]
  - H0: merkezi F(df1, df2); H1: merkezi olmayan F(df1, df2, λ)  [DOK]
  - kritik F = merkezi F'nin 1 − α kantili: F_crit = F⁻¹(1 − α; df1, df2)  [REA]
  - güç = 1 − F(F_crit; df1, df2, λ)  [REA]
- **Kanıt:** LEDGER L-04, L-05, L-06, L-41, L-34 (düzeltildi)
- **Test:** oracle V05, V11, V14 (kılavuz örneği), V15, V16, V17

### R-04 · A priori N araması  [REA]
- **Kural:** h(N) = güç(f, α, N) − hedef güç fonksiyonunun **sürekli N**
  üzerindeki kökü aranır (N kesirli; λ ve df2 kesirli N ile hesaplanır).
  1. **Taban aralık:** lo = k + 1, hi = k + 100.
  2. **Aralık kurma:**
     - h(hi) < 0 ise: alt := hi, üst := 1,6·hi; h(üst) < 0 olduğu sürece
       alt := üst, üst := 1,6·üst. **İterasyon sınırı yoktur** (tavan yok).
     - h(hi) ≥ 0 ise: üst := hi, m := (lo + hi)/2. m ≥ lo ve h(m) > 0 olduğu
       sürece: üst := m, m := (m + lo)/2 − lo (sic; etkisi m := (m − lo)/2).
       Döngü bitince alt := m.
     - Son olarak alt < lo ise alt := lo.
  3. **Kök bulma:** [alt, üst] üzerinde Brent yöntemi (ikiye bölme + ters
     kuadratik/sekant interpolasyonu).
     - **Durma koşulu:** h(b) = 0 **veya** |yarı aralık| ≤ 2⁻⁵³·|b| (yaklaşık
       makine hassasiyeti; dışarıdan verilen ayrı bir mutlak tolerans
       **kullanılmaz**).
     - **En fazla 300 iterasyon**; aşılırsa o anki tahmin döndürülür, hata
       verilmez.
     - h(alt) ve h(üst) aynı işaretliyse kök bulucu **0** döndürür; hata
       verilmez (sonuç R-06 ile alt sınıra kıskaçlanır).
  - Kök tam sayıya değil, sonradan R-05 ile yuvarlanır; bu yüzden herhangi
    bir doğru kök bulucu, sınır durumları ve R-18 dışında aynı N'i verir.
  - Çok küçük f'de de (f = 0,0001'e kadar ✓ V52) sonuç döner; tavan yoktur.
- **Kanıt:** LEDGER L-07, L-08, L-10, L-13, L-14, L-31
- **Test:** oracle V05, V18, V19, V20, V51, V52 · kütüphane `library_vectors.csv` (lib_n_total_raw ile ham kök karşılaştırması)

### R-05 · N yuvarlama ve grup dağılımı  [REA] (yukarı yuvarlama [DOK])
- **Kural:** Ham (kesirli) kök N_ham, **grup sayısının bir sonraki katına
  yukarı** yuvarlanır: N = ⌈N_ham / k⌉ · k. Gruplar eşittir: n = N / k.
  (Kılavuz yalnızca "yukarı yuvarlanır" der; **k'nın katına** yuvarlama
  kılavuzda yoktur.) Hesaplanan 32 a priori oracle sonucunun tamamında N,
  k'nın katıdır ✓.
- **Kanıt:** LEDGER L-09, L-33, L-44
- **Test:** oracle V05 (k=3), V11 (k=2), V12 (k=4), V13 (k=5), V14 (k=10), V15, V16, V17

### R-06 · Minimum N (çok büyük f)  [REA] ✓ ORACLE
- **Kural:** R-05'ten sonra N < k + 1 ise N := k + 1 alınır ve R-05 ile yeniden
  yuvarlanır. Sonuç olarak a priori'de en küçük N = 2k'dır. Kök bulucunun
  başarısız olduğu (R-04 adım 3, aynı işaret) durumlar da buraya düşer; hata
  mesajı yoktur. ✓ V23, V47, V48 (k = 3 → N = 6).
- **Kanıt:** LEDGER L-11, L-14
- **Test:** oracle V21, V22, V23, V47, V48

### R-07 · Gerçekleşen güç  [DOK] (istisna [ORACLE])
- **Kural:** "Actual power", yuvarlanmış N ile R-03 formülünden yeniden
  hesaplanır (hedef gücün kendisi değildir). λ, df2 ve kritik F de
  yuvarlanmış N ile gösterilir. Normalde gerçekleşen güç ≥ hedef güçtür;
  **istisna:** çok küçük f'de (V52) hedefin bir birim altında gösterilebilir
  (bkz. R-18).
- **Kanıt:** LEDGER L-12, L-38, L-44
- **Test:** oracle V05, V15, V16, V17, V52

### R-08 · Doğrulama sırası ve hata davranışı  [REA]
- **Kural:** Kontroller sırayla yapılır; **ilk** başarısız kontrol tek mesaj
  üretir, hesap yapılmaz, hiçbir çıktı yazılmaz (G*Power'da başlığı
  `Input error` olan hata kutusu; çıktı alanları `?`).
  - A priori sırası: k → f → α → güç → güç ≥ α
  - Post hoc sırası: k → f → α → N > k
- **Kanıt:** LEDGER L-15, L-29
- **Test:** tests/ (birden çok geçersiz girdi → yalnızca ilk mesaj) · oracle V28–V33, V40, V49, V50

### R-09 · Grup sayısı k < 2  [REA] ✓ ORACLE
- **Kural:** (R-17 yuvarlamasından sonra) k ≤ 1 → mesaj metni:
  `There must be at least 2 groups.` ✓ V33
- **Kanıt:** LEDGER L-16, L-45
- **Test:** oracle V33

### R-10 · Etki büyüklüğü aralığı  [REA] ✓ ORACLE
- **Kural:** f aralık dışındaysa mesaj:
  `Effect size f is outside the admissible range (<alt>, <üst>).`
  - A priori: metin `(1e-06, 50)` → f = 0, f < 0 ve f > 50 hatadır ✓ V28, V29, V49.
  - Post hoc: metin `(0, 50)` → f < 0 hatadır ✓ V50; **f = 0 geçerlidir**,
    λ = 0 ve güç = α çıkar ✓ V43.
  - f = 50 geçerlidir ✓ V47.
- **Kanıt:** LEDGER L-17, L-24, L-30
- **Test:** oracle V28, V29, V43, V47, V49, V50

### R-11 · α ve güç aralığı  [REA] ✓ ORACLE
- **Kural:**
  - α ∉ [1e-7, 0,9999999] → `Alpha is outside the admissible range (1e-07, 1).` ✓ V30, V31
  - güç ∉ [1e-7, 0,9999999] → `Power is outside the admissible range (1e-07, 1).` ✓ V32
  - Mesajdaki üst sınır 6 anlamlı basamakla yazıldığı için `1` görünür.
- **Kanıt:** LEDGER L-18, L-19, L-30
- **Test:** oracle V30, V31, V32

### R-12 · Güç ve α ilişkisi  [REA] ✓ ORACLE
- **Kural:** α > güç → `Power must be greater than or equal to alpha.` ✓ V25
  **güç = α hata değildir**: hesap yapılır; f > 0 iken her N > k için güç > α
  olduğundan kök bulunamaz ve R-06 gereği **N = 2k** raporlanır ✓ V24.
- **Kanıt:** LEDGER L-20, L-23
- **Test:** oracle V24 (güç = α), V25 (güç < α)

### R-13 · Post hoc N ≤ k  [REA] ✓ ORACLE
- **Kural:** N ≤ k → mesaj (iki satır):
  `Sample size must be greater than` / `the number of groups (<k>).` ✓ V40
  N = k + 1 geçerlidir (df2 = 1) ✓ V39.
- **Kanıt:** LEDGER L-21
- **Test:** oracle V39 (N = k+1), V40 (N = k)

### R-14 · Post hoc, N k'ya bölünmüyor  [REA] ✓ ORACLE
- **Kural:** Hesap **verilen N ile** yapılır (λ = f²N, df2 = N − k; N
  yuvarlanmaz, düzeltilmez) ve tüm çıktılar gösterilir. Ek olarak bir
  **uyarı** (hata değil; G*Power'da başlığı `Please note` olan bilgi kutusu)
  verilir:
  `The total sample size (<N>) is not a multiple of` /
  `the number of groups (<k>). The analysis was` /
  `based on the average group size.`
  Çıkış başarılıdır. Bu uyarı a priori modda hiçbir zaman çıkmaz.
  ✓ V38 (N = 61), V39 (N = 4), V41 (N = 1000).
- **Kanıt:** LEDGER L-22, L-29, L-32
- **Test:** oracle V38, V39, V41

### R-15 · Gösterim hassasiyeti  [REA] ✓ ORACLE
- **Kural:**
  - Kesirli alanlar (λ, kritik F, güç): 0,01 < |x| < 100 ise **7 ondalık,
    yuvarlayarak** (`%.7f`, ör. `15.7500000`, `1.0000000`); |x| ≤ 0,01 veya
    |x| ≥ 100 ise **7 anlamlı basamak, sondaki sıfırlar ve gereksiz ondalık
    noktası atılmış** (`%.7g`). ✓ V23 λ `150`, V39 kritik F `199.5`,
    V47 λ `15000`, V48 λ `156.06`, V43 λ `0`.
  - Tamsayı alanları (df1, df2, toplam N): ⌊x + 0,5⌋ ile yuvarlanıp ondalıksız
    yazılır; |x| ≥ 10¹² ise 5 anlamlı basamak (`%.5g`). ✓ 42 hesaplanan vektörün tamamı.
  - JSON çıktısında sayılar tam hassasiyette verilebilir; oracle ile
    karşılaştırma bu kuralla biçimlendirilmiş metin üzerinden yapılmalıdır.
- **Kanıt:** LEDGER L-25, L-26, L-27
- **Test:** oracle V05, V15, V23, V39, V41, V43, V47, V48

### R-16 · Uzun hesap, kesme ve sayısal hata  [REA]
- **Kural:**
  - Zaman aşımı **yoktur**; hesap bitene kadar beklenir. Kullanıcı keserse
    `Calculation interrupted!` gösterilir ve çıktı verilmez.
  - Hesap sırasında sayısal istisna (ör. kayan nokta taşması, dağılım
    kodunun arama sınırı hatası) olursa çıktı verilmez; mesaj
    `G*Power was not able to compute the results.` /
    `Please try less extreme input parameters!` ya da
    `G*Power encountered an unknown internal error!…` olur.
  - Çok küçük f için tavan yoktur ✓ V18–V20, V51, V52.
- **Kanıt:** LEDGER L-28, L-29, L-31, L-37
- **Test:** oracle V18, V19, V20, V51, V52

### R-17 · Kesirli tamsayı girdileri (k ve post hoc N)  [REA] ✓ ORACLE
- **Kural:** Grup sayısı ve post hoc toplam örneklem tamsayı girdileridir;
  kesirli bir değer verilirse **en yakın tamsayıya, yarım yukarı** yuvarlanır:
  k := ⌊k + 0,5⌋, N := ⌊N + 0,5⌋. Yuvarlama **sessizdir** (uyarı yok) ve
  geçerlilik kontrolleri (R-09, R-13) ile tüm hesaplar yuvarlanmış değerle
  yapılır. ✓ V45 (k = 2,5 → 3), V46 (k = 2,4 → 2).
  - Sayı olarak çözümlenemeyen girdi hatadır (G*Power metni:
    `Input error (illegal character?)`).
- **Kanıt:** LEDGER L-35, L-36
- **Test:** oracle V45, V46 · önerilen yeni vektörler (bkz. §6)

### R-18 · Uç küçük f'de sayısal sapma  [ORACLE] (sebep [AJAN])
- **Kural:** f çok küçük olduğunda (df2 ~10⁹) G*Power'ın merkezi olmayan F
  hesabı sayısal gürültü içerir; bu yüzden G*Power'ın raporladığı N ve
  gerçekleşen güç, tam doğru bir hesaptan son basamaklarda ayrılabilir ve
  gerçekleşen güç hedefin altında görünebilir (V52: `0.7999999` < 0,80).
  - Yeniden yazım bu gürültüyü **taklit etmek zorunda değildir**; doğru bir
    hesap yapmalıdır. V52 (ve df2 ~10⁸ üstü benzer vektörler) diferansiyel
    testte "bilinen sayısal sapma" olarak işaretlenmeli ve uyuşmazlık
    README'de açıklanmalıdır.
  - Sebep hipotezi [AJAN]: büyük df2'de log-gamma farklarındaki yuvarlama
    hatası güce ~10⁻⁷ genlikli gürültü ekler; N'yi k kadar artırmanın etkisi
    bundan çok küçüktür. Kök bulucu tek başına sebep değildir.
- **Kanıt:** LEDGER L-37, L-38, L-39
- **Test:** oracle V51, V52 · kütüphane katmanında yüksek hassasiyetli referans

## 4. Kabul kriterleri (Gherkin)

```gherkin
Özellik: anova-oneway a priori örneklem büyüklüğü

  Senaryo: Cohen orta etki, üç tedavi kolu
    Diyelim ki test "anova-oneway" ve mod "a-priori"
    Ve f = 0.25, α = 0.05, güç = 0.95, grup = 3
    O zaman n_total G*Power oracle V05 ile birebir aynıdır
    Ve actual_power, critical, ncp G*Power'ın gösterdiği hane kadar eşleşir

  Senaryo: Kılavuz örneği, on grup (R-03, R-05)
    Diyelim ki mod "a-priori", f = 0.25, α = 0.05, güç = 0.95, grup = 10
    O zaman tüm çıktılar oracle V14 ile aynıdır

  Senaryo: N grup sayısının katına yukarı yuvarlanır (R-05)
    Diyelim ki mod "a-priori" ve oracle vektörü V15, V16 veya V17
    O zaman n_total, grup sayısına tam bölünür
    Ve n_total oracle ile birebir aynıdır
    Ve n_per_group = n_total / groups

  Senaryo: k = 2 iki bağımsız grup t testine denktir
    Diyelim ki f = 0.25, α = 0.05, güç = 0.95, grup = 2
    O zaman n_total oracle V11 ile aynıdır

  Senaryo: Çok büyük etki minimum N'e iner (R-06)
    Diyelim ki mod "a-priori", α = 0.05, grup = 3
    Ve f, oracle V23, V47 veya V48'deki değerdir
    O zaman n_total = 2 × groups olur ve oracle ile aynıdır

  Senaryo: Güç = α hata değildir (R-12)
    Diyelim ki mod "a-priori" ve f = 0.25, α = 0.05, güç = 0.05, grup = 3
    O zaman hata çıkmaz ve n_total oracle V24 ile aynıdır (2 × groups)

  Senaryo: Güç < α hatadır (R-12)
    Diyelim ki mod "a-priori" ve güç = 0.03, α = 0.05
    O zaman çıkış kodu sıfırdan farklıdır
    Ve mesaj "Power must be greater than or equal to alpha." olur

  Senaryo: f sınırları (R-10)
    Eğer mod "a-priori" ve f = 0 ise mesaj "Effect size f is outside the admissible range (1e-06, 50)." olur
    Eğer mod "a-priori" ve f = 50 ise hata çıkmaz (oracle V47)
    Eğer mod "a-priori" ve f = 50.01 ise mesaj oracle V49 ile aynıdır
    Eğer mod "post-hoc" ve f = -0.1 ise mesaj "Effect size f is outside the admissible range (0, 50)." olur
    Eğer mod "post-hoc", f = 0, N = 60, grup = 3 ise hata çıkmaz ve actual_power oracle V43 ile aynıdır

  Senaryo: α ve güç sınırları (R-11)
    Eğer α = 0 veya α = 1 ise mesaj "Alpha is outside the admissible range (1e-07, 1)." olur
    Eğer güç = 1 ise mesaj "Power is outside the admissible range (1e-07, 1)." olur

  Senaryo: Kesirli grup sayısı yarım yukarı yuvarlanır (R-17)
    Diyelim ki mod "a-priori", f = 0.25, α = 0.05, güç = 0.95
    Eğer grup = 2.5 ise tüm çıktılar oracle V45 ile (grup = 3 sonucu) aynıdır
    Eğer grup = 2.4 ise tüm çıktılar oracle V46 ile (grup = 2 sonucu) aynıdır
    Ve hiçbir uyarı verilmez

  Senaryo: 100 ve üstü değerler 7 anlamlı basamakla gösterilir (R-15)
    Diyelim ki oracle vektörü V23, V39, V47 veya V48
    O zaman biçimlendirilmiş ncp / critical metni oracle'daki metinle birebir aynıdır

  Senaryo: Post hoc'ta N grup sayısına bölünmüyor (R-14)
    Diyelim ki mod "post-hoc", f = 0.25, α = 0.05, N = 61, grup = 3
    O zaman actual_power, df2 ve ncp N = 61 ile hesaplanır (oracle V38)
    Ve "not a multiple of" içeren bir uyarı verilir ama çıkış kodu 0'dır

  Senaryo: Post hoc'ta N = k hatadır, N = k + 1 değildir (R-13)
    Eğer mod "post-hoc", N = 3, grup = 3 ise mesaj "Sample size must be greater than" ile başlar (oracle V40)
    Eğer mod "post-hoc", N = 4, grup = 3 ise hesap yapılır ve oracle V39 ile aynıdır

  Senaryo: Tek grup hatadır (R-09)
    Diyelim ki grup = 1
    O zaman mesaj "There must be at least 2 groups." olur (oracle V33)

  Senaryo: Doğrulama sırası (R-08)
    Diyelim ki mod "a-priori", grup = 1 ve f = 0
    O zaman yalnızca "There must be at least 2 groups." mesajı verilir

  Senaryo: Uç küçük f bilinen sayısal sapmadır (R-18)
    Diyelim ki mod "a-priori", f = 0.0001, α = 0.05, güç = 0.80, grup = 3
    O zaman hesap hatasız tamamlanır ve n_total grup sayısının katıdır
    Ve oracle V52 ile uyuşmazlık "bilinen sayısal sapma" olarak raporlanır
```

## 5. Bilinmeyenler

| Konu | Neden bilinmiyor | Nasıl sınanacak |
|------|------------------|-----------------|
| V52'de tam doğru güç ve doğru minimum N | G*Power değeri sayısal gürültü içeriyor (R-18); gürültü genliği gözlenmedi. Güç N ile arttığı için, tam güç(963468906) < 0,80 ise doğru minimum N **daha büyük** bir 3 katıdır; ≥ 0,80 ise G*Power değeri doğrudur ve yalnızca gösterilen güç hatalıdır | Kütüphane katmanında yüksek hassasiyetli merkezi olmayan F ile güç(963468906) ve komşu 3 katlarını hesaplamak; V51/V52 arasına ek f değerleriyle (ör. 0,0005, 0,0002) sapmanın başladığı yeri bulmak |
| f ≈ 1e-6 (a priori alt sınırı) davranışı | Taşma/dağılım hatası olası ama sınanmadı | Yeni GUI vektörü: f = 0,000001, güç 0,80, k = 3 |
| Hangi istisna "not able to compute", hangisi "unknown internal error" verir | İstisna türü eşlemesi izlenmedi; oracle'da istisna üreten vektör yok | Uç girdiler (f = 1e-6, çok büyük k) ile GUI denemesi |
| Birden çok geçersiz girdide yalnızca ilk mesaj mı | Sıra kodda görüldü; oracle'da bu tip vektör yok | Yeni GUI vektörü: grup = 1 ve f = 0 birlikte |
| Kesirli post hoc N (ör. 60,5) ve k = 1,5 / k = 0,6 gibi sınır yuvarlamaları | Okuyucu kodu aynı (R-17) ama oracle'da yalnızca k = 2,5 / 2,4 var | Yeni GUI vektörleri (bkz. §6) |
| Ham N'in tam k katına denk geldiği kayan nokta sınırı (R-05) | Ceil'de epsilon koruması yok; böyle bir girdi bilinmiyor | Kütüphane vektörlerinde ham N'i tamsayı katına çok yakın olan satırları aramak |
| df/N alanlarının "tamsayı" bayrağının koddaki kaynağı | İzlenmedi; davranış oracle ile kesin (R-15) | Gerekmez — yeniden yazım için davranış yeterli |

## 6. Öncelikli vektörler (sonraki tur)

Mevcut 52 vektörün tamamı dolduruldu. Önce şunlar girilmeli/hesaplanmalı:

| Sıra | Vektör (öneri) | Katman | Neyi doğrular |
|------|----------------|--------|---------------|
| 1 | V52'nin yüksek hassasiyetli referansı + f = 0,0005 / 0,0002 / 0,00005 (a priori, güç 0,80, k = 3) | Kütüphane + GUI | R-18: sapmanın başladığı f ve doğru N |
| 2 | f = 0,000001, α = 0,05, güç = 0,80, k = 3 (a priori) | GUI | R-16/R-18: alt sınırda hata mı sonuç mu |
| 3 | grup = 1 ve f = 0 (a priori) | GUI | R-08: yalnızca ilk mesaj |
| 4 | post hoc f = 0,25, α = 0,05, N = 60,5, k = 3 | GUI | R-17: N yarım yukarı → 61 (+ R-14 uyarısı) |
| 5 | a priori grup = 1,5 ve grup = 1,4 | GUI | R-17 + R-09: 1,5 → 2 (geçerli), 1,4 → 1 (hata) |
| 6 | post hoc f = 0,5, N = 600, k = 3 | GUI | R-15: λ ≥ 100 post hoc'ta `%g` |
| 7 | post hoc f = 0,01, α = 0,005, N = 30, k = 3 | GUI | R-15: güç ≤ 0,01 → `%g` |
| 8 | a priori f = 0,25, α = 0,05, güç = 0,95, k = 7 | GUI | R-05: büyük k'da kat yuvarlaması |
