import pandas as pd


class Portfolio:
    def __init__(self, prices, position=None):
        if position is None:
            position = pd.DataFrame(index=prices.index, columns=prices.keys(), data=0.0)

        if not prices.index.equals(position.index):
            raise AssertionError
        if set(prices.keys()) != set(position.keys()):
            raise AssertionError

        # avoid duplicates
        if prices.index.has_duplicates:
            raise AssertionError("Price Index has duplicates")
        if position.index.has_duplicates:
            raise AssertionError("Position Index has duplicates")

        if not prices.index.is_monotonic_increasing:
            raise AssertionError("Price Index is not increasing")
        if not position.index.is_monotonic_increasing:
            raise AssertionError("Position Index is not increasing")

        self.__prices = prices
        self.__position = position

    @property
    def prices(self):
        return self.__prices

    @property
    def index(self):
        return self.__prices.index

    @property
    def position(self):
        return self.__position

    @property
    def profit(self):
        return (self.prices.pct_change() * self.position.shift(periods=1)).sum(axis=1)

    def nav(self, init_capital=None):
        # We then simply compound the nav!
        # We could also achieve the same by scaling the
        # positions with increasing fund size...
        return (1 + self.returns(init_capital=init_capital)).cumprod()

    def returns(self, init_capital=None):
        # common problem for most CTAs.
        init_capital = init_capital or 100 * self.profit.std()
        # We assume we start every day with the same initial capital!
        return self.profit / init_capital

    # set the position for time t
    def __setitem__(self, t, value):
        self.__position.loc[t] = value
