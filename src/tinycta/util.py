"""Volatility adjustment and price normalization helpers (Polars expressions).

This module provides expression-level building blocks used to standardize
log returns by an exponentially weighted volatility estimate and to integrate
those standardized returns into adjusted log-price series. These are designed
for use within Polars pipelines (e.g., DataFrame.with_columns) and operate
column-wise.

Functions:
- vol_adj: Standardize log returns using EWMA volatility and clip extremes.
- adj_log_prices: Cumulative sum (integration) of standardized, clipped returns.
"""

import polars as pl


def vol_adj(x: pl.Expr, vola: int, clip: float, min_samples: int = 1) -> pl.Expr:
    """Compute clipped, volatility-adjusted log returns per column.

    Args:
        x: Price series to transform.
        vola: EWMA lookback (span-equivalent) for std.
        clip: Symmetric clipping threshold applied after standardization.
        min_samples: Minimum samples required by EWM to yield non-null values.

    Returns:
        pl.Expr: Standardized and clipped log returns.
    """
    log_returns = x.log().diff()
    vol = log_returns.ewm_std(com=vola - 1, adjust=True, min_samples=min_samples)
    return (log_returns / vol).clip(-clip, clip)


def adj_log_prices(x: pl.Expr, vola: int, clip: float, min_samples: int = 1) -> pl.Expr:
    """Integrate clipped, volatility-adjusted log returns to adjusted log prices.

    Uses ``vol_adj`` to standardize/clamp log returns and then integrates them
    via cumulative sum. The resulting series behaves like a standardized price-
    like process with roughly unit volatility.

    Args:
        x: Polars expression of the price series to transform.
        vola: EWMA lookback (span-equivalent) used to estimate volatility.
        clip: Symmetric clipping threshold applied after standardization.
        min_samples: Minimum samples required by EWM to emit non-null values.

    Returns:
        pl.Expr: Adjusted-log-price series obtained by cumulative sum of
            standardized returns.
    """
    return vol_adj(x, vola=vola, clip=clip, min_samples=min_samples).cum_sum()
