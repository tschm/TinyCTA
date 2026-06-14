"""Engine for correlation-aware risk position optimization."""

from __future__ import annotations

import dataclasses
from collections.abc import Hashable

import numpy as np
import polars as pl

from .config import Config
from .ewm_cov import ewm_covariance as _ewm_covariance
from .linalg import inv_a_norm as _inv_a_norm
from .linalg import solve as _solve
from .signal import shrink2id as _shrink2id
from .util import vol_adj as _vol_adj

# Arbitrary epsilon floor for the correlation-norm denominator: any nearby
# threshold value or a ``<`` vs ``<=`` boundary behaves identically for
# realistic denominators, so this comparison is intentionally excluded from
# mutation.
_DENOM_EPSILON = 1e-12


def _denominator_is_degenerate(denom: float) -> bool:
    """Return True when the correlation-norm denominator is effectively zero."""
    return denom <= _DENOM_EPSILON  # pragma: no mutate


def _risk_position(corr: np.ndarray, mu_row: np.ndarray, mask: np.ndarray, shrink: float) -> np.ndarray:
    """Solve the shrunk correlation system for one timestamp's tradable assets.

    Shrinks ``corr`` towards the identity by ``shrink`` (via
    :func:`~tinycta.signal.shrink2id`), restricts it to the masked assets, solves
    for the expected returns ``mu_row`` and normalises by ``inv_a_norm`` so the raw
    risk position has unit norm under the correlation metric. Returns zeros when the
    normaliser is non-finite/degenerate or ``mu_row`` is all-zero.

    Args:
        corr: Full EWMA correlation matrix for the timestamp.
        mu_row: Expected returns for every asset at the timestamp (NaNs tolerated).
        mask: Boolean mask of currently-tradable assets.
        shrink: Identity-shrinkage weight in ``[0, 1]``.

    Returns:
        np.ndarray: The normalised risk position over the masked assets.
    """
    matrix = _shrink2id(corr, lamb=shrink)[np.ix_(mask, mask)]
    expected_mu = np.nan_to_num(mu_row[mask])
    denom = _inv_a_norm(expected_mu, matrix)
    if denom is None or not np.isfinite(denom) or _denominator_is_degenerate(denom) or np.allclose(expected_mu, 0.0):
        return np.zeros_like(expected_mu)
    return _solve(matrix, expected_mu) / denom


def _update_profit_variance(
    profit_variance: float,
    cash_pos_prev: np.ndarray,
    returns_row: np.ndarray,
    ret_mask: np.ndarray,
    lamb: float,
) -> float:
    """EWMA-update the running profit-variance estimate with one period's P&L.

    Realised profit is the previous cash position dotted with the current returns
    over the jointly-finite assets; the variance decays towards the new squared
    profit by ``1 - lamb``.

    Args:
        profit_variance: Previous running profit-variance estimate.
        cash_pos_prev: Previous timestamp's cash position (NaNs tolerated).
        returns_row: Current timestamp's simple returns (NaNs tolerated).
        ret_mask: Boolean mask of assets finite in both rows.
        lamb: EWMA decay factor.

    Returns:
        float: The updated profit-variance estimate.
    """
    lhs = np.nan_to_num(cash_pos_prev[ret_mask], nan=0.0)
    rhs = np.nan_to_num(returns_row[ret_mask], nan=0.0)
    profit = lhs @ rhs
    return lamb * profit_variance + (1 - lamb) * profit**2


@dataclasses.dataclass(frozen=True)
class Engine:
    """Correlation-aware risk position optimizer (Basanos engine)."""

    prices: pl.DataFrame
    mu: pl.DataFrame
    cfg: Config

    def __post_init__(self) -> None:
        """Validate that prices and mu are aligned and both contain a date column."""
        if "date" not in self.prices.columns:
            msg = "prices must contain a 'date' column"
            raise ValueError(msg)
        if "date" not in self.mu.columns:
            msg = "mu must contain a 'date' column"
            raise ValueError(msg)
        if self.prices.shape != self.mu.shape:
            msg = f"prices and mu must share the same shape, got {self.prices.shape} and {self.mu.shape}"
            raise ValueError(msg)
        if set(self.prices.columns) != set(self.mu.columns):
            msg = "prices and mu must share identical columns"
            raise ValueError(msg)

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
    def cor(self) -> dict[Hashable, np.ndarray]:
        """Per-timestamp EWMA correlation matrices, keyed by the ``date`` value.

        Each key is the value of the ``date`` column for that timestamp (a
        ``datetime.date`` in normal use, though any hashable index value such as
        an integer is accepted), and each value is the square symmetric
        correlation matrix over :attr:`assets`, in column order.

        The correlation matrix is derived from the EWMA covariance
        (:func:`~tinycta.ewm_cov.ewm_covariance`) with span ``2 * cfg.corr + 1``
        and a ``cfg.corr`` warmup.

        Contract:

        - **Warmup.** Timestamps before any asset pair has accumulated
          ``cfg.corr`` common observations are absent from the dict entirely
          (the underlying covariance drops all-NaN dates).
        - **NaN cells.** A cell is ``NaN`` whenever its variance is
          non-positive (e.g. an asset that has not yet warmed up, or a
          late-starting asset); the date is still present as long as at least
          one cell is finite. Downstream, :attr:`cash_position` masks to the
          currently-tradable assets, so these ``NaN`` cells are not solved.

        Returns:
            dict[Hashable, np.ndarray]: Date-keyed correlation matrices.
        """
        cov = _ewm_covariance(
            self.ret_adj,
            assets=self.assets,
            index_col="date",
            window=2 * self.cfg.corr + 1,
            warmup=self.cfg.corr,
        )
        result = {}
        for k, mat in cov.items():
            std = np.sqrt(np.abs(np.diag(mat)))
            outer = np.outer(std, std)
            result[k] = np.where(outer > 0, mat / outer, np.nan)
        return result

    @property
    def cash_position(self) -> pl.DataFrame:
        """Correlation-shrinkage-optimized cash positions for each timestamp.

        Walks forward through time, and at each timestamp ``t``:

        1. **Mask** assets with a finite price at ``t`` so the optimisation only
           sees currently-tradable instruments.
        2. **Shrink** the EWMA correlation matrix towards the identity by
           ``cfg.shrink`` (via :func:`~tinycta.signal.shrink2id`) for numerical
           stability, then restrict it to the masked assets.
        3. **Solve** the shrunk system for the expected returns ``mu`` and
           normalise by ``inv_a_norm(mu, matrix)`` so the raw risk position has
           unit norm under the correlation metric (zeroed when the denominator
           is non-finite/degenerate or ``mu`` is all-zero).
        4. **Scale** the risk position by a running EWMA estimate of realised
           profit variance (decay ``lamb=0.99``), which down-weights positions
           after volatile P&L, then divide by per-asset EWMA volatility
           (``self.vola``) to convert the risk position into a cash position.

        Returns:
            pl.DataFrame: The input ``prices`` frame (including its ``date``
                column) with each asset column replaced by its per-timestamp
                cash position. Warmup rows are ``NaN``.

        Example:
            >>> import polars as pl
            >>> from tinycta.config import Config
            >>> from tinycta.engine import Engine
            >>> prices = pl.DataFrame({"date": [1, 2, 3], "A": [100.0, 101.0, 102.0]})
            >>> mu = pl.DataFrame({"date": [1, 2, 3], "A": [0.0, 0.1, 0.2]})
            >>> engine = Engine(prices=prices, mu=mu, cfg=Config(vola=2, corr=2, clip=4.2, shrink=0.5))
            >>> positions = engine.cash_position
        """
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
                    profit_variance = _update_profit_variance(
                        profit_variance, cash_pos_np[i - 1], returns_num[i], ret_mask, lamb
                    )

            if not mask.any():
                continue

            pos = _risk_position(cor[t], mu[i], mask, self.cfg.shrink)
            risk_pos_np[i, mask] = pos / profit_variance
            cash_pos_np[i, mask] = risk_pos_np[i, mask] / vola_np[i, mask]

        return self.prices.with_columns([(pl.lit(cash_pos_np[:, i]).alias(asset)) for i, asset in enumerate(assets)])
