from dataclasses import dataclass, field
import pandas as pd


def build_portfolio(prices, constracts=None, aum=1e6):
    assert isinstance(prices, pd.DataFrame)

    if constracts is None:
        constracts = pd.DataFrame(index=prices.index, columns=prices.columns, data=0.0, dtype=float)

    assert set(constracts.index).issubset(set(prices.index))
    assert set(constracts.columns).issubset(set(prices.columns))

    prices = prices[constracts.columns].loc[constracts.index]

    return _FuturesPortfolio(contracts=constracts, prices=prices.ffill(), aum=float(aum))


@dataclass(frozen=True)
class _FuturesPortfolio:
    prices: pd.DataFrame
    contracts: pd.DataFrame
    aum: float = 1e6

    @property
    def index(self):
        return self.prices.index

    @property
    def assets(self):
        return self.prices.columns

    def __iter__(self):
        for before, now in zip(self.index[:-1], self.index[1:]):
            # valuation of the current position
            #price_diff = self.prices.loc[now] - self.prices.loc[before]

            yield before, now

    def __setitem__(self, key, position):
        assert isinstance(position, pd.Series)
        assert set(position.index).issubset(set(self.assets))

        self.contracts.loc[key, position.index] = position / self.prices.loc[key]

    def __getitem__(self, item):
        assert item in self.index
        return self.contracts.loc[item]

    @property
    def profit(self) -> pd.Series:
         """
         Profit
         """
         price_changes = self.prices.ffill().diff()
         previous_stocks = self.contracts.shift(1).fillna(0.0)
         return (previous_stocks * price_changes).sum(axis=1)
