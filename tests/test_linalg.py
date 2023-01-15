import pytest
import numpy as np

from tinycta.linalg import valid, a_norm, inv_a_norm, solve


def test_non_quadratic():
    with pytest.raises(AssertionError):
        valid(np.array([[2.0, 1.0]]))


def test_valid():
    a = np.array([[1.0, np.NaN],[np.NaN, np.NaN]])
    val, submatrix = valid(a)

    np.testing.assert_array_equal(val, np.array([True, False]))
    np.testing.assert_array_equal(submatrix, np.array([[1.0]]))


def test_valid_eye():
    a = np.eye(2)
    val, submatrix = valid(a)

    np.testing.assert_array_equal(val, np.array([True, True]))
    np.testing.assert_array_equal(submatrix, np.eye(2))


def test_anorm_without_matrix():
    v = np.array([[3.0, 4.0]])
    assert a_norm(vector=v) == pytest.approx(5.0)


def test_anorm_with_matrix():
    v = np.array([3.0, 4.0])
    a = 2*np.eye(2)
    assert a_norm(vector=v, matrix=a) == pytest.approx(np.sqrt(2)*5.0)


def test_anorm_all_nan():
    v = np.array([3.0, 4.0])
    a = np.NaN * np.eye(2)
    assert np.isnan(a_norm(vector=v, matrix=a))


def test_inv_a_norm():
    v = np.array([3.0, 4.0])
    a = 0.5*np.eye(2)
    assert inv_a_norm(vector=v, matrix=a) == pytest.approx(np.sqrt(2)*5.0)


def test_inv_a_norm_without_matrix():
    v = np.array([3.0, 4.0])
    assert inv_a_norm(vector=v) == pytest.approx(5.0)


def test_inv_a_norm_all_nan():
    v = np.array([3.0, 4.0])
    a = np.NaN * np.eye(2)
    assert np.isnan(inv_a_norm(vector=v, matrix=a))


def test_solve():
    rhs = np.array([3.0, 4.0])
    matrix = 0.5*np.eye(2)
    x = solve(matrix=matrix, rhs=rhs)

    np.testing.assert_array_equal(matrix @ x, rhs)