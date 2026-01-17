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
"""signal."""

from __future__ import annotations

import numpy as np
import pandas as pd


# compute the oscillator
def osc(prices: pd.DataFrame, fast: int = 32, slow: int = 96, scaling: bool = True) -> pd.DataFrame:
    """Compute the oscillator for a given financial price data.

    Use Exponential Weighted Moving Averages (EWM).
    The calculation involves the difference between fast and
    slow EWM means, optionally scaled by the standard deviation.

    Parameters:
    prices (pd.DataFrame)
        DataFrame containing the price data used for the oscillator computation.
    fast (int, optional)
        The time period for the fast EWM calculation. Default is 32.
    slow (int, optional)
        The time period for the slow EWM calculation. Default is 96.
    scaling (bool, optional)
        If True, the difference will be scaled using its standard deviation. If
        False, scaling is skipped. Default is True.

    Returns:
    pd.DataFrame
        DataFrame containing the computed oscillator values.
    """
    diff = prices.ewm(com=fast - 1).mean() - prices.ewm(com=slow - 1).mean()
    s = diff.std() if scaling else 1

    return diff / s


def returns_adjust(price: pd.DataFrame, com: int = 32, min_periods: int = 300, clip: float = 4.2) -> pd.DataFrame:
    """Calculate and adjust log returns for a given price DataFrame.

    This function computes the logarithmic returns of a given price DataFrame,
    normalizes them using exponentially weighted moving standard deviation with
    specified parameters, and clips the resulting values to a specified range.

    Parameters:
    price : pd.DataFrame
        The DataFrame containing price data for which log returns will be calculated.
    com : int, default=32
        Specifies the center of mass for the exponentially weighted moving average
        calculation.
    min_periods : int, default=300
        Minimum number of periods required for the calculation of the exponentially
        weighted moving standard deviation to be valid.
    clip : float, default=4.2
        The absolute value threshold to which the adjusted returns are clipped.

    Returns:
    pd.DataFrame
        A DataFrame of normalized and clipped log returns for the input price data.
    """
    r = np.log(price).diff()
    return (r / r.ewm(com=com, min_periods=min_periods).std()).clip(-clip, +clip)


def shrink2id(matrix: np.ndarray, lamb: float = 1.0) -> np.ndarray:
    """Performs shrinkage of a given square matrix towards the identity matrix by a weight factor.

    This function modifies the input matrix by shrinking it towards the identity matrix. The
    shrinking is controlled by the `lamb` parameter, which determines the weighting between the
    original matrix and the identity matrix.

    Parameters:
    matrix (np.ndarray): The input square matrix to be shrunk.
    lamb (float): The mixing ratio for shrinkage. Defaults to 1.0. A value of 1.0 retains the
                  original matrix, while 0.0 completely replaces it with the identity matrix.

    Returns:
    np.ndarray: The resulting matrix after applying the shrinkage transformation.
    """
    return matrix * lamb + (1 - lamb) * np.eye(N=matrix.shape[0])
