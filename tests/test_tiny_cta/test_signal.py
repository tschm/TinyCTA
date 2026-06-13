"""Tests for the signal processing module of TinyCTA."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from tinycta.signal import moving_absolute_deviation, shrink2id


def test_moving_absolute_deviation_non_negative(prices: pl.DataFrame) -> None:
    """moving_absolute_deviation yields non-negative dispersion for every asset."""
    asset_cols = [c for c in prices.columns if c != "date"]
    mad = prices.with_columns([moving_absolute_deviation(pl.col(c)).alias(c) for c in asset_cols])
    mad_assets = mad.select(asset_cols).drop_nulls()
    assert mad_assets.select(pl.all() >= 0).select(pl.all_horizontal(pl.all())).to_series().all()


def test_moving_absolute_deviation_recovers_known_volatility() -> None:
    """The 1/0.6745 scaling makes MAD a consistent estimator of std under normality.

    Feeding a series whose log returns are i.i.d. normal with a known sigma, the
    rolling MAD should recover that sigma (rather than matching a fixture-specific
    magic constant).
    """
    rng = np.random.default_rng(0)
    n, sigma, com = 4000, 0.02, 250
    prices = 100.0 * np.exp(np.cumsum(rng.normal(0.0, sigma, size=n)))
    df = pl.DataFrame({"p": prices})
    mad = df.with_columns(moving_absolute_deviation(pl.col("p"), com=com).alias("mad"))
    estimate = mad.select(pl.col("mad").median()).item()
    assert estimate == pytest.approx(sigma, rel=0.1)


def test_shrink2id() -> None:
    """Test shrink2id shrinks off-diagonal elements by lambda."""
    matrix = np.array([[1.0, 1.0], [1.0, 1.0]])
    s = shrink2id(matrix=matrix, lamb=0.3)
    np.testing.assert_array_equal(s, np.array([[1.0, 0.3], [0.3, 1.0]]))
