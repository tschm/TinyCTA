"""test portfolio"""
import numpy as np
import pytest
import quantstats as qs

from tinycta.port import build_portfolio

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
    # construct a fake-price, those fake-prices have homescedastic returns
    price_adj = filter(prices, volatility=vola, clip=clip)
    # compute mu
    mu = np.tanh(osc(price_adj, fast=fast, slow=slow))
    return mu/prices.pct_change().ewm(com=slow, min_periods=100).std()


def test_portfolio(prices):
    portfolio = build_portfolio(prices=prices, cashposition=1e6*f(prices))
    assert qs.stats.sharpe(portfolio.profit) == pytest.approx(0.8626112376600886)