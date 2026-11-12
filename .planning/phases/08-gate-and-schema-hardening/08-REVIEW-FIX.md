---
phase: 08-gate-and-schema-hardening
fixed_at: 2026-11-12T00:00:00Z
review_path: .planning/phases/08-gate-and-schema-hardening/08-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 7
skipped: 1
status: partial
---

# Phase 8: Code Review Fix Report

**Fixed at:** 2026-11-12
**Source review:** .planning/phases/08-gate-and-schema-hardening/08-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 8 (1 critical, 7 warnings; Info findings are out of scope)
- Fixed: 7
- Skipped: 1 (WR-01, deferred to Phase 9 by design)

No committed `registry/`, `schemas/` or `generated/` file was regenerated or edited. `VERSION` is unchanged. Neither `--publish` nor `--record-publication` was run. Every edited `.py` file passed `python -m py_compile` and kept its line endings (CRLF where the file used CRLF). pytest was not run; the orchestrator runs it.

## Fixed Issues

### CR-01: Publication record `digest_normalisation` value is never validated

**Files modified:** `scripts/publish_archive_assessment_applicability_authority_v2.py`, `tests/test_archive_assessment_applicability_authority_v2_publication.py`
**Commit:** 92944c2
**Applied fix:**
- `check_publication_record` now raises `AuthorityError('publication record digest_normalisation must be CRLF_TO_LF')` after the key-set check. The check runs in both plain and `--pre-publication` modes.
- New test `test_record_digest_normalisation_must_be_crlf_to_lf` covers `RAW_BYTES`, `7`, `None` and `crlf_to_lf` in both modes.
- The committed 2.0.1 record already carries `CRLF_TO_LF`, so the real record is not affected.

### WR-02: Narrowed mutation gate still counts environment failures as domain rejections

**Files modified:** `scripts/publish_archive_assessment_applicability_authority_v2.py`, `tests/test_archive_assessment_applicability_authority_v2_publication.py`
**Commit:** f9d8461
**Applied fix:**
- Added `class GitHistoryError(AuthorityError)`. `git_show` raises it when git is unavailable (OSError) and when `git show` exits non-zero. Malformed commit or path input still raises plain `AuthorityError`.
- `mutation_gates` re-raises `GitHistoryError` before its `except AuthorityError` in the AUTHORITY and SIGNOFF branches.
- The DECISIONS branch now catches only the builder's `AuthorityError`, not any `ValueError`, and re-raises the builder's `V2.GitHistoryError`.
- Because `GitHistoryError` subclasses `AuthorityError`, existing tests that expect `AuthorityError` on a git failure still hold. So does the error-list handling inside `validate_lineage`.
- New tests:
  - subclass relationship;
  - `GitHistoryError` propagates from the AUTHORITY gate;
  - real `git_show` of a missing object raises `GitHistoryError`;
  - a plain `ValueError` propagates from the DECISIONS gate.
- I did not add the per-run catalog cache the review also suggested. It would interfere with tests that monkeypatch `ROOT` and `CATALOG_COMMIT`, and the subclass re-raise already stops git failures being counted as rejections.

### WR-03: Validators crash with non-domain exceptions on malformed authority shapes

**Files modified:** `scripts/publish_archive_assessment_applicability_authority_v2.py`, `tests/test_archive_assessment_applicability_authority_v2_publication.py`
**Commit:** af37b01
**Applied fix:**
- `validate_authority` now rejects a non-object authority up front.
- It also guards these before calling `.get` or building sets: `classification_vocabulary`, `evidence_boundary` (and the type of its list), `attestation_prohibitions`, `dependencies` and each item in it, `controls`, each control row, and the `control_id` type.
- `validate_publication` checks that `applicability_decision_ids` holds only strings before hashing them.
- New tests:
  - parametrised `test_malformed_authority_shapes_raise_domain_error`, with 9 shapes including "classification_vocabulary is a list" and "a control row is a string";
  - `test_non_object_authority_raises_domain_error`.
- `validate_published` still runs the Python check before the schema check. Swapping the order would change the exception type that existing tests expect. With the guards in place, the Python step now fails with `AuthorityError` instead of `AttributeError` or `TypeError`.
- I confirmed that the 29 mutation outcomes are unchanged.

### WR-04: SCHEMA-07 "closed" schema accepts open nested objects and omits fields Python requires

**Files modified:** `scripts/publish_archive_assessment_applicability_authority_v2.py`, `tests/test_archive_assessment_applicability_authority_v2.py`
**Commit:** 082eb5a
**Applied fix:** `schema()` gains only constraints that the Python validator already enforces:
- `attestation_prohibitions` is now required, and its three flags are pinned to `false`.
- `classification_vocabulary`:
  - `states` is pinned with `const`.
  - `unknown_is_not_false` and `unknown_is_not_not_applicable` are required and must be truthy. The schema uses `not enum [false, null, 0, "", [], {}]` to mirror the Python truthiness check.
- `evidence_boundary.archive_content_does_not_establish` is required and must contain the six live-state entries.
- `not_applicable_semantics.statements` and `fields_not_usable_in_rules_statement` are pinned with `const` to `semantics()`. Python already pins the whole semantics block.
- `control_name` and `catalog_scope` are now required on control rows. `validate_publication` already requires them through the v1 row equality.

I shared `ATTESTATION_KEYS` and `LIVE_BOUNDARY` between the validator and the schema.

Constraints I chose not to add, because Python does not enforce them:
- no `additionalProperties:false` on these nested objects;
- no `const` on `applicability_vocabulary`;
- no `const` on `classification_vocabulary.fields`.

Checks:
- The built authority, both published and unpublished, still validates against the new schema.
- The negative-invariant outcomes are byte-identical to the previous `schema()`.
- The committed schema file is not regenerated. `test_committed_schema_equals_schema_function` was already in the accepted red set and resolves at the Phase 9 republication.

New tests: 8 cases where both the schema and the validator reject (`historical_compliance_attestation: true`, missing `attestation_prohibitions`, and others), plus schema-required checks for `control_name` and `catalog_scope`.

### WR-05: GATE-05 cross-note uniqueness is not enforced on any `--validate` path

**Files modified:** `scripts/build_archive_assessment_governance_decisions.py`, `tests/test_archive_assessment_governance_decisions.py`
**Commit:** a9ff5d1
**Applied fix:**
- `validate_decisions` now runs the uniqueness check over the notes of unsuperseded records.
- The comparison key is `norm` when `answers_sha256 == CERTIFIED_ANSWERS_SHA256` (the D-13 grandfathering) and `norm_templated` otherwise.
- Superseded records are excluded, so the existing supersession test, which copies a note, still passes.
- I confirmed that the committed decisions still pass. Under a non-certified digest they are rejected, which is the expected grandfathering behaviour.
- New tests:
  - a templated collision is rejected under an uncertified digest;
  - the same collision is grandfathered under the certified digest;
  - an exact repeat is rejected under the certified digest;
  - a superseded repeat is ignored.

### WR-06: D-10 "live catalog edit does not change the build or `--validate` result" is not proven

**Files modified:** `tests/test_archive_assessment_lineage_validation.py`
**Commit:** b72c3e9
**Applied fix:**
- New test `test_d10_live_catalog_edit_or_delete_does_not_change_build_or_validation`. It runs in a scratch git repo pinned to the real catalog blob.
- It asserts that `jtext(build_authority())` and `build_published_authority()` are unchanged, and that `validate_publication` still passes, after the working-tree catalog is first overwritten and then deleted.
- I checked the same logic manually outside pytest.

### WR-07: D-13 "changing the answers bytes removes the exemption" is tested with a fabricated digest

**Files modified:** `tests/test_archive_assessment_governance_answers.py`
**Commit:** 6893164
**Applied fix:**
- New tests copy the committed answers file to `tmp_path` and monkeypatch `MODULE.ANSWERS` to point at the copy. They then drive `build_from_files()` and the `--validate-answers` CLI (`main()`).
- The untouched copy keeps the certified digest and builds.
- Appending one byte changes `answers_digest()`, and both real paths then fail with `repeats the note of`.

## Skipped Issues

### WR-01: Pre-publication anchor is hard-wired to the 2.0.0 constant and its messages

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:695-698`
**Reason:** Deferred to Phase 9 by design, as the orchestrator instructed. `SUPERSEDED_V2_0_0` must stay 2.0.0 until 2.0.2 is published (08-RESEARCH note; 08-CONTEXT Phase 9 sequence). The same constant drives `source_lineage.supersedes`, the decisions-digest equality check, the schema pin and the dry-run summary. Repointing it now would break the current 2.0.1 build and validation. Phase 9 must rename the constant, update it to 2.0.1 at `31addfa`, and make the messages and test regexes version-agnostic.
**Original issue:** In pre-publication mode the record must name the superseded authority (2.0.1 at `31addfa` for 2.0.2), but the code and its messages are tied to `SUPERSEDED_V2_0_0`.

---

_Fixed: 2026-11-12_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
