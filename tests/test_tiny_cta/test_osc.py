"""Tests for tinycta.osc.osc.

These tests validate that the oscillator expression:
- produces finite outputs for typical parameters,
- matches the analytically scaled EWM difference,
- raises when invalid fast/slow parameters are used.
"""

from __future__ import annotations

import math
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
    """Osc equals analytically scaled EWM diff; outputs finite values."""
    fast, slow = 8, 24
    df = frame

    out = df.with_columns(osc(pl.col("A"), fast=fast, slow=slow).alias("A")).select(["date", "A"])

    f, g = 1 - 1 / fast, 1 - 1 / slow
    s = math.sqrt(1.0 / (1 - f * f) - 2.0 / (1 - f * g) + 1.0 / (1 - g * g))
    _osc = df.with_columns(
        ((pl.col("A").ewm_mean(com=fast - 1, adjust=True) - pl.col("A").ewm_mean(com=slow - 1, adjust=True)) / s).alias(
            "A"
        )
    ).select(["date", "A"])

    pt.assert_frame_equal(out, _osc)


def test_osc_multi_asset_application(frame):
    """Applying osc to multiple numeric columns should work column-wise."""
    df = frame.head(80)
    fast, slow = 6, 18
    assets = ["A", "B"]

    out = df.with_columns(osc(pl.col(c), fast=fast, slow=slow, min_samples=10).alias(c) for c in assets)

    for c in assets:
        s = out[c]
        assert s.null_count() > 0  # warmup nulls due to min_samples
        assert s.drop_nulls().len() > 0


def test_osc_invalid_params_raise(frame):
    """Invalid parameters (fast >= slow or <=1) should raise ValueError."""
    df = frame.head(32)
    with pytest.raises(ValueError, match="fast must be greater than 1"):
        _ = df.with_columns(osc(pl.col("A"), fast=1, slow=2).alias("osc"))
    with pytest.raises(ValueError, match="slow must be greater than 1"):
        _ = df.with_columns(osc(pl.col("A"), fast=2, slow=1).alias("osc"))
    with pytest.raises(ValueError, match="fast must be less than slow"):
        _ = df.with_columns(osc(pl.col("A"), fast=8, slow=8).alias("osc"))


def test_osc_non_integer_params_raise(frame):
    """Non-integer fast or slow should raise TypeError."""
    df = frame.head(32)
    with pytest.raises(TypeError, match="fast must be an integer"):
        _ = df.with_columns(osc(pl.col("A"), fast=2.0, slow=8).alias("osc"))
    with pytest.raises(TypeError, match="slow must be an integer"):
        _ = df.with_columns(osc(pl.col("A"), fast=2, slow=8.0).alias("osc"))
