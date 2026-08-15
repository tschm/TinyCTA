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
            Note that ``ewm_std`` is undefined for a single observation, so the
            first log return is null regardless of this value — the output
            therefore starts at the *second* log return.

    Returns:
        pl.Expr: Standardized and clipped log returns.

    Example:
        >>> import polars as pl
        >>> from tinycta.util import vol_adj
        >>> prices = pl.DataFrame({"A": [100.0, 102.0, 101.0, 104.0, 103.0, 106.0]})
        >>> out = prices.with_columns(vol_adj(pl.col("A"), vola=3, clip=4.2).alias("adj"))

        The first row has no log return and the second has no ``ewm_std`` (it is
        undefined for a single observation), so the series starts on the third row:

        >>> out["adj"].null_count()
        2

        Standardised returns keep the sign of the underlying move:

        >>> [v > 0 for v in out["adj"][2:]]
        [False, True, False, True]

        ``clip`` bounds the output symmetrically, which is what keeps a single
        volatility spike from dominating a downstream signal:

        >>> tight = prices.with_columns(vol_adj(pl.col("A"), vola=3, clip=1.0).alias("adj"))
        >>> all(-1.0 <= v <= 1.0 for v in tight["adj"][2:])
        True
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

    Example:
        >>> import polars as pl
        >>> from tinycta.util import adj_log_prices, vol_adj
        >>> prices = pl.DataFrame({"A": [100.0, 102.0, 101.0, 104.0, 103.0, 106.0]})
        >>> out = prices.with_columns(
        ...     vol_adj(pl.col("A"), vola=3, clip=4.2).alias("adj"),
        ...     adj_log_prices(pl.col("A"), vola=3, clip=4.2).alias("level"),
        ... )

        The result is the running total of the standardised returns, so each level
        is the previous one plus the current adjusted return:

        >>> float(out["level"][2]) == float(out["adj"][2])
        True
        >>> round(float(out["level"][3]) - float(out["level"][2]), 12) == round(float(out["adj"][3]), 12)
        True

        ``cum_sum`` carries the leading nulls through, so the level series starts
        where the adjusted returns do:

        >>> out["level"].null_count()
        2
    """
    return vol_adj(x, vola=vola, clip=clip, min_samples=min_samples).cum_sum()
