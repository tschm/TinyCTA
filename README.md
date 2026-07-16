# 📈 [TinyCTA](https://tschm.github.io/TinyCTA/)

A Lightweight Python Package for Commodity Trading Advisor Strategies.

[![PyPI version](https://badge.fury.io/py/tinycta.svg)](https://badge.fury.io/py/tinycta)
[![MIT License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://github.com/tschm/TinyCTA/blob/main/LICENSE)
[![Coverage](https://tschm.github.io/TinyCTA/coverage-badge.svg)](https://tschm.github.io/TinyCTA/reports/html-coverage/index.html)
[![Downloads](https://static.pepy.tech/personalized-badge/tinycta?period=month&units=international_system&left_color=black&right_color=orange&left_text=PyPI%20downloads%20per%20month)](https://pepy.tech/project/tinycta)
[![CodeFactor](https://www.codefactor.io/repository/github/tschm/TinyCTA/badge)](https://www.codefactor.io/repository/github/tschm/TinyCTA)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/tschm/TinyCTA/badge)](https://scorecard.dev/viewer/?uri=github.com/tschm/TinyCTA)
[![Rhiza](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2Ftschm%2FTinyCTA%2Fmain%2F.rhiza%2Ftemplate.yml&query=%24.ref&label=rhiza&color=blue)](https://github.com/jebel-quant/rhiza)

---

**Quick Links:** [📚 Repository](https://github.com/tschm/TinyCTA) • [📦 PyPI](https://pypi.org/project/tinycta/) • [🐛 Issues](https://github.com/tschm/TinyCTA/issues) • [💬 Discussions](https://github.com/tschm/TinyCTA/discussions)

---

## 📋 Overview

TinyCTA provides essential tools for quantitative finance and algorithmic trading,
particularly for trend-following strategies. The package includes:

- Polars-based signal processing: oscillators, moving-average crossovers, and volatility-adjusted returns
- Robust volatility estimation via rolling median absolute deviation
- Linear algebra utilities that handle matrices with missing values
- Matrix shrinkage techniques commonly used in portfolio optimization

This package is designed to be the foundation for implementing CTA strategies
in just a few lines of code, hence the name "TinyCTA".

📖 New here? Follow the [end-to-end CTA tutorial](https://tschm.github.io/TinyCTA/tutorial/)
to go from raw prices through signals and the `Engine` to cash positions.

## 🚀 Installation

### Using pip

```bash
pip install tinycta
```

The core install keeps a minimal dependency footprint (numpy, polars, pydantic, cvx-linalg).
The optional Optuna-based hyperparameter-optimisation layer (`tinycta.hyper`) is installed via
the `hyper` extra:

```bash
pip install "tinycta[hyper]"
```

### From source

Clone the repository and install using the provided Makefile:

```bash
git clone https://github.com/tschm/tinycta.git
cd tinycta
make install
```

This will install [uv](https://github.com/astral-sh/uv)
(a fast Python package installer) and create a
virtual environment with all dependencies.

## 💻 Usage

### Oscillator signal (Polars)

```python
import polars as pl
from tinycta.osc import osc

prices = pl.DataFrame({"A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
result = prices.with_columns(osc(pl.col("A"), fast=2, slow=6).alias("osc_A"))
```

### Moving-average crossover (Polars)

```python
import polars as pl
from tinycta.ewma import ma_cross

prices = pl.DataFrame({"A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
result = prices.with_columns(
    ma_cross(pl.col("A"), fast=2, slow=6).alias("sig_A")
)
```

### Volatility-adjusted returns (Polars)

```python
import polars as pl
from tinycta.util import vol_adj, adj_log_prices

prices = pl.DataFrame({"A": [100, 101, 99, 102, 98, 103]})
result = prices.with_columns(
    vol_adj(pl.col("A"), vola=3, clip=4.2).alias("vol_adj_A"),
    adj_log_prices(pl.col("A"), vola=3, clip=4.2).alias("adj_log_A"),
)
```

### Linear algebra operations

```python
import numpy as np
from tinycta.linalg import solve

matrix = np.array([[1.0, 0.5], [0.5, 1.0]])
rhs = np.array([1.0, 2.0])
solution = solve(matrix, rhs)
print(np.round(solution, 10) + 0)
```

```result
[0. 2.]
```

### Position-sizing engine

The `Engine` turns aligned price and expected-return (`mu`) frames into
correlation-shrinkage-optimized cash positions. It is configured by a validated `Config`.

```python
import polars as pl
from tinycta.config import Config
from tinycta.engine import Engine

dates = list(range(1, 9))
prices = pl.DataFrame({"date": dates, "A": [100.0, 101.0, 102.0, 101.5, 103.0, 104.0, 103.5, 105.0]})
mu = pl.DataFrame({"date": dates, "A": [0.0, 0.1, 0.2, 0.1, 0.2, 0.3, 0.2, 0.3]})

cfg = Config(vola=3, corr=3, clip=4.2, shrink=0.5)
positions = Engine(prices=prices, mu=mu, cfg=cfg).cash_position

# .cash_position mirrors the input frame: one row per date, one column per asset.
print(sorted(positions.columns))
print(positions.shape)
```

```result
['A', 'date']
(8, 2)
```

`Config` is a frozen Pydantic model: `vola`, `corr` (must be `>= vola`) and `clip` must be
positive, and `shrink` must lie in `[0, 1]`.

### Hyperparameter optimization

`tinycta.hyper.optimize` runs an Optuna study over a function that builds a portfolio from a
trial and scores it by Sharpe ratio, returning a frozen `Study`.

```python +RHIZA_SKIP
from tinycta.hyper import optimize

def suggest_portfolio(trial):
    fast = trial.suggest_int("fast", 2, 20)
    slow = trial.suggest_int("slow", fast + 1, 100)
    # ... build and return a jquantstats Portfolio from the suggested params ...
    return build_portfolio(fast, slow)

study = optimize(suggest_portfolio, n_trials=100, seed=42)
print(study.best_params, study.best_value)
```

### Experiment setup (`get_config`)

`tinycta.hyper.get_config` bundles the config sections and a configured logger for a notebook
experiment. It reads a shared `config.yml` and, for an experiment named `name`, an optional
experiment-specific `config/{name}.yml`; each `data` / `params` / `optuna` section is taken from
`config.yml` when present, otherwise from the sibling file. All three sections are optional.

```yaml
# config.yml — every section is optional
data:
  output_path: output   # output dir, relative to the notebooks directory (default: "output")
params:
  fast: 12              # arbitrary experiment parameters
optuna:
  n_trials: 100         # arbitrary Optuna settings
```

Paths resolve relative to the **notebooks directory** — the parent of `config.yml`, or its
grandparent when `config.yml` lives inside a `config/` subdirectory. Outputs are written to
`{notebooks}/{output_path}/{name}/`, and a config-supplied `output_path` is confined to the
notebooks directory (a traversing or absolute path raises `ValueError`). Set the
`NOTEBOOK_OUTPUT_FOLDER` environment variable to override the output directory entirely — this
explicit operator override is trusted and not confined.

```python +RHIZA_SKIP
from tinycta.hyper import get_config

cfg = get_config("my_experiment")            # reads ./config.yml (+ ./config/my_experiment.yml)
cfg.logger.info("run starting")              # loguru logger, also writing to output.log
fast = cfg.params["fast"]                    # config sections as plain dicts
```

## 📚 API Reference

### Signal Processing (`tinycta.osc`, `tinycta.ewma`, `tinycta.util`)

- `osc(x, fast, slow, min_samples=1)` — analytically scaled EWMA-difference oscillator (Polars)
- `ma_cross(prices, fast, slow, min_samples=1)` — sign of fast-vs-slow EWM crossover: -1, 0, or +1 (Polars)
- `vol_adj(x, vola, clip, min_samples=1)` — clipped, volatility-adjusted log returns (Polars)
- `adj_log_prices(x, vola, clip, min_samples=1)` — cumulative sum of volatility-adjusted log returns (Polars)

### Signal Utilities (`tinycta.signal`)

- `moving_absolute_deviation(price, com=32)` — robust rolling volatility estimate via median absolute deviation (Polars)
- `shrink2id(matrix, lamb=1.0)` — shrink a matrix towards the identity matrix

### Linear Algebra (`tinycta.linalg`)

- `valid(matrix)` — extract the finite subset of a matrix by filtering NaN rows/columns
- `a_norm(vector, matrix=None)` — matrix-norm of a vector
- `inv_a_norm(vector, matrix=None)` — inverse matrix-norm of a vector
- `solve(matrix, rhs)` — solve a linear system, handling matrices with NaN values

### Position-Sizing Engine (`tinycta.engine`, `tinycta.config`)

- `Config(vola, corr, clip, shrink)` — frozen Pydantic config; `corr >= vola`, `vola`/`corr`/`clip > 0`, `shrink ∈ [0, 1]`
- `Engine(prices, mu, cfg)` — correlation-aware position optimizer; `.cash_position` returns per-asset cash positions
  - `.assets`, `.ret_adj`, `.vola`, `.cor` — intermediate per-asset/per-timestamp quantities

### Hyperparameter Optimization (`tinycta.hyper`)

- `optimize(suggest_portfolio_fn, n_trials=100, seed=42)` — run an Optuna study scored by Sharpe; returns a `Study`
- `Study` — frozen result wrapper exposing `best_params`, `best_value`, `n_completed`, `n_trials`, and `.plot(output_dir)`
- `get_config(name, config_path=None)` — load merged `data`/`params`/`optuna` sections and a configured logger; returns an `ExperimentConfig`
- `ExperimentConfig` — `NamedTuple` bundling `name`, `logger`, and the optional `params`, `optuna` and `data` sections

## 🛠️ Development

### Setting up the development environment

```bash
make install
```

### Running tests

```bash
make test
```

### Code formatting and linting

```bash
make fmt
```

### Cleaning up

```bash
make clean
```

## 📄 License

TinyCTA is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
