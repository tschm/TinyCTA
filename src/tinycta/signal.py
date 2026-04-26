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


def moving_absolute_deviation(price: pd.DataFrame, com: int = 32) -> pd.DataFrame:
    """Compute the rolling median absolute deviation (MAD) of log returns.

    A robust alternative to moving standard deviation, less sensitive to outliers.
    Both the center and dispersion use rolling medians, making the estimate doubly
    robust. The result is scaled by 1/0.6745 to be a consistent estimator of std
    under normality.

    Args:
        price: DataFrame containing price data.
        com: Center of mass used to derive the rolling window as ``window = 2 * com - 1``.

    Returns:
        DataFrame of scaled rolling MAD values consistent with std under normality.
    """
    r = price.apply(np.log).diff()
    window = 2 * com - 1
    rolling_median = r.rolling(window=window).median()
    return (r - rolling_median).abs().rolling(window=window).median() / 0.6745


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
