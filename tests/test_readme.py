"""Tests for README code examples.

This module extracts Python code and expected result blocks from README.md,
executes the code, and verifies the output matches the documented result.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent.parent
README = ROOT / "README.md"

# Regex for Python code blocks
CODE_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)

RESULT = re.compile(r"```result\n(.*?)```", re.DOTALL)


def test_readme_runs():
    """Execute README code blocks and compare output to documented results."""
    code_blocks = CODE_BLOCK.findall(README.read_text())
    result_blocks = RESULT.findall(README.read_text())

    code = "".join(code_blocks)  # merged code
    expected = "".join(result_blocks)

    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)

    stdout = result.stdout

    assert stdout.strip() == expected.strip()
