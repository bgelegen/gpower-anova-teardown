"""Kütüphane oracle'ı: statsmodels FTestAnovaPower ile 500+ vektör üretir.

İkinci katman kâhindir (slayt 17). G*Power'ın yerini tutmaz:
- statsmodels a priori modda KESİRLİ toplam N verir; G*Power tam sayıya
  yuvarlar. Bu fark bir bulgudur (slayt 20) ve testlerde ayrıca ele alınır:
  beklenen N, ham N'den G*Power'ın kuralıyla (SPEC.md) türetilir.
- post hoc güç değerleri doğrudan karşılaştırılabilir.

Kullanım:  python oracle/gen_library_vectors.py
Çıktı:     oracle/library_vectors.csv
"""
import csv
import itertools
import sys
from pathlib import Path

import statsmodels
from statsmodels.stats.power import FTestAnovaPower

OUT = Path(__file__).with_name("library_vectors.csv")
solver = FTestAnovaPower()

F_VALUES = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.75, 1.00]
ALPHAS = [0.01, 0.05, 0.10]
POWERS = [0.80, 0.90, 0.95]
GROUPS = [2, 3, 4, 5, 6]
POSTHOC_N_PER_GROUP = [5, 10, 20, 30, 50, 100]


def main() -> int:
    rows = []
    for f, a, p, k in itertools.product(F_VALUES, ALPHAS, POWERS, GROUPS):
        n = solver.solve_power(effect_size=f, nobs=None, alpha=a, power=p, k_groups=k)
        rows.append({"mode": "a-priori", "f": f, "alpha": a, "power": p, "groups": k,
                     "n_total": "", "lib_n_total_raw": f"{float(n):.6f}", "lib_power": ""})
    for f, a, k, m in itertools.product(F_VALUES, ALPHAS, GROUPS, POSTHOC_N_PER_GROUP):
        n = k * m
        pw = solver.power(effect_size=f, nobs=n, alpha=a, k_groups=k)
        rows.append({"mode": "post-hoc", "f": f, "alpha": a, "power": "", "groups": k,
                     "n_total": n, "lib_n_total_raw": "", "lib_power": f"{float(pw):.6f}"})
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"{len(rows)} vektör → {OUT.name} (statsmodels {statsmodels.__version__})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
