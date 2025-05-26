"""Tests for the signal processing module of TinyCTA.

This module contains tests for the signal processing functions in the TinyCTA package.
It tests the functionality of matrix shrinkage, returns adjustment, and oscillator calculations
with various parameters to ensure they produce the expected results.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from tinycta.signal import osc, returns_adjust, shrink2id


def test_shrink() -> None:
    """Test the shrink2id function for matrix shrinkage towards identity.

    This test verifies that the shrink2id function correctly performs linear shrinkage
    of a matrix towards the identity matrix using the specified lambda parameter.

    The test creates a matrix of all 1.0s and applies shrinkage with lambda=0.3,
    then checks that the result has 1.0s on the diagonal and 0.3s elsewhere.
    """
    matrix = np.array([[1.0, 1.0], [1.0, 1.0]])
    s = shrink2id(matrix=matrix, lamb=0.3)
    np.testing.assert_array_equal(s, np.array([[1.0, 0.3], [0.3, 1.0]]))


def test_returns_adjust(prices: pd.DataFrame) -> None:
    """Test the returns_adjust function for volatility adjustment.

    This test verifies that the returns_adjust function correctly calculates
    volatility-adjusted log returns from price data.

    Args:
        prices: DataFrame fixture containing price data for testing.

    The test applies the returns_adjust function to the prices DataFrame with
    a minimum period of 2, then checks that the standard deviation of a specific
    column matches the expected value.
    """
    r = prices.apply(returns_adjust, min_periods=2)
    assert r.std()["-9186993121995610806"] == pytest.approx(0.9771085360599361)


def test_osc_scaling(prices: pd.DataFrame) -> None:
    """Test the oscillator function with scaling enabled.

    This test verifies that the osc function correctly calculates the oscillator
    with scaling enabled, which should normalize the standard deviation to 1.0.

    Args:
        prices: DataFrame fixture containing price data for testing.

    The test applies the osc function to the prices DataFrame with default parameters
    (scaling=True), then checks that the standard deviation of a specific column
    is exactly 1.0, confirming proper scaling.
    """
    x = prices.apply(osc)
    assert x.std()["-9186993121995610806"] == 1.0


def test_osc_no_scaling(prices: pd.DataFrame) -> None:
    """Test the oscillator function with scaling disabled.

    This test verifies that the osc function correctly calculates the oscillator
    with scaling disabled, which should preserve the original standard deviation.

    Args:
        prices: DataFrame fixture containing price data for testing.

    The test applies the osc function to the prices DataFrame with scaling=False,
    then checks that the standard deviation of a specific column matches the
    expected unscaled value.
    """
    x = prices.apply(osc, scaling=False)
    assert x.std()["-9186993121995610806"] == pytest.approx(1.7559634754674203)
