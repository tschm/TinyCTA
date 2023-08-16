"""Portfolio"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from plotly.subplots import make_subplots
import plotly.graph_objects as go

from tinycta.month import monthlytable, Aggregate

pd.options.plotting.backend = "plotly"


def build_portfolio(prices, cashposition=None, aum=1e6):
    """
    Build portfolio using prices and cash positions

    Args:
        prices: frame of prices
        cashposition: None or frame of cashpositions

    Returns:
        _FuturesPortfolio object
    """
    if not isinstance(prices, pd.DataFrame):
        raise AssertionError
    if not prices.index.is_monotonic_increasing:
        raise AssertionError
    if not prices.index.is_unique:
        raise AssertionError

    if cashposition is None:
        cashposition = pd.DataFrame(
            index=prices.index, columns=prices.columns, dtype=float
        )
    else:
        if not cashposition.index.is_monotonic_increasing:
            raise AssertionError
        if not cashposition.index.is_unique:
            raise AssertionError

    if not set(cashposition.index).issubset(set(prices.index)):
        raise AssertionError
    if not set(cashposition.columns).issubset(set(prices.columns)):
        raise AssertionError

    prices = prices[cashposition.columns].loc[cashposition.index]

    return _FuturesPortfolio(cashposition=cashposition, prices=prices.ffill(), aum=aum)


@dataclass(frozen=True)
class _FuturesPortfolio:
    """Portfolio"""

    prices: pd.DataFrame
    cashposition: pd.DataFrame
    aum: float = 1e6

    @property
    def index(self):
        """
        Index of the portfolio (e.g. index of the prices)
        """
        return self.prices.index

    @property
    def assets(self):
        """
        Columns of the prices
        """
        return self.prices.columns

    def __iter__(self):
        """Iterate over indizes in portfolio"""
        yield from zip(self.index[:-1], self.index[1:])

    def __setitem__(self, t, cashposition):
        """set cashposition at time t"""
        if t not in self.index:
            raise AssertionError

        if not isinstance(cashposition, pd.Series):
            raise AssertionError
        if not set(cashposition.index).issubset(set(self.assets)):
            raise AssertionError

        self.cashposition.loc[t, cashposition.index] = cashposition

    def __getitem__(self, item):
        """get cashposition at time t"""
        if item not in self.index:
            raise AssertionError
        return self.cashposition.loc[item]

    @property
    def nav_accum(self) -> pd.Series:
        """
        NAV, e.g. cumsum of daily profits and aum
        """
        return self.profit.cumsum() + self.aum

    @property
    def nav_compound(self) -> pd.Series:
        """
        NAV, e.g. cumprod of the returns
        """
        return self.aum * (1 + self.returns).cumprod()

    @property
    def returns(self) -> pd.Series:
        return self.profit / self.aum

    @property
    def profit(self):
        """
        Daily profits, has to be cashposition yesterday times
                                 return in % between (yesterday, today)
        """
        price_changes = self.prices.ffill().pct_change()
        previous_position = self.cashposition.shift(1)
        return (previous_position * price_changes).sum(axis=1)

    @property
    def start(self):
        """first index with a profit that is not zero"""
        return self.profit.ne(0).idxmax()

    def truncate(self, before=None, after=None):
        """truncate the portfolio"""
        return _FuturesPortfolio(
            prices=self.prices.truncate(before=before, after=after),
            cashposition=self.cashposition.truncate(before=before, after=after),
            aum=self.aum,
        )

    def monthly(self, f: Aggregate = Aggregate.CUMULATIVE):
        """monthly returns"""
        return 100 * monthlytable(self.returns, f)

    def metrics(self, days=252):
        """metrics"""
        return {
            "Sharpe": np.sqrt(days) * self.returns.mean() / self.returns.std(),
            "Kurtosis": self.returns.kurtosis(),
            "Skewness": self.returns.skew(),
            "Annualized Volatility (%)": 100 * np.sqrt(days) * self.returns.std(),
            "Annualized Return (%)": 100 * days * self.returns.mean(),
        }

    # def metrics2(self, days=252):
    #     return {
    #         "Sharpe": np.sqrt(days) * self.profit.mean() / self.profit.std(),
    #         "Kurtosis": self.profit.kurtosis(),
    #         "Skewness": self.profit.skew(),
    #         "Annualized Volatility (%)": 100
    #         * np.sqrt(days)
    #         * self.profit.std()
    #         / self.aum,
    #         "Annualized Return (%)": 100 * days * self.profit.mean() / self.aum,
    #     }
    #     # return self.returns().resample("M").sum()

    def plot(self, com=100, **kwargs):
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)

        # fig.append_trace(
        fig.add_trace(
            go.Scatter(
                x=self.nav_accum.index, y=self.nav_accum, name="NAV accumulated"
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=self.nav_accum.index,
                y=self.returns.ewm(com=com).std(),
                name="Volatility",
            ),
            row=2,
            col=1,
        )
        # portfolio.nav_accum.plot(), row=1, col=1)

        fig.update_layout(
            {
                "title": "NAV Accumulated",
                "xaxis": {"title": "Time"},
                "yaxis": {"title": "NAV"},
                "showlegend": True,
            }
        )

        return fig
