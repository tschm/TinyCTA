"""Engine for correlation-aware risk position optimization.

This module is the Polars-facing orchestration layer: :class:`Engine` validates and holds
the aligned ``prices``/``mu`` frames, derives the volatility-adjusted returns and per-timestamp
EWMA correlation matrices, and hands the resulting NumPy arrays to the pure-numeric kernel in
:mod:`tinycta._kernel` for the forward walk.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Hashable

import numpy as np
import polars as pl

from ._kernel import forward_walk as _forward_walk
from .config import Config
from .ewm_cov import ewm_covariance as _ewm_covariance
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
            - **Warmup:** the first ``cfg.corr + 1`` timestamps are omitted — a
              key exists only once at least one matrix cell is finite (see
              :func:`~tinycta.ewm_cov.ewm_covariance`). That takes ``cfg.corr``
              observations of :attr:`ret_adj`, which itself starts on the third
              row because ``vol_adj`` needs two log returns to standardise one.
            - **NaN cells:** a cell is ``NaN`` while either asset is still in its
              own warmup, and a zero-variance asset (``outer == 0``) yields ``NaN``
              correlations rather than a divide-by-zero.

        Example:
            >>> import math
            >>> import polars as pl
            >>> from tinycta.config import Config
            >>> from tinycta.engine import Engine
            >>> dates = list(range(1, 11))
            >>> prices = pl.DataFrame(
            ...     {
            ...         "date": dates,
            ...         "A": [100.0, 101.5, 100.8, 102.3, 103.1, 102.0, 104.5, 105.2, 104.1, 106.0],
            ...         "B": [50.0, 49.2, 50.4, 49.8, 51.1, 50.3, 49.5, 50.8, 51.6, 50.9],
            ...     }
            ... )
            >>> mu = pl.DataFrame({"date": dates, "A": [0.1] * 10, "B": [-0.05] * 10})
            >>> cfg = Config(vola=3, corr=3, clip=4.2, shrink=0.5)
            >>> cor = Engine(prices=prices, mu=mu, cfg=cfg).cor

            The first ``cfg.corr + 1`` timestamps are omitted, so the mapping is
            keyed by the surviving dates rather than by position:

            >>> sorted(cor)
            [5, 6, 7, 8, 9, 10]

            Each value is a correlation matrix with a unit diagonal:

            >>> mat = cor[5]
            >>> mat.shape
            (2, 2)
            >>> [round(float(v), 6) for v in mat.diagonal()]
            [1.0, 1.0]
            >>> bool(-1.0 <= mat[0, 1] <= 1.0)
            True

            A zero-variance asset yields ``NaN`` rather than a divide-by-zero. Here
            ``B`` never moves, so every cell touching it is ``NaN`` while ``A`` keeps
            its unit diagonal:

            >>> flat = prices.with_columns(pl.lit(50.0).alias("B"))
            >>> flat_cor = Engine(prices=flat, mu=mu, cfg=cfg).cor[5]
            >>> math.isnan(flat_cor[1, 1]), math.isnan(flat_cor[0, 1])
            (True, True)
            >>> round(float(flat_cor[0, 0]), 6)
            1.0
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

        The per-timestamp walk itself is delegated to
        :func:`tinycta._kernel.forward_walk`, which operates purely on NumPy arrays.

        Returns:
            pl.DataFrame: The input ``prices`` frame (including its ``date``
                column) with each asset column replaced by its per-timestamp
                cash position. Warmup rows are ``NaN``.

        Example:
            >>> import math
            >>> import polars as pl
            >>> from tinycta.config import Config
            >>> from tinycta.engine import Engine
            >>> dates = list(range(1, 11))
            >>> prices = pl.DataFrame(
            ...     {
            ...         "date": dates,
            ...         "A": [100.0, 101.5, 100.8, 102.3, 103.1, 102.0, 104.5, 105.2, 104.1, 106.0],
            ...         "B": [50.0, 49.2, 50.4, 49.8, 51.1, 50.3, 49.5, 50.8, 51.6, 50.9],
            ...     }
            ... )
            >>> mu = pl.DataFrame({"date": dates, "A": [0.1] * 10, "B": [-0.05] * 10})
            >>> engine = Engine(prices=prices, mu=mu, cfg=Config(vola=3, corr=3, clip=4.2, shrink=0.5))
            >>> positions = engine.cash_position

            The frame keeps its shape and its ``date`` column; only the asset
            columns are replaced:

            >>> positions.shape
            (10, 3)
            >>> positions.columns
            ['date', 'A', 'B']

            The leading rows are warmup and come back ``NaN`` (here ``cfg.corr``
            observations of :attr:`ret_adj`, which itself starts on the third row):

            >>> sum(1 for v in positions["A"] if math.isnan(v))
            4

            After warmup the position takes the sign of the expected return, so a
            positive ``mu`` is held long and a negative one short:

            >>> [v > 0 for v in positions["A"][4:]]
            [True, True, True, True, True, True]
            >>> [v < 0 for v in positions["B"][4:]]
            [True, True, True, True, True, True]
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

        _forward_walk(cor, prices_num, returns_num, mu, vola_np, risk_pos_np, cash_pos_np, row_of, self.cfg.shrink)

        return self.prices.with_columns([(pl.lit(cash_pos_np[:, i]).alias(asset)) for i, asset in enumerate(assets)])
