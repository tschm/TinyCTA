"""Tests for tinycta.engine.Engine."""

from __future__ import annotations

import datetime

import numpy as np
import polars as pl
import pytest

from tinycta.config import Config
from tinycta.engine import Engine


def _synthetic_prices(n_days: int = 500, assets: list[str] | None = None) -> pl.DataFrame:
    """Return a synthetic wide-format price DataFrame for testing."""
    if assets is None:
        assets = ["A", "B", "C"]
    rng = np.random.default_rng(42)
    dates = [datetime.date(2020, 1, 1) + datetime.timedelta(days=i) for i in range(n_days)]
    data: dict = {"date": dates}
    for asset in assets:
        returns = rng.normal(0.0001, 0.02, size=n_days)
        data[asset] = (100 * np.exp(np.cumsum(returns))).tolist()
    return pl.DataFrame(data).with_columns(pl.col("date").cast(pl.Date))


@pytest.fixture
def synthetic_prices() -> pl.DataFrame:
    """Provide synthetic price data."""
    return _synthetic_prices()


@pytest.fixture
def assets() -> list[str]:
    """Provide asset list."""
    return ["A", "B", "C"]


@pytest.fixture
def cfg() -> Config:
    """Provide a default Config with short lookbacks for speed."""
    return Config(vola=50, corr=50, clip=4.2, shrink=0.5)


class TestEngineValidation:
    """Validation checks in Engine.__post_init__."""

    def test_missing_date_in_prices_raises(self, cfg: Config):
        """Engine rejects prices without a date column."""
        bad = pl.DataFrame({"A": [1.0, 2.0], "B": [3.0, 4.0]})
        with pytest.raises(ValueError):  # noqa: PT011
            Engine(prices=bad, mu=bad, cfg=cfg)

    def test_missing_date_in_mu_raises(self, cfg: Config):
        """Engine rejects mu without a date column."""
        good = pl.DataFrame({"date": [1, 2], "A": [1.0, 2.0]})
        bad_mu = pl.DataFrame({"A": [1.0, 2.0], "B": [3.0, 4.0]})
        with pytest.raises(ValueError):  # noqa: PT011
            Engine(prices=good, mu=bad_mu, cfg=cfg)

    def test_shape_mismatch_raises(self, cfg: Config):
        """Engine rejects prices and mu with different shapes."""
        prices = pl.DataFrame({"date": [1, 2, 3], "A": [1.0, 2.0, 3.0]})
        mu = pl.DataFrame({"date": [1, 2], "A": [1.0, 2.0]})
        with pytest.raises(ValueError):  # noqa: PT011
            Engine(prices=prices, mu=mu, cfg=cfg)

    def test_column_mismatch_raises(self, cfg: Config):
        """Engine rejects prices and mu with different columns."""
        prices = pl.DataFrame({"date": [1, 2], "A": [1.0, 2.0]})
        mu = pl.DataFrame({"date": [1, 2], "B": [1.0, 2.0]})
        with pytest.raises(ValueError):  # noqa: PT011
            Engine(prices=prices, mu=mu, cfg=cfg)


class TestEngineCashPosition:
    """Behavioural tests for Engine.cash_position."""

    def test_cash_position_runs(self, synthetic_prices: pl.DataFrame, assets: list[str], cfg: Config):
        """cash_position completes without error on well-formed inputs."""
        mu = synthetic_prices.with_columns(pl.lit(0.0).alias(a) for a in assets)
        result = Engine(prices=synthetic_prices, mu=mu, cfg=cfg).cash_position
        assert result is not None
        assert set(result.columns) == set(synthetic_prices.columns)

    def test_cash_position_nonzero_mu_exercises_solve(
        self, synthetic_prices: pl.DataFrame, assets: list[str], cfg: Config
    ):
        """Non-zero mu triggers the _solve branch (line 111) and produces finite positions."""
        rng = np.random.default_rng(0)
        mu_data = {"date": synthetic_prices["date"].to_list()}
        for asset in assets:
            mu_data[asset] = rng.normal(0.001, 0.01, size=len(synthetic_prices)).tolist()
        mu = pl.DataFrame(mu_data).with_columns(pl.col("date").cast(pl.Date))
        result = Engine(prices=synthetic_prices, mu=mu, cfg=cfg).cash_position
        assert result is not None
        numeric_cols = [c for c in result.columns if c != "date"]
        assert all(result[c].is_finite().any() for c in numeric_cols)

    def test_all_nan_row_is_skipped(self, synthetic_prices: pl.DataFrame, assets: list[str], cfg: Config):
        """A row where all prices are NaN is skipped without raising."""
        nan_row = {
            col: (float("nan") if col != "date" else synthetic_prices["date"][5]) for col in synthetic_prices.columns
        }
        prices_with_nan = pl.concat(
            [
                synthetic_prices[:5],
                pl.DataFrame(nan_row).with_columns(pl.col("date").cast(pl.Date)),
                synthetic_prices[6:],
            ]
        )
        mu = prices_with_nan.with_columns(pl.lit(0.0).alias(a) for a in assets)
        result = Engine(prices=prices_with_nan, mu=mu, cfg=cfg).cash_position
        assert result is not None
