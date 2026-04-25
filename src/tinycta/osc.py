"""Oscillator signal utilities built on Polars expressions.

This module provides a helper to compute an oscillator from price series using
exponentially weighted moving averages (EWMA) and an EWMA-based volatility
scaling. The functions are designed to be used inside Polars pipelines
(e.g., with DataFrame.with_columns) and operate column-wise on numeric data.
"""

import polars as pl


def osc(x: pl.Expr, fast: int, slow: int, vola: int, min_samples: int = 1) -> pl.Expr:
    """Compute an EWMA-difference oscillator scaled by EWMA volatility.

    The oscillator is defined as (EMA_fast - EMA_slow) divided by an
    EWMA-based standard deviation of first differences. This normalization
    aims to make magnitudes more comparable across parameter choices; values
    are not strictly bounded but are typically O(1) for reasonable inputs.

    Args:
        x: Polars expression representing the price series to transform.
        fast: Fast EWMA length (interpreted via ``com=fast-1``). Must be > 1.
        slow: Slow EWMA length (interpreted via ``com=slow-1``). Must be > 1 and ``slow > fast``.
        vola: Lookback used to compute EWMA volatility of first differences. Must be > 0.
        min_samples: Minimum number of observations required before EWMA
            means/std are emitted; controls warmup period (earlier rows are
            null until this threshold is met).

    Returns:
        pl.Expr: A Polars expression representing the oscillator values.

    Raises:
        AssertionError: If ``fast <= 1``, ``slow <= 1``, or ``fast >= slow``;
            or if any of ``fast``, ``slow``, ``vola`` are not integers.

    Example:
        >>> prices = pl.DataFrame({"A": [1,2,3,4,5,6,7,8,9,10]})
        >>> df = prices.with_columns(osc(pl.col("A"), fast=2, slow=6, vola=3).alias("osc_A"))
    """
    # Validate parameters to catch invalid configurations as asserted in tests
    if not isinstance(fast, int):
        msg = "fast must be an integer"
        raise TypeError(msg)
    if not isinstance(slow, int):
        msg = "slow must be an integer"
        raise TypeError(msg)
    if not isinstance(vola, int):
        msg = "vola must be an integer"
        raise TypeError(msg)
    if fast <= 1:
        msg = "fast must be greater than 1"
        raise ValueError(msg)
    if slow <= 1:
        msg = "slow must be greater than 1"
        raise ValueError(msg)
    if fast >= slow:
        msg = "fast must be less than slow"
        raise ValueError(msg)

    # f, g = 1 - 1 / fast, 1 - 1 / slow
    # s = np.sqrt(1.0 / (1 - f * f) - 2.0 / (1 - f * g) + 1.0 / (1 - g * g))
    # or a moving std

    osc = x.ewm_mean(com=fast - 1, adjust=False, min_samples=min_samples) - x.ewm_mean(
        com=slow - 1, adjust=False, min_samples=min_samples
    )
    return osc / osc.ewm_std(com=vola - 1, adjust=False, min_samples=min_samples)
