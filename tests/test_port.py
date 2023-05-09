"""test portfolio"""
import pandas as pd

from tinycta.port import build_portfolio


def test_portfolio(prices):
    portfolio = build_portfolio(prices=prices)
    for before, now in portfolio:
        print(before, now)
        portfolio[now] = pd.Series({"A": -3000000, "B": 4000000})

    print(portfolio.profit.cumsum() + portfolio.aum)