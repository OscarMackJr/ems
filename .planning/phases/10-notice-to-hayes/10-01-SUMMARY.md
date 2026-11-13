---
phase: 10-notice-to-hayes
plan: 01
subsystem: archive-assessment
tags: [notice, builder, tests, hayes]
requires: [AA3 2.0.2 publication ae15c74, record a71257e]
provides: [notice builder with --build/--validate/--emit-schema, notice tests]
affects: [Plan 02 generation and CI]
key-files:
  created:
    - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
    - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
  modified: []
requirements: [NOTICE-01, NOTICE-02]
completed: 2026-11-12
---

# Phase 10 Plan 01: Notice builder and tests Summary

Builder that derives the 2.0.2 notice (Markdown, JSON, closed schema) only from git-frozen bytes at ae15c74, a71257e (record only) and 31addfa, with byte-rebuild `--validate`, plus a test file covering tamper, derivation and fail-closed cases.

## Tasks

1. Builder core: constants, frozen reads (`pinned_raw_digest` for RAW_BYTES AA1/AA2 digests), `resolve_record_commit` (shallow, cat-file, ancestor for all three commits, publication ancestor of record), `load_inputs` with the WR-01 record binding, derivations (lineage, 29 mutations, 16 closed levels, 0 of 80 rows, digest-scope error), `validate_notice_object`.
2. Output: `render_markdown`, `schema()` (additionalProperties false at every object, consts for id, version, publication commit), `validate_notice`, CLI.
3. Tests: tamper, constants, fail-closed (non-skipping), live-independence, derivations, forbidden words, CLI.

No commits were made (Plan 02 gates and commits). Reply builder and v2 publisher are unchanged.

## Verification

- `py_compile` passes for both files.
- A read-only run of `load_inputs`, `build_notice`, `validate_notice_object` and a temp-dir `validate_notice` round trip printed PASS and confirmed 29 mutations, 16 closed levels, 0 of 80 rows differing, decisions sha 4e746d1f, record diff (excluding `.planning/`) is only the publication record.
- pytest was not run (orchestrator runs it with `--basetemp`).

## Deviations from Plan

- NOTICE_DATE set to 2026-11-12 (as instructed) instead of the plan's 2026-11-13 default.
- Tests build their temp JSON/MD/schema from `build_notice` rather than reading generated files, since nothing is generated until Plan 02.

## Self-Check: PASSED
