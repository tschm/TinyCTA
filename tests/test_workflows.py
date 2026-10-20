"""Workflow tests for security-related CI gates."""

from __future__ import annotations

import re
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


def _version(ref: str) -> tuple[int, ...]:
    """Parse a ``vX.Y.Z`` release tag into a comparable tuple."""
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", ref)
    assert match, f"{ref!r} is not a vX.Y.Z release tag"
    return tuple(int(part) for part in match.groups())


def _assert_pinned_to_release(uses: str, workflow: str) -> None:
    """Assert ``uses`` calls the Rhiza reusable workflow pinned to a release tag.

    Dependabot bumps these pins independently of ``.rhiza/template.yml``, so the
    tag may run ahead of the synced template, but never behind it.
    """
    prefix = f"jebel-quant/rhiza/.github/workflows/{workflow}@"
    assert uses.startswith(prefix), uses
    assert _version(uses.removeprefix(prefix)) >= _version(_template_ref())


def test_ci_workflow_uses_rhiza_release_with_security_gate():
    """CI should call the Rhiza reusable workflow pinned to a release at or above the synced template."""
    workflow = _load_workflow("rhiza_ci.yml")
    _assert_pinned_to_release(workflow["jobs"]["ci"]["uses"], "rhiza_ci.yml")


def test_scorecard_workflow_is_present_and_uploads_sarif():
    """Scorecard workflow should grant the token scopes needed to publish SARIF."""
    workflow = _load_workflow("rhiza_scorecard.yml")
    assert workflow["name"] == "(RHIZA) SCORECARD"
    assert "branch_protection_rule" in workflow["on"]
    assert workflow["permissions"] == "read-all"

    # Thin stub: the analysis (and SARIF upload) lives in the reusable workflow;
    # locally we assert the job calls it and grants security-events: write.
    scorecard = workflow["jobs"]["scorecard"]
    _assert_pinned_to_release(scorecard["uses"], "rhiza_scorecard.yml")
    assert scorecard["permissions"]["security-events"] == "write"
