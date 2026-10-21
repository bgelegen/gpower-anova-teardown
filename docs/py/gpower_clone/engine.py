"""Pure computation for the one-way ANOVA F test (SPEC.md R-01 .. R-18).

No I/O. Raises :class:`GPowerError` with the SPEC message text on invalid input
and returns warnings together with the full-precision result.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable

from scipy import optimize, stats

from .contract import APRIORI, POSTHOC

F_MIN_APRIORI = 1e-6
F_MIN_POSTHOC = 0.0
F_MAX = 50.0
ALPHA_MIN = 1e-7
ALPHA_MAX = 0.9999999
POWER_MIN = 1e-7
POWER_MAX = 0.9999999
BRENT_MAX_ITER = 300

MSG_ILLEGAL = "Input error (illegal character?)"
MSG_GROUPS = "There must be at least 2 groups."
MSG_ALPHA_POWER = "Power must be greater than or equal to alpha."
MSG_NUMERIC = ("G*Power was not able to compute the results. "
               "Please try less extreme input parameters!")


class GPowerError(ValueError):
    """Invalid input or numerical failure; ``str(exc)`` is the SPEC message."""


@dataclass(frozen=True)
class Result:
    mode: str
    per_group: float
    total_n: int
    power: float
    critical: float
    df1: int
    df2: int
    ncp: float
    warnings: tuple = ()


def _number(value: Any) -> float:
    if value is None or isinstance(value, bool):
        raise GPowerError(MSG_ILLEGAL)
    try:
        x = float(value)
    except (TypeError, ValueError):
        raise GPowerError(MSG_ILLEGAL) from None
    if not math.isfinite(x):
        raise GPowerError(MSG_ILLEGAL)
    return x


def _round_half_up(x: float) -> int:
    return math.floor(x + 0.5)


def _range_msg(label: str, lo: float, hi: float) -> str:
    return f"{label} is outside the admissible range ({lo:g}, {hi:g})."


def critical_f(alpha: float, df1: float, df2: float) -> float:
    return float(stats.f.isf(alpha, df1, df2))


def power_at(f: float, alpha: float, k: int, n: float) -> float:
    """R-03 power for (possibly fractional) total sample size ``n``."""
    df1, df2 = k - 1, n - k
    crit = critical_f(alpha, df1, df2)
    lam = f * f * n
    if lam == 0:
        return float(stats.f.sf(crit, df1, df2))
    return float(stats.ncf.sf(crit, df1, df2, lam))


def _search_total_n(f: float, alpha: float, target: float, k: int) -> float:
    """R-04: continuous root of power(N) - target; 0 if no bracket is found."""
    def h(n: float) -> float:
        v = power_at(f, alpha, k, n) - target
        if math.isnan(v):
            raise GPowerError(MSG_NUMERIC)
        return v

    lo, hi = k + 1.0, k + 100.0
    if h(hi) < 0:
        lower, upper = hi, 1.6 * hi
        while h(upper) < 0:
            lower, upper = upper, 1.6 * upper
            if math.isinf(upper):
                raise GPowerError(MSG_NUMERIC)
    else:
        upper, m = hi, (lo + hi) / 2
        while m >= lo and h(m) > 0:
            upper = m
            m = (m + lo) / 2 - lo
        lower = m
    if lower < lo:
        lower = lo
    h_lo, h_up = h(lower), h(upper)
    if h_lo == 0:
        return lower
    if h_up == 0:
        return upper
    if (h_lo < 0) == (h_up < 0):
        return 0.0
    root = optimize.brentq(h, lower, upper, xtol=1e-300, rtol=4 * 2.0 ** -52,
                           maxiter=BRENT_MAX_ITER, disp=False)
    return float(root)


def _round_up_to_groups(n_raw: float, k: int) -> int:
    """R-05 / R-06: next multiple of k, never below 2k."""
    n = math.ceil(n_raw / k) * k
    if n < k + 1:
        n = math.ceil((k + 1) / k) * k
    return n


def _validate_common(mode: str, f: Any, alpha: Any, groups: Any) -> tuple:
    k = _round_half_up(_number(groups))  # R-17
    if k < 2:
        raise GPowerError(MSG_GROUPS)
    f_lo = F_MIN_APRIORI if mode == APRIORI else F_MIN_POSTHOC
    fv = _number(f)
    if not f_lo <= fv <= F_MAX:
        raise GPowerError(_range_msg("Effect size f", f_lo, F_MAX))
    a = _number(alpha)
    if not ALPHA_MIN <= a <= ALPHA_MAX:
        raise GPowerError(_range_msg("Alpha", ALPHA_MIN, ALPHA_MAX))
    return k, fv, a


def _outcome(mode: str, f: float, alpha: float, k: int, n: int,
             warnings: tuple = ()) -> Result:
    try:
        crit = critical_f(alpha, k - 1, n - k)
        pw = power_at(f, alpha, k, n)
    except ArithmeticError:
        raise GPowerError(MSG_NUMERIC) from None
    if math.isnan(pw) or math.isnan(crit):
        raise GPowerError(MSG_NUMERIC)
    return Result(mode=mode, per_group=n / k, total_n=n, power=pw,
                  critical=crit, df1=k - 1, df2=n - k, ncp=f * f * n,
                  warnings=warnings)


def calculate(mode: str, f: Any, alpha: Any, groups: Any,
              power: Any = None, total_n: Any = None) -> Result:
    """Validate (R-08 order) and compute. ``mode`` is a canonical mode name."""
    if mode == APRIORI:
        k, fv, a = _validate_common(mode, f, alpha, groups)
        target = _number(power)
        if not POWER_MIN <= target <= POWER_MAX:
            raise GPowerError(_range_msg("Power", POWER_MIN, POWER_MAX))
        if a > target:
            raise GPowerError(MSG_ALPHA_POWER)
        try:
            n_raw = _search_total_n(fv, a, target, k)
        except ArithmeticError:
            raise GPowerError(MSG_NUMERIC) from None
        return _outcome(mode, fv, a, k, _round_up_to_groups(n_raw, k))
    if mode == POSTHOC:
        k, fv, a = _validate_common(mode, f, alpha, groups)
        n = _round_half_up(_number(total_n))  # R-17
        if n <= k:
            raise GPowerError("Sample size must be greater than "
                              f"the number of groups ({k}).")
        warnings = ()
        if n % k:
            warnings = (f"The total sample size ({n}) is not a multiple of "
                        f"the number of groups ({k}). The analysis was "
                        "based on the average group size.",)
        return _outcome(mode, fv, a, k, n, warnings)
    raise GPowerError(f"Unknown mode: {mode}")
