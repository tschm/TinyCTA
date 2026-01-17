# TinyCTA Repository Analysis

**Analysis Date:** January 2026
**Repository:** https://github.com/tschm/TinyCTA
**Version Analyzed:** 0.8.6

---

## Executive Summary

TinyCTA is a well-maintained, lightweight Python package for Commodity Trading Advisor (CTA) strategies. The project demonstrates strong engineering practices with comprehensive CI/CD, security scanning, and consistent code quality tooling. It serves a focused purpose with minimal dependencies.

**Overall Score: 8.2/10**

---

## Category Scores

| Category | Score | Details |
|----------|-------|---------|
| Code Quality | 8/10 | Clean, readable code with good docstrings |
| Test Coverage | 7/10 | Good test structure, test-to-code ratio ~1.1:1 |
| Documentation | 8/10 | Excellent README, API docs, comprehensive docstrings |
| Project Structure | 9/10 | Clean src layout, proper packaging, well-organized |
| CI/CD Pipeline | 9/10 | 12 workflows covering all aspects |
| Security Practices | 9/10 | Multiple security tools, CodeQL, bandit, pip-audit |
| Dependency Management | 9/10 | Modern tooling (uv), minimal deps, lock file |
| Type Safety | 7/10 | Type hints present but mypy not fully enforced |
| Maintainability | 8/10 | Small codebase, clear purpose, active development |
| Developer Experience | 8/10 | Good Makefile targets, clear workflow |

---

## Detailed Analysis

### 1. Code Quality (8/10)

**Strengths:**
- Consistent code style enforced via ruff (format and lint)
- All functions have comprehensive docstrings with parameter descriptions
- Clear separation between signal processing and linear algebra modules
- Proper use of `__future__` annotations for forward compatibility
- Functions are single-purpose and well-named

**Areas for Improvement:**
- Some functions use generic `AssertionError` instead of specific exceptions (e.g., `ValueError` for dimension mismatches)
- The `a_norm` and `inv_a_norm` functions have nearly identical implementations - could potentially share more code
- Comment `# that's somewhat not needed...` in linalg.py:50 suggests technical debt

**Metrics:**
- Source lines: 289 (excluding blanks/comments)
- Average function length: ~15-20 lines
- Cyclomatic complexity: Low (simple control flow)

### 2. Test Coverage (7/10)

**Strengths:**
- Tests exist for all public functions
- Tests cover edge cases (NaN values, dimension mismatches)
- Use of pytest fixtures for shared test data
- Test files have comprehensive docstrings explaining test purpose
- Test-to-code ratio: 323 test lines / 289 source lines = 1.1:1

**Areas for Improvement:**
- No explicit coverage threshold enforced in CI
- Missing tests for boundary conditions (e.g., empty arrays, single-element arrays)
- No property-based testing (e.g., hypothesis)
- Test data file (prices_hashed.csv at 3.7MB) is large for a test fixture

**Test Structure:**
```
tests/
├── test_tiny_cta/          # Package tests
│   ├── conftest.py         # Fixtures
│   ├── test_linalg.py      # 14 tests
│   ├── test_signal.py      # 4 tests
│   └── test_version.py     # 1 test
└── test_rhiza/             # Infrastructure tests
```

### 3. Documentation (8/10)

**Strengths:**
- Excellent README with badges, installation instructions, and API reference
- Every function has NumPy-style docstrings with Parameters/Returns sections
- Usage examples included in README
- Book/documentation infrastructure in place
- Quick links to PyPI, Issues, Discussions

**Areas for Improvement:**
- No inline examples in docstrings (doctests)
- No changelog/HISTORY file
- Book directory exists but appears minimally populated
- No architecture decision records (ADRs)

### 4. Project Structure (9/10)

**Strengths:**
- Clean `src/` layout following modern Python packaging standards
- Proper separation: source, tests, docs, assets
- Uses hatchling as build backend (modern, fast)
- Wheel configuration explicitly specifies packages
- `.rhiza/` framework provides standardized infrastructure

**Structure:**
```
TinyCTA/
├── src/tinycta/           # Package source (3 files)
├── tests/                 # Test suite
├── book/                  # Documentation
├── .github/workflows/     # 12 CI workflows
├── .rhiza/                # Template framework
├── pyproject.toml         # Modern config
└── Makefile               # Developer commands
```

**Areas for Improvement:**
- No `py.typed` marker file for PEP 561 compliance
- No examples/ directory with standalone usage examples

### 5. CI/CD Pipeline (9/10)

**Strengths:**
- 12 GitHub Actions workflows covering:
  - CI testing across multiple Python versions
  - Pre-commit hooks
  - Security scanning (pip-audit, bandit)
  - CodeQL analysis (Python + GitHub Actions)
  - Dependency checking (deptry)
  - Documentation building
  - Release automation
  - Template synchronization
- Matrix testing generates Python versions dynamically from pyproject.toml
- Minimal permissions (principle of least privilege)

**Workflows:**
| Workflow | Purpose |
|----------|---------|
| rhiza_ci.yml | Multi-version pytest |
| rhiza_pre-commit.yml | Code quality checks |
| rhiza_security.yml | pip-audit + bandit |
| codeql.yml | Advanced security analysis |
| rhiza_deptry.yml | Dependency issues |
| rhiza_release.yml | PyPI publishing |
| rhiza_book.yml | Documentation |
| rhiza_marimo.yml | Notebooks |
| rhiza_benchmarks.yml | Performance |
| rhiza_sync.yml | Template sync |
| rhiza_validate.yml | Structure validation |
| rhiza_codeql.yml | Additional CodeQL |

**Areas for Improvement:**
- No explicit coverage threshold check in CI
- No smoke tests for installed package
- Scheduled CodeQL runs only weekly

### 6. Security Practices (9/10)

**Strengths:**
- Multiple security scanning tools:
  - Bandit (static analysis for Python security issues)
  - pip-audit (dependency vulnerability checking)
  - CodeQL (advanced code scanning)
- Pre-commit hooks include bandit
- Minimal permissions in workflows
- Dependencies pinned with lock file (uv.lock)
- renovate[bot] for automated dependency updates

**Areas for Improvement:**
- No SECURITY.md file with vulnerability reporting instructions
- No signed commits required
- No dependency review action for PRs

### 7. Dependency Management (9/10)

**Strengths:**
- Only 2 runtime dependencies: numpy>=2.0.0, pandas>=2.2.3
- Modern tooling: uv for fast, reliable dependency management
- Lock file (uv.lock) ensures reproducible builds
- Clear separation of dev dependencies via dependency-groups
- deptry workflow checks for unused/missing dependencies
- renovate[bot] automates updates (223 commits from bot)

**Dependencies:**
```
Runtime: numpy, pandas
Dev: pre-commit, marimo, plotly
```

**Areas for Improvement:**
- numpy>=2.0.0 is very recent - may limit compatibility
- No optional dependency groups (e.g., [dev], [docs])

### 8. Type Safety (7/10)

**Strengths:**
- Type hints present on all function signatures
- Uses `from __future__ import annotations` for modern syntax
- mypy configured in pre-commit hooks
- Return types specified

**Example:**
```python
def solve(matrix: np.ndarray, rhs: np.ndarray) -> np.ndarray:
```

**Areas for Improvement:**
- No `py.typed` marker file
- mypy only runs on `src/` directory (not tests)
- No strict mypy configuration in pyproject.toml
- Some type hints could be more specific (e.g., `np.ndarray[np.float64]`)

### 9. Maintainability (8/10)

**Strengths:**
- Small, focused codebase (~290 lines)
- Single responsibility principle followed
- Active development (599 commits in last year)
- Single maintainer with clear ownership
- Template framework (Rhiza) provides consistent infrastructure

**Metrics:**
- Primary contributor: 432 commits
- Bot contributions: 323 commits (renovate, pre-commit-ci, dependabot)
- Recent activity: Active as of late 2025

**Areas for Improvement:**
- Single maintainer - bus factor of 1
- No CODEOWNERS file
- No contributing guidelines beyond "Contributions welcome"

### 10. Developer Experience (8/10)

**Strengths:**
- Clear Makefile with well-documented targets
- Single command setup: `make install`
- Consistent tooling via Rhiza framework
- Pre-commit hooks catch issues early
- GitHub Copilot instructions provided

**Key Commands:**
```bash
make install   # Setup environment
make test      # Run tests with coverage
make fmt       # Format and lint
make deptry    # Check dependencies
make marimo    # Interactive notebooks
make book      # Build documentation
```

**Areas for Improvement:**
- No devcontainer configuration (referenced but not present)
- No docker-compose for development
- No VS Code workspace settings

---

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Bus factor (single maintainer) | Medium | Document processes, seek co-maintainers |
| Large test data file | Low | Consider generating synthetic data |
| numpy 2.0 requirement | Low | Well-tested, modern standard |

---

## Recommendations

### High Priority
1. Add `py.typed` marker file for PEP 561 compliance
2. Create SECURITY.md with vulnerability reporting process
3. Add coverage threshold check in CI (suggest 80%)

### Medium Priority
4. Replace generic `AssertionError` with specific exceptions
5. Add property-based tests with hypothesis
6. Create CONTRIBUTING.md with detailed guidelines

### Low Priority
7. Add doctests to function docstrings
8. Create examples/ directory with standalone scripts
9. Consider generating synthetic test data to reduce repo size

---

## Conclusion

TinyCTA is a high-quality, well-maintained Python package that demonstrates modern Python development practices. The project excels in CI/CD, security scanning, and code organization. The main areas for improvement are around type safety enforcement and expanding test coverage. The Rhiza framework provides excellent infrastructure standardization.

The package serves its purpose well - providing a minimal, focused toolkit for CTA strategy implementation without unnecessary complexity.
