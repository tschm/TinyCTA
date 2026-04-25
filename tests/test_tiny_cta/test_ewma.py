"""Tests for tinycta.ewma.ma_cross.

These tests validate that the EWMA crossover signal:
- equals the sign of the difference between fast and slow EWMA means,
- yields zeros when fast == slow (tie), and
- works column-wise for multiple assets when used in with_columns.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import polars as pl
import polars.testing as pt

from tinycta.ewma import ma_cross


def _make_prices(n: int = 20, seed: int = 0) -> pl.DataFrame:
    """Create a simple synthetic price series with a date column and two assets.

    Prices follow a noisy random walk so that EWMA means are well-defined.
    """
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0, 1.0, size=n)
    p = 100.0 + np.cumsum(r)
    q = 50.0 + np.cumsum(r[::-1])  # a second asset with reversed path
    start = date(2020, 1, 1)
    end = start + timedelta(days=n - 1)
    dates = pl.date_range(start=start, end=end, interval="1d", eager=True)
    return pl.DataFrame({"date": dates, "A": p, "B": q}).with_columns(pl.col("A", "B").cast(pl.Float64))


def test_ma_cross_matches_independent_sign_computation():
    """ma_cross equals sign(fast_ewm - slow_ewm) for a single column.

    Validates against an independently computed expression using Polars APIs.
    """
    df = _make_prices(n=32)
    fast, slow = 4, 12

    out = df.with_columns(ma_cross(pl.col("A"), fast=fast, slow=slow, min_samples=5).alias("sig")).select(
        ["date", "sig"]
    )

    ref = df.with_columns(
        (
            pl.col("A").ewm_mean(com=fast - 1, adjust=False, min_samples=5)
            - pl.col("A").ewm_mean(com=slow - 1, adjust=False, min_samples=5)
        )
        .sign()
        .alias("sig")
    ).select(["date", "sig"])

    pt.assert_frame_equal(out, ref)


def test_ma_cross_ties_return_zero_when_fast_equals_slow():
    """When fast == slow, the difference of EWM means is 0, so signals are 0."""
    df = _make_prices(n=16)
    k = 8

    out = df.with_columns(ma_cross(pl.col("A"), fast=k, slow=k).alias("sig"))

    # All non-null entries should be exactly 0.0
    sig = out["sig"].drop_nans().drop_nulls().to_numpy()
    assert sig.shape[0] == df.height
    assert np.all(sig == 0.0)


def test_ma_cross_multi_asset_application_matches_reference():
    """Applying ma_cross to multiple assets yields per-column correct signals."""
    df = _make_prices(n=40)
    fast, slow = 6, 18

    # Use ma_cross the same way as in notebooks: with_columns over assets
    assets = [c for c in df.columns if c != "date" and df[c].dtype.is_numeric()]
    out = df.with_columns(ma_cross(pl.col(c), fast=fast, slow=slow).alias(c) for c in assets).select(["date", *assets])

    # Independent reference computation per column
    ref = df.with_columns(
        [
            (pl.col(c).ewm_mean(com=fast - 1, adjust=False) - pl.col(c).ewm_mean(com=slow - 1, adjust=False))
            .sign()
            .alias(c)
            for c in assets
        ]
    ).select(["date", *assets])

    pt.assert_frame_equal(out, ref)

    # for c in assets:
    #    assert np.allclose(out[c].to_numpy(), ref[c].to_numpy(), rtol=0, atol=0)
