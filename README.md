# 📈 TinyCTA

[![PyPI version](https://badge.fury.io/py/tinycta.svg)](https://badge.fury.io/py/tinycta)
[![MIT License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://github.com/tschm/tinycta/blob/master/LICENSE)
[![Downloads](https://static.pepy.tech/personalized-badge/tinycta?period=month&units=international_system&left_color=black&right_color=orange&left_text=PyPI%20downloads%20per%20month)](https://pepy.tech/project/tinycta)
[![Coverage Status](https://coveralls.io/repos/github/tschm/TinyCTA/badge.png?branch=main)](https://coveralls.io/github/tschm/TinyCTA?branch=main)
[![CodeFactor](https://www.codefactor.io/repository/github/tschm/TinyCTA/badge)](https://www.codefactor.io/repository/github/tschm/TinyCTA)

📦 A lightweight Python package for implementing Commodity
Trading Advisor (CTA) strategies with a focus on trend-following
signals and linear algebra operations.

## 📋 Overview

TinyCTA provides essential tools for quantitative finance and algorithmic trading,
particularly for trend-following strategies. The package includes:

- Signal processing functions for creating oscillators and adjusting returns
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

### Creating an oscillator

```python
import pandas as pd
from tinycta.signal import osc

# Load price data
prices = pd.read_csv('prices.csv', index_col=0, parse_dates=True)

# Create an oscillator with default parameters
oscillator = prices.apply(osc)

# Create an oscillator with custom parameters
custom_oscillator = prices.apply(osc, fast=16, slow=64, scaling=False)
```

### Adjusting returns for volatility

```python
import pandas as pd
from tinycta.signal import returns_adjust

# Load price data
prices = pd.read_csv('prices.csv', index_col=0, parse_dates=True)

# Adjust returns for volatility
adjusted_returns = prices.apply(returns_adjust)
```

### Linear algebra operations

```python
import numpy as np
from tinycta.linalg import solve, shrink2id

# Create a matrix and right-hand side vector
matrix = np.array([[1.0, 0.5], [0.5, 1.0]])
rhs = np.array([1.0, 2.0])

# Solve the linear system
solution = solve(matrix, rhs)

# Apply shrinkage to the matrix
shrunk_matrix = shrink2id(matrix, lamb=0.5)
```

## 📚 API Reference

### Signal Processing

- `osc(prices, fast=32, slow=96, scaling=True)`:
   Creates an oscillator based on the difference between fast and slow moving averages
- `returns_adjust(price, com=32, min_periods=300, clip=4.2)`:
   Adjusts log-returns by volatility and applies winsorization
- `shrink2id(matrix, lamb=1.0)`:
   Performs shrinkage of a matrix towards the identity matrix

### Linear Algebra

- `valid(matrix)`:
Constructs a valid subset of a matrix by filtering out rows/columns with NaN values
- `a_norm(vector, matrix=None)`:
Computes the matrix-norm of a vector with respect to a matrix
- `inv_a_norm(vector, matrix=None)`: Computes the inverse matrix-norm of a vector
- `solve(matrix, rhs)`:
Solves a linear system of equations, handling matrices with NaN values

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
