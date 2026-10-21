"""Canlı demo (docs/) tarayıcıda **aynı motoru** çalıştırır: oradaki Python dosyaları
src/ ile birebir olmalı. Fark varsa `python tools/build_site.py` çalıştırılmamıştır."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [(ROOT / "src" / "gpower_clone" / n, ROOT / "docs" / "py" / "gpower_clone" / n)
         for n in ["__init__.py", "contract.py", "engine.py", "display.py", "cli.py"]]
PAIRS.append((ROOT / "tests" / "helpers.py", ROOT / "docs" / "py" / "helpers.py"))


@pytest.mark.parametrize("src,web", PAIRS, ids=[p[0].name for p in PAIRS])
def test_web_demo_runs_the_same_engine(src, web):
    assert web.read_bytes() == src.read_bytes(), f"{web} eski; tools/build_site.py çalıştırın"


def test_web_oracle_copy_is_current():
    assert (ROOT / "docs" / "data" / "oracle.csv").read_bytes() == \
        (ROOT / "oracle" / "gpower_gui_vectors.csv").read_bytes()
