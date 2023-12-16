from __future__ import annotations

import pandas as pd
import pytest

from cvx.simulator import FuturesBuilder
from cvx.simulator._abc.interpolation import interpolate


@pytest.fixture()
def prices_interpolated(prices):
    return prices.apply(interpolate)


@pytest.fixture()
def portfolio(prices_interpolated, position):
    builder = FuturesBuilder(prices=prices_interpolated, aum=1e7)

    for t, state in builder:
        pos = position[state.assets].loc[t[-1]].fillna(0.0)
        builder.cashposition = pos

    portfolio = builder.build()
    return portfolio


def test_prices(prices, portfolio):
    pd.testing.assert_frame_equal(portfolio.prices, prices)


def test_nav(portfolio):
    assert portfolio.nav[-1] == pytest.approx(96213100.91697493)


def test_metrics(portfolio):
    assert portfolio.profit.kurtosis() == pytest.approx(30.54402394742987)
    assert portfolio.profit.sharpe() == pytest.approx(0.5511187319241556)


# todo: move interpolation to utils in cvxSimulator
# todo: move month to utils in cvxSimulator
# todo: remove types