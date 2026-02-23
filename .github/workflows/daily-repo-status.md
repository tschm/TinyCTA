---
on:
  schedule:
    - cron: "0 9 * * 1-5"  # Weekdays at 09:00 UTC
  workflow_dispatch:

description: "Daily status report for the repository"

engine: copilot

permissions:
  issues: read
  contents: read
  pull-requests: read

tools:
  github:
    toolsets: [repos, issues, pull_requests]

safe-outputs:
  create-issue:
    labels: ["report", "automated"]

network:
  allowed:
    - defaults
    - python
---

# Daily Repository Status Report

Analyze the current state of this repository and produce a concise status report.

## What to include

- **Open issues**: Count and highlight any critical/blocking issues
- **Open PRs**: Count, age, and any stale PRs (>7 days without activity)
- **Recent CI status**: Summary of recent workflow runs (pass/fail trends)
- **Recent releases**: Most recent release tag and date
- **Test coverage**: If available, report current coverage percentage
- **Dependencies**: Note any outdated or flagged dependencies

## Style

- Be concise and factual
- Use tables where appropriate
- Highlight action items clearly
- Max 500 words

## Process

1. Read repository metadata, issues, and PRs
2. Check recent workflow run status
3. Compile findings into a structured report
4. Create an issue with the report
