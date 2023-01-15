import numpy as np
import pytest

from tinycta.signal import osc, returns_adjust, shrink2id


def test_shrink():
    matrix = np.array([[1.0, 1.0], [1.0, 1.0]])
    s = shrink2id(matrix=matrix, lamb=0.3)
    np.testing.assert_array_equal(s, np.array([[1.0, 0.3], [0.3, 1.0]]))


def test_returns_adjust(prices):
    r = prices.apply(returns_adjust, min_periods=2)
    assert r.std()["C"] == pytest.approx(1.0047100385667558)


def test_osc_scaling(prices):
    x = prices.apply(osc)
    assert x.std()["C"] == 1.0


def test_osc_no_scaling(prices):
    x = prices.apply(osc, scaling=False)
    assert x.std()["C"] == pytest.approx(1401.1333534321523)
