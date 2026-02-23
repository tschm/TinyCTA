---
on:
  issues:
    types: [opened]

description: "Automatically triage new issues with labels and initial response"

engine: copilot

permissions:
  issues: read
  contents: read

tools:
  github:
    toolsets: [issues, repos]

safe-outputs:
  add-comment:
  add-labels:
    allowed: ["bug", "enhancement", "question", "documentation", "good first issue"]

network:
  allowed:
    - defaults
---

# Issue Triage

A new issue has been opened: #${{ github.event.issue.number }}

## Instructions

1. Read the issue title and body
2. Classify the issue type:
   - **bug**: Something is broken or not working as expected
   - **enhancement**: A feature request or improvement
   - **question**: A question about usage or behaviour
   - **documentation**: Documentation improvement needed
   - **good first issue**: Simple enough for new contributors
3. Apply appropriate label(s)
4. Post a helpful initial comment acknowledging the issue and providing relevant context

## Guidelines

- Be welcoming and helpful
- If it's a bug, ask for reproduction steps if not provided
- If it's a question, point to relevant documentation in `docs/`
- If it's an enhancement, acknowledge and note it for maintainer review
- Never close issues automatically
