"""Tests for the signal processing module of TinyCTA."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from tinycta.signal import moving_absolute_deviation, shrink2id


def test_moving_absolute_deviation(prices: pd.DataFrame) -> None:
    """Test moving_absolute_deviation returns non-negative values."""
    mad = prices.apply(moving_absolute_deviation)
    assert (mad.dropna() >= 0).all().all()
    assert mad.std()["-9186993121995610806"] == pytest.approx(0.000859190064724947)


def test_shrink2id() -> None:
    """Test shrink2id shrinks off-diagonal elements by lambda."""
    matrix = np.array([[1.0, 1.0], [1.0, 1.0]])
    s = shrink2id(matrix=matrix, lamb=0.3)
    np.testing.assert_array_equal(s, np.array([[1.0, 0.3], [0.3, 1.0]]))
