---
phase: 09-certified-republication-2-0-2
plan: 03
subsystem: archive-assessment v2 publisher
tags: [D-09, D-10, sign-off summary, PUB-07, PUB-08]
requirements: [PUB-07, PUB-08]
key-files:
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
metrics:
  completed: 2026-11-12
---

# Phase 9 Plan 03: Complete the dry-run sign-off summary Summary

dry_run_summary still shows 21 decided and 59 undecided controls, the AA4 ids and states, the 3 rules in full, the authority LF digest, and the line saying 2.0.2 supersedes 2.0.1 at 31addfa with no decision changed. It now also has a neutral "What changed in 2.0.2" section. Every value in that section is derived, not typed:
- each lineage entry with its normalisation (AA1 manifest RAW_BYTES)
- the mutation count, len(NEGATIVE_MUTATIONS) = 29
- the 16 schema levels with additionalProperties false, walked from schema()
- the 2.0.1 → 2.0.2 row-comparison result ("80 controls identical to 2.0.1")
- the GATE-01 to GATE-05 hardening

The row comparison was factored into `rows_differing_from_previous`, and validate_publication still raises the same messages through it.

## Commits
- 251cb30: feat — what-changed block, rows_differing_from_previous, closed_schema_levels, extended dry-run summary test

## Verification
- The executor ran the dry run read-only. It wrote nothing; `git status` of registry/, generated/ and schemas/ was unchanged.
- Greps found the heading, RAW_BYTES, GATE-01, 31addfa, 21 and 59. They found no "Published on" and none of best, critical, important, recommended or highest.
- The orchestrator ran the full `-k archive_assessment` suite: 717 passed, 3 failed, all of them the accepted red set.
- The commit touches only the two planned files.

## Deviations from Plan
- The publication test file has LF endings in the working tree, not CRLF as assumed; they were preserved. No other deviations.

## Self-Check: PASSED
