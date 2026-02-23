---
on:
  workflow_run:
    workflows: ["*"]
    types: [completed]
    branches: [main]
  workflow_dispatch:

if: github.event.workflow_run.conclusion == 'failure'

description: "Diagnose and suggest fixes for failing CI workflows"

engine: copilot

permissions:
  contents: read
  actions: read
  issues: read

tools:
  github:
    toolsets: [repos, issues, actions]
  bash: ["make test", "make fmt", "uv run pytest"]

safe-outputs:
  create-issue:
    labels: ["ci", "automated", "needs-attention"]

network:
  allowed:
    - defaults
    - python
---

# CI Failure Diagnosis

A CI workflow has failed on the main branch. Diagnose the failure and suggest fixes.

## Instructions

1. Identify which workflow failed and on which commit
2. Read the workflow logs to understand the failure
3. Check if the failure is:
   - A test failure (examine test output)
   - A lint/format issue (check ruff output)
   - A dependency issue (check uv/pip output)
   - An infrastructure issue (runner, network, etc.)
4. If possible, identify the root cause commit
5. Suggest a concrete fix

## Rhiza project context

This is a Rhiza-based Python project. Key commands:
- `make test` — run pytest with coverage
- `make fmt` — run ruff format + check
- `make deptry` — check dependencies
- `uv run pytest` — run tests via uv

## Output

Create an issue with:
- **Workflow**: Name and run URL
- **Failure type**: Classification
- **Root cause**: What went wrong
- **Suggested fix**: Concrete steps or code changes
- **Severity**: Critical / Warning / Info
