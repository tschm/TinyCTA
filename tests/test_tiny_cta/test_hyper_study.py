"""Tests for tinycta.hyper.run_study."""

from __future__ import annotations

import math

import optuna
import polars as pl

from tinycta.hyper import run_study


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
