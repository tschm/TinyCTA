from dataclasses import dataclass, field

import pandas as pd


def build_portfolio(prices, cashposition=None):
    assert isinstance(prices, pd.DataFrame)

    if cashposition is None:
        cashposition = pd.DataFrame(
            index=prices.index, columns=prices.columns, data=0.0, dtype=float
        )

    assert set(cashposition.index).issubset(set(prices.index))
    assert set(cashposition.columns).issubset(set(prices.columns))

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
        assert isinstance(cashposition, pd.Series)
        assert set(cashposition.index).issubset(set(self.assets))

        self.cashposition.loc[key, cashposition.index] = cashposition

    def __getitem__(self, item):
        assert item in self.index
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
