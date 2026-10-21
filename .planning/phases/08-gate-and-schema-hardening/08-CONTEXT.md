# Phase 8: Gate and Schema Hardening - Context

**Gathered:** 2026-10-20
**Status:** Ready for planning

<domain>
## Phase Boundary

The gates that guard publication and the reply now fail closed on every path the v1.0.0 audit found open. `--validate` no longer depends on the live shared catalog, and the generated v2 schema rejects unexpected fields itself. Covers GATE-01..05 and SCHEMA-07.

This phase changes the v2 publisher, the reply builder's commit lookup and the governance-decisions builder's uniqueness check. It does not publish 2.0.2 (Phase 9). It does not regenerate any committed registry, schema or generated output, and it does not bump `VERSION`. The accepted red window from Phase 7 stays open: the red set may grow only by tests named in a plan.

</domain>

<decisions>
## Implementation Decisions

### Pre-publication mode (GATE-01)
- **D-01:** The pre-publication window is an explicit CLI flag, `--validate --pre-publication`. In that mode the publication record must exist and name exactly the superseded authority (for 2.0.2 that is `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1`, version 2.0.1). Its digests and commit are checked against that superseded publication.
- **D-02:** Plain `--validate`, which is what CI runs, requires a publication record whose `authority_id` and `version` match the current authority. If the record is absent, or names any other authority, it fails. Today's skip branch at publisher L679-683 is removed.
- **D-03:** The record cross-check also proves that `publication_commit` really contains the published bytes. It runs `git_show(publication_commit, AUTHORITY_REL)` and `git_show(publication_commit, <manifest rel>)`, reusing the Phase 7 helper, and their LF digests must equal `authority_sha256` and `manifest_sha256`. If history is missing it fails closed.

### Mutation gate (GATE-02)
- **D-04:** `mutation_gates` counts a rejection only for domain errors:
  - AUTHORITY and SIGNOFF targets: `AuthorityError`
  - DECISIONS target: the builder's `ValueError`
  - schema gate: `jsonschema.ValidationError`

  Any other exception propagates and fails the run. It is never counted as a rejection.
- **D-05:** Any of the 26 existing mutations that is rejected today only through `KeyError`, `TypeError` or `AttributeError` is fixed by hardening the validators (`validate_publication`, `validate_signoff`, the decisions validator path) so they check shape first and raise the domain error. Mutation ids and descriptions do not change, and every mutation must still be rejected.
- **D-06:** The negative-invariant output keeps its current shape (`rejected_by: [PYTHON_VALIDATOR, SCHEMA]`), with no exception-class field.

### Catalog freezing (GATE-03)
- **D-07:** The frozen reference is the catalog at a pinned commit. `catalog_reference` gains `commit: 62a8955dc28d9458cd1167fad314926e057c31fc`, the v1 baseline. Its LF digest is `12bb1a9d…`, verified identical at `62a8955`, `31addfa` and HEAD on 2026-10-20; the catalog last changed in `d5c1a73`.
- **D-08:** Every catalog read in the v2 publisher goes through `git_show(CATALOG_COMMIT, CATALOG_REL)` instead of the live file. That covers `catalog_controls()` used by the build (L133), `validate_publication` (L241, L306) and lineage. `catalog_reference` joins `COMMIT_PINNED` in `validate_lineage`. The live `registry/control_catalog.yaml` is no longer read by `--validate`.
- **D-09:** Without git history, or in a shallow clone, catalog validation fails closed, consistent with 07 D-11. CI uses `fetch-depth: 0`.
- **D-10:** Tests prove both directions:
  - editing the live catalog in a scratch copy does not change the `--validate` and build result;
  - tampering with the pinned reference (its commit, path or digest) makes validation fail.

### Shallow-clone lookup (GATE-04)
- **D-11:** `resolve_record_commit` in `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` first runs `git rev-parse --is-shallow-repository`. If the answer is `true`, or the command fails, it raises `AuthorityError` with an explicit message along the lines of "shallow clone: cannot resolve the publication record commit; fetch full history". A full clone behaves as before.
- **D-12:** GATE-04 is output-neutral. The reply JSON and MD stay byte-identical and nothing is regenerated in Phase 8. Phase 7 D-14 still holds for reply content.

### Claude's Discretion
- **GATE-05:** cross-note uniqueness in `scripts/build_archive_assessment_governance_decisions.py` compares `norm_templated` forms on both sides, and at every comparison site rather than only L161. Add a test with two notes that differ only in templated values. The change must be output-neutral, so the committed decisions do not change.
- **SCHEMA-07:** `schema()` sets `additionalProperties: false` at the top level, on control rows and on `not_applicable_semantics`. Add three negative mutations (an extra field at each level) with `schema_must_reject=True`, so the negative-invariant output records each as rejected by `SCHEMA`. The mutation count grows from 26 to 29, and the certified outputs pick this up at the Phase 9 republication.
- **Keep the flag minimal:** the exact flag name is `--pre-publication`; the helper names are up to the planner. Match the publisher's compact single-quote style.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope
- `.planning/ROADMAP.md` — Phase 8 goal, success criteria, red-window and staging rules
- `.planning/REQUIREMENTS.md` — GATE-01..05, SCHEMA-07
- `.planning/PROJECT.md` — constraints

### Prior decisions
- `.planning/phases/07-lineage-source-and-per-digest-scope/07-CONTEXT.md` — lineage shape; D-10 and D-11 git_show fail-closed; D-14 reply untouched
- `.planning/phases/07-lineage-source-and-per-digest-scope/07-REVIEW-FIX.md` — `bad_rel`, `COMMIT_PINNED`, type guards added in Phase 7
- `.planning/phases/06-address-tech-debt-publication-gate-hardening-2-0-1/06-REVIEW.md` — origin of WR-02, WR-04 and WR-05
- `.planning/phases/03-governance-decisions/03-REVIEW.md` — origin of Phase 3 WR-01 (`norm_templated`)
- `.planning/milestones/v1.0.0-MILESTONE-AUDIT.md` — tech-debt list (catalog live coupling, schema strictness)

### Code
- `scripts/publish_archive_assessment_applicability_authority_v2.py`:
  - `catalog_controls` L90, build L133/L170, `validate_publication` L241 and L306
  - `git_show` and `validate_lineage`
  - `mutation_gates` L584-601, `run_mutations` L603
  - `validate_published` L655-684, `write_publication_record` L686, `main` L693
- `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` — `resolve_record_commit` L262-267, `git()` L258
- `scripts/build_archive_assessment_governance_decisions.py` — `norm`/`norm_templated` L69-71, uniqueness L161
- `scripts/validate_archive_assessment_rule_proposals.py` — the 06 D-03 frozen-catalog analog (`frozen_catalog` L78); its skip behaviour is NOT copied (D-09)
- `tests/test_archive_assessment_applicability_authority_v2_publication.py` — the `env` fixture (stubs `validate_lineage`), record-check tests, mutation tests
- `tests/test_archive_assessment_lineage_validation.py` — temp git repo fixture to reuse for the catalog and commit-pinned tests

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `git_show`, `bad_rel`, `COMMIT_PINNED`, `NORMALISERS` and `EXPECTED_NORMALISATION` from Phase 7 can be reused for the catalog pin and the D-03 commit check.
- The temp git repo fixture in `tests/test_archive_assessment_lineage_validation.py` suits the catalog and record-commit tests.

### Established Patterns
- `errors = []`, joined at the end and raised as `AuthorityError`.
- `build_*` / `validate_*` pairs.
- The schema is generated by `schema()`; it is never hand-edited.
- The `env` fixture monkeypatches `ROOT` and stubs `validate_lineage`. New git-dependent checks inside `validate_published` need the same treatment, or a recorder, so synthetic tests stay meaningful.

### Integration Points
- The catalog via `git_show` changes the build input source. The 2.0.2 output must still be byte-identical in its decision content (PUB-08). Since the catalog bytes are identical at `62a8955`, the build output must not change.
- The red window: any new test that reads the real committed 2.0.1 files and expects the new behaviour (for example a record matching the current authority) must be listed in the plan's expected red set. The current red set is 3 tests plus `--validate`.

</code_context>

<specifics>
## Specific Ideas

- The Phase 9 sequence becomes: `--publish`, commit, `--validate --pre-publication` (the record still names 2.0.1), `--record-publication <sha>`, commit, then plain `--validate`, which must PASS and closes the red window.

</specifics>

<deferred>
## Deferred Ideas

- Recording the exception class in the negative-invariant output (D-06: not now).
- Verifying the reply record's introducing commit beyond the shallow check (D-11 chose shallow detection only).

</deferred>

---

*Phase: 08-gate-and-schema-hardening*
*Context gathered: 2026-10-20*
