"""Tests for tinycta.hyper.run_study."""

from __future__ import annotations

import math

import numpy as np
import optuna
import polars as pl
import pytest

from tinycta.hyper import run_study
from tinycta.hyper._study import Study, _build_objective, _sharpe, optimize


def _dummy_objective(trial, prices: pl.DataFrame, assets: list[str]) -> float:
    fast = trial.suggest_int("fast", 2, 10)
    slow = trial.suggest_int("slow", fast + 2, 20)
    return float(slow - fast)


def test_run_study_returns_study():
    """run_study returns an optuna.Study with the expected number of trials."""
    study = run_study(_dummy_objective, prices=pl.DataFrame(), assets=["A", "B"], n_trials=2, name="test_study")
    assert isinstance(study, optuna.Study)
    assert len(study.trials) == 2


def test_run_study_best_params():
    """run_study populates best_params with fast and slow, and a finite best_value."""
    study = run_study(_dummy_objective, prices=pl.DataFrame(), assets=["A"], n_trials=3, name="test_best_params")
    assert "fast" in study.best_params
    assert "slow" in study.best_params
    assert math.isfinite(study.best_value)


def test_run_study_without_prices():
    """run_study passes the objective directly when prices/assets are omitted."""
    s = run_study(lambda trial: float(trial.suggest_int("x", 0, 5)), n_trials=2)
    assert isinstance(s, optuna.Study)
    assert len(s.trials) == 2


def test_study_str_no_completed():
    """__str__ returns the no-trials message when n_completed is 0."""
    s = optuna.create_study(direction="maximize")
    study = Study(best_params={}, best_value=float("nan"), n_completed=0, n_trials=0, optuna_study=s)
    assert str(study) == "No completed trials — all returned NaN Sharpe."


def test_study_from_optuna_and_str():
    """from_optuna wraps a completed study; __str__ includes params and Sharpe."""
    s = optuna.create_study(direction="maximize")
    s.optimize(lambda trial: float(trial.suggest_int("x", 0, 5)), n_trials=2)
    study = Study.from_optuna(s)
    assert study.n_completed == 2
    text = str(study)
    assert "x" in text
    assert "Sharpe" in text


def test_sharpe_float_return(mocker):
    """_sharpe returns float when portfolio.stats.sharpe() returns a scalar."""
    portfolio = mocker.MagicMock()
    portfolio.stats.sharpe.return_value = 1.5
    assert _sharpe(portfolio) == 1.5


def test_sharpe_dict_return(mocker):
    """_sharpe extracts 'returns' key when portfolio.stats.sharpe() returns a dict."""
    portfolio = mocker.MagicMock()
    portfolio.stats.sharpe.return_value = {"returns": 2.0}
    assert _sharpe(portfolio) == 2.0


def test_sharpe_raises_on_nan(mocker):
    """_sharpe raises TrialPruned when Sharpe is NaN."""
    portfolio = mocker.MagicMock()
    portfolio.stats.sharpe.return_value = float("nan")
    with pytest.raises(optuna.exceptions.TrialPruned):
        _sharpe(portfolio)


def test_study_plot_writes_html_and_swallows_image_error(mocker, tmp_path):
    """Plot writes HTML for each figure and silently ignores write_image failures."""
    s = optuna.create_study(direction="maximize")
    s.optimize(lambda trial: float(trial.suggest_int("x", 0, 5)), n_trials=1)
    study = Study.from_optuna(s)

    mock_fig = mocker.MagicMock()
    mock_fig.write_image.side_effect = Exception("kaleido not installed")
    for fn in (
        "optuna.visualization.plot_optimization_history",
        "optuna.visualization.plot_param_importances",
        "optuna.visualization.plot_parallel_coordinate",
        "optuna.visualization.plot_contour",
    ):
        mocker.patch(fn, return_value=mock_fig)

    output_dir = tmp_path / "plots"
    study.plot(output_dir)

    assert output_dir.is_dir()
    assert mock_fig.write_html.call_count == 4
    assert mock_fig.write_image.call_count == 4


def test_build_objective_inner_calls_sharpe(mocker):
    """The objective closure built by build_objective passes the portfolio to _sharpe."""
    prices = pl.DataFrame({"date": [1, 2], "A": [1.0, 2.0], "B": [3.0, 4.0]})

    mock_portfolio = mocker.MagicMock()
    mocker.patch("tinycta.hyper._study.Portfolio.from_cash_position", return_value=mock_portfolio)
    mocker.patch("tinycta.hyper._study._sharpe", return_value=1.23)

    def suggest_positions(trial, prices_only):
        return np.zeros((len(prices_only), len(prices_only.columns)))

    objective_fn = _build_objective(prices, suggest_positions)
    result = objective_fn(mocker.MagicMock())

    assert result == 1.23


def test_optimize_returns_frozen_study(mocker):
    """Optimize wraps the optuna study in a frozen Study and returns it."""
    mocker.patch("tinycta.hyper._study.build_objective", return_value=lambda trial: 1.0)

    result = optimize(lambda trial, prices: None, pl.DataFrame(), n_trials=1)

    assert isinstance(result, Study)
    assert result.n_completed == 1
    assert result.best_value == 1.0
