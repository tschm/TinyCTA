"""test portfolio"""
import numpy as np
import pytest
import quantstats as qs

from tinycta.port import build_portfolio
from tinycta.month import monthlytable

# take two moving averages and apply sign-function
def f(prices, fast=32, slow=96):
    """
    construct cash position
    """
    s = prices.ewm(com=slow, min_periods=100).mean()
    f = prices.ewm(com=fast, min_periods=100).mean()
    return np.sign(f - s)


def test_portfolio(prices):
    """
    test portfolio

    Args:
        prices: adjusted prices of futures
    """
    portfolio = build_portfolio(prices=prices, cashposition=1e6 * f(prices))

    assert qs.stats.sharpe(portfolio.profit) == pytest.approx(0.5527420886866333)
    assert qs.stats.sharpe(
        portfolio.truncate(before=portfolio.start).profit
    ) == pytest.approx(0.5548581162109552)


def test_month(prices):
    """test the month table"""
    portfolio = build_portfolio(prices=prices, cashposition=1e6 * f(prices))
    returns = portfolio.profit / portfolio.profit.std()

    table = 100*monthlytable(portfolio.nav(aum=1e6).pct_change())
    assert table["YTD"].loc[1973] == pytest.approx(231.72540665897102)

