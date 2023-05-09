"""test portfolio"""
import pandas as pd
import pytest


from tinycta.port import build_portfolio


def test_portfolio(prices):
    """
    build portfolio from price
    """
    portfolio = build_portfolio(prices=prices)
    pd.testing.assert_frame_equal(portfolio.prices, prices.ffill())

    for t in portfolio.index:
        # set the cash cashposition
        portfolio[t] = pd.Series(index=prices.keys(), data=1000.0)

    pd.testing.assert_frame_equal(
        portfolio.cashposition,
        pd.DataFrame(index=prices.index, columns=prices.keys(), data=1000.0),
    )



def test_duplicates():
    """
    duplicate in index
    """
    prices = pd.DataFrame(index=[1, 1], columns=["A"])
    with pytest.raises(AssertionError):
        build_portfolio(prices=prices)

    prices = pd.DataFrame(index=[1], columns=["A"])
    position = pd.DataFrame(index=[1, 1], columns=["A"])

    with pytest.raises(AssertionError):
        build_portfolio(prices=prices, cashposition=position)


def test_monotonic():
    """
    index not increasing
    """
    prices = pd.DataFrame(index=[2, 1], columns=["A"])
    with pytest.raises(AssertionError):
        build_portfolio(prices=prices)
