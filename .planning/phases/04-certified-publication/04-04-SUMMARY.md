---
phase: 04-certified-publication
plan: 04
subsystem: archive-assessment-applicability-authority
tags: [publication, validation, schema, governance]
requires: [04-01, 04-02, 04-03]
provides:
  - build_published_authority and validate_publication in the v2 publisher
  - applicability_decision_ids top-level list and governance_decisions lineage in the v2 schema
affects: [04-05, 04-06]
key-files:
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - schemas/archive_assessment_applicability_authority_v2.schema.json
  created:
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
key-decisions:
  - "The 21/59 pin lives in validate_publication so validate_authority and its existing tests are unchanged"
  - "Base build_authority emits an empty applicability_decision_ids list; the overlay fills it"
requirements-completed: [PUB-01, PUB-02, PUB-04, PUB-05]
duration: ~20 min
completed: 2026-10-14
---

# Phase 4 Plan 04: Build and validate the published v2 authority Summary

The v2 publisher can now build, in memory, the 80-row authority with the 21 Phase 3 decisions overlaid (3 RULE_PUBLISHED, 18 NO_RULE_WILL_BE_PUBLISHED, 59 NOT_YET_DECIDED) and validate it with `validate_publication`. Nothing was published to disk.

## Accomplishments
- `build_published_authority()` overlays the latest unsuperseded decision record per control (state, rule, authority = AA4 id); rows stay lean and `decision_ids` stays the eight AA1 ids.
- `applicability_decision_ids` (21 sorted ids) added to the document and schema; `source_lineage.governance_decisions` carries relative_path, LF sha256, record_count, drafting_commit (read from the decisions file, no git calls).
- Lineage catalog and v1 digests are now LF digests, with `digest_normalisation: CRLF_TO_LF`.
- `validate_publication` enforces: decided set equals the 21 request ids; id list matches cited authorities once each; live decisions-file digest/count/commit; latest-unsuperseded record with matching state and rule; field-by-field v1.0.0 equality apart from the decision fields; v1.0.0 at 62a8955 lineage.
- Schema regenerated via `--emit-schema` (idempotent).

## Task Commits
1. Task 1 and 2 (code, tests, schema, one commit as planned): 38b3210

## Verification
`python -m pytest tests -k archive_assessment -q`: 336 passed. Commit lists exactly the three planned files.

## Deviations from Plan
None - plan executed exactly as written.

## Known Stubs
None.

## Self-Check: PASSED
