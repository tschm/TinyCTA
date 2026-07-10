"""Pure-NumPy numeric kernel for the correlation-aware position optimizer.

Every function here operates on NumPy arrays only — no Polars, no :class:`~tinycta.config.Config`
— so the Polars-facing orchestration in :mod:`tinycta.engine` stays a thin adapter that
prepares arrays, delegates the timestamp walk to :func:`forward_walk`, and writes the result
back into a DataFrame.
"""

from __future__ import annotations

from collections.abc import Hashable

import numpy as np
from loguru import logger

from .linalg import inv_a_norm as _inv_a_norm
from .linalg import solve as _solve
from .signal import shrink2id as _shrink2id


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
        logger.debug(
            "Risk position zeroed for {} masked asset(s): degenerate correlation-norm "
            "denominator (denom={}) or all-zero expected returns.",
            int(mask.sum()),
            denom,
        )
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


def forward_walk(
    cor: dict[Hashable, np.ndarray],
    prices_num: np.ndarray,
    returns_num: np.ndarray,
    mu: np.ndarray,
    vola_np: np.ndarray,
    risk_pos_np: np.ndarray,
    cash_pos_np: np.ndarray,
    row_of: dict[Hashable, int],
    shrink: float,
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
        shrink: Identity-shrinkage weight in ``[0, 1]`` passed to :func:`_risk_position`.
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
            pos = _risk_position(cor[t], mu[row], mask, shrink)
            risk_pos_np[row, mask] = pos / profit_variance
            cash_pos_np[row, mask] = risk_pos_np[row, mask] / vola_np[row, mask]

        prev_row = row
