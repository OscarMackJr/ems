---
phase: 07-lineage-source-and-per-digest-scope
plan: 02
subsystem: archive-assessment-applicability-authority
tags: [lineage, normalisation, git_show, validate_lineage]
requires: [07-01]
provides: [per-digest lineage objects, validate_lineage hooked into validate_published]
affects: [scripts/publish_archive_assessment_applicability_authority_v2.py]
key-files:
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
decisions:
  - supersedes keeps flat keys with sibling normalisation/relative_path keys (D-14)
  - subprocess confined to git_show (D-10)
requirements: [LIN-01, LIN-02]
metrics:
  tasks: 2
  files: 3
  completed: 2026-10-20
---

# Phase 7 Plan 02: Per-digest lineage and validate_lineage Summary

Every AA3 v2 lineage digest is now an object with relative_path, sha256 and normalisation; `validate_lineage` recomputes each from `git show <commit>:<path>` or the checked-out file and runs only from `validate_published`.

## Commits

- caea558 feat(07-02): publisher reshape, schema(), git_show, validate_lineage
- test commit (see git log, "test(07-02)"): both existing test files updated

## What changed

- Publisher: added `subprocess` import, `NORMALISATIONS`, `NORMALISERS`, `*_REL` constants, `EXPECTED_NORMALISATION`, `digest_entry`, `git_show`, `validate_lineage`. `digest_normalisation` removed. aa1/aa2 digests are RAW_BYTES objects; catalog, governance_decisions, supersedes (both digests) and v1_baseline are CRLF_TO_LF. `schema()` pins per-digest normalisation (enum plus const). `validate_publication` gained pure shape checks (no IO).
- Tests: shape tests updated, new rejection tests for `digest_normalisation` and normalisation values, subprocess bans narrowed to `git_show`, `env` fixture stubs `validate_lineage` with a recorder, new `test_validate_published_calls_validate_lineage`.

## Verify commands (all pending orchestrator run, PowerShell, from C:\temp\standars\ems)

1. `.\.venv\Scripts\python.exe -I -m py_compile scripts\publish_archive_assessment_applicability_authority_v2.py` - pending orchestrator run
2. `.\.venv\Scripts\python.exe -m pytest tests\test_archive_assessment_applicability_authority_v2.py tests\test_archive_assessment_applicability_authority_v2_publication.py -p no:cacheprovider -q --basetemp <scratch>\bt` - pending orchestrator run; expected failures only: test_committed_schema_equals_schema_function, test_real_published_files_validate
3. `.\.venv\Scripts\python.exe -m pytest tests -k archive_assessment -p no:cacheprovider -q --basetemp <scratch>\bt2` - pending orchestrator run; expected exactly 3 failed (the two above plus tests/test_archive_assessment_demo3_w1_req_001_reply.py::test_publisher_still_valid_and_digest_matches_manifest)
4. `.\.venv\Scripts\python.exe scripts\publish_archive_assessment_applicability_authority_v2.py --publish --dry-run` - pending; must write nothing (note: it runs validate_publication on the fresh build only, so should print the summary)
5. `.\.venv\Scripts\python.exe scripts\publish_archive_assessment_applicability_authority_v2.py --validate` - expected red (committed authority is old shape) until Phase 9

Expected red set: the 3 pytest tests above plus CLI `--validate`.

## Deviations from Plan

None in logic. Notes: python and pytest were not run (forbidden for this executor); `validate_lineage` falls back to the working file when no commit is present, and `validate_publication` pins commits on supersedes and v1_baseline by equality.

## Known Stubs

None.

## Self-Check

Files exist and commits recorded by git; test results pending orchestrator run.
