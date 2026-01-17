# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TinyCTA is a lightweight Python package for Commodity Trading Advisor (CTA) strategies. It provides signal processing functions for trend-following strategies and linear algebra utilities that handle matrices with missing values.

## Development Commands

The project uses `make` and `uv` for development. Key commands:

```bash
make install    # Install uv, create .venv, install dependencies
make test       # Run pytest with coverage (outputs to _tests/)
make fmt        # Run pre-commit hooks (ruff format, ruff check --fix)
make deptry     # Check for missing/unused dependencies
make marimo     # Start Marimo notebook server
```

To run a single test file:
```bash
.venv/bin/python -m pytest tests/test_tiny_cta/test_signal.py
```

To run a specific test:
```bash
.venv/bin/python -m pytest tests/test_tiny_cta/test_signal.py::test_name -v
```

## Project Structure

- `src/tinycta/` - Main package source code
  - `signal.py` - Signal processing: `osc()` (oscillator), `returns_adjust()`, `shrink2id()`
  - `linalg.py` - Linear algebra utilities: `valid()`, `a_norm()`, `inv_a_norm()`, `solve()`
- `tests/test_tiny_cta/` - Package tests
- `tests/test_rhiza/` - Rhiza framework infrastructure tests
- `book/` - Documentation source
- `.rhiza/` - Rhiza framework scripts and configurations

## Architecture Notes

The package has two core modules:

1. **signal.py** - Functions for trend-following signal generation:
   - Uses pandas EWM (exponentially weighted moving) for oscillator calculations
   - Returns volatility-adjusted using log returns and clipping

2. **linalg.py** - Linear algebra operations that handle NaN values:
   - `valid()` extracts the finite subset of a matrix by checking diagonal elements
   - All functions (`a_norm`, `inv_a_norm`, `solve`) use `valid()` to work with partial data

## Dependencies

Core: `numpy>=2.0.0`, `pandas>=2.2.3`

Dev: `pre-commit`, `marimo`, `plotly`

Managed via `uv add` and `pyproject.toml`.

## Rhiza Framework

This project uses the Rhiza framework for standardized Python development. The main Makefile includes `.rhiza/rhiza.mk` which provides common targets. Do not modify `.rhiza/` files directly - they are template-managed.
