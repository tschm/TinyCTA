#    Copyright (c) 2023 Thomas Schmelzer
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
"""signal"""

from __future__ import annotations

import numpy as np
import pandas as pd


# compute the oscillator
def osc(prices: pd.DataFrame, fast: int = 32, slow: int = 96, scaling: bool = True) -> pd.DataFrame:
    """
    oscillator

    Args:
        prices: a dataframe of prices
        fast: fast moving average factor, e.g. 32
        slow: slow moving average factor, e.g. 96
        scaling: true/false. If true scales with the standard deviation of the signal
        Strictly speacking this step is forward looking.

    Returns:
        oscillator as a DataFrame
    """
    diff = prices.ewm(com=fast - 1).mean() - prices.ewm(com=slow - 1).mean()
    if scaling:
        s = diff.std()
    else:
        s = 1

    return diff / s


def returns_adjust(price: pd.DataFrame, com: int = 32, min_periods: int = 300, clip: float = 4.2) -> pd.DataFrame:
    """
    volatility adjust the log-returns by a moving volatility, winsorize
    Args:
        price: a dataframe of prices
        com: center of mass for moving average for volatility
        min_periods: number of periods
        clip: winsorize at this level

    Returns:
        volatility adjusted and winsorized returns as a DataFrame
    """
    r = np.log(price).diff()
    return (r / r.ewm(com=com, min_periods=min_periods).std()).clip(-clip, +clip)


def shrink2id(matrix: np.ndarray, lamb: float = 1.0) -> np.ndarray:
    """
    Simple shrinkage towards the identity

    Args:
        matrix: the matrix A
        lamb: the shrinkage factor lambda

    Returns:
        A * lambda + (1 - lambda) * I
        where I is the identity matrix
    """
    return matrix * lamb + (1 - lamb) * np.eye(N=matrix.shape[0])
