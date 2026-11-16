---
phase: 11-frozen-validators
plan: 06
subsystem: archive-assessment frozen validators (evidence record)
tags: [gap-closure, review, WR-03, documentation]
requires: [11-04]
provides: [accurate FROZEN-03 evidence record for the reply validator's resolve_record_commit path]
affects: [.planning/phases/11-frozen-validators/11-04-SUMMARY.md, tests/test_archive_assessment_demo3_w1_req_001_reply.py]
tech-stack:
  added: []
  patterns: []
key-files:
  created: []
  modified:
    - .planning/phases/11-frozen-validators/11-04-SUMMARY.md
    - tests/test_archive_assessment_demo3_w1_req_001_reply.py
decisions:
  - "11-06: WR-03 closed as a wording fix only; the reply builder ordering (guard after pinned reads) stays as-is, deferred with the frozen-builder edits"
metrics:
  duration: 5min
  completed: 2026-11-15
  tasks: 1
  files: 2
requirements: [FROZEN-03]
---

# Phase 11 Plan 06: Correct WR-03 resolve_record_commit statements Summary

The 11-04 evidence record and one reply test comment now say that `resolve_record_commit` is called via build_reply, after the pinned reads in load_inputs, instead of claiming that `validate_reply` never calls it.

## What changed

- `11-04-SUMMARY.md`: two statements rewritten (the "Reply tampered constants" deviation bullet and the findings bullet). With an unknown commit, `validate_reply` fails at the first pinned `git show` (`GitHistoryError`, still with the fetch hint) before reaching the history check. The rest of each bullet stays, including that the builder was not changed (FROZEN-04 is test-only) and that the notice's `load_inputs()` calls the guard first.
- `tests/test_archive_assessment_demo3_w1_req_001_reply.py`: the comment above the `d*40` parameter now reads "resolve_record_commit is called via build_reply, after the pinned reads in load_inputs, so the first pinned read fails". Only the comment changed; no code lines.

I checked the call path in `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` before editing: `validate_reply` (line 318) calls `load_inputs` (line 322), then `build_reply`, which calls `resolve_record_commit()` at line 177.

## Verification

- `.venv/Scripts/python.exe -m pytest tests/test_archive_assessment_demo3_w1_req_001_reply.py --basetemp=.pytest-temp/reply-wr03 -p no:cacheprovider -q`: exit 0, 109 passed.
- `grep -c "does not call resolve_record_commit\|never calls resolve_record_commit"`: 0 in both files.
- `grep -c "via build_reply"`: 2 in the 11-04 summary, 1 in the reply test.
- The test file diff changes one comment line only.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | 67d115d | docs(11-06): correct resolve_record_commit statements (WR-03) |

## Deviations from Plan

None. I wrote the summary phrase "via build_reply, after the pinned reads in load_inputs" without backticks so that the literal grep gate matches.

## Self-Check: PASSED

- FOUND: .planning/phases/11-frozen-validators/11-04-SUMMARY.md (corrected)
- FOUND: tests/test_archive_assessment_demo3_w1_req_001_reply.py (comment corrected)
- FOUND: commit 67d115d
