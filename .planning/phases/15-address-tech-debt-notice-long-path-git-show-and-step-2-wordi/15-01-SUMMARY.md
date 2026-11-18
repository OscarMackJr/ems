---
phase: 15-address-tech-debt-notice-long-path-git-show-and-step-2-wordi
plan: 01
subsystem: archive-assessment-notice
tags: [notice-2.0.3, tech-debt, windows-long-path]
requires: []
provides:
  - "2.0.3 notice with git show '--', core.longpaths hint and prerequisite, honest step 2 wording"
affects: [notice-2.0.3]
key-files:
  modified:
    - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
    - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
    - registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json
    - docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md
    - schemas/archive_assessment_demo3_w1_req_001_notice_2_0_3.schema.json
decisions:
  - "'--' in git_show is the fix for the step 3 long-path failure: without it git lstat()s '<rev>:<path>' as a possible file name and fails with 'Filename too long' (exit 128) under a deep root; with it git show exits 0 (reproduced in 15-REVIEW.md). core.longpaths is only needed for the clone/checkout in step 1. (Corrected by 15-REVIEW-FIX WR-02; the original line wrongly called '--' defensive only.)"
metrics:
  tasks: 3
  files: 5
  completed: 2026-11-17
---

# Phase 15 Plan 01: Notice long-path and step 2 wording Summary

Closed audit WARNING-1 and WARNING-2 in the 2.0.3 notice: git_show now passes `--`, the error hint and a fifth prerequisite name `core.longpaths`, and step 2 / the outcomes row no longer claim plain --validate proves the 1544dc1 binding (step 3 enforces it; all three steps required).

## Verification of git behavior
`git show 1544dc1...:registry/archive_assessment_governance_decisions.json` with and without `--`: both exit 0, identical bytes (59113 bytes, cmp equal). No long-path failure was observable in this checkout, because its root is short.

Correction (15-REVIEW WR-02): under a deep checkout root with `core.longpaths=false`, `git show <rev>:<120-char path>` without `--` exits 128 with `fatal: failed to stat ...: Filename too long`, and with `--` it exits 0. So `--` alone fixes the step 3 failure; `core.longpaths` only matters for the clone/checkout in step 1, and the `git_show` error hint names it only when git reports `Filename too long`.

## Commits
- c049daa: builder edits (fix)
- 5694189: four new tests
- 35b2980: notice JSON, Markdown, schema regenerated via --emit-schema / --build

## Results
- `--validate` prints PASS; 2.0.3 test file 94 passed; frozen reply + 2.0.2 notice tests 242 passed, untouched.
- Reply and 2.0.2 builders unmodified.

## Deviations from Plan
None. (A Python escape in the `C:\\ems` literal was fixed before building.)

## Self-Check: PASSED
