"""Workflow tests for security-related CI gates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load_workflow(name: str) -> dict[str, Any]:
    """Load a workflow YAML, normalizing the truthy ``on:`` key back to a string."""
    path = ROOT / ".github" / "workflows" / name
    workflow = yaml.safe_load(path.read_text())
    if True in workflow and "on" not in workflow:
        workflow["on"] = workflow.pop(True)
    return workflow


def _template_ref() -> str:
    """Return the Rhiza template version pinned in .rhiza/template.yml."""
    template = yaml.safe_load((ROOT / ".rhiza" / "template.yml").read_text())
    return str(template["ref"])


def test_ci_workflow_uses_rhiza_release_with_security_gate():
    """CI should call the Rhiza reusable workflow pinned to the synced template version."""
    workflow = _load_workflow("rhiza_ci.yml")
    expected = f"jebel-quant/rhiza/.github/workflows/rhiza_ci.yml@{_template_ref()}"
    assert workflow["jobs"]["ci"]["uses"] == expected


def test_scorecard_workflow_is_present_and_uploads_sarif():
    """Scorecard workflow should grant the token scopes needed to publish SARIF."""
    workflow = _load_workflow("rhiza_scorecard.yml")
    assert workflow["name"] == "(RHIZA) SCORECARD"
    assert "branch_protection_rule" in workflow["on"]
    assert workflow["permissions"] == "read-all"

    # Thin stub: the analysis (and SARIF upload) lives in the reusable workflow;
    # locally we assert the job calls it and grants security-events: write.
    scorecard = workflow["jobs"]["scorecard"]
    assert scorecard["uses"] == f"jebel-quant/rhiza/.github/workflows/rhiza_scorecard.yml@{_template_ref()}"
    assert scorecard["permissions"]["security-events"] == "write"
