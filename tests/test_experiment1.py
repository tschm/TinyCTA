"""test portfolio"""
import numpy as np
import pytest
import quantstats as qs

from tinycta.port import build_portfolio


# take two moving averages and apply sign-functiond
def f(prices, fast=32, slow=96):
    s = prices.ewm(com=slow, min_periods=100).mean()
    f = prices.ewm(com=fast, min_periods=100).mean()
    return np.sign(f - s)


def test_portfolio(prices):
    portfolio = build_portfolio(prices=prices, cashposition=1e6 * f(prices))

    assert qs.stats.sharpe(portfolio.profit) == pytest.approx(0.5527420886866333)
    assert qs.stats.sharpe(
        portfolio.truncate(before=portfolio.start).profit
    ) == pytest.approx(0.5548581162109552)
