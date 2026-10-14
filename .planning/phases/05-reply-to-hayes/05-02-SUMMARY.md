---
phase: 05-reply-to-hayes
plan: 02
subsystem: archive-assessment-publication
tags: [reply, pytest, gitattributes, hayes]
requires:
  - phase: 05-reply-to-hayes
    provides: reply generator script and schema (plan 05-01)
provides:
  - pytest locking the reply to the v2 authority, decision records and git history
  - LF rules for the three reply files
affects: [05-03]
tech-stack:
  added: []
  patterns: [importlib module load, tempfile fixtures instead of tmp_path, git-gated tests with shallow-clone skip]
key-files:
  created:
    - tests/test_archive_assessment_demo3_w1_req_001_reply.py
  modified:
    - .gitattributes
key-decisions:
  - "Test and .gitattributes left uncommitted on purpose; plan 05-03 commits script, schema, test and .gitattributes together (D-18)"
  - "Drift that stays schema-valid (swapped AA4 id, altered digest, flipped rule state) is detected by comparison to a fresh build_reply, matching how validate_reply() byte-compares"
requirements-completed: [REPLY-01, REPLY-02, REPLY-03]
duration: 15min
completed: 2026-10-14
---

# Phase 5 Plan 02: Reply tests and LF rules Summary

A 17-test pytest file locks every reply entry to the published v2 authority and decision records and pins the publication SHA to git history; three explicit `text eol=lf` lines cover the reply files.

## Tasks

1. Test file `tests/test_archive_assessment_demo3_w1_req_001_reply.py`: counts (21, 3 and 18, 59 undecided), per-entry equality with the authority row and latest decision record, the three rules, first-sentence checks for all 21 records, mutation tests (swapped and malformed AA4 id, flipped state both ways, altered rule, removed and extra control, bad SHA format, wrong digests, altered dual-role text, absolute path), Markdown content and neutral-word checks, real-file tests (skipped until the reply is generated), publisher `validate_published()` plus script digest versus manifest, and git-gated ancestor, digest-at-SHA and record-commit tests.
2. `.gitattributes`: three explicit lines for the reply Markdown, JSON and schema; `git check-attr eol` prints `lf` for all three; diff is 3 inserted lines.

## Commits

None for the test and `.gitattributes`, by instruction (D-18): left written for plan 05-03. This SUMMARY and tracking files are committed.

## Verification

pytest with `--basetemp=C:/temp/pytest-reply-tmp`: 16 passed, 1 skipped (real-file test, reply not built yet). No `tmp_path` use. Test count exceeds 10.

## Deviations from Plan

None - plan executed as written. Git printed a warning that `.gitattributes` LF may be converted to CRLF on the next git touch; the file's existing endings were LF and were preserved.

## Known Stubs

None.

## Self-Check: PASSED
