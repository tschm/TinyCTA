"""Behavioural tests for tinycta._kernel, the pure-NumPy numeric kernel.

The kernel is otherwise exercised only indirectly through :mod:`tinycta.engine`.
These tests pin its leaf functions on observable output for known inputs — the
solved risk position, the EWMA profit-variance recursion, and the degenerate
fallback — so a behaviour change is caught at the source rather than diagnosed
through the Polars orchestration layer.
"""

from __future__ import annotations

import numpy as np
from loguru import logger

from tinycta._kernel import _denominator_is_degenerate, _risk_position, _update_profit_variance


class TestDenominatorIsDegenerate:
    """The 1e-12 epsilon floor that guards the correlation-norm division."""

    def test_true_at_and_below_the_floor(self):
        """Zero, negatives and values up to the 1e-12 floor are degenerate."""
        assert _denominator_is_degenerate(0.0)
        assert _denominator_is_degenerate(-1.0)
        assert _denominator_is_degenerate(1e-12)

    def test_false_above_the_floor(self):
        """A comfortably positive denominator is not degenerate."""
        assert not _denominator_is_degenerate(1e-6)
        assert not _denominator_is_degenerate(1.0)


class TestRiskPosition:
    """The per-timestamp shrunk-correlation solve."""

    def test_well_posed_system_solves_directionally(self):
        """Positive mu on an identity correlation yields a positive, finite position.

        With an identity correlation the shrink leaves the matrix unchanged, so the
        asset carrying zero expected return gets exactly zero weight and the asset
        with positive expected return gets a positive weight.
        """
        corr = np.eye(2)
        mu_row = np.array([1.0, 0.0])
        mask = np.array([True, True])

        pos = _risk_position(corr, mu_row, mask, shrink=0.5)

        assert np.all(np.isfinite(pos))
        assert pos[0] > 0.0
        assert pos[1] == 0.0

    def test_all_zero_mu_returns_zeros_and_logs_reason(self):
        """All-zero expected returns yield a zero position and a debug reason.

        The degenerate/all-zero fallback must be observable (zeros + a logged
        reason), not a silent NaN.
        """
        corr = np.eye(2)
        mu_row = np.zeros(2)
        mask = np.array([True, True])

        captured: list[str] = []
        sink_id = logger.add(captured.append, level="DEBUG", format="{message}")
        try:
            pos = _risk_position(corr, mu_row, mask, shrink=0.5)
        finally:
            logger.remove(sink_id)

        assert np.array_equal(pos, np.zeros(2))
        assert any("Risk position zeroed for 2 masked asset(s)" in m for m in captured)

    def test_mask_restricts_the_solve_to_tradable_assets(self):
        """Only masked-in assets appear in the returned position."""
        corr = np.eye(3)
        mu_row = np.array([1.0, 2.0, 3.0])
        mask = np.array([True, False, True])

        pos = _risk_position(corr, mu_row, mask, shrink=0.5)

        assert pos.shape == (2,)
        assert np.all(np.isfinite(pos))


class TestUpdateProfitVariance:
    """The EWMA recursion that scales positions by realised P&L variance."""

    def test_matches_the_ewma_formula_on_known_inputs(self):
        """profit_variance decays toward the squared realised profit by (1 - lamb)."""
        cash_pos_prev = np.array([1.0, 0.0])
        returns_row = np.array([0.1, 0.2])
        ret_mask = np.array([True, True])

        # profit = 1.0*0.1 + 0.0*0.2 = 0.1 ; new = 0.9*1.0 + 0.1*0.1**2 = 0.901
        updated = _update_profit_variance(1.0, cash_pos_prev, returns_row, ret_mask, lamb=0.9)

        assert updated == 0.901

    def test_treats_nans_as_zero(self):
        """NaNs in the position or returns contribute zero profit, not NaN."""
        cash_pos_prev = np.array([1.0, np.nan])
        returns_row = np.array([np.nan, 0.2])
        ret_mask = np.array([True, True])

        # both cross terms hit a NaN -> profit is 0 -> variance decays with no P&L term.
        updated = _update_profit_variance(2.0, cash_pos_prev, returns_row, ret_mask, lamb=0.5)

        assert updated == 1.0
