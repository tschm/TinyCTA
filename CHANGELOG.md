## [0.13.1] - 2026-06-04

### 🐛 Bug Fixes

- *(hyper)* Restore missing docstring on inner objective function

### 💼 Other

- Bump version 0.13.0 → 0.13.1

### 🚜 Refactor

- *(hyper)* Suggest_portfolio_fn returns Portfolio directly

### 📚 Documentation

- Add optimizer.md documenting tinycta.hyper usage

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md for v0.13.0 [skip ci]
## [0.13.0] - 2026-06-04

### 🚀 Features

- *(hyper)* Introduce Study dataclass and optimize wrapper

### 🐛 Bug Fixes

- Update cvx.linalg import path and bump polars minimum to 1.21.0
- Increase tolerance in test_moving_absolute_deviation
- *(hyper)* Fix stale run_study references and patch path in tests
- *(hyper)* Guard best_params/best_value access in Study.from_optuna

### 💼 Other

- Bump version 0.12.5 → 0.13.0

### 📚 Documentation

- Add missing docstring to _load_yaml to reach 100% docs coverage

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md for v0.12.5 [skip ci]
- Bump rhiza to v0.18.4
- Apply rhiza sync v0.18.4
- Add classifiers to pyproject.toml
- Add pip dependabot entry for .rhiza/requirements
- Remove plotly as explicit dependency
## [0.12.5] - 2026-05-27

### 🚀 Features

- Add profiles: github-project to template.yml

### 🐛 Bug Fixes

- Remove leading newline from .python-version

### 💼 Other

- Bump rhiza template version v0.10.3 → v0.10.9
- Sync rhiza template to v0.10.9
- Rename template entries tests→github-tests, book→github-book
- Sync rhiza template — restore missing workflow files
- Bump version 0.12.4 → 0.12.5

### ⚙️ Miscellaneous Tasks

- Bump rhiza template to v0.11.0
- Sync with rhiza v0.11.0
- Sync rhiza to v0.16.1
- Sync rhiza to v0.15.1 with conflict resolution
- Remove extra blank lines in rhiza API tests
- Bump rhiza to v0.15.2
- Apply rhiza sync v0.15.2
- Bump workflow callers from v0.14.0 to v0.15.2
- Bump rhiza to v0.15.3
- Apply rhiza sync v0.15.3
- Bump rhiza to v0.17.0
- Apply rhiza sync v0.17.0
## [0.12.4] - 2026-05-21

### 🐛 Bug Fixes

- *(readme)* Round solve output to suppress floating-point noise from cvx-linalg 0.5.1

### 💼 Other

- Bump version 0.12.3 → 0.12.4

### 🧪 Testing

- *(linalg)* Adapt tests to cvx-linalg 0.5.1 exception types
## [0.12.3] - 2026-05-17

### 💼 Other

- Bump version 0.12.2 → 0.12.3

### 🚜 Refactor

- *(signal)* Replace pandas with polars in moving_absolute_deviation
## [0.12.2] - 2026-05-15

### 🐛 Bug Fixes

- *(osc)* Switch ewm_mean to adjust=True for unbiased EWMA
- *(test_osc)* Update reference to use adjust=True to match osc()

### 💼 Other

- Bump version 0.12.1 → 0.12.2
## [0.12.1] - 2026-05-15

### 💼 Other

- Bump version 0.12.0 → 0.12.1

### 🚜 Refactor

- *(osc)* Replace EWMA-std scaling with analytical scaling factor

### 📚 Documentation

- *(readme)* Update osc() signature to remove vola parameter
## [0.12.0] - 2026-05-14

### 🚀 Features

- *(ewm_cov)* Add ewm_covariance function with tests
- *(engine)* Remove pyarrow dependency by using ewm_covariance
- *(ewm_cov)* Delegate to cvx.linalg 0.4.1, achieve 100% test coverage

### 🐛 Bug Fixes

- *(deptry)* Map cvx-linalg to cvx namespace in package_module_name_map
- *(deptry)* Add all packages to package_module_name_map to silence warnings

### 💼 Other

- Bump version 0.11.0 → 0.12.0

### 🚜 Refactor

- *(linalg)* Replace implementation with thin wrapper around cvx.linalg
## [0.11.0] - 2026-04-26

### 🚀 Features

- Add optuna, loguru, and pyyaml dependencies
- Add hyper module with experiment config and optuna study runner

### 💼 Other

- Bump version 0.10.0 → 0.11.0

### ⚙️ Miscellaneous Tasks

- Add pyyaml import mapping and remove mypy config
## [0.10.0] - 2026-04-26

### 🚀 Features

- Add engine with pydantic, pyarrow dependencies

### 🐛 Bug Fixes

- Suppress DEP002 for pyarrow and fix ty type error in engine

### 💼 Other

- Bump version 0.9.9 → 0.10.0

### 📚 Documentation

- Update README to reflect Polars-based API

### 🎨 Styling

- Fix import order in engine.py

### 🧪 Testing

- Remove osc and returns_adjust tests
- Bring engine coverage to 100%
## [0.9.9] - 2026-04-25

### 🚀 Features

- Add polars dependency and ewma/osc modules with tests

### 💼 Other

- Bump version 0.9.8 → 0.9.9
## [0.9.8] - 2026-04-25

### 💼 Other

- Bump version 0.9.7 → 0.9.8

### ⚙️ Miscellaneous Tasks

- Update via rhiza
- Sync with rhiza template v0.10.3
## [0.9.7] - 2026-04-18

### 💼 Other

- Bump version 0.9.6 → 0.9.7
## [0.9.6] - 2026-04-18

### 🐛 Bug Fixes

- Remove duplicate security target from Makefile
- Remove mkdocs-build:: to resolve double/single colon conflict
- Remove HTML div wrapper from README to fix MkDocs rendering
- Correct nav paths from report/ to reports/ in mkdocs.yml

### 💼 Other

- Bump version 0.9.5 → 0.9.6

### 📚 Documentation

- Add mkdocs.yml inheriting from docs/mkdocs-base.yml
- Add CI/CD section with Hypothesis to mkdocs nav

### ⚙️ Miscellaneous Tasks

- Sync rhiza template files
- Update rhiza template to v0.10.0
- Sync rhiza template files to v0.10.0
- Sync rhiza template files
- Remove .rhiza/docs and exclude from template sync
- Sync rhiza template files
- Remove unused rhiza make.d files and exclude from sync
- Sync rhiza template files
- Remove gh-aw and github test files, exclude from sync
- Sync rhiza template files
- Remove docs/adr folder and exclude from sync
- Sync rhiza template files
## [0.9.5] - 2026-04-12

### 🐛 Bug Fixes

- Ignore CVE-2026-4539 in pygments (no fix available yet)
- Ensure _book directory exists when mkdocs.yml is absent

### 💼 Other

- Remove CVE-2026-4539 exception from pip-audit
- Bump version 0.9.4 → 0.9.5

### 📚 Documentation

- Update SECURITY.md to reference TinyCTA instead of Rhiza

### ⚙️ Miscellaneous Tasks

- Resolve rhiza template sync conflicts and apply patch updates
- Sync rhiza template files
- Apply rhiza template sync and resolve merge conflicts
## [0.9.4] - 2026-03-22

### 🐛 Bug Fixes

- Update coverage badge URL to gh-pages SVG

### 💼 Other

- Bump version 0.9.3 → 0.9.4

### ⚙️ Miscellaneous Tasks

- Sync rhiza template files
## [0.9.3] - 2026-03-17

### 🐛 Bug Fixes

- Resolve merge conflicts in workflow files for setup-uv v7.5.0

### 💼 Other

- Bump version 0.9.2 → 0.9.3

### ⚙️ Miscellaneous Tasks

- Sync rhiza template files
- Bump uv to 0.10.11, add materialize deprecation target, update CodeQL
- Remove benchmark workflow and tests, update template.lock
## [0.9.2] - 2026-03-11

### 🐛 Bug Fixes

- Resolve merge conflicts keeping uv 0.10.9

### 💼 Other

- Bump version 0.9.1 → 0.9.2

### ⚙️ Miscellaneous Tasks

- Sync rhiza template files
- Sync rhiza template files
## [0.9.1] - 2026-02-24

### 🚀 Features

- Make renovate.json flexible for template.yml field names
- *(renovate)* Add rhiza template sync and disable automerge
- Add GitHub Actions workflow for rhiza template sync

### 🐛 Bug Fixes

- *(renovate)* Correct custom regex manager name in enabledManagers
- *(renovate)* Use fileMatch for custom regex manager
- *(renovate)* Allow rhiza materialize command in postUpgradeTasks
- Use heredoc for multi-line commit message in workflow
- Use PAT_TOKEN for workflow modifications in rhiza sync
- *(renovate)* Correct fileMatch field in custom regex manager

### 💼 Other

- Bump version 0.9.0 → 0.9.1

### 🚜 Refactor

- Make renovate regex more robust to handle fields between repository and ref

### 📚 Documentation

- Expand module-level docstrings in source files

### 🧪 Testing

- Document security exceptions in conftest.py

### ⚙️ Miscellaneous Tasks

- *(config)* Migrate config renovate.json
- *(config)* Migrate config renovate.json
- *(config)* Migrate config renovate.json
- Sync rhiza template files
- *(config)* Migrate config renovate.json
- Sync rhiza template files
- Sync rhiza template files
- Sync rhiza template files
- Sync rhiza template files
## [0.9.0] - 2026-02-13

### 💼 Other

- Bump version 0.8.7 → 0.9.0

### 🚜 Refactor

- Update template config and Renovate custom manager syntax

### ⚙️ Miscellaneous Tasks

- Update via rhiza
- Pin rhiza template to v0.7.1 and automate version updates
- Bump rhiza version requirement to 0.11.0
## [0.8.7] - 2026-01-30

### 🐛 Bug Fixes

- Resolve mypy type errors
- Add pandas-stubs to deptry package_module_name_map
- Resolve conftest import error in test_rhiza_workflows
- Resolve mypy strict mode errors
- Correct coverage badge URL capitalization

### 💼 Other

- Bump version 0.8.5 → 0.8.6
- Bump version 0.8.6 → 0.8.7

### ⚙️ Miscellaneous Tasks

- Update via rhiza
- Update via rhiza
- Update via rhiza
- Update via rhiza
## [0.8.5] - 2026-01-02

### 🐛 Bug Fixes

- *(deps)* Update dependency pre-commit to v4.5.1 (#498)

### ⚙️ Miscellaneous Tasks

- Sync template files
- Sync template files
- Sync template files
- Remove deprecated files
- Update via rhiza
- Bump version to 0.8.5
## [0.8.4] - 2025-12-12

### ⚙️ Miscellaneous Tasks

- Bump version to 0.8.4
## [0.8.3] - 2025-12-12

### ⚙️ Miscellaneous Tasks

- Bump version to 0.8.3
## [0.8.2] - 2025-12-12

### 🐛 Bug Fixes

- *(deps)* Update dependency marimo to v0.18.2
- *(deps)* Update dependency marimo to v0.18.3
- *(deps)* Update dependency pytest to v9.0.2
- *(deps)* Update dependency marimo to v0.18.4

### ⚙️ Miscellaneous Tasks

- Sync template files
- Bump version to 0.8.2
## [0.8.1] - 2025-12-02

### ⚙️ Miscellaneous Tasks

- Bump version to 0.8.1
## [0.8.0] - 2025-12-02

### 🐛 Bug Fixes

- *(deps)* Update dependency marimo to v0.17.6 (#442)
- *(deps)* Update dependency marimo to v0.17.7 (#443)
- *(deps)* Update dependency pre-commit to v4.4.0 (#447)
- *(deps)* Update dependency pytest to v9
- *(deps)* Update dependency pytest to v9.0.1
- *(deps)* Update dependency marimo to v0.18.0 (#457)
- *(deps)* Update dependency pre-commit to v4.5.0 (#458)
- *(deps)* Update dependency marimo to v0.18.1

### ⚙️ Miscellaneous Tasks

- Sync template files (#440)
- Sync template files (#441)
- Sync template files
- Sync template files
- Sync template files
- Sync template files
- Sync template files
- Sync template files
- Bump version to 0.8.0
## [0.7.24] - 2025-10-26

### 🐛 Bug Fixes

- *(deps)* Update dependency marimo to v0.15.3 (#391)
- *(deps)* Update dependency marimo to v0.15.5 (#397)
- *(deps)* Update dependency marimo to v0.16.0 (#400)
- *(deps)* Update dependency marimo to v0.16.1 (#404)
- *(deps)* Update dependency marimo to v0.16.2 (#412)
- *(deps)* Update dependency marimo to v0.16.3 (#417)
- *(deps)* Update dependency marimo to v0.16.5 (#422)
- *(deps)* Update dependency marimo to v0.17.0 (#430)
- *(deps)* Update dependency marimo to v0.17.2 (#435)

### ⚙️ Miscellaneous Tasks

- Sync config files from .config-templates (#395)
- Sync config files from .config-templates (#403)
- Sync template files (#409)
- Sync template files (#410)
- Sync template files (#415)
- Sync template files (#416)
- Sync template files (#419)
- Sync template files (#424)
- Sync template files (#429)
- Sync template files (#432)
## [0.7.23] - 2025-09-11

### 🐛 Bug Fixes

- *(deps)* Update dependency pytest to v8.4.1 (#350)
- *(deps)* Update dependency pre-commit to v4.3.0 (#364)
- *(deps)* Update dependency marimo to v0.14.17 (#369)
- *(deps)* Update dependency marimo to v0.15.0 (#378)
- *(deps)* Update dependency marimo to v0.15.2 (#382)
- *(deps)* Update dependency pytest to v8.4.2 (#385)

### ⚙️ Miscellaneous Tasks

- Sync config files from .config-templates (#348)
- Sync config files from .config-templates (#351)
- Sync config files from .config-templates (#356)
- Sync config files from .config-templates (#362)
- Sync config files from .config-templates (#363)
- Sync config files from .config-templates (#368)
- Sync config files from .config-templates (#372)
- Sync config files from .config-templates (#375)
- Sync config files from .config-templates (#377)
- Sync config files from .config-templates (#381)
- Sync config files from .config-templates (#387)
- Sync config files from .config-templates (#389)
## [0.7.21] - 2025-07-01

### 🐛 Bug Fixes

- *(deps)* Update dependency pytest to v8.4.0 (#319)
- *(deps)* Update dependency pytest to v8.4.1 (#328)
## [0.7.18] - 2025-05-26

### ⚙️ Miscellaneous Tasks

- *(config)* Migrate config .github/renovate.json (#287)
## [0.3.2] - 2023-08-16

### 🎨 Styling

- Format code with black and isort (#63)
## [0.2.9] - 2023-05-15

### 🚜 Refactor

- Remove assert statement from non-test files (#43)

### 🎨 Styling

- Format code with black and isort (#32)
## [0.2.1] - 2023-01-14
