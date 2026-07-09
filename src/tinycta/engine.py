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


def _denominator_is_degenerate(denom: float) -> bool:
    """Return True when the correlation-norm denominator is effectively zero.

    ``1e-12`` is an arbitrary epsilon floor: any nearby threshold value or a
    ``<`` vs ``<=`` boundary behaves identically for realistic denominators, so
    this comparison is intentionally excluded from mutation.
    """
    return denom <= 1e-12  # pragma: no mutate


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
    return float(lamb * profit_variance + (1 - lamb) * profit**2)


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
        """Per-timestamp EWMA correlation matrices, keyed by index value.

        Each key is a value of the ``date`` column (a ``datetime.date`` in normal
        use, but any hashable index value such as an integer is supported, hence
        the ``Hashable`` key type). Each value is the EWMA covariance matrix at
        that timestamp normalised to a correlation matrix (unit diagonal).

        Contract:
            - **Warmup:** the first ``cfg.corr`` timestamps are omitted — a key
              exists only once at least one matrix cell is finite (see
              :func:`~tinycta.ewm_cov.ewm_covariance`).
            - **NaN cells:** a cell is ``NaN`` while either asset is still in its
              own warmup, and a zero-variance asset (``outer == 0``) yields ``NaN``
              correlations rather than a divide-by-zero.
        """
        cov = _ewm_covariance(
            self.ret_adj,
            assets=self.assets,
            index_col="date",
            window=2 * self.cfg.corr + 1,
            warmup=self.cfg.corr,
        )
        result: dict[Hashable, np.ndarray] = {}
        for k, mat in cov.items():
            std = np.sqrt(np.abs(np.diag(mat)))
            outer = np.outer(std, std)
            # Divide only where the variance product is positive; zero-variance
            # cells stay NaN. Computing ``mat / outer`` eagerly (before masking)
            # would divide by zero on those cells and emit a spurious RuntimeWarning.
            result[k] = np.divide(mat, outer, out=np.full(mat.shape, np.nan), where=outer > 0)
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

        # ``cor`` is keyed by the post-warmup dates. Map each key back to its row
        # in prices/mu/vola so the correlation matrix for date ``t`` is paired with
        # (and stored at) that same date, rather than at a positional offset of
        # ``corr`` rows — otherwise the most recent dates never receive a position.
        row_of = {date: idx for idx, date in enumerate(self.prices["date"].to_list())}

        self._forward_walk(cor, prices_num, returns_num, mu, vola_np, risk_pos_np, cash_pos_np, row_of)

        return self.prices.with_columns([(pl.lit(cash_pos_np[:, i]).alias(asset)) for i, asset in enumerate(assets)])

    def _forward_walk(
        self,
        cor: dict[Hashable, np.ndarray],
        prices_num: np.ndarray,
        returns_num: np.ndarray,
        mu: np.ndarray,
        vola_np: np.ndarray,
        risk_pos_np: np.ndarray,
        cash_pos_np: np.ndarray,
        row_of: dict[Hashable, int],
    ) -> None:
        """Walk forward through the post-warmup timestamps, filling positions in place.

        Mutates ``risk_pos_np`` and ``cash_pos_np`` row-by-row. At each timestamp the
        previous period's realised P&L EWMA-updates a running profit-variance estimate
        (decay ``lamb=0.99``), which scales the freshly-solved risk position before it is
        divided by per-asset volatility to yield the cash position.

        Args:
            cor: Per-timestamp correlation matrices, keyed by ``date`` value.
            prices_num: Asset prices as a ``(rows, assets)`` array (NaNs tolerated).
            returns_num: Simple returns aligned to ``prices_num``.
            mu: Expected returns aligned to ``prices_num``.
            vola_np: Per-asset EWMA volatility aligned to ``prices_num``.
            risk_pos_np: Output risk-position buffer, mutated in place.
            cash_pos_np: Output cash-position buffer, mutated in place.
            row_of: Map from a ``cor`` key back to its row index.
        """
        profit_variance = 1.0
        lamb = 0.99

        prev_row: int | None = None
        for t in cor:
            row = row_of[t]
            mask = np.isfinite(prices_num[row])

            if prev_row is not None:
                ret_mask = np.isfinite(returns_num[row]) & mask
                if ret_mask.any():
                    cash_pos_np[prev_row] = risk_pos_np[prev_row] / vola_np[prev_row]
                    profit_variance = _update_profit_variance(
                        profit_variance, cash_pos_np[prev_row], returns_num[row], ret_mask, lamb
                    )

            if mask.any():
                pos = _risk_position(cor[t], mu[row], mask, self.cfg.shrink)
                risk_pos_np[row, mask] = pos / profit_variance
                cash_pos_np[row, mask] = risk_pos_np[row, mask] / vola_np[row, mask]

            prev_row = row
