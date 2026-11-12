---
phase: 08-gate-and-schema-hardening
plan: 01
subsystem: governance-decisions-builder
tags: [GATE-05, D-13, norm_templated, grandfather]
requires: []
provides:
  - CERTIFIED_ANSWERS_SHA256 constant and digest-threaded strict_checks
affects:
  - scripts/build_archive_assessment_governance_decisions.py
tech-stack:
  added: []
  patterns: [digest-keyed grandfather exemption]
key-files:
  modified:
    - scripts/build_archive_assessment_governance_decisions.py
    - tests/test_archive_assessment_governance_answers.py
    - tests/test_archive_assessment_governance_decisions.py
key-decisions:
  - "D-13: cross-note uniqueness uses norm_templated except for the certified answers digest, which falls back to norm"
requirements-completed: [GATE-05]
duration: short
completed: 2026-11-12
---

# Phase 8 Plan 01: Cross-note uniqueness (GATE-05) Summary

Cross-note uniqueness in the governance-decisions builder now compares `norm_templated` forms for every answers file except the one whose LF SHA-256 equals `CERTIFIED_ANSWERS_SHA256` (`8efccce9...3a972`, verified equal to the live file and to the committed decisions' `answers_sha256`). Output is byte-neutral; no registry file was edited.

## Commits
- c821f5f: builder change (`answers_sha256` keyword on `validate_answers` and `strict_checks`, threaded from `build_decisions` and the CLI `--validate-answers`)
- 9a0ba04: tests

## Tests
- Fixtures in both test files now differ by words (a 21-word list) instead of control ids; `extra_entry` notes likewise.
- New: `test_notes_differing_only_in_templated_values_fail`, `test_certified_digest_grandfathers_committed_answers`, `test_changed_answers_bytes_remove_exemption`, `test_exemption_is_the_exact_constant`.
- `test_committed_answers_strict_when_filled` passes the certified digest.
- Tests were not run by the executor (orchestrator runs them).

## Deviations from Plan
- Decisions-test `built()` was left using the real committed digest: fixtures are now word-distinct, so the exemption is irrelevant to them and no change was needed.
- Files use CRLF; edits preserved CRLF.

## Self-Check: PASSED (commits c821f5f, 9a0ba04 exist; protected paths unchanged)
