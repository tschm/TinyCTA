"""Guard the core-install contract.

``pip install tinycta`` provides only ``[project].dependencies``. The Optuna-based
``tinycta.hyper`` layer and the four packages it needs (``jquantstats``, ``loguru``,
``optuna``, ``pyyaml``) arrive only with ``pip install "tinycta[hyper]"``.

Nothing else in the suite can see that contract break. ``[tool.uv]``
``default-groups = ["dev", "hyper"]`` puts the extra into every dev and CI
environment, and ``deptry`` treats an import as declared when it appears *anywhere*
in the manifest — including in an extra. So a core module can import ``loguru``, as
``_kernel.py`` once did, and `make fmt`, `make typecheck`, `make deptry`,
`make security` and a 100%-coverage `make test` all stay green while
``pip install tinycta`` ships an unimportable :class:`~tinycta.engine.Engine`.

Two independent checks, because they fail in different directions:

* :func:`test_core_modules_import_only_core_dependencies` reads the manifest and the
  core modules' ASTs. Fast and hermetic, and it names the offending import.
* :func:`test_core_modules_import_with_hyper_dependencies_absent` really imports every
  core module in a subprocess where the hyper-only distributions are unimportable, so a
  lazily-imported or dynamically-resolved dependency that the AST scan cannot see still
  fails the suite.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "src" / "tinycta"
PYPROJECT = PROJECT_ROOT / "pyproject.toml"

# The subpackage that is allowed to import the `hyper` extra's dependencies.
_OPTIONAL_SUBPACKAGE = "hyper"


def _manifest() -> dict:
    """Return the parsed ``pyproject.toml``."""
    return tomllib.loads(PYPROJECT.read_text())


def _normalize(dist: str) -> str:
    """Normalise a distribution name per PEP 503 (lowercase, runs of -_. to -)."""
    return re.sub(r"[-_.]+", "-", dist).lower()


def _requirement_name(requirement: str) -> str:
    """Return the bare distribution name from a PEP 508 requirement string."""
    return _normalize(re.split(r"[\[<>=!~;\s]", requirement, maxsplit=1)[0])


def _module_name_map() -> dict[str, str]:
    """Return the normalised distribution -> import-module map from the deptry table.

    Reusing ``[tool.deptry.package_module_name_map]`` keeps this test in step with the
    manifest instead of hardcoding a second copy that can drift (``pyyaml`` imports as
    ``yaml``, ``cvx-linalg`` as ``cvx``).
    """
    table = _manifest()["tool"]["deptry"]["package_module_name_map"]
    return {_normalize(dist): module for dist, module in table.items() if module}


def _modules_for(requirements: list[str]) -> set[str]:
    """Return the top-level import names provided by ``requirements``."""
    name_map = _module_name_map()
    modules = set()
    for requirement in requirements:
        dist = _requirement_name(requirement)
        modules.add(name_map.get(dist, dist.replace("-", "_")))
    return modules


def _core_dependency_modules() -> set[str]:
    """Return the import names available from a bare ``pip install tinycta``."""
    return _modules_for(_manifest()["project"]["dependencies"])


def _hyper_only_modules() -> set[str]:
    """Return the import names that arrive *only* with the ``hyper`` extra."""
    extra = _manifest()["project"]["optional-dependencies"][_OPTIONAL_SUBPACKAGE]
    return _modules_for(extra) - _core_dependency_modules()


def _core_source_files() -> list[Path]:
    """Return the source modules on the core import path (everything outside hyper/)."""
    return sorted(p for p in SRC_ROOT.rglob("*.py") if _OPTIONAL_SUBPACKAGE not in p.relative_to(SRC_ROOT).parts)


def _core_module_names() -> list[str]:
    """Return the importable dotted names of the core modules."""
    names = []
    for path in _core_source_files():
        rel = path.relative_to(SRC_ROOT).with_suffix("")
        parts = [p for p in rel.parts if p != "__init__"]
        names.append(".".join(["tinycta", *parts]))
    return sorted(set(names))


def _imported_top_level_modules(path: Path) -> set[str]:
    """Return the top-level names imported by ``path``, excluding stdlib and self-imports.

    Relative imports (``node.level > 0``) are intra-package and carry no external
    dependency, so they are skipped.
    """
    tree = ast.parse(path.read_text(), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return {root for root in roots if root not in sys.stdlib_module_names and root != "tinycta"}


def _render_offenders(offenders: dict[str, set[str]]) -> str:
    """Render the offending file -> imports mapping as a stable, readable string."""
    return "; ".join(f"{path} imports {', '.join(sorted(mods))}" for path, mods in sorted(offenders.items()))


def test_core_modules_import_only_core_dependencies():
    """No module outside ``tinycta.hyper`` may import a package missing from core deps.

    This is the static half: it reads the manifest, walks each core module's AST and
    reports any third-party import that a bare ``pip install tinycta`` would not supply.
    """
    allowed = _core_dependency_modules()

    offenders: dict[str, set[str]] = {}
    for path in _core_source_files():
        stray = _imported_top_level_modules(path) - allowed
        if stray:
            offenders[str(path.relative_to(PROJECT_ROOT))] = stray

    assert not offenders, (
        "core modules import packages absent from [project].dependencies, so "
        f"`pip install tinycta` cannot import them: {_render_offenders(offenders)}"
    )


def test_hyper_extra_actually_supplies_something_beyond_core():
    """The hyper extra must contribute imports core lacks, or these tests prove nothing.

    If the extra were folded into core, :func:`_hyper_only_modules` would go empty and
    the subprocess test below would block nothing while still passing.
    """
    assert _hyper_only_modules(), (
        "the `hyper` extra adds no packages beyond [project].dependencies — the core-install guard would be vacuous"
    )


def test_core_modules_import_with_hyper_dependencies_absent():
    """Every core module imports when the hyper extra's packages are unimportable.

    Runs in a subprocess with a ``sys.meta_path`` finder that raises
    :class:`ModuleNotFoundError` for the hyper-only distributions, reproducing a bare
    ``pip install tinycta`` without building a wheel or touching the network.
    """
    blocked = sorted(_hyper_only_modules())
    modules = _core_module_names()

    completed = subprocess.run(
        [sys.executable, "-c", _IMPORT_UNDER_BLOCKADE, json.dumps(blocked), json.dumps(modules)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        timeout=60,
    )

    if completed.returncode != 0:
        pytest.fail(f"import probe failed to run: {completed.stderr.strip()}")

    failures = json.loads(completed.stdout)
    assert not failures, (
        f"core modules fail to import without the `hyper` extra ({', '.join(blocked)} blocked): " + "; ".join(failures)
    )


# Executed by the test above via ``python -c``. Kept dependency-free and stdlib-only so
# it runs in the blockaded interpreter; arguments arrive as JSON on argv.
_IMPORT_UNDER_BLOCKADE = '''
import importlib
import importlib.abc
import json
import sys

blocked = set(json.loads(sys.argv[1]))
modules = json.loads(sys.argv[2])


class _Blockade(importlib.abc.MetaPathFinder):
    """Make the hyper-only distributions look absent, as on a core-only install."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in blocked:
            raise ModuleNotFoundError("No module named " + repr(fullname), name=fullname)
        return None


# Drop anything already imported so the blockade applies on re-import.
for name in list(sys.modules):
    if name.split(".")[0] in blocked or name.split(".")[0] == "tinycta":
        del sys.modules[name]

sys.meta_path.insert(0, _Blockade())

failures = []
for name in modules:
    try:
        importlib.import_module(name)
    except BaseException as exc:
        failures.append(name + ": " + type(exc).__name__ + ": " + str(exc))

print(json.dumps(failures))
'''
