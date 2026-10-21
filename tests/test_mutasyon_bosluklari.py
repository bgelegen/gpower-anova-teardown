"""Mutasyon testinin (tools/mutasyon.py, MUTATION.md) ortaya çıkardığı iki test açığını kapatır.

İlk kampanyada bu iki mutant hiçbir test başarısız olmadan "yaşadı":
  M17  güç alt sınırını hariç tutmak  (POWER_MIN < güç)      → R-11 uçları dahil
  M26  CLI'de konumsal argümanı yutmak                        → CONTRACT: geçersiz girdi
"""
import json
import subprocess
import sys

from gpower_clone.engine import calculate


def test_R11_power_lower_bound_is_inclusive():
    """SPEC §2: güç ∈ [1e-7; 0,9999999], uçlar DAHİL. α = güç = 1e-7 geçerlidir ve
    R-12 gereği (güç = α) kök bulunamaz → N = 2k."""
    r = calculate(mode="a-priori", f=0.25, alpha=1e-7, power=1e-7, groups=3)
    assert r.total_n == 6


def test_cli_positional_argument_is_rejected_with_its_own_message():
    """CONTRACT §3: bayraksız argüman geçersiz girdidir; mesaj neyin yanlış olduğunu söyler."""
    p = subprocess.run([sys.executable, "-m", "gpower_clone.cli", "--mode", "a-priori", "foo",
                        "--f", "0.25"], capture_output=True, text=True)
    assert p.returncode == 2
    assert json.loads(p.stdout) == {"error": "Unexpected argument: foo"}
