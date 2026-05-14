"""Exponentially weighted covariance matrix computation."""

from __future__ import annotations

from collections.abc import Hashable

import numpy as np
import polars as pl


class NegativeWarmupError(ValueError):
    """Raised when warmup is a negative integer."""


def ewm_covariance(
    data: pl.DataFrame,
    assets: list[str],
    index_col: str,
    window: int = 30,
    is_halflife: bool = False,
    warmup: int = 0,
) -> dict[Hashable, np.ndarray]:
    """Compute the exponentially weighted covariance matrix of returns.

    EWM covariance uses the identity
    ``Cov(X, Y) = EWM(X*Y) - EWM(X)*EWM(Y)`` applied to the
    *common non-null observations* of each pair, which is equivalent
    to ``pandas.DataFrame.ewm(span).cov(bias=True)``.

    Each date is included in the result as long as at least one
    matrix entry is non-NaN.  Cells involving a late-starting asset
    are ``NaN`` until that asset has enough observations; the date is
    never dropped on account of a single asset being unavailable.
    Dates where every cell is NaN (before the warmup period is met
    for any asset) are omitted.

    Args:
        data: Polars DataFrame containing the index column and asset columns.
        assets: Ordered list of asset column names.
        index_col: Name of the index (e.g. date) column in *data*.
        window: Span (default) or half-life (when *is_halflife* is
            ``True``) of the exponential decay.  Defaults to ``30``.
        is_halflife: When ``True`` *window* is interpreted as the
            half-life; otherwise it is the EWMA span.  Defaults to
            ``False``.
        warmup: Minimum number of common observations required before
            a pair's cell is non-NaN.  Defaults to ``0`` (cells are
            non-NaN from the first shared observation).

    Returns:
        Dictionary keyed by index value (date or integer) mapping to
        a square symmetric ``numpy.ndarray`` of shape ``(n, n)``
        where ``n`` is the number of assets.  Row/column order
        matches *assets*.  Unavailable cells are ``NaN``.

    """
    if isinstance(warmup, bool) or not isinstance(warmup, int):
        raise TypeError
    if warmup < 0:
        raise NegativeWarmupError

    n = len(assets)
    min_samples = 1 if warmup == 0 else warmup

    def _ewm(expr: pl.Expr) -> pl.Expr:
        """Apply EWM mean with the configured span or half-life."""
        if is_halflife:
            return expr.ewm_mean(half_life=window, min_samples=min_samples)
        return expr.ewm_mean(span=window, min_samples=min_samples)

    cov_exprs = [
        (
            _ewm(pl.col(a) * pl.col(b))
            - _ewm(pl.when(pl.col(b).is_null()).then(None).otherwise(pl.col(a)))
            * _ewm(pl.when(pl.col(a).is_null()).then(None).otherwise(pl.col(b)))
        ).alias(f"{a}_{b}")
        for i, a in enumerate(assets)
        for b in assets[i:]
    ]

    pair_df = data.with_columns(cov_exprs).drop(assets)
    all_keys = pair_df[index_col].to_list()
    pair_arr = pair_df.drop(index_col).to_numpy()

    ii, jj = np.triu_indices(n)
    cube = np.full((len(all_keys), n, n), np.nan)
    cube[:, ii, jj] = pair_arr
    cube[:, jj, ii] = pair_arr

    has_data = ~np.all(np.isnan(cube), axis=(1, 2))
    return {k: cube[t] for t, k in enumerate(all_keys) if has_data[t]}
