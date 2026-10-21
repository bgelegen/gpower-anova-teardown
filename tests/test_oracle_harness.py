"""Self-check of the oracle comparison code with synthetic rows (no real oracle needed)."""
import helpers
from helpers import compare_gui_row

HEAD = dict(id="T", mode="a-priori", f="0.25", alpha="0.05", power="0.95",
            groups="3", n_total="", gp_n_total="", gp_actual_power="",
            gp_critical="", gp_df1="", gp_df2="", gp_ncp="", gp_mesaj="")


def row(**kw):
    return {**HEAD, **kw}


def test_harness_matching_apriori_row():
    r = row(gp_n_total="252", gp_df1="2", gp_df2="249", gp_ncp="15.7500000",
            gp_critical="3.0320649", gp_actual_power="0.9514888")
    assert compare_gui_row(r) == []


def test_harness_reports_vector_id_on_mismatch():
    bad = compare_gui_row(row(id="V99", gp_n_total="255", gp_ncp="15.0"))
    assert bad and all(m.startswith("V99:") for m in bad)


def test_harness_error_row_whitespace_insensitive():
    r = row(power="0.03", gp_mesaj="Power must be greater\nthan or equal to alpha.")
    assert compare_gui_row(r) == []
    assert compare_gui_row(row(power="0.03", gp_mesaj="other")) != []


def test_harness_warning_row():
    r = row(mode="post-hoc", power="", n_total="61", gp_n_total="61",
            gp_mesaj="Please note: The total sample size (61) is not a multiple of\n"
                     "the number of groups (3). The analysis was\n"
                     "based on the average group size.")
    assert compare_gui_row(r) == []


def test_harness_oracle_dir_env(monkeypatch, tmp_path):
    (tmp_path / "x.csv").write_text("a;b\n1;2\n", encoding="utf-8")
    monkeypatch.setenv("ORACLE_DIR", str(tmp_path))
    assert helpers.read_csv("x.csv") == [{"a": "1", "b": "2"}]
    assert helpers.read_csv("missing.csv") == []
