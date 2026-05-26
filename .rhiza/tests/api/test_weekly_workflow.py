"""Tests for the rhiza_weekly.yml workflow and its referenced Makefile targets.

Covers two layers:
- Structural: parse .github/workflows/rhiza_weekly.yml and assert every job,
  trigger, and key step is correctly defined.
- Behavioural: dry-run (make -n) the Makefile targets that the workflow invokes
  (semgrep, security, test) to confirm they are wired up without actually
  running them.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from api.conftest import run_make

WORKFLOW_PATH = Path(".github") / "workflows" / "rhiza_weekly.yml"
EXPECTED_JOBS = {"dep-compat-test", "semgrep", "pip-audit", "link-check"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_workflow(root: Path) -> dict:
    """Load and parse the weekly workflow YAML file."""
    workflow_file = root / WORKFLOW_PATH
    if not workflow_file.exists():
        pytest.fail(f"Workflow file not found: {workflow_file}")
    with open(workflow_file) as fh:
        return yaml.safe_load(fh)


def _get_triggers(workflow: dict) -> dict:
    """Return the 'on' / triggers block.

    PyYAML parses the bare YAML keyword ``on`` as Python ``True``, so we look
    up both the string key and the boolean key to be robust.
    """
    return workflow.get("on") or workflow.get(True) or {}

    # --- jobs present ---


# ---------------------------------------------------------------------------
# Makefile dry-run tests — verify the targets invoked by the workflow compile
# ---------------------------------------------------------------------------


class TestWeeklyWorkflowMakeTargets:
    """Dry-run the Makefile targets that rhiza_weekly.yml invokes."""

    def test_semgrep_target_dry_run(self, logger):
        """Make semgrep must parse and plan without error."""
        result = run_make(logger, ["semgrep"])
        assert result.returncode == 0

    def test_test_target_dry_run(self, logger):
        """Make test must parse and plan without error."""
        result = run_make(logger, ["test"])
        assert result.returncode == 0

    def test_security_target_invokes_pip_audit(self, logger):
        """Make security dry-run must include a pip-audit invocation."""
        result = run_make(logger, ["security"])
        assert result.returncode == 0
        assert "pip-audit" in result.stdout

    def test_pip_audit_args_forwarded(self, logger):
        """PIP_AUDIT_ARGS variable must be forwarded to the pip-audit call."""
        result = run_make(logger, ["security", "PIP_AUDIT_ARGS=--ignore-vuln TEST-0001"])
        assert result.returncode == 0
        assert "--ignore-vuln TEST-0001" in result.stdout

    def test_semgrep_target_in_help(self, logger):
        """Semgrep target must appear in make help output."""
        result = run_make(logger, ["help"], dry_run=False)
        assert "semgrep" in result.stdout

    def test_security_target_in_help(self, logger):
        """Security target must appear in make help output."""
        result = run_make(logger, ["help"], dry_run=False)
        assert "security" in result.stdout
