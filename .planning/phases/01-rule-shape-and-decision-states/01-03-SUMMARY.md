---
phase: 01-rule-shape-and-decision-states
plan: 03
subsystem: testing
tags: [pytest, jsonschema, applicability, not-applicable-rule]
requires: [01-02]
provides:
  - v2 pytest module proving SCHEMA-01..06
key-files:
  created: [tests/test_archive_assessment_applicability_authority_v2.py]
requirements-completed: [SCHEMA-01, SCHEMA-02, SCHEMA-03, SCHEMA-04, SCHEMA-05, SCHEMA-06]
completed: 2026-10-13
---

# Phase 1 Plan 03: v2 Tests Summary

71 pytest cases prove the v2 rule shape, three decision states, semantics block, D-12 resolver oracle and schema drift, with no dependence on `generated/` or any v2 registry file.

## Commits
- 39f1569: loader, helpers, positive cases, state/rule/authority negatives, carried-forward v1 negatives (48 tests)
- 380b533: semantics weakening, resolver oracle, drift, independence, non-rule-field tests (71 tests total)

## Verification
- `tests/test_archive_assessment_applicability_authority_v2.py`: 71 passed.
- v1 test file in this worktree: 12 failed, all FileNotFoundError on gitignored `generated/archive-assessment/ems-aa2/...` (environmental, as expected; the orchestrator re-runs in the main checkout).
- `git diff --quiet HEAD` on the v1 publisher, v1 registry and v1 test: clean. v1 schema file not touched.
- Checks that `registry/adjudication_rules.json` / `registry/policy_decisions.json` still show as modified cannot be observed in a worktree.

## Deviations from Plan
None. No defect found in the v2 publisher; no publisher edits. Duplicate-field cases are validator-only (named `_validator_only`) because JSON Schema cannot express it.

## Self-Check: PASSED
Test file exists; commits 39f1569 and 380b533 exist; commits contain only the test file.
