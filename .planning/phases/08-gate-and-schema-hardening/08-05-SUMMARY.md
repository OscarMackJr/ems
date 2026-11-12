---
phase: 08-gate-and-schema-hardening
plan: 05
subsystem: archive-assessment v2 publisher
tags: [publication-record, GATE-01]
requirements: [GATE-01]
key-files:
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
metrics:
  completed: 2026-11-12
---

# Phase 8 Plan 05: Mandatory publication record Summary

validate_published now requires a publication record (check_publication_record): exact six keys, identity per mode, live-file digests in plain mode, and git_show LF digest equality of authority and manifest at the record commit in both modes. New `--validate --pre-publication` mode requires a record naming SUPERSEDED_V2_0_0.

## Commits
- 823145f: publisher (check_publication_record, pre_publication parameter, --pre-publication flag, skip branch removed)
- 143e6b7: tests (fake_git_show fixture, absent/other-authority/shape/digest/unreachable cases, real temp git repo test, CLI wiring)

## Verification
Orchestrator runs: `.\.venv\Scripts\python.exe -m pytest tests/test_archive_assessment_applicability_authority_v2_publication.py -p no:cacheprovider -q --basetemp=.pytest-temp/p8-05`
Expected red in this file: test_real_published_files_validate only (real 2.0.1 record cannot match until Phase 9). Whole `-k archive_assessment` suite: exactly the 3 accepted red tests. py_compile passed; no pytest run by this agent. Protected paths unchanged.

## Deviations from Plan
None.

## Self-Check: PASSED
