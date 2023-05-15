from dataclasses import dataclass, field

import pandas as pd


def build_portfolio(prices, cashposition=None):
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

    return _FuturesPortfolio(cashposition=cashposition, prices=prices.ffill())


@dataclass(frozen=True)
class _FuturesPortfolio:
    prices: pd.DataFrame
    cashposition: pd.DataFrame

    @property
    def index(self):
        return self.prices.index

    @property
    def assets(self):
        return self.prices.columns

    def __iter__(self):
        for before, now in zip(self.index[:-1], self.index[1:]):
            # valuation of the current cashposition
            # price_diff = self.prices.loc[now] - self.prices.loc[before]

            yield before, now

    def __setitem__(self, key, cashposition):
        if not isinstance(cashposition, pd.Series):
            raise AssertionError
        if not set(cashposition.index).issubset(set(self.assets)):
            raise AssertionError

        self.cashposition.loc[key, cashposition.index] = cashposition

    def __getitem__(self, item):
        if item not in self.index:
            raise AssertionError
        return self.cashposition.loc[item]

    def nav(self, aum) -> pd.Series:
        """
        Profit
        """
        return self.profit.cumsum() + aum

    @property
    def profit(self):
        price_changes = self.prices.ffill().pct_change()
        previous_position = self.cashposition.shift(1)
        return (previous_position * price_changes).sum(axis=1)

    @property
    def start(self):
        return self.profit.ne(0).idxmax()

    def truncate(self, before=None, after=None):
        return _FuturesPortfolio(
            prices=self.prices.truncate(before=before, after=after),
            cashposition=self.cashposition.truncate(before=before, after=after),
        )
