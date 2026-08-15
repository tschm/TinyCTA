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

import math

import numpy as np
import polars as pl


def moving_absolute_deviation(x: pl.Expr, com: int = 32) -> pl.Expr:
    """Compute the rolling median absolute deviation (MAD) of log returns.

    A robust alternative to moving standard deviation, less sensitive to outliers.
    Both the center and dispersion use rolling medians, making the estimate doubly
    robust. The result is scaled by 1/0.6745 to be a consistent estimator of std
    under normality.

    Args:
        x: Polars expression representing the price series.
        com: Center of mass used to derive the rolling window as ``window = 2 * com - 1``.

    Returns:
        Polars expression of scaled rolling MAD values consistent with std under normality.

    Example:
        >>> import polars as pl
        >>> from tinycta.signal import moving_absolute_deviation
        >>> prices = pl.DataFrame({"A": [100.0, 101.5, 100.8, 103.2, 102.1, 105.0, 104.2, 107.5]})
        >>> mad = prices.with_columns(moving_absolute_deviation(pl.col("A"), com=2).alias("mad"))

        Two rolling medians of ``window = 2 * com - 1`` are chained over a log-return
        series that itself starts one row late, so the estimate needs
        ``2 * window - 1`` rows of returns before it emits a value:

        >>> mad["mad"].null_count()
        5
        >>> float(mad["mad"][5]) > 0.0
        True

        The estimate is a dispersion, so it never goes negative:

        >>> all(v >= 0.0 for v in mad["mad"][5:])
        True
    """
    window = 2 * com - 1
    r = x.log(base=math.e).diff()
    rolling_median = r.rolling_median(window_size=window)
    return (r - rolling_median).abs().rolling_median(window_size=window) / 0.6745


def shrink2id(matrix: np.ndarray, lamb: float = 1.0) -> np.ndarray:
    """Shrink a square matrix towards the identity matrix by a weight factor.

    Args:
        matrix: The input square matrix to be shrunk.
        lamb: Mixing ratio for shrinkage. A value of 1.0 retains the original
            matrix; 0.0 replaces it entirely with the identity matrix. Default is 1.0.

    Returns:
        The resulting matrix after applying the shrinkage transformation.

    Example:
        >>> import numpy as np
        >>> from tinycta.signal import shrink2id
        >>> corr = np.array([[1.0, 0.8], [0.8, 1.0]])

        ``lamb=1.0`` keeps the matrix as it is:

        >>> shrink2id(corr, lamb=1.0)
        array([[1. , 0.8],
               [0.8, 1. ]])

        ``lamb=0.0`` replaces it entirely with the identity:

        >>> shrink2id(corr, lamb=0.0)
        array([[1., 0.],
               [0., 1.]])

        In between, the unit diagonal is preserved and the off-diagonal
        correlation is pulled towards zero in proportion to ``1 - lamb``:

        >>> shrink2id(corr, lamb=0.5)
        array([[1. , 0.4],
               [0.4, 1. ]])
    """
    return matrix * lamb + (1 - lamb) * np.eye(N=matrix.shape[0])
