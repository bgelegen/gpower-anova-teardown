# Halüsinasyon Günlüğü

Ajanların yanlış çıkardığı ya da uydurduğu şeyler: ne iddia edildi, gerçek ne,
nasıl fark edildi, hangi test/vektör yakaladı, nasıl düzeltildi. Kronolojik.

Oturumlar: **O1** söküm (Opus, REA + Ghidra) · **O2** temiz oda yazım (Sonnet, REA yok) ·
**ORK** orkestratör (oturumları hazırlayan ve değerlendiren ajan) · **AJAN** MCP üzerinden
klinik soru yanıtlayan ajan (Haiku).

---

## H-01 · Kılavuzda olmayan formülü "kılavuzda var" saymak (O1)

| Alan | |
|------|---|
| Oturum | O1, ilk tur |
| Ajanın iddiası | "λ = f²N, df1, df2, **kritik F = F⁻¹(1 − α; df1, df2) ve güç = 1 − F_nc** formülleri kılavuzun ANOVA bölümünde de yazar." (LEDGER L-34) |
| Gerçek davranış | Kılavuz s. 25 §10.5 yalnızca λ = f²N, df1 = k − 1, df2 = N − k ve H0/H1 dağılımlarını veriyor; kritik değerin 1 − α kantili, gücün 1 − F_nc olarak hesaplandığı ANOVA bölümünde **yazmıyor**. |
| Nasıl fark edildi | O1 ilk turda kılavuza erişmemişti, iddia kod izinden ve genel bilgiden "tahmin"di. Devam turunda kılavuz metni çıkarılıp s. 24–25 okununca çelişti. |
| Yakalayan | Kılavuz okuması (`prompts/oturum1-devam.md` madde 3) · etkilenen kural R-03 |
| Düzeltme | L-34 üstü çizildi + **YANILGI** işaretlendi; kritik F/güç tanımı [REA] olarak L-06'ya taşındı, kılavuzdaki kısım [DOK] L-41/L-42 oldu. Puanlama açısından önemli: yanlış etiket kalsaydı [REA] puanı haksız yere düşecekti. |

## H-02 · "Uç küçük f'de G*Power'ın N'i belki doğrudur" ve eşik tahmini (O1)

| Alan | |
|------|---|
| Oturum | O1, devam turu (SPEC R-18, §5; LEDGER L-38, L-39) |
| Ajanın iddiası | (a) Sapma "df2 ~10⁹" civarında başlar; (b) "tam güç(963468906) ≥ 0,80 ise G*Power'ın N'i doğrudur, yalnızca gösterilen güç hatalıdır" dalı mümkün; (c) gerçekleşen gücün hedefin altında görünmesi "actual power ≥ hedef" garantisinin bozulduğunu gösterir. |
| Gerçek davranış | 40 basamaklı bağımsız hesap (`tests/test_r18_high_precision.py`): V52'de G*Power'ın N'i **15 kişi fazla** (en küçük doğru N 963 468 891), gösterdiği güç 0.7999999 ama o N'in gerçek gücü 0,8000000071 ≥ 0,80 → V52'de garanti bozulmuyor, **gösterim** yanlış. Sapma df2 ≈ **2,4·10⁸**'de (V54, f = 0,0002) başlıyor ve orada G*Power'ın N'i gerçekten hedefin **altında** (güç 0,7999999953). |
| Nasıl fark edildi | SPEC §6'nın önerdiği V53–V56 G*Power'a girildi; motor V53'te eşleşti, V54–V56'da ayrıştı. Kimin doğru olduğu motordan ve scipy'den bağımsız mpmath hesabıyla ayrıldı. |
| Yakalayan | Oracle V52, V54, V55, V56 · `tests/test_r18_high_precision.py` · `oracle/R18_YUKSEK_HASSASIYET.md` |
| Düzeltme | V54–V56, V52 ile birlikte `xfail(strict=True)` "bilinen sayısal sapma" oldu. SPEC.md, O2'nin gördüğü sürümde donduruldu (SHA-256 `8b9ef5a8…`, `logs/oturum2-spec-sha256.txt`); §5'teki bilinmeyenin kapanışı LEDGER L-47–L-49'da. |

## H-03 · SPEC'te olmayan gösterim kuralı ve sözleşme hanesi uydurmak (O2)

| Alan | |
|------|---|
| Oturum | O2 (temiz oda), ilk test koşusu: `4 failed, 107 passed` |
| Ajanın iddiası | (a) 99,99999999 değerinin ekranda `100` görüneceğini varsaydı (yuvarlamadan **sonra** `%g` seçimi); (b) Gherkin G01 testinde kritik F'nin `3.0321` görüneceğini varsaydı (CONTRACT'ın 4 haneli JSON'unu G*Power penceresinin 7 haneli gösterimiyle karıştırdı). |
| Gerçek davranış | SPEC R-15: biçim seçimi yuvarlamadan **önceki** değere göre yapılır (0,01 < \|x\| < 100 → `%.7f`) → `100.0000000`. Pencerede kritik F `3.0320649` (oracle V05). |
| Nasıl fark edildi | O2'nin kendi testleri motorla çelişti; O2 testlerin SPEC'e değil kendi varsayımına dayandığını gördü. |
| Yakalayan | `tests/test_rules.py::test_R15_fraction_format[99.99999999-100]`, `test_G01_cohen_medium_three_arms` (log: `logs/oturum2.jsonl`) |
| Düzeltme | Beklenen değerler SPEC'e göre düzeltildi (`"100.0000000"`, `"3.0320649"`); motor değişmedi. |

## H-04 · Var olmayan API'yi kesin bilgi gibi vermek (ORK)

| Alan | |
|------|---|
| Oturum | ORK — O2'nin ilk prompt'u (`prompts/oturum2-yazim.md`) |
| Ajanın iddiası | "`mcp` paketinin **FastMCP** sınıfıyla stdio MCP sunucusu" yaz. |
| Gerçek davranış | Kurulan `mcp` 2.x'te `mcp.server.fastmcp` yok; sınıfın adı `MCPServer` (`ModuleNotFoundError: No module named 'mcp.server.fastmcp'. This is mcp 2.x, where FastMCP was renamed to MCPServer…`). |
| Nasıl fark edildi | O2 sunucuyu içe aktarırken hata aldı. |
| Yakalayan | `tests/test_mcp_equality.py` (sunucu başlamayınca 16 test kırıldı) · `SPEC_SORULARI.md` madde 12 |
| Düzeltme | `mcp_server.py` önce `FastMCP`, olmazsa `MCPServer` dener; `pyproject.toml` sürüm sabitlemiyor, iki sürümde de çalışıyor. |

## H-05 · "Hiç hesap yapma" kuralına rağmen yuvarlamak (AJAN)

| Alan | |
|------|---|
| Oturum | AJAN, değerlendirme koşusu v1 (`eval/v1-haiku/`) |
| Ajanın iddiası | S04: araç `actual_power: 0.3744` döndürdü, yanıt "gücü **yaklaşık 0,37**" dedi. S05: araç `0.4663`, yanıt "**%47**" dedi. |
| Gerçek davranış | Sistem mesajı "yuvarlama, yüzdeye çevirme yok; aracın değerini aynen yaz" diyordu. 0,37 ve %47 ajanın kendi hesabı; klinik bağlamda yanlış aktarım riski. |
| Nasıl fark edildi | Değerlendirme betiğinin `hesap_yapmadi` kontrolü: yanıttaki her sayı ya soruda ya araç çıktısında geçmeli → `_kaynaksiz_sayilar: ['0.37']`, `['47']`. |
| Yakalayan | `eval/agent_eval.py` · `eval/v1-haiku/RESULTS.md` (S04, S05 ❌) |
| Düzeltme | Sistem mesajına "tüm basamaklarıyla yaz; 'yaklaşık', yüzde ya da kısaltılmış sayı yazma" eklendi → v2: **10/10** (`eval/RESULTS.md`). |

## H-06 · Doğru yanıtı "kaldı" sayan değerlendirme betiği (ORK)

| Alan | |
|------|---|
| Oturum | ORK — `eval/agent_eval.py` |
| Ajanın iddiası | S08'de ajan post hoc uyarısını aktarmadı (`uyari_aktarildi: False`). |
| Gerçek davranış | Ajan uyarıyı Türkçe aktarmıştı: "Toplam örneklem (61), grup sayısına (3) tam **bölünmüyor**… grup başına **ortalama** büyüklüğü kullanarak…". Betiğin kalıbı (`kat[ıi]\|multiple\|ortalama grup\|average`) bu cümleyi yakalamıyordu. |
| Nasıl fark edildi | Başarısız yanıtlar tek tek okunurken. |
| Yakalayan | İnsan incelemesi · `eval/v1-haiku/logs/S08-mcp.jsonl` |
| Düzeltme | Kalıp `kat[ıi]\|multiple\|ortalama\|average\|b[öo]l[üu]nm` oldu; v1 kayıtları `--regrade` ile yeniden puanlandı (7/10 → 8/10). Aynı hata S10'da da çıktı: ajan "**Desteklediğim** tek test tek yönlü ANOVA'dır" diyerek doğru reddetti, kalıp `desteklen` "Desteklediğim"i kaçırdı → `destekle` yapıldı (v3a 3/10 → 4/10). Ders: değerlendiriciyi de test etmek gerekir. |

## H-07 · Türkçe ondalık virgülü ve uydurma örnek sayılar (AJAN)

| Alan | |
|------|---|
| Oturum | AJAN, koşu v3a (`eval/v3a-haiku/`) — bağlamda yalnızca `anova_oneway` varken |
| Ajanın iddiası | (a) Araca `{"f": "0,25", "alpha": "0,05", "power": "0,95"}` gönderdi (5 soruda: S02, S03, S04, S06, S09). (b) S08'de "kol bazında gerçek n değerlerini (ör. **20, 20, 21** gibi) girmek gerekir" ve "%**38**" yazdı. |
| Gerçek davranış | (a) Araç, G*Power gibi ondalık virgülü kabul etmez: `{"error":"Input error (illegal character?)"}`; ajan çoğunlukla noktayla yeniden denedi, ama S09'da hata zaten grup sayısından geldi. (b) 20/20/21 ve %38 araç çıktısında yok; ajanın kendi bölmesi ve yuvarlaması. |
| Nasıl fark edildi | `parametreler_dogru` (ilk çağrının girdileri) ve `hesap_yapmadi` (`_kaynaksiz_sayilar: ['20','21','38']`) kontrolleri. İlginç yan bulgu: aynı model, bağlamında 22 ilgisiz tarayıcı aracı varken (v2) bu hatayı yapmadı; ilgisiz araçlar kaldırılınca (v3a) yaptı. |
| Yakalayan | `eval/agent_eval.py` · `eval/v3a-haiku/RESULTS.md` |
| Düzeltme | Motor değişmedi (G*Power'a sadık kalındı). MCP aracının açıklamasına "her sayıyı ondalık **nokta** ile JSON sayısı olarak gönder; virgül reddedilir" eklendi → v3: **10/10**, ilk çağrıların hepsi doğru. |

## H-08 · Soruda olmayan parametreyi varsaymak (AJAN)

| Alan | |
|------|---|
| Oturum | AJAN, koşu v3 tekrar (`eval/v3-tekrar/`) — v3 ile aynı ayarlar |
| Ajanın iddiası | S09 ("**Tek kollu** bir çalışmada f = 0,25, α = 0,05, güç 0,95 için tek yönlü ANOVA ile kaç hasta gerekir?") için araca `groups: 2` verdi ve "grup sayısı belirtilmemişti, **2 grup kabul ettim**" dedi → N = 210. |
| Gerçek davranış | Sistem mesajı "kullanıcının verdiği değerleri (grup sayısı 2'den küçük olsa bile) olduğu gibi araca ver; geçerliliği araç denetler" diyor. Doğru davranış `groups: 1` göndermek ve G*Power'ın hatasını (`There must be at least 2 groups.`) aktarmak (v3'te ajan böyle yaptı). |
| Nasıl fark edildi | `parametreler_dogru: False`, `hata_aktarildi: False` (aynı soru v3'te geçmişti → kararsızlık). |
| Yakalayan | `eval/agent_eval.py` · `eval/v3-tekrar/RESULTS.md` |
| Düzeltme | Düzeltilmedi; dürüst sonuç olarak bırakıldı: son sürüm 2 koşuda 19/20. Ders: küçük model "yardımcı olmak için" eksik bilgiyi tamamlıyor; aracın kendisi reddettiği sürece yanlış **hesap** üretmiyor ama yanlış **soruyu** yanıtlayabiliyor. Olası iyileştirme: aracın `groups` için ayrı bir "kullanıcı belirtmedi" durumu istemesi. |
