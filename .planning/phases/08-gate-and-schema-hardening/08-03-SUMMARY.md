---
phase: 08-gate-and-schema-hardening
plan: 03
subsystem: archive-assessment v2 publisher
tags: [schema, mutation-gates, SCHEMA-07, GATE-02]
requirements: [SCHEMA-07, GATE-02]
key-files:
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - tests/test_archive_assessment_applicability_authority_v2.py
metrics:
  completed: 2026-11-12
---

# Phase 8 Plan 03: Closed schema and narrowed mutation gates Summary

schema() now declares the 14 previously undeclared properties and sets additionalProperties false on the top level, control rows and not_applicable_semantics; mutations grow 26 to 29 and mutation_gates counts only domain errors.

## Commits
- a2fc8d0: publisher changes (Tasks 1 and 2 committed together, same file)
- a89bcce: tests (Task 3)

## Changes
- Schema closed at three levels; the real built authority validates against it (probed).
- Added mutations extra_top_level_field, extra_field_on_undecided_row, extra_field_in_semantics (schema_must_reject). extra_top_level_field is rejected by SCHEMA only (the Python validator accepts it).
- mutation_gates: AUTHORITY/SIGNOFF catch AuthorityError, DECISIONS catches ValueError; schema gates unchanged; output shape unchanged.
- D-05 probe: all AUTHORITY mutations raise AuthorityError (or are accepted by Python, never crash); no validator rewrite needed.
- Tests: counts 29, new SCHEMA-07 tests, propagation tests for KeyError/TypeError/AttributeError on all three targets, publish() propagation test, per-mutation domain-error regression.

## Deviations from Plan
Tasks 1 and 2 committed as one commit (same file). Otherwise none. No pytest was run by this agent (orchestrator verifies); py_compile and an inline probe passed.

## Verification
`.\.venv\Scripts\python.exe -m pytest tests/test_archive_assessment_applicability_authority_v2_publication.py tests/test_archive_assessment_applicability_authority_v2.py -p no:cacheprovider -q --basetemp=.pytest-temp/p8-03b`
Expected red set: test_committed_schema_equals_schema_function and test_real_published_files_validate only.

## Self-Check: PASSED
