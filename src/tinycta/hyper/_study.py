"""Frozen Study result and Optuna-based hyperparameter optimisation."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import optuna
from jquantstats import Portfolio
from loguru import logger


@dataclass(frozen=True)
class Study:
    """Frozen wrapper around a completed Optuna study.

    Example:
        >>> import optuna
        >>> from tinycta.hyper import Study
        >>> optuna.logging.set_verbosity(optuna.logging.WARNING)
        >>> s = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=0))
        >>> s.optimize(lambda trial: trial.suggest_float("x", 0.0, 1.0), n_trials=5)
        >>> study = Study.from_optuna(s)
        >>> study.n_trials, study.n_completed
        (5, 5)
        >>> sorted(study.best_params)
        ['x']

        ``str`` renders the best trial as a report block:

        >>> print(study)  # doctest: +ELLIPSIS
        === Best parameters ===
          x            = 0...
          Sharpe       = 0...
          Completed    = 5 / 5 trials

        A study in which every trial was pruned (each scored a NaN Sharpe) is not an
        error — it reports no best parameters and a NaN best value:

        >>> pruned = optuna.create_study(direction="maximize")
        >>> pruned.optimize(
        ...     lambda trial: (_ for _ in ()).throw(optuna.exceptions.TrialPruned()), n_trials=2
        ... )
        >>> empty = Study.from_optuna(pruned)
        >>> empty.n_completed, empty.best_params
        (0, {})
        >>> print(empty)
        No completed trials — all returned NaN Sharpe.
    """

    best_params: dict[str, Any]
    best_value: float
    n_completed: int
    n_trials: int
    optuna_study: optuna.Study = field(repr=False)

    def __str__(self) -> str:
        """Return a human-readable summary of the best trial."""
        if self.n_completed == 0:
            return "No completed trials — all returned NaN Sharpe."
        lines = ["=== Best parameters ==="]
        for k, v in self.best_params.items():
            lines.append(f"  {k:<12} = {v}")
        lines.append(f"  {'Sharpe':<12} = {self.best_value:.4f}")
        lines.append(f"  {'Completed':<12} = {self.n_completed} / {self.n_trials} trials")
        return "\n".join(lines)

    @classmethod
    def from_optuna(cls, s: optuna.Study) -> Study:
        """Wrap a completed optuna.Study in a frozen Study."""
        n_completed = sum(1 for t in s.trials if t.state == optuna.trial.TrialState.COMPLETE)
        if n_completed == 0:
            best_params, best_value = {}, float("nan")
        else:
            best_params, best_value = s.best_params, s.best_value
        return cls(
            best_params=best_params,
            best_value=best_value,
            n_completed=n_completed,
            n_trials=len(s.trials),
            optuna_study=s,
        )

    def plot(self, output_dir: Path) -> None:
        """Write Optuna visualisation plots to output_dir (HTML, PNG if kaleido available)."""
        output_dir.mkdir(parents=True, exist_ok=True)
        figures = {
            "optuna_history": optuna.visualization.plot_optimization_history(self.optuna_study),
            "optuna_importance": optuna.visualization.plot_param_importances(self.optuna_study),
            "optuna_parallel": optuna.visualization.plot_parallel_coordinate(self.optuna_study),
            "optuna_contour": optuna.visualization.plot_contour(self.optuna_study),
        }
        for name, fig in figures.items():
            fig.write_html(str(output_dir / f"{name}.html"))
            try:
                fig.write_image(str(output_dir / f"{name}.png"), scale=2)
            except (ValueError, ImportError) as exc:
                # PNG export needs the optional `kaleido` backend; skip if unavailable.
                logger.debug(f"Skipping PNG export for {name}: {exc}")


def _sharpe(portfolio: Portfolio) -> float:
    """Compute Sharpe ratio, raising TrialPruned if the result is NaN or None."""
    result = portfolio.stats.sharpe()
    sharpe = result["returns"] if isinstance(result, dict) else float(result)
    if sharpe is None or sharpe != sharpe:
        raise optuna.exceptions.TrialPruned()
    return sharpe


def _run_study(
    objective: Callable[[optuna.Trial], float],
    *,
    n_trials: int = 100,
    seed: int = 42,
    name: str | None = None,
) -> optuna.Study:
    """Create and run an Optuna study, returning the optuna.Study."""
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    s = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed), study_name=name)
    s.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    return s


def _build_objective(
    suggest_portfolio_fn: Callable[[optuna.Trial], Portfolio],
) -> Callable[[optuna.Trial], float]:
    """Objective factory: wraps a portfolio-returning function with Sharpe scoring."""

    def objective(trial: optuna.Trial) -> float:
        """Call suggest_portfolio_fn and return the Sharpe ratio."""
        return _sharpe(suggest_portfolio_fn(trial))

    return objective


def optimize(
    suggest_portfolio_fn: Callable[[optuna.Trial], Portfolio],
    n_trials: int = 100,
    seed: int = 42,
) -> Study:
    """Build objective, run study, log the summary and return a frozen Study.

    ``suggest_portfolio_fn`` draws its parameters from the trial and returns a
    portfolio; the trial is then scored by that portfolio's Sharpe ratio, which
    the study maximises. A trial whose Sharpe is NaN is pruned rather than fatal.

    Example:
        >>> from types import SimpleNamespace
        >>> from tinycta.hyper import optimize

        Any object exposing ``.stats.sharpe()`` works here; in real use that is a
        ``jquantstats`` ``Portfolio`` built from the strategy's returns:

        >>> def portfolio(sharpe):
        ...     return SimpleNamespace(stats=SimpleNamespace(sharpe=lambda: sharpe))

        The objective is maximised, so the best value is the highest Sharpe seen —
        here the reward peaks where ``fast`` is largest:

        >>> study = optimize(lambda trial: portfolio(trial.suggest_int("fast", 1, 8)), n_trials=12)
        >>> study.best_value
        8.0
        >>> study.best_params
        {'fast': 8}

        Runs are seeded, so the same objective and seed reproduce the same result:

        >>> repeat = optimize(lambda trial: portfolio(trial.suggest_int("fast", 1, 8)), n_trials=12)
        >>> repeat.best_params == study.best_params
        True
    """
    s = _run_study(_build_objective(suggest_portfolio_fn), n_trials=n_trials, seed=seed)
    study = Study.from_optuna(s)
    logger.info(str(study))
    return study
