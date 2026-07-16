"""Tests for the ewm_covariance function."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from tinycta.ewm_cov import NegativeWarmupError, ewm_covariance


@pytest.fixture
def returns() -> pl.DataFrame:
    """Two-asset returns DataFrame with a date index."""
    rng = np.random.default_rng(42)
    n = 50
    return pl.DataFrame(
        {
            "date": list(range(n)),
            "A": rng.standard_normal(n).tolist(),
            "B": rng.standard_normal(n).tolist(),
        }
    )


@pytest.fixture
def result(returns: pl.DataFrame) -> dict:
    """Default ewm_covariance result for the two-asset fixture."""
    return ewm_covariance(returns, ["A", "B"], "date", window=10)


def test_returns_dict(result: dict) -> None:
    """Result is a non-empty dictionary."""
    assert isinstance(result, dict)
    assert len(result) > 0


def test_keys_are_index_values(returns: pl.DataFrame, result: dict) -> None:
    """Dict keys are a subset of the index column values."""
    assert set(result.keys()) <= set(returns["date"].to_list())


def test_values_are_numpy_arrays(result: dict) -> None:
    """Each value is a numpy ndarray."""
    for mat in result.values():
        assert isinstance(mat, np.ndarray)


def test_shape(result: dict) -> None:
    """Each matrix has shape (n_assets, n_assets)."""
    for mat in result.values():
        assert mat.shape == (2, 2)


def test_symmetry(result: dict) -> None:
    """Each covariance matrix is symmetric."""
    for mat in result.values():
        np.testing.assert_array_equal(mat, mat.T)


def test_diagonal_non_negative(result: dict) -> None:
    """Diagonal entries (variances) are non-negative where defined."""
    for mat in result.values():
        diag = np.diag(mat)
        finite = diag[np.isfinite(diag)]
        assert (finite >= 0).all()


def test_single_asset() -> None:
    """Single-asset input produces 1x1 matrices."""
    df = pl.DataFrame({"date": list(range(10)), "X": list(range(10, 20))})
    res = ewm_covariance(df, ["X"], "date", window=3)
    for mat in res.values():
        assert mat.shape == (1, 1)


def test_halflife_mode() -> None:
    """Halflife mode returns the same structure as span mode."""
    df = pl.DataFrame(
        {
            "date": list(range(20)),
            "A": [float(i) for i in range(20)],
            "B": [float(i) * 0.5 for i in range(20)],
        }
    )
    res_span = ewm_covariance(df, ["A", "B"], "date", window=5, is_halflife=False)
    res_hl = ewm_covariance(df, ["A", "B"], "date", window=5, is_halflife=True)
    # Both modes return a dict of (2, 2) matrices covering the same dates
    assert set(res_span.keys()) == set(res_hl.keys())
    for mat in res_hl.values():
        assert mat.shape == (2, 2)
        np.testing.assert_array_equal(mat, mat.T)


def test_warmup_reduces_output_length(returns: pl.DataFrame) -> None:
    """A positive warmup produces fewer (or equal) entries than warmup=0."""
    res_no_warmup = ewm_covariance(returns, ["A", "B"], "date", window=5, warmup=0)
    res_warmup = ewm_covariance(returns, ["A", "B"], "date", window=5, warmup=10)
    assert len(res_warmup) <= len(res_no_warmup)


def test_warmup_bool_raises() -> None:
    """Passing a bool as warmup raises TypeError."""
    df = pl.DataFrame({"date": [0, 1], "A": [1.0, 2.0]})
    with pytest.raises(TypeError):
        ewm_covariance(df, ["A"], "date", warmup=True)


def test_warmup_negative_raises() -> None:
    """Passing a negative warmup raises ValueError."""
    df = pl.DataFrame({"date": [0, 1], "A": [1.0, 2.0]})
    with pytest.raises(NegativeWarmupError):
        ewm_covariance(df, ["A"], "date", warmup=-1)


def test_late_starting_asset_does_not_drop_dates() -> None:
    """Dates with at least one valid cell are kept even if one asset starts late."""
    n = 20
    a_vals = [float(i) for i in range(n)]
    # B starts only at row 10
    b_vals = [None] * 10 + [float(i) for i in range(10)]
    df = pl.DataFrame({"date": list(range(n)), "A": a_vals, "B": b_vals})
    res = ewm_covariance(df, ["A", "B"], "date", window=5)
    # Dates from the A-only period should still appear
    early_keys = [k for k in res if k < 10]  # ty: ignore[unsupported-operator]
    assert len(early_keys) > 0


def test_all_nan_dates_excluded() -> None:
    """Dates where every cell is NaN are excluded from the result."""
    # With warmup=5, the first few dates should be absent
    n = 20
    df = pl.DataFrame(
        {
            "date": list(range(n)),
            "A": [float(i) for i in range(n)],
        }
    )
    res = ewm_covariance(df, ["A"], "date", window=3, warmup=5)
    # Keys should only start once warmup is satisfied
    assert min(res.keys()) >= 4


def test_matches_pandas_ewm_cov() -> None:
    """Diagonal entries match pandas ewm(span).cov(bias=True) for complete data."""
    import pandas as pd

    rng = np.random.default_rng(0)
    n = 30
    a = rng.standard_normal(n)
    b = rng.standard_normal(n)

    df = pl.DataFrame({"date": list(range(n)), "A": a.tolist(), "B": b.tolist()})
    res = ewm_covariance(df, ["A", "B"], "date", window=5)

    pdf = pd.DataFrame({"A": a, "B": b})
    pandas_cov = pdf.ewm(span=5).cov(bias=True)

    for t, mat in res.items():
        expected_aa = pandas_cov.loc[(t, "A"), "A"]  # ty: ignore[invalid-argument-type]
        expected_bb = pandas_cov.loc[(t, "B"), "B"]  # ty: ignore[invalid-argument-type]
        expected_ab = pandas_cov.loc[(t, "A"), "B"]  # ty: ignore[invalid-argument-type]
        if np.isfinite(expected_aa):
            assert mat[0, 0] == pytest.approx(expected_aa, rel=1e-6)
        if np.isfinite(expected_bb):
            assert mat[1, 1] == pytest.approx(expected_bb, rel=1e-6)
        if np.isfinite(expected_ab):
            assert mat[0, 1] == pytest.approx(expected_ab, rel=1e-6)
