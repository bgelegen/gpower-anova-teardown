"""R-18 kanıtı: G*Power'ın uç küçük f'deki N'i mi, motorun N'i mi doğru?

Motordan bağımsız, 40 basamaklı bir güç hesabıyla (mpmath) motorun a priori N'inin
hedef güce ulaşan EN KÜÇÜK k katı olduğu doğrulanır. df1 = 2 (k = 3) için merkezi
F'nin kritik değeri kapalı biçimdedir: P(Y > y) = (1 - y)^(df2/2) = α; merkezi olmayan
F, Poisson ağırlıklı tamamlanmamış beta toplamıdır.

Aynı hesap, G*Power'ın V52, V54 ve V55'te gösterdiği N'lerin minimum olmadığını da
gösterir (bkz. oracle/R18_YUKSEK_HASSASIYET.md).
"""
import pytest

mp = pytest.importorskip("mpmath")

from gpower_clone.engine import calculate

mp.mp.dps = 40


def power_hp(f, alpha, n, k=3):
    f, alpha, n = mp.mpf(f), mp.mpf(alpha), mp.mpf(n)
    b = (n - k) / 2
    lam = f * f * n
    y = 1 - alpha ** (1 / b)
    cdf, j = mp.mpf(0), 0
    while True:
        w = mp.e ** (-lam / 2) * (lam / 2) ** j / mp.factorial(j)
        cdf += w * mp.betainc(1 + j, b, 0, y, regularized=True)
        if j > lam and w < mp.mpf(10) ** -35:
            break
        j += 1
    return 1 - cdf


# (oracle id, f, G*Power'ın gösterdiği N)
CASES = [("V51", 0.001, 9634692), ("V52", 0.0001, 963468906),
         ("V53", 0.0005, 38538759), ("V54", 0.0002, 240867222)]


@pytest.mark.parametrize("vid,f,gp_n", CASES, ids=[c[0] for c in CASES])
def test_R18_engine_n_is_minimal_multiple(vid, f, gp_n):
    n = calculate(mode="a-priori", f=f, alpha=0.05, power=0.80, groups=3).total_n
    assert n % 3 == 0
    assert power_hp(f, 0.05, n) >= mp.mpf("0.80"), f"{vid}: N={n} hedefe ulaşmıyor"
    assert power_hp(f, 0.05, n - 3) < mp.mpf("0.80"), f"{vid}: N-3 de yetiyor, N minimum değil"


def test_R18_gpower_n_not_minimal_v52_v54():
    # V52: G*Power 15 fazla; V54: G*Power'ın N'i hedefin ALTINDA kalıyor.
    assert power_hp(0.0001, 0.05, 963468906 - 15) >= mp.mpf("0.80")
    assert power_hp(0.0002, 0.05, 240867222) < mp.mpf("0.80")
