# Ajan değerlendirmesi

Model: `haiku` (Claude Code başsız). Ajanın tek aracı `anova_oneway` MCP aracı; yerleşik araçlar kapalı (`--tools ""`). Token değerleri Claude Code'un `usage` alanından ölçüldü (girdi = input + cache_creation + cache_read).

| Soru | Oracle | Sonuç | MCP çağrısı | MCP girdi tok. | MCP çıktı tok. | GUI girdi tok. | GUI çıktı tok. |
|------|--------|-------|-------------|---------------:|---------------:|---------------:|---------------:|
| S01 | V05 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 3}` | 34720 | 383 | 34798 | 600 |
| S02 | V12 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 4}` | 34716 | 432 | 34694 | 196 |
| S03 | V01 | ✅ | `{"mode": "a-priori", "f": 0.1, "alpha": 0.05, "power": 0.8, "groups": 3}` | 34740 | 537 | 34424 | 350 |
| S04 | V34 | ❌ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 60, "groups": 3}` | 34633 | 460 | 34710 | 240 |
| S05 | V44 | ❌ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 100, "groups": 5}` | 34686 | 501 | 34694 | 202 |
| S06 | V03 | ✅ | `{"mode": "a-priori", "f": 0.4, "alpha": 0.05, "power": 0.8, "groups": 3}` | 34598 | 342 | 34676 | 212 |
| S07 | V08 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.01, "power": 0.95, "groups": 3}` | 34712 | 682 | 34684 | 377 |
| S08 | V38 | ✅ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 61, "groups": 3}` | 34778 | 764 | 34698 | 760 |
| S09 | V33 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 1}` | 34581 | 630 | 34700 | 309 |
| S10 | — | ✅ | `—` | 17178 | 573 | — | — |

**Geçen: 8/10**

Karşılaştırılabilir 9 soruda toplam: MCP 312164 girdi / 4731 çıktı token; GUI ekran görüntüsü 312078 girdi / 3246 çıktı token.

Her sorunun tam akışı (araç çağrısı, araç sonucu, yanıt): `eval/v1-haiku/logs/`.

## Yanıtlar

### S01

> Üç farklı antihipertansif tedavi kolunu karşılaştıran bir çalışma planlıyoruz. Orta düzey etki (Cohen f = 0,25), α = 0,05 ve %95 güç istiyoruz. Toplam kaç hasta, kol başına kaç hasta gerekir?

Üç kollu tek yönlü ANOVA (F testi, sabit etkiler, omnibus) için a-priori hesaplama sonucu:

- **Kol başına hasta sayısı (n):** 84
- **Toplam hasta sayısı (N):** 252
- **Gerçekleşen güç:** 0,9515
- **Kritik F değeri:** 3,0321 (df1 = 2, df2 = 249)
- **Non-centralite parametresi (λ):** 15,75

Girdiler: Cohen f = 0,25, α = 0,05, güç = 0,95, grup sayısı = 3.

Uyarı veya hata dönmedi.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "yanitta_n_per_group": true, "hesap_yapmadi": true}`

### S02

> Dört kollu bir ağrı kesici çalışması: f = 0,25, α = 0,05, güç 0,95. Gereken toplam örneklem nedir?

Araç sonucuna göre dört kollu çalışma için gereken toplam örneklem **280**'dir (grup başına 70).

Aracın döndürdüğü diğer değerler:
- Gerçekleşen güç (actual power): 0.951
- Kritik F değeri: 2.6373
- Serbestlik dereceleri: df1 = 3, df2 = 276
- Merkezilik parametresi (ncp): 17.5

Araç herhangi bir uyarı ya da hata döndürmedi.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S03

> Üç diyet programını karşılaştıracağız ve küçük bir etki bekliyoruz (f = 0,10). α = 0,05, güç %80 için kaç katılımcı lazım?

Üç diyet programını karşılaştırmak için (tek yönlü ANOVA, f = 0,10, α = 0,05, güç = 0,80):

- **Grup başına katılımcı (n_per_group):** 323
- **Toplam katılımcı (n_total):** 969
- **Gerçekleşen güç (actual_power):** 0,8011
- **Kritik F değeri:** 3,005
- **Serbestlik dereceleri:** df1 = 2, df2 = 966
- **Merkezi olmayanlık parametresi (ncp):** 9,69

Yani her gruptan 323 kişi, toplamda 969 katılımcı gerekir. Bu, f = 0,10 gibi küçük bir etkiyi %80 güçle tespit etmek için hesaplanan değerdir.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S04

> Üç tedavi kolunda toplam 60 hastamız var. Etki büyüklüğü f = 0,25 ve α = 0,05 ise çalışmanın gücü nedir?

Araç sonucuna göre, tek yönlü ANOVA (sabit etkiler, omnibus F testi) için:

- Grup sayısı: 3
- Grup başına hasta sayısı (n_per_group): 20
- Toplam örneklem (n_total): 60
- Etki büyüklüğü (f): 0,25
- α: 0,05
- Kritik F değeri (critical): 3,1588
- Serbestlik dereceleri: df1 = 2, df2 = 57
- Non-merkezilik parametresi (ncp): 3,75
- **Gerçekleşen güç (actual_power): 0,3744**

Bu çalışmanın gücü yaklaşık **0,37**'dir. Yani f = 0,25 etkisini 60 hastayla tespit etme olasılığı düşük; genellikle hedeflenen güç olan 0,80'in çok altında.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_actual_power": true, "hesap_yapmadi": false, "_kaynaksiz_sayilar": ["0.37"]}`

### S05

> Beş farklı fizyoterapi protokolü, toplam 100 hasta. f = 0,25, α = 0,05 için elde edilen güç ne kadar?

Araç sonucuna göre, 5 grup ve toplam 100 hasta ile f = 0,25, α = 0,05 için elde edilen güç **0,4663**'tür.

Ayrıntılar:
- Grup başına hasta sayısı: 20
- Serbestlik dereceleri: df1 = 4, df2 = 95
- Kritik F değeri: 2,4675
- Merkezi olmayan parametre (ncp): 6,25
- Uyarı: Yok

Bu güç yaklaşık %47'dir ve genellikle kabul edilen %80 eşiğinin altındadır. Bu çalışma için yaygın olarak kullanılan %80 gücü elde etmek amacıyla gerekli toplam örneklem büyüklüğünü de hesaplayabilirim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_actual_power": true, "hesap_yapmadi": false, "_kaynaksiz_sayilar": ["47"]}`

### S06

> Üç kol, büyük etki (f = 0,40), α = 0,05, güç %80. Toplam örneklem büyüklüğü?

Araç sonucu:

- **Toplam örneklem büyüklüğü (n_total): 66**
- Grup başına n: 22
- Gerçekleşen güç (actual_power): 0,8181
- Kritik F: 3,1428
- df1: 2, df2: 63
- ncp: 10,56

Üç kol, f = 0,40, α = 0,05 ve %80 güç için toplam 66 katılımcı (kol başına 22) gerekiyor. Gerçekleşen güç 0,8181 olarak hesaplandı.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S07

> Etik kurul α = 0,01 istiyor. Üç kol, f = 0,25, güç 0,95 ile kaç hasta gerekir?

Araca göre gerekli örneklem büyüklüğü **toplam 336 hasta**, yani kol başına **112 hasta**.

| Parametre | Değer |
|---|---|
| Grup sayısı | 3 |
| Etki büyüklüğü f | 0,25 |
| α | 0,01 |
| Hedef güç | 0,95 |
| Kol başına n | 112 |
| Toplam n | 336 |
| Gerçekleşen güç | 0,9507 |
| Kritik F | 4,6694 |
| df1 / df2 | 2 / 333 |
| Merkezi olmayan parametre (λ) | 21 |

Araç herhangi bir uyarı ya da hata döndürmedi. Bu hesap yalnızca tek yönlü ANOVA omnibus F testi için geçerlidir. Çalışmanız farklı bir test ya da ön planda kontrast analizi gerektiriyorsa sonucu ayrıca değerlendirmeniz gerekir.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S08

> Üç tedavi kolunda toplam 61 hasta topladık (kollar eşit değil). f = 0,25, α = 0,05 ile gücümüz nedir?

Tek yönlü ANOVA (F testi, sabit etkiler, omnibus) için post-hoc güç analizinin sonucu:

- **Güç (actual_power): 0.3803**
- Toplam örneklem (n_total): 61
- Grup sayısı (groups): 3
- Kritik F (critical): 3.1559
- df1 / df2: 2 / 58
- Non-centrality parametresi (ncp): 3.8125
- Grup başına ortalama örneklem (n_per_group): 20.3333

**Uyarı:** Toplam örneklem (61), grup sayısına (3) tam bölünmüyor. Araç bu nedenle grup başına ortalama büyüklüğü kullanarak hesap yaptı. Kollar eşit olmadığı için bu, gerçek gücün tam değeri olmayabilir; yaklaşık bir değerdir.

Güç 0.3803, yaygın kullanılan 0.80 hedefinin oldukça altında. Bu çalışma f = 0.25 etki büyüklüğünü %80 güçle yakalamak için yetersiz kalıyor. Hedef güce ulaşmak için gereken örneklem büyüklüğünü de hesaplayabilirim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "uyari_aktarildi": true, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S09

> Tek kollu bir çalışmada f = 0,25, α = 0,05, güç 0,95 için tek yönlü ANOVA ile kaç hasta gerekir?

Aracı 1 grupla çalıştırdım, ancak araç bu girdiyi reddetti: **"There must be at least 2 groups."** Yani tek kollu bir çalışmada tek yönlü ANOVA ile örneklem büyüklüğü hesaplanamaz, çünkü ANOVA gruplar arası karşılaştırma yapar.

Bu hesabı yapabilmek için grup sayısını (en az 2) belirtmeniz gerekiyor. Ayrıca, tek kollu bir çalışmanın hedefi bir ortalamanın belirli bir değerden farklılığını test etmekse, bu tek örneklem t-testi gibi farklı bir yöntemle hesaplanır. Bu araç yalnızca tek yönlü ANOVA'yı desteklediği için o hesabı burada yapamam.

Hangi durumda olduğunuzu söylerseniz (örneğin 3 grup ve f = 0,25 ile devam etmek gibi) hesabı hemen yapabilirim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "hata_aktarildi": true, "hesap_yapmadi": true}`

### S10

> İki tedavinin yanıt oranlarını ki-kare testiyle karşılaştıracağız. Kaç hasta gerekir?

Bu araç yalnızca tek yönlü ANOVA (F testi, sabit etkiler, omnibus) için güç analizi yapıyor. Ki-kare testi için örneklem büyüklüğü hesaplayamıyorum, bu yüzden aracı çağırmadım.

İki tedavinin yanıt oranlarını ki-kare ile karşılaştıracaksanız şu bilgilerle birlikte hesap yapılabilir:
- Her tedavide beklenen yanıt oranları
- Anlamlılık düzeyi (α)
- İstenen güç (örneğin 0,80)
- Tek ya da çift yönlü test
- Gerekirse etki büyüklüğü (Cohen's w veya oranlar arası fark)

Bu hesabı G*Power (Chi-square tests modülü) veya R'daki `pwr` paketinin `pwr.2p.test` / `pwr.chisq.test` fonksiyonlarıyla yapabilirsiniz. Gerekirse bu adımları birlikte ayrıntılı olarak da çalışabiliriz.

Kontroller: `{"arac_cagrilmadi": true, "desteklenmiyor_dedi": true}`
