# Ajan değerlendirmesi

Model: `haiku` (Claude Code başsız). Ajanın tek aracı `anova_oneway` MCP aracı; yerleşik araçlar kapalı (`--tools ""`). Token değerleri Claude Code'un `usage` alanından ölçüldü (girdi = input + cache_creation + cache_read).

| Soru | Oracle | Sonuç | MCP çağrısı | MCP girdi tok. | MCP çıktı tok. | GUI girdi tok. | GUI çıktı tok. |
|------|--------|-------|-------------|---------------:|---------------:|---------------:|---------------:|
| S01 | V05 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 3}` | 34932 | 563 | 34798 | 368 |
| S02 | V12 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 4}` | 34827 | 397 | 34694 | 198 |
| S03 | V01 | ✅ | `{"mode": "a-priori", "f": 0.1, "alpha": 0.05, "power": 0.8, "groups": 3}` | 34847 | 404 | 34424 | 362 |
| S04 | V34 | ✅ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 60, "groups": 3}` | 34845 | 451 | 34710 | 257 |
| S05 | V44 | ✅ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 100, "groups": 5}` | 34829 | 407 | 34694 | 285 |
| S06 | V03 | ✅ | `{"mode": "a-priori", "f": 0.4, "alpha": 0.05, "power": 0.8, "groups": 3}` | 34810 | 367 | 34676 | 201 |
| S07 | V08 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.01, "power": 0.95, "groups": 3}` | 34816 | 487 | 34684 | 216 |
| S08 | V38 | ✅ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 61, "groups": 3}` | 35018 | 835 | 34698 | 596 |
| S09 | V33 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 1}` | 34793 | 648 | 34700 | 359 |
| S10 | — | ✅ | `—` | 17284 | 678 | — | — |

**Geçen: 10/10**

Karşılaştırılabilir 9 soruda toplam: MCP 313717 girdi / 4559 çıktı token; GUI ekran görüntüsü 312078 girdi / 2842 çıktı token.

Her sorunun tam akışı (araç çağrısı, araç sonucu, yanıt): `eval/logs/`.

## Yanıtlar

### S01

> Üç farklı antihipertansif tedavi kolunu karşılaştıran bir çalışma planlıyoruz. Orta düzey etki (Cohen f = 0,25), α = 0,05 ve %95 güç istiyoruz. Toplam kaç hasta, kol başına kaç hasta gerekir?

Üç kollu tek yönlü ANOVA için gerekli örneklem büyüklüğü:

- **Kol başına hasta sayısı (n):** 84
- **Toplam hasta sayısı (N):** 252

Hesaplama parametreleri ve çıktılar:

- Etki büyüklüğü (f): 0,25
- α: 0,05
- Hedef güç: 0,95
- Gerçekleşen güç (actual_power): 0,9515
- Kritik F değeri: 3,0321
- Serbestlik dereceleri: df1 = 2, df2 = 249
- Merkezi olmayan parametre (ncp): 15,75

Gerçekleşen güç hedeflenen 0,95'in biraz üzerinde, çünkü kol başına hasta sayısı tam sayıya yuvarlanıyor.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "yanitta_n_per_group": true, "hesap_yapmadi": true}`

### S02

> Dört kollu bir ağrı kesici çalışması: f = 0,25, α = 0,05, güç 0,95. Gereken toplam örneklem nedir?

Dört grup, f = 0,25, α = 0,05 ve güç = 0,95 için gereken toplam örneklem **280**'dir.

- Grup başına örneklem (n_per_group): 70
- Toplam örneklem (n_total): 280
- Gerçekleşen güç (actual_power): 0.951
- Kritik F değeri (critical): 2.6373
- df1: 3, df2: 276
- Merkezi olmayanlık parametresi (ncp): 17.5

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S03

> Üç diyet programını karşılaştıracağız ve küçük bir etki bekliyoruz (f = 0,10). α = 0,05, güç %80 için kaç katılımcı lazım?

Üç grup, f = 0,10, α = 0,05 ve hedef güç 0,8 için gereken toplam örneklem büyüklüğü **969** katılımcıdır. Her gruba **323** katılımcı düşer.

Aracın döndürdüğü ayrıntılar:
- n_per_group: 323
- n_total: 969
- actual_power: 0.8011
- critical F: 3.005
- df1: 2, df2: 966
- ncp: 9.69

Araç bir uyarı döndürmedi.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S04

> Üç tedavi kolunda toplam 60 hastamız var. Etki büyüklüğü f = 0,25 ve α = 0,05 ise çalışmanın gücü nedir?

Araç sonucuna göre çalışmanın gücü **0,3744**'tür.

Girdiler ve ara sonuçlar:
- Grup sayısı: 3
- Toplam örneklem: 60 (grup başına 20)
- Etki büyüklüğü f: 0,25
- α: 0,05
- df1 = 2, df2 = 57
- Kritik F değeri: 3,1588
- Merkezi olmayışlık parametresi (ncp): 3,75

Bu güç, yaklaşık %37,44'e denk gelir; yani bu tasarımla gerçek bir etkinin yalnızca yaklaşık üçte birinde tespit edilebilir. Genellikle kabul gören eşik 0,80'dir. Bu eşiğe ulaşmak için araçla ek bir *a priori* hesaplama yapabilirim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S05

> Beş farklı fizyoterapi protokolü, toplam 100 hasta. f = 0,25, α = 0,05 için elde edilen güç ne kadar?

Araç sonucuna göre, beş grup, toplam 100 hasta (grup başına 20), f = 0,25 ve α = 0,05 için gerçekleşen güç **0,4663**'tür.

Ayrıntılar:
- Grup başına n: 20
- Toplam n: 100
- df1 = 4, df2 = 95
- Kritik F: 2,4675
- Merkezi olmayan parametre (λ): 6,25
- Gerçekleşen güç: 0,4663

Bu güç, yaygın kabul edilen 0,80 eşiğinin altında kalıyor. Bu nedenle bu tasarım, f = 0,25 etki büyüklüğünü tespit etmek için yeterli değil.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S06

> Üç kol, büyük etki (f = 0,40), α = 0,05, güç %80. Toplam örneklem büyüklüğü?

Araç sonucuna göre:

- **Toplam örneklem büyüklüğü: 66**
- Grup başına: 22
- Gerçekleşen güç (actual_power): 0,8181
- Kritik F: 3,1428
- df1 = 2, df2 = 63
- Noncentrality parametresi (ncp): 10,56

Hesaplama parametreleri: f = 0,4, α = 0,05, güç = 0,8, 3 grup, tek yönlü ANOVA (F testi, sabit etkiler, omnibus). Araç herhangi bir uyarı ya da hata döndürmedi.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S07

> Etik kurul α = 0,01 istiyor. Üç kol, f = 0,25, güç 0,95 ile kaç hasta gerekir?

Üç kol, f = 0,25, α = 0,01 ve güç 0,95 için gereken toplam örneklem **336** hastadır. Her kolda **112** hasta olmalıdır.

Aracın döndürdüğü değerler:
- n_per_group: 112
- n_total: 336
- actual_power: 0.9507
- critical: 4.6694
- df1: 2
- df2: 333
- ncp: 21

Gerçekleşen güç 0,9507 olduğu için hedeflenen 0,95'in üzerindedir. Bu, tek yönlü ANOVA omnibus F testi varsayımıyla hesaplanmıştır. Kayıp takibi için bu sayıya ek hasta eklemeniz gerekebilir.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S08

> Üç tedavi kolunda toplam 61 hasta topladık (kollar eşit değil). f = 0,25, α = 0,05 ile gücümüz nedir?

**Gerçekleşen güç (actual power): 0.3803**

Girdiler: f = 0,25, α = 0,05, toplam N = 61, grup sayısı = 3.

Aracın diğer çıktıları:
- Grup başına ortalama örneklem büyüklüğü (n_per_group): 20.3333
- Kritik F değeri: 3.1559
- df1 = 2, df2 = 58
- Merkezilik parametresi (ncp): 3.8125

**Uyarı:** Toplam N = 61, 3'e tam bölünmüyor. Araç analizi ortalama grup büyüklüğü üzerinden yaptı. Kollar eşit olmadığı için bu, gerçek gücü tam olarak yansıtmayabilir. Bu tek yönlü ANOVA aracı, kolların ayrı ayrı büyüklüklerini girmenize izin vermiyor. Dengesiz gruplar için kesin sonuç gerekiyorsa, grup büyüklüklerini kullanan başka bir araçla ya da istatistikçinizle doğrulamanızı öneririm.

Gücün 0.3803 olması, bu tasarımla bir etkiyi (f = 0,25) tespit etme olasılığının düşük olduğunu gösteriyor. Genellikle 0.80 hedeflenir.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "uyari_aktarildi": true, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S09

> Tek kollu bir çalışmada f = 0,25, α = 0,05, güç 0,95 için tek yönlü ANOVA ile kaç hasta gerekir?

Bu hesaplamayı yapamıyorum. Araç, tek yönlü ANOVA için en az 2 grup gerektiğini bildirdi: `There must be at least 2 groups.`

Tek kollu bir çalışma tek yönlü ANOVA ile analiz edilemez. Bu tasarımda karşılaştırılacak en az iki grup olmalı. Güç analizini şu bilgiyle yeniden çalıştırabilirim:

- **Grup sayısı:** Kaç grup karşılaştırılacak? (Örneğin 2, 3 veya 4.)

Bu tasarımda tek kollu bir çalışma için farklı bir analiz (ör. tek örneklem t testi veya tek oranlı test) gerekiyorsa, bu durumda ANOVA aracı uygun değil. Böyle bir test sorarsanız bunun desteklenmediğini belirtirim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "hata_aktarildi": true, "hesap_yapmadi": true}`

### S10

> İki tedavinin yanıt oranlarını ki-kare testiyle karşılaştıracağız. Kaç hasta gerekir?

Bu araç yalnızca tek yönlü ANOVA (F testi, sabit etkiler, omnibus) güç analizini destekliyor. İki oranın ki-kare testiyle karşılaştırılması bu kapsamın dışında olduğu için aracı çağırmadım ve hasta sayısı hesaplamadım.

Ki-kare testi için örneklem büyüklüğünü şu yollarla hesaplayabilirsiniz:
- **G\*Power**: "Exact" veya "χ² tests" ailesinde "Goodness-of-fit" ya da "Contingency tables" seçeneğini kullanın. Beklenen oranlar, α, güç ve etki büyüklüğü (w) girilir.
- **R**: `pwr` paketindeki `pwr.2p.test` (iki oran için) veya `pwr.chisq.test` fonksiyonu.
- **Biyoistatistikçi ile danışma**: Oranlar ve etki büyüklüğü belirlenirken istatistikçinin görüşü önemlidir.

Hesabı yaparken şu bilgilerin hazır olması gerekir: iki grubun beklenen yanıt oranları, α düzeyi (genellikle 0,05), istenen güç (genellikle 0,80) ve iki kuyruklu mu tek kuyruklu mu test edileceği. Bu değerleri paylaşırsanız, ANOVA ile ilgili bir sorunuz olursa yardımcı olabilirim.

Kontroller: `{"arac_cagrilmadi": true, "desteklenmiyor_dedi": true}`
