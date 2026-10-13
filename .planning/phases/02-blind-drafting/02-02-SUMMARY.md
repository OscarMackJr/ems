---
phase: 02-blind-drafting
plan: 02
subsystem: archive-assessment-applicability
tags: [pytest, validator, schemas, drafting]
requires: [02-01]
provides:
  - tests/test_archive_assessment_rule_proposals.py
key-files:
  created:
    - tests/test_archive_assessment_rule_proposals.py
  committed:
    - scripts/validate_archive_assessment_rule_proposals.py
    - schemas/archive_assessment_not_applicable_rule_proposals.schema.json
    - schemas/archive_assessment_rule_proposals_drafting_record.schema.json
requirements: [DRAFT-01, DRAFT-02, DRAFT-03]
metrics:
  tasks: 3
  completed: 2026-10-13
---

# Phase 2 Plan 02: Proposals tests and tooling commit Summary

Pytest module for the proposals validator and schemas, committed together with the validator and both schemas in one tooling commit (c8b2712) of exactly four explicit paths.

## What was built
- 62 test functions: in-test fixture of 21 uniform PROPOSE_NO_RULE entries built from the live catalog, fail-closed cases (both validator and schema where the schema can express the rule), schema-equality and check_schema tests, record fixture tests, source guards, a case-insensitive term-scan with a self-test (term list lives only in the test), and file-existence-gated tests for the real proposals file, brief and drafting record (catalog drift, fingerprint, header equality, brief extract equality).
- Regression run: 147 passed, 11 skipped (the gated cases, reason "not yet written"), 0 failed, across the AA3 authority tests, the v2 tests and the new module.
- Commit contains no registry path; the two unrelated modified registry files and all untracked files were left untouched.

## Deviations from Plan
- Seven fail-closed cases (catalog sha256 altered, catalog blob id altered, duplicate control, governance id string in rationale, alternative equal to outcome, shape_limitation scope mismatch, absolute path) are validator-only rather than both-reject, because JSON Schema cannot express those cross-field or live-value checks. The validator rejects all of them.

## Self-Check: PASSED
