# Ajan değerlendirmesi

Model: `haiku` (Claude Code başsız). Ajanın tek aracı `anova_oneway` MCP aracı; yerleşik araçlar kapalı (`--tools ""`). Token değerleri Claude Code'un `usage` alanından ölçüldü (girdi = input + cache_creation + cache_read).

| Soru | Oracle | Sonuç | MCP çağrısı | MCP girdi tok. | MCP çıktı tok. | GUI girdi tok. | GUI çıktı tok. |
|------|--------|-------|-------------|---------------:|---------------:|---------------:|---------------:|
| S01 | V05 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 3}` | 13780 | 464 | 13504 | 423 |
| S02 | V12 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 4}` | 13675 | 438 | 13400 | 214 |
| S03 | V01 | ✅ | `{"mode": "a-priori", "f": 0.1, "alpha": 0.05, "power": 0.8, "groups": 3}` | 13695 | 575 | 13130 | 466 |
| S04 | V34 | ✅ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 60, "groups": 3}` | 13693 | 515 | 13416 | 256 |
| S05 | V44 | ✅ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 100, "groups": 5}` | 13677 | 497 | 13400 | 228 |
| S06 | V03 | ✅ | `{"mode": "a-priori", "f": 0.4, "alpha": 0.05, "power": 0.8, "groups": 3}` | 13658 | 440 | 13382 | 202 |
| S07 | V08 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.01, "power": 0.95, "groups": 3}` | 13664 | 605 | 13390 | 360 |
| S08 | V38 | ✅ | `{"mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 61, "groups": 3}` | 13728 | 610 | 13404 | 708 |
| S09 | V33 | ✅ | `{"mode": "a-priori", "f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 1}` | 13641 | 784 | 13406 | 367 |
| S10 | — | ✅ | `—` | 6708 | 670 | — | — |

**Geçen: 10/10**

Karşılaştırılabilir 9 soruda toplam: MCP 123211 girdi / 4928 çıktı token; GUI ekran görüntüsü 120432 girdi / 3224 çıktı token.

Her sorunun tam akışı (araç çağrısı, araç sonucu, yanıt): `eval/logs/`.

## Yanıtlar

### S01

> Üç farklı antihipertansif tedavi kolunu karşılaştıran bir çalışma planlıyoruz. Orta düzey etki (Cohen f = 0,25), α = 0,05 ve %95 güç istiyoruz. Toplam kaç hasta, kol başına kaç hasta gerekir?

Üç kollu tek yönlü ANOVA için gereken örneklem:

- **Toplam:** 252 hasta
- **Kol başına:** 84 hasta

Araç, bu büyüklükte gerçekleşen gücü **0,9515** olarak hesapladı. Bu değer, hedeflenen 0,95'in biraz üzerindedir. Kritik F değeri **3,0321** (df1 = 2, df2 = 249), kolların ncp değeri ise **15,75**.

Kayıp veya bırakma (dropout) payı eklenmedi. Gerçek çalışmada bu sayıyı kayıp oranına göre artırmanız gerekir.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "yanitta_n_per_group": true, "hesap_yapmadi": true}`

### S02

> Dört kollu bir ağrı kesici çalışması: f = 0,25, α = 0,05, güç 0,95. Gereken toplam örneklem nedir?

Dört kollu çalışma için gereken toplam örneklem **280**'dir (grup başına **70**).

Araç çıktısındaki diğer değerler:
- Gerçekleşen güç (actual_power): 0.951
- Kritik F: 2.6373
- Serbestlik dereceleri: df1 = 3, df2 = 276
- Merkezi olmayan parametre (ncp): 17.5

Hesap, f = 0,25, α = 0,05, hedef güç 0,95 ve 4 grup ile yapıldı.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S03

> Üç diyet programını karşılaştıracağız ve küçük bir etki bekliyoruz (f = 0,10). α = 0,05, güç %80 için kaç katılımcı lazım?

Üç grup, f = 0,10, α = 0,05 ve hedef güç 0,80 için araç sonucu:

- **Grup başına katılımcı (n_per_group):** 323
- **Toplam katılımcı (n_total):** 969
- **Gerçekleşen güç (actual_power):** 0,8011
- **Kritik F değeri:** 3,005
- **Serbestlik dereceleri:** df1 = 2, df2 = 966
- **Merkezi olmayanlık parametresi (ncp):** 9,69

Üç diyet programını karşılaştırmak için, küçük etki (f = 0,10) varsayımıyla her gruba 323 katılımcı (toplamda 969) gerekir. Bu, hedeflenen güç olan 0,80'i sağlar.

Küçük etki büyüklükleri gerçekçi bir varsayım olabilir, ancak bu tahmin pilot veriye veya literatüre dayanmalıdır. Düşme oranını (attrition) hesaba katmak için bu sayıyı artırmanız gerekebilir.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S04

> Üç tedavi kolunda toplam 60 hastamız var. Etki büyüklüğü f = 0,25 ve α = 0,05 ise çalışmanın gücü nedir?

Üç gruplu tek yönlü ANOVA'da (f = 0,25, α = 0,05, toplam N = 60, grup başına 20 hasta) çalışmanın gücü **0.3744**'tür.

Aracın döndürdüğü ayrıntılar:
- Kritik F değeri: 3.1588
- Serbestlik dereceleri: df1 = 2, df2 = 57
- Merkezi olmayanlık parametresi (λ): 3.75

Bu güç, 0.80 gibi yaygın bir hedefin oldukça altındadır. Bu etki büyüklüğü için yaklaşık %80 güç istenirse daha fazla hastaya ihtiyaç var. Gerekli toplam örneklem büyüklüğünü de hesaplayabilirim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S05

> Beş farklı fizyoterapi protokolü, toplam 100 hasta. f = 0,25, α = 0,05 için elde edilen güç ne kadar?

Beş protokol ve toplam 100 hasta (grup başına 20) ile f = 0,25, α = 0,05 için gerçekleşen güç **actual_power = 0,4663**'tür.

Aracın döndürdüğü diğer değerler:
- Grup başına hasta sayısı: 20
- Serbestlik dereceleri: df1 = 4, df2 = 95
- Kritik F değeri: 2,4675
- Merkezi olmayanlık parametresi (ncp): 6,25

Bu güç, genel olarak kabul edilen %80 düzeyinin oldukça altında. Gücü %80 için yükseltmek istiyorsanız, aynı parametrelerle toplam örneklem büyüklüğünü artırmak gerekir.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S06

> Üç kol, büyük etki (f = 0,40), α = 0,05, güç %80. Toplam örneklem büyüklüğü?

**Toplam örneklem büyüklüğü: 66** (grup başına 22)

Araç sonuçları:
- Grup başına n: 22
- Toplam n: 66
- Gerçekleşen güç: 0.8181
- Kritik F: 3.1428
- Serbestlik dereceleri: df1 = 2, df2 = 63
- Merkezi olmayan parametre (ncp): 10.56

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S07

> Etik kurul α = 0,01 istiyor. Üç kol, f = 0,25, güç 0,95 ile kaç hasta gerekir?

Üç kol, f = 0,25, α = 0,01 ve güç 0,95 için gereken örneklem:

- **Grup başına hasta sayısı:** 112
- **Toplam hasta sayısı:** 336
- **Gerçekleşen güç:** 0,9507
- **Kritik F değeri:** 4,6694
- **Serbestlik dereceleri:** df1 = 2, df2 = 333
- **Merkezi olmayışlık parametresi (λ):** 21

Güç 0,95'in biraz üstünde çıktığı için 112 hasta/kol yeterli. Etik kurul gerekçesini yazarken bu değerleri ve f = 0,25 varsayımını belirtmeniz faydalı olur.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "yanitta_n_total": true, "hesap_yapmadi": true}`

### S08

> Üç tedavi kolunda toplam 61 hasta topladık (kollar eşit değil). f = 0,25, α = 0,05 ile gücümüz nedir?

Gücünüz **0,3803** (`actual_power`).

Hesap, 61 hastanın üç kola eşit dağıldığı varsayımıyla yapıldı: grup başına ortalama `n_per_group` = 20.3333.

**Uyarı:** Toplam örneklem (61), grup sayısına (3) tam bölünmüyor. Analiz ortalama grup büyüklüğü üzerinden yapıldı. Kollar eşit olmadığı için bu, gerçek gücün tam olarak aynı olmayabileceği anlamına gelir.

Diğer çıktılar: kritik F = 3,1559, df1 = 2, df2 = 58, ncp = 3,8125.

Güç 0,3803 olduğundan bu tasarım yaklaşık %80 güç hedefinin çok altında kalıyor. Yalnızca araç çıktısına dayanarak, hedeflenen güce ulaşmak için daha fazla hastaya ihtiyaç olduğunu söyleyebilirim. Gerekli toplam örneklemi bulmak isterseniz a priori hesabı (güç = 0,80) yapabilirim.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "uyari_aktarildi": true, "yanitta_actual_power": true, "hesap_yapmadi": true}`

### S09

> Tek kollu bir çalışmada f = 0,25, α = 0,05, güç 0,95 için tek yönlü ANOVA ile kaç hasta gerekir?

Aracın döndürdüğü hata: **"There must be at least 2 groups."** Tek yönlü ANOVA en az 2 grup gerektirdiği için tek kollu bir çalışma için hasta sayısı hesaplanamadı.

Tek kollu bir çalışma (tek bir grup) tek yönlü ANOVA ile analiz edilemez. Bu durumda hesaplama, tek örneklem testi gibi farklı bir yönteme dayanmalı; bu araç ise yalnızca tek yönlü ANOVA'yı destekliyor.

Şunlardan birini yaparsanız hesaplayabilirim:
- **Grup sayısını belirtin:** En az 2 grubunuz varsa (ör. kontrol ve tedavi), f = 0,25, α = 0,05, güç = 0,95 değerleriyle toplam hasta sayısını hesaplarım.
- **Tek kollu tasarımınızın ne tür bir karşılaştırma yaptığını söyleyin:** Örneğin tek bir grubun önceden belirlenmiş bir değerle karşılaştırılması gibi bir test gerekiyorsa, bu durum ANOVA dışında bir yöntemi gerektirir ve bu araçla hesaplanamaz.

Kontroller: `{"arac_cagrildi": true, "parametreler_dogru": true, "hata_aktarildi": true, "hesap_yapmadi": true}`

### S10

> İki tedavinin yanıt oranlarını ki-kare testiyle karşılaştıracağız. Kaç hasta gerekir?

Bu araç yalnızca tek yönlü ANOVA (F testi, sabit etkiler, omnibus) için örneklem büyüklüğü ve güç hesabı yapabiliyor. İki tedavinin yanıt oranlarını ki-kare testiyle karşılaştırmak için hesaplama yapamıyorum, bu yüzden aracı çağırmadım ve sayı vermedim.

Bu hesap için şu yollardan birini deneyebilirsiniz:

- **G*Power**: "Exact" veya "χ² tests" bölümünde 2×2 tablo (ki-kare) için güç analizi seçeneği bulunuyor. Beklenen yanıt oranlarınızı, α'yı ve istediğiniz gücü girerek hesabı yapabilirsiniz.
- **Biyoistatistikçi**: Yanıt oranları küçük ya da çalışma tasarımı karmaşıksa (tabakalama, kümeleme, eşleştirme gibi) bir istatistikçiyle çalışmanız daha güvenli olur.

Başka bir konuda, örneğin üç veya daha fazla tedavi grubunun ortalamalarını karşılaştırmak için tek yönlü ANOVA güç analizi konusunda yardımcı olabilirim.

Kontroller: `{"arac_cagrilmadi": true, "desteklenmiyor_dedi": true}`
