"""Oscillator signal utilities built on Polars expressions.

This module provides a helper to compute an oscillator from price series using
exponentially weighted moving averages (EWMA) and an analytical scaling factor.
The functions are designed to be used inside Polars pipelines
(e.g., with DataFrame.with_columns) and operate column-wise on numeric data.
"""

import math

import polars as pl


def _validate_windows(fast: int, slow: int) -> None:
    """Validate the fast/slow EWMA window parameters.

    Args:
        fast: Fast EWMA length. Must be an integer greater than 1.
        slow: Slow EWMA length. Must be an integer greater than 1 and ``> fast``.

    Raises:
        TypeError: If ``fast`` or ``slow`` are not integers.
        ValueError: If ``fast <= 1``, ``slow <= 1``, or ``fast >= slow``.
    """
    for value, name in ((fast, "fast"), (slow, "slow")):
        if not isinstance(value, int):
            msg = f"{name} must be an integer"
            raise TypeError(msg)

    value_checks = (
        (fast <= 1, "fast must be greater than 1"),
        (slow <= 1, "slow must be greater than 1"),
        (fast >= slow, "fast must be less than slow"),
    )
    for failed, msg in value_checks:
        if failed:
            raise ValueError(msg)


def osc(x: pl.Expr, fast: int, slow: int, min_samples: int = 1) -> pl.Expr:
    """Compute an analytically scaled EWMA-difference oscillator.

    The oscillator is defined as (EMA_fast - EMA_slow) divided by the
    theoretical standard deviation of that difference under a unit-variance
    random walk:
        s = sqrt(1/(1-f²) - 2/(1-fg) + 1/(1-g²))
    where f = 1 - 1/fast and g = 1 - 1/slow.

    This gives consistent signal magnitudes regardless of the fast/slow
    parameter choice, without requiring a separate volatility lookback.

    Args:
        x: Polars expression representing the price series to transform.
        fast: Fast EWMA length (interpreted via ``com=fast-1``). Must be > 1.
        slow: Slow EWMA length (interpreted via ``com=slow-1``). Must be > 1 and ``slow > fast``.
        min_samples: Minimum number of observations required before EWMA
            means are emitted; controls warmup period (earlier rows are
            null until this threshold is met).

    Returns:
        pl.Expr: A Polars expression representing the oscillator values.

    Raises:
        TypeError: If ``fast`` or ``slow`` are not integers.
        ValueError: If ``fast <= 1``, ``slow <= 1``, or ``fast >= slow``.

    Example:
        >>> prices = pl.DataFrame({"A": [1,2,3,4,5,6,7,8,9,10]})
        >>> df = prices.with_columns(osc(pl.col("A"), fast=2, slow=6).alias("osc_A"))
    """
    _validate_windows(fast, slow)

    f, g = 1 - 1 / fast, 1 - 1 / slow
    s = math.sqrt(1.0 / (1 - f * f) - 2.0 / (1 - f * g) + 1.0 / (1 - g * g))

    diff = x.ewm_mean(com=fast - 1, adjust=True, min_samples=min_samples) - x.ewm_mean(
        com=slow - 1, adjust=True, min_samples=min_samples
    )
    return diff / s
