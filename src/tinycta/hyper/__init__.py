"""Hyperparameter optimisation support via Optuna.

Public API
----------
- ``run_study``: Convenience wrapper that creates a study and calls ``study.optimize``.
- ``get_config``: Set up logger and config sections for a notebook experiment.
- ``ExperimentConfig``: NamedTuple returned by ``get_config``.

Example::

    from tinycta.hyper import run_study

    study = run_study(objective, prices=prices, assets=assets, n_trials=200)
    print(study.best_params)
"""

from ._setup import ExperimentConfig, get_config
from ._study import run_study

__all__ = [
    "ExperimentConfig",
    "get_config",
    "run_study",
]
