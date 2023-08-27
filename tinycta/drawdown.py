import pandas as pd


def drawdown(nav: pd.Series) -> pd.Series:
    # compute high water mark
    hwm = nav.cummax()

    # compute drawdown
    return (nav - hwm) / hwm
