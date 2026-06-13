"""Workflow tests for security-related CI gates."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load_workflow(name: str) -> dict[str, object]:
    path = ROOT / ".github" / "workflows" / name
    return yaml.load(path.read_text(), Loader=yaml.BaseLoader)


def test_ci_workflow_uses_rhiza_release_with_security_gate():
    """CI should use the Rhiza workflow version that exposes security scanning."""
    workflow = _load_workflow("rhiza_ci.yml")
    assert workflow["jobs"]["ci"]["uses"] == "jebel-quant/rhiza/.github/workflows/rhiza_ci.yml@v0.18.9"


def test_scorecard_workflow_is_present_and_uploads_sarif():
    """Scorecard workflow should publish SARIF results to code scanning."""
    workflow = _load_workflow("rhiza_scorecard.yml")
    assert workflow["name"] == "(RHIZA) SCORECARD"
    assert "branch_protection_rule" in workflow["on"]
    assert workflow["permissions"] == "read-all"

    analysis = workflow["jobs"]["analysis"]
    assert analysis["permissions"]["security-events"] == "write"
    assert analysis["steps"][-1]["with"]["sarif_file"] == "results.sarif"
