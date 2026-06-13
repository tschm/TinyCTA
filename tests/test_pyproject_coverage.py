"""Tests for project-owned coverage configuration."""

from __future__ import annotations

from pathlib import Path
import tomllib


def test_branch_coverage_enabled() -> None:
    """Ensure Coverage.py collects branch coverage for CI gating."""
    with (Path(__file__).resolve().parents[1] / "pyproject.toml").open("rb") as file:
        pyproject = tomllib.load(file)

    assert pyproject["tool"]["coverage"]["run"]["branch"] is True
