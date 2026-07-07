"""Behavioural tests pinning the exact arithmetic of tinycta.engine.

These complement test_engine.py by asserting *values* (not just "runs without
error") for the private helpers and properties, and by re-deriving
``cash_position`` from an independent reference implementation. Together they
exercise every operator, index and constant in the engine so that mutations are
detected rather than silently tolerated.
"""

from __future__ import annotations

import dataclasses
import datetime

import numpy as np
import polars as pl
import polars.testing as pt
import pytest

from tinycta.config import Config
from tinycta.engine import Engine, _risk_position, _update_profit_variance
from tinycta.ewm_cov import ewm_covariance
from tinycta.linalg import inv_a_norm, solve
from tinycta.signal import shrink2id


@pytest.fixture
def cfg() -> Config:
    """Short lookbacks so correlation/vola warmups are reached quickly."""
    return Config(vola=3, corr=3, clip=4.2, shrink=0.5)


def _prices_and_mu(n: int = 40, seed: int = 0, with_gap: bool = False):
    """Deterministic 3-asset prices and a non-zero mu sharing the same frame."""
    assets = ["A", "B", "C"]
    rng = np.random.default_rng(seed)
    dates = [datetime.date(2020, 1, 1) + datetime.timedelta(days=i) for i in range(n)]
    price_arr = 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.02, size=(n, len(assets))), axis=0))
    pdata: dict = {"date": dates}
    mdata: dict = {"date": dates}
    for j, a in enumerate(assets):
        vals = price_arr[:, j].tolist()
        if with_gap:
            vals[n // 2] = None  # all-null row -> mask all-False -> exercises the `continue`
        pdata[a] = vals
        mdata[a] = rng.normal(0.001, 0.01, size=n).tolist()
    prices = pl.DataFrame(pdata).with_columns(pl.col("date").cast(pl.Date))
    mu = pl.DataFrame(mdata).with_columns(pl.col("date").cast(pl.Date))
    return prices, mu, assets


# --------------------------------------------------------------------------- #
# _update_profit_variance
# --------------------------------------------------------------------------- #
def _profit_variance_reference(pv, cash_prev, returns, ret_mask, lamb):
    """Documented contract: EWMA-decay ``pv`` towards the squared masked profit.

    Realised profit is the previous cash position dotted with the current returns
    over the masked assets, with NaNs on either side coerced to zero. Independent
    re-derivation of the public formula so operator/constant mutations diverge.
    """
    profit = np.nan_to_num(cash_prev[ret_mask]) @ np.nan_to_num(returns[ret_mask])
    return lamb * pv + (1 - lamb) * profit**2


def test_update_profit_variance_matches_contract():
    """The update reproduces the documented lamb*pv + (1-lamb)*profit**2 contract."""
    pv, lamb = 0.5, 0.9
    cash_prev = np.array([1.0, 2.0, np.nan])  # NaN must be treated as 0 on the lhs
    returns = np.array([0.1, 0.2, 0.3])
    ret_mask = np.array([True, True, True])
    got = _update_profit_variance(pv, cash_prev, returns, ret_mask, lamb)
    assert got == pytest.approx(_profit_variance_reference(pv, cash_prev, returns, ret_mask, lamb))
    assert got != pytest.approx(pv)  # the update genuinely moved the estimate


def test_update_profit_variance_nan_returns_treated_as_zero():
    """A NaN on the returns side is coerced to 0 (not 1) before the dot product."""
    cash_prev = np.array([1.0, 2.0, 3.0])
    returns = np.array([0.1, 0.2, np.nan])
    ret_mask = np.array([True, True, True])
    got = _update_profit_variance(1.0, cash_prev, returns, ret_mask, 0.0)  # lamb=0 isolates profit
    assert got == pytest.approx(_profit_variance_reference(1.0, cash_prev, returns, ret_mask, 0.0))


def test_update_profit_variance_mask_selects_entries():
    """ret_mask selects which assets contribute to realised profit."""
    cash_prev = np.array([1.0, 99.0, 3.0])
    returns = np.array([0.1, 99.0, 0.3])
    ret_mask = np.array([True, False, True])
    got = _update_profit_variance(1.0, cash_prev, returns, ret_mask, 0.0)  # lamb=0 isolates profit
    assert got == pytest.approx(_profit_variance_reference(1.0, cash_prev, returns, ret_mask, 0.0))
    # The masked-out (index 1) entry must not leak into the result.
    assert got != pytest.approx(_profit_variance_reference(1.0, cash_prev, returns, np.array([True, True, True]), 0.0))


# --------------------------------------------------------------------------- #
# _risk_position
# --------------------------------------------------------------------------- #
_CORR = np.array([[1.0, 0.2, 0.1], [0.2, 1.0, 0.3], [0.1, 0.3, 1.0]])


def _risk_reference(corr, mu_row, mask, shrink):
    """Reference risk position: shrink the correlation, then solve for the masked subset."""
    matrix = shrink2id(corr, lamb=shrink)[np.ix_(mask, mask)]
    emu = np.nan_to_num(mu_row[mask])
    denom = inv_a_norm(emu, matrix)
    return solve(matrix, emu) / denom


def test_risk_position_matches_reference_full_mask():
    """Risk position equals solve(matrix, mu) / inv_a_norm(mu, matrix)."""
    mu = np.array([0.5, -0.3, 0.8])
    mask = np.array([True, True, True])
    got = _risk_position(_CORR, mu, mask, shrink=0.7)
    np.testing.assert_allclose(got, _risk_reference(_CORR, mu, mask, 0.7))
    assert not np.allclose(got, 0.0)  # genuinely non-zero -> guard did not fire


def test_risk_position_respects_mask():
    """A masked-out asset is excluded from the solved system."""
    mu = np.array([0.5, -0.3, 0.8])
    mask = np.array([True, False, True])
    got = _risk_position(_CORR, mu, mask, shrink=0.4)
    np.testing.assert_allclose(got, _risk_reference(_CORR, mu, mask, 0.4))


def test_risk_position_zero_mu_returns_zeros():
    """An all-zero mu yields a zero position."""
    mask = np.array([True, True, True])
    np.testing.assert_array_equal(_risk_position(_CORR, np.zeros(3), mask, 0.5), np.zeros(3))


def test_risk_position_non_finite_denominator_returns_zeros():
    """A non-finite (NaN) denominator short-circuits to zeros before solving.

    A NaN correlation matrix makes ``inv_a_norm`` return NaN. The ``not
    np.isfinite(denom)`` guard must fire on its own (the ``or`` is a real
    disjunction, not an ``and``); otherwise the code would divide by NaN.
    """
    corr = np.full((3, 3), np.nan)
    mu = np.array([0.5, -0.3, 0.8])
    mask = np.array([True, True, True])
    np.testing.assert_array_equal(_risk_position(corr, mu, mask, shrink=0.5), np.zeros(3))


def test_risk_position_near_zero_mu_returns_zeros():
    """A mu that is all-close to zero (1e-9) is treated as zero, not as one.

    Pins ``np.allclose(expected_mu, 0.0)`` (rather than ``1.0``): the denominator
    is ~1e-9 (> the 1e-12 floor), so only the all-close-to-zero guard makes this
    return zeros.
    """
    mask = np.array([True, True, True])
    np.testing.assert_array_equal(_risk_position(_CORR, np.full(3, 1e-9), mask, 0.5), np.zeros(3))


# --------------------------------------------------------------------------- #
# Engine structure / validation
# --------------------------------------------------------------------------- #
def test_engine_is_frozen(cfg: Config):
    """Engine is an immutable (frozen) dataclass."""
    prices, mu, _ = _prices_and_mu(n=10)
    eng = Engine(prices=prices, mu=mu, cfg=cfg)
    with pytest.raises(dataclasses.FrozenInstanceError):
        eng.cfg = cfg  # ty: ignore[invalid-assignment]


def test_validation_messages_are_exact(cfg: Config):
    """Each __post_init__ guard raises with its exact message text."""
    with pytest.raises(ValueError) as e1:  # noqa: PT011
        Engine(prices=pl.DataFrame({"A": [1.0, 2.0]}), mu=pl.DataFrame({"A": [1.0, 2.0]}), cfg=cfg)
    assert str(e1.value) == "prices must contain a 'date' column"

    with pytest.raises(ValueError) as e2:  # noqa: PT011
        Engine(prices=pl.DataFrame({"date": [1, 2], "A": [1.0, 2.0]}), mu=pl.DataFrame({"A": [1.0, 2.0]}), cfg=cfg)
    assert str(e2.value) == "mu must contain a 'date' column"

    with pytest.raises(ValueError) as e3:  # noqa: PT011
        Engine(
            prices=pl.DataFrame({"date": [1, 2, 3], "A": [1.0, 2.0, 3.0]}),
            mu=pl.DataFrame({"date": [1, 2], "A": [1.0, 2.0]}),
            cfg=cfg,
        )
    assert str(e3.value) == "prices and mu must share the same shape, got (3, 2) and (2, 2)"

    with pytest.raises(ValueError) as e4:  # noqa: PT011
        Engine(
            prices=pl.DataFrame({"date": [1, 2], "A": [1.0, 2.0]}),
            mu=pl.DataFrame({"date": [1, 2], "B": [1.0, 2.0]}),
            cfg=cfg,
        )
    assert str(e4.value) == "prices and mu must share identical columns"


def test_assets_excludes_date_and_non_numeric(cfg: Config):
    """Assets lists only numeric, non-date columns."""
    prices = pl.DataFrame({"date": [1, 2], "A": [1.0, 2.0], "label": ["x", "y"]})
    mu = pl.DataFrame({"date": [1, 2], "A": [0.0, 0.0], "label": ["p", "q"]})
    eng = Engine(prices=prices, mu=mu, cfg=cfg)
    assert eng.assets == ["A"]


# --------------------------------------------------------------------------- #
# vola / cor properties
# --------------------------------------------------------------------------- #
def test_vola_matches_reference(cfg: Config):
    """Vola equals EWMA std of pct_change with com=vola-1, adjust=True."""
    prices, mu, assets = _prices_and_mu(n=40)
    eng = Engine(prices=prices, mu=mu, cfg=cfg)
    out = eng.vola.select(assets)
    ref = prices.with_columns(
        pl.col(a).pct_change().ewm_std(com=cfg.vola - 1, adjust=True, min_samples=cfg.vola).alias(a) for a in assets
    ).select(assets)
    pt.assert_frame_equal(out, ref)


def test_cor_matches_reference(cfg: Config):
    """Cor is the EWMA covariance normalised to a correlation matrix."""
    prices, mu, assets = _prices_and_mu(n=40)
    eng = Engine(prices=prices, mu=mu, cfg=cfg)
    cov = ewm_covariance(eng.ret_adj, assets=assets, index_col="date", window=2 * cfg.corr + 1, warmup=cfg.corr)
    expected = {}
    for k, mat in cov.items():
        std = np.sqrt(np.abs(np.diag(mat)))
        outer = np.outer(std, std)
        expected[k] = np.where(outer > 0, mat / outer, np.nan)

    got = eng.cor
    assert list(got.keys()) == list(expected.keys())
    for k in expected:
        np.testing.assert_allclose(got[k], expected[k], equal_nan=True)


@pytest.mark.filterwarnings("ignore:invalid value encountered:RuntimeWarning")
@pytest.mark.filterwarnings("ignore:divide by zero encountered:RuntimeWarning")
def test_cor_zero_variance_asset_maps_to_nan(cfg: Config):
    """A zero-variance asset (std == 0) yields NaN correlations, not a 0-division.

    An asset with constant log-returns has zero variance after vol-adjustment, so
    its ``outer`` products are exactly 0. The guard is ``outer > 0`` (strictly
    positive): such entries become NaN. Were it ``outer >= 0`` they would divide
    by zero and produce inf instead.
    """
    n = 40
    rng = np.random.default_rng(0)
    dates = [datetime.date(2020, 1, 1) + datetime.timedelta(days=i) for i in range(n)]
    assets = ["A", "B", "C"]
    data: dict = {"date": dates}
    data["A"] = (100 * np.exp(np.cumsum(rng.normal(0.0002, 0.02, n)))).tolist()
    data["B"] = (100 * np.exp(np.cumsum(rng.normal(0.0002, 0.02, n)))).tolist()
    data["C"] = (100 * (1.01 ** np.arange(n))).tolist()  # constant log-returns -> zero variance
    prices = pl.DataFrame(data).with_columns(pl.col("date").cast(pl.Date))
    mu = prices.with_columns(pl.lit(0.0).alias(a) for a in assets)
    eng = Engine(prices=prices, mu=mu, cfg=cfg)

    cov = ewm_covariance(eng.ret_adj, assets=assets, index_col="date", window=2 * cfg.corr + 1, warmup=cfg.corr)
    expected = {}
    zero_outer_seen = False
    for k, mat in cov.items():
        std = np.sqrt(np.abs(np.diag(mat)))
        outer = np.outer(std, std)
        zero_outer_seen = zero_outer_seen or bool((outer == 0).any())
        expected[k] = np.where(outer > 0, mat / outer, np.nan)
    assert zero_outer_seen  # the constructed data really does exercise the outer == 0 branch

    got = eng.cor
    for k in expected:
        np.testing.assert_allclose(got[k], expected[k], equal_nan=True)


# --------------------------------------------------------------------------- #
# cash_position: independent reference re-derivation
# --------------------------------------------------------------------------- #
def _cash_position_reference(eng: Engine) -> pl.DataFrame:
    """Re-derive cash_position independently from the (separately tested) helpers.

    Uses eng.cor / eng.vola / eng.assets as already-validated inputs and
    re-implements only the forward loop, so loop-level mutations diverge.
    """
    cor = eng.cor
    assets = eng.assets
    prices_num = eng.prices.select(assets).to_numpy()
    returns_num = np.zeros_like(prices_num, dtype=float)
    returns_num[1:] = prices_num[1:] / prices_num[:-1] - 1.0
    mu = eng.mu.select(assets).to_numpy()
    vola_np = eng.vola.select(assets).to_numpy()
    risk = np.full_like(mu, np.nan, dtype=float)
    cash = np.full_like(mu, np.nan, dtype=float)
    profit_variance = 1.0
    lamb = 0.99
    row_of = {date: idx for idx, date in enumerate(eng.prices["date"].to_list())}
    prev_row = None
    for t in cor:
        row = row_of[t]
        mask = np.isfinite(prices_num[row])
        if prev_row is not None:
            ret_mask = np.isfinite(returns_num[row]) & mask
            if ret_mask.any():
                cash[prev_row] = risk[prev_row] / vola_np[prev_row]
                profit_variance = _update_profit_variance(
                    profit_variance, cash[prev_row], returns_num[row], ret_mask, lamb
                )
        if mask.any():
            pos = _risk_position(cor[t], mu[row], mask, eng.cfg.shrink)
            risk[row, mask] = pos / profit_variance
            cash[row, mask] = risk[row, mask] / vola_np[row, mask]
        prev_row = row
    return eng.prices.with_columns([pl.lit(cash[:, i]).alias(a) for i, a in enumerate(assets)])


def test_cash_position_matches_reference(cfg: Config):
    """cash_position reproduces the independent reference exactly."""
    prices, mu, _ = _prices_and_mu(n=40, seed=1)
    eng = Engine(prices=prices, mu=mu, cfg=cfg)
    pt.assert_frame_equal(eng.cash_position, _cash_position_reference(eng))


def test_cash_position_matches_reference_with_missing_row(cfg: Config):
    """cash_position handles an all-null price row (mask all-False -> continue)."""
    prices, mu, _ = _prices_and_mu(n=40, seed=2, with_gap=True)
    eng = Engine(prices=prices, mu=mu, cfg=cfg)
    pt.assert_frame_equal(eng.cash_position, _cash_position_reference(eng))


def test_cash_position_skips_degenerate_cor_key(cfg: Config, mocker):
    """A cor key whose price row is fully missing is skipped without error.

    Date-aligned iteration only visits rows that ``ewm_covariance`` deems
    computable, so an all-NaN price row is never a real cor key. This forces such
    a degenerate key to pin the two defensive guards in the forward loop: the
    all-False ``mask`` skips ``_risk_position`` and storage, and the all-False
    ``ret_mask`` skips the profit-variance update. The injected row stays NaN
    while a normal preceding row remains finite.
    """
    n = 12
    assets = ["A", "B", "C"]
    rng = np.random.default_rng(0)
    dates = [datetime.date(2020, 1, 1) + datetime.timedelta(days=i) for i in range(n)]
    arr = 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.02, size=(n, len(assets))), axis=0))
    pdata: dict = {"date": dates}
    mdata: dict = {"date": dates}
    for j, a in enumerate(assets):
        vals = arr[:, j].tolist()
        vals[8] = float("nan")  # row 8: every asset missing -> mask all-False
        pdata[a] = vals
        mdata[a] = rng.normal(0.001, 0.01, size=n).tolist()
    prices = pl.DataFrame(pdata).with_columns(pl.col("date").cast(pl.Date))
    mu = pl.DataFrame(mdata).with_columns(pl.col("date").cast(pl.Date))
    eng = Engine(prices=prices, mu=mu, cfg=cfg)

    # Force a finite date (seeds prev_row) followed by the all-NaN date as cor keys.
    forced = {dates[7]: np.eye(len(assets)), dates[8]: np.eye(len(assets))}
    mocker.patch.object(Engine, "cor", new_callable=mocker.PropertyMock, return_value=forced)

    result = eng.cash_position
    assert all(np.isfinite(result[a][7]) for a in assets)  # normal row processed
    assert all(not np.isfinite(result[a][8]) for a in assets)  # degenerate row skipped


def test_cash_position_is_date_aligned_through_latest_row(cfg: Config):
    """Positions are populated across the whole post-warmup range, incl. the last row.

    Regression guard for the date-alignment bug: ``cash_position`` previously paired
    each correlation matrix (keyed by a post-warmup date) with a row offset by
    ``corr`` via positional ``enumerate`` indexing, so the most recent ``corr`` dates
    were always NaN. The matrix for date ``t`` must drive the position stored at ``t``.
    """
    prices, mu, assets = _prices_and_mu(n=40, seed=3)
    eng = Engine(prices=prices, mu=mu, cfg=cfg)
    result = eng.cash_position

    # The final (most recent) row must carry finite positions for every asset.
    last = result.tail(1)
    assert all(np.isfinite(last[a][0]) for a in assets)

    # Finite positions cover exactly the dates present in ``cor`` (the post-warmup
    # range), confirming each cor key maps to its own date rather than an offset.
    finite_dates = set(result.filter(pl.col(assets[0]).is_finite())["date"].to_list())
    assert finite_dates == set(eng.cor.keys())
