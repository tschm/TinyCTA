"""Property-based tests for TinyCTA using Hypothesis.

Tests mathematical invariants for linalg and signal modules.
"""

from __future__ import annotations

import math

import numpy as np
import polars as pl
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from tinycta.ewma import ma_cross
from tinycta.linalg import a_norm, inv_a_norm, solve, valid
from tinycta.osc import osc
from tinycta.signal import shrink2id
from tinycta.util import adj_log_prices, vol_adj

# Strategy for positive-definite diagonal matrices (safe for norm/solve tests)
_pos_diag = arrays(
    dtype=np.float64,
    shape=st.integers(min_value=1, max_value=8),
    elements=st.floats(min_value=0.1, max_value=1e3, allow_nan=False, allow_infinity=False),
)

# Strategy for strictly-positive finite price series (safe for log/EWMA tests).
_prices = st.lists(
    st.floats(min_value=1.0, max_value=1e4, allow_nan=False, allow_infinity=False),
    min_size=5,
    max_size=60,
)


@pytest.mark.property
@given(diag=_pos_diag)
@settings(max_examples=50)
def test_valid_identity_all_true(diag: np.ndarray) -> None:
    """valid() on a diagonal matrix with finite entries reports all rows valid."""
    mat = np.diag(diag)
    v, sub = valid(mat)
    assert v.all()
    assert sub.shape == mat.shape


@pytest.mark.property
@given(
    size=st.integers(min_value=1, max_value=8),
    scalar=st.floats(min_value=0.1, max_value=1e3, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=50)
def test_a_norm_homogeneity(size: int, scalar: float) -> None:
    """a_norm(k*v) == |k| * a_norm(v) for scalar multiples of a vector."""
    rng = np.random.default_rng(0)
    v = rng.standard_normal(size)
    expected = abs(scalar) * a_norm(vector=v)
    assert a_norm(vector=scalar * v) == pytest.approx(expected, rel=1e-9)


@pytest.mark.property
@given(diag=_pos_diag)
@settings(max_examples=50)
def test_a_norm_non_negative(diag: np.ndarray) -> None:
    """a_norm is always non-negative for any input vector."""
    rng = np.random.default_rng(1)
    v = rng.standard_normal(diag.size)
    mat = np.diag(diag)
    assert a_norm(vector=v, matrix=mat) >= 0.0


@pytest.mark.property
@given(diag=_pos_diag)
@settings(max_examples=50)
def test_inv_a_norm_non_negative(diag: np.ndarray) -> None:
    """inv_a_norm is always non-negative for any input vector."""
    rng = np.random.default_rng(2)
    v = rng.standard_normal(diag.size)
    mat = np.diag(diag)
    assert inv_a_norm(vector=v, matrix=mat) >= 0.0


@pytest.mark.property
@given(diag=_pos_diag)
@settings(max_examples=50)
def test_solve_identity_check(diag: np.ndarray) -> None:
    """solve(A, b) satisfies A @ x == b for positive-definite diagonal matrices."""
    mat = np.diag(diag)
    rng = np.random.default_rng(3)
    b = rng.standard_normal(diag.size)
    x = solve(matrix=mat, rhs=b)
    np.testing.assert_allclose(mat @ x, b, rtol=1e-9)


@pytest.mark.property
@given(
    n=st.integers(min_value=1, max_value=8),
    lamb=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=50)
def test_shrink2id_diagonal_is_one(n: int, lamb: float) -> None:
    """shrink2id always produces a matrix with ones on the diagonal."""
    rng = np.random.default_rng(4)
    mat = rng.standard_normal((n, n))
    result = shrink2id(matrix=mat, lamb=lamb)
    np.testing.assert_allclose(np.diag(result), lamb * np.diag(mat) + (1 - lamb))


@pytest.mark.property
@given(n=st.integers(min_value=1, max_value=8))
@settings(max_examples=50)
def test_shrink2id_lamb_zero_gives_identity(n: int) -> None:
    """shrink2id with lamb=0 returns the identity matrix."""
    rng = np.random.default_rng(5)
    mat = rng.standard_normal((n, n))
    result = shrink2id(matrix=mat, lamb=0.0)
    np.testing.assert_array_equal(result, np.eye(n))


@pytest.mark.property
@given(n=st.integers(min_value=1, max_value=8))
@settings(max_examples=50)
def test_shrink2id_lamb_one_preserves_matrix(n: int) -> None:
    """shrink2id with lamb=1 returns the original matrix unchanged."""
    rng = np.random.default_rng(6)
    mat = rng.standard_normal((n, n))
    result = shrink2id(matrix=mat, lamb=1.0)
    np.testing.assert_array_equal(result, mat)


@pytest.mark.property
@given(prices=_prices)
@settings(max_examples=50)
def test_ma_cross_is_sign_valued(prices: list[float]) -> None:
    """ma_cross only ever emits -1, 0, or +1 (the sign of an EWM difference)."""
    df = pl.DataFrame({"p": prices}).with_columns(ma_cross(pl.col("p"), fast=2, slow=6).alias("s"))
    values = [v for v in df["s"].to_list() if v is not None]
    assert all(v in (-1.0, 0.0, 1.0) for v in values)


@pytest.mark.property
@given(
    prices=_prices,
    clip=st.floats(min_value=0.5, max_value=10.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=50)
def test_vol_adj_respects_clip_bound(prices: list[float], clip: float) -> None:
    """Every finite vol_adj value lies within the symmetric clip bound."""
    df = pl.DataFrame({"p": prices}).with_columns(vol_adj(pl.col("p"), vola=5, clip=clip).alias("v"))
    finite = [v for v in df["v"].to_list() if v is not None and math.isfinite(v)]
    assert all(abs(v) <= clip + 1e-9 for v in finite)


@pytest.mark.property
@given(prices=_prices)
@settings(max_examples=50)
def test_adj_log_prices_integrates_vol_adj(prices: list[float]) -> None:
    """adj_log_prices is the cumulative sum of vol_adj (its first difference recovers vol_adj)."""
    df = pl.DataFrame({"p": prices})
    va = df.with_columns(vol_adj(pl.col("p"), vola=5, clip=4.2).alias("x"))["x"]
    al = df.with_columns(adj_log_prices(pl.col("p"), vola=5, clip=4.2).alias("y"))["y"]
    np.testing.assert_allclose(al.to_numpy(), va.cum_sum().to_numpy(), rtol=1e-9, equal_nan=True)


@pytest.mark.property
@given(prices=_prices)
@settings(max_examples=50)
def test_osc_is_finite(prices: list[float]) -> None:
    """Osc produces only finite values for finite, strictly-positive price series."""
    df = pl.DataFrame({"p": prices}).with_columns(osc(pl.col("p"), fast=2, slow=6).alias("o"))
    values = df["o"].to_list()
    assert all(v is not None and math.isfinite(v) for v in values)
