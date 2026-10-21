# CLI Sözleşmesi — anova-oneway

> **Durum: GEÇİCİ (v0.4).** Yönergedeki CONTRACT.md bağlantısı boş geldiği için
> ANOVA ailesinin resmî parametre/çıktı adları bilinmiyor. Buradaki adlar,
> yönergedeki tek örnekle (`t2-indep`) aynı üslupta seçildi ve gizli vektörlerde
> ad uyuşmazlığı riskini azaltmak için yaygın **takma adlar** da kabul edilir.
> Resmî sözleşme gelince yalnızca bu dosya ve `src/gpower_clone/contract.py`
> değişir; motor değişmez.

Yönergedeki referans örnek (biçim bu örnekten türetildi):

```
gpower-clone --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1
{"n1":105,"n2":105,"n_total":210,"actual_power":0.9501,"critical":1.9714,"df":208,"ncp":3.6228}
```

## 1. Komut

```
gpower-clone --test anova-oneway --mode <mod> [parametreler]
```

- `--test` isteğe bağlıdır (araç tek aileyi uygular). Verilirse büyük/küçük harf ve
  `_`/`-` farkı gözetilmeden şu yazımlar kabul edilir: `anova-oneway` (kanonik),
  `anova-one-way`, `oneway-anova`, `one-way-anova`, `anova1`, `anova`. Başka bir aile
  (ör. `t2-indep`) → `{"error":"Unsupported test: t2-indep"}`, çıkış 2.
- Ad seçimi: Ödev 5'teki sınıflandırıcı etiketleri (`t2-indep`, `t-paired`,
  `anova-oneway`, `chi2-contingency`, `multireg-r2`) ile aynıdır.

## 2. Modlar

| `--mode` | Kabul edilen takma adlar | Hesaplanan |
|----------|--------------------------|------------|
| `a-priori` | `apriori`, `a_priori` | toplam N (ve grup başı n) |
| `post-hoc` | `posthoc`, `post_hoc` | güç |

## 3. Parametreler

Bayrak adlarında `_` ile `-` eşdeğerdir (`--n_total` = `--n-total`).

| Bayrak | Takma adlar | Tip | a-priori | post-hoc |
|--------|-------------|-----|:--------:|:--------:|
| `--f` | `--effect-size`, `--es` | sayı | zorunlu | zorunlu |
| `--alpha` | — | sayı | zorunlu | zorunlu |
| `--power` | — | sayı | zorunlu | kullanılmaz |
| `--groups` | `--k`, `--k-groups`, `--n-groups`, `--num-groups` | sayı | zorunlu | zorunlu |
| `--n-total` | `--n`, `--N`, `--total-n`, `--sample-size` | tam sayı | kullanılmaz | zorunlu |
| `--digits` | — | tam sayı | isteğe bağlı (varsayılan 4) | isteğe bağlı |

- Modda kullanılmayan ya da bu aileye ait olmayan bir bayrak (ör. `--tails`,
  `--ratio`, `--d`) **geçersiz girdi** sayılır.
- Aynı parametre iki kez (ör. `--k 3 --groups 3`) verilirse geçersiz girdidir.

## 4. Çıktı — standart çıktıya tek satır JSON

Alanlar her iki modda da aynıdır ve bu sırayla yazılır:

| Alan | Tip | Anlamı (G*Power penceresindeki karşılığı) |
|------|-----|-------------------------------------------|
| `n_per_group` | tam sayı ya da sayı | Grup başına n (N/k; post hoc'ta N k'ya bölünmüyorsa ortalama) |
| `n_total` | tam sayı | Total sample size |
| `actual_power` | sayı | Actual power (a priori) / Power (1−β err prob) (post hoc) |
| `critical` | sayı | Critical F |
| `df1` | tam sayı | Numerator df |
| `df2` | tam sayı | Denominator df |
| `ncp` | sayı | Noncentrality parameter λ |

Ondalıklı alanlar `--digits` haneye (varsayılan **4**, yönergedeki örnekle aynı)
yuvarlanır; tam sayılar ondalıksız yazılır.

- **Neden 4 hane?** Yönergedeki tek referans çıktı (`t2-indep`) 4 hanelidir
  (`"actual_power":0.9501`). Otomatik değerlendirici JSON'u metin olarak
  karşılaştırırsa 4 hane birebir tutar; sayı olarak ve G*Power'ın 7 hanesine göre
  karşılaştırırsa `--digits 7` aynı değeri 7 haneyle verir (G*Power penceresiyle
  birebir: `display.py`).
- `n_total`, `df1`, `df2` her zaman tam sayıdır; a priori'de `n_per_group` da tam sayıdır
  (N birebir eşleşme kuralı). Yalnızca post hoc'ta N, k'ya bölünmüyorsa `n_per_group`
  ortalamadır ve `--digits` haneye yuvarlanır.

```
gpower-clone --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.95 --groups 3
{"n_per_group":84,"n_total":252,"actual_power":0.9515,"critical":3.0321,"df1":2,"df2":249,"ncp":15.75}

gpower-clone --test anova-oneway --mode post-hoc --f 0.25 --alpha 0.05 --n-total 60 --groups 3
{"n_per_group":20,"n_total":60,"actual_power":0.3744,"critical":3.1588,"df1":2,"df2":57,"ncp":3.75}
```

(Bu iki satırın beklenen değerleri G*Power oracle vektörleri V05 ve V34'ten gelir.)

### Uyarılar

G*Power'ın hesabı yapıp yine de bir bilgi kutusu gösterdiği durumlarda (ör.
post hoc'ta N grup sayısına bölünmüyor) sonuç normal biçimde stdout'a yazılır,
uyarı metni **stderr**'e tek satır olarak yazılır ve çıkış kodu **0** olur.
MCP aracı (`anova_oneway`) aynı nesneyi döndürür ve stderr'e gidecek uyarı
satırlarını nesnenin sonuna `warnings` listesi olarak ekler (stdio MCP
sunucusunun stderr'i ajana ulaşmaz; bkz. `eval/` S08).

### Geçersiz girdi

```
{"error":"<açıklama>"}
```

- stdout'a tek satır, çıkış kodu **2**.
- Açıklama metni, G*Power aynı girdi için bir hata kutusu gösteriyorsa o kutudaki
  İngilizce metnin aynısıdır (ör. `Power must be greater than or equal to alpha.`);
  yoksa kısa bir İngilizce açıklamadır.
- Beklenmeyen iç hata: `{"error":"internal: ..."}`, çıkış kodu **1**.

## 5. Tek değiştirme noktası

`src/gpower_clone/contract.py` içindeki üç tablo:

- `FLAG_ALIASES` — kanonik parametre adı → kabul edilen bayraklar
- `MODE_ALIASES` — kanonik mod → kabul edilen yazımlar
- `OUTPUT_FIELDS` — çıktı alanlarının adı ve sırası
- `TEST_ALIASES` — `--test` için kabul edilen yazımlar

Resmî CONTRACT gelince yalnızca bu tablolar ve bu dosya güncellenir.

## 6. Kapsam dışı

Hesap kuralları (yuvarlama, arama, sınırlar, gösterim) bu dosyada değil,
**SPEC.md**'de ve kanıtları **LEDGER.md**'de tanımlanır.
