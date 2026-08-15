# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TinyCTA is a lightweight Python package for Commodity Trading Advisor (CTA) strategies. It provides
Polars-based signal-processing expressions for trend-following strategies, a correlation-aware
position-sizing engine, linear-algebra utilities that handle matrices with missing values, and an
Optuna-based hyperparameter-optimisation layer.

## Development Commands

The project uses `make` and `uv` for development. Key commands:

```bash
make install    # Install uv, create .venv, install dependencies
make test       # Run pytest with coverage (outputs to _tests/)
make fmt        # Run pre-commit hooks (ruff format, ruff check --fix)
make deps       # Check for missing/unused dependencies (deptry)
make marimo     # Start Marimo notebook server
```

To run a single test file:
```bash
uv run pytest tests/tinycta/test_osc.py
```

To run a specific test:
```bash
uv run pytest tests/tinycta/test_osc.py::test_name -v
```

## Project Structure

- `src/tinycta/` - Main package source code
  - `osc.py` - `osc()` analytically scaled EWMA-difference oscillator (Polars expression)
  - `ewma.py` - `ma_cross()` sign of a fast-vs-slow EWM moving-average crossover (Polars expression)
  - `util.py` - `vol_adj()` and `adj_log_prices()` volatility-adjusted log returns (Polars expressions)
  - `signal.py` - `moving_absolute_deviation()` robust rolling volatility and `shrink2id()` matrix shrinkage
  - `linalg.py` - re-exports `valid()`, `a_norm()`, `inv_a_norm()`, `solve()` from `cvx.linalg`
  - `ewm_cov.py` - re-exports `ewm_covariance()` and `NegativeWarmupError` from `cvx.linalg.ewm_cov`
  - `config.py` - `Config`, a frozen Pydantic model validating the engine parameters
  - `engine.py` - `Engine`, the correlation-aware risk/cash position optimizer ("Basanos" engine);
    the Polars-facing orchestration layer
  - `_kernel.py` - private pure-NumPy numeric kernel: `forward_walk()` and the per-timestamp
    helpers `_risk_position()`, `_update_profit_variance()`, `_denominator_is_degenerate()`
  - `hyper/` - Optuna-based hyperparameter optimisation
    - `_study.py` - frozen `Study` result wrapper and `optimize()` entry point
    - `_setup.py` - `get_config()` / `ExperimentConfig` notebook experiment setup helpers
- `tests/tinycta/` - Package tests
- `tests/property/` - Hypothesis property-based tests
- `.rhiza/tests/` - Rhiza framework infrastructure tests
- `book/` - Documentation source
- `.rhiza/` - Rhiza framework scripts and configurations

## Architecture Notes

The package is organised in three layers:

1. **Signal expressions** (`osc.py`, `ewma.py`, `util.py`, `signal.py`) - composable Polars
   expressions for use inside `DataFrame.with_columns`. They build on `ewm_mean`/`ewm_std` and
   operate column-wise. `signal.py` additionally provides a pandas-free robust volatility estimate
   (median absolute deviation) and identity-shrinkage of a matrix.

2. **Linear algebra** (`linalg.py`, `ewm_cov.py`) - thin re-exports of `cvx.linalg`. These operations
   tolerate NaN values: `valid()` extracts the finite subset of a matrix, and `a_norm`, `inv_a_norm`,
   and `solve` work on that partial data.

3. **Engine** (`config.py`, `engine.py`, `_kernel.py`) - `Engine` consumes aligned `prices` and `mu`
   Polars DataFrames plus a validated `Config` and produces correlation-shrinkage-optimized cash
   positions. It combines volatility adjustment, EWMA correlation matrices, identity shrinkage, and
   the linalg solver, scaling positions by a running profit-variance estimate.

   This layer is deliberately split in two. `engine.py` is a thin Polars-facing adapter: it
   validates the frames, derives `ret_adj`/`vola`/`cor`, converts them to NumPy arrays, and writes
   the result back into a DataFrame. The actual timestamp walk lives in `_kernel.py`, whose
   functions touch **only** NumPy arrays — no Polars and no `Config`. Keep that boundary when
   editing: numeric changes belong in `_kernel.py`, frame handling in `engine.py`.

The optional **hyper** layer (`hyper/`) wraps Optuna: `optimize()` runs a study over a
portfolio-returning function scored by Sharpe ratio and returns a frozen `Study`.

## Dependencies

Core (`[project].dependencies`, what `pip install tinycta` provides): `cvx-linalg`,
`numpy>=2.0.0`, `polars>=1.43.0`, `pydantic`

**Everything on the core import path must import only these four.** `tinycta.engine`
imports `tinycta._kernel` at module level, so an import from the `hyper` extra anywhere
outside `hyper/` breaks `pip install tinycta` — this is why `_kernel.py` does no logging.
`tests/test_core_install.py` guards the contract; `deptry` cannot, because it accepts an
import declared anywhere in the manifest, including in an extra.

Hyper extra (`pip install "tinycta[hyper]"`, required by `tinycta.hyper` only):
`jquantstats`, `loguru`, `optuna`, `pyyaml`

Dev: `pre-commit`, `marimo`, `pandas`, `pandas-stubs`

Test: `pytest`, `pytest-cov`, `pytest-html`, `pytest-mock`, `pytest-xdist`, `pytest-timeout`,
`hypothesis`, `pytest-benchmark`

Managed via `uv add` and `pyproject.toml`.

## Rhiza Framework

This project uses the Rhiza framework for standardized Python development. The main Makefile includes
`.rhiza/rhiza.mk` which provides common targets. Do not modify `.rhiza/` files directly - they are
template-managed.
