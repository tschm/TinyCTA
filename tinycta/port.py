"""Portfolio"""
from dataclasses import dataclass

import pandas as pd


def build_portfolio(prices, cashposition=None):
    """
    Build portfolio using prices and cash positions

    Args:
        prices: frame of prices
        cashposition: None or frame of cashpositions

    Returns:
        _FuturesPortfolio object
    """
    assert isinstance(prices, pd.DataFrame)
    assert prices.index.is_monotonic_increasing
    assert prices.index.is_unique

    if cashposition is None:
        cashposition = pd.DataFrame(
            index=prices.index, columns=prices.columns, dtype=float
        )
    else:
        assert cashposition.index.is_monotonic_increasing
        assert cashposition.index.is_unique

    assert set(cashposition.index).issubset(set(prices.index))
    assert set(cashposition.columns).issubset(set(prices.columns))

    prices = prices[cashposition.columns].loc[cashposition.index]

    return _FuturesPortfolio(cashposition=cashposition, prices=prices.ffill())


@dataclass(frozen=True)
class _FuturesPortfolio:
    """Portfolio"""

    prices: pd.DataFrame
    cashposition: pd.DataFrame

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
        for before, now in zip(self.index[:-1], self.index[1:]):
            # valuation of the current cashposition
            # price_diff = self.prices.loc[now] - self.prices.loc[before]

            yield before, now

    def __setitem__(self, t, cashposition):
        """set cashposition at time t"""
        assert isinstance(cashposition, pd.Series)
        assert set(cashposition.index).issubset(set(self.assets))

        self.cashposition.loc[t, cashposition.index] = cashposition

    def __getitem__(self, item):
        """get cashposition at time t"""
        assert item in self.index
        return self.cashposition.loc[item]

    def nav(self, aum) -> pd.Series:
        """
        NAV, e.g. cumsum of daily profits and aum
        """
        return self.profit.cumsum() + aum

    @property
    def profit(self):
        """
        Daily profits, has to be cashposition yesterday x return in % between (yesterday, today)
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
        )
