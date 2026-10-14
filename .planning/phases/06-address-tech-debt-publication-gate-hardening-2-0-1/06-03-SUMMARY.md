---
phase: 06-address-tech-debt-publication-gate-hardening-2-0-1
plan: 03
subsystem: archive-assessment governance-decisions builder
tags: [wr-05, wr-07, wr-08, wr-10, hardening]
requires: []
provides:
  - builder constants sourced from the v2 publisher
  - published-digest refusal with --supersede-published
key-files:
  modified:
    - scripts/build_archive_assessment_governance_decisions.py
    - tests/test_archive_assessment_governance_decisions.py
decisions:
  - "--build refuses a refreshable rewrite when the v2 authority lineage digest equals the current decisions digest, unless --supersede-published (prints republish and re-sign-off notice)"
metrics:
  tasks: 2
  files: 2
  completed: 2026-10-14
requirements: [D-01, D-11, D-22]
---

# Phase 6 Plan 03: Builder Hardening Summary

The governance-decisions builder now takes its approver, roles, dual-role statement and 21-id list from the v2 publisher, and `--build` refuses to rewrite a decisions file that the v2 authority has already published unless `--supersede-published` is given.

## What changed

- WR-10: `APPROVER`, `APPROVER_ROLES`, `DUAL_ROLE_STATEMENT` and `CONTROL_IDS` are now taken from `V2`. A test asserts equality and that the literals no longer appear in the builder source.
- WR-05: new `is_published()` and `--supersede-published` flag. The refusal message contains "republish" and "sign-off"; with the flag, a notice with "republish" and "re-sign-off" is printed. An identical-bytes rebuild still prints PASS.
- WR-07: the emit-template test uses `sys.executable` and asserts `'already exists'` in stderr.
- WR-08: new tests run `main()` for real with patched `DECISIONS`, `ANSWERS` and `V2.AUTHORITY` in a module-level temp dir, covering the append case, the changed-record refusal, the published refusal, the flag, and the identical no-op.

## Verification

Archive-assessment suite: 410 passed. `--validate` prints PASS. Registry decisions file and answers schema untouched. `--emit-schema` was never run.

## Deviations from Plan

The plan expected the WR-08 cases 1 and 2 to fail before the edit. They passed, because `main()` already behaved that way; only the WR-10, WR-05 refusal and flag tests failed first. No other deviations. The Task 1 and Task 2 changes went into one commit, as the plan allows.

## Commits

- a2c3014: fix(06-03): builder constants from publisher, published-digest refusal, real CLI tests

## Self-Check: PASSED
