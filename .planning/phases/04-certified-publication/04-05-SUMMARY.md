---
phase: 04-certified-publication
plan: 05
subsystem: archive-assessment-applicability-authority
tags: [publication, signoff, validation, determinism]
requires: [04-04]
provides:
  - build_all_outputs, publish (dry-run and sign-off gated), validate_published, write_publication_record, validate_signoff in the v2 publisher
affects: [04-06]
key-files:
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - tests/test_archive_assessment_applicability_authority_v2.py
key-decisions:
  - "Authority is serialised once by jtext(); its LF digest is computed from that text so sign-off, certification and manifest agree"
  - "validate_published rebuilds authority and all outputs from tracked inputs and requires byte equality; a consistent hand edit plus re-hash fails"
requirements-completed: [PUB-03, PUB-04, PUB-06]
duration: ~25 min
completed: 2026-10-14
---

# Phase 4 Plan 05: Publication machinery for the v2 publisher Summary

The v2 publisher now has `--publish --dry-run` (prints the sign-off summary: 21 decided, 59 undecided, the three rules in full, authority LF digest), a sign-off-gated `--publish`, a rebuild-and-compare `--validate`, `--validate-signoff`, and `--record-publication SHA`. Nothing was published; no v2 registry file, sign-off, record or generated output exists.

## Accomplishments
- `PUBLISHED_ON = '2026-10-14'` stamps all outputs; no datetime or git calls; all writes LF; `digest_normalisation: CRLF_TO_LF` in certification and manifest.
- Outputs under `generated/archive-assessment/ems-aa3-v2/`: matrix, semantic validation (UNKNOWN checked for 030/039/052), negative invariants, AA4 decision traceability (21 records plus 59 undecided), certification, report .md, manifest.
- `validate_signoff` fails closed on missing keys, wrong status, approver, role, dual-role statement, digest or normalisation.
- 52 new/updated tests pass (mutation, determinism, hand-edit-plus-rehash, file-set, record writer); real-file and publication-commit tests skip until files exist.

## Task Commits
1. Tasks 1-3 (code, tests, commit): 6a580bb

## Verification
`python -m pytest tests -k archive_assessment -q`: 363 passed, 2 skipped. Dry run prints the summary and writes nothing; `--validate` exits non-zero with "not published".

## Deviations from Plan
**1. [Rule 3 - Blocking] Existing test forbade the word "generated" in the v2 source**
- **Issue:** `test_v2_builder_does_not_use_generated_dir` in `tests/test_archive_assessment_applicability_authority_v2.py` asserted `'generated' not in src`, which conflicts with the mandated `OUT` path.
- **Fix:** narrowed to the intent (no `ems-aa2`, no v1 `'ems-aa3'` folder, no `AA2 / ` read).
- **Commit:** 6a580bb (this file is a third file in the commit; the plan listed two).

## Known Stubs
None.

## Self-Check: PASSED
