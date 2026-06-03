"""Hyperparameter optimisation support via Optuna.

Public API
----------
- ``Study``: Frozen dataclass wrapping a completed Optuna study.
- ``optimize``: Convenience wrapper: build objective, run study, print, return ``Study``.
- ``get_config``: Set up logger and config sections for a notebook experiment.
- ``ExperimentConfig``: NamedTuple returned by ``get_config``.
"""

from ._setup import ExperimentConfig, get_config
from ._study import Study, optimize

__all__ = [
    "ExperimentConfig",
    "Study",
    "get_config",
    "optimize",
]
