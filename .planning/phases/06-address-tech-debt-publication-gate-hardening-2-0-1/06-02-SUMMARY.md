---
phase: 06-address-tech-debt-publication-gate-hardening-2-0-1
plan: 02
subsystem: archive-assessment-rule-proposals-validator
tags: [validation, frozen-artifacts, drafting-record, WR-01]
requires: []
provides:
  - frozen_catalog, frozen_catalog_source, frozen_frame, FROZEN_FRAME_SHA256, catalog_blob_id
affects: [scripts/validate_archive_assessment_rule_proposals.py]
key-files:
  modified:
    - scripts/validate_archive_assessment_rule_proposals.py
    - tests/test_archive_assessment_rule_proposals.py
    - tests/test_archive_assessment_rule_proposals_record.py
decisions:
  - "Frozen validation binds to the drafting record digests plus a pinned frame digest; git is read only when the live catalog has drifted"
  - "When the frozen catalog is unavailable, only the catalog_inputs equality check is skipped (stderr NOTICE naming dc3b41c); shape_limitation scope is then checked against the proposal's own catalog_inputs"
metrics:
  tasks: 2
  files: 3
  tests: "404 passed (397 + 7 new)"
completed: 2026-10-14
---

# Phase 6 Plan 02: Frozen catalog and frame validation Summary

Validation of the frozen Phase 2 proposals and drafting record now binds to the catalog and frame as at dc3b41c, so a later edit to the live catalog cannot turn `--validate` red (Phase 2 WR-01, D-03).

## What changed

- `catalog_blob_id` computes the git blob id with `hashlib.sha1` over LF-normalised bytes; the `git hash-object` call is gone and the default path runs no git subprocess.
- `frozen_catalog_source()` and `expected_header()` take the catalog source from the drafting record; the frame comes from `frozen_frame()`, which checks the proposals LF digest against the record and the frame against `FROZEN_FRAME_SHA256` (`2bb11806...7dab`, computed from the frozen file, not typed).
- `frozen_catalog()` uses the live parse when its LF sha256 equals the recorded one; otherwise it reads `dc3b41c:registry/control_catalog.yaml` through `git()` and requires the sha256 to match (mismatch raises AuthorityError). If git or the commit is unavailable it prints one `NOTICE:` line and `catalog_inputs` equality alone is skipped.
- `catalog_fingerprint` deleted. `build_authority`, `validate_publication`, and all registry and schema files untouched.
- Existing live-catalog tests renamed to `test_catalog_drift_info_*` and documented as drift information.

## TDD record

RED run before implementation: 5 failed (`without_git_and_says_so`, `default_path_runs_no_git`, `catalog_blob_id_matches_record`, `frozen_frame_is_pinned_to_constant`, `frozen_frame_constant_matches_drafting_commit`; AttributeError on the missing `catalog_blob_id`/`FROZEN_FRAME_SHA256` and no NOTICE). GREEN: 404 passed.

## Deviations from Plan

- Test A (drift read via git) and Test E (frame mismatch rejected) already passed before the change, because the old code read the live catalog via an unpatched path and already compared the frame to live semantics. They remain as regression guards; the plan expected them to fail first. They are covered by the other failing tests for the new mechanism.
- Shallow-clone fallback: shape_limitation scope uses the proposal's own catalog_inputs scope (Rule 2, so that check is not silently dropped).

## Verification

`--validate` and `--validate-record` print PASS; no `hash-object` remains; the full `tests/test_archive_assessment_*.py` suite passes (404, none skipped). Commit 1da27db contains exactly the three files; the unrelated modified files remain uncommitted.

## Self-Check: PASSED
