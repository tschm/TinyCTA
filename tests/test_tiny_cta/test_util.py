"""Tests for tinycta.util helpers: vol_adj and adj_log_prices.

These tests verify that:
- vol_adj standardizes log returns and applies clipping,
- adj_log_prices integrates the adjusted returns via cum_sum,
- both functions are usable as Polars expressions in with_columns.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import polars as pl
import polars.testing as pt
import pytest

from tinycta.util import adj_log_prices, vol_adj


def _make_prices(n: int = 50, seed: int = 0) -> pl.DataFrame:
    """Create a simple price series with controlled jumps for clipping checks."""
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0, 0.01, size=n)
    r[10] = 10.0  # outlier to trigger clipping
    prices = 100.0 * np.exp(np.cumsum(r))
    start = date(2020, 1, 1)
    end = start + timedelta(days=n - 1)
    dates = pl.date_range(start=start, end=end, interval="1d", eager=True)
    return pl.DataFrame({"date": dates, "P": prices}).with_columns(pl.col("P").cast(pl.Float64))


def test_vol_adj_matches_exact_reference_formula():
    """vol_adj equals ``log_returns / ewm_std(com=vola-1, adjust=True)`` clipped.

    Uses a high clip so the clamp never binds, exposing the exact ``com``,
    ``adjust`` and division (rather than multiplication) used internally. A
    separate test pins the clip bounds.
    """
    df = _make_prices(n=80, seed=3)
    vola, clip, min_samples = 10, 1e9, 1

    out = df.with_columns(vol_adj(pl.col("P"), vola=vola, clip=clip, min_samples=min_samples).alias("va")).select(
        ["date", "va"]
    )

    log_returns = pl.col("P").log().diff()
    vol = log_returns.ewm_std(com=vola - 1, adjust=True, min_samples=min_samples)
    ref = df.with_columns((log_returns / vol).clip(-clip, clip).alias("va")).select(["date", "va"])

    pt.assert_frame_equal(out, ref)


def test_vol_adj_clip_is_symmetric_lower_bound():
    """The lower clip bound is ``-clip`` (negative), not ``+clip``.

    With a tiny clip many standardized returns exceed it in magnitude. The
    minimum must reach ``-clip``; if the lower bound were ``+clip`` every value
    would collapse to the constant ``clip``.
    """
    df = _make_prices(n=80, seed=4)
    clip = 0.5
    out = df.with_columns(vol_adj(pl.col("P"), vola=10, clip=clip).alias("va"))
    vals = out["va"].drop_nulls().to_numpy()
    assert vals.min() == pytest.approx(-clip)
    assert vals.min() < vals.max()  # not collapsed to a constant


def test_vol_adj_clips_and_is_finite():
    """vol_adj should clip standardized log returns and yield finite outputs."""
    df = _make_prices(n=60)
    vola, clip = 12, 3.0

    out = df.with_columns(vol_adj(pl.col("P"), vola=vola, clip=clip).alias("va"))

    s = out["va"].drop_nulls()
    assert (s >= -clip).all()
    assert (s <= clip).all()
    assert s.is_finite().all()


def test_adj_log_prices_is_cumsum_of_vol_adj():
    """adj_log_prices should be the cumulative sum of vol_adj outputs."""
    df = _make_prices(n=40)
    vola, clip = 8, 2.5

    out = df.with_columns(
        vol_adj(pl.col("P"), vola=vola, clip=clip).alias("va"),
        adj_log_prices(pl.col("P"), vola=vola, clip=clip).alias("alp"),
    )

    mask = (~out["va"].is_null()) & (~out["alp"].is_null())
    filtered = out.filter(mask)
    assert np.allclose(filtered["alp"].to_numpy(), filtered["va"].cum_sum().to_numpy(), rtol=1e-12, atol=1e-12)


def test_vol_adj_multi_asset():
    """vol_adj applied to multiple columns should work column-wise."""
    n = 60
    rng = np.random.default_rng(1)
    r = rng.normal(0.0, 0.01, size=n)
    prices_a = 100.0 * np.exp(np.cumsum(r))
    prices_b = 50.0 * np.exp(np.cumsum(r[::-1]))
    start = date(2020, 1, 1)
    end = start + timedelta(days=n - 1)
    dates = pl.date_range(start=start, end=end, interval="1d", eager=True)
    df = pl.DataFrame({"date": dates, "A": prices_a, "B": prices_b}).with_columns(pl.col("A", "B").cast(pl.Float64))

    vola, clip = 10, 4.0
    out = df.with_columns(vol_adj(pl.col(c), vola=vola, clip=clip).alias(c) for c in ["A", "B"])

    for c in ["A", "B"]:
        s = out[c].drop_nulls()
        assert (s >= -clip).all()
        assert (s <= clip).all()
