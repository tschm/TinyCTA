"""test portfolio"""
import numpy as np
import pytest
import quantstats as qs

from tinycta.port import build_portfolio
from tinycta.signal import returns_adjust, osc


# take two moving averages and apply the sign-function, adjust by volatility
def f(prices, slow=96, fast=32, vola=96, clip=3):
    # construct a fake-price, those fake-prices have homescedastic returns
    price_adj = returns_adjust(prices, com=vola, min_periods=100, clip=clip).cumsum()
    # compute mu
    mu = np.tanh(osc(price_adj, fast=fast, slow=slow))
    return mu/prices.pct_change().ewm(com=slow, min_periods=100).std()


def test_portfolio(prices):
    portfolio = build_portfolio(prices=prices, cashposition=1e6*f(prices))
    assert qs.stats.sharpe(portfolio.profit) == pytest.approx(0.8626112376600886)