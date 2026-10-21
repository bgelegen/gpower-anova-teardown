# Ajan değerlendirmesi

Model: `haiku` (Claude Code başsız). Ajanın tek aracı `anova_oneway` MCP aracı; yerleşik araçlar kapalı (`--tools ""`). Token değerleri Claude Code'un `usage` alanından ölçüldü (girdi = input + cache_creation + cache_read).

| Soru | Oracle | Sonuç | MCP çağrısı | MCP girdi tok. | MCP çıktı tok. | GUI girdi tok. | GUI çıktı tok. |
|------|--------|-------|-------------|---------------:|---------------:|---------------:|---------------:|
| S01 | V05 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 3}` | 13638 | 546 | 13504 | 603 |
| S02 | V12 | ❌ | `{"mode": "a-priori", "f": "0,25", "alpha": "0,05", "power": "0,95", "groups": 4}` | 20731 | 729 | 13400 | 214 |
| S03 | V01 | ❌ | `{"mode": "a-priori", "f": "0,10", "alpha": "0,05", "power": "0,80", "groups": 3}` | 20867 | 1087 | 13130 | 394 |
| S04 | V34 | ❌ | `{"mode": "post-hoc", "f": "0,25", "alpha": "0,05", "n_total": 60, "groups": 3}` | 20810 | 932 | 13416 | 397 |
| S05 | V44 | ✅ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 100, "groups": 5}` | 13664 | 665 | 13400 | 342 |
| S06 | V03 | ❌ | `{"mode": "a-priori", "f": "0,40", "alpha": "0,05", "power": "0,80", "groups": 3}` | 20738 | 817 | 13382 | 233 |
| S07 | V08 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.01, "power": 0.95, "groups": 3}` | 13522 | 481 | 13390 | 380 |
| S08 | V38 | ❌ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 61, "groups": 3}` | 13699 | 900 | 13404 | 780 |
| S09 | V33 | ❌ | `{"mode": "a-priori", "f": "0,25", "alpha": "0,05", "power": "0,95", "groups": 1}` | 13499 | 604 | 13406 | 434 |
| S10 | — | ✅ | `—` | 6637 | 495 | — | — |

**Geçen: 4/10**

Karşılaştırılabilir 9 soruda toplam: MCP 151168 girdi / 6761 çıktı token; GUI ekran görüntüsü 120432 girdi / 3777 çıktı token.

Her sorunun tam akışı (araç çağrısı, araç sonucu, yanıt): `eval/v3a-haiku/logs/`.

## Yanıtlar

### S01

> Üç farklı antihipertansif tedavi kolunu karşılaştıran bir çalışma planlıyoruz. Orta düzey etki (Cohen f = 0,25), α = 0,05 ve %95 güç istiyoruz. Toplam kaç hasta, kol başına kaç hasta gerekir?

**Sonuç (tek yönlü ANOVA, F testi, sabit etkiler):**

- **Kol başına hasta sayısı:** 84
- **Toplam hasta sayısı:** 252

**Doğrulama değerleri:**
- Gerçekleşen güç: 0.9515
- Kritik F değeri: 3.0321
- Serbestlik dereceleri: df1 = 2, df2 = 249
- Merkezi olmayan parametre (λ): 15.75

Gerçekleşen güç (0.9515), hedeflenen 0.95'in üzerinde olduğu için 84 kişilik kollar bu hedefi karşılıyor.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "yanitta_n_per_group": true, "hesap_yapmadi": true}`

### S02

> Dört kollu bir ağrı kesici çalışması: f = 0,25, α = 0,05, güç 0,95. Gereken toplam örneklem nedir?

Araç sonucuna göre gereken toplam örneklem **280**'dir (grup başına **70**, 4 grup).

Araçtan dönen ayrıntılar:
- n_per_group: 70
- n_total: 280
- actual_power: 0.951
- critical: 2.6373
- df1: 3
- df2: 276
- ncp: 17.5

Not: İlk çağrıda ondalık sayıları virgülle (0,25) gönderdim ve araç bunu girdi hatası olarak reddetti. Değerleri nokta ile (0.25, 0.05, 0.95) yeniden gönderdim; değerler aynı kaldı.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": false, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S03

> Üç diyet programını karşılaştıracağız ve küçük bir etki bekliyoruz (f = 0,10). α = 0,05, güç %80 için kaç katılımcı lazım?

Üç grup için, f = 0.1, α = 0.05 ve hedef güç 0.8 ile gereken toplam örneklem büyüklüğü aracın sonucuna göre:

- **Grup başına katılımcı (n_per_group):** 323
- **Toplam katılımcı (n_total):** 969
- **Gerçekleşen güç (actual_power):** 0.8011
- **Kritik F değeri (critical):** 3.005
- **Serbestlik dereceleri:** df1 = 2, df2 = 966
- **Merkezi olmayışlık parametresi (ncp):** 9.69

Üç diyet programını karşılaştırmak için her gruba 323 kişi, toplamda 969 katılımcı gerekiyor. Bu, tek yönlü ANOVA F testi için hesaplanmıştır.

Aracı ilk denediğimde "0,10" biçimindeki virgüllü ondalık sayılar hata verdi. Değerleri değiştirmeden noktalı biçimde ("0.1", "0.05", "0.8") yeniden gönderdim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": false, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S04

> Üç tedavi kolunda toplam 60 hastamız var. Etki büyüklüğü f = 0,25 ve α = 0,05 ise çalışmanın gücü nedir?

Çalışmanın gücü **0,3744**'tür.

Araç sonuçları:
- Grup başına hasta sayısı: 20
- Toplam hasta sayısı: 60
- Gerçek güç (actual_power): 0,3744
- Kritik F değeri: 3,1588
- Serbestlik dereceleri: df1 = 2, df2 = 57
- Merkezsizlik parametresi (ncp): 3,75

Gücün 0,80'in altında olduğu için bu çalışma f = 0,25 gibi orta büyüklükteki bir etkiyi yeterince güvenilir biçimde saptayamaz. Yaygın hedef olan %80 gücü için daha fazla hastaya ihtiyaç var. Bunu hesaplamak isterseniz a priori analiz yapabilirim.

Not: İlk çağrıda ondalık ayracı olarak virgül kullandığım için araç girdi hatası döndü. Değerleri nokta ile (0.25, 0.05) yeniden gönderdim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": false, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S05

> Beş farklı fizyoterapi protokolü, toplam 100 hasta. f = 0,25, α = 0,05 için elde edilen güç ne kadar?

Tek yönlü ANOVA post-hoc analizinin sonucu aşağıdaki gibidir (f = 0.25, α = 0.05, toplam n = 100, 5 grup):

- **Gözlenen güç (actual_power): 0.4663**
- Grup başına hasta sayısı (n_per_group): 20
- Serbestlik dereceleri: df1 = 4, df2 = 95
- Kritik F değeri (critical): 2.4675
- Merkezi olmayan parametre (ncp): 6.25

Bu tasarımın gücü 0.4663'tür ve yaygın olarak kabul edilen 0.80 eşiğinin oldukça altındadır. Yani 100 hasta ile beş protokolün gerçek etki büyüklüğü f = 0.25 ise, farkı tespit etme olasılığı düşüktür.

Aracın çıktısında herhangi bir uyarı veya hata yoktu.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S06

> Üç kol, büyük etki (f = 0,40), α = 0,05, güç %80. Toplam örneklem büyüklüğü?

Üç kol, f = 0.4, α = 0.05 ve güç 0.8 için araç toplam **n_total = 66** döndürdü (grup başına n_per_group = 22).

Aracın döndürdüğü diğer değerler:
- Gerçekleşen güç (actual_power): 0.8181
- Kritik F değeri (critical): 3.1428
- Serbestlik dereceleri: df1 = 2, df2 = 63
- Merkezi olmayan parametre (ncp): 10.56

Not: İlk çağrıda ondalık virgül (0,40) kullandığım için araç girdi hatası verdi. Değerleri nokta ile (0.4, 0.05, 0.8) tekrar gönderdim; değerler aynıdır.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": false, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S07

> Etik kurul α = 0,01 istiyor. Üç kol, f = 0,25, güç 0,95 ile kaç hasta gerekir?

Üç kollu tek yönlü ANOVA için (f = 0,25, α = 0,01, güç = 0,95) gereken toplam örneklem büyüklüğü **336** hastadır. Kol başına **112** hasta düşer.

Aracın döndürdüğü ayrıntılar:
- Kol başına n: 112
- Toplam N: 336
- Gerçekleşen güç: 0.9507
- Kritik F değeri: 4.6694
- Serbestlik dereceleri: df1 = 2, df2 = 333
- Merkezi olmayan parametre (λ): 21

Gerçekleşen güç (0.9507), istenen 0,95'in biraz üzerindedir; çünkü kol başına hasta sayısı tam sayıya yuvarlanmıştır.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S08

> Üç tedavi kolunda toplam 61 hasta topladık (kollar eşit değil). f = 0,25, α = 0,05 ile gücümüz nedir?

**Post-hoc güç analizi (tek yönlü ANOVA, F testi, sabit etkiler)**

Girdiler: f = 0,25, α = 0,05, toplam N = 61, grup sayısı = 3.

- **Güç (actual_power): 0,3803**
- Kritik F: 3,1559
- df1 = 2, df2 = 58
- Merkezi parametre (ncp): 3,8125
- Grup başına ortalama n: 20,3333

**Uyarı:** Toplam örneklem büyüklüğü (61), grup sayısına (3) tam bölünmüyor. Analiz ortalama grup büyüklüğü üzerinden yapıldı. Kollar eşit olmadığı için gerçek güç bu değerden farklı olabilir. Kesin sonuç için kol bazında gerçek n değerlerini (ör. 20, 20, 21 gibi) girmek gerekir, ancak bu aracın tek yönlü ANOVA girişi toplam N ve grup sayısını aldığı için kol bazlı hesap bu araçla yapılamıyor.

Sonuç olarak, bu tasarımın f = 0,25 etki büyüklüğünü α = 0,05'te yakalama gücü **0,3803**, yani yaklaşık %38 değil, aracın verdiği değer olarak 0,3803 ile düşük. Yaygın hedef olan 0,80 güce ulaşmak için bu etki büyüklüğünde çok daha fazla hastaya ihtiyaç var.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "uyari_aktarildi": true, "yanitta_actual_power": true, "hesap_yapmadi": false, "_kaynaksiz_sayilar": ["20", "21", "38"]}`

### S09

> Tek kollu bir çalışmada f = 0,25, α = 0,05, güç 0,95 için tek yönlü ANOVA ile kaç hasta gerekir?

Tek kollu bir çalışmada tek yönlü ANOVA ile örneklem büyüklüğü hesaplanamıyor. Araç, "En az 2 grup olmalı." hatasını döndürdü. Tek yönlü ANOVA en az iki grup karşılaştırması gerektirir.

Çalışmanızda birden fazla grup varsa (ör. kontrol ve tedavi kolları), grup sayısını belirtirseniz f = 0,25, α = 0,05 ve güç = 0,95 değerleriyle hesabı yeniden yapabilirim. Tek bir grubun ortalamasını bilinen bir değerle karşılaştırıyorsanız bu, ANOVA değil başka bir test (ör. tek örneklem t testi) gerektirir; bu test desteklenmediği için hesaplama yapamam.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": false, "hata_aktarildi": true, "hesap_yapmadi": true}`

### S10

> İki tedavinin yanıt oranlarını ki-kare testiyle karşılaştıracağız. Kaç hasta gerekir?

Bu araçla ki-kare testi için örneklem büyüklüğü hesaplayamıyorum. Desteklediğim tek test tek yönlü ANOVA'dır (F testi, sabit etkiler, omnibus). İki tedavinin yanıt oranlarını ki-kare ile karşılaştırmak için gereken hasta sayısını bu araçtan alamam. Bu hesabı G*Power'da "Exact" ya da "χ² tests" bölümünden, ya da R'da `pwr.2p.test` ile yapabilirsiniz.

Üç ortalama ya da daha fazla grubun sürekli bir sonucunu karşılaştırmak isterseniz, etki büyüklüğü (f), alfa, güç ve grup sayısıyla örneklem büyüklüğünü hesaplayabilirim.

Kontroller: `{"arac_cagrilmadi": true, "desteklenmiyor_dedi": true}`
