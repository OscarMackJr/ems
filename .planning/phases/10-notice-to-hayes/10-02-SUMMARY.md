---
phase: 10-notice-to-hayes
plan: 02
subsystem: archive-assessment
tags: [notice, generation, review, hayes]
requires: [10-01 builder and tests]
provides: [generated notice Markdown, JSON and closed schema, code commit 47343a1]
affects: [10-03 notice commit and CI]
key-files:
  created:
    - docs/DEMO3_W1_REQ_001_NOTICE_2_0_2.md
    - registry/archive_assessment_demo3_w1_req_001_notice_2_0_2.json
    - schemas/archive_assessment_demo3_w1_req_001_notice_2_0_2.schema.json
  modified: []
requirements: [NOTICE-01, NOTICE-02]
completed: 2026-11-12
---

# Phase 10 Plan 02: Gate, commit code, generate and review Summary

The orchestrator ran the tests in PowerShell with `--basetemp`, committed the builder and tests as 47343a1, and generated the three notice files. Oscar Mack approved the rendered notice (D-12).

## Tasks

1. **Test gate.** The first run gave 1 failed and 47 passed. `test_validate_reports_ungenerated_files` points `NOTICE_JSON` at a temp path outside the repository root, so `V2.rel` raised ValueError before the AuthorityError the test expects. Fix: `validate_notice` now falls back to the file name for paths outside `V2.ROOT`. The rerun gave 48 passed, 0 skipped.
2. **Commit and generate.** `feat(10-02): add notice builder and tests for 2.0.2` (47343a1) contains exactly the builder and the test file, staged by explicit path. `--emit-schema`, `--build` and `--validate` were run, and `--validate` printed PASS.
   - The JSON contains the full ae15c74 SHA, `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2` and `2.0.2`.
   - The Markdown contains the three digest names, RAW_BYTES, 21, 59 and 4e746d1f, and none of the forbidden words.
   - After generation, pytest was rerun against the generated files: 48 passed.
3. **D-12 review.** Oscar Mack approved the notice without wording changes.

## Deviations

- The builder was fixed before the code commit (see task 1).
- NOTICE_DATE is 2026-11-12, the actual generation date, not the plan's 2026-11-13 default.

## Self-Check: PASSED
