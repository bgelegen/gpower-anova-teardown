"""Differential test against G*Power GUI vectors (skipped without oracle files)."""
import pytest

from helpers import compare_gui_row, read_csv

ROWS = read_csv("gpower_gui_vectors.csv")

# SPEC R-18: G*Power's own value is numerically noisy here; we compute the exact
# answer, so the mismatch is expected and recorded (known numerical deviation).
KNOWN_DEVIATION = {"V52", "V54", "V55", "V56"}
R18 = ("R-18: G*Power's non-central F is numerically noisy for df2 >~ 2e8; "
       "we do not imitate it (known numerical deviation, proven in "
       "tests/test_r18_high_precision.py and oracle/R18_YUKSEK_HASSASIYET.md)")


def _params():
    for row in ROWS:
        vid = row.get("id", "").strip()
        marks = []
        if vid.upper() in KNOWN_DEVIATION:
            marks.append(pytest.mark.xfail(strict=True, reason=R18))
        yield pytest.param(row, id=vid, marks=marks)


@pytest.mark.skipif(not ROWS, reason="oracle/gpower_gui_vectors.csv not found")
@pytest.mark.parametrize("row", list(_params()))
def test_gui_vector(row):
    bad = compare_gui_row(row)
    assert not bad, "; ".join(bad)
