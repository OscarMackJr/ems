---
phase: 16-test-robustness-and-review-closure
plan: 01
subsystem: tests
tags: [pytest, d10-baseline, review-closure]
requirements-completed: [BASE-01, BASE-03, BASE-04, GATE-13]
key-files:
  modified:
    - tests/test_archive_assessment_lineage_validation.py
    - tests/test_archive_assessment_skip_guard.py
    - tests/test_archive_assessment_demo3_w1_req_001_reply.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
metrics:
  completed: 2026-11-18
---

# Phase 16 Plan 01: D-10 baseline test and IN-07 test parts Summary

The D-10 baseline test now overlays the working-tree publication paths and publisher (LF-normalised, committed in the clone only when the index differs), picks `--validate --at-pin` or plain `--validate` from the clone's record versus the authority's `source_lineage.supersedes`, and reads UTF-8 stdout only.

## Commits
- 04e5ff6: D-10 baseline rewrite (overlay, validate_mode, UTF-8 outcome, mode and stderr in assert messages, D-08a red-window comment)
- c1cec3a: HINT wording test (BASE-04), reply test `cat_exc` match fixed, source grep removed from `test_at_pin_binding_reads_supersedes_from_authority` (`import inspect` kept, other uses remain)

## Notes
- BASE-04: `tests/aa_history.py` already carries the fixed HINT and verbatim shallow output (8dd3778); not edited, regression test added.
- No script edited (publisher, reply builder, 2.0.2 notice builder untouched).
- Verification: py_compile OK on all four files; targeted pytest (hint, resolve_record_commit, at_pin_binding) 12 passed. The clone-based D-10 test was not run locally (clone unreliable); CI is authoritative.

## Deviations from Plan
None.

## Self-Check: PASSED
