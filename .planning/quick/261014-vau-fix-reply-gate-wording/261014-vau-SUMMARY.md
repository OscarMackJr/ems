---
quick_id: 261014-vau
slug: fix-reply-gate-wording
status: complete
completed: 2026-10-15
commit: 258875d
key-files:
  modified:
    - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
    - registry/archive_assessment_demo3_w1_req_001_reply.json
    - docs/DEMO3_W1_REQ_001_REPLY.md
decisions:
  - "Oscar Mack approved the regenerated gate wording as shown (2026-10-15); gate 3 left unchanged"
---

# Quick Task 261014-vau: Fix reply gate wording — Summary

Two history-note gates in the DEMO3-W1-REQ-001 reply now state what the code enforces (milestone audit AUDIT-W1, AUDIT-W2):

- Gate 1: the sign-off approver role must be EMS_GOVERNANCE_AUTHORITY; the Hayes Verify developer role is rejected.
- Gate 4: the schema rejects unknown fields in a rule, a condition and the source lineage, and a repeated field within one rule; an extra field on a decided control row is rejected by the Python validator.

## Verification

- Reply `--build` then `--validate`: PASS
- Publisher `--validate`: PASS (authority 2.0.1 at 31addfa unchanged, no republish)
- `pytest tests -k archive_assessment`: 492 passed
- Commit 258875d holds only the three files above; unrelated modified files untouched

## Deviations

Executed inline by the orchestrator, not by planner/executor subagents: Bash fails on this machine (cygwin fatal error) and the GSD agents have no PowerShell tool, so they could not run the build, validators or tests.
