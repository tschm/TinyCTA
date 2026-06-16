# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and entries are generated from [Conventional Commits](https://www.conventionalcommits.org).

## [0.13.3] - 2026-06-16

### New Features
- *(typing)* Ship py.typed marker (PEP 561) (#785)

### Bug Fixes
- Address P0 repo-quality gaps (#760, #761, #762)
- *(ci)* Make hyper deps available to the lowest-deps job
- *(engine)* Date-align cash_position; add end-to-end tutorial (#805)

### Documentation
- Fix doc accuracy for current API (#763, #764)
- Add API reference pages for all public modules
- Add OpenSSF Scorecard badge to README (closes #782) (#802)

### Maintenance
- Achieve 100% coverage for hyper/_study.py
- Chore(deps)(deps): bump the python-dependencies group with 4 updates
- Chore(deps)(deps): bump the github-actions group with 4 updates
- P2 polish — optional hyper extra, engine docstring, signal property tests
- Replace brittle magic-float assertion in test_signal (#787)
- Decompose Engine.cash_position into named helpers (#791)
- Enable branch coverage in CI (#788)
- Harden RHIZA CI triggers with concurrency, docs path filters, and SHA pin (#793)
- Gate mutmut in CI (#789)
- Chore(deps)(deps): bump the python-dependencies group with 4 updates (#797)
- Add Rhiza Claude commands (/rhiza_quality, /rhiza_update) (#795)
- Chore(deps)(deps): bump python-multipart from 0.0.30 to 0.0.31 (#798)
- Chore(deps)(deps): bump starlette from 1.2.1 to 1.3.1 (#799)
- Chore(deps)(deps): bump the github-actions group with 10 updates (#796)
- *(engine)* Accurate cor key typing + guarded divide (#806)

### Other Changes
- Merge pull request #758 from tschm/dependabot/uv/python-dependencies-a20c5222c7
- Merge pull request #757 from tschm/dependabot/github_actions/github-actions-7ad05fae5e
- Merge pull request #768 from tschm/fix/p0-quality-gaps
- Merge pull request #769 from tschm/docs/p1-doc-accuracy
- Merge pull request #770 from tschm/chore/p2-polish
- Merge pull request #786 from tschm/docs/api-reference-771
- Surface security scanning as a first-class CI gate (#792)
- Pin ty and extend typecheck to tests (#790)
- Sync Rhiza template v0.18.8 → v0.19.3 (#800)
- Fix docs book build: install tinycta into mkdocstrings uvx env (#801)

## [0.13.2] - 2026-06-06

### Maintenance
- Apply rhiza v0.18.8 template updates

### Other Changes
- Clean up public API imports in optimizer.md
- Merge pull request #756 from tschm/rhiza_v0.18.8
- Bump version 0.13.1 → 0.13.2

## [0.13.1] - 2026-06-04

### Bug Fixes
- *(hyper)* Restore missing docstring on inner objective function

### Documentation
- Add optimizer.md documenting tinycta.hyper usage

### Maintenance
- *(hyper)* Suggest_portfolio_fn returns Portfolio directly

### Other Changes
- Bump version 0.13.0 → 0.13.1

## [0.13.0] - 2026-06-04

### New Features
- *(hyper)* Introduce Study dataclass and optimize wrapper

### Bug Fixes
- Update cvx.linalg import path and bump polars minimum to 1.21.0
- Increase tolerance in test_moving_absolute_deviation
- *(hyper)* Fix stale run_study references and patch path in tests
- *(hyper)* Guard best_params/best_value access in Study.from_optuna

### Documentation
- Add missing docstring to _load_yaml to reach 100% docs coverage

### Maintenance
- Apply rhiza sync v0.18.4
- Add classifiers to pyproject.toml
- Add pip dependabot entry for .rhiza/requirements
- Chore(deps)(deps): bump the python-dependencies group across 1 directory with 3 updates
- Chore(deps)(deps): bump the github-actions group with 8 updates
- Chore(deps)(deps): bump the github-actions group with 9 updates
- Chore(deps)(deps): bump the python-dependencies group with 5 updates
- Remove plotly as explicit dependency

### Other Changes
- Merge pull request #749 from tschm/rhiza_v0.18.4
- Merge pull request #751 from tschm/dependabot/uv/python-dependencies-c993449c2e
- Merge branch 'main' into dependabot/github_actions/github-actions-f379237d3f
- Merge pull request #750 from tschm/dependabot/github_actions/github-actions-f379237d3f
- Merge pull request #753 from tschm/dependabot/github_actions/github-actions-74b91dd3f0
- Merge pull request #754 from tschm/dependabot/uv/python-dependencies-c09406e6c5
- Merge pull request #752 from tschm/hyperYU
- Bump version 0.12.5 → 0.13.0

## [0.12.5] - 2026-05-27

### New Features
- Add profiles: github-project to template.yml

### Bug Fixes
- Remove leading newline from .python-version

### Maintenance
- Sync with rhiza v0.11.0
- Sync rhiza to v0.16.1
- Sync rhiza to v0.15.1 with conflict resolution
- Remove extra blank lines in rhiza API tests
- Apply rhiza sync v0.15.2
- Apply rhiza sync v0.15.3
- Apply rhiza sync v0.17.0

### Other Changes
- Bump rhiza template version v0.10.3 → v0.10.9
- Sync rhiza template to v0.10.9
- Rename template entries tests→github-tests, book→github-book
- Sync rhiza template — restore missing workflow files
- Merge pull request #741 from tschm/rhiza222
- Copy rhiza_*.yml workflows from cvxrisk
- Sync .rhiza/tests from cvxrisk
- Merge pull request #743 from tschm/rhizaMove
- Merge pull request #745 from tschm/RhizaSync
- Merge pull request #747 from tschm/rhiza_v0.15.3
- Merge pull request #748 from tschm/rhiza_v0.17.0
- Bump version 0.12.4 → 0.12.5

## [0.12.4] - 2026-05-21

### Bug Fixes
- *(readme)* Round solve output to suppress floating-point noise from cvx-linalg 0.5.1

### Maintenance
- *(linalg)* Adapt tests to cvx-linalg 0.5.1 exception types
- Chore(deps)(deps): bump github/codeql-action in the github-actions group
- Chore(deps)(deps): bump the python-dependencies group with 2 updates
- Chore(deps)(deps): bump idna from 3.11 to 3.15
- Chore(deps)(deps): bump pymdown-extensions from 10.21.2 to 10.21.3

### Other Changes
- Merge pull request #736 from tschm/linalg-242
- Merge pull request #737 from tschm/dependabot/github_actions/github-actions-bcb0c4251a
- Merge pull request #738 from tschm/dependabot/uv/python-dependencies-ed654ffc18
- Merge pull request #739 from tschm/dependabot/uv/idna-3.15
- Merge pull request #740 from tschm/dependabot/uv/pymdown-extensions-10.21.3
- Bump version 0.12.3 → 0.12.4

## [0.12.3] - 2026-05-17

### Maintenance
- *(signal)* Replace pandas with polars in moving_absolute_deviation

### Other Changes
- Merge pull request #735 from tschm/pandas
- Bump version 0.12.2 → 0.12.3

## [0.12.2] - 2026-05-15

### Bug Fixes
- *(osc)* Switch ewm_mean to adjust=True for unbiased EWMA
- *(test_osc)* Update reference to use adjust=True to match osc()

### Other Changes
- Bump version 0.12.1 → 0.12.2

## [0.12.1] - 2026-05-15

### Documentation
- *(readme)* Update osc() signature to remove vola parameter

### Maintenance
- *(osc)* Replace EWMA-std scaling with analytical scaling factor

### Other Changes
- Bump version 0.12.0 → 0.12.1

## [0.12.0] - 2026-05-14

### New Features
- *(ewm_cov)* Add ewm_covariance function with tests
- *(engine)* Remove pyarrow dependency by using ewm_covariance
- *(ewm_cov)* Delegate to cvx.linalg 0.4.1, achieve 100% test coverage

### Bug Fixes
- *(deptry)* Map cvx-linalg to cvx namespace in package_module_name_map
- *(deptry)* Add all packages to package_module_name_map to silence warnings

### Dependencies
- *(deps)* Add cvx-linalg as dev dependency

### Maintenance
- Chore(deps-dev)(deps-dev): bump the python-dependencies group with 2 updates
- Chore(deps-dev)(deps-dev): bump marimo in the python-dependencies group
- Chore(deps)(deps): bump github/codeql-action in the github-actions group
- Chore(deps)(deps): bump mako from 1.3.11 to 1.3.12
- Chore(deps)(deps): bump github/codeql-action in the github-actions group
- Chore(deps)(deps): bump the python-dependencies group with 3 updates
- *(linalg)* Replace implementation with thin wrapper around cvx.linalg

### Other Changes
- Merge pull request #725 from tschm/dependabot/uv/python-dependencies-4dbcc8583a
- Merge pull request #727 from tschm/dependabot/uv/python-dependencies-189a206c4b
- Merge pull request #726 from tschm/dependabot/github_actions/github-actions-937d73b4db
- Merge pull request #728 from tschm/dependabot/uv/mako-1.3.12
- Merge pull request #729 from tschm/dependabot/github_actions/github-actions-8abaa2cbc6
- Merge pull request #730 from tschm/dependabot/uv/python-dependencies-3d4d314338
- Merge pull request #731 from tschm/cvxlinalg
- Merge pull request #732 from tschm/ewm_cov
- Merge pull request #733 from tschm/test_pyarrow
- Merge pull request #734 from tschm/ewm_cov2
- Bump version 0.11.0 → 0.12.0

## [0.11.0] - 2026-04-26

### New Features
- Add optuna, loguru, and pyyaml dependencies
- Add hyper module with experiment config and optuna study runner

### Maintenance
- Add pyyaml import mapping and remove mypy config

### Other Changes
- Merge pull request #723 from tschm/hyper
- Bump version 0.10.0 → 0.11.0

## [0.10.0] - 2026-04-26

### New Features
- Add engine with pydantic, pyarrow dependencies

### Bug Fixes
- Suppress DEP002 for pyarrow and fix ty type error in engine

### Documentation
- Update README to reflect Polars-based API

### Maintenance
- Remove osc and returns_adjust tests
- Bring engine coverage to 100%
- Fix import order in engine.py

### Other Changes
- Vol adjusting with polars
- Remove osc and returns_adjust functions
- Merge pull request #721 from tschm/tschm-patch-1
- Update module imports to relative paths
- Merge pull request #722 from tschm/engine
- Bump version 0.9.9 → 0.10.0

## [0.9.9] - 2026-04-25

### New Features
- Add polars dependency and ewma/osc modules with tests

### Other Changes
- Merge pull request #720 from tschm/polars
- Bump version 0.9.8 → 0.9.9

## [0.9.8] - 2026-04-25

### Maintenance
- Chore(deps-dev)(deps-dev): bump marimo in the python-dependencies group
- Update via rhiza
- Sync with rhiza template v0.10.3

### Other Changes
- Merge pull request #717 from tschm/dependabot/uv/python-dependencies-763d8570f9
- Merge pull request #716 from tschm/rhiza/24643027654
- Merge pull request #718 from tschm/dependabot/pip/dot-rhiza/requirements/python-dotenv-1.2.2
- Update repository reference version to v0.10.3
- Merge pull request #719 from tschm/tschm-patch-security
- Bump version 0.9.7 → 0.9.8

## [0.9.7] - 2026-04-18

### Other Changes
- Simpler sync
- Simpler sync
- Simpler sync
- Remove broken test_mkdocs_extra_packages_used_in_build test
- Remove gh-pages branch: serve coverage badge from Pages site
- Fix coverage badge link path: tests → reports
- Rhiza template sync v0.10.1: remove Copilot/gh-pages artifacts, update coverage badge
- Remove excluded files from template.yml
- Merge pull request #715 from tschm/tschm-patch-1
- Bump version 0.9.6 → 0.9.7

## [0.9.6] - 2026-04-18

### Bug Fixes
- Remove duplicate security target from Makefile
- Remove mkdocs-build:: to resolve double/single colon conflict
- Remove HTML div wrapper from README to fix MkDocs rendering
- Correct nav paths from report/ to reports/ in mkdocs.yml
- Fix MKDOCS_EXTRA_PACKAGES quoting and package name typo

### Documentation
- Add mkdocs.yml inheriting from docs/mkdocs-base.yml
- Add CI/CD section with Hypothesis to mkdocs nav

### Dependencies
- *(deps)* Update pre-commit hook jebel-quant/rhiza-hooks to v0.3.3 (#700)
- *(deps)* Lock file maintenance
- *(deps)* Update dependency jebel-quant/rhiza to v0.9.5
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.15.11 (#707)
- *(deps)* Update astral-sh/setup-uv action to v8.1.0

### Maintenance
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

### Other Changes
- Merge pull request #701 from tschm/renovate/lock-file-maintenance
- Merge pull request #703 from tschm/renovate/jebel-quant-rhiza-0.x
- Merge pull request #704 from tschm/rhiza/update-v0.10.0
- Delete issues directory
- Merge pull request #705 from tschm/tschm-patch-1
- Include reports
- Delete .rhiza/docs directory
- Merge pull request #706 from tschm/tschm-patch-1
- Merge pull request #708 from tschm/renovate/astral-sh-setup-uv-8.x
- Initial plan
- Integrate mkdocstrings: add plugin config and API reference pages
- Apply suggestion from @Copilot
- Apply suggestion from @Copilot
- Merge pull request #712 from tschm/copilot/integrate-mkdocstrings
- Book with mkdocstrings
- Install tinycta into uvx env for mkdocstrings
- Align docstring style to Google convention throughout
- Slim down docs.txt
- Initial plan
- Add moving_absolute_deviation as robust alternative to moving variance
- Use rolling median instead of ewm mean in moving_absolute_deviation for robustness
- Potential fix for pull request finding
- Merge pull request #710 from tschm/copilot/add-moving-absolute-deviation
- Remove default AI model and engine from Makefile
- Scale moving_absolute_deviation by 1/0.6745 for std consistency
- Fix moving_absolute_deviation docstring to Google style
- No window for rolling median (rely on the standard instead)
- Bump version 0.9.5 → 0.9.6

## [0.9.5] - 2026-04-12

### Bug Fixes
- Ignore CVE-2026-4539 in pygments (no fix available yet)
- Ensure _book directory exists when mkdocs.yml is absent

### Documentation
- Update SECURITY.md to reference TinyCTA instead of Rhiza

### Dependencies
- *(deps)* Lock file maintenance
- *(deps)* Update pre-commit hook jebel-quant/rhiza-hooks to v0.3.1 (#657)
- *(deps)* Lock file maintenance
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.11.1
- *(deps)* Update dependency astral-sh/uv to v0.11.1
- *(deps)* Update actions/deploy-pages action to v5
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.15.8 (#663)
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.37.1 (#664)
- *(deps)* Update dependency astral-sh/uv to v0.11.2 (#665)
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.11.2 (#666)
- *(deps)* Update github/codeql-action action to v4.35.1
- *(deps)* Lock file maintenance (#669)
- *(deps)* Update astral-sh/setup-uv action to v8
- *(deps)* Update pre-commit hook rhysd/actionlint to v1.7.12 (#671)
- *(deps)* Update dependency marimo to v0.22.0 (#674)
- *(deps)* Update dependency jebel-quant/rhiza to v0.8.19
- *(deps)* Update dependency astral-sh/uv to v0.11.3 (#675)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.15.9 (#679)
- *(deps)* Update dependency marimo to v0.22.4 (#678)
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.11.3 (#680)
- *(deps)* Update pre-commit hook jebel-quant/rhiza-hooks to v0.3.2 (#681)
- *(deps)* Update docker/login-action action to v4.1.0 (#683)
- *(deps)* Update astral-sh/setup-uv action to v8
- *(deps)* Update dependency marimo to v0.22.5 (#687)
- *(deps)* Update dependency marimo to v0.23.0 [security] (#689)
- *(deps)* Update dependency astral-sh/uv to v0.11.5
- *(deps)* Update dependency astral-sh/uv to v0.11.6 (#691)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.15.10 (#692)
- *(deps)* Update actions/upload-artifact action to v7.0.1 (#693)
- *(deps)* Update peter-evans/create-pull-request action to v8.1.1 (#694)
- *(deps)* Update dependency marimo to v0.23.1 (#695)
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.11.6 (#696)

### Maintenance
- Resolve rhiza template sync conflicts and apply patch updates
- Sync rhiza template files
- Chore(deps)(deps): bump pandas in the python-dependencies group
- Apply rhiza template sync and resolve merge conflicts

### Other Changes
- Merge pull request #656 from tschm/renovate/lock-file-maintenance
- Merge pull request #658 from tschm/renovate/lock-file-maintenance
- Merge pull request #661 from tschm/renovate/astral-sh-uv-pre-commit-0.x
- Merge pull request #660 from tschm/renovate/astral-sh-uv-0.x
- Merge pull request #662 from tschm/renovate/actions-deploy-pages-5.x
- Merge pull request #667 from tschm/renovate/github-codeql-action-4.x
- Merge pull request #668 from tschm/renovate/astral-sh-setup-uv-8.x
- Update ref version from v0.8.16 to v0.8.17
- Merge pull request #672 from tschm/tschm-patch-300
- Remove CVE-2026-4539 exception from pip-audit
- Update Makefile
- Update Semgrep config file path in Makefile
- Merge pull request #673 from tschm/renovate/jebel-quant-rhiza-0.x
- Merge pull request #686 from tschm/dependabot/uv/python-dependencies-40001dd672
- Merge pull request #685 from tschm/renovate/astral-sh-setup-uv-8.x
- Merge pull request #690 from tschm/renovate/astral-sh-uv-0.x
- Update repository reference to version 0.9.1
- Merge pull request #697 from tschm/tschm-patch-400
- Update repository reference to version 0.9.2
- Sync
- Merge pull request #699 from tschm/tschm-patch-401
- Bump version 0.9.4 → 0.9.5

## [0.9.4] - 2026-03-22

### Bug Fixes
- Update coverage badge URL to gh-pages SVG

### Dependencies
- *(deps)* Update dependency marimo to v0.21.1 (#643)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.15.7 (#645)
- *(deps)* Update dependency jebel-quant/rhiza to v0.8.14
- *(deps)* Update dependency astral-sh/uv to v0.10.12 (#646)
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.10.12
- *(deps)* Update github/codeql-action action to v4.34.1 (#649)
- *(deps)* Lock file maintenance

### Maintenance
- Sync rhiza template files

### Other Changes
- Merge pull request #644 from tschm/renovate/jebel-quant-rhiza-0.x
- Merge pull request #647 from tschm/renovate/astral-sh-uv-pre-commit-0.x
- Update ref version from v0.8.14 to v0.8.16
- Sync
- Merge pull request #650 from tschm/tschm-patch-1
- LICENSE in pyproject
- LICENSE in pyproject
- Initial plan
- Merge pull request #652 from tschm/copilot/fix-broken-badge
- Merge pull request #653 from tschm/renovate/lock-file-maintenance
- Initial plan
- Replace hardcoded Rhiza badge version with dynamic shields.io badge
- Merge pull request #655 from tschm/copilot/update-rhiza-version-badge
- Bump version 0.9.3 → 0.9.4

## [0.9.3] - 2026-03-17

### Bug Fixes
- Resolve merge conflicts in workflow files for setup-uv v7.5.0

### Dependencies
- *(deps)* Update actions/download-artifact action to v8.0.1 (#632)
- *(deps)* Update dependency astral-sh/uv to v0.10.10 (#633)
- *(deps)* Update dependency jebel-quant/rhiza to v0.8.12
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.10.10 (#635)
- *(deps)* Update ncipollo/release-action action to v1.21.0
- *(deps)* Update astral-sh/setup-uv action to v7.6.0 (#638)
- *(deps)* Update dependency marimo to v0.21.0

### Maintenance
- Sync rhiza template files
- Remove benchmark workflow and tests, update template.lock

### Other Changes
- Merge pull request #634 from tschm/renovate/jebel-quant-rhiza-0.x
- Merge pull request #636 from tschm/renovate/ncipollo-release-action-1.x
- Merge pull request #639 from tschm/renovate/marimo-0.x
- Bump version reference to v0.8.13
- Merge pull request #641 from tschm/tschm-patch-160
- Merge pull request #642 from tschm/tschm-patch-160
- Bump version 0.9.2 → 0.9.3

## [0.9.2] - 2026-03-11

### Bug Fixes
- Resolve merge conflicts keeping uv 0.10.9

### Dependencies
- *(deps)* Update dependency astral-sh/uv to v0.10.6 (#601)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.15.4
- *(deps)* Update dependency astral-sh/uv to v0.10.7
- *(deps)* Update astral-sh/setup-uv action to v7.3.1
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.37.0 (#605)
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.10.7
- *(deps)* Lock file maintenance
- *(deps)* Lock file maintenance (#613)
- *(deps)* Update github/codeql-action action to v4.32.5 (#614)
- *(deps)* Update pre-commit hook igorshubovych/markdownlint-cli to v0.48.0 (#617)
- *(deps)* Update dependency marimo to v0.20.4
- *(deps)* Update dependency astral-sh/uv to v0.10.8 (#618)
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.10.8
- *(deps)* Update dependency astral-sh/uv to v0.10.9 (#620)
- *(deps)* Update github/codeql-action action to v4.32.6
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.15.5 (#622)
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.10.9
- *(deps)* Lock file maintenance (#625)
- *(deps)* Update docker/login-action action to v4
- *(deps)* Update dependency jebel-quant/rhiza to v0.8.7
- *(deps)* Update astral-sh/setup-uv action to v7.4.0 (#630)
- *(deps)* Update dependency jebel-quant/rhiza to v0.8.9

### Maintenance
- Chore(deps-dev)(deps-dev): bump plotly in the python-dependencies group
- Sync rhiza template files
- Chore(deps)(deps): bump numpy in the python-dependencies group
- Sync rhiza template files

### Other Changes
- Update Rhiza version to 0.11.4-rc.1
- Bump version from 0.11.4-rc.1 to 0.11.4-rc.2
- Update version format in .rhiza-version file
- Sync
- Remove stale .rhiza/history file
- Merge pull request #602 from tschm/renovate/astral-sh-ruff-pre-commit-0.x
- Merge pull request #604 from tschm/renovate/astral-sh-uv-0.x
- Merge pull request #603 from tschm/renovate/astral-sh-setup-uv-7.x
- Sync
- Merge pull request #611 from tschm/renovate/astral-sh-uv-pre-commit-0.x
- Merge pull request #609 from tschm/renovate/lock-file-maintenance
- Merge pull request #615 from tschm/dependabot/uv/python-dependencies-698941b3fe
- Merge pull request #616 from tschm/renovate/marimo-0.x
- Merge pull request #619 from tschm/renovate/astral-sh-uv-pre-commit-0.x
- Merge pull request #621 from tschm/renovate/github-codeql-action-4.x
- Merge pull request #623 from tschm/renovate/astral-sh-uv-pre-commit-0.x
- Merge pull request #624 from tschm/renovate/docker-login-action-4.x
- Merge pull request #627 from tschm/renovate/jebel-quant-rhiza-0.x
- Merge pull request #628 from tschm/dependabot/uv/python-dependencies-9e55b512a1
- Merge pull request #629 from tschm/renovate/jebel-quant-rhiza-0.x
- Remove 'marimo' from template.yml components
- Remove marimo books
- Merge pull request #631 from tschm/tschm-patch-140
- Bump version 0.9.1 → 0.9.2

## [0.9.1] - 2026-02-24

### New Features
- Make renovate.json flexible for template.yml field names
- *(renovate)* Add rhiza template sync and disable automerge
- Add GitHub Actions workflow for rhiza template sync

### Bug Fixes
- *(renovate)* Correct custom regex manager name in enabledManagers
- *(renovate)* Use fileMatch for custom regex manager
- *(renovate)* Allow rhiza materialize command in postUpgradeTasks
- Use heredoc for multi-line commit message in workflow
- Use PAT_TOKEN for workflow modifications in rhiza sync
- *(renovate)* Correct fileMatch field in custom regex manager

### Documentation
- Expand module-level docstrings in source files

### Dependencies
- *(deps)* Lock file maintenance
- *(deps)* Update dependency jebel-quant/rhiza to v0.7.4
- *(deps)* Update dependency jebel-quant/rhiza to v0.7.5
- *(deps)* Lock file maintenance (#578)
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.36.2 (#579)
- *(deps)* Update pre-commit hook rhysd/actionlint to v1.7.11
- *(deps)* Lock file maintenance
- *(deps)* Update actions/download-artifact action to v7
- *(deps)* Update dependency jebel-quant/rhiza to v0.8.0
- *(deps)* Update dependency astral-sh/uv to v0.10.3 (#584)
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.10.3
- *(deps)* Update dependency astral-sh/uv to v0.10.4 (#586)
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.10.4 (#587)
- *(deps)* Update github/codeql-action action to v4.32.4 (#588)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.15.2 (#589)
- *(deps)* Update dependency marimo to v0.20.1 (#590)
- *(deps)* Update dependency marimo to v0.20.2 (#591)
- *(deps)* Lock file maintenance (#592)
- *(deps)* Update dependency jebel-quant/rhiza to v0.8.2
- *(deps)* Update dependency astral-sh/uv to v0.10.5 (#597)
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.10.5
- *(deps)* Lock file maintenance
- *(deps)* Update dependency jebel-quant/rhiza to v0.8.3

### Maintenance
- Make renovate regex more robust to handle fields between repository and ref
- *(config)* Migrate config renovate.json
- *(config)* Migrate config renovate.json
- *(config)* Migrate config renovate.json
- Sync rhiza template files
- *(config)* Migrate config renovate.json
- Sync rhiza template files
- Sync rhiza template files
- Sync rhiza template files
- Document security exceptions in conftest.py
- Sync rhiza template files

### Other Changes
- Initial plan
- Merge pull request #567 from tschm/copilot/update-renovate-json-flexibility
- Merge pull request #568 from tschm/renovate/migrate-config
- Merge pull request #569 from tschm/renovate/lock-file-maintenance
- Merge pull request #570 from tschm/renovate/migrate-config
- Merge pull request #573 from tschm/renovate/migrate-config
- Delete .github/workflows/codeql.yml
- Merge pull request #575 from tschm/renovate/jebel-quant-rhiza-0.x
- Merge pull request #576 from tschm/renovate/migrate-config
- Merge pull request #577 from tschm/renovate/jebel-quant-rhiza-0.x
- Merge pull request #580 from tschm/renovate/rhysd-actionlint-1.x
- Merge pull request #583 from tschm/renovate/lock-file-maintenance
- Merge pull request #582 from tschm/renovate/major-github-artifact-actions
- Merge pull request #581 from tschm/renovate/jebel-quant-rhiza-0.x
- Merge pull request #585 from tschm/renovate/astral-sh-uv-pre-commit-0.x
- Add 'renovate' and 'gh-aw' to template.yml
- Merge pull request #593 from tschm/renovate/jebel-quant-rhiza-0.x
- Towards hypothesis test
- Assign issue #594 to copilot
- Assign issue #594 to Copilot
- Initial plan
- Add Rhiza badge to README.md with version from .rhiza/template.yml
- Merge pull request #595 from tschm/copilot/add-rhiza-badge-display
- Update .cfg.toml
- Merge pull request #596 from tschm/tschm-patch-1
- Merge pull request #599 from tschm/renovate/astral-sh-uv-pre-commit-0.x
- Merge pull request #600 from tschm/renovate/lock-file-maintenance
- Merge pull request #598 from tschm/renovate/jebel-quant-rhiza-0.x
- Bump version 0.9.0 → 0.9.1

## [0.9.0] - 2026-02-13

### Dependencies
- *(deps)* Lock file maintenance (#536)
- *(deps)* Update pre-commit hook abravalheri/validate-pyproject to v0.25
- *(deps)* Update pre-commit hook jebel-quant/rhiza-hooks to v0.1.3
- *(deps)* Update github/codeql-action action to v4.32.1
- *(deps)* Update dependency marimo to v0.19.7
- *(deps)* Lock file maintenance (#542)
- *(deps)* Update dependency marimo to v0.19.9 (#546)
- *(deps)* Update github/codeql-action action to v4.32.2
- *(deps)* Update astral-sh/setup-uv action to v7.3.0
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.30
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.15.0
- *(deps)* Update dependency astral-sh/uv to v0.10.0
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.10.1
- *(deps)* Update pre-commit hook jebel-quant/rhiza-hooks to v0.2.1
- *(deps)* Update dependency astral-sh/uv to v0.10.1
- *(deps)* Lock file maintenance
- *(deps)* Update dependency astral-sh/uv to v0.10.2 (#558)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.15.1
- *(deps)* Update dependency marimo to v0.19.11
- *(deps)* Update github/codeql-action action to v4.32.3
- *(deps)* Update pre-commit hook astral-sh/uv-pre-commit to v0.10.2
- *(deps)* Lock file maintenance

### Maintenance
- Update via rhiza
- Pin rhiza template to v0.7.1 and automate version updates
- Update template config and Renovate custom manager syntax

### Other Changes
- Merge pull request #537 from tschm/rhiza/21573163073
- Sync
- Merge pull request #541 from tschm/renovate/abravalheri-validate-pyproject-0.x
- Merge pull request #540 from tschm/renovate/jebel-quant-rhiza-hooks-0.x
- Merge pull request #539 from tschm/renovate/github-codeql-action-4.x
- Merge pull request #538 from tschm/renovate/marimo-0.x
- Delete tests/test_rhiza directory
- Merge pull request #545 from tschm/tschm-patch-2
- Update template.yml include and exclude lists
- Merge pull request #544 from tschm/tschm-patch-1
- Merge pull request #548 from tschm/renovate/github-codeql-action-4.x
- Merge pull request #549 from tschm/renovate/astral-sh-setup-uv-7.x
- Merge pull request #547 from tschm/renovate/ghcr.io-astral-sh-uv-0.x
- Merge pull request #551 from tschm/renovate/astral-sh-ruff-pre-commit-0.x
- Merge pull request #550 from tschm/renovate/astral-sh-uv-0.x
- Update template.yml
- Sync
- Merge pull request #552 from tschm/tschm-patch-1
- Merge pull request #554 from tschm/renovate/astral-sh-uv-pre-commit-0.x
- Merge pull request #555 from tschm/renovate/jebel-quant-rhiza-hooks-0.x
- Merge pull request #553 from tschm/renovate/astral-sh-uv-0.x
- Merge pull request #556 from tschm/renovate/lock-file-maintenance
- Update .pre-commit-config.yaml
- Remove check-template-bundles hook from config
- Merge pull request #557 from tschm/rhiza_branch
- Merge pull request #561 from tschm/renovate/astral-sh-ruff-pre-commit-0.x
- Merge pull request #559 from tschm/renovate/marimo-0.x
- Merge pull request #560 from tschm/renovate/github-codeql-action-4.x
- Merge pull request #562 from tschm/renovate/astral-sh-uv-pre-commit-0.x
- Merge pull request #563 from tschm/renovate/lock-file-maintenance
- Bump version 0.8.7 → 0.9.0

## [0.8.7] - 2026-01-30

### Bug Fixes
- Resolve mypy type errors
- Add pandas-stubs to deptry package_module_name_map
- Resolve conftest import error in test_rhiza_workflows
- Resolve mypy strict mode errors
- Correct coverage badge URL capitalization

### Dependencies
- *(deps)* Lock file maintenance (#509)
- *(deps)* Update dependency astral-sh/uv to v0.9.22 (#511)
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.22 (#512)
- *(deps)* Lock file maintenance (#513)
- *(deps)* Lock file maintenance (#515)
- *(deps)* Update dependency marimo to v0.19.2 (#517)
- *(deps)* Update pre-commit hook pycqa/bandit to v1.9.2
- *(deps)* Update dependency marimo to v0.19.4
- *(deps)* Lock file maintenance (#527)
- *(deps)* Update pre-commit hook pycqa/bandit to v1.9.3 (#529)
- *(deps)* Lock file maintenance (#530)
- *(deps)* Update dependency marimo to v0.19.6 (#532)
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.27
- *(deps)* Update dependency astral-sh/uv to v0.9.27
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.36.1

### Maintenance
- Update via rhiza
- Update via rhiza
- Testing Rhiza
- Update via rhiza
- Update via rhiza

### Other Changes
- Update README.md
- Update README.md
- Dependencies
- Merge pull request #510 from tschm/rhiza/20701445902
- Rhiza
- Merge pull request #516 from tschm/rhiza/20904376231
- Sync
- Rhiza
- Bump version 0.8.5 → 0.8.6
- Rhiza
- Parso issue
- Initial plan
- Add deptry package module name map configuration
- Format deptry config as multiline for better readability
- Merge pull request #519 from tschm/copilot/configure-package-module-map
- Delete .rhiza.env
- Merge pull request #520 from tschm/tschm-patch-1
- Sync
- Delete .github/workflows/rhiza_devcontainer.yml
- Delete .github/workflows/rhiza_docker.yml
- Update excluded workflow files in template.yml
- Update template.yml
- Remove dependabot
- Add CLAUDE.md for Claude Code guidance
- Update .pre-commit-config.yaml
- Fmt
- Merge pull request #526 from tschm/renovate/pycqa-bandit-1.x
- Fmt
- Merge pull request #525 from tschm/renovate/marimo-0.x
- Merge pull request #528 from tschm/rhiza/21121218910
- Merge pull request #531 from tschm/rhiza/21342222583
- Merge pull request #535 from tschm/renovate/ghcr.io-astral-sh-uv-0.x
- Merge pull request #534 from tschm/renovate/astral-sh-uv-0.x
- Merge pull request #533 from tschm/renovate/python-jsonschema-check-jsonschema-0.x
- Delete book/marimo/.gitkeep
- Sync
- Bump version 0.8.6 → 0.8.7

## [0.8.5] - 2026-01-02

### Bug Fixes
- *(deps)* Update dependency pre-commit to v4.5.1 (#498)

### Dependencies
- *(deps)* Lock file maintenance (#488)
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.36.0 (#490)
- *(deps)* Lock file maintenance (#496)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.14.10 (#497)
- *(deps)* Lock file maintenance (#500)
- *(deps)* Update dependency astral-sh/uv to v0.9.20 (#502)
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.20 (#503)

### Maintenance
- Sync template files
- Sync template files
- Sync template files
- Remove deprecated files
- Update via rhiza
- Chore(deps)(deps): bump actions/checkout from 4 to 6

### Other Changes
- Remove effort to publish on GitHub
- Update template repository in template.yml
- Delete tests/test_config_templates directory
- Merge pull request #486 from tschm/template-updates
- Merge pull request #487 from tschm/template-updates
- Update repository reference in post-release script
- Delete .github/scripts/post-release.sh
- Remove unnecessary comment from LICENSE file
- Delete .github/workflows/devcontainer.yml
- Delete .github/workflows/docker.yml
- Delete .github/workflows/structure.yml
- Delete .github/scripts/build-extras.sh
- Delete .github/workflows/devcontainer.yml
- Delete .github/workflows/docker.yml
- Merge pull request #489 from tschm/template-updates
- Fmt
- Add Rhiza config validation step in CI workflow
- Merge pull request #492 from tschm/tschm-patch-1
- Enhance sync workflow with validation and PR creation
- Update sync workflow for configuration synchronization
- Remove effort to publish on GitHub
- Remove effort to publish on GitHub
- Sync
- Sync
- Initial plan
- Fix PAT_TOKEN usage in sync workflow and add comprehensive documentation
- Add early PAT_TOKEN validation step to sync workflow
- Use environment variable for consistent PAT_TOKEN checking
- Merge pull request #494 from tschm/copilot/fix-token-push-error
- Rhiza
- Delete .github/scripts/sync.sh
- Delete .github/README.md
- Rhiza
- Merge pull request #495 from tschm/cleanup/delete-files
- Remove rhiza as dependency
- Rhiza
- Book
- Book
- Create codeql.yml
- Remove test_rhiza for a second
- Rhiza
- Towards .rhiza
- Update of template.yml
- Update rhiza_pre-commit.yml
- Merge pull request #501 from tschm/rhiza/20561658141
- Merge pull request #505 from tschm/dependabot/github_actions/actions/checkout-6
- Python version
- Python dotenv
- Rizha.env
- Rhiza
- Initial plan
- Add professional header for README with tagline and quick links
- Merge pull request #507 from tschm/copilot/add-professional-header-readme
- Update README.md
- Update README.md
- Fix link case in TinyCTA README
- Update link text from 'Documentation' to 'Repository'

## [0.8.4] - 2025-12-12

### Other Changes
- Install uv in release
- With package name
- With package name

## [0.8.3] - 2025-12-12

### Other Changes
- Data for README
- Simpler install of uv

## [0.8.2] - 2025-12-12

### Bug Fixes
- *(deps)* Update dependency marimo to v0.18.2
- *(deps)* Update dependency marimo to v0.18.3
- *(deps)* Update dependency pytest to v9.0.2
- *(deps)* Update dependency marimo to v0.18.4
- Fixing README
- Fix readme tes

### Dependencies
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.15 (#472)
- *(deps)* Lock file maintenance (#474)
- *(deps)* Lock file maintenance (#475)
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.16 (#477)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.14.8 (#478)
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.17
- *(deps)* Update pre-commit hook igorshubovych/markdownlint-cli to v0.47.0
- *(deps)* Lock file maintenance

### Maintenance
- Sync template files

### Other Changes
- Merge pull request #473 from tschm/renovate/marimo-0.x
- Delete tests/test_docstrings.py
- Delete tests/test_makefile.py
- Delete tests/test_readme.py
- Delete tests/test_release_script.py
- Update template.yml
- Moving tests
- Merge pull request #479 from tschm/renovate/marimo-0.x
- Merge pull request #480 from tschm/renovate/pytest-9.x
- Merge pull request #481 from tschm/renovate/ghcr.io-astral-sh-uv-0.x
- Merge pull request #483 from tschm/renovate/igorshubovych-markdownlint-cli-0.x
- Merge pull request #482 from tschm/renovate/marimo-0.x
- Merge pull request #484 from tschm/renovate/lock-file-maintenance
- Enhance release workflow with package publishing
- Merge pull request #485 from tschm/template-updates
- Release to github packages with updated permissions

## [0.8.1] - 2025-12-02

### Other Changes
- Remove obsolete workflows

## [0.8.0] - 2025-12-02

### Bug Fixes
- *(deps)* Update dependency marimo to v0.17.6 (#442)
- *(deps)* Update dependency marimo to v0.17.7 (#443)
- *(deps)* Update dependency pre-commit to v4.4.0 (#447)
- *(deps)* Update dependency pytest to v9
- *(deps)* Update dependency pytest to v9.0.1
- *(deps)* Update dependency marimo to v0.18.0 (#457)
- *(deps)* Update dependency pre-commit to v4.5.0 (#458)
- *(deps)* Update dependency marimo to v0.18.1

### Dependencies
- *(deps)* Lock file maintenance (#438)
- *(deps)* Lock file maintenance (#439)
- *(deps)* Lock file maintenance (#444)
- *(deps)* Lock file maintenance (#445)
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.9 (#449)
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.35.0
- *(deps)* Lock file maintenance
- *(deps)* Lock file maintenance (#455)
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.13 (#465)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.14.7 (#466)
- *(deps)* Lock file maintenance
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.14 (#469)
- *(deps)* Update softprops/action-gh-release action to v2.5.0

### Maintenance
- Sync template files (#440)
- Sync template files (#441)
- Sync template files
- Sync template files
- Test readme
- Sync template files
- Sync template files
- Sync template files
- Sync template files

### Other Changes
- Merge pull request #446 from tschm/template-updates
- Merge pull request #448 from tschm/renovate/pytest-9.x
- Merge pull request #451 from tschm/renovate/python-jsonschema-check-jsonschema-0.x
- Merge pull request #450 from tschm/renovate/pytest-9.x
- Merge pull request #452 from tschm/renovate/lock-file-maintenance
- Merge pull request #453 from tschm/template-updates
- Testing README
- Testing README
- Testing README
- Merge pull request #454 from tschm/testREADME
- Merge pull request #456 from tschm/template-updates
- Update template reference in template.yml
- Update sync_template action version to v0.4.2
- Merge pull request #460 from tschm/template-updates
- Update template reference version to v0.7.15
- Update sync_template action to version 0.4.2
- Downgrade template reference from v0.7.15 to v0.7.14
- Update template.yml to exclude taskfiles
- Merge pull request #462 from tschm/template-updates
- Remove task leftovers
- Update template.yml with branch and exclude settings
- Merge pull request #464 from tschm/tschm-patch-1
- Merge pull request #467 from tschm/renovate/marimo-0.x
- Merge pull request #468 from tschm/renovate/lock-file-maintenance
- Merge pull request #470 from tschm/renovate/softprops-action-gh-release-2.x
- Merge pull request #471 from tschm/template-updates

## [0.7.24] - 2025-10-26

### Bug Fixes
- *(deps)* Update dependency marimo to v0.15.3 (#391)
- *(deps)* Update dependency marimo to v0.15.5 (#397)
- *(deps)* Update dependency marimo to v0.16.0 (#400)
- *(deps)* Update dependency marimo to v0.16.1 (#404)
- Fixing sync
- Fixing sync
- Fixing sync
- Fixing sync
- Fixing sync
- Fixing sync
- Fixing sync
- Fixing sync
- Fixing sync
- Fixing sync and remove devcontainer for now
- *(deps)* Update dependency marimo to v0.16.2 (#412)
- *(deps)* Update dependency marimo to v0.16.3 (#417)
- *(deps)* Update dependency marimo to v0.16.5 (#422)
- *(deps)* Update dependency marimo to v0.17.0 (#430)
- *(deps)* Update dependency marimo to v0.17.2 (#435)

### Dependencies
- *(deps)* Lock file maintenance (#390)
- *(deps)* Lock file maintenance (#392)
- *(deps)* Lock file maintenance (#394)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.13.1 (#398)
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.34.0 (#399)
- *(deps)* Lock file maintenance (#401)
- *(deps)* Lock file maintenance (#402)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.13.2 (#411)
- *(deps)* Lock file maintenance (#413)
- *(deps)* Lock file maintenance (#414)
- *(deps)* Lock file maintenance (#418)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.13.3 (#420)
- *(deps)* Update softprops/action-gh-release action to v2.4.0 (#421)
- *(deps)* Lock file maintenance (#423)
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.34.1 (#425)
- *(deps)* Update pre-commit hook rhysd/actionlint to v1.7.8 (#426)
- *(deps)* Update softprops/action-gh-release action to v2.4.1 (#427)
- *(deps)* Lock file maintenance (#428)
- *(deps)* Update dependency python to 3.14 (#431)
- *(deps)* Lock file maintenance (#437)

### Maintenance
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

### Other Changes
- Use a bash script (easier to convert to GitLab)
- Use a bash script (easier to convert to GitLab)
- Use a bash script (easier to convert to GitLab)
- Use a bash script (easier to convert to GitLab)
- Use a bash script (easier to convert to GitLab)
- Deptry
- Deptry
- Deptry
- Delete .github/taskfiles directory (#396)
- Change config templates action and include more files (#405)
- Tschm patch 1 (#407)
- Update sync.yml to include .pre-commit-config.yaml
- Towards testing of sync
- Update sync_template action version to v0.2.1
- Delete .github/scripts directory
- Template file
- Template file
- Sync with standard Token?
- Sync with standard Token?
- Sync with standard Token?
- Sync with standard Token?
- Sync with standard Token?
- Sync with standard Token?

## [0.7.23] - 2025-09-11

### Bug Fixes
- *(deps)* Update dependency pytest to v8.4.1 (#350)
- *(deps)* Update dependency pre-commit to v4.3.0 (#364)
- *(deps)* Update dependency marimo to v0.14.17 (#369)
- *(deps)* Update dependency marimo to v0.15.0 (#378)
- *(deps)* Update dependency marimo to v0.15.2 (#382)
- *(deps)* Update dependency pytest to v8.4.2 (#385)

### Dependencies
- *(deps)* Lock file maintenance (#347)
- *(deps)* Update tschm/.config-templates action to v0.1.6 (#349)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.12.7 (#352)
- *(deps)* Update tschm/.config-templates action to v0.2.0 (#354)
- *(deps)* Update tschm/cradle action to v0.3.06 (#353)
- *(deps)* Lock file maintenance (#355)
- *(deps)* Update pre-commit hook pre-commit/pre-commit-hooks to v6 (#365)
- *(deps)* Lock file maintenance (#366)
- *(deps)* Update tschm/.config-templates action to v0.4.6 (#367)
- *(deps)* Update actions/checkout action to v5 (#370)
- *(deps)* Lock file maintenance (#371)
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.33.3 (#373)
- *(deps)* Lock file maintenance (#376)
- *(deps)* Update actions/upload-pages-artifact action to v4 (#379)
- *(deps)* Lock file maintenance (#380)
- *(deps)* Update softprops/action-gh-release action to v2.3.3 (#384)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.12.12 (#383)
- *(deps)* Lock file maintenance (#386)

### Maintenance
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

### Other Changes
- Template
- Templates
- Folder for testing
- Workflows
- Update workflow
- Updater
- Update workflow
- Remove the update workflow
- Update
- Update configuration templates from tschm/.config-templates (#346)
- Sync
- Delete .devcontainer/startup.sh
- Delete update.sh
- 357 prepare for a new sync (#359)
- Change SOURCE FOLDER
- Update sync.yml
- Makefile corrections
- Split up make book
- Split up make book
- Update sync.yml
- Delete Makefile
- Delete src/.gitkeep
- Update sync.yml
- Delete taskfiles directory
- Render step (#374)
- Update .gitignore to remove quantstats.md

## [0.7.22] - 2025-07-12

### Dependencies
- *(deps)* Update tschm/cradle action to v0.1.75 (#336)
- *(deps)* Lock file maintenance (#340)
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.33.2 (#338)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.12.2 (#337)
- *(deps)* Update tschm/cradle action to v0.1.80 (#339)
- *(deps)* Update pre-commit hook pycqa/bandit to v1.8.6 (#341)
- *(deps)* Update tschm/cradle action to v0.2.1 (#342)
- *(deps)* Lock file maintenance (#345)
- *(deps)* Update tschm/cradle action to v0.3.01 (#344)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.12.3 (#343)

## [0.7.21] - 2025-07-01

### Bug Fixes
- *(deps)* Update dependency pytest to v8.4.0 (#319)
- *(deps)* Update dependency pytest to v8.4.1 (#328)

### Dependencies
- *(deps)* Update tschm/cradle action to v0.1.69 (#315)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.11.12 (#314)
- *(deps)* Update tschm/cradle action to v0.1.71 (#316)
- *(deps)* Update pre-commit hook crate-ci/typos to v1.33.1 (#317)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.11.13 (#318)
- *(deps)* Lock file maintenance (#320)
- *(deps)* Lock file maintenance (#322)
- *(deps)* Update tschm/cradle action to v0.1.72 (#323)
- *(deps)* Lock file maintenance (#324)
- *(deps)* Update pre-commit hook pycqa/bandit to v1.8.4 (#325)
- *(deps)* Update pre-commit hook pycqa/bandit to v1.8.5 (#326)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.12.0 (#327)
- *(deps)* Lock file maintenance (#329)
- *(deps)* Lock file maintenance (#330)
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.33.1 (#331)
- *(deps)* Update pre-commit hook crate-ci/typos to v1.34.0 (#333)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.12.1 (#332)
- *(deps)* Update tschm/cradle action to v0.1.73 (#334)

### Other Changes
- Update Makefile (#321)
- Update Makefile (#335)

## [0.7.20] - 2025-05-29

### Other Changes
- Version and relaxing numpy
- License copy

## [0.7.19] - 2025-05-26

### Other Changes
- Potential fix for code scanning alert no. 12: Workflow does not contain permissions (#312)
- Potential fix for code scanning alert no. 10: Workflow does not contain permissions (#313)

## [0.7.18] - 2025-05-26

### Dependencies
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.11.3 (#283)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.11.4 (#284)
- *(deps)* Lock file maintenance (#285)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.11.5 (#286)
- *(deps)* Update tschm/cradle action to v0.1.60 (#289)
- *(deps)* Update pre-commit hook python-jsonschema/check-jsonschema to v0.33.0 (#290)
- *(deps)* Lock file maintenance (#291)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.11.6 (#292)
- *(deps)* Lock file maintenance (#293)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.11.7 (#294)
- *(deps)* Update pre-commit hook crate-ci/typos to v1.31.2 (#295)
- *(deps)* Update tschm/cradle action to v0.1.63 (#296)
- *(deps)* Lock file maintenance (#297)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.11.8 (#298)
- *(deps)* Update pre-commit hook crate-ci/typos to v1.32.0 (#299)
- *(deps)* Lock file maintenance (#300)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.11.9 (#301)
- *(deps)* Lock file maintenance (#302)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.11.10 (#303)
- *(deps)* Update tschm/cradle action to v0.1.64 (#304)
- *(deps)* Update pre-commit hook igorshubovych/markdownlint-cli to v0.45.0 (#305)
- *(deps)* Update tschm/cradle action to v0.1.66 (#306)
- *(deps)* Update tschm/cradle action to v0.1.68 (#307)
- *(deps)* Lock file maintenance (#308)
- *(deps)* Update pre-commit hook asottile/pyupgrade to v3.20.0 (#311)
- *(deps)* Update pre-commit hook astral-sh/ruff-pre-commit to v0.11.11 (#310)

### Maintenance
- *(config)* Migrate config .github/renovate.json (#287)

### Other Changes
- Update renovate.json
- Update README.md
- Update README.md
- Emojis and remove devcontainer
- Clean (#309)

## [0.7.17] - 2025-04-01

### Dependencies
- *(deps)* Lock file maintenance (#282)

### Other Changes
- Update tschm/cradle action to v0.1.58 (#277)
- Update pyproject.toml (#276)
- Update tschm/cradle action to v0.1.59 (#278)
- Update pre-commit hook crate-ci/typos to v1.31.0 (#279)
- Update pre-commit hook crate-ci/typos to v1.31.1 (#280)
- Update renovate.json (#281)

## [0.7.16] - 2025-03-26

### Maintenance
- Testing for Windows (#247)

### Other Changes
- Workflows (#232)
- Workflows simplified (#233)
- Deptry (#234)
- Update pre-commit.yml (#235)
- Update ci.yml (#236)
- Lock file maintenance (#238)
- Lock file maintenance (#239)
- Update cvxgrp/.github action to v2.1.0 (#237)
- Lock file maintenance (#240)
- Update cvxgrp/.github action to v2.1.1 (#241)
- Update pre-commit.yml (#242)
- Update renovate.json
- Update ci.yml (#245)
- Update cvxgrp/.github action to v2.2.1 (#244)
- Update cvxgrp/.github action to v2.2.2 (#246)
- Update cvxgrp/.github action to v2.2.3 (#248)
- Lock file maintenance (#249)
- Update cvxgrp/.github action to v2.2.4 (#250)
- Update pre-commit hooks (#251)
- Update mcr.microsoft.com/devcontainers/python Docker tag to v3.13 (#252)
- Lock file maintenance (#253)
- Lock file maintenance (#254)
- Update cvxgrp/.github action to v2.2.5 (#255)
- Lock file maintenance (#256)
- Update pre-commit hooks (#257)
- Lock file maintenance (#258)
- Update cvxgrp/.github action to v2.2.6 (#259)
- Update pre-commit hooks (#260)
- Lock file maintenance (#261)
- Update cvxgrp/.github action to v2.2.7 (#262)
- Lock file maintenance (#263)
- Update cvxgrp/.github action to v2.2.8 (#264)
- Lock file maintenance (#265)
- Lock file maintenance (#266)
- Update release.yml (#268)
- Update release.yml (#269)
- Update release.yml (#270)
- Update pre-commit hooks (#271)
- Lock file maintenance (#272)
- Update ci.yml (#273)
- Update pre-commit.yml (#274)
- Update tschm/cradle action to v0.1.57 (#275)

## [0.7.15] - 2025-02-01

### Other Changes
- Update cvxgrp/.github action to v2.0.13 (#230)

## [0.7.14] - 2025-02-01

### Other Changes
- Update pre-commit.yml (#229)

## [0.7.13] - 2025-01-31

### Other Changes
- Update pre-commit hook crate-ci/typos to v1.29.5 (#228)

## [0.7.12] - 2025-01-31

### Other Changes
- Update renovate.json

## [0.7.11] - 2025-01-31

### Other Changes
- Update pre-commit hook astral-sh/ruff-pre-commit to v0.9.4 (#226)

## [0.7.10] - 2025-01-30

### Other Changes
- Update pre-commit hook python-jsonschema/check-jsonschema to v0.31.1 (#225)

## [0.7.9] - 2025-01-30

### Other Changes
- Update cvxgrp/.github action to v2.0.12 (#224)

## [0.7.8] - 2025-01-29

### Other Changes
- Update cvxgrp/.github action to v2.0.11 (#223)

## [0.7.7] - 2025-01-29

### Other Changes
- Update cvxgrp/.github action to v2.0.10 (#222)

## [0.7.6] - 2025-01-28

### Other Changes
- Dispatch

## [0.7.5] - 2025-01-27

### Other Changes
- Update cvxgrp/.github action to v2.0.9 (#220)

## [0.7.4] - 2025-01-27

### Other Changes
- Release
- Update cvxgrp/.github action to v2.0.8 (#219)

## [0.7.3] - 2025-01-27

### Other Changes
- Update pre-commit hook igorshubovych/markdownlint-cli to v0.44.0 (#216)
- Update cvxgrp/.github action to v2.0.7 (#217)
- Release
- Lock file maintenance (#218)

## [0.7.2] - 2025-01-24

### Other Changes
- Bump numpy from 1.26.2 to 1.26.3
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pandas from 2.1.4 to 2.2.0
- Bump pytest from 7.4.4 to 8.0.0
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] auto fixes from pre-commit.com hooks
- [pre-commit.ci] pre-commit autoupdate
- Update dependabot.yml
- Bump numpy from 1.26.3 to 1.26.4
- Bump pre-commit from 3.6.0 to 3.6.1
- Bump actions/checkout from 3 to 4
- Update pre-commit.yml
- [pre-commit.ci] pre-commit autoupdate
- Bump pytest from 8.0.0 to 8.0.1
- Bump pre-commit from 3.6.1 to 3.6.2
- [pre-commit.ci] pre-commit autoupdate
- Bump pandas from 2.2.0 to 2.2.1
- Bump pytest from 8.0.1 to 8.0.2
- Bump pytest from 8.0.2 to 8.1.1
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pre-commit from 3.6.2 to 3.7.0
- Bump pytest-cov from 4.1.0 to 5.0.0
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pandas from 2.2.1 to 2.2.2
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pytest from 8.1.1 to 8.2.0
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pre-commit from 3.7.0 to 3.7.1
- ---
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pytest from 8.2.1 to 8.2.2
- [pre-commit.ci] pre-commit autoupdate
- Update pre-commit.yml
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Update tests.yml
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump setuptools from 69.0.3 to 70.0.0
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pytest from 8.2.2 to 8.3.1
- Bump pre-commit from 3.7.1 to 3.8.0
- Bump pytest from 8.3.1 to 8.3.2
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pandas from 2.2.2 to 2.2.3
- Bump pytest from 8.3.2 to 8.3.3
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pre-commit from 3.8.0 to 4.0.0
- [pre-commit.ci] pre-commit autoupdate
- Bump numpy from 1.26.4 to 2.0.2
- Update test_linalg.py
- Bump pre-commit from 4.0.0 to 4.0.1
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pytest-cov from 5.0.0 to 6.0.0
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pytest from 8.3.3 to 8.3.4
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Update pre-commit.yml
- Update release.yml
- Update tests.yml
- Towards taskfile
- Move to uv
- Actions
- Remove poetry.lock
- Pre-commit update
- Pre-commit
- Fmt
- Pre-commit update
- Moving Code of conduct
- Use main branch of .github
- Deptry works out of the box for public repos
- Add renovate.json
- Moving renovate
- Update pre-commit hook crate-ci/typos to v1.29.3
- Update pre-commit hook astral-sh/ruff-pre-commit to v0.8.5
- Lock file maintenance
- Devcontainer
- Devcontainer
- Update pre-commit hook crate-ci/typos to v1.29.4
- Bandit
- Automerge for pre-commit and lockFileMaintenance
- Update pre-commit hook astral-sh/ruff-pre-commit to v0.8.6 (#195)
- Update pre-commit hook rhysd/actionlint to v1.7.6 (#196)
- Explicit v2.0.0 for workflows
- Lock file maintenance (#197)
- Update cvxgrp/.github action to v2.0.1
- Update pre-commit hook python-jsonschema/check-jsonschema to v0.31.0
- Update pre-commit hook astral-sh/ruff-pre-commit to v0.9.0 (#201)
- Update cvxgrp/.github action to v2.0.2
- Update renovate.json
- Update cvxgrp/.github action to v2.0.3
- Update pre-commit hook astral-sh/ruff-pre-commit to v0.9.1 (#205)
- Update pre-commit hook PyCQA/bandit to v1.8.2 (#206)
- Update .pre-commit-config.yaml (#208)
- Update pre-commit hook astral-sh/ruff-pre-commit to v0.9.2 (#209)
- Update cvxgrp/.github action to v2.0.6 (#210)
- Update pre-commit hook rhysd/actionlint to v1.7.7 (#211)
- [pre-commit.ci] pre-commit autoupdate (#212)
- Update pre-commit hook crate-ci/typos to v1 (#214)
- Update pre-commit hook astral-sh/ruff-pre-commit to v0.9.3 (#215)
- Update release.yml

## [0.7.1] - 2024-01-02

### Other Changes
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pytest from 7.4.3 to 7.4.4
- Remove upper bound on python

## [0.7.0] - 2023-12-16

### Other Changes
- Update poetry version for build
- Make fmt update
- Fmt lock
- Poetry pre-commit not that useful
- Update README.md
- Update README.md
- Conduct
- Bump plotly from 5.16.1 to 5.17.0 (#72)
- Update Makefile
- Bump pandas from 2.1.0 to 2.1.1 (#73)
- Update README.md
- [pre-commit.ci] pre-commit autoupdate (#74)
- [pre-commit.ci] pre-commit autoupdate (#75)
- [pre-commit.ci] pre-commit autoupdate (#76)
- [pre-commit.ci] pre-commit autoupdate (#77)
- Bump pandas from 2.1.1 to 2.1.2 (#78)
- Bump plotly from 5.17.0 to 5.18.0 (#79)
- [pre-commit.ci] pre-commit autoupdate (#81)
- Bump pytest from 7.4.2 to 7.4.3 (#80)
- [pre-commit.ci] pre-commit autoupdate (#83)
- Bump pandas from 2.1.2 to 2.1.3
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- [pre-commit.ci] pre-commit autoupdate
- Bump pandas from 2.1.3 to 2.1.4
- [pre-commit.ci] pre-commit autoupdate
- Lock file
- Update for 3.12
- Ignore ruff cache
- Remove portfolio building instead use cvxSimulator
- Dependencies
- Cleaning

## [0.6.1] - 2023-09-05

### Other Changes
- Lock fmt

## [0.6.0] - 2023-09-03

### Other Changes
- Update README.md
- Revisit docstring
- Update pre-commit.yml
- Update pre-commit.yml
- Fmt
- Revisit coveralls
- Update port.py

## [0.5.4] - 2023-09-03

### Other Changes
- Revisit graph

## [0.5.3] - 2023-09-03

### Other Changes
- Update port.py
- Graph revisited

## [0.5.2] - 2023-09-03

### Other Changes
- Ignore warning for pct_change

## [0.5.1] - 2023-09-03

### Maintenance
- Build and publish instead of release
- Testing, testing

### Other Changes
- Install pytest on the fly
- Remove testing from pyproject
- Makefile
- Remove tests
- Makefile
- Fmt
- Update pre-commit.yml
- 68 drawdown (#71)
- Pre-commit verbose
- Poetry updates
- Readme
- Plot portfolio
- Update .pre-commit-config.yaml
- Update pre-commit.yml
- Lock file updates
- Copyright notice
- Remove MIT LICENSE
- Create LICENSE
- License per file
- Update pre-commit.yml
- Update pre-commit.yml

## [0.5.0] - 2023-08-16

### Other Changes
- Nav compound and accum
- Badges
- Plotly dependency
- Aggregate for monthly table
- Plotting
- Fmt

## [0.4.6] - 2023-08-16

### Maintenance
- Testing, testing
- Testing, testing
- Testing, testing

### Other Changes
- Update port.py
- Towards testing
- Remove tests, have moved to cs repo
- Comment mypy

## [0.3.2] - 2023-08-16

### Bug Fixes
- Fixing
- Fixing
- Fix coverage

### Documentation
- Docs
- Docs
- Doc string in tests missing (#38)

### Maintenance
- Tests
- Test
- Test file
- Tests
- Testing
- Testing
- Testing
- Testing
- Testing
- Test coverage
- Test coverage
- Test coverage
- Testing experiment 5
- Format code with black and isort (#32)
- Remove assert statement from non-test files (#43)
- Test coverage (#45)
- Testing monthtable
- Testing monthtable
- Testing monthtable
- Testing monthtable
- Testing monthtable
- Format code with black and isort (#63)

### Other Changes
- Initial commit
- Bring in poetry
- Pypi
- Support module
- Workflows
- Poetry
- Request >=3.9
- Update tests.yml
- Update pyproject.toml
- Update pyproject.toml
- Update README.md
- Coverage
- Lock file
- Used Token
- Rename pycta to tinycta
- Ignore .idea
- Add .deepsource.toml (#1)
- Format code with black and isort (#2)
- Add newline at end of file (#3)
- Remove commented out code (#4)
- Refactor unnecessary `else` / `elif` when `if` block has a `return` statement (#5)
- Remove assert statement from non-test files (#6)
- Length of line (#8)
- Create CODE_OF_CONDUCT.md (#9)
- Create CODE_OF_CONDUCT.md (#11)
- Create LICENSE (#10)
- Delete license directory (#13)
- Update README.md
- Update tests.yml (#14)
- Update .deepsource.toml (#15)
- Update tests.yml (#16)
- Format code with black and isort (#17)
- 19 documentation (#20)
- Update tests.yml (#22)
- Update conftest.py (#21)
- 24 documentation of files (#25)
- 24 documentation of files (#27)
- Update tests.yml (#28)
- Update tests.yml (#29)
- Update pypi.yml
- Update and rename pypi.yml to release.yml
- Rename release.yml to release.yml
- Update release.yml
- Update release.yml (#30)
- Monthly performance
- Port
- Remove commented out code (#40)
- Remove unused imports (#42)
- Remove assert statement from non-test files (#39)
- Update release.yml (#47)
- Updating workflows (#49)
- 48 use central actions (#50)
- Workflows simplified
- Qodana analysis
- Qodana analysis
- Qodana analysis
- Qodana analysis
- Qodana analysis
- Qodana analysis
- Qodana analysis
- Coverage
- Pre-commit
- Pre-commit workflow
- Remove LICENSE stuff
- Makefile
- Remove qodana
- Poetry
- Create dependabot.yml
- Update Makefile
- Deps
- Pyupgrade
- Update README.md (#64)
- Update tests.yml
- Create book.yml (#65)
- Update Makefile
- Update pyproject.toml (#67)

<!-- generated by git-cliff -->
