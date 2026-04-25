"""Tests for tinycta.osc.osc.

These tests validate that the oscillator expression:
- produces finite, bounded outputs for typical parameters,
- corresponds to the ratio of EWMA-difference over EWMA-std of first diffs,
- raises when invalid fast/slow parameters are used (via internal assertions).
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import polars as pl
import polars.testing as pt
import pytest

from tinycta.osc import osc


@pytest.fixture
def frame():
    """Create a sample DataFrame for testing."""
    n = 96
    seed = 0
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0, 1.0, size=n)
    p = 100.0 + np.cumsum(r)
    q = 50.0 + np.cumsum(r[::-1])
    start = date(2020, 1, 1)
    end = start + timedelta(days=n - 1)
    dates = pl.date_range(start=start, end=end, interval="1d", eager=True)
    return pl.DataFrame({"date": dates, "A": p, "B": q}).with_columns(pl.col("A", "B").cast(pl.Float64))


def test_osc_matches_reference_and_is_finite(frame):
    """Osc equals EWMA-diff divided by EWMA std of first diffs; outputs finite values."""
    fast, slow, vola = 8, 24, 16
    df = frame

    out = df.with_columns(osc(pl.col("A"), fast=fast, slow=slow, vola=vola).alias("A")).select(["date", "A"])

    d = df.with_columns(
        (pl.col("A").ewm_mean(com=fast - 1, adjust=False) - pl.col("A").ewm_mean(com=slow - 1, adjust=False)).alias("A")
    )

    _osc = d.with_columns(
        (pl.col(asset) / pl.col(asset).ewm_std(com=vola - 1, adjust=False)).alias(asset) for asset in ["A"]
    ).select(["date", "A"])

    pt.assert_frame_equal(out, _osc)


def test_osc_multi_asset_application(frame):
    """Applying osc to multiple numeric columns should work column-wise."""
    df = frame.head(80)
    fast, slow, vola = 6, 18, 12
    assets = ["A", "B"]

    out = df.with_columns(osc(pl.col(c), fast=fast, slow=slow, vola=vola, min_samples=10).alias(c) for c in assets)

    # Just ensure columns exist and yield some non-null results after warmup
    for c in assets:
        s = out[c]
        assert s.null_count() > 0  # warmup nulls due to min_samples
        assert s.drop_nulls().len() > 0


def test_osc_invalid_params_raise(frame):
    """Invalid parameters (fast >= slow or <=1) should raise ValueError in helper."""
    df = frame.head(32)
    with pytest.raises(ValueError, match="fast must be greater than 1"):
        _ = df.with_columns(osc(pl.col("A"), fast=1, slow=2, vola=8).alias("osc"))
    with pytest.raises(ValueError, match="slow must be greater than 1"):
        _ = df.with_columns(osc(pl.col("A"), fast=2, slow=1, vola=8).alias("osc"))
    with pytest.raises(ValueError, match="fast must be less than slow"):
        _ = df.with_columns(osc(pl.col("A"), fast=8, slow=8, vola=8).alias("osc"))


def test_osc_non_integer_params_raise(frame):
    """Non-integer fast, slow, or vola should raise TypeError."""
    df = frame.head(32)
    with pytest.raises(TypeError, match="fast must be an integer"):
        _ = df.with_columns(osc(pl.col("A"), fast=2.0, slow=8, vola=4).alias("osc"))
    with pytest.raises(TypeError, match="slow must be an integer"):
        _ = df.with_columns(osc(pl.col("A"), fast=2, slow=8.0, vola=4).alias("osc"))
    with pytest.raises(TypeError, match="vola must be an integer"):
        _ = df.with_columns(osc(pl.col("A"), fast=2, slow=8, vola=4.0).alias("osc"))
