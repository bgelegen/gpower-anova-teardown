# AI ajanı (+10 bonus) — özet

**Kurgu.** Ajan = Claude Code başsız (`claude -p`), model **Haiku**. Tek aracı bu repodaki
MCP sunucusunun `anova_oneway` aracı; yerleşik araçların hepsi kapalı (`--tools ""`,
`--strict-mcp-config`), çalışma ortamının kendiliğinden eklediği tarayıcı MCP'si de
`--disallowedTools` ile kapalı. Yani ajanın kod çalıştırıp kendi hesabını yapma imkânı yok;
sistem mesajı ayrıca "hiç sayısal işlem yapma" diyor. Sorular: `questions.json`
(10 Türkçe klinik soru: 6 a priori, 3 post hoc, 1 hata, 1 kapsam dışı). Doğru yanıtlar
G*Power oracle vektörlerinden (V01, V03, V05, V08, V12, V33, V34, V38, V44).

| Koşu | Klasör | Ne değişti | Geçen | Ne öğrendik |
|------|--------|------------|------:|-------------|
| v1 | `v1-haiku/` | ilk sistem mesajı | 8/10 | S04 "yaklaşık 0,37", S05 "%47": ajan yuvarladı → H-05 |
| v2 | `v2-haiku/` | + "tüm basamaklarıyla yaz; yüzde/yaklaşık yazma" | 10/10 | — ama bağlamda ortamın eklediği 22 tarayıcı aracı da vardı (çağrılmadı, izinsizdi) |
| v3a | `v3a-haiku/` | tarayıcı araçları yasaklandı → bağlamda **yalnızca** `anova_oneway` | 4/10 | Ajan Türkçe ondalık virgülüyle `"0,25"` gönderdi (araç G*Power gibi reddetti, ajan noktayla yeniden denedi); S08'de örnek sayı uydurdu → H-07 |
| **v3** | `.` (`RESULTS.md`, `logs/`) | araç açıklamasına "sayıyı ondalık **nokta** ile JSON sayısı olarak gönder" | **10/10** | son sürüm |
| v3 tekrar | `v3-tekrar/` | v3'ün aynısı, kararlılık için | 9/10 | S09: "tek kollu" soruda ajan grup sayısını kendisi **2 varsaydı** (kuralı çiğnedi) → H-08 |

Her sorunun tam akışı (araç çağrısı, girdi, araç sonucu, yanıt, `usage`): `logs/<id>-mcp.jsonl`.
Değerlendirme ölçütleri (`agent_eval.py::grade`): araç çağrıldı mı, ilk çağrının parametreleri
soruyla aynı mı, beklenen sayı yanıtta mı, uyarı/hata Türkçe aktarıldı mı ve **yanıttaki her sayı
ya soruda ya araç çıktısında geçiyor mu** (ajan hesap yapmadı mı). Değerlendiricinin kendi iki
kalıp hatası (S08, S10) bulundu ve düzeltildi → H-06; eski koşular `--regrade` ile yeniden puanlandı.

## Token karşılaştırması: MCP ve GUI

**1) Ölçülen (Claude Code `usage`, v3).** Aynı 9 soru, aynı model:

| Kol | Ne yapıyor | Model isteği | Girdi token (toplam) | Çıktı token (toplam) | Liste maliyeti |
|-----|------------|-------------:|---------------------:|---------------------:|---------------:|
| — | araçsız tek yanıt (S10, karşılaştırma tabanı) | 1 | 6 708 | 670 | — |
| MCP | `anova_oneway` çağırır | 2 / soru | 123 211 | 4 928 | 0,0105 $ |
| GUI-görüntü | hazır G*Power ekran görüntüsünü `Read` ile okur | 2 / soru | 120 432 | 3 224 | 0,0050 $ |

Bir aracı bir kez çağırmak, bağlamın ikinci kez işlenmesi demek (~6,7 bin token); iki kolun
toplamı bu yüzden yakın. Asıl fark değişken kısımda: MCP aracının sonucu ~40 token'lık tek
satır JSON, bir G*Power pencere görüntüsü (604×732) ≈ **590** görüntü token'ı. GUI kolu
ayrıca **önceden alınmış doğru ekran görüntüsünü** hazır buluyor; gerçekte o görüntüyü
birinin üretmesi gerekir. (Bağlam etkisi: ortamın eklediği 22 tarayıcı aracının tanımları
v1/v2'de soru başına ~21 bin token ekliyordu; v3'te kaldırıldı.)

**2) GUI'yi gerçekten sürmenin maliyeti (bu repodaki V53–V63 girişi).** Orkestratör ajan
G*Power'ı bilgisayar kullanımıyla (ekran görüntüsü + tıklama) sürdü: 11 vektör için
8 küçük (874×491), 3 tam (1456×819), 14 pencere yakınlaştırması alındı ve ~30 araç
çağrısı yapıldı. Anthropic'in görüntü token formülüyle (genişlik × yükseklik / 750)
yalnızca görüntüler ≈ **16 500 token**, yani vektör başına ≈ **1 500 token** + ~3 araç
çağrısı. (Görüntü boyutları gerçek; token sayısı formülden **hesaplandı**, API'den okunmadı.)

| | MCP | GUI'yi sürmek |
|---|---:|---:|
| Değişken girdi / soru | ~40 token | ~1 500 token |
| Araç çağrısı / soru | 1 | ~3 |
| Hata kipi | yok (yapısal JSON) | yanlış alan, okunamayan basamak, açık kalan iletişim kutusu |

**Sonuç.** Son sürümün iki koşusunda **19/20** (v3 10/10, tekrar 9/10); 20 yanıtın hiçbirinde
kaynaksız sayı yok. Ajan sayıları hiç hesaplamadan MCP
aracından aktarabiliyor. Tek bir hazır ekran görüntüsünü okumak MCP kadar ucuz, ama
o görüntüyü üretmek (GUI'yi sürmek) MCP'ye göre ~35 kat daha fazla değişken token ve
daha fazla hata noktası demek.

## Ajanın hesap yapmaması nasıl güvenceye alındı

- Yerleşik araçlar kapalı: ajanın Bash/Python çalıştırma imkânı yok.
- MCP sunucusu motoru çağırır ve CLI ile **aynı** biçimlendirme fonksiyonunu kullanır
  (`tests/test_mcp_equality.py`: 51 girdide MCP nesnesi = CLI JSON'u).
- `hesap_yapmadi` kontrolü: yanıttaki her sayı soruda ya da araç çıktısında geçmeli.
  v1'deki iki ihlal (H-05) ve v3a'daki uydurma örnek sayılar (H-07) bu kontrolle yakalandı.

Çalıştırma (repo kökü): `python eval/agent_eval.py --model haiku`
(`GPOWER_VENV` = `gpower-clone-mcp` komutunun kurulu olduğu sanal ortam).
