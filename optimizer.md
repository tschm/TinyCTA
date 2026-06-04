# Hyperparameter Optimisation with `tinycta.hyper`

The `tinycta.hyper` module provides a thin wrapper around [Optuna](https://optuna.org/) for tuning the parameters of a CTA position-suggestion function against historical prices. The objective metric is the **Sharpe ratio** of the resulting portfolio, computed via `jquantstats`.

---

## Public API

```python
from tinycta.hyper import Study, optimize, get_config, ExperimentConfig
```

| Symbol | Kind | Purpose |
|---|---|---|
| `optimize` | function | Run an Optuna study and return a frozen `Study`. |
| `Study` | dataclass | Immutable result of a completed study. |
| `get_config` | function | Load YAML config and initialise a file-based logger. |
| `ExperimentConfig` | NamedTuple | Bundle returned by `get_config`. |

---

## Core workflow

### 1. Write a position-suggestion function

The function receives an `optuna.Trial` (for sampling hyperparameters) and a Polars DataFrame of prices (float columns only), and must return a NumPy array of positions with shape `(n_dates, n_assets)`.

```python
import numpy as np

def suggest_positions(trial, prices):
    fast = trial.suggest_int("fast", 2, 50)
    slow = trial.suggest_int("slow", fast + 5, 200)
    # … compute signals using fast/slow …
    return positions  # np.ndarray, shape (n_dates, n_assets)
```

### 2. Run the optimiser

```python
import polars as pl
from tinycta.hyper import optimize

prices = pl.read_parquet("prices.parquet")  # must include a date column

study = optimize(suggest_positions, prices, n_trials=200, seed=42)
```

`optimize` returns a frozen `Study` and prints a summary to stdout.

### 3. Inspect results

```python
print(study)
# === Best parameters ===
#   fast         = 12
#   slow         = 48
#   Sharpe       = 0.8731
#   Completed    = 187 / 200 trials

print(study.best_params)   # {'fast': 12, 'slow': 48}
print(study.best_value)    # 0.8731
print(study.n_completed)   # number of non-pruned trials
```

### 4. Save diagnostic plots

```python
from pathlib import Path

study.plot(Path("output/my_strategy"))
```

Four interactive HTML files are written (PNG if `kaleido` is installed):

| File | Content |
|---|---|
| `optuna_history.html` | Objective value per trial |
| `optuna_importance.html` | Parameter importances |
| `optuna_parallel.html` | Parallel-coordinate view |
| `optuna_contour.html` | Parameter interaction contours |

---

## Optimiser internals

### Sampler

Optuna's **TPE (Tree-structured Parzen Estimator)** sampler is used. TPE is a sequential model-based algorithm that builds separate density models for good and bad trials and samples from the region likely to improve the objective. It is efficient for moderate-dimensional search spaces (< ~20 parameters) and handles mixed integer/float/categorical types natively.

Key settings (hardcoded defaults, overridable via `_run_study`):

| Setting | Value |
|---|---|
| Direction | `maximize` (Sharpe ratio) |
| Sampler | `TPESampler(seed=seed)` |
| Default trials | 100 |
| Default seed | 42 |

### Trial pruning

Trials that produce a `NaN` or `None` Sharpe ratio are pruned via `optuna.exceptions.TrialPruned` rather than treated as failures. This keeps the study statistics clean — pruned trials are excluded from `n_completed` and do not influence `best_params`/`best_value`.

### Price/position contract

Inside `_build_objective`:

- Float columns in the prices DataFrame are treated as asset prices.
- Non-float columns (e.g. a `date` column) are forwarded unchanged to `Portfolio.from_cash_position`.
- The suggestion function receives only the float sub-DataFrame (`prices_only`).
- Positions are wrapped in a Polars DataFrame with the same asset columns before being passed to the portfolio constructor.

---

## Experiment configuration (`get_config`)

For notebook-driven experiments, `get_config` loads a YAML file and returns an `ExperimentConfig` with four sections:

```python
from tinycta.hyper import get_config

cfg = get_config("my_experiment", config_path="config/my_experiment.yml")

cfg.logger.info("Starting run")
n_trials = cfg.optuna.get("n_trials", 100)
```

YAML layout (shared `config.yml` or per-experiment `config/{name}.yml`):

```yaml
data:
  output_path: output        # relative to notebook dir; overridden by $NOTEBOOK_OUTPUT_FOLDER
params:
  # arbitrary strategy parameters
optuna:
  n_trials: 200
```

The logger writes to `<output_dir>/output.log`. The file sink is registered once per path, so calling `get_config` multiple times in the same process is safe.

---

## Reproducibility

Pass an explicit `seed` to `optimize` (default `42`). The TPE sampler is seeded, so the same `(suggest_positions_fn, prices, n_trials, seed)` combination produces identical trial sequences across runs.

```python
study = optimize(suggest_positions, prices, n_trials=200, seed=0)
```

---

## Dependencies

| Package | Role |
|---|---|
| `optuna` | Bayesian optimisation engine |
| `polars` | Price DataFrame format |
| `jquantstats` | Portfolio construction and Sharpe computation |
| `loguru` | Structured file logging in `get_config` |
| `pyyaml` | YAML config loading |
