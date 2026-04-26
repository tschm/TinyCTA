"""Engine for correlation-aware risk position optimization."""

from __future__ import annotations

import dataclasses
from typing import cast

import numpy as np
import polars as pl

from .config import Config
from .linalg import inv_a_norm as _inv_a_norm
from .linalg import solve as _solve
from .signal import shrink2id as _shrink2id
from .util import vol_adj as _vol_adj


@dataclasses.dataclass(frozen=True)
class Engine:
    """Correlation-aware risk position optimizer (Basanos engine)."""

    prices: pl.DataFrame
    mu: pl.DataFrame
    cfg: Config

    def __post_init__(self) -> None:
        """Validate that prices and mu are aligned and both contain a date column."""
        if "date" not in self.prices.columns:
            raise ValueError
        if "date" not in self.mu.columns:
            raise ValueError
        if self.prices.shape != self.mu.shape:
            raise ValueError
        if not set(self.prices.columns) == set(self.mu.columns):
            raise ValueError

    @property
    def assets(self) -> list[str]:
        """List numeric asset column names, excluding the date column."""
        return [c for c in self.prices.columns if c != "date" and self.prices[c].dtype.is_numeric()]

    @property
    def ret_adj(self) -> pl.DataFrame:
        """Per-asset EWMA-volatility-adjusted log returns clipped by cfg.clip."""
        return self.prices.with_columns(
            [_vol_adj(pl.col(asset), vola=self.cfg.vola, clip=self.cfg.clip) for asset in self.assets]
        )

    @property
    def vola(self) -> pl.DataFrame:
        """Per-asset EWMA volatility of percentage returns."""
        return self.prices.with_columns(
            pl.col(asset)
            .pct_change()
            .ewm_std(com=self.cfg.vola - 1, adjust=True, min_samples=self.cfg.vola)
            .alias(asset)
            for asset in self.assets
        )

    @property
    def cor(self) -> dict[object, np.ndarray]:
        """Per-timestamp EWMA correlation matrices, returned as a date-keyed dict."""
        index = self.prices["date"]
        ret_adj_pd = self.ret_adj.select(self.assets).to_pandas()
        ewm_corr = ret_adj_pd.ewm(com=self.cfg.corr, min_periods=self.cfg.corr).corr()
        cor = ewm_corr.reset_index(names=["t", "asset"])
        return {index[cast(int, t)]: df_t.drop(columns=["t", "asset"]).to_numpy() for t, df_t in cor.groupby("t")}

    @property
    def cash_position(self) -> pl.DataFrame:
        """Correlation-shrinkage-optimized cash positions for each timestamp."""
        cor = self.cor
        assets = self.assets

        prices_num = self.prices.select(assets).to_numpy()
        returns_num = np.zeros_like(prices_num, dtype=float)
        returns_num[1:] = prices_num[1:] / prices_num[:-1] - 1.0

        mu = self.mu.select(assets).to_numpy()
        risk_pos_np = np.full_like(mu, fill_value=np.nan, dtype=float)
        cash_pos_np = np.full_like(mu, fill_value=np.nan, dtype=float)
        vola_np = self.vola.select(assets).to_numpy()

        profit_variance = 1.0
        lamb = 0.99

        for i, t in enumerate(cor.keys()):
            mask = np.isfinite(prices_num[i])

            if i > 0:
                ret_mask = np.isfinite(returns_num[i]) & mask
                if ret_mask.any():
                    cash_pos_np[i - 1] = risk_pos_np[i - 1] / vola_np[i - 1]
                    lhs = np.nan_to_num(cash_pos_np[i - 1, ret_mask], nan=0.0)
                    rhs = np.nan_to_num(returns_num[i, ret_mask], nan=0.0)
                    profit = lhs @ rhs
                    profit_variance = lamb * profit_variance + (1 - lamb) * profit**2

            if not mask.any():
                continue

            corr_n = cor[t]
            matrix = _shrink2id(corr_n, lamb=self.cfg.shrink)[np.ix_(mask, mask)]
            expected_mu = np.nan_to_num(mu[i][mask])
            denom = _inv_a_norm(expected_mu, matrix)

            if denom is None or not np.isfinite(denom) or denom <= 1e-12 or np.allclose(expected_mu, 0.0):
                pos = np.zeros_like(expected_mu)
            else:
                pos = _solve(matrix, expected_mu) / denom

            risk_pos_np[i, mask] = pos / profit_variance
            cash_pos_np[i, mask] = risk_pos_np[i, mask] / vola_np[i, mask]

        return self.prices.with_columns([(pl.lit(cash_pos_np[:, i]).alias(asset)) for i, asset in enumerate(assets)])
