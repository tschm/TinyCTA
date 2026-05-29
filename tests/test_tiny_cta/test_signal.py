"""Tests for the signal processing module of TinyCTA."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from tinycta.signal import moving_absolute_deviation, shrink2id


def test_moving_absolute_deviation(prices: pl.DataFrame) -> None:
    """Test moving_absolute_deviation returns non-negative values."""
    asset_cols = [c for c in prices.columns if c != "date"]
    mad = prices.with_columns([moving_absolute_deviation(pl.col(c)).alias(c) for c in asset_cols])
    mad_assets = mad.select(asset_cols).drop_nulls()
    assert mad_assets.select(pl.all() >= 0).select(pl.all_horizontal(pl.all())).to_series().all()
    assert mad.select(pl.col("-9186993121995610806").std()).item() == pytest.approx(0.000859190064724947, rel=1e-3)


def test_shrink2id() -> None:
    """Test shrink2id shrinks off-diagonal elements by lambda."""
    matrix = np.array([[1.0, 1.0], [1.0, 1.0]])
    s = shrink2id(matrix=matrix, lamb=0.3)
    np.testing.assert_array_equal(s, np.array([[1.0, 0.3], [0.3, 1.0]]))
