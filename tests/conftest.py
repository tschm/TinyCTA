"""global fixtures"""
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(scope="session", name="resource_dir")
def resource_fixture():
    """resource fixture"""
    return Path(__file__).parent / "resources"


@pytest.fixture
def prices(resource_dir):
    """prices fixture"""
    # frame = pd.read_csv(
    #     resource_dir / "Prices.csv", index_col=0, header=0
    # )

    # frame.index = pd.to_datetime(frame.index, format="%d/%m/%Y")
    # assert frame.index.is_monotonic_increasing
    # frame.columns = [hash(column) for column in frame.columns]
    # frame.to_csv(resource_dir / "Prices_hashed.csv")

    frame = pd.read_csv(resource_dir / "Prices_hashed.csv", index_col=0, header=0)

    if not frame.index.is_monotonic_increasing:
        raise AssertionError
    return frame
