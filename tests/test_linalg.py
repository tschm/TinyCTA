"""test linalg"""

from __future__ import annotations

import numpy as np
import pytest

from tinycta.linalg import a_norm, inv_a_norm, solve, valid


def test_non_quadratic():
    """
    Mismatch in matrix not square
    """
    with pytest.raises(AssertionError):
        valid(np.array([[2.0, 1.0]]))

    with pytest.raises(AssertionError):
        a_norm(vector=np.array([2.0, 1.0]), matrix=np.array([[2.0, 1.0]]))

    with pytest.raises(AssertionError):
        inv_a_norm(vector=np.array([2.0, 1.0]), matrix=np.array([[2.0, 1.0]]))

    with pytest.raises(AssertionError):
        solve(matrix=np.array([[2.0, 1.0]]), rhs=np.array([2.0, 1.0]))


def test_mismatch():
    """
    Mismatch in matrix dimensions vs vector dimensions
    """
    with pytest.raises(AssertionError):
        a_norm(vector=np.array([1.0, 2.0]), matrix=np.array([[1.0]]))

    with pytest.raises(AssertionError):
        inv_a_norm(vector=np.array([1.0, 2.0]), matrix=np.array([[1.0]]))

    with pytest.raises(AssertionError):
        solve(matrix=np.array([[1.0]]), rhs=np.array([1.0, 2.0]))


def test_valid():
    """
    Valid submatrices
    """
    a = np.array([[1.0, np.nan], [np.nan, np.nan]])
    val, submatrix = valid(a)

    np.testing.assert_array_equal(val, np.array([True, False]))
    np.testing.assert_array_equal(submatrix, np.array([[1.0]]))


def test_valid_eye():
    """
    Valid submatrix applied to identity
    """
    a = np.eye(2)
    val, submatrix = valid(a)

    np.testing.assert_array_equal(val, np.array([True, True]))
    np.testing.assert_array_equal(submatrix, np.eye(2))


def test_anorm_without_matrix():
    """
    a-norm without matrix
    """
    v = np.array([[3.0, 4.0]])
    assert a_norm(vector=v) == pytest.approx(5.0)


def test_anorm_with_matrix():
    """
    a-norm with matrix
    """
    v = np.array([3.0, 4.0])
    a = 2 * np.eye(2)
    assert a_norm(vector=v, matrix=a) == pytest.approx(np.sqrt(2) * 5.0)


def test_anorm_all_nan():
    """
    a-norm with matrix but all NaNs
    """
    v = np.array([3.0, 4.0])
    a = np.nan * np.eye(2)
    assert np.isnan(a_norm(vector=v, matrix=a))


def test_inv_a_norm():
    """
    inv a-norm
    """
    v = np.array([3.0, 4.0])
    a = 0.5 * np.eye(2)
    assert inv_a_norm(vector=v, matrix=a) == pytest.approx(np.sqrt(2) * 5.0)


def test_inv_a_norm_without_matrix():
    """
    inv-a-norm without matrix a
    """
    v = np.array([3.0, 4.0])
    assert inv_a_norm(vector=v) == pytest.approx(5.0)


def test_inv_a_norm_all_nan():
    """
    inv-a-norm with matrix a but all NaNs
    """
    v = np.array([3.0, 4.0])
    a = np.nan * np.eye(2)
    assert np.isnan(inv_a_norm(vector=v, matrix=a))


def test_solve():
    """
    test solve
    """
    rhs = np.array([3.0, 4.0])
    matrix = 0.5 * np.eye(2)
    x = solve(matrix=matrix, rhs=rhs)

    np.testing.assert_array_equal(matrix @ x, rhs)
