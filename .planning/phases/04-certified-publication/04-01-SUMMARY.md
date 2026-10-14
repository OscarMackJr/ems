---
phase: 04-certified-publication
plan: 01
subsystem: archive-assessment-governance-decisions
tags: [lf-normalisation, digests, review-debt]
requires: []
provides:
  - "V2.lf_bytes, V2.lf_digest, V2.dump (newline LF) shared helpers"
  - "frozen_input_sha256_normalisation header field in decisions file and schema"
  - "--validate rebuild-compare and answers_sha256 binding"
affects: [04-02, 04-03, 04-04]
key-files:
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - scripts/build_archive_assessment_governance_decisions.py
    - schemas/archive_assessment_governance_decisions.schema.json
    - registry/archive_assessment_governance_decisions.json
    - tests/test_archive_assessment_governance_decisions.py
decisions:
  - "Builder --build may rewrite the decisions file only when records are equal and the sole header difference is in HEADER_REFRESH_KEYS"
metrics:
  commit: 753bcfd
  completed: 2026-10-14
---

# Phase 4 Plan 01: LF-normalised decisions builder Summary

Phase 3 review debt CR-01, CR-02, WR-05 and WR-08 is fixed: all digests in the decisions builder are LF-normalised through one shared helper, answers_sha256 is bound to the live answers file, and --validate rejects any file that differs from a rebuild.

## Accomplishments
- `lf_bytes`, `lf_digest` and an LF-only `dump` live once in the v2 publisher module; the builder's `answers_digest` delegates to them.
- Header gained `frozen_input_sha256_normalisation: CRLF_TO_LF` (builder, validator, schema, decisions file).
- `validate_decisions` requires answers_sha256 to equal the live answers LF digest and the full `wording_approval` object to equal the approval file.
- `--validate` also rebuild-compares the decisions file.
- Decisions file diff is a single added header line; all 21 records equal commit eed4a5f (tested). Answers file untouched.

## Deviations from Plan
- The plan listed tests/test_archive_assessment_governance_answers.py as modified; no change was needed there, so it is not in the commit (five files committed, not six).
- Existing tests were adjusted (built() now uses the live answers digest, lf_digest for frozen digests) because the new binding rejects the synthetic digest.
- New tests use a module-level TemporaryDirectory instead of pytest tmp_path (tmp_path errored in this Windows environment).
- Tests were written alongside the implementation rather than strictly red-first.

## Verification
`python -m pytest tests -k archive_assessment -q` gives 285 passed; builder `--validate` prints PASS.

## Self-Check: PASSED
Commit 753bcfd contains exactly the five files above; registry/adjudication_rules.json and registry/policy_decisions.json remain unstaged.
