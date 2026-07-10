"""Tests for tinycta.hyper Study and optimize."""

from __future__ import annotations

import dataclasses
import math
import os

import optuna
import pytest

from tinycta.hyper import Study, optimize
from tinycta.hyper._study import _build_objective, _run_study, _sharpe


def _dummy_objective(trial) -> float:
    """Trivial Optuna objective: suggest fast/slow ints and return their gap."""
    fast = trial.suggest_int("fast", 2, 10)
    slow = trial.suggest_int("slow", fast + 2, 20)
    return float(slow - fast)


class _FakeStats:
    """Minimal stand-in for jquantstats stats exposing sharpe()."""

    def __init__(self, value: float | dict) -> None:
        self._value = value

    def sharpe(self) -> float | dict:
        """Return the configured Sharpe value (scalar or ``{'returns': ...}``)."""
        return self._value


class _FakePortfolio:
    """Lightweight Portfolio stand-in so tests exercise the real _sharpe logic.

    Prefer this over ``MagicMock`` for the Sharpe/objective/optimize paths: a real
    object with a fixed contract asserts behaviour and returned values rather than
    auto-vivifying attributes and pinning internal call order.
    """

    def __init__(self, sharpe_value: float | dict) -> None:
        self.stats = _FakeStats(sharpe_value)


def test_run_study_returns_optuna_study():
    """_run_study returns an optuna.Study with the expected number of trials."""
    study = _run_study(_dummy_objective, n_trials=2, name="test_study")
    assert isinstance(study, optuna.Study)
    assert len(study.trials) == 2


def test_run_study_best_params():
    """_run_study populates best_params with fast and slow, and a finite best_value."""
    study = _run_study(_dummy_objective, n_trials=3, name="test_best_params")
    assert "fast" in study.best_params
    assert "slow" in study.best_params
    assert math.isfinite(study.best_value)


def test_run_study_simple_objective():
    """_run_study runs a simple scalar-returning objective."""
    s = _run_study(lambda trial: float(trial.suggest_int("x", 0, 5)), n_trials=2)
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


def test_sharpe_float_return():
    """_sharpe returns float when portfolio.stats.sharpe() returns a scalar."""
    assert _sharpe(_FakePortfolio(1.5)) == 1.5


def test_sharpe_dict_return():
    """_sharpe extracts 'returns' key when portfolio.stats.sharpe() returns a dict."""
    assert _sharpe(_FakePortfolio({"returns": 2.0})) == 2.0


def test_sharpe_raises_on_nan():
    """_sharpe raises TrialPruned when Sharpe is NaN."""
    with pytest.raises(optuna.exceptions.TrialPruned):
        _sharpe(_FakePortfolio(float("nan")))


def test_study_plot_writes_html_and_swallows_image_error(mocker, tmp_path):
    """Plot writes HTML for each figure and skips write_image failures (missing kaleido)."""
    s = optuna.create_study(direction="maximize")
    s.optimize(lambda trial: float(trial.suggest_int("x", 0, 5)), n_trials=1)
    study = Study.from_optuna(s)

    mock_fig = mocker.MagicMock()
    # plotly raises ValueError when the optional kaleido image backend is missing.
    mock_fig.write_image.side_effect = ValueError("kaleido not installed")
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


def test_build_objective_scores_portfolio_with_sharpe():
    """The objective from _build_objective scores its portfolio's real Sharpe.

    Runs the objective through a real optuna study (no patched internals) so the
    _build_objective -> _sharpe chain is exercised end to end.
    """
    study = optuna.create_study(direction="maximize")
    study.optimize(_build_objective(lambda trial: _FakePortfolio(1.23)), n_trials=1)
    assert study.best_value == 1.23


def test_from_optuna_no_completed_trials():
    """from_optuna sets best_params={} and best_value=nan when all trials are pruned."""
    s = optuna.create_study(direction="maximize")
    s.optimize(lambda trial: (_ for _ in ()).throw(optuna.exceptions.TrialPruned()), n_trials=2)
    study = Study.from_optuna(s)
    assert study.n_completed == 0
    assert study.best_params == {}
    assert math.isnan(study.best_value)


def test_optimize_returns_frozen_study():
    """Optimize runs the real objective chain and wraps the result in a frozen Study."""
    result = optimize(lambda trial: _FakePortfolio(1.0), n_trials=1)

    assert isinstance(result, Study)
    assert result.n_completed == 1
    assert result.best_value == 1.0


# --------------------------------------------------------------------------- #
# Mutation-killing tests: pin structure, formatting and defaults exactly.
# --------------------------------------------------------------------------- #
def _completed_study(best_params: dict, best_value: float, n_completed: int, n_trials: int) -> Study:
    """Build a Study with explicit fields and a real (empty) optuna study."""
    return Study(
        best_params=best_params,
        best_value=best_value,
        n_completed=n_completed,
        n_trials=n_trials,
        optuna_study=optuna.create_study(direction="maximize"),
    )


def test_study_is_frozen():
    """Study is an immutable (frozen) dataclass."""
    study = _completed_study({"fast": 3}, 1.0, 1, 1)
    with pytest.raises(dataclasses.FrozenInstanceError):
        study.best_value = 2.0  # ty: ignore[invalid-assignment]


def test_optuna_study_excluded_from_repr():
    """The optuna_study field is hidden from repr (field(repr=False))."""
    study = _completed_study({"fast": 3}, 1.0, 1, 1)
    assert "optuna_study" not in repr(study)


def test_optuna_study_is_a_required_field():
    """optuna_study has no default; constructing without it raises TypeError."""
    with pytest.raises(TypeError):
        Study(best_params={}, best_value=1.0, n_completed=1, n_trials=1)  # ty: ignore[missing-argument]


def test_str_completed_is_exact():
    """__str__ formatting (labels, Sharpe precision, newline join) is exact."""
    study = _completed_study({"fast": 3, "slow": 9}, 1.2345, 2, 3)
    expected = "\n".join(
        [
            "=== Best parameters ===",
            f"  {'fast':<12} = {3}",
            f"  {'slow':<12} = {9}",
            f"  {'Sharpe':<12} = {1.2345:.4f}",
            f"  {'Completed':<12} = {2} / {3} trials",
        ]
    )
    assert str(study) == expected


def test_plot_creates_nested_dirs_and_overwrites(mocker, tmp_path):
    """Plot creates parent dirs (parents=True) and tolerates an existing dir (exist_ok=True)."""
    s = optuna.create_study(direction="maximize")
    s.optimize(lambda trial: float(trial.suggest_int("x", 0, 5)), n_trials=1)
    study = Study.from_optuna(s)

    mock_fig = mocker.MagicMock()
    for fn in (
        "optuna.visualization.plot_optimization_history",
        "optuna.visualization.plot_param_importances",
        "optuna.visualization.plot_parallel_coordinate",
        "optuna.visualization.plot_contour",
    ):
        mocker.patch(fn, return_value=mock_fig)

    nested = tmp_path / "deep" / "plots"  # parent "deep" does not exist yet -> needs parents=True
    study.plot(nested)
    study.plot(nested)  # second call into the existing dir -> needs exist_ok=True
    assert nested.is_dir()


def test_plot_uses_expected_filenames_and_scale(mocker, tmp_path):
    """Figure keys map to exact .html/.png filenames and PNG uses scale=2."""
    s = optuna.create_study(direction="maximize")
    s.optimize(lambda trial: float(trial.suggest_int("x", 0, 5)), n_trials=1)
    study = Study.from_optuna(s)

    mock_fig = mocker.MagicMock()
    for fn in (
        "optuna.visualization.plot_optimization_history",
        "optuna.visualization.plot_param_importances",
        "optuna.visualization.plot_parallel_coordinate",
        "optuna.visualization.plot_contour",
    ):
        mocker.patch(fn, return_value=mock_fig)

    output_dir = tmp_path / "plots"
    study.plot(output_dir)

    html_names = {os.path.basename(p[0][0]) for p in mock_fig.write_html.call_args_list}
    assert html_names == {
        "optuna_history.html",
        "optuna_importance.html",
        "optuna_parallel.html",
        "optuna_contour.html",
    }
    png_names = {os.path.basename(c.args[0]) for c in mock_fig.write_image.call_args_list}
    assert png_names == {
        "optuna_history.png",
        "optuna_importance.png",
        "optuna_parallel.png",
        "optuna_contour.png",
    }
    for c in mock_fig.write_image.call_args_list:
        assert c.kwargs["scale"] == 2


def test_plot_logs_exact_message_on_image_failure(mocker, tmp_path):
    """The PNG-export failure is logged with the exact (unwrapped) debug message."""
    from loguru import logger

    s = optuna.create_study(direction="maximize")
    s.optimize(lambda trial: float(trial.suggest_int("x", 0, 5)), n_trials=1)
    study = Study.from_optuna(s)

    mock_fig = mocker.MagicMock()
    mock_fig.write_image.side_effect = ValueError("kaleido not installed")
    for fn in (
        "optuna.visualization.plot_optimization_history",
        "optuna.visualization.plot_param_importances",
        "optuna.visualization.plot_parallel_coordinate",
        "optuna.visualization.plot_contour",
    ):
        mocker.patch(fn, return_value=mock_fig)

    captured: list[str] = []
    sink_id = logger.add(captured.append, level="DEBUG", format="{message}")
    try:
        study.plot(tmp_path / "plots")
    finally:
        logger.remove(sink_id)

    messages = [m.strip() for m in captured]
    assert "Skipping PNG export for optuna_history: kaleido not installed" in messages


def test_run_study_default_n_trials_is_100():
    """_run_study defaults to 100 trials."""
    study = _run_study(lambda trial: float(trial.suggest_int("x", 0, 5)), name="defaults_n")
    assert len(study.trials) == 100


def test_run_study_default_seed_is_42():
    """_run_study defaults to seed 42 (identical sampling sequence to explicit 42)."""
    obj = lambda trial: float(trial.suggest_int("x", 0, 100))  # noqa: E731
    default = _run_study(obj, n_trials=12, name="seed_default")
    explicit = _run_study(obj, n_trials=12, seed=42, name="seed_explicit")
    assert [t.params for t in default.trials] == [t.params for t in explicit.trials]


def test_run_study_disables_progress_bar(mocker):
    """_run_study calls optimize with show_progress_bar=False."""
    fake_study = mocker.MagicMock()
    mocker.patch("optuna.create_study", return_value=fake_study)
    _run_study(lambda trial: 1.0, n_trials=1)
    assert fake_study.optimize.call_args.kwargs["show_progress_bar"] is False


def test_optimize_default_n_trials_is_100():
    """Optimize defaults to 100 trials."""
    result = optimize(lambda trial: _FakePortfolio(1.0))
    assert result.n_trials == 100


def test_optimize_default_seed_is_42():
    """Optimize defaults to seed 42 (identical sampling sequence to explicit 42)."""
    fn = lambda trial: _FakePortfolio(float(trial.suggest_int("x", 0, 100)))  # noqa: E731
    default = optimize(fn, n_trials=12)
    explicit = optimize(fn, n_trials=12, seed=42)
    seqs_default = [t.params for t in default.optuna_study.trials]
    seqs_explicit = [t.params for t in explicit.optuna_study.trials]
    assert seqs_default == seqs_explicit


def test_optimize_logs_the_study():
    """Optimize logs the Study summary (not None) before returning."""
    from loguru import logger

    captured: list[str] = []
    sink_id = logger.add(captured.append, level="INFO", format="{message}")
    try:
        optimize(lambda trial: _FakePortfolio(1.0), n_trials=1)
    finally:
        logger.remove(sink_id)
    assert any("=== Best parameters ===" in message for message in captured)
