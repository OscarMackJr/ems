---
phase: 16-test-robustness-and-review-closure
verified: 2026-11-18T00:00:00Z
status: passed
score: 5/5 success criteria verified
overrides_applied: 0
---

# Phase 16: Test Robustness and Review Closure Verification Report

**Phase Goal:** Tests and validators guarding the authority are honest about what they check; every selected review info item from phases 11-15 is fixed with a test or closed with a recorded reason; frozen builders untouched.
**Status:** passed
**Re-verification:** No

## Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | D-10 baseline passes at publication and later commits, checks working tree, UTF-8 stdout, stderr separate | VERIFIED | `tests/test_archive_assessment_lineage_validation.py`: `overlay()` copies working-tree publication paths with `git add -f` (l.35-46). `mode_for` picks `--validate --at-pin` only when record identity equals `supersedes_identity()` (l.49-66). Subprocess runs with `text=True, encoding='utf-8'`, and stderr is kept separate (l.408-410). CI run 44408700761 passed the test. |
| 2 | Deep-root git_show test fails loudly unless `Filename too long` reproduces without `--`; no skips under `EMS_FAIL_ON_SKIP=1` | VERIFIED | `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` l.740-751: `pytest.fail` on setup problems; asserts `bare.returncode != 0 and b'Filename too long' in bare.stderr`. Local run 1133 passed, 0 skipped. CI run: 0 skipped. |
| 3 | Every selected 11/12/14/15 item has a disposition in 16-REVIEW-CLOSURE.md | VERIFIED | The ledger has rows for 11 IN-08/09, 12 IN-01..07 (IN-06 split), 14 IN-01..05, 15 IN-01..03. Dispositions match the roadmap: 14 IN-01..05 and 15 IN-02/03 FIXED with named tests; 12 IN-07 test parts FIXED and the reply-builder message CLOSED as frozen; 12 IN-01..04 and the IN-06 digest-check move DEFERRED-17; 12 IN-05 and the IN-06 decisions-builder scope SUPERSEDED by SEC-04 and SEC-02; 15 IN-01 DEFERRED-19. Front-matter counts add up (11+1+5+1+2 = 20 rows). |
| 4 | History hint and shallow-output fixed, or recorded out of scope | VERIFIED | 11 IN-08 and IN-09 are FIXED in `tests/aa_history.py`, a test helper (commits 8dd3778 and c1cec3a), with regression tests `test_hint_says_opt_out_only_skips_guarded_tests` and `test_history_problem_unrecognised_shallow_output_is_problem`. |
| 5 | Phase 11-13 SUMMARY `requirements-completed`; V2-01/V2-02 deferred; unrelated changes kept out | VERIFIED | Grep shows `requirements-completed` in all sampled 11-xx, 12-xx and 13-xx SUMMARY files (for example 11-01 FROZEN-01, 12-07 PIN-01/PIN-02/GATE-06, 13-04 PUB-10..12). REQUIREMENTS.md l.113-114 lists V2-01 and V2-02 as Deferred. Per the orchestrator, 16-04 changed 18 files, 18 insertions, commit 850f0da. Phase commits touch only `.planning/`, the 2.0.3 notice builder and 5 test files. |

## Invariants

| Invariant | Status | Evidence (orchestrator-gathered, accepted) |
|-----------|--------|-------|
| Frozen publisher v2, reply builder and 2.0.2 notice builder unchanged | VERIFIED | `git diff --ignore-cr-at-eol` exit 0 for the range and the working tree |
| Decisions digest `4e746d1f...`; 21 decided / 59 undecided | VERIFIED | Publisher v2 `--validate` PASS |
| No registry/schemas/generated/sign-off edits | VERIFIED | Phase-commit file scope |
| CI `archive-assessment` green with 0 skips | VERIFIED | Run 44408700761 at b47a93f: 1133 passed, 0 skipped, 7/7 validators PASS |

## Requirements Coverage

All 9 IDs are claimed by plan frontmatter and accounted for.

| ID | Plan(s) | Status |
|----|---------|--------|
| BASE-01 | 16-01, 16-05 | SATISFIED |
| BASE-02 | 16-02, 16-05 | SATISFIED |
| BASE-03 | 16-01, 16-05 | SATISFIED |
| BASE-04 | 16-01, 16-05 | SATISFIED |
| GATE-13 | 16-01, 16-03, 16-05 | SATISFIED (Phase 16 share; IN-01..04 and the IN-06 digest-check move carried to Phase 17 per traceability) |
| GATE-14 | 16-02, 16-03, 16-05 | SATISFIED |
| GATE-15 | 16-02, 16-03, 16-05 | SATISFIED (IN-02/03 fixed; IN-01 carried to Phase 19 per traceability) |
| BOOK-01 | 16-04, 16-05 | SATISFIED |
| BOOK-02 | 16-03, 16-05 | SATISFIED |

No orphaned requirements for Phase 16.

## Anti-Patterns / Notes (non-blocking, WARNING/INFO)

- REQUIREMENTS.md still shows the 9 Phase 16 checkboxes as `[ ]` and the traceability rows as `Pending` (l.14-17, 68-69, 91-99). Update these at phase close. This is bookkeeping and does not affect goal achievement.
- 16-05 records 2 unexplained local failures from the first run. The output was truncated and they did not reproduce in per-file reruns. CI at HEAD is green, so this is informational.
- The deep-root Windows branch is not exercised on ubuntu CI. Local evidence was a 109-passed run of the 2.0.3 notice test file.
- 16-REVIEW.md reports 0 critical, 3 warning and 4 info (advisory). I did not re-triage them here.
- Bash was unavailable, so I did not re-run git or pytest. I relied on the orchestrator evidence and read the code with Read/Grep.

## Human Verification Required

None.

## Gaps Summary

No gaps. The phase goal is achieved.

_Verified: 2026-11-18_
_Verifier: Claude (gsd-verifier)_
