---
phase: 16-test-robustness-and-review-closure
plan: 05
subsystem: phase-gate
tags: [gate, frozen-files, ci]
requirements: [BASE-01, BASE-02, BASE-03, BASE-04, GATE-13, GATE-14, GATE-15, BOOK-01, BOOK-02]
key-files:
  created: []
  modified:
    - tests/test_archive_assessment_lineage_validation.py
metrics:
  completed: 2026-11-18
  tasks: 2
status: complete
---

# Phase 16 Plan 05: Phase gate Summary

## Task 1: Orchestrator-run local gates (PowerShell)

| Gate | Result |
|------|--------|
| Frozen files, committed: `git diff --ignore-cr-at-eol --exit-code 9a10810..HEAD` over publisher v2, reply builder and 2.0.2 notice builder | exit 0 |
| Frozen files, working tree: the same 3 scripts | exit 0 |
| Phase-commit scope: `git diff --name-only 9a10810..HEAD` | only `.planning/`, `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` and 5 `tests/test_archive_assessment_*` files. No `registry/`, `schemas/`, `generated/` or sign-off file |
| 2.0.3 notice `--validate` | PASS |
| Publisher v2 plain `--validate` (also covers the decisions digest invariant and the 21/59 counts) | PASS |
| pytest with `EMS_FAIL_ON_SKIP=1` over the 13 `tests/test_archive_assessment_*.py` files | 1133 passed, 0 skipped (after the fix below) |

### The gate found a defect in 16-01

The first full run gave 1130 passed and 3 failed. One failure was named: `test_d10_live_catalog_edit_or_delete_does_not_change_validate_outcome`.

- **Cause:** the new `overlay()` helper ran `git add` on the 10 publication paths. Seven of them are under the gitignored `generated/` tree; they are tracked, but they are ignored in the clone context, so `git add` refused them.
- **Fix:** `git add -f`, the minimal change (b47a93f). The test's assertions are unchanged.
- **Reruns after the fix:**
  - `test_archive_assessment_lineage_validation.py`: 83 passed
  - `test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`: 109 passed
  - the other 11 files: 941 passed
  - Total: 1133 passed, 0 skipped.
- **The other 2 failures:** the first run's output was truncated, so they could not be named, and they did not reproduce in the per-file reruns. They are recorded as unexplained local failures. CI is the authoritative evidence.

The clone-based tests (D-10 baseline, deep-root, `make_clone`) ran locally without the sh.exe crash in this session.

## Task 2: Push and CI archive-assessment

- The user approved the push (2026-11-18).
- `git push` succeeded on the first try: `05b5459..b47a93f`.
- `workflow_dispatch` run 44408700761 (https://github.com/OscarMackJr/ems/actions/runs/44408700761):
  - Conclusion: **success**. Head SHA `b47a93f749b439f45bb064cbb4b8f08f06ddd4f6`, which equals local HEAD.
  - `validate` job: success.
  - `archive-assessment` job: success. **1133 passed**, 0 skipped (`EMS_FAIL_ON_SKIP=1`). The rewritten D-10 baseline test is included.
  - All **7/7 validators print PASS**.

The deep-root Windows branch is not exercised on ubuntu CI. Its local evidence is the 109-passed run of the 2.0.3 notice test file in this session.

## Self-Check: PASSED
