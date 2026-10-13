---
phase: 02-blind-drafting
plan: 01
subsystem: archive-assessment-applicability
tags: [validator, schema, drafting]
requires: []
provides:
  - scripts/validate_archive_assessment_rule_proposals.py
  - schemas/archive_assessment_not_applicable_rule_proposals.schema.json
  - schemas/archive_assessment_rule_proposals_drafting_record.schema.json
key-files:
  created:
    - scripts/validate_archive_assessment_rule_proposals.py
    - schemas/archive_assessment_not_applicable_rule_proposals.schema.json
    - schemas/archive_assessment_rule_proposals_drafting_record.schema.json
requirements: [DRAFT-01, DRAFT-02, DRAFT-03]
metrics:
  tasks: 2
  completed: 2026-10-13
---

# Phase 2 Plan 01: Proposals validator and schemas Summary

Validator for the 21-control rule proposals file and the later drafting record, reusing the v2 publisher's `validate_rule` and `semantics` by file-location import, plus two emitted Draft 2020-12 schemas.

## What was built
- `validate_proposals` enforces the exact header (status DRAFT_NO_AUTHORITY, non-authority statement, v2 `semantics()` frame, catalog fingerprint by git blob id and blob-bytes SHA-256), exactly 21 control ids, per-proposal key set, live catalog_inputs equality, labelled interpretation, 2-4 sentence rationale, confidence, alternative_considered, shape_limitation; rejects authority/decision-id keys, AA-GOV id strings and absolute paths.
- `validate_record` checks the drafting record (D-24); `--validate`, `--validate-record`, `--emit-schema` CLI. `--validate` fails closed (AuthorityError) while the proposals file is absent.
- Schemas emitted via `--emit-schema`; idempotent; pass `check_schema`; no authority or decision-id properties.
- Functional spot check: a synthetic 21-entry PROPOSE_NO_RULE document passed validator and schema; adding a `decision_id` key was rejected.

## Deviations from Plan
- Worktree base was reset to 1f96cff per the startup check (merge-base differed). No other deviations.

## Uncommitted by design
Per the plan, the script and both schemas are left untracked for plan 02's single tooling commit. This SUMMARY is the only file committed by this plan.

## Self-Check: PASSED
