---
phase: 14-notice-to-hayes-2-0-3
plan: 03
subsystem: testing
tags: [pytest, notice, tamper-tests, fail-closed, git-history]
requires:
  - phase: 14-02
    provides: builder with closed schema(), validate_notice_object, validate_notice, CLI
provides:
  - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py (written, uncommitted; Plan 04 commits it after the orchestrator pytest run)
affects: [14-04]
key-files:
  created:
    - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
metrics:
  tasks: 2
  files: 1
  completed: 2026-11-17
---

# Phase 14 Plan 03: Notice 2.0.3 test file Summary

Test file for the 2.0.3 notice: per-claim tests with specific `match=`, 16 schema-const and 15 derivation tamper cases, non-skipping fail-closed history tests, content and verify tests, a CLI test and a live-file clone test. 42 test functions; with parametrisation this is well over 100 cases. pytest was not run (the orchestrator runs it in Plan 04).

## Accomplishments

- Claim tests call `check_rerun`, `pinned_mutation_run`, `lineage_entries` and `digest_scope_error` directly with named match strings (not rejected / not PASS / rerun differs / noop accepted / baseline rejected / recomputed sha256 / raw equals LF / publisher digest).
- Lineage wrong-digest test is parametrised over the 7 keys; raw==LF over the 3 RAW_BYTES keys.
- Tamper tests: 16 const paths (schema `const` plus "notice JSON differs from a fresh build") and 15 derivation paths (schema still passes, "notice differs from the values derived from the frozen inputs"). A cross-check test asserts every const path has `const` in `schema()` and no derivation path has `const` or `enum`.
- Fail-closed: `test_validate_fails_closed_without_history_git_show` and the shallow variant use TMP dummy notice files and never reach `require_history`; the fake-git resolve tests call `resolve_record_commit()` directly. No `pytest.skip`.
- Clone test overwrites the clone's live publisher and decisions builder with `raise SystemExit('mutated live file executed')` and asserts `--validate` stays `(0, 'PASS')` and `--build` stays byte-identical.
- `inputs()` caches the real `load_inputs()` (one 29-mutation rerun per module); `cached_pinned_run` primes the cache before patching `pinned_mutation_run`.

## Acceptance checks

| Check | Result |
| --- | --- |
| py_compile | exit 0 |
| grep -c pytest.skip | 0 |
| grep -c publisher_refs | 0 |
| grep -c "mutated live file executed" | 1 |
| grep -c "jsonschema==4.26.0" / "OscarMackJr/ems.git" | 1 / 1 |
| def test_committed_notice_files_validate | 1 |
| def test_validate_rejects_tampered_cited_commit_by_derivation | 1 |
| "derived from the frozen inputs" | 2 |
| "publication commit is not an ancestor of the record commit" | 2 |
| const / derivation parametrisation sizes | 16 / 15 |
| const/derivation vs builder `schema()` cross-check | passed (run directly, not via pytest) |

I also confirmed from the builder that the raw and LF digest prefixes (f0da8e2e / de170ebc / ed589d76 and 06e39f7b / 248b6e38 / 66662df3, in key order) and the lineage `recomputed_at` commits match what the tests assert.

## Deviations from Plan

None. The builder was not modified. The test file is intentionally uncommitted (Plan 04 commits it).

## Known Stubs

None.

## Self-Check: PASSED
