"""signal"""
from __future__ import annotations

import numpy as np


# compute the oscillator
def osc(prices, fast=32, slow=96, scaling=True):
    """
    oscillator

    Args:
        prices: a dataframe of prices
        fast: fast moving average factor, e.g. 32
        slow: slow moving average factor, e.g. 96
        scaling: true/false. If true scales with the standard deviation of the signal
        Strictly speacking this step is forward looking.

    Returns:
        oscillator
    """
    diff = prices.ewm(com=fast - 1).mean() - prices.ewm(com=slow - 1).mean()
    if scaling:
        s = diff.std()
    else:
        s = 1

    return diff / s


def returns_adjust(price, com=32, min_periods=300, clip=4.2):
    """
    volatility adjust the log-returns by a moving volatility, winsorize
    Args:
        price: a dataframe of prices
        com: center of mass for moving average for volatility
        min_periods: number of periods
        clip: winsorize at this level

    Returns:
        volatility adjusted and winsorized returns
    """
    r = np.log(price).diff()
    return (r / r.ewm(com=com, min_periods=min_periods).std()).clip(-clip, +clip)


def shrink2id(matrix, lamb=1.0):
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
