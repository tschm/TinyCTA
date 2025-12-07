"""Test fixtures for the TinyCTA package.

This module contains pytest fixtures that are used across multiple test files.
These fixtures provide common test data and resources to ensure consistent testing.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(scope="session", name="resource_dir")
def resource_fixture() -> Path:
    """Provide the path to the test resources' directory.

    This fixture has session scope, meaning it's created once per test session
    and shared across all tests that use it.

    Returns:
        Path: The absolute path to the resources directory containing test data files.
    """
    return Path(__file__).parent / "resources"


@pytest.fixture
def prices(resource_dir: Path) -> pd.DataFrame:
    """Provide a DataFrame of price data for testing.

    This fixture loads price data from a CSV file with hashed column names.
    The data is used for testing signal processing functions.

    Args:
        resource_dir: Path fixture pointing to the resources directory.

    Returns:
        pd.DataFrame: A DataFrame containing price data with datetime index.
    """
    return pd.read_csv(resource_dir / "prices_hashed.csv", index_col=0, header=0, parse_dates=True)
