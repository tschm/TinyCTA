"""EWMA-based signal generation utilities.

This module exposes helpers built around exponentially weighted moving averages
(EWMA) for use inside Polars expression pipelines. Functions operate column-
wise and are suitable for DataFrame.with_columns usage in notebooks and batch
pipelines.
"""

import polars as pl


def ma_cross(prices: pl.Expr, fast: int, slow: int, min_samples: int = 1) -> pl.Expr:
    """Return the sign of the fast-vs-slow EWM moving-average cross per column.

    Computes two exponentially weighted moving averages (EWM) of the input
    price series using windows ``fast`` and ``slow`` (interpreted as
    ``com=window-1``) and returns the sign of their difference. The output
    is -1, 0, or +1 after the warmup implied by ``min_samples``.

    Args:
        prices: Polars expression containing the price series to transform.
        fast: Length for the fast EWM mean (``fast > 0``). Typically ``fast < slow``.
        slow: Length for the slow EWM mean (``slow > 0``).
        min_samples: Minimum number of observations required before EWM values
            are produced; earlier rows will be null.

    Returns:
        pl.Expr: An expression yielding -1, 0, or +1 per row after warmup.

    Example:
        >>> prices = pl.DataFrame({"A": [1,2,3,4,5,6,7,8,9,10]})
        >>> df = prices.with_columns(
        ...     ma_cross(pl.col("A"), fast=2, slow=6, min_samples=3).alias("sig_A")
        ... )
    """
    return (
        prices.ewm_mean(com=fast - 1, adjust=False, min_samples=min_samples)
        - prices.ewm_mean(com=slow - 1, adjust=False, min_samples=min_samples)
    ).sign()
