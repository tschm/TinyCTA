import pandas as pd
import pytest

from pycta.portfolio import Portfolio

import quantstats as qs


def test_portfolio(prices):
    portfolio = Portfolio(prices=prices)
    pd.testing.assert_frame_equal(portfolio.prices, prices)

    for t in portfolio.index:
        # set the cash position
        portfolio[t] = pd.Series(index=prices.keys(), data=1000.0)

    pd.testing.assert_frame_equal(portfolio.position, pd.DataFrame(index=prices.index, columns=prices.keys(), data=1000.0))

    returns = portfolio.returns(init_capital=10000)
    assert qs.stats.sharpe(returns) == pytest.approx(0.3012828629001599)
