# TinyCTA Improvement Plan: 8.2 → 10.0

**Goal:** Elevate TinyCTA from 8.2/10 to 10.0/10 through targeted improvements across all categories.

---

## Score Gap Analysis

| Category | Current | Target | Gap | Priority |
|----------|---------|--------|-----|----------|
| Test Coverage | 7/10 | 10/10 | +3 | High |
| Type Safety | 7/10 | 10/10 | +3 | High |
| Code Quality | 8/10 | 10/10 | +2 | Medium |
| Documentation | 8/10 | 10/10 | +2 | Medium |
| Maintainability | 8/10 | 10/10 | +2 | Medium |
| Developer Experience | 8/10 | 10/10 | +2 | Medium |
| Project Structure | 9/10 | 10/10 | +1 | Low |
| CI/CD Pipeline | 9/10 | 10/10 | +1 | Low |
| Security Practices | 9/10 | 10/10 | +1 | Low |
| Dependency Management | 9/10 | 10/10 | +1 | Low |

---

## Phase 1: Quick Wins (1-2 days)

These items require minimal effort but provide immediate score improvements.

### 1.1 Type Safety (+1 point)

**Task: Add PEP 561 marker file**
```bash
touch src/tinycta/py.typed
```

**Task: Update pyproject.toml to include marker**
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/tinycta"]
include = ["src/tinycta/py.typed"]
```

### 1.2 Project Structure (+0.5 points)

**Task: Create examples directory with usage scripts**
```
examples/
├── README.md
├── basic_oscillator.py
├── volatility_adjustment.py
└── portfolio_optimization.py
```

**Example content for `examples/basic_oscillator.py`:**
```python
"""Example: Creating a trend-following oscillator."""
import pandas as pd
from tinycta.signal import osc

# Load your price data
prices = pd.read_csv("your_prices.csv", index_col=0, parse_dates=True)

# Create oscillator with default parameters (fast=32, slow=96)
oscillator = prices.apply(osc)

# Create oscillator without scaling
raw_oscillator = prices.apply(osc, scaling=False)

print(oscillator.tail())
```

### 1.3 Security Practices (+0.5 points)

**Task: Create SECURITY.md**
```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.8.x   | :white_check_mark: |
| < 0.8   | :x:                |

## Reporting a Vulnerability

Please report security vulnerabilities by emailing thomas.schmelzer@gmail.com.

Do NOT create public GitHub issues for security vulnerabilities.

You can expect:
- Acknowledgment within 48 hours
- Status update within 7 days
- Fix timeline discussion for confirmed vulnerabilities

## Security Measures

This project uses:
- CodeQL for code scanning
- pip-audit for dependency vulnerabilities
- bandit for Python security issues
- renovate for automated dependency updates
```

### 1.4 Maintainability (+0.5 points)

**Task: Create CODEOWNERS file**
```
# .github/CODEOWNERS
* @tschm
```

---

## Phase 2: Code Quality & Type Safety (3-5 days)

### 2.1 Replace Generic Exceptions (+1 point for Code Quality)

**Task: Create custom exceptions in `src/tinycta/exceptions.py`**
```python
"""Custom exceptions for TinyCTA."""

class TinyCTAError(Exception):
    """Base exception for TinyCTA."""
    pass

class DimensionMismatchError(TinyCTAError, ValueError):
    """Raised when matrix/vector dimensions don't match."""
    pass

class NonSquareMatrixError(TinyCTAError, ValueError):
    """Raised when a square matrix is required but not provided."""
    pass
```

**Task: Update linalg.py to use specific exceptions**

Replace all instances of:
```python
if matrix.shape[0] != matrix.shape[1]:
    raise AssertionError
```

With:
```python
from tinycta.exceptions import NonSquareMatrixError, DimensionMismatchError

if matrix.shape[0] != matrix.shape[1]:
    raise NonSquareMatrixError(
        f"Matrix must be square, got shape {matrix.shape}"
    )
```

Replace dimension mismatch checks:
```python
if vector.size != matrix.shape[0]:
    raise DimensionMismatchError(
        f"Vector size {vector.size} doesn't match matrix dimension {matrix.shape[0]}"
    )
```

### 2.2 Strict Type Hints (+1 point for Type Safety)

**Task: Add mypy configuration to pyproject.toml**
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
show_error_codes = true

[[tool.mypy.overrides]]
module = "pandas.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "numpy.*"
ignore_missing_imports = true
```

**Task: Add more specific type hints**

Update function signatures with more precise types:
```python
from typing import TypeAlias
import numpy as np
import numpy.typing as npt

# Define type aliases
FloatArray: TypeAlias = npt.NDArray[np.floating[Any]]
BoolArray: TypeAlias = npt.NDArray[np.bool_]

def valid(matrix: FloatArray) -> tuple[BoolArray, FloatArray]:
    ...

def solve(matrix: FloatArray, rhs: FloatArray) -> FloatArray:
    ...
```

### 2.3 Remove Technical Debt (+0.5 points for Code Quality)

**Task: Remove or address the comment in linalg.py:50**

Either:
1. Remove the comment if the function is needed
2. Deprecate the function if truly not needed:
```python
import warnings

def a_norm(vector: np.ndarray, matrix: np.ndarray | None = None) -> float:
    """..."""
    warnings.warn(
        "a_norm may be removed in a future version. Use numpy.linalg.norm instead.",
        DeprecationWarning,
        stacklevel=2
    )
    ...
```

### 2.4 Refactor Duplicate Code (+0.5 points for Code Quality)

**Task: Extract shared validation logic**

Create a helper function in linalg.py:
```python
def _validate_matrix_vector(
    matrix: FloatArray,
    vector: FloatArray
) -> tuple[BoolArray, FloatArray, FloatArray]:
    """Validate matrix-vector pair and return valid subset.

    Returns:
        Tuple of (validity mask, valid submatrix, valid subvector)
    """
    if matrix.shape[0] != matrix.shape[1]:
        raise NonSquareMatrixError(f"Matrix must be square, got shape {matrix.shape}")

    if vector.size != matrix.shape[0]:
        raise DimensionMismatchError(
            f"Vector size {vector.size} doesn't match matrix dimension {matrix.shape[0]}"
        )

    v, mat = valid(matrix)
    return v, mat, vector[v]
```

---

## Phase 3: Test Coverage (+3 points, 5-7 days)

### 3.1 Add Coverage Threshold to CI

**Task: Update tests/tests.mk**
```makefile
test: install
	@rm -rf _tests;
	@if [ -d ${TESTS_FOLDER} ]; then \
	  mkdir -p _tests/html-coverage _tests/html-report; \
	  ${VENV}/bin/python -m pytest ${TESTS_FOLDER} \
	    --ignore=${TESTS_FOLDER}/benchmarks \
	    --cov=${SOURCE_FOLDER} \
	    --cov-report=term \
	    --cov-report=html:_tests/html-coverage \
	    --cov-report=json:_tests/coverage.json \
	    --cov-fail-under=90 \
	    --html=_tests/html-report/report.html; \
	else \
	  printf "${YELLOW}[WARN] Test folder ${TESTS_FOLDER} not found, skipping tests${RESET}\n"; \
	fi
```

### 3.2 Add Boundary Condition Tests

**Task: Create `tests/test_tiny_cta/test_edge_cases.py`**
```python
"""Edge case tests for TinyCTA."""
import numpy as np
import pandas as pd
import pytest

from tinycta.linalg import a_norm, inv_a_norm, solve, valid
from tinycta.signal import osc, returns_adjust, shrink2id


class TestEmptyInputs:
    """Test behavior with empty inputs."""

    def test_valid_empty_matrix(self):
        """Test valid() with 0x0 matrix."""
        matrix = np.array([]).reshape(0, 0)
        v, submatrix = valid(matrix)
        assert len(v) == 0
        assert submatrix.shape == (0, 0)

    def test_solve_empty(self):
        """Test solve() with empty matrix."""
        matrix = np.array([]).reshape(0, 0)
        rhs = np.array([])
        result = solve(matrix, rhs)
        assert len(result) == 0


class TestSingleElement:
    """Test behavior with single-element inputs."""

    def test_valid_single_element(self):
        """Test valid() with 1x1 matrix."""
        matrix = np.array([[5.0]])
        v, submatrix = valid(matrix)
        np.testing.assert_array_equal(v, [True])
        np.testing.assert_array_equal(submatrix, [[5.0]])

    def test_solve_single_element(self):
        """Test solve() with 1x1 matrix."""
        matrix = np.array([[2.0]])
        rhs = np.array([4.0])
        result = solve(matrix, rhs)
        np.testing.assert_array_almost_equal(result, [2.0])

    def test_shrink_single_element(self):
        """Test shrink2id with 1x1 matrix."""
        matrix = np.array([[5.0]])
        result = shrink2id(matrix, lamb=0.5)
        np.testing.assert_array_almost_equal(result, [[3.0]])  # 5*0.5 + 1*0.5


class TestLargeValues:
    """Test numerical stability with large values."""

    def test_a_norm_large_values(self):
        """Test a_norm doesn't overflow with large values."""
        v = np.array([1e150, 1e150])
        result = a_norm(v)
        assert np.isfinite(result)

    def test_solve_near_singular(self):
        """Test solve with near-singular matrix."""
        matrix = np.array([[1.0, 1.0], [1.0, 1.0 + 1e-10]])
        rhs = np.array([1.0, 1.0])
        result = solve(matrix, rhs)
        # Should still produce a result (may be inaccurate)
        assert result is not None


class TestAllNaN:
    """Test behavior when all values are NaN."""

    def test_valid_all_nan(self):
        """Test valid() with all-NaN matrix."""
        matrix = np.array([[np.nan, np.nan], [np.nan, np.nan]])
        v, submatrix = valid(matrix)
        np.testing.assert_array_equal(v, [False, False])
        assert submatrix.shape == (0, 0)

    def test_solve_all_nan(self):
        """Test solve() returns NaN for all-NaN matrix."""
        matrix = np.nan * np.ones((2, 2))
        rhs = np.array([1.0, 2.0])
        result = solve(matrix, rhs)
        assert np.all(np.isnan(result))
```

### 3.3 Add Property-Based Tests

**Task: Add hypothesis to dev dependencies**
```bash
uv add --group dev hypothesis
```

**Task: Create `tests/test_tiny_cta/test_properties.py`**
```python
"""Property-based tests for TinyCTA using Hypothesis."""
import numpy as np
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from tinycta.linalg import a_norm, solve, valid
from tinycta.signal import osc, shrink2id


# Custom strategies
def square_matrices(min_size=1, max_size=10):
    """Generate square matrices."""
    return st.integers(min_value=min_size, max_value=max_size).flatmap(
        lambda n: arrays(
            dtype=np.float64,
            shape=(n, n),
            elements=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
        )
    )


def positive_definite_matrices(size):
    """Generate positive definite matrices."""
    return arrays(
        dtype=np.float64,
        shape=(size, size),
        elements=st.floats(min_value=-1, max_value=1, allow_nan=False, allow_infinity=False)
    ).map(lambda a: a @ a.T + np.eye(size))


class TestLinalgProperties:
    """Property-based tests for linear algebra functions."""

    @given(square_matrices())
    @settings(max_examples=100)
    def test_valid_preserves_square(self, matrix):
        """valid() always returns a square submatrix."""
        v, submatrix = valid(matrix)
        assert submatrix.shape[0] == submatrix.shape[1]
        assert submatrix.shape[0] == np.sum(v)

    @given(st.integers(min_value=2, max_value=5))
    @settings(max_examples=50)
    def test_solve_inverse_property(self, n):
        """solve(A, A@x) should return x for invertible A."""
        # Generate positive definite matrix (always invertible)
        rng = np.random.default_rng(42)
        A = rng.random((n, n))
        A = A @ A.T + np.eye(n)  # Make positive definite
        x = rng.random(n)
        b = A @ x

        result = solve(A, b)
        np.testing.assert_array_almost_equal(result, x, decimal=10)

    @given(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=100)
    def test_shrink_interpolation(self, lamb, n):
        """shrink2id interpolates between matrix and identity."""
        matrix = np.ones((n, n))
        result = shrink2id(matrix, lamb=lamb)

        # Diagonal should always be 1.0 (matrix has 1s, identity has 1s)
        np.testing.assert_array_almost_equal(np.diag(result), np.ones(n))

        # Off-diagonal should be lamb
        off_diag = result[~np.eye(n, dtype=bool)]
        np.testing.assert_array_almost_equal(off_diag, np.full(n*n - n, lamb))

    @given(
        arrays(
            dtype=np.float64,
            shape=st.tuples(st.integers(1, 100)),
            elements=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
        )
    )
    @settings(max_examples=100)
    def test_a_norm_non_negative(self, vector):
        """a_norm should always return non-negative values."""
        result = a_norm(vector)
        assert result >= 0
```

### 3.4 Add Doctests

**Task: Add doctest examples to signal.py**
```python
def osc(prices: pd.DataFrame, fast: int = 32, slow: int = 96, scaling: bool = True) -> pd.DataFrame:
    """Compute the oscillator for given financial price data.

    Examples
    --------
    >>> import pandas as pd
    >>> prices = pd.Series([100, 101, 102, 103, 104], name='price')
    >>> result = osc(prices, fast=2, slow=4, scaling=False)
    >>> len(result) == len(prices)
    True
    """
    ...
```

**Task: Enable doctests in pytest**

Add to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
addopts = "--doctest-modules"
testpaths = ["tests", "src"]
```

### 3.5 Generate Synthetic Test Data

**Task: Replace large CSV with synthetic data generator**

Create `tests/test_tiny_cta/conftest.py`:
```python
@pytest.fixture
def prices(request) -> pd.DataFrame:
    """Generate synthetic price data for testing."""
    rng = np.random.default_rng(42)  # Fixed seed for reproducibility
    n_days = 500
    n_assets = 10

    dates = pd.date_range('2020-01-01', periods=n_days, freq='D')

    # Generate random walk prices
    returns = rng.normal(0.0001, 0.02, (n_days, n_assets))
    prices = 100 * np.exp(np.cumsum(returns, axis=0))

    columns = [str(hash(f'asset_{i}')) for i in range(n_assets)]
    return pd.DataFrame(prices, index=dates, columns=columns)
```

This removes the 3.7MB test data file dependency.

---

## Phase 4: Documentation (+2 points, 3-4 days)

### 4.1 Create CHANGELOG.md

**Task: Create CHANGELOG.md following Keep a Changelog format**
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Custom exceptions for better error handling
- Property-based tests with Hypothesis
- Type hints with strict mypy configuration

## [0.8.6] - 2025-XX-XX

### Changed
- Updated dependencies

## [0.8.5] - 2025-XX-XX

### Fixed
- Minor bug fixes

[Unreleased]: https://github.com/tschm/TinyCTA/compare/v0.8.6...HEAD
[0.8.6]: https://github.com/tschm/TinyCTA/compare/v0.8.5...v0.8.6
```

### 4.2 Create CONTRIBUTING.md

**Task: Create comprehensive contributing guide**
```markdown
# Contributing to TinyCTA

Thank you for your interest in contributing to TinyCTA!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/tschm/TinyCTA.git
   cd TinyCTA
   ```

2. Install dependencies:
   ```bash
   make install
   ```

3. Verify setup:
   ```bash
   make test
   ```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests and formatting:
   ```bash
   make test
   make fmt
   ```

4. Commit with a descriptive message:
   ```bash
   git commit -m "Add: brief description of change"
   ```

5. Push and create a pull request

## Code Standards

- Follow PEP 8 (enforced via ruff)
- Add type hints to all functions
- Write docstrings for public functions (NumPy style)
- Add tests for new functionality
- Maintain >90% test coverage

## Commit Message Format

Use conventional commits:
- `Add:` for new features
- `Fix:` for bug fixes
- `Docs:` for documentation
- `Refactor:` for code changes that don't add features or fix bugs
- `Test:` for adding tests

## Questions?

Open a [Discussion](https://github.com/tschm/TinyCTA/discussions) for questions.
```

### 4.3 Populate Book Directory

**Task: Create Marimo notebooks for documentation**

Create `book/marimo/signal_tutorial.py`:
```python
import marimo

__generated_with = "0.19.2"
app = marimo.App()

@app.cell
def _():
    import marimo as mo
    mo.md("# Signal Processing with TinyCTA")
    return mo,

@app.cell
def _():
    import pandas as pd
    import numpy as np
    from tinycta.signal import osc, returns_adjust

    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    prices = pd.DataFrame({
        'AAPL': 100 * np.exp(np.cumsum(np.random.normal(0.0001, 0.02, 500))),
        'GOOGL': 100 * np.exp(np.cumsum(np.random.normal(0.0001, 0.025, 500)))
    }, index=dates)
    return prices,

@app.cell
def _(prices, osc):
    oscillator = prices.apply(osc)
    oscillator.plot(title='Trend-Following Oscillator')
    return oscillator,

if __name__ == "__main__":
    app.run()
```

---

## Phase 5: Developer Experience & CI (+2 points, 2-3 days)

### 5.1 Add Devcontainer Configuration

**Task: Create `.devcontainer/devcontainer.json`**
```json
{
  "name": "TinyCTA Development",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "postCreateCommand": "make install",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        "tamasfe.even-better-toml"
      ],
      "settings": {
        "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
        "python.testing.pytestEnabled": true,
        "python.testing.pytestPath": "${workspaceFolder}/.venv/bin/pytest",
        "[python]": {
          "editor.defaultFormatter": "charliermarsh.ruff",
          "editor.formatOnSave": true
        }
      }
    }
  }
}
```

### 5.2 Add VS Code Workspace Settings

**Task: Create `.vscode/settings.json`**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestPath": "${workspaceFolder}/.venv/bin/pytest",
  "python.testing.pytestArgs": ["tests"],
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "ruff.path": ["${workspaceFolder}/.venv/bin/ruff"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/*.egg-info": true,
    ".venv": true
  }
}
```

**Task: Create `.vscode/launch.json`**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "python": "${workspaceFolder}/.venv/bin/python"
    },
    {
      "name": "Python: Pytest",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": ["tests", "-v"],
      "console": "integratedTerminal",
      "python": "${workspaceFolder}/.venv/bin/python"
    }
  ]
}
```

### 5.3 Enhance CI Pipeline

**Task: Add dependency review action**

Create `.github/workflows/dependency-review.yml`:
```yaml
name: 'Dependency Review'
on: [pull_request]

permissions:
  contents: read

jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - name: 'Checkout Repository'
        uses: actions/checkout@v6
      - name: 'Dependency Review'
        uses: actions/dependency-review-action@v4
```

**Task: Add smoke test for installed package**

Add to `rhiza_ci.yml`:
```yaml
      - name: Smoke test installed package
        run: |
          .venv/bin/pip install .
          .venv/bin/python -c "from tinycta.signal import osc; from tinycta.linalg import solve; print('Import successful')"
```

---

## Phase 6: Final Polish (+1 point, 1 day)

### 6.1 Dependency Management

**Task: Add optional dependency groups to pyproject.toml**
```toml
[project.optional-dependencies]
dev = [
    "pre-commit>=4.0",
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "hypothesis>=6.0",
]
docs = [
    "marimo>=0.19",
    "pdoc>=14.0",
]
all = ["tinycta[dev,docs]"]
```

### 6.2 Maintainability

**Task: Seek co-maintainers**

Add to README.md:
```markdown
## Maintainers

- [@tschm](https://github.com/tschm) (Lead)

Interested in becoming a maintainer? Open a discussion!
```

### 6.3 Final Checklist

- [ ] All tests pass with >90% coverage
- [ ] mypy passes with strict mode
- [ ] All documentation is up to date
- [ ] CHANGELOG reflects all changes
- [ ] All new files are committed
- [ ] CI pipeline passes on all workflows

---

## Implementation Timeline

| Phase | Duration | Score Impact |
|-------|----------|--------------|
| Phase 1: Quick Wins | 1-2 days | +1.5 |
| Phase 2: Code Quality & Type Safety | 3-5 days | +3.0 |
| Phase 3: Test Coverage | 5-7 days | +3.0 |
| Phase 4: Documentation | 3-4 days | +2.0 |
| Phase 5: Developer Experience & CI | 2-3 days | +2.0 |
| Phase 6: Final Polish | 1 day | +1.0 |

**Total Estimated Duration:** 15-22 days
**Expected Final Score:** 10.0/10

---

## Post-Implementation Verification

After completing all phases, re-run the analysis to verify:

```bash
# Run all quality checks
make test
make fmt
make deptry

# Verify type checking
.venv/bin/mypy src/tinycta --strict

# Check coverage
.venv/bin/pytest --cov=src/tinycta --cov-fail-under=90

# Verify documentation builds
make book
```

---

## Maintenance

To maintain a 10/10 score:

1. **Weekly:** Review renovate PRs for dependency updates
2. **Per PR:** Ensure tests pass and coverage doesn't drop
3. **Monthly:** Review security advisories
4. **Quarterly:** Update CHANGELOG and documentation
