#!/usr/bin/env python3
"""Check that the test layout mirrors the source layout (TinyCTA variant).

This is a repo-local adaptation of the Rhiza ``check_test_layout.py`` gate. It
keeps the strict 1:1 mirror as the default, but recognises that a handful of
TinyCTA test suites intentionally have *no* ``src/`` counterpart, and that
behavioural test *classes* are a legitimate way to group tests.

Rules enforced:

  * every source module ``src/…/xyz.py`` has a mirrored test file
    ``tests/…/test_xyz.py`` (nested packages are mirrored);
  * every top-level ``class A`` in a source module has a matching ``TestA``
    class in that mirrored test file;
  * every ``tests/…/test_*.py`` file traces back to a source module, *unless*
    it is an allowlisted meta/infra or auxiliary suite (see below).

Deliberately **not** enforced (relaxed from the upstream strict checker):

  * the reverse orphan-*class* rule. TinyCTA groups tests into behavioural
    classes (e.g. ``TestRiskPosition``, ``TestOutputPathConfinement``) that
    describe a scenario around a source *function* rather than mirroring a
    source class. The forward rule above still guarantees every source class is
    covered, so binding every ``Test*`` class to a source class as well only
    produces false positives here.

Allowlisted test files (no ``src/`` counterpart required):

  * anything under ``tests/property/`` or ``tests/fuzz/`` — auxiliary
    property/fuzz suites;
  * any top-level ``tests/test_*.py`` — repository meta-tests (pyproject,
    README links, CI workflows) that assert about the repo itself, not a module;
  * the explicitly listed package-level auxiliary suites in ``_EXEMPT_TESTS``
    (mutation-kill, tutorial and version tests).

``__init__.py`` and ``conftest.py`` are ignored on both sides. Test *functions*
are unconstrained — the rules bind files and classes only.

Usage:
  python3 scripts/check_test_layout.py [--src DIR] [--tests DIR]

Exits 0 when the layout is clean, 1 (listing every violation) otherwise.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

_IGNORED = {"__init__.py", "conftest.py"}

# Path components (relative to the tests root) whose whole subtree is exempt
# from the reverse "every test file mirrors a source module" rule.
_EXEMPT_TEST_DIRS = {"property", "fuzz"}

# Explicit package-level auxiliary test files (relative to the tests root) that
# intentionally have no mirrored source module. Kept explicit so a genuinely
# stray test file is still reported.
_EXEMPT_TESTS = {
    "tinycta/test_engine_mutation.py",  # mutation-kill suite for engine.py
    "tinycta/test_tutorial.py",  # exercises the tutorial notebook/docs
    "tinycta/test_version.py",  # asserts the packaged __version__
}


def _top_level_classes(path: Path) -> set[str]:
    """Return the names of top-level classes defined in *path*."""
    tree = ast.parse(path.read_text(), filename=str(path))
    return {node.name for node in tree.body if isinstance(node, ast.ClassDef)}


def _source_modules(src: Path) -> list[Path]:
    """Return the source ``.py`` modules under *src* (ignoring dunder/conftest)."""
    return sorted(p for p in src.rglob("*.py") if p.name not in _IGNORED)


def _test_files(tests: Path) -> list[Path]:
    """Return the ``test_*.py`` files under *tests* (ignoring conftest)."""
    return sorted(p for p in tests.rglob("test_*.py") if p.name not in _IGNORED)


def _is_exempt(rel: Path) -> bool:
    """Return whether a test file (relative to the tests root) is exempt.

    A file is exempt from the reverse module-mirror rule when it lives in an
    auxiliary subtree, is a top-level repository meta-test, or is explicitly
    allowlisted.
    """
    if _EXEMPT_TEST_DIRS.intersection(rel.parts):
        return True
    if rel.parent == Path():  # top-level tests/test_*.py meta-test
        return True
    return rel.as_posix() in _EXEMPT_TESTS


def check(src: Path, tests: Path) -> list[str]:
    """Return a list of layout violations (empty when the layout is clean)."""
    errors: list[str] = []

    # Forward: every source module needs a mirrored test file + Test* classes.
    for module in _source_modules(src):
        rel = module.relative_to(src)
        test_path = tests / rel.parent / f"test_{module.stem}.py"
        if not test_path.exists():
            errors.append(f"missing test file {test_path} for source module {module}")
            continue
        test_classes = _top_level_classes(test_path)
        for cls in sorted(_top_level_classes(module)):
            if f"Test{cls}" not in test_classes:
                errors.append(f"missing class Test{cls} in {test_path} for class {cls} in {module}")

    # Reverse: every non-exempt test file must trace back to a source module.
    for test_file in _test_files(tests):
        rel = test_file.relative_to(tests)
        if _is_exempt(rel):
            continue
        source_name = test_file.stem[len("test_") :]
        source_path = src / rel.parent / f"{source_name}.py"
        if not source_path.exists():
            errors.append(f"orphan test file {test_file} (no source module {source_path})")

    return errors


def main(argv: list[str] | None = None) -> int:
    """Entry point: check the layout and return an exit code."""
    parser = argparse.ArgumentParser(description="Check test/source layout parity.")
    parser.add_argument("--src", default="src", help="Source directory (default: src).")
    parser.add_argument("--tests", default="tests", help="Tests directory (default: tests).")
    args = parser.parse_args(argv)

    errors = check(Path(args.src), Path(args.tests))
    if errors:
        print("Test-layout check failed:", file=sys.stderr)
        for err in errors:
            print(f"  ✗ {err}", file=sys.stderr)
        return 1
    print("Test layout OK: tests mirror sources 1:1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
