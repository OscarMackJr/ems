---
phase: 08-gate-and-schema-hardening
plan: 02
subsystem: reply-builder
tags: [GATE-04, D-11, D-12, shallow-clone]
requires: []
provides:
  - shallow-clone guard in resolve_record_commit
affects:
  - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
key-files:
  modified:
    - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
    - tests/test_archive_assessment_demo3_w1_req_001_reply.py
key-decisions:
  - "D-11: resolve_record_commit requires git rev-parse --is-shallow-repository to print exactly 'false'; anything else (true, nonzero rc, odd output, OSError) raises V2.AuthorityError mentioning shallow (fail closed)"
requirements-completed: [GATE-04]
duration: short
completed: 2026-11-12
---

# Phase 8 Plan 02: Shallow-clone guard (GATE-04) Summary

`resolve_record_commit` now calls the module's `git('rev-parse', '--is-shallow-repository')` before the `git log` lookup and raises `V2.AuthorityError` unless stdout is exactly `false`. Full clones behave as before; no reply JSON/MD was regenerated (D-12).

## Commits
- 7099106: guard in the builder
- 9a66899: synthetic tests (shallow true, rc 128, odd stdout, OSError, full-clone pass-through)
- 0f29b8f, b47cbbb: fixes for newline literals in the test fake (my scripted edit had inserted raw newlines; the earlier commits were syntactically broken, the final one is correct)

## Tests
Not run by the executor (orchestrator runs them). Files byte-compile.

## Deviations
- Commits 9a66899/0f29b8f contain a broken test file intermediate state, fixed in b47cbbb.

## Self-Check: PASSED (commits exist; protected paths unchanged)
