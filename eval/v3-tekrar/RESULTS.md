# Ajan değerlendirmesi

Model: `haiku` (Claude Code başsız). Ajanın tek aracı `anova_oneway` MCP aracı; yerleşik araçlar kapalı (`--tools ""`). Token değerleri Claude Code'un `usage` alanından ölçüldü (girdi = input + cache_creation + cache_read).

| Soru | Oracle | Sonuç | MCP çağrısı | MCP girdi tok. | MCP çıktı tok. | GUI girdi tok. | GUI çıktı tok. |
|------|--------|-------|-------------|---------------:|---------------:|---------------:|---------------:|
| S01 | V05 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 3}` | 13780 | 544 | 13504 | 540 |
| S02 | V12 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 4}` | 13675 | 482 | 13400 | 207 |
| S03 | V01 | ✅ | `{"mode": "a-priori", "f": 0.1, "alpha": 0.05, "power": 0.8, "groups": 3}` | 13695 | 465 | 13130 | 330 |
| S04 | V34 | ✅ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 60, "groups": 3}` | 13693 | 511 | 13416 | 256 |
| S05 | V44 | ✅ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 100, "groups": 5}` | 13777 | 622 | 13400 | 254 |
| S06 | V03 | ✅ | `{"mode": "a-priori", "f": 0.4, "alpha": 0.05, "power": 0.8, "groups": 3}` | 13658 | 435 | 13382 | 209 |
| S07 | V08 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.01, "power": 0.95, "groups": 3}` | 13664 | 431 | 13390 | 357 |
| S08 | V38 | ✅ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 61, "groups": 3}` | 13869 | 813 | 13404 | 642 |
| S09 | V33 | ❌ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 2}` | 13682 | 860 | 13406 | 479 |
| S10 | — | ✅ | `—` | 6708 | 383 | — | — |

**Geçen: 9/10**

Karşılaştırılabilir 9 soruda toplam: MCP 123493 girdi / 5163 çıktı token; GUI ekran görüntüsü 120432 girdi / 3274 çıktı token.

Her sorunun tam akışı (araç çağrısı, araç sonucu, yanıt): `eval/v3-tekrar/logs/`.

## Yanıtlar

### S01

> Üç farklı antihipertansif tedavi kolunu karşılaştıran bir çalışma planlıyoruz. Orta düzey etki (Cohen f = 0,25), α = 0,05 ve %95 güç istiyoruz. Toplam kaç hasta, kol başına kaç hasta gerekir?

Üç kollu tek yönlü ANOVA için gereken örneklem büyüklüğü:

- **Kol başına hasta sayısı (n):** 84
- **Toplam hasta sayısı (N):** 252

Girdiler: f = 0,25, α = 0,05, güç = 0,95, grup sayısı = 3.

Aracın ayrıntılı çıktısı:
- Gerçekleşen güç (actual_power): 0.9515
- Kritik F değeri (critical): 3.0321
- Serbestlik dereceleri: df1 = 2, df2 = 249
- Merkezi olmayanlık parametresi (ncp): 15.75

Gerçekleşen güç hedef olan 0,95'in biraz üstünde. Bu, kol başına 84 hastanın hedefi karşıladığını gösteriyor. Ayrıca hasta kaybını hesaba katmak isterseniz bu sayıyı kayıp oranına göre artırmanız gerekir.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "yanitta_n_per_group": true, "hesap_yapmadi": true}`

### S02

> Dört kollu bir ağrı kesici çalışması: f = 0,25, α = 0,05, güç 0,95. Gereken toplam örneklem nedir?

Gereken toplam örneklem **280**'dir (grup başına 70).

- Grup başına örneklem: 70
- Gerçekleşen güç: 0.951
- Kritik F: 2.6373
- Serbestlik dereceleri: df1 = 3, df2 = 276
- Merkezi olmayan parametre (ncp): 17.5

Hesap tek yönlü ANOVA F testi (sabit etkiler, omnibus) için yapıldı. Araçtan uyarı gelmedi.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S03

> Üç diyet programını karşılaştıracağız ve küçük bir etki bekliyoruz (f = 0,10). α = 0,05, güç %80 için kaç katılımcı lazım?

Üç diyet programını karşılaştırmak için (f = 0,1, α = 0,05, güç = 0,8) gereken toplam katılımcı sayısı **969**'dur. Bu, grup başına **323** kişi demektir.

Aracın döndürdüğü diğer değerler:
- Gerçekleşen güç: 0,8011
- Kritik F: 3,005
- Serbestlik dereceleri: df1 = 2, df2 = 966
- Merkezi olmayan parametre (λ): 9,69

Uyarı ya da hata dönmedi.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S04

> Üç tedavi kolunda toplam 60 hastamız var. Etki büyüklüğü f = 0,25 ve α = 0,05 ise çalışmanın gücü nedir?

Araç sonucuna göre çalışmanın gücü **0,3744**'tür.

Girdiler ve ara sonuçlar (araçtan aynen alınmıştır):

- Grup sayısı: 3
- Toplam örneklem: 60 (grup başına 20)
- Etki büyüklüğü f: 0,25
- α: 0,05
- df1: 2
- df2: 57
- Kritik F: 3,1588
- Merkezi olmayan parametre (λ): 3,75
- Güç: 0,3744

Bu güç, yaygin kabul edilen 0,80 eşiğinin oldukça altındadır. Yani bu tasarımda f = 0,25 gibi orta büyüklükteki bir etkiyi tespit etme olasılığı düşüktür. Araç, 0,80 gücü için gereken toplam örneklem büyüklüğünü hesaplamadı; bunu isterseniz aynı aracı a-priori modda (güç = 0,80) çalıştırarak belirleyebilirim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S05

> Beş farklı fizyoterapi protokolü, toplam 100 hasta. f = 0,25, α = 0,05 için elde edilen güç ne kadar?

Post-hoc analiz sonucu (tek yönlü ANOVA, F testi, sabit etkiler):

- Grup sayısı: 5
- Toplam örneklem (N): 100
- Grup başına hasta: 20
- Etki büyüklüğü (f): 0.25
- α: 0.05
- Serbestlik dereceleri: df1 = 4, df2 = 95
- Kritik F: 2.4675
- Merkezi olmayan parametre (λ): 6.25
- **Elde edilen güç (actual power): 0.4663**

Bu tasarımda gücün 0.4663 olduğu görülüyor; yani f = 0.25 etkisini α = 0.05 düzeyinde saptama olasılığı yaklaşık yarım düzeyde kalıyor. Genellikle kabul gören 0.80 güç için bu tasarımın yetersiz olduğu söylenebilir. Hedef gücü 0.80 olarak alıp gerekli toplam örneklemi hesaplamak isterseniz bunu da yapabilirim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S06

> Üç kol, büyük etki (f = 0,40), α = 0,05, güç %80. Toplam örneklem büyüklüğü?

Tek yönlü ANOVA a priori analizine göre toplam örneklem büyüklüğü **66**'dır (grup başına 22).

- Grup sayısı: 3
- Etki büyüklüğü (f): 0.4
- α: 0.05
- Hedef güç: 0.8
- Gerçekleşen güç: 0.8181
- Kritik F: 3.1428
- df1 = 2, df2 = 63
- Merkezi parametre (ncp): 10.56

Araç herhangi bir uyarı ya da hata döndürmedi.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S07

> Etik kurul α = 0,01 istiyor. Üç kol, f = 0,25, güç 0,95 ile kaç hasta gerekir?

Tek yönlü ANOVA için gereken toplam örneklem **336** hastadır (grup başına **112**).

Girdiler: f = 0,25, α = 0,01, güç = 0,95, grup sayısı = 3.

Araç çıktısının tamamı:
- n_per_group: 112
- n_total: 336
- actual_power: 0,9507
- critical (F kritik değeri): 4,6694
- df1: 2
- df2: 333
- ncp: 21

Gerçekleşen güç 0,95'in biraz üzerindedir (0,9507), çünkü grup başına örneklem tam sayıya yuvarlanmıştır.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S08

> Üç tedavi kolunda toplam 61 hasta topladık (kollar eşit değil). f = 0,25, α = 0,05 ile gücümüz nedir?

**Güç (actual_power): 0.3803**

Analiz parametreleri: f = 0.25, α = 0.05, toplam N = 61, grup sayısı = 3, df1 = 2, df2 = 58, kritik F = 3.1559, ncp = 3.8125, grup başına ortalama n = 20.3333.

**Uyarı:** Araç "Toplam örneklem büyüklüğü (61), grup sayısının (3) katı değil. Analiz ortalama grup büyüklüğüne göre yapıldı" uyarısını döndürdü. Araç yalnızca eşit grup büyüklüğünü varsayıyor ve kollarınızın gerçek dağılımını almıyor. Bu nedenle 0.3803 değeri, kollar eşit değilse gerçek gücün tam karşılığı olmayabilir. Kesin değer için her kolun hasta sayısını bilmem gerekiyor; bu bilgiyi verirseniz eşit olmayan dağılımı hesaplamak için başka bir yol araştırabilirim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "uyari_aktarildi": true, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S09

> Tek kollu bir çalışmada f = 0,25, α = 0,05, güç 0,95 için tek yönlü ANOVA ile kaç hasta gerekir?

Araç sonucuna göre toplam **210** hasta gerekir (grup başına **105**).

Ayrıca bir varsayımım var: sorunuzda grup sayısı belirtilmemişti, bu yüzden **2 grup** kabul ettim. Farklı bir grup sayısı söylerseniz hesabı yeniden yapabilirim. "Tek kollu" ifadesini tek grup olarak anladıysanız, ANOVA en az iki grup gerektirdiği için bu tasarım için tek yönlü ANOVA uygun değildir.

Araç çıktısındaki ayrıntılar:
- Kritik F değeri: 3,8866 (sd1 = 1, sd2 = 208)
- Gerçekleşen güç: 0,9501
- Merkezi olmayışlık parametresi (λ): 13,125

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": false, "hata_aktarildi": false, "hesap_yapmadi": true}`

### S10

> İki tedavinin yanıt oranlarını ki-kare testiyle karşılaştıracağız. Kaç hasta gerekir?

Bu araç yalnızca tek yönlü ANOVA (F testi, sabit etkiler, omnibus) için örneklem büyüklüğü ve güç hesabı yapabiliyor. Ki-kare testi ile iki oranın karşılaştırılması desteklenmediği için bu hesabı yapamıyorum.

Yanıt oranlarını karşılaştırmak için G*Power'da "Proportions: Difference between two independent proportions" gibi bir test ailesi ya da başka bir istatistik yazılımı kullanabilirsiniz. Bu testi hesaplamak isterseniz, beklenen iki oran, alfa, güç ve oran farkı gibi bilgilerle bunu adım adım birlikte yapabiliriz.

Kontroller: `{"arac_cagrilmadi": true, "desteklenmiyor_dedi": true}`
