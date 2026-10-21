"""Differential test against statsmodels vectors (skipped without oracle files)."""
import math

import pytest

from gpower_clone import engine
from gpower_clone.contract import APRIORI
from helpers import blank, canonical_mode, engine_inputs, read_csv

ROWS = read_csv("library_vectors.csv")


def _id(i, row):
    return (f"row{i}-{row['mode']}-f{row['f']}-a{row['alpha']}-"
            f"p{row.get('power') or '-'}-k{row['groups']}-n{row.get('n_total') or '-'}")


def expected_n(raw: float, k: int) -> int:
    """SPEC R-05/R-06 applied to the library's raw fractional N."""
    n = math.ceil(raw / k) * k
    return n if n >= k + 1 else 2 * k


@pytest.mark.skipif(not ROWS, reason="oracle/library_vectors.csv not found")
@pytest.mark.parametrize("i,row", [pytest.param(i, r, id=f"row{i}")
                                   for i, r in enumerate(ROWS)])
def test_library_vector(i, row):
    vid = _id(i, row)
    try:
        res = engine.calculate(**engine_inputs(row))
    except engine.GPowerError as exc:
        pytest.fail(f"{vid}: engine error {exc}")
    if canonical_mode(row["mode"]) == APRIORI:
        if blank(row.get("lib_n_total_raw")):
            pytest.skip("no library value")
        k = engine._round_half_up(float(row["groups"]))
        want = expected_n(float(row["lib_n_total_raw"]), k)
        assert res.total_n == want, (
            f"{vid}: N engine {res.total_n} != library-derived {want} "
            f"(raw {row['lib_n_total_raw']})")
    else:
        if blank(row.get("lib_power")):
            pytest.skip("no library value")
        diff = abs(res.power - float(row["lib_power"]))
        assert diff < 1e-6, (f"{vid}: power engine {res.power!r} vs library "
                             f"{row['lib_power']} (|diff| {diff:.3g})")
