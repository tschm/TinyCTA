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
"""Signal processing functions for trend-following CTA strategies.

Provides oscillator computation and volatility-adjusted return calculations
used to generate trading signals from price data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def osc(prices: pd.DataFrame, fast: int = 32, slow: int = 96, scaling: bool = True) -> pd.DataFrame:
    """Compute the oscillator for a given financial price data.

    Use Exponential Weighted Moving Averages (EWM). The calculation involves
    the difference between fast and slow EWM means, optionally scaled by the
    standard deviation.

    Args:
        prices: DataFrame containing the price data used for the oscillator computation.
        fast: The time period for the fast EWM calculation. Default is 32.
        slow: The time period for the slow EWM calculation. Default is 96.
        scaling: If True, the difference will be scaled using its standard deviation.
            If False, scaling is skipped. Default is True.

    Returns:
        DataFrame containing the computed oscillator values.
    """
    diff = prices.ewm(com=fast - 1).mean() - prices.ewm(com=slow - 1).mean()
    s = diff.std() if scaling else 1

    return diff / s


def returns_adjust(price: pd.DataFrame, com: int = 32, min_periods: int = 300, clip: float = 4.2) -> pd.DataFrame:
    """Calculate and adjust log returns for a given price DataFrame.

    Computes the logarithmic returns, normalizes them using exponentially
    weighted moving standard deviation, and clips the resulting values to a
    specified range.

    Args:
        price: DataFrame containing price data for which log returns will be calculated.
        com: Center of mass for the exponentially weighted moving average. Default is 32.
        min_periods: Minimum number of periods required for the EWMA standard deviation
            to be valid. Default is 300.
        clip: Absolute value threshold to which the adjusted returns are clipped.
            Default is 4.2.

    Returns:
        A DataFrame of normalized and clipped log returns for the input price data.
    """
    r = price.apply(np.log).diff()
    return (r / r.ewm(com=com, min_periods=min_periods).std()).clip(-clip, +clip)


def moving_absolute_deviation(price: pd.DataFrame, com: int = 32, min_periods: int = 300) -> pd.DataFrame:
    """Compute the rolling median absolute deviation (MAD) of log returns.

    This is a robust alternative to moving variance/standard deviation as it is
    less sensitive to outliers. Both the center (median) and the dispersion
    (median of absolute deviations) use the rolling median, making the estimate
    doubly robust compared to mean-based approaches.

    Parameters:
    price : pd.DataFrame
        The DataFrame containing price data.
    com : int, default=32
        Specifies the center of mass, used to derive the rolling window size as
        ``window = 2 * com - 1``.
    min_periods : int, default=300
        Minimum number of periods required for the result to be valid. Values
        larger than the derived rolling window are capped to ``window`` so the
        rolling calculations remain valid.

    Returns:
        pd.DataFrame
            A DataFrame of rolling median absolute deviations of log returns.
    """
    r = price.apply(np.log).diff()
    window = 2 * com - 1
    effective_min_periods = min(min_periods, window)
    rolling_median = r.rolling(window=window, min_periods=effective_min_periods).median()
    return (r - rolling_median).abs().rolling(window=window, min_periods=effective_min_periods).median()


def shrink2id(matrix: np.ndarray, lamb: float = 1.0) -> np.ndarray:
    """Shrink a square matrix towards the identity matrix by a weight factor.

    Args:
        matrix: The input square matrix to be shrunk.
        lamb: Mixing ratio for shrinkage. A value of 1.0 retains the original
            matrix; 0.0 replaces it entirely with the identity matrix. Default is 1.0.

    Returns:
        The resulting matrix after applying the shrinkage transformation.
    """
    return matrix * lamb + (1 - lamb) * np.eye(N=matrix.shape[0])
