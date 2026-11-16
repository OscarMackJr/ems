---
phase: 12-verify-at-pin-and-gate-hardening
plan: 03
subsystem: archive-assessment-applicability-authority (tests, frozen reply builder)
tags: [GATE-10, IN-02, IN-03, IN-04, IN-06, D-13, D-16]
requires: [12-02]
provides:
  - 2.0.0 anchor bound to the frozen 2.0.1 publisher constant and the 2.0.1/2.0.2 supersedes chain
  - D-08 row-tamper coverage of NOT_YET_DECIDED, NO_RULE_WILL_BE_PUBLISHED and RULE_PUBLISHED rows
  - uniform git-error handling in the reply builder's resolve_record_commit
affects: [12-04, 12-07]
tech-stack:
  added: []
  patterns: [exec of a pinned publisher blob into a throwaway module (tests only)]
key-files:
  created: []
  modified:
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - tests/test_archive_assessment_demo3_w1_req_001_reply.py
    - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
    - .planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md
decisions:
  - "[Phase 12] 2.0.0 anchor literal gains relative_path so it equals the frozen SUPERSEDED_V2_0_0 at 31addfa by full dict equality"
  - "[Phase 12] Reply resolve_record_commit: merge-base rc 1 = not an ancestor; any other rc or OSError = cannot check ancestry (D-13, reply builder only; notice builder deferred)"
metrics:
  duration: ~35 min
  completed: 2026-11-16
  tasks: 2
  files: 4
---

# Phase 12 Plan 03: GATE-10 IN-02, IN-03, IN-04, IN-06 Summary

The 2.0.0 superseded-constant test now checks the real `SUPERSEDED_V2_0_0` constant in the publisher blob at 31addfa and the 2.0.0 -> 2.0.1 -> 2.0.2 supersedes chain. The D-08 tamper test now covers rule, no-rule and undecided rows (12 cases). The reply builder's `resolve_record_commit` turns cat-file and merge-base OSError into AuthorityError and separates "not an ancestor" (rc 1) from "cannot check ancestry" (any other rc). The dead `log` handling is gone from the fake git.

## Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | IN-02 anchor bound to frozen publisher + chain; IN-06 tamper over 3 row kinds | e0d929b | tests/test_archive_assessment_applicability_authority_v2_publication.py |
| 2 | IN-03 drop dead log fake; IN-04 uniform resolve_record_commit errors | a3a9c9b | scripts/build_archive_assessment_demo3_w1_req_001_reply.py, tests/test_archive_assessment_demo3_w1_req_001_reply.py |

## Verification (measured)

- Task 1 targeted: `pytest tests/test_archive_assessment_applicability_authority_v2_publication.py -k "anchor or row_tamper"`: 13 passed, exit 0.
- Task 1 full: `EMS_FAIL_ON_SKIP=1 ... tests/test_archive_assessment_*.py --basetemp=.pytest-temp/p12-03-t1-full`: **932 passed**, exit 0, validators 1-6 PASS.
- Task 2 targeted: `pytest tests/test_archive_assessment_demo3_w1_req_001_reply.py`: 112 passed, exit 0. Reply `--validate`: PASS.
- Task 2 full: `--basetemp=.pytest-temp/p12-03-t2-full`: **935 passed**, exit 0, validators 1-6 PASS.
- grep checks: `log_sha` 0; `args[0] == 'log'` 0; `cannot check ancestry` in builder 2; `is not an ancestor of HEAD` in builder 1; `importlib|exec(|eval(` in builder **0 before and 0 after**.
- `git diff HEAD~1 HEAD -- scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` is empty; the publisher is unchanged.
- Ledger sections "After plan 12-03 Task 1" and "After plan 12-03 Task 2" were appended to 12-BASELINE-RED.md. Accepted red set: none.

## Deviations from Plan

1. **IN-02 literal extended.** The frozen `SUPERSEDED_V2_0_0` at 31addfa has a `relative_path` key that the test literal did not have. As the plan allows, the literal now includes `relative_path` (`registry/archive_assessment_applicability_authority_v2.json`). The test also asserts that the blob read through `sup['relative_path']` at the 2.0.0 commit equals the bytes the digest checks already verified. The check is full dict equality.
2. **IN-06 no-op guard.** None of the 12 tamper cases is a no-op: all three rows carry 8 `decision_ids`, and each tamper changes each row. The guard `assert r != before` is in place.
3. **IN-04 test match tightened.** The `mb_rc: 128` case matches `cannot check ancestry.*git merge-base exit 128`, so it checks both required fragments.
4. **TDD RED was reasoned, not run.** The IN-02 and IN-06 tests bind to behaviour that already exists, so they passed as soon as they were written; this is expected for test-only items. For IN-04, the old builder would fail the three new cases: rc 128 gave "not an ancestor", and OSError escaped as a raw OSError. That conclusion comes from reading the code; the tests were not run against the old builder.

## Known Stubs

None.

## Notes

- GATE-10 is not marked complete: IN-01 lands in 12-04.
- In plan 12-07, the third assertion of `test_2_0_0_anchor_matches_frozen_2_0_1_publisher_and_chain` (2.0.2 supersedes `MODULE.SUPERSEDED_V2_0_1`) moves to the 2.0.2 chain.

## Self-Check: PASSED

- FOUND: commit e0d929b, commit a3a9c9b
- FOUND: 12-BASELINE-RED.md sections for Task 1 and Task 2
