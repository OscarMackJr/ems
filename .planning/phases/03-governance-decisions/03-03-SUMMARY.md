---
phase: 03-governance-decisions
plan: 03
subsystem: governance
tags: [decision-records, validator, jsonschema, pytest]
requires:
  - phase: 03-01
    provides: approved wording of the three statements
  - phase: 03-02
    provides: answers validator and worksheet
provides:
  - build_decisions / validate_decisions pair
  - Decisions schema emitted from code
  - --build and --validate CLI
affects: [03-04]
key-files:
  created:
    - schemas/archive_assessment_governance_decisions.schema.json
    - tests/test_archive_assessment_governance_decisions.py
  modified:
    - scripts/build_archive_assessment_governance_decisions.py
key-decisions:
  - "decision ids are AA4-GOV-NNN by answers position; supersession entries append and name the superseded id"
  - "validator re-checks proposals and drafting-record digests against live files; answers digest checked in the gated real-file test"
duration: short
completed: 2026-10-13
---

# Phase 3 Plan 03: Decision Record Builder Summary

Pure build/validate pair for the 21 governance decision records, with a const-heavy schema (dual-role sentence, approver, roles, both header statements) and mutation tests on synthetic answers; no real decisions file exists yet.

## Commit
- 6e4f953: script extension, decisions schema, decisions tests.

## Verification
`python -m pytest tests/test_archive_assessment_governance_answers.py tests/test_archive_assessment_governance_decisions.py tests/test_archive_assessment_rule_proposals.py tests/test_archive_assessment_rule_proposals_record.py -q` -> 184 passed, 3 skipped (real decisions file tests x2, strict-on-real-answers).
`--build` on the blank answers file raises AuthorityError and writes nothing.

## Deviations from Plan
- Settings S1-S3 in the approval file matched the plan 02 defaults, so no plan 02 file was changed.
- scope_note.drafted_note is an object (scope, note) because the proposals hold shape_limitation as an object; the schema reflects that.
- Task 3 folded into the single commit as specified; tasks 1 and 2 not committed separately.

## Known Stubs
None.

## Self-Check: PASSED
