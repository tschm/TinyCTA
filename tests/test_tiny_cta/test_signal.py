"""Tests for the signal processing module of TinyCTA."""

from __future__ import annotations

import math

import numpy as np
import polars as pl
import polars.testing as pt
import pytest

from tinycta.signal import moving_absolute_deviation, shrink2id


def _mad_reference(col: str, com: int) -> pl.Expr:
    """Independent reference for moving_absolute_deviation with explicit window."""
    window = 2 * com - 1
    r = pl.col(col).log(base=math.e).diff()
    rolling_median = r.rolling_median(window_size=window)
    return (r - rolling_median).abs().rolling_median(window_size=window) / 0.6745


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


def _drifting_prices(n: int = 400, seed: int = 11) -> pl.DataFrame:
    """Price series whose log returns have a clear non-zero drift.

    A non-zero rolling median of returns is needed so that ``r - rolling_median``
    differs measurably from ``r + rolling_median``.
    """
    rng = np.random.default_rng(seed)
    r = rng.normal(0.01, 0.02, size=n)  # positive drift -> non-zero rolling median
    prices = 100.0 * np.exp(np.cumsum(r))
    return pl.DataFrame({"p": prices})


def test_moving_absolute_deviation_matches_reference_explicit_com() -> None:
    """MAD matches the exact window/centering/scaling for an explicit ``com``.

    Catches mutations of the window expression (``2 * com - 1``) and of the
    centering subtraction (``r - rolling_median``).
    """
    df = _drifting_prices()
    com = 20
    out = df.with_columns(moving_absolute_deviation(pl.col("p"), com=com).alias("mad")).select("mad")
    ref = df.with_columns(_mad_reference("p", com).alias("mad")).select("mad")
    pt.assert_frame_equal(out, ref)


def test_moving_absolute_deviation_default_com_is_32() -> None:
    """Calling without ``com`` uses the documented default of 32."""
    df = _drifting_prices(n=200)
    out = df.with_columns(moving_absolute_deviation(pl.col("p")).alias("mad")).select("mad")
    ref = df.with_columns(_mad_reference("p", com=32).alias("mad")).select("mad")
    pt.assert_frame_equal(out, ref)


def test_shrink2id() -> None:
    """Test shrink2id shrinks off-diagonal elements by lambda."""
    matrix = np.array([[1.0, 1.0], [1.0, 1.0]])
    s = shrink2id(matrix=matrix, lamb=0.3)
    np.testing.assert_array_equal(s, np.array([[1.0, 0.3], [0.3, 1.0]]))


def test_shrink2id_default_lambda_is_identity_passthrough() -> None:
    """Default ``lamb=1.0`` returns the matrix unchanged (no shrinkage)."""
    matrix = np.array([[1.0, 0.4], [0.4, 1.0]])
    np.testing.assert_array_equal(shrink2id(matrix), matrix)


def test_shrink2id_identity_dimension_follows_row_count() -> None:
    """The identity block is sized by ``matrix.shape[0]`` (rows), not ``shape[1]``.

    Exercised with a non-square matrix so the two sizings produce different
    result shapes, pinning the use of ``shape[0]``.
    """
    matrix = np.array([[2.0, 4.0]])  # shape (1, 2)
    result = shrink2id(matrix, lamb=0.5)
    assert result.shape == (1, 2)
    np.testing.assert_array_equal(result, matrix * 0.5 + 0.5 * np.eye(N=1))
