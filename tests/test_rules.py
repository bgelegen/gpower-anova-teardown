"""One or more tests per SPEC rule (R-xx) and per Gherkin scenario (test_G*)."""
import math

import pytest
from scipy import stats

from gpower_clone import engine
from gpower_clone.contract import APRIORI, POSTHOC
from gpower_clone.display import format_fraction, format_integer, format_result
from gpower_clone.engine import GPowerError, calculate
from helpers import assert_vector


def apriori(f=0.25, alpha=0.05, power=0.95, groups=3):
    return calculate(APRIORI, f, alpha, groups, power=power)


def posthoc(f=0.25, alpha=0.05, total_n=60, groups=3):
    return calculate(POSTHOC, f, alpha, groups, total_n=total_n)


def err(**kw):
    mode = kw.pop("mode", APRIORI)
    kw.setdefault("f", 0.25)
    kw.setdefault("alpha", 0.05)
    kw.setdefault("groups", 3)
    if mode == APRIORI:
        kw.setdefault("power", 0.95)
    else:
        kw.setdefault("total_n", 60)
    with pytest.raises(GPowerError) as ei:
        calculate(mode, **kw)
    return " ".join(str(ei.value).split())


def independent_power(f, alpha, k, n):
    crit = stats.f.ppf(1 - alpha, k - 1, n - k)
    return 1 - stats.ncf.cdf(crit, k - 1, n - k, f * f * n)


# ---------------------------------------------------------------- R-01
def test_R01_apriori_outputs():
    r = apriori()
    assert (r.total_n, r.df1, r.df2) == (252, 2, 249)
    assert r.per_group == 84 and r.warnings == ()
    shown = format_result(r)
    assert (shown["total_n"], shown["df1"], shown["df2"]) == ("252", "2", "249")
    assert (shown["ncp"], shown["critical"]) == ("15.7500000", "3.0320649")


def test_R01_posthoc_outputs_v34():
    r = posthoc()
    assert round(r.power, 4) == 0.3744
    assert round(r.critical, 4) == 3.1588
    assert (r.total_n, r.df1, r.df2, r.ncp, r.per_group) == (60, 2, 57, 3.75, 20)


# ---------------------------------------------------------------- R-02
@pytest.mark.parametrize("k,n", [(2, 10), (3, 60), (10, 11), (7, 100)])
def test_R02_degrees_of_freedom(k, n):
    r = posthoc(total_n=n, groups=k)
    assert (r.df1, r.df2) == (k - 1, n - k)


def test_R02_apriori_df_use_rounded_n():
    r = apriori()
    assert r.df2 == r.total_n - 3


# ---------------------------------------------------------------- R-03
@pytest.mark.parametrize("f,alpha,k,n", [(0.25, 0.05, 3, 60), (0.4, 0.01, 4, 48),
                                         (0.1, 0.1, 2, 500), (0.25, 0.05, 10, 390)])
def test_R03_lambda_critical_power(f, alpha, k, n):
    r = posthoc(f, alpha, n, k)
    assert r.ncp == pytest.approx(f * f * n, rel=1e-15)
    assert r.critical == pytest.approx(stats.f.ppf(1 - alpha, k - 1, n - k), rel=1e-12)
    assert r.power == pytest.approx(independent_power(f, alpha, k, n), abs=1e-10)


def test_R03_contract_example_a_priori():
    r = apriori()
    assert round(r.power, 4) == 0.9515 and round(r.critical, 4) == 3.0321


# ---------------------------------------------------------------- R-04
@pytest.mark.parametrize("f,alpha,power,k", [
    (0.25, 0.05, 0.95, 3), (0.25, 0.05, 0.80, 4), (0.1, 0.05, 0.80, 3),
    (0.4, 0.01, 0.90, 5), (0.8, 0.05, 0.80, 3), (0.05, 0.05, 0.95, 2)])
def test_R04_smallest_multiple_reaching_power(f, alpha, power, k):
    r = apriori(f, alpha, power, k)
    assert independent_power(f, alpha, k, r.total_n) >= power - 1e-12
    if r.total_n > 2 * k:
        assert independent_power(f, alpha, k, r.total_n - k) < power


def test_R04_continuous_root_matches_bisection():
    raw = engine._search_total_n(0.25, 0.05, 0.95, 3)
    lo, hi = 4.0, 400.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if engine.power_at(0.25, 0.05, 3, mid) < 0.95:
            lo = mid
        else:
            hi = mid
    assert raw == pytest.approx(lo, rel=1e-9)
    assert not float(raw).is_integer()  # fractional N is searched


def test_R04_no_ceiling_for_small_f():
    r = apriori(f=0.01, power=0.8, groups=3)
    assert r.total_n > 9e4 and r.total_n % 3 == 0


def test_R04_failed_bracket_returns_zero_without_error(monkeypatch):
    monkeypatch.setattr(engine, "power_at", lambda *a: 0.99)  # h > 0 everywhere
    assert engine._search_total_n(0.25, 0.05, 0.5, 3) == 0.0


# ---------------------------------------------------------------- R-05
@pytest.mark.parametrize("k", [2, 3, 4, 5, 7, 10])
def test_R05_total_is_multiple_of_groups(k):
    r = apriori(groups=k)
    assert r.total_n % k == 0 and r.per_group == r.total_n // k


def test_R05_ceil_to_next_multiple_without_epsilon():
    assert engine._round_up_to_groups(252.0, 3) == 252
    assert engine._round_up_to_groups(252.0000001, 3) == 255
    assert engine._round_up_to_groups(250.2, 3) == 252


# ---------------------------------------------------------------- R-06
def test_R06_minimum_total_is_two_k():
    assert apriori(f=50).total_n == 6
    assert apriori(f=50, groups=5).total_n == 10
    assert apriori(f=15, groups=3).total_n == 6


def test_R06_rounding_rule_and_failed_root():
    assert engine._round_up_to_groups(0.0, 4) == 8
    assert engine._round_up_to_groups(2.5, 3) == 6


# ---------------------------------------------------------------- R-07
def test_R07_actual_power_from_rounded_n():
    r = apriori()
    assert r.power >= 0.95
    assert r.power == pytest.approx(independent_power(0.25, 0.05, 3, 252), abs=1e-10)
    assert r.ncp == pytest.approx(0.0625 * 252)
    assert r.critical == pytest.approx(stats.f.ppf(0.95, 2, 249))


# ---------------------------------------------------------------- R-08
def test_R08_apriori_order():
    base = dict(groups=3, f=0.25, alpha=0.05, power=0.95)
    assert "2 groups" in err(**{**base, "groups": 1, "f": 0, "alpha": 0, "power": 2})
    assert "Effect size" in err(**{**base, "f": 0, "alpha": 0, "power": 2})
    assert "Alpha" in err(**{**base, "alpha": 0, "power": 2})
    assert "Power is outside" in err(**{**base, "alpha": 0.5, "power": 0})
    assert "greater than or equal" in err(**{**base, "alpha": 0.5, "power": 0.3})


def test_R08_posthoc_order():
    base = dict(mode=POSTHOC, groups=3, f=0.25, alpha=0.05, total_n=60)
    assert "2 groups" in err(**{**base, "groups": 1, "f": -1, "alpha": 0, "total_n": 1})
    assert "Effect size" in err(**{**base, "f": -1, "alpha": 0, "total_n": 1})
    assert "Alpha" in err(**{**base, "alpha": 0, "total_n": 1})
    assert "Sample size" in err(**{**base, "total_n": 1})


def test_R08_error_has_no_partial_output():
    with pytest.raises(GPowerError):
        apriori(f=0)


# ---------------------------------------------------------------- R-09
@pytest.mark.parametrize("k", [1, 0, -2, 1.4])
def test_R09_fewer_than_two_groups(k):
    assert err(groups=k) == "There must be at least 2 groups."


def test_R09_one_and_a_half_rounds_to_two():
    assert apriori(groups=1.5).df1 == 1


# ---------------------------------------------------------------- R-10
def test_R10_apriori_range_and_message():
    msg = "Effect size f is outside the admissible range (1e-06, 50)."
    for f in (0, -0.1, 50.01, 1e-7):
        assert err(f=f) == msg
    assert apriori(f=50).total_n == 6
    assert apriori(f=1e-6 * 100, power=0.8).total_n > 0


def test_R10_posthoc_range_and_zero_is_valid():
    assert err(mode=POSTHOC, f=-0.1) == "Effect size f is outside the admissible range (0, 50)."
    assert err(mode=POSTHOC, f=50.01).endswith("(0, 50).")
    r = posthoc(f=0)
    assert r.ncp == 0 and r.power == pytest.approx(0.05)
    assert format_fraction(r.ncp) == "0"


# ---------------------------------------------------------------- R-11
@pytest.mark.parametrize("alpha", [0, 1, -0.1, 1e-8, 0.99999991])
def test_R11_alpha_range(alpha):
    assert err(alpha=alpha) == "Alpha is outside the admissible range (1e-07, 1)."


@pytest.mark.parametrize("power", [0, 1, 1e-8, 0.99999991, 2])
def test_R11_power_range(power):
    assert err(power=power) == "Power is outside the admissible range (1e-07, 1)."


def test_R11_bounds_are_inclusive():
    assert apriori(alpha=1e-7, power=0.5).total_n > 0
    assert apriori(alpha=0.5, power=0.9999999).total_n > 0


# ---------------------------------------------------------------- R-12
def test_R12_power_below_alpha():
    assert err(alpha=0.05, power=0.03) == "Power must be greater than or equal to alpha."


def test_R12_power_equal_alpha_gives_two_k():
    assert apriori(alpha=0.05, power=0.05).total_n == 6
    assert apriori(alpha=0.05, power=0.05, groups=4).total_n == 8


# ---------------------------------------------------------------- R-13
def test_R13_n_not_above_k():
    msg = "Sample size must be greater than the number of groups (3)."
    assert err(mode=POSTHOC, total_n=3) == msg
    assert err(mode=POSTHOC, total_n=1) == msg
    assert err(mode=POSTHOC, total_n=-5) == msg


def test_R13_k_plus_one_is_valid():
    r = posthoc(total_n=4)
    assert r.df2 == 1 and 0 < r.power < 1


# ---------------------------------------------------------------- R-14
def test_R14_warning_and_calculation_with_given_n():
    r = posthoc(total_n=61)
    assert r.total_n == 61 and r.df2 == 58 and r.ncp == pytest.approx(0.0625 * 61)
    assert r.per_group == pytest.approx(61 / 3)
    assert len(r.warnings) == 1
    assert "The total sample size (61) is not a multiple of" in r.warnings[0]
    assert "the number of groups (3). The analysis was" in r.warnings[0]
    assert r.warnings[0].endswith("based on the average group size.")


def test_R14_no_warning_when_divisible_or_apriori():
    assert posthoc(total_n=60).warnings == ()
    for k in (2, 3, 7):
        assert apriori(groups=k).warnings == ()


# ---------------------------------------------------------------- R-15
@pytest.mark.parametrize("x,text", [
    (15.75, "15.7500000"), (1.0, "1.0000000"), (0.3743, "0.3743000"),
    (150.0, "150"), (199.5, "199.5"), (15000.0, "15000"), (156.06, "156.06"),
    (0.0, "0"), (0.01, "0.01"), (0.005, "0.005"), (0.0100001, "0.0100001"),
    (99.99999999, "100.0000000"), (100.0, "100"), (123.45678912, "123.4568"),
    (0.0050000001, "0.005"), (1e-9, "1e-09")])
def test_R15_fraction_format(x, text):
    assert format_fraction(x) == text


@pytest.mark.parametrize("x,text", [(252, "252"), (2.5, "3"), (2.4999, "2"),
                                    (1e12, "1e+12"), (123456789012345, "1.2346e+14"),
                                    (999999999999, "999999999999")])
def test_R15_integer_format(x, text):
    assert format_integer(x) == text


def test_R15_boundary_between_modes():
    assert format_fraction(99.9999999) == "99.9999999"
    assert format_fraction(0.0100000001) == "0.0100000"


# ---------------------------------------------------------------- R-16
def test_R16_no_time_limit_small_f_completes():
    r = apriori(f=0.0005, power=0.8)
    assert r.total_n % 3 == 0 and r.total_n > 1e7


@pytest.mark.parametrize("exc", [ArithmeticError, OverflowError])
def test_R16_arithmetic_failure_message(monkeypatch, exc):
    def boom(*a):
        raise exc("boom")
    monkeypatch.setattr(engine, "power_at", boom)
    assert err() == ("G*Power was not able to compute the results. "
                     "Please try less extreme input parameters!")


def test_R16_nan_power_message(monkeypatch):
    monkeypatch.setattr(engine, "power_at", lambda *a: float("nan"))
    assert "not able to compute" in err()


# ---------------------------------------------------------------- R-17
def test_R17_fractional_groups_round_half_up():
    assert apriori(groups=2.5) == apriori(groups=3)
    assert apriori(groups=2.4) == apriori(groups=2)
    assert apriori(groups=2.5).warnings == ()


def test_R17_fractional_posthoc_n():
    assert posthoc(total_n=60.5) == posthoc(total_n=61)
    assert posthoc(total_n=60.4) == posthoc(total_n=60)
    assert err(mode=POSTHOC, groups=3.4, total_n=2.5) == (
        "Sample size must be greater than the number of groups (3).")


@pytest.mark.parametrize("bad", ["abc", "", None, "nan", "inf", True, "1,5"])
def test_R17_unparsable_input(bad):
    assert err(f=bad) == "Input error (illegal character?)"
    assert err(groups=bad) == "Input error (illegal character?)"


# ---------------------------------------------------------------- R-18
def test_R18_tiny_f_completes_with_correct_power():
    r = apriori(f=0.0001, power=0.80)
    assert r.total_n % 3 == 0
    # exact calculation (not G*Power's noisy value): reaches the target to ~1e-7
    assert r.power >= 0.8 - 1e-6


# ================================================================ Gherkin
def test_G01_cohen_medium_three_arms():
    r = apriori()
    assert r.total_n == 252
    shown = format_result(r)
    assert (shown["ncp"], shown["critical"], shown["df2"]) == ("15.7500000", "3.0320649", "249")
    assert_vector("V05")


def test_G02_manual_example_ten_groups():
    r = apriori(groups=10)
    assert r.total_n % 10 == 0 and r.df1 == 9
    assert_vector("V14")


def test_G03_n_rounds_up_to_group_multiple():
    for k, vid in ((3, "V15"), (4, "V16"), (5, "V17")):
        r = apriori(f=0.2, groups=k, power=0.9)
        assert r.total_n % k == 0 and r.per_group == r.total_n / k
        assert_vector(vid)


def test_G04_two_groups_equals_t_test():
    r = apriori(groups=2)
    assert r.total_n == 210 and r.per_group == 105
    assert_vector("V11")


def test_G05_huge_effect_gives_minimum_n():
    for f, vid in ((50, "V47"), (5, "V23"), (5.1, "V48")):
        assert apriori(f=f, groups=3).total_n == 6
        assert_vector(vid)


def test_G06_power_equal_alpha_is_not_an_error():
    assert apriori(alpha=0.05, power=0.05).total_n == 6
    assert_vector("V24")


def test_G07_power_below_alpha_is_an_error():
    assert err(power=0.03, alpha=0.05) == "Power must be greater than or equal to alpha."
    assert_vector("V25")


def test_G08_f_limits():
    assert err(f=0) == "Effect size f is outside the admissible range (1e-06, 50)."
    assert apriori(f=50).total_n == 6
    err(f=50.01)
    assert err(mode=POSTHOC, f=-0.1) == "Effect size f is outside the admissible range (0, 50)."
    r = posthoc(f=0, total_n=60, groups=3)
    assert r.power == pytest.approx(0.05)
    for vid in ("V47", "V49", "V43"):
        assert_vector(vid)


def test_G09_alpha_and_power_limits():
    for a in (0, 1):
        assert err(alpha=a) == "Alpha is outside the admissible range (1e-07, 1)."
    assert err(power=1) == "Power is outside the admissible range (1e-07, 1)."
    for vid in ("V30", "V31", "V32"):
        assert_vector(vid)


def test_G10_fractional_groups_round_half_up():
    assert apriori(groups=2.5) == apriori(groups=3)
    assert apriori(groups=2.4) == apriori(groups=2)
    assert apriori(groups=2.5).warnings == ()
    assert_vector("V45")
    assert_vector("V46")


def test_G11_hundred_and_above_use_seven_significant_digits():
    assert format_fraction(150.0) == "150" and format_fraction(199.5) == "199.5"
    assert format_fraction(apriori(f=15).ncp) == "1350"
    for vid in ("V23", "V39", "V47", "V48"):
        assert_vector(vid)


def test_G12_posthoc_n_not_divisible_warns():
    r = posthoc(total_n=61)
    assert r.df2 == 58 and r.ncp == pytest.approx(0.0625 * 61)
    assert any("not a multiple of" in w for w in r.warnings)
    assert_vector("V38")


def test_G13_posthoc_n_equals_k_is_error_k_plus_one_is_not():
    assert err(mode=POSTHOC, total_n=3).startswith("Sample size must be greater than")
    assert posthoc(total_n=4, groups=3).df2 == 1
    assert_vector("V40")
    assert_vector("V39")


def test_G14_single_group_error():
    assert err(groups=1) == "There must be at least 2 groups."
    assert_vector("V33")


def test_G15_validation_order():
    assert err(groups=1, f=0) == "There must be at least 2 groups."


def test_G16_tiny_f_known_numerical_deviation():
    r = apriori(f=0.0001, alpha=0.05, power=0.80, groups=3)
    assert r.total_n % 3 == 0
    # The V52 mismatch with G*Power is reported as xfail in test_oracle_gui.py.
