"""Özellik tabanlı (metamorfik) testler — Hypothesis.

Oracle vektörleri tek tek noktaları sınar; bu testler ise binlerce rastgele girdide
**her girdide doğru olması gereken** ilişkileri sınar (Sommerville 8.1.2: bölüm testi
ve sınır değerlerinin tamamlayıcısı). Beklenen değer burada bir sayı değil, bir
ilişkidir; bu yüzden G*Power'a gerek duymadan gizli kural ihlallerini yakalar.

Aralık: f ∈ [0,05; 1,5] — R-18'in (df2 ≳ 2·10⁸) çok dışında, yani G*Power ile motorun
birebir aynı olduğu bölge.
"""
import math
import os

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st
from scipy import stats

from gpower_clone.cli import evaluate
from gpower_clone.engine import calculate, power_at

# Varsayılan 120 örnek/test (hızlı); derin koşu: PROPS_EXAMPLES=2000 pytest tests/test_properties.py
hyp = settings(max_examples=int(os.environ.get("PROPS_EXAMPLES", "120")), deadline=None,
               suppress_health_check=[HealthCheck.too_slow])

f_st = st.floats(min_value=0.05, max_value=1.5, allow_nan=False)
alpha_st = st.sampled_from([0.001, 0.01, 0.025, 0.05, 0.1])
power_st = st.floats(min_value=0.5, max_value=0.99, allow_nan=False)
k_st = st.integers(min_value=2, max_value=10)


def apriori(f, a, p, k):
    return calculate(mode="a-priori", f=f, alpha=a, power=p, groups=k)


def posthoc(f, a, n, k):
    return calculate(mode="post-hoc", f=f, alpha=a, total_n=n, groups=k)


@hyp
@given(f_st, alpha_st, power_st, k_st)
def test_P1_n_is_multiple_of_k_and_at_least_2k(f, a, p, k):
    """R-05/R-06: N her zaman k'nın katı ve ≥ 2k; grup başı n tam sayı."""
    assume(a <= p)
    r = apriori(f, a, p, k)
    assert r.total_n % k == 0 and r.total_n >= 2 * k
    assert r.per_group == r.total_n // k
    assert (r.df1, r.df2) == (k - 1, r.total_n - k)


@hyp
@given(f_st, alpha_st, power_st, k_st)
def test_P2_n_is_the_smallest_sufficient_multiple(f, a, p, k):
    """R-04/R-05/R-07: gerçekleşen güç ≥ hedef ve bir önceki k katı hedefe yetmez."""
    assume(a < p)
    r = apriori(f, a, p, k)
    assert r.power >= p
    prev = r.total_n - k
    if prev >= k + 1:  # 2k alt sınırına (R-06) inilmediyse
        assert power_at(f, a, k, prev) < p


@hyp
@given(f_st, f_st, alpha_st, power_st, k_st)
def test_P3_larger_effect_never_needs_more_patients(f1, f2, a, p, k):
    """Metamorfik: f büyürse N artmaz."""
    assume(a < p and abs(f1 - f2) > 1e-6)
    lo, hi = sorted((f1, f2))
    assert apriori(hi, a, p, k).total_n <= apriori(lo, a, p, k).total_n


@hyp
@given(f_st, alpha_st, power_st, power_st, k_st)
def test_P4_higher_power_never_needs_fewer_patients(f, a, p1, p2, k):
    """Metamorfik: hedef güç artarsa N azalmaz."""
    lo, hi = sorted((p1, p2))
    assume(a < lo)
    assert apriori(f, a, hi, k).total_n >= apriori(f, a, lo, k).total_n


@hyp
@given(f_st, alpha_st, k_st, st.integers(min_value=1, max_value=200))
def test_P5_posthoc_power_increases_with_n(f, a, k, m):
    """Metamorfik: post hoc güç N ile (k'nın katlarında) artar ya da 1'de kalır."""
    n1, n2 = k * (m + 1), k * (m + 2)
    p1, p2 = posthoc(f, a, n1, k).power, posthoc(f, a, n2, k).power
    assert p2 >= p1 - 1e-12


@hyp
@given(f_st, alpha_st, power_st, k_st)
def test_P6_apriori_posthoc_round_trip(f, a, p, k):
    """Gidiş-dönüş: a priori N ile post hoc güç = a priori'nin gerçekleşen gücü."""
    assume(a < p)
    r = apriori(f, a, p, k)
    back = posthoc(f, a, r.total_n, k)
    assert back.warnings == ()  # N k'nın katı → uyarı yok (R-14)
    assert math.isclose(back.power, r.power, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(back.critical, r.critical, rel_tol=0, abs_tol=1e-12)


@hyp
@given(f_st, alpha_st, st.integers(min_value=2, max_value=400))
def test_P7_two_groups_equal_two_sided_t_test(f, a, m):
    """Aileler arası metamorfik ilişki: k = 2'de F testi, d = 2f olan iki yönlü
    bağımsız t testine denktir. Güç, motordan tamamen bağımsız bir formülle
    (merkezi olmayan t) hesaplanır."""
    n = 2 * m
    df = n - 2
    delta = 2 * f * math.sqrt(n / 4)          # d·sqrt(n1·n2/(n1+n2)), n1 = n2 = m
    tcrit = stats.t.isf(a / 2, df)
    # P(T < -c | δ) = P(T > c | -δ); bu kuyruk 1e-30 mertebesinde olabilir ve scipy'nin
    # nct'si orada NaN döndürür (motorun ncf'si döndürmez) → ihmal edilebilir kütle = 0.
    lower = stats.nct.sf(tcrit, df, -delta)
    t_power = stats.nct.sf(tcrit, df, delta) + (0.0 if math.isnan(lower) else lower)
    assume(not math.isnan(t_power))
    assert math.isclose(posthoc(f, a, n, 2).power, t_power, abs_tol=1e-9)


@hyp
@given(f_st, alpha_st, power_st, k_st)
def test_P8_cli_json_equals_engine(f, a, p, k):
    """Adaptör ince: CLI JSON'undaki tam sayı alanları motorla aynı, ondalıklar
    motorun 4 haneye yuvarlanmış hâli."""
    assume(a <= p)
    payload, warnings, code = evaluate({"mode": "a-priori", "f": f, "alpha": a,
                                        "power": p, "groups": k})
    r = apriori(f, a, p, k)
    assert code == 0 and not warnings
    assert (payload["n_total"], payload["df1"], payload["df2"]) == (r.total_n, r.df1, r.df2)
    assert payload["actual_power"] == pytest.approx(round(r.power, 4), abs=1e-12)
    assert payload["critical"] == pytest.approx(round(r.critical, 4), abs=1e-12)
