---
phase: 08-gate-and-schema-hardening
plan: 04
subsystem: archive-assessment v2 publisher
tags: [catalog-pin, GATE-03]
requirements: [GATE-03]
key-files:
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - tests/test_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_lineage_validation.py
metrics:
  completed: 2026-11-12
---

# Phase 8 Plan 04: Pinned catalog reads Summary

All v2 catalog reads now go through git_show(CATALOG_COMMIT, CATALOG_REL) via catalog_bytes(); catalog_reference carries the pinned commit and is commit-pinned in lineage validation and the schema.

## Commits
- 4a257eb: publisher (CATALOG_COMMIT, catalog_bytes, pinned catalog_reference, COMMIT_PINNED, schema commit const, validate_publication commit/path/digest checks; live CATALOG constant removed)
- dbfda6e: tests commit (fixtures, D-10 both directions, D-09 fail-closed)

## Verification
Probe: build_published_authority() gives catalog_reference commit == CATALOG_COMMIT, 80 controls, digest 12bb1a9d2476e4b0208ff51f9296f51462395f01af8d0543ad3c7eae9f039477.
`.\.venv\Scripts\python.exe -m pytest tests/test_archive_assessment_applicability_authority_v2_publication.py tests/test_archive_assessment_applicability_authority_v2.py tests/test_archive_assessment_lineage_validation.py tests/test_archive_assessment_rule_proposals_record.py -p no:cacheprovider -q --basetemp=.pytest-temp/p8-04`
Expected red set: test_committed_schema_equals_schema_function and test_real_published_files_validate only (committed schema/authority not regenerated).

## Deviations from Plan
None. No pytest run by this agent (orchestrator verifies); py_compile and inline probe passed. Protected paths unchanged.

## Self-Check: PASSED
