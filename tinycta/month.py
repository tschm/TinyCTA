"""
Popular year vs month performance table.

Supports compounded and cumulative (i.e. fixed AUM) returns logic.
"""
from __future__ import annotations

from enum import Enum
import calendar

import numpy as np
import pandas as pd

from tinycta.types import TIMESERIES


def _compound_returns(returns):
    return (1.0 + returns).prod() - 1.0


def _cumulative_returns(returns):
    return returns.sum()


class Aggregate(Enum):
    COMPOUND = _compound_returns
    CUMULATIVE = _cumulative_returns


def monthlytable(returns: TIMESERIES, f: Aggregate) -> pd.DataFrame:
    """
    Get a table of monthly returns.

    Args:
        returns: Series of individual returns.
        f: Aggregate function to use.

    Returns:
        DataFrame with monthly returns, their STDev and YTD.
    """
    # Works better in the first month
    # Compute all the intramonth-returns
    # instead of reapplying some monthly resampling of the NAV
    r = pd.Series(returns)

    return_monthly = r.groupby([r.index.year, r.index.month]).apply(f)

    frame = return_monthly.unstack(level=1).rename(
        columns=lambda x: calendar.month_abbr[x]
    )

    ytd = frame.apply(f, axis=1)
    frame["STDev"] = np.sqrt(12) * frame.std(axis=1)
    # make sure that you don't include the column for the STDev in your computation
    frame["YTD"] = ytd
    frame.index.name = "Year"
    frame.columns.name = None
    # most recent years on top
    return frame.iloc[::-1]
