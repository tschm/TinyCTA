"""test signal"""

from __future__ import annotations

import numpy as np
import pytest

from tinycta.signal import osc, returns_adjust, shrink2id


def test_shrink():
    """shrink matrix"""
    matrix = np.array([[1.0, 1.0], [1.0, 1.0]])
    s = shrink2id(matrix=matrix, lamb=0.3)
    np.testing.assert_array_equal(s, np.array([[1.0, 0.3], [0.3, 1.0]]))


def test_returns_adjust(prices):
    """adjusted returns"""
    r = prices.apply(returns_adjust, min_periods=2)
    assert r.std()["-9186993121995610806"] == pytest.approx(0.9771085360599361)


def test_osc_scaling(prices):
    """oscillator with scaling"""
    x = prices.apply(osc)
    assert x.std()["-9186993121995610806"] == 1.0


def test_osc_no_scaling(prices):
    """oscillator without scaling"""
    x = prices.apply(osc, scaling=False)
    assert x.std()["-9186993121995610806"] == pytest.approx(1.7559634754674203)
