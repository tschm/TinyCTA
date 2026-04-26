# 📈 [TinyCTA](https://tschm.github.io/TinyCTA/)

A Lightweight Python Package for Commodity Trading Advisor Strategies.

[![PyPI version](https://badge.fury.io/py/tinycta.svg)](https://badge.fury.io/py/tinycta)
[![MIT License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://github.com/tschm/tinycta/blob/master/LICENSE)
[![Coverage](https://tschm.github.io/TinyCTA/coverage-badge.svg)](https://tschm.github.io/TinyCTA/reports/html-coverage/index.html)
[![Downloads](https://static.pepy.tech/personalized-badge/tinycta?period=month&units=international_system&left_color=black&right_color=orange&left_text=PyPI%20downloads%20per%20month)](https://pepy.tech/project/tinycta)
[![CodeFactor](https://www.codefactor.io/repository/github/tschm/TinyCTA/badge)](https://www.codefactor.io/repository/github/tschm/TinyCTA)
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

## 🚀 Installation

### Using pip

```bash
pip install tinycta
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
result = prices.with_columns(osc(pl.col("A"), fast=2, slow=6, vola=3).alias("osc_A"))
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
print(solution)
```

```result
[0. 2.]
```

## 📚 API Reference

### Signal Processing (`tinycta.osc`, `tinycta.ewma`, `tinycta.util`)

- `osc(x, fast, slow, vola, min_samples=1)` — EWMA-difference oscillator scaled by EWMA volatility (Polars)
- `ma_cross(prices, fast, slow, min_samples=1)` — sign of fast-vs-slow EWM crossover: -1, 0, or +1 (Polars)
- `vol_adj(x, vola, clip, min_samples=1)` — clipped, volatility-adjusted log returns (Polars)
- `adj_log_prices(x, vola, clip, min_samples=1)` — cumulative sum of volatility-adjusted log returns (Polars)

### Signal Utilities (`tinycta.signal`)

- `moving_absolute_deviation(price, com=32)` — robust rolling volatility estimate via median absolute deviation (pandas)
- `shrink2id(matrix, lamb=1.0)` — shrink a matrix towards the identity matrix

### Linear Algebra (`tinycta.linalg`)

- `valid(matrix)` — extract the finite subset of a matrix by filtering NaN rows/columns
- `a_norm(vector, matrix=None)` — matrix-norm of a vector
- `inv_a_norm(vector, matrix=None)` — inverse matrix-norm of a vector
- `solve(matrix, rhs)` — solve a linear system, handling matrices with NaN values

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
