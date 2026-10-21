# Mutasyon testi

Test paketi gerçekten hata yakalıyor mu? Motora, gösterime ve CLI'ye bilerek **tek bir küçük hata** sokulur (mutant) ve test paketi koşulur. Test başarısız olursa mutant *öldürülmüştür*. Mutantlar rastgele değil, G*Power'ın gizli kurallarını (SPEC R-xx) bozacak şekilde elle seçildi. Araç: `tools/mutasyon.py`.

**Sonuç: 25 / 26 mutant öldürüldü (mutasyon skoru %96).**

| Mutant | Dosya | Kural | Sokulan hata | Sonuç | İlk yakalayan test |
|--------|-------|-------|--------------|-------|--------------------|
| M01 | `engine.py` | R-05 | k katına yukarı değil en yakına yuvarla<br>`n = math.ceil(n_raw / k) * k` → `n = round(n_raw / k) * k` | ✅ öldü | `tests/test_rules.py::test_R01_apriori_outputs` |
| M02 | `engine.py` | R-05 | k katına yuvarlamayı unut (yalnızca tam sayıya yukarı)<br>`n = math.ceil(n_raw / k) * k` → `n = math.ceil(n_raw)` | ✅ öldü | `tests/test_rules.py::test_R01_apriori_outputs` |
| M03 | `engine.py` | R-02 | payda serbestlik derecesinde bir eksik<br>`df1, df2 = k - 1, n - k` → `df1, df2 = k - 1, n - k - 1` | ✅ öldü | `tests/test_rules.py::test_R01_posthoc_outputs_v34` |
| M04 | `engine.py` | R-03 | λ'yı toplam N yerine grup başı n ile kur<br>`lam = f * f * n` → `lam = f * f * n / k` | ✅ öldü | `tests/test_rules.py::test_R01_apriori_outputs` |
| M05 | `engine.py` | R-03 | λ = f·N (kare unutuldu)<br>`lam = f * f * n` → `lam = f * n` | ✅ öldü | `tests/test_rules.py::test_R01_apriori_outputs` |
| M06 | `engine.py` | R-03 | kritik F'de iki yönlü α/2 (t testi alışkanlığı)<br>`return float(stats.f.isf(alpha, df1, df2))` → `return float(stats.f.isf(alpha / 2, df1, df2))` | ✅ öldü | `tests/test_rules.py::test_R01_apriori_outputs` |
| M07 | `engine.py` | R-06 | alt sınırı k+1'de bırak (yeniden k katına yuvarlama yok)<br>`n = math.ceil((k + 1) / k) * k` → `n = k + 1` | ✅ öldü | `tests/test_rules.py::test_R06_minimum_total_is_two_k` |
| M08 | `engine.py` | R-10 | f alt ucunu hariç tut (post hoc f = 0 geçersiz olur)<br>`if not f_lo <= fv <= F_MAX:` → `if not f_lo < fv <= F_MAX:` | ✅ öldü | `tests/test_rules.py::test_R10_posthoc_range_and_zero_is_valid` |
| M09 | `engine.py` | R-10 | f üst sınırı 51<br>`F_MAX = 50.0` → `F_MAX = 51.0` | ✅ öldü | `tests/test_rules.py::test_R10_apriori_range_and_message` |
| M10 | `engine.py` | R-09 | tek gruba izin ver<br>`if k < 2:` → `if k < 1:` | ✅ öldü | `tests/test_rules.py::test_R08_apriori_order` |
| M11 | `engine.py` | R-17 | yarım yukarı yerine bankacı yuvarlaması (2,5 → 2)<br>`return math.floor(x + 0.5)` → `return round(x)` | ✅ öldü | `tests/test_rules.py::test_R17_fractional_groups_round_half_up` |
| M12 | `engine.py` | R-12 | güç = α'yı da hata say<br>`if a > target:` → `if a >= target:` | ✅ öldü | `tests/test_rules.py::test_R12_power_equal_alpha_gives_two_k` |
| M13 | `engine.py` | R-13 | post hoc N = k'ya izin ver<br>`if n <= k:` → `if n < k:` | ✅ öldü | `tests/test_rules.py::test_R13_n_not_above_k` |
| M14 | `engine.py` | R-14 | uyarı koşulunu ters çevir<br>`if n % k:` → `if n % k == 0:` | ✅ öldü | `tests/test_rules.py::test_R14_warning_and_calculation_with_given_n` |
| M15 | `engine.py` | R-14 | uyarı metninde tek kelime<br>`based on the average group size.` → `based on the mean group size.` | ✅ öldü | `tests/test_rules.py::test_R14_warning_and_calculation_with_given_n` |
| M16 | `engine.py` | R-11 | α üst sınırında bir hane eksik<br>`ALPHA_MAX = 0.9999999` → `ALPHA_MAX = 0.999999` | ✅ öldü | `tests/test_rules.py::test_R11_alpha_range` |
| M17 | `engine.py` | R-11 | güç alt ucunu hariç tut<br>`if not POWER_MIN <= target <= POWER_MAX:` → `if not POWER_MIN < target <= POWER_MAX:` | ✅ öldü | `tests/test_mutasyon_bosluklari.py::test_R11_power_lower_bound_is_inclusive` |
| M18 | `engine.py` | R-04 | aralık büyütme çarpanı 1,6 → 2 (eşdeğer olması beklenir)<br>`lower, upper = upper, 1.6 * upper` → `lower, upper = upper, 2.0 * upper` | 🟡 yaşadı | — |
| M19 | `engine.py` | R-04 | kök bulucu toleransını gevşet<br>`rtol=4 * 2.0 ** -52` → `rtol=1e-3` | ✅ öldü | `tests/test_rules.py::test_R04_continuous_root_matches_bisection` |
| M20 | `engine.py` | R-14 | post hoc ortalama grup büyüklüğünü tam sayıya kes<br>`per_group=n / k` → `per_group=n // k` | ✅ öldü | `tests/test_rules.py::test_R14_warning_and_calculation_with_given_n` |
| M21 | `display.py` | R-15 | %.7f / %.7g eşiği 100 → 1000<br>`if 0.01 < abs(x) < 100:` → `if 0.01 < abs(x) < 1000:` | ✅ öldü | `tests/test_rules.py::test_R15_fraction_format` |
| M22 | `display.py` | R-15 | alt eşik dahil<br>`if 0.01 < abs(x) < 100:` → `if 0.01 <= abs(x) < 100:` | ✅ öldü | `tests/test_rules.py::test_R15_fraction_format` |
| M23 | `display.py` | R-15 | 6 ondalık (kılavuz örneğinin biçimi)<br>`return f"{x:.7f}"` → `return f"{x:.6f}"` | ✅ öldü | `tests/test_rules.py::test_R01_apriori_outputs` |
| M24 | `display.py` | R-15 | tam sayı alanında kesme<br>`return str(math.floor(x + 0.5))` → `return str(int(x))` | ✅ öldü | `tests/test_rules.py::test_R15_integer_format` |
| M25 | `contract.py` | CONTRACT | varsayılan JSON hanesi 3<br>`DEFAULT_DIGITS = 4` → `DEFAULT_DIGITS = 3` | ✅ öldü | `tests/test_properties.py::test_P8_cli_json_equals_engine` |
| M26 | `cli.py` | CONTRACT | konumsal argüman kontrolünü kaldır<br>`if not token.startswith("--"):` → `if False:` | ✅ öldü | `tests/test_mutasyon_bosluklari.py::test_cli_positional_argument_is_rejected_with_its_own_message` |

## Yaşayan mutantlar

- **M18** (aralık büyütme çarpanı 1,6 → 2 (eşdeğer olması beklenir)): **eşdeğer mutant.** Çarpan yalnızca kök arama aralığının ne kadar hızlı genişlediğini değiştirir; Brent aynı kökü bulur ve sonuç k'nın katına yuvarlandığı için hiçbir çıktı değişmez. Hiçbir test bunu yakalayamaz — yakalayamaması da doğrudur (SPEC R-04: 'herhangi bir doğru kök bulucu aynı N'i verir').

## Kampanya geçmişi — mutasyon testi iki test açığı buldu

| Koşu | Öldürülen | Yaşayan | Ne yapıldı |
|------|----------:|---------|------------|
| 1 | 23 / 26 (%88) | M17, M18, M26 | M18 eşdeğer. **M17** (güç alt sınırı hariç) ve **M26** (konumsal argüman kontrolü kaldırıldı) hiçbir testi kırmadı → iki gerçek test açığı. |
| 2 | **25 / 26 (%96)** | yalnızca M18 (eşdeğer) | `tests/test_mutasyon_bosluklari.py` eklendi: güç = α = 1e-7 sınırı (SPEC §2 "uçlar dahil") ve `Unexpected argument` mesajı. **Eşdeğer olmayan mutantların tamamı öldürüldü.** |

Ders (Sommerville 8.1): Oracle vektörleri ve %100 geçen 1750 test, iki sınır kuralını
hiç sınamıyordu; bunu "testleri test eden" mutasyon analizi gösterdi.

Yeniden üretmek için: `python tools/mutasyon.py` (~4 dk; her mutant hızlı paket ile koşulur,
CLI mutantları ayrıca `tests/test_cli.py` ile).
