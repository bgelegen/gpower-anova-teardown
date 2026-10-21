"""Mutasyon testi: test paketi gerçek hataları yakalıyor mu?

Her mutant, motora / gösterime / CLI'ye bilerek sokulmuş TEK bir küçük hatadır
(G*Power'ın gizli kurallarını bozan türden). Mutant kaynağın geçici bir kopyasına
uygulanır, test paketi o kopyaya karşı koşulur:
    test başarısız  → mutant ÖLDÜRÜLDÜ (iyi: test hatayı yakaladı)
    testler geçti   → mutant YAŞADI (ya test eksik ya da mutant eşdeğer)

Kullanım (repo kökü):  python tools/mutasyon.py      → MUTATION.md
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "src" / "gpower_clone"

# Hızlı paket: kural testleri + iki katman oracle + özellik testleri + R-18 kanıtı.
FAST = ["tests/test_rules.py", "tests/test_oracle_gui.py", "tests/test_oracle_library.py",
        "tests/test_properties.py", "tests/test_r18_high_precision.py",
        "tests/test_mutasyon_bosluklari.py"]
CLI = ["tests/test_cli.py"]

# (kimlik, dosya, eski, yeni, hangi kural, açıklama, ek testler)
MUTANTS = [
    ("M01", "engine.py", "n = math.ceil(n_raw / k) * k", "n = round(n_raw / k) * k",
     "R-05", "k katına yukarı değil en yakına yuvarla", []),
    ("M02", "engine.py", "n = math.ceil(n_raw / k) * k", "n = math.ceil(n_raw)",
     "R-05", "k katına yuvarlamayı unut (yalnızca tam sayıya yukarı)", []),
    ("M03", "engine.py", "df1, df2 = k - 1, n - k", "df1, df2 = k - 1, n - k - 1",
     "R-02", "payda serbestlik derecesinde bir eksik", []),
    ("M04", "engine.py", "lam = f * f * n\n", "lam = f * f * n / k\n",
     "R-03", "λ'yı toplam N yerine grup başı n ile kur", []),
    ("M05", "engine.py", "lam = f * f * n\n", "lam = f * n\n",
     "R-03", "λ = f·N (kare unutuldu)", []),
    ("M06", "engine.py", "return float(stats.f.isf(alpha, df1, df2))",
     "return float(stats.f.isf(alpha / 2, df1, df2))",
     "R-03", "kritik F'de iki yönlü α/2 (t testi alışkanlığı)", []),
    ("M07", "engine.py", "n = math.ceil((k + 1) / k) * k", "n = k + 1",
     "R-06", "alt sınırı k+1'de bırak (yeniden k katına yuvarlama yok)", []),
    ("M08", "engine.py", "if not f_lo <= fv <= F_MAX:", "if not f_lo < fv <= F_MAX:",
     "R-10", "f alt ucunu hariç tut (post hoc f = 0 geçersiz olur)", []),
    ("M09", "engine.py", "F_MAX = 50.0", "F_MAX = 51.0",
     "R-10", "f üst sınırı 51", []),
    ("M10", "engine.py", "if k < 2:", "if k < 1:",
     "R-09", "tek gruba izin ver", []),
    ("M11", "engine.py", "return math.floor(x + 0.5)", "return round(x)",
     "R-17", "yarım yukarı yerine bankacı yuvarlaması (2,5 → 2)", []),
    ("M12", "engine.py", "if a > target:", "if a >= target:",
     "R-12", "güç = α'yı da hata say", []),
    ("M13", "engine.py", "if n <= k:", "if n < k:",
     "R-13", "post hoc N = k'ya izin ver", []),
    ("M14", "engine.py", "if n % k:", "if n % k == 0:",
     "R-14", "uyarı koşulunu ters çevir", []),
    ("M15", "engine.py", "based on the average group size.", "based on the mean group size.",
     "R-14", "uyarı metninde tek kelime", []),
    ("M16", "engine.py", "ALPHA_MAX = 0.9999999", "ALPHA_MAX = 0.999999",
     "R-11", "α üst sınırında bir hane eksik", []),
    ("M17", "engine.py", "if not POWER_MIN <= target <= POWER_MAX:",
     "if not POWER_MIN < target <= POWER_MAX:",
     "R-11", "güç alt ucunu hariç tut", []),
    ("M18", "engine.py", "lower, upper = upper, 1.6 * upper", "lower, upper = upper, 2.0 * upper",
     "R-04", "aralık büyütme çarpanı 1,6 → 2 (eşdeğer olması beklenir)", []),
    ("M19", "engine.py", "rtol=4 * 2.0 ** -52", "rtol=1e-3",
     "R-04", "kök bulucu toleransını gevşet", []),
    ("M20", "engine.py", "per_group=n / k", "per_group=n // k",
     "R-14", "post hoc ortalama grup büyüklüğünü tam sayıya kes", []),
    ("M21", "display.py", "if 0.01 < abs(x) < 100:", "if 0.01 < abs(x) < 1000:",
     "R-15", "%.7f / %.7g eşiği 100 → 1000", []),
    ("M22", "display.py", "if 0.01 < abs(x) < 100:", "if 0.01 <= abs(x) < 100:",
     "R-15", "alt eşik dahil", []),
    ("M23", "display.py", 'return f"{x:.7f}"', 'return f"{x:.6f}"',
     "R-15", "6 ondalık (kılavuz örneğinin biçimi)", []),
    ("M24", "display.py", "return str(math.floor(x + 0.5))", "return str(int(x))",
     "R-15", "tam sayı alanında kesme", []),
    ("M25", "contract.py", "DEFAULT_DIGITS = 4", "DEFAULT_DIGITS = 3",
     "CONTRACT", "varsayılan JSON hanesi 3", CLI),
    ("M26", "cli.py", "if not token.startswith(\"--\"):", "if False:",
     "CONTRACT", "konumsal argüman kontrolünü kaldır", CLI),
]


def run(tests: list[str], src: Path) -> tuple[bool, str, float]:
    env = dict(os.environ, PYTHONPATH=str(src), PROPS_EXAMPLES="60")
    t0 = time.time()
    p = subprocess.run([sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider",
                        *tests], cwd=ROOT, env=env, capture_output=True, text=True)
    killer = ""
    m = re.search(r"^FAILED (\S+)", p.stdout, re.M)
    if m:
        killer = m.group(1).split("[")[0]
    return p.returncode == 0, killer, time.time() - t0


def main() -> int:
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src"
        shutil.copytree(PKG, src / "gpower_clone")
        ok, _, sec = run(FAST + CLI, src)
        assert ok, "mutasyonsuz kaynakta testler geçmeli"
        print(f"temel koşu: {sec:.0f} sn", flush=True)
        for mid, fname, old, new, rule, why, extra in MUTANTS:
            target = src / "gpower_clone" / fname
            original = target.read_text(encoding="utf-8")
            assert original.count(old) >= 1, f"{mid}: kalıp bulunamadı"
            target.write_text(original.replace(old, new, 1), encoding="utf-8")
            survived, killer, sec = run(FAST + extra, src)
            target.write_text(original, encoding="utf-8")
            rows.append((mid, fname, rule, why, old, new, survived, killer, sec))
            print(f"{mid} {'YAŞADI' if survived else 'öldü   ← ' + killer} ({sec:.0f} sn)", flush=True)
    write_report(rows)
    return 0


def write_report(rows) -> None:
    killed = sum(not r[6] for r in rows)
    lines = [
        "# Mutasyon testi",
        "",
        "Test paketi gerçekten hata yakalıyor mu? Motora, gösterime ve CLI'ye bilerek "
        "**tek bir küçük hata** sokulur (mutant) ve test paketi koşulur. Test başarısız olursa "
        "mutant *öldürülmüştür*. Mutantlar rastgele değil, G*Power'ın gizli kurallarını "
        "(SPEC R-xx) bozacak şekilde elle seçildi. Araç: `tools/mutasyon.py`.",
        "",
        f"**Sonuç: {killed} / {len(rows)} mutant öldürüldü "
        f"(mutasyon skoru %{100 * killed / len(rows):.0f}).**",
        "",
        "| Mutant | Dosya | Kural | Sokulan hata | Sonuç | İlk yakalayan test |",
        "|--------|-------|-------|--------------|-------|--------------------|",
    ]
    for mid, fname, rule, why, old, new, survived, killer, sec in rows:
        res = "🟡 yaşadı" if survived else "✅ öldü"
        lines.append(f"| {mid} | `{fname}` | {rule} | {why}<br>`{old.strip()}` → `{new.strip()}` "
                     f"| {res} | {('`' + killer + '`') if killer else '—'} |")
    survivors = [r for r in rows if r[6]]
    lines += ["", "## Yaşayan mutantlar", ""]
    if not survivors:
        lines.append("Yok.")
    for mid, fname, rule, why, *_ in survivors:
        lines.append(f"- **{mid}** ({why}): " + EXPLAIN.get(mid, "incelenmeli."))
    (ROOT / "MUTATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


EXPLAIN = {
    "M18": "**eşdeğer mutant.** Çarpan yalnızca kök arama aralığının ne kadar hızlı "
           "genişlediğini değiştirir; Brent aynı kökü bulur ve sonuç k'nın katına "
           "yuvarlandığı için hiçbir çıktı değişmez. Hiçbir test bunu yakalayamaz — "
           "yakalayamaması da doğrudur (SPEC R-04: 'herhangi bir doğru kök bulucu aynı N'i verir').",
    "M19": "**pratikte eşdeğer.** Kök ~1e-3 göreli hatayla bulunsa da N k'nın bir sonraki "
           "katına yuvarlanır; ham kökün k-katı sınırına 1e-3'ten yakın düştüğü bir girdi "
           "test kümesinde yok.",
}


if __name__ == "__main__":
    sys.exit(main())
