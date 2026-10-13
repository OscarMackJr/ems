---
phase: 03-governance-decisions
plan: 02
subsystem: governance
tags: [worksheet, validator, jsonschema, pytest]
requires:
  - phase: 03-01
    provides: governance wording approval (S1-S4 settings)
provides:
  - Neutral read-only view of the 21 drafts
  - Blank 21-entry answers worksheet and answers schema
  - Lenient and strict answers validator
affects: [03-03, 03-04]
key-files:
  created:
    - scripts/build_archive_assessment_governance_decisions.py
    - schemas/archive_assessment_governance_answers.schema.json
    - registry/archive_assessment_governance_answers.json
    - docs/ARCHIVE_ASSESSMENT_RULE_PROPOSALS_VIEW.md
    - tests/test_archive_assessment_governance_answers.py
key-decisions:
  - "Strict mode needs 21 individual dispositions, distinct notes of 20+ chars, and disposition consistent with drafted outcome; no approve-all value exists"
  - "emit-template refuses to overwrite an existing answers file"
duration: short
completed: 2026-10-13
---

# Phase 3 Plan 02: Governance Worksheet Tooling Summary

Neutral view, blank 21-entry answers file, fail-closed strict/lenient validator and schema, imported V2.validate_rule for rule shape; the tooling never writes any answer content.

## Commit
- dd37c25: the five files above (only these were staged).

## Verification
`python -m pytest tests/test_archive_assessment_governance_answers.py tests/test_archive_assessment_rule_proposals.py tests/test_archive_assessment_rule_proposals_record.py -q` -> 138 passed, 1 skipped (strict-on-real-file, skipped while answers blank).

## Deviations from Plan
- Duplicate-control test is validator-only (JSON schema cannot express uniqueness by field); other cases assert both validator and schema.
- Malformed-JSON test uses tempfile instead of pytest tmp_path (tmp_path hit a Windows PermissionError on the system pytest temp root).
- Tasks 1-3 committed as one commit, as the plan's Task 3 specifies.

## Notes
- The view-on-disk byte-equality test assumes LF; git warned of CRLF conversion under autocrlf, so a fresh CRLF checkout could make that test fail.

## Known Stubs
None. The answers file is intentionally blank until plan 04.

## Self-Check: PASSED
