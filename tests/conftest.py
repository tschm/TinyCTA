from pathlib import Path

import pytest
import pandas as pd


@pytest.fixture(scope="session", name="resource_dir")
def resource_fixture():
    """resource fixture"""
    return Path(__file__).parent / "resources"


@pytest.fixture
def prices(resource_dir):
    return pd.read_csv(resource_dir / "test_prices.csv", index_col=0, parse_dates=True, header=0)
