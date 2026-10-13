---
phase: 01-rule-shape-and-decision-states
plan: 02
subsystem: archive-assessment-applicability
tags: [schema, validator, resolver, v2]
requires: [01-01]
provides: [v2 publisher (build/validate/schema/resolve_applicability), v2 JSON schema]
key-files:
  created:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - schemas/archive_assessment_applicability_authority_v2.schema.json
  modified: []
requirements-completed: [SCHEMA-01, SCHEMA-02, SCHEMA-03, SCHEMA-04, SCHEMA-05, SCHEMA-06]
duration: short
completed: 2026-10-13
---

# Phase 1 Plan 02: v2 Publisher and Schema Summary

v2 publisher and schema for the not-applicable rule shape (flat ALL-match conditions), three decision states, AA4-GOV authority citation and the full semantics block, with a fail-closed reference resolver. Nothing is published.

## Scope statement (D-07/D-08)
In 2.0.0 rule conditions may name only production, internet_exposed, contains_customer_data, ai_enabled. owner, tier, service_criticality and data_classification remain declared classification fields but are not usable in rules.

## What was built
- `build_authority()` builds 80 controls, all NOT_YET_DECIDED, version 2.0.0, authority_id EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0, lineage read from the tracked v1 registry (no generated/ access) plus a `supersedes` entry (commit 62a8955, sha256 of v1 registry).
- `validate_authority()` enforces rule shape (flat, 1..4 conditions, unique fields, KNOWN_TRUE/KNOWN_FALSE only, four rule fields only), three-way state/rule/authority consistency, AA4-GOV-NNN authority (AA1-GOV rejected), pinned semantics (field_definitions checked separately; wording from approved 01-FIELD-DEFINITIONS.md, verbatim).
- `schema()` emits Draft 2020-12 with three if/then branches. `resolve_applicability()` implements the five D-12 rows, no short-circuit, exact-string fact comparison, fail closed.
- CLI: `--validate` (raises "not published" while no v2 registry file exists) and `--emit-schema`. No publish path, no v2 registry file, nothing written under generated/.

## Verification (actual)
- py_compile OK; built authority passes validate_authority and the emitted schema.
- Mutations rejected by validator and schema: free-text rule, non-rule field (owner), UNKNOWN condition state, AA1-GOV authority, NO_RULE without authority, NOT_YET_DECIDED with authority. Repeated field rejected by validator only (JSON Schema cannot express per-field uniqueness; D-04 is validator-enforced as planned).
- Resolver: both conditions met -> NOT_APPLICABLE; one UNKNOWN even with other failing -> APPLICABILITY_UNRESOLVED; unmet -> APPLICABLE; boolean fact -> unresolved.
- `--validate` -> AuthorityError "v2 registry authority file is not published" (expected).
- v1 files byte-unchanged (never edited). registry/adjudication_rules.json and policy_decisions.json never touched (their unrelated edits exist only in the main checkout).

## Deviations
None to the code. Environment note: the v1 pytest file (tests/test_archive_assessment_applicability_authority.py) fails 12/12 in this worktree with FileNotFoundError on gitignored `generated/.../ems-aa2/...` (the v1 builder needs it; absent in a fresh worktree). Not caused by this plan; v1 is unedited. It should be re-run in the main checkout, where generated/ exists.

## Commits
- d8c9cf5: feat(01-02): add v2 applicability authority publisher and schema

## Self-Check: PASSED
Both files exist and are committed in d8c9cf5.
