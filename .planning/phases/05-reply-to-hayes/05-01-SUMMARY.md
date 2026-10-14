---
phase: 05-reply-to-hayes
plan: 01
subsystem: archive-assessment-publication
tags: [reply, generator, schema, hayes]
requires:
  - phase: 04-certified-publication
    provides: published v2 authority, publication record, sign-off, decision records
provides:
  - reply generator script (--build, --validate, --emit-schema, --push-check)
  - JSON schema for the reply file
affects: [05-02, 05-03]
tech-stack:
  added: []
  patterns: [import publisher V2 by importlib, rebuild-and-byte-compare validate]
key-files:
  created:
    - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
    - schemas/archive_assessment_demo3_w1_req_001_reply.schema.json
  modified: []
key-decisions:
  - "Code files left uncommitted on purpose; plan 05-03 commits script, schema, test and .gitattributes together (D-18)"
  - "Dual-role text read from the sign-off; V2.DUAL_ROLE_STATEMENT used only as a cross-check"
requirements-completed: [REPLY-01, REPLY-02, REPLY-03]
duration: 20min
completed: 2026-10-14
---

# Phase 5 Plan 01: Reply generator and schema Summary

A generator script builds the Hayes reply (JSON and Markdown) from the published v2 authority, publication record, sign-off, decision records and manifest, with a 21-control schema; no authority values are typed.

## Tasks

1. Reply builder and Markdown renderer: `build_reply` (pure, cross-checks each of 21 rows to the latest decision records, fails closed), `render_markdown` (LF only, sections for opening with dual role, decisions, rule meaning, pin, published shape with one decided row, the other 59 controls, what publication does not change, disclosure naming WR-01, send condition).
2. `schema()`, `validate_reply_object()`, `validate_reply()` (byte-equality after LF normalisation, schema, no absolute paths, record digests), read-only `push_check()`, CLI. Schema emitted with `--emit-schema`.

Only typed commit value: `0ce89f2` (publication record commit), to be checked against git by the test in plan 05-02. The publication SHA is read from the record.

## Commits

None for the code files, by instruction: script and schema are written and left uncommitted for plan 05-03 (D-18). This SUMMARY and tracking files are committed.

## Verification

- Task 1 and Task 2 automated commands print OK.
- `--push-check` exits 0 and prints the push command; the remote branch tip could not be read (reported as UNKNOWN, not guessed), so the pin is not confirmed on the remote.
- Publisher `--validate` prints PASS; publisher and v2 schema unmodified; schema has no CR; publication SHA literal appears 0 times in the script.
- Neutral-word check: the only match for the banned words in the rendered text is the field name `service_criticality` inside the example row.

## Deviations from Plan

None - plan executed as written. Generated reply files were not built (later plans).

## Known Stubs

None.

## Self-Check: PASSED
