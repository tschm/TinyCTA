"""Tests for project-owned coverage configuration."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).parent.parent


def test_branch_coverage_enabled() -> None:
    """Ensure Coverage.py collects branch coverage for CI gating."""
    with (ROOT / "pyproject.toml").open("rb") as file:
        pyproject = tomllib.load(file)

    assert pyproject["tool"]["coverage"]["run"]["branch"] is True
