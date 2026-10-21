"""Canlı demo sitesini (GitHub Pages, docs/) üretir.

- docs/py/gpower_clone/*.py : motorun kendisi (src/ ile birebir; tests/test_site_sync.py denetler)
- docs/py/helpers.py        : diferansiyel testin karşılaştırma kodu (tests/helpers.py ile birebir)
- docs/data/vectors.json    : 63 G*Power vektörü + motorun aynı girdideki gösterimi
- docs/data/oracle.csv      : oracle CSV'sinin kopyası (tarayıcıda yeniden doğrulama için)

Kullanım (repo kökü): python tools/build_site.py
"""
from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from helpers import compare_gui_row, engine_inputs, read_csv  # noqa: E402

from gpower_clone import engine  # noqa: E402
from gpower_clone.display import format_fraction, format_integer  # noqa: E402

DOCS = ROOT / "docs"
PY_FILES = ["__init__.py", "contract.py", "engine.py", "display.py", "cli.py"]
RAW = "https://raw.githubusercontent.com/bgelegen/gpower-anova-teardown/main/oracle/"
KNOWN = {"V52", "V54", "V55", "V56"}


def main() -> int:
    pkg = DOCS / "py" / "gpower_clone"
    pkg.mkdir(parents=True, exist_ok=True)
    for name in PY_FILES:
        shutil.copyfile(ROOT / "src" / "gpower_clone" / name, pkg / name)
    shutil.copyfile(ROOT / "tests" / "helpers.py", DOCS / "py" / "helpers.py")
    (DOCS / "data").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "oracle" / "gpower_gui_vectors.csv", DOCS / "data" / "oracle.csv")

    out = []
    for row in read_csv("gpower_gui_vectors.csv"):
        vid = row["id"]
        bad = compare_gui_row(row)
        try:
            r = engine.calculate(**engine_inputs(row))
            motor = {"n": format_integer(r.total_n), "power": format_fraction(r.power),
                     "critical": format_fraction(r.critical), "df1": format_integer(r.df1),
                     "df2": format_integer(r.df2), "ncp": format_fraction(r.ncp),
                     "message": " ".join(r.warnings)}
        except engine.GPowerError as exc:
            motor = {"message": str(exc)}
        gp = {"n": row["gp_n_total"], "power": row["gp_actual_power"],
              "critical": row["gp_critical"], "df1": row["gp_df1"], "df2": row["gp_df2"],
              "ncp": row["gp_ncp"], "message": row["gp_mesaj"]}
        status = "known" if vid in KNOWN else ("ok" if not bad else "fail")
        kind = "error" if not row["gp_n_total"].strip() else (
            "note" if row["gp_mesaj"].lower().startswith("please note") else "result")
        out.append({"id": vid, "mode": row["mode"], "f": row["f"], "alpha": row["alpha"],
                    "power": row["power"], "groups": row["groups"], "n_total": row["n_total"],
                    "why": row["neden"], "kind": kind, "status": status, "gp": gp,
                    "motor": motor, "diff": bad, "shot": RAW + row["ekran_goruntusu"]})
    (DOCS / "data" / "vectors.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                                encoding="utf-8")
    ok = sum(v["status"] == "ok" for v in out)
    print(f"{len(out)} vektör · {ok} birebir · {sum(v['status'] == 'known' for v in out)} bilinen sapma"
          f" · {sum(v['status'] == 'fail' for v in out)} uyuşmazlık")
    return 0


if __name__ == "__main__":
    sys.exit(main())
