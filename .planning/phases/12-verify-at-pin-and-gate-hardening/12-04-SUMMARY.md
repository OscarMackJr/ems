---
phase: 12-verify-at-pin-and-gate-hardening
plan: 04
subsystem: archive-assessment publisher (authority v2)
tags: [GATE-07, GATE-10, red-window, domain-errors, json-schema, dry-run]
requires: [12-03]
provides:
  - load_checked and schema_check helpers in the v2 publisher
  - schema-first validate_published
  - manifest and source_lineage non-object guards
  - conditional dry-run lead clause with a reachable DIFFER branch
affects:
  - scripts/publish_archive_assessment_applicability_authority_v2.py (live bytes no longer match manifest publisher_script.sha256)
tech-stack:
  added: []
  patterns: [wrap jsonschema SchemaError/ValidationError and JSON decode errors as AuthorityError]
key-files:
  created: []
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - tests/test_archive_assessment_lineage_validation.py
    - .planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md
decisions:
  - "[Phase 12] 12-04: validate_published runs schema_check (check_schema + validate, wrapped as AuthorityError) before validate_publication; load() is unchanged, only validate_published and check_publication_record use load_checked"
  - "[Phase 12] 12-04: dry-run lead clause reads 'DECISIONS DIFFER from <version>' unless the decisions digest equals the superseded value and no row or decision set differs"
  - "[Phase 12] 12-04: red window opened by design; accepted red set is exactly test_publisher_still_valid_and_digest_matches_manifest (live publisher LF digest ee810746..., manifest f6b51cca...)"
metrics:
  duration: ~25 min
  completed: 2026-11-16
  tasks: 2
  files: 4
---

# Phase 12 Plan 04: Schema-first domain errors and conditional dry-run text Summary

The v2 publisher's `validate_published` now raises only `AuthorityError` for malformed published files. It checks the committed schema (wrapped `SchemaError`/`ValidationError`) before the Python checks. The dry run can no longer print "No decision changed" when a decision differs. These changes deliver GATE-07 and GATE-10 IN-01, and they open the planned red window with exactly one test.

## What was done

**Task 1 (GATE-07):**
- `load_checked(p)` converts `OSError`/`ValueError` into `AuthorityError('<name>: cannot be read as JSON: ...')`. It is used for the authority, schema, sign-off and manifest in `validate_published`, and for the record in `check_publication_record`.
- `schema_check(doc, schema_doc, what)` runs `Draft202012Validator.check_schema` and then `validate`. Errors come back as `'<what>: committed schema is invalid: ...'` or `'<what> fails the schema: ...'`.
- In `validate_published`, `schema_check(a, load_checked(SCHEMA), 'published authority')` (line 728) now runs before `validate_publication(a)` (line 729).
- New guards: `publication manifest must be an object` and `source_lineage must be an object` (as the first line of `validate_lineage`).
- `load`, `mutation_gates`, `published_authority_checked`, `publish`, `NEGATIVE_MUTATIONS`, `schema()`, VERSION and the SUPERSEDED_* constants are unchanged.

**Task 2 (GATE-10 IN-01):**
- `dry_run_summary` now computes `rows_differing_from_previous` before the supersedes sentence. The lead clause keeps the old text exactly when nothing changed. Otherwise it reads `DECISIONS DIFFER from 2.0.1: ...`.

**Tests:**
- `MALFORMED_FILES` drives the 8-case `test_malformed_published_files_raise_domain_error`. It covers invalid JSON in the authority, sign-off, manifest, record and schema; a manifest that is a list; a schema of `{"type": 7}`; and an authority with `evidence_boundary` removed.
- `test_dry_run_summary_differ_branch_is_reachable` covers the new dry-run branch.
- `test_validate_lineage_rejects_non_object` covers `[]` and `'x'`.

No existing test match string needed to change: no existing `validate_published` test hit the schema-first reordering with a different message.

## Verification (measured)

- Task 1 check (`v2_publication` and `lineage_validation` modules, basetemp `p12-04-t1`): 314 passed, 1 failed (`test_publisher_still_valid_and_digest_matches_manifest`), exit 1.
- `-k dry_run` (basetemp `p12-04-t2`): 3 passed, exit 0.
- Full archive suite: `EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-04-full`
  - Result: **945 passed, 1 failed** (347.07s), pytest exit 1.
  - The only failure is `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`, the accepted window opener.
- CI validators 1-6 all PASS (exit 0 each), run after the full suite and before the commit.
- Mutation invariance check prints `True`: the 29 `rejected_by` outcomes are unchanged.
- Acceptance greps all print 1:
  - in the publisher: `def load_checked`, `def schema_check`, `publication manifest must be an object`, `source_lineage must be an object` and `DECISIONS DIFFER from`;
  - in the tests: each of the two new test defs.
- `git show --stat HEAD` (68231fc) lists exactly the publisher and the two test files.

## Deviations from Plan

None. The plan was executed as written.

Implementation notes:
- The publisher is stored with CRLF in the working tree. The edit was applied on LF text and written back as CRLF, so the diff contains only the intended lines.
- The lead text is built as `{lead}` inside the sentence, so the literal `DECISIONS DIFFER from` appears once in the source, which is what the acceptance grep expects.

## TDD Gate Compliance

The plan bundles the tests and the implementation into one `fix(12-04)` commit (Task 2 commits). So there is no separate `test(...)` RED commit. The research probe table (12-RESEARCH "GATE-07") documents the pre-change behaviour as RED for each case: `JSONDecodeError`, `AttributeError`, `TypeError` and `ValidationError`.

## Known Stubs

None.

## Commits

- 68231fc: fix(12-04): schema-first domain-error validation and conditional dry-run text (GATE-07, GATE-10 IN-01)

## Self-Check: PASSED

- FOUND: scripts/publish_archive_assessment_applicability_authority_v2.py (modified, in 68231fc)
- FOUND: commit 68231fc
- FOUND: "## After plan 12-04" in 12-BASELINE-RED.md
