"""test portfolio"""
import numpy as np
import pytest
import quantstats as qs

from tinycta.port import build_portfolio
from tinycta.signal import returns_adjust


def filter(price, volatility=32,clip=4.2, min_periods=100):
    r = np.log(price).diff()
    vola = r.ewm(com=volatility, min_periods=min_periods).std()
    price_adj = (r/vola).clip(-clip, clip).cumsum()
    return price_adj


def osc(prices, fast=32, slow=96, scaling=True):
    diff = prices.ewm(com=fast-1).mean() - prices.ewm(com=slow-1).mean()
    if scaling:
        s = diff.std()
    else:
        s = 1
    return diff/s


# take two moving averages and apply the sign-function, adjust by volatility
def f(prices, slow=96, fast=32, vola=96, clip=3):
    mu = np.tanh(prices.apply(returns_adjust, com=vola, clip=clip).cumsum().apply(osc, fast=fast, slow=slow))
    volatility = prices.pct_change().ewm(com=vola, min_periods=vola).std()

    # compute the series of Euclidean norms by compute the sum of squares for each row
    euclid_norm = np.sqrt((mu * mu).sum(axis=1))

    # Divide each column of mu by the Euclidean norm
    risk_scaled = mu.apply(lambda x: x / euclid_norm, axis=0)

    return risk_scaled / volatility


def test_portfolio(prices):
    portfolio = build_portfolio(prices=prices, cashposition=1e6*f(prices))
    assert qs.stats.sharpe(portfolio.profit) == pytest.approx(1.0165734639278787)
