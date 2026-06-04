"""Frozen Study result and Optuna-based hyperparameter optimisation."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from pathlib import Path

import optuna
from jquantstats import Portfolio


@dataclass(frozen=True)
class Study:
    """Frozen wrapper around a completed Optuna study."""

    best_params: dict
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
            with contextlib.suppress(Exception):
                fig.write_image(str(output_dir / f"{name}.png"), scale=2)


def _sharpe(portfolio: Portfolio) -> float:
    """Compute Sharpe ratio, raising TrialPruned if the result is NaN or None."""
    result = portfolio.stats.sharpe()
    sharpe = result["returns"] if isinstance(result, dict) else float(result)
    if sharpe is None or sharpe != sharpe:
        raise optuna.exceptions.TrialPruned()
    return sharpe


def _run_study(
    objective,
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


def _build_objective(suggest_portfolio_fn):
    """Objective factory: wraps a portfolio-returning function with Sharpe scoring."""

    def objective(trial: optuna.Trial) -> float:
        return _sharpe(suggest_portfolio_fn(trial))

    return objective


def optimize(suggest_portfolio_fn, n_trials: int = 100, seed: int = 42) -> Study:
    """Build objective, run study, print and return a frozen Study."""
    s = _run_study(_build_objective(suggest_portfolio_fn), n_trials=n_trials, seed=seed)
    study = Study.from_optuna(s)
    print(study)
    return study
