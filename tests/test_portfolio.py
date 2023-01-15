import pandas as pd
import pytest
import quantstats as qs

from tinycta.portfolio import build_portfolio


def test_portfolio(prices):
    portfolio = build_portfolio(prices=prices)
    pd.testing.assert_frame_equal(portfolio.prices, prices)

    for t in portfolio.index:
        # set the cash position
        portfolio[t] = pd.Series(index=prices.keys(), data=1000.0)

    pd.testing.assert_frame_equal(
        portfolio.position,
        pd.DataFrame(index=prices.index, columns=prices.keys(), data=1000.0),
    )

    returns = portfolio.returns(init_capital=10000)
    assert qs.stats.sharpe(returns) == pytest.approx(0.3012828629001599)

    nav = portfolio.nav(init_capital=10000)
    returns = nav.pct_change().fillna(0.0)
    assert qs.stats.sharpe(returns) == pytest.approx(0.3012828629001599)

def test_keys():
    prices = pd.DataFrame(index=[1], columns=["A","B"])
    positions = pd.DataFrame(index=[1], columns=["A"])
    with pytest.raises(AssertionError):
        build_portfolio(prices=prices, position=positions)


def test_index():
    prices = pd.DataFrame(index=[1], columns=["A"])
    positions = pd.DataFrame(index=[2], columns=["A"])
    with pytest.raises(AssertionError):
        build_portfolio(prices=prices, position=positions)


def test_duplicates():
    prices = pd.DataFrame(index=[1,1], columns=["A"])
    with pytest.raises(AssertionError):
        build_portfolio(prices=prices)

    prices = pd.DataFrame(index=[1], columns=["A"])
    position = pd.DataFrame(index=[1,1], columns=["A"])

    with pytest.raises(AssertionError):
        build_portfolio(prices=prices, position=position)

def test_monotonic():
    prices = pd.DataFrame(index=[2,1], columns=["A"])
    with pytest.raises(AssertionError):
        build_portfolio(prices=prices)