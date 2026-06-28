"""Tests for repository-owned README links."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def test_license_badge_uses_main_branch() -> None:
    """The README license badge should point at LICENSE on the main branch."""
    readme = README.read_text()
    badge = "[![MIT License](https://img.shields.io/badge/License-MIT-brightgreen.svg)]"
    assert f"{badge}(https://github.com/tschm/TinyCTA/blob/main/LICENSE)" in readme
