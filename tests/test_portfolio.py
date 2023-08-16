"""test portfolio"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from tinycta.port import build_portfolio, Aggregate


@pytest.fixture()
def portfolio(prices, position):
    return build_portfolio(prices=prices, cashposition=position, aum=1e7)


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


def test_monthly(portfolio):
    assert portfolio.monthly(Aggregate.COMPOUND)["YTD"][2022] == pytest.approx(
        55.004591
    )
    assert portfolio.monthly(Aggregate.CUMULATIVE)["YTD"][2022] == pytest.approx(
        52.861904028489384
    )


def test_start(portfolio):
    assert portfolio.start == pd.Timestamp("1970-05-25")


def test_get(portfolio):
    with pytest.raises(AssertionError):
        portfolio[pd.Timestamp("2082-05-25")]

    pd.testing.assert_series_equal(
        portfolio[pd.Timestamp("1970-05-25")],
        portfolio.cashposition.loc[pd.Timestamp("1970-05-25")],
    )


def test_truncate(portfolio):
    reduced = portfolio.truncate(before=pd.Timestamp("2000-01-01"))
    assert reduced.start == pd.Timestamp("2000-01-04")


def test_nav(portfolio):
    assert portfolio.nav_accum[-1] == pytest.approx(96213100.91697493)
    assert portfolio.nav_compound[-1] == pytest.approx(6057029955.177139)


def test_set(portfolio):
    with pytest.raises(AssertionError):
        portfolio[pd.Timestamp("2082-05-25")] = pd.Series(
            index=portfolio.assets, data=1.0
        )

    with pytest.raises(AssertionError):
        portfolio[portfolio.start] = 2.0

    with pytest.raises(AssertionError):
        portfolio[portfolio.start] = pd.Series(index=["A"], data=2.0)


def test_iter(portfolio):
    for t, s in portfolio:
        assert t < s


def test_build():
    with pytest.raises(AssertionError):
        build_portfolio(prices=np.random.rand(100, 10))

    with pytest.raises(AssertionError):
        build_portfolio(
            prices=pd.DataFrame(index=[1, 2], columns=["A", "B"], data=2.0),
            cashposition=pd.DataFrame(index=[2, 1], columns=["A", "B"], data=2.0),
        )

    with pytest.raises(AssertionError):
        build_portfolio(
            prices=pd.DataFrame(index=[1, 2], columns=["A", "B"], data=2.0),
            cashposition=pd.DataFrame(index=[1, 2], columns=["A", "B", "C"], data=2.0),
        )

    with pytest.raises(AssertionError):
        build_portfolio(
            prices=pd.DataFrame(index=[1, 2], columns=["A", "B"], data=2.0),
            cashposition=pd.DataFrame(index=[1, 2, 3], columns=["A", "B"], data=2.0),
        )


def test_metrics(portfolio):
    print(portfolio.metrics())

    target = pd.Series(
        {
            "Sharpe": 0.5511187319241556,
            "Kurtosis": 30.54402394742987,
            "Skewness": 0.4912251491984351,
            "Annualized Volatility (%)": 28.34214576383152,
            "Annualized Return (%)": 15.619887433372406,
        }
    )

    pd.testing.assert_series_equal(pd.Series(portfolio.metrics()), target)


def test_plot(portfolio):
    fig = portfolio.plot()
    fig.show()
    assert fig
