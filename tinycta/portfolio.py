from dataclasses import dataclass

import pandas as pd


def build_portfolio(prices, position=None):
    if position is None:
        position = pd.DataFrame(index=prices.index, columns=prices.keys(), data=0.0)

    if not prices.index.equals(position.index):
        raise AssertionError
    if set(prices.keys()) != set(position.keys()):
        raise AssertionError

    if prices.index.has_duplicates:
        raise AssertionError("Price Index has duplicates")

    if not prices.index.is_monotonic_increasing:
        raise AssertionError("Price Index is not increasing")

    return _Portfolio(prices=prices, position=position)


@dataclass(frozen=True)
class _Portfolio:
    prices: pd.DataFrame
    position: pd.DataFrame

    @property
    def index(self):
        return self.prices.index

    @property
    def profit(self):
        """
        Profit of a portfolio

        Returns:
            Timeseries of profits, e.g. prices-%-change * position (in currency units) of yesterday
        """
        return (self.prices.pct_change() * self.position.shift(periods=1)).sum(axis=1)

    def nav(self, init_capital=None):
        # We then simply compound the nav!
        # We could also achieve the same by scaling the
        # positions with increasing fund size...
        return (1 + self.returns(init_capital=init_capital)).cumprod()

    def returns(self, init_capital=None):
        """
        Relative returns of a portfolio

        Args:
            init_capital: if not given use 100 * standard deviation of profits

        Returns:
            Profit / init_capital. The initial capital is kept constant throughout a backtest.
        """

        # common problem for most CTAs.
        init_capital = init_capital or 100 * self.profit.std()
        # We assume we start every day with the same initial capital!
        return self.profit / init_capital

    # set the position for time t
    def __setitem__(self, t, value):
        self.position.loc[t] = value
