import pytest
import numpy as np

from pycta.linalg import valid, a_norm


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
    a = np.eye(2)
    assert a_norm(vector=v, matrix=a) == pytest.approx(5.0)