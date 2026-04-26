"""Study runner for Optuna-based hyperparameter optimisation."""

from __future__ import annotations

import functools
from collections.abc import Callable

import optuna
import polars as pl


def run_study(
    objective: Callable,
    prices: pl.DataFrame,
    assets: list[str],
    n_trials: int = 200,
    storage: str | None = None,
    name: str = "study",
    direction: str = "maximize",
) -> optuna.Study:
    """Create an Optuna study and optimise the given objective.

    Args:
        objective: Callable with signature ``(trial, prices, assets) -> float``.
        prices: Wide price frame passed through to the objective unchanged.
        assets: Asset list passed through to the objective unchanged.
        n_trials: Number of optimisation trials.
        storage: Optuna storage URL (e.g. ``"sqlite:///optuna.db"``). Defaults to in-memory.
        name: Study name passed to ``optuna.create_study``.
        direction: Optimisation direction (``"maximize"`` or ``"minimize"``).

    Returns:
        The completed ``optuna.Study`` with ``best_params`` and ``best_value`` populated.
    """
    study = optuna.create_study(direction=direction, storage=storage, study_name=name)
    obj = functools.partial(objective, prices=prices, assets=assets)
    study.optimize(obj, n_trials=n_trials)
    return study
