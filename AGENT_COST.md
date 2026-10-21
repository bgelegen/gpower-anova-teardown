# Ajan Maliyet Günlüğü

Değerler **ölçülmüştür**: başsız oturumlarda Claude Code'un `result` olayındaki `usage` /
`total_cost_usd` alanları, etkileşimli oturumda `/usage` ekranı. Kayıtlar: `logs/` (O2'nin tam akışı ve kota dökümleri).
O1'in akışı REA'nın decompile çıktılarını içerdiği için kural gereği repoya konmadı; yerelde
`YZM301-teardown\loglar\oturum1-devam.jsonl` olarak duruyor.
"Liste maliyeti" API liste fiyatıyla karşılığıdır; çalışmalar abonelik kotasından yürüdü,
ayrıca ödeme yapılmadı.

| Oturum | Amaç | Model | Süre | Tur | Girdi token (yeni + önbellek yazma + önbellek okuma) | Çıktı token (düşünme dahil) | Liste maliyeti | Kota (5 saatlik pencere) |
|--------|------|-------|-----:|----:|------------------------------------------------------|-----------------------------|---------------:|--------------------------|
| O1 · ilk tur | Söküm: REA + Ghidra → SPEC + LEDGER taslağı | Opus | ~20 dk | — | ölçülemedi (etkileşimli) | ölçülemedi | — | → %38 |
| O1 · devam | Oracle'a göre doğrulama, kılavuz [DOK] satırları, yeni [REA] aramaları | Opus | 14,0 dk | 40 | 62 + 180 590 + 12 848 845 | 51 212 (19 487) | 5,04 $ | %38 → %67 |
| O2 · temiz oda | SPEC'ten motor + CLI + MCP + testler | Sonnet | 20,0 dk | 41 | 60 + 94 524 + 2 253 495 | 56 705 (16 645) | 1,17 $ | %67 → %85 |
| AJAN · v1 | 10 klinik soru × (MCP + GUI-görüntü) | Haiku | — | 19 (MCP kolu) | 641 420 (toplam) | 8 550 | 0,022 $ | bulut |
| AJAN · v2 | sıkı sistem mesajı | Haiku | — | 19 | 643 079 | 8 079 | 0,019 $ | bulut |
| AJAN · v3a | bağlamda yalnızca `anova_oneway` | Haiku | — | 23 | 278 237 | 11 033 | 0,020 $ | bulut |
| AJAN · v3 | + araç açıklamasında sayı biçimi (son sürüm) | Haiku | — | 19 | 250 351 | 8 822 | 0,016 $ | bulut |
| AJAN · v3 tekrar | kararlılık | Haiku | — | 19 | 250 633 | 8 820 | 0,012 $ | bulut |

## Araç kullanımı

| Oturum | Araç çağrıları |
|--------|----------------|
| O1 · devam | `rea` 21 · Bash 9 · Read 5 · ToolSearch 2 · Write 2 (toplam 39) |
| O2 | Bash 25 · Write 10 · Read 2 · Edit 2 · PowerShell 1 — **MCP sunucusu 0** (REA yüklenmedi; `--strict-mcp-config` + boş yapılandırma) |
| AJAN v3 | `anova_oneway` 9 (S10 kapsam dışı: 0); v3a'da 13 (virgüllü girdiler yeniden denendi) |

## Gözlemler

- **En pahalı adım söküm:** O1 devam turunun girdisinin %98'i önbellekten okunan bağlam
  (12,8 M token). REA araç çıktıları (decompile, xref, dizgi listeleri) bağlamı hızla
  büyütüyor; Claude Code'un `/usage` önerisi de "rea'yı gerekmediğinde kapat" oldu
  (`logs/oturum1-maliyet-*.txt`).
- **Yazım, söküme göre ~4 kat ucuz** (1,17 $ / 5,04 $): SPEC iyi olunca yeniden yazım
  oturumu binary'ye hiç bakmadan 41 turda bitti.
- **Kota sınırı gerçek bir risk:** ilk ajan değerlendirmesi yerel makinede "session limit"
  hatasıyla boş döndü (`logs/ajan-degerlendirme-yerel-kota-hatasi.txt`, 10/10 soru boş); değerlendirme
  bulut çalışma alanında yeniden koşuldu.
- v1/v2'de girdi tokenleri v3'ün ~2,5 katı: bulut ortamı ajana 22 ilgisiz tarayıcı aracı
  ekliyordu; `--disallowedTools` ile kaldırılınca soru başı maliyet düştü (`eval/OZET.md`).
- Orkestratör ajanın (oturumları hazırlayan, oracle'ı GUI'den dolduran ve değerlendiren
  sohbet) maliyeti Claude Code dışında olduğu için ölçülemedi; GUI sürme maliyetinin
  hesaplanmış karşılığı `eval/OZET.md`'de.
