"""Execute the end-to-end tutorial and verify its documented output.

``docs/tutorial.md`` is a runnable walkthrough: its non-skipped ``python`` code
blocks are concatenated and executed, and the merged stdout must match the
concatenated ``result`` blocks. This keeps the tutorial honest — if the API or
its behaviour drifts, the page stops matching and this test fails.

Blocks tagged ``+RHIZA_SKIP`` on the fence line are illustrative (e.g. pasted
DataFrame dumps with platform-dependent floats) and are excluded from execution,
mirroring the README validation convention.
"""

from __future__ import annotations

import re
import subprocess  # nosec B404
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TUTORIAL = ROOT / "docs" / "tutorial.md"

CODE_BLOCK = re.compile(r"```python([^\n]*)\n(.*?)```", re.DOTALL)
RESULT_BLOCK = re.compile(r"```result\n(.*?)```", re.DOTALL)
SKIP_FLAG = "+RHIZA_SKIP"


def _runnable_blocks(text: str) -> list[str]:
    """Return the code bodies of python blocks not marked +RHIZA_SKIP."""
    return [code for flags, code in CODE_BLOCK.findall(text) if SKIP_FLAG not in flags]


def test_tutorial_exists() -> None:
    """The tutorial page is present and non-empty."""
    assert TUTORIAL.is_file()
    assert TUTORIAL.read_text(encoding="utf-8").strip()


def test_tutorial_blocks_are_syntactically_valid() -> None:
    """Every executed python block compiles."""
    for i, code in enumerate(_runnable_blocks(TUTORIAL.read_text(encoding="utf-8"))):
        compile(code, f"<tutorial_block_{i}>", "exec")


def test_tutorial_runs_and_matches_documented_output() -> None:
    """Executing the tutorial reproduces its documented ``result`` blocks."""
    text = TUTORIAL.read_text(encoding="utf-8")
    code = "".join(_runnable_blocks(text))
    expected = "".join(RESULT_BLOCK.findall(text))

    # At least one runnable block and one result block, else the page is not a
    # validated walkthrough and this test would pass vacuously.
    assert code.strip()
    assert expected.strip()

    # Trust boundary: the tutorial lives in this repository and is reviewed in PRs.
    result = subprocess.run(  # nosec B603
        [sys.executable, "-c", code], capture_output=True, text=True, cwd=ROOT
    )
    if result.returncode != 0:
        pytest.fail(f"tutorial code exited with {result.returncode}. Stderr:\n{result.stderr}")
    assert result.stdout.strip() == expected.strip()
