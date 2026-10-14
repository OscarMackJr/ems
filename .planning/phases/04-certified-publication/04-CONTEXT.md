# Phase 4: Certified Publication - Context

**Gathered:** 2026-10-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Publish `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0`, a new controlled version of the archive-assessment applicability authority (PUB-01..06). In it:
- the 21 requested controls each carry an explicit decision taken from the Phase 3 records `AA4-GOV-001`..`021`: three `RULE_PUBLISHED` (EMS-CTRL-030 and 039 on `production` `KNOWN_FALSE`, EMS-CTRL-052 on `ai_enabled` `KNOWN_FALSE`) and eighteen `NO_RULE_WILL_BE_PUBLISHED`
- the other 59 controls are `NOT_YET_DECIDED` and otherwise identical to v1.0.0
- the publication comes with certification, a manifest, decision-to-control traceability and pytest invariants, in a clean publication commit Hayes can re-pin to.

This phase also clears the Phase 3 review debt (CR-01..03, WR-01..09) that would otherwise make `--validate` an untrustworthy publication gate.

It does not change any governance decision, the proposals, the drafting record, the field definitions, the control catalog or the v1.0.0 authority or outputs. It writes no reply (Phase 5), compares no rule with any target, and does not push or merge.

</domain>

<decisions>
## Implementation Decisions

### Review debt and line endings
- **D-01:** All three critical findings (CR-01 line-ending hashing, CR-02 answers binding, CR-03 strict checks on superseding entries) and all nine warnings (WR-01..09) in `03-REVIEW.md` are fixed before anything is published, with tests for each. Info items IN-01..05 are not in scope.
- **D-02:** A new, narrow `.gitattributes` lists only this project's files as `text eol=lf`: the `archive_assessment_*` registry and schema JSON this project created, `docs/ARCHIVE_ASSESSMENT_RULE_PROPOSALS_VIEW.md`, the v2 registry authority and the `generated/archive-assessment/ems-aa3-v2/` outputs. No broad globs, so checkout of unrelated in-flight files is not affected.
- **D-03:** v1.0.0 files are NOT listed in `.gitattributes` and are not touched. Their raw-byte manifest is a recorded v1 limitation.
- **D-04:** Every SHA-256 that this phase writes or checks (manifest, certification, lineage, frozen-input digests) is taken over LF-normalised bytes (CRLF→LF), and the document states this in a normalisation field, following the existing `answers_sha256_normalisation` precedent. The digests then come out the same on any checkout, and Hayes can recompute them.
- **D-05:** All generated files are written with `newline='\n'` (fixes WR-08) so bytes on disk do not depend on the OS.
- **D-06:** The review fixes land in their own commits, before the `.gitattributes` commit, the publisher-code commit and the publication commit.
- **D-07:** If the fixes require rewriting `registry/archive_assessment_governance_decisions.json`, only header digest/normalisation fields and newline bytes may change. Every record must be value-equal to the version at commit `eed4a5f` (ids, dispositions, notes, rules, rationales, dates). A test proves this against `git show eed4a5f:<path>`. The answers file is not rewritten.

### What a decided control carries
- **D-08:** Per control, the AA4-GOV id goes in `not_applicable_authority` only. `decision_ids` keeps exactly the eight AA1-GOV-001..008 ids on all 80 rows (Phase 1 D-16).
- **D-09:** A new top-level list (working name `applicability_decision_ids`) holds the 21 AA4-GOV ids that the authority publishes. `approved_governance_decision_ids` stays the eight AA1 ids. Every `not_applicable_authority` must appear in the new list, and every id in the list must be cited by exactly one control. This needs a schema change in the v2 publisher (`schema()`), regenerated, not hand-edited.
- **D-10:** `source_lineage` gains a `governance_decisions` entry with `relative_path`, LF `sha256`, `record_count` and `drafting_commit`. The validator checks the digest against the live decisions file. It also checks that each cited id is the latest unsuperseded record for that control and that the decided state and rule match that record (`decided_outcome`, `decided.rule`).
- **D-11:** Control rows stay lean: decision state, rule and authority id only. Rationale, `decided_on`, notes and scope-note rulings stay in the decision records and are not copied into the authority. The traceability output joins control → AA4 id → record.
- **D-12:** The v2 validator, not only the tests, pins the decided set to exactly the 21 request ids (EMS-CTRL-009, 010, 011, 012, 013, 014, 015, 017, 018, 019, 020, 021, 022, 030, 033, 039, 042, 052, 062, 075, 079) and requires every other control to be `NOT_YET_DECIDED`.
- **D-13:** The validator and a test compare all 80 rows field by field with the v1.0.0 registry file. Every v1 field must be equal. The only fields added are `not_applicable_decision_state` on all rows and the non-null rule/authority on the 21. Any other difference fails.

### Output location and determinism
- **D-14:** The registry authority is `registry/archive_assessment_applicability_authority_v2.json`, the path the v2 publisher already uses. Generated outputs go in a new `generated/archive-assessment/ems-aa3-v2/` folder, force-added as v1's `ems-aa3/` was. The v1 `ems-aa3/` folder is not touched.
- **D-15:** The output set mirrors v1's (authority matrix, semantic validation, negative-invariant validation, publication certification JSON, publication report `.md`, publication manifest) and adds an AA4 decision-to-control traceability file. That file holds 21 records (control, AA4 id, decision state, rule or null, record path and digest) plus the 59 undecided controls. Names follow v1 with a v2 marker.
- **D-16:** No `now()`. A fixed `published_on` date constant in the publisher stamps the outputs, so re-running publish produces byte-identical files.
- **D-17:** `--validate` rebuilds the authority and every output in memory and requires equality with the committed files and with every LF digest in the manifest before it prints `PASS`. A pytest runs the same check. A consistent hand edit plus a re-hash must fail.
- **D-18:** The publisher reads tracked inputs only: the catalog, the v1 authority, the governance decisions, the proposals and the drafting record. The AA2 lineage digests are copied from the v1 registry file, as `build_authority()` already does. Publishing and `--validate` must work on a fresh clone and on ubuntu CI.

### Publication commit and sign-off
- **D-19:** Human gate: after a dry-run publish, execution stops at a blocking checkpoint. The authority (Oscar Mack) sees a summary: 21 decided and 59 undecided; for each of the 21, the control, its AA4 id and its state; the three rules in full; and the authority LF digest. He then approves. The approval is recorded in a tracked file (approver, role, date, authority LF digest, scope) and cited by the certification. This follows the pattern of the Phase 3 wording approval.
- **D-20:** The publication commit, the SHA Hayes re-pins to, holds only the generated publication: the v2 registry authority, the `ems-aa3-v2/` outputs and the sign-off record. Publisher code, the schema change and tests land in an earlier commit. `git show --stat` on the publication commit must list only those files.
- **D-21:** A small follow-up commit adds a publication record holding the publication commit SHA, the authority id and version, and the manifest and authority LF digests. A test checks that the SHA is an ancestor commit containing the authority with that digest, following the Phase 2 drafting-record test (with the same shallow-clone handling). Phase 5 cites this SHA.
- **D-22:** Phase 4 does not push, tag or merge. The last step reports the publication SHA and the push command, and the authority pushes.

### Claude's Discretion
- Exact names for the new top-level id list, the lineage entry, the normalisation field, the v2 output files, the sign-off record and the publication record (snake_case, `archive_assessment_*` / v1 naming with a v2 marker).
- Whether the v2 build/publish code extends `scripts/publish_archive_assessment_applicability_authority_v2.py` (preferred, since it already owns `build_authority`/`validate_authority`/`schema`) or sits in a sibling script, and how CLI flags are named (`--publish`, `--validate`, `--emit-schema`).
- How the LF digest helper is shared between the Phase 3 builder and the v2 publisher (import from one place; do not duplicate the normalisation rule).
- How tests behave before the publication commit exists. They must not sit red between commits: real-file tests skip when the v2 registry file or the publication record is absent, then go active once it exists.
- How many commits the review fixes take, and in what order. Each commit stages explicit paths only.
- The exact `published_on` date value (the date of the publication run).
- The wording of the sign-off summary. It must be neutral and complete, adding no ranking or emphasis.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and requirements
- `.planning/PROJECT.md` — constraints (publication pattern, working tree, scope), key decisions, the 21 controls
- `.planning/REQUIREMENTS.md` — PUB-01..06 for this phase; REPLY-02 for what Phase 5 needs (authority id, version, commit)
- `.planning/ROADMAP.md` — Phase 4 success criteria 1–5, ordering guarantees, "Notes for Planning"
- `.planning/STATE.md` — Phase 4 prerequisites (CR-01, CR-02), stage by explicit path only

### Review debt to clear (prerequisite)
- `.planning/phases/03-governance-decisions/03-REVIEW.md` — CR-01..03 and WR-01..09 with probes and suggested fixes

### Prior phase decisions
- `.planning/phases/01-rule-shape-and-decision-states/01-CONTEXT.md` — D-11..D-19: decision states, resolution semantics, authority carries AA4 id for both outcomes, AA1 provenance kept, v2 files beside v1, version 2.0.0
- `.planning/phases/03-governance-decisions/03-CONTEXT.md` — D-12 (latest unsuperseded record is published), D-14 (id ↔ control mapping), D-20 (drafting commit cited)
- `.planning/phases/02-blind-drafting/02-CONTEXT.md` — D-24 (ancestor-commit test pattern for a recorded SHA)

### Inputs (tracked, read-only except D-07)
- `registry/archive_assessment_governance_decisions.json` — 21 records AA4-GOV-001..021 (`decided_outcome`, `decided.rule`, `supersedes`)
- `registry/archive_assessment_governance_answers.json` — authority-typed answers (not rewritten)
- `registry/archive_assessment_not_applicable_rule_proposals.json`, `registry/archive_assessment_rule_proposals_drafting_record.json` — frozen
- `registry/archive_assessment_applicability_authority.json` — v1.0.0, the field-by-field baseline (D-13) and lineage source
- `registry/control_catalog.yaml` — 80 controls

### Code to extend / follow
- `scripts/publish_archive_assessment_applicability_authority_v2.py` — `build_authority()`, `validate_authority(a, known_decision_ids)`, `schema()`, `resolve_applicability()`; currently only `--validate`/`--emit-schema`, with no publish step
- `schemas/archive_assessment_applicability_authority_v2.schema.json` — generated from `schema()`; regenerate after D-09
- `scripts/publish_archive_assessment_applicability_authority.py` — v1 `publish()`: the output set, matrix/semantic/negative/traceability/certification/report/manifest pattern to mirror (D-15)
- `scripts/build_archive_assessment_governance_decisions.py` — Phase 3 builder/validator to fix (CR/WR); `answers_digest` and normalisation precedent
- `tests/test_archive_assessment_applicability_authority_v2.py`, `tests/test_archive_assessment_governance_decisions.py`, `tests/test_archive_assessment_governance_answers.py`, `tests/test_archive_assessment_rule_proposals_record.py` — test style, `invalid(mutator)`, ancestor-commit test
- `generated/archive-assessment/ems-aa3/` — v1 tracked outputs (pattern only; do not edit)
- `generated/archive-assessment/ems-aa3/ems_aa3_archive_applicability_authority_publication_manifest.json` — v1 manifest shape (artifacts list, self-exclusion reason)

### Conventions
- `.planning/codebase/CONVENTIONS.md` — naming, code style, error handling, deterministic JSON
- `.planning/codebase/ARCHITECTURE.md` — authority publication flow

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- v2 publisher `build_authority()` already builds 80 rows as `NOT_YET_DECIDED`, with v1 lineage and `supersedes` pointing at commit `62a8955`. Phase 4 overlays the 21 decisions on it.
- `validate_authority(a, known_decision_ids=...)` already enforces the D-15 consistency rules and the AA4 id pattern. Phase 4 adds: the exact 21 set (D-12), the v1 diff (D-13), the decisions-file binding (D-10) and the top-level id list (D-09).
- `resolve_applicability()` can be used in the semantic-validation output and the tests (e.g. 030/039/052 with KNOWN_TRUE/KNOWN_FALSE/UNKNOWN facts).
- v1 `publish()` shows the output set and manifest construction; replace its `now()` and raw `digest()` with the fixed date (D-16) and the LF digest (D-04).

### Established Patterns
- `build_*` (pure) and `validate_*` (raises `AuthorityError`) pairs; tests deep-copy, mutate and expect failure.
- The schema is emitted from code; hand edits are overwritten.
- Deterministic JSON is `indent=2, sort_keys=True` with a trailing newline. No absolute paths in registry JSON.
- v1 outputs under the gitignored `generated/` were force-added (`git add -f`). The v2 outputs need the same.

### Integration Points
- The current v2 schema fixes `approved_governance_decision_ids` to eight AA1 ids and `decision_ids` to eight per row. D-09 adds a separate list rather than changing these.
- The Phase 3 decisions file was written with CRLF on this machine (WR-08). Fixing it touches a frozen file under D-07 rules only.
- `core.autocrlf=true` with no `.gitattributes` today. Adding `.gitattributes` may show listed files as modified until they are renormalised. Commit the renormalisation by explicit path.
- Phase 5 reads the publication record (D-21) for the SHA and the authority id/version.
- The working tree holds two modified registry files and about 60 untracked files from unrelated work. Never `git add -A`/`.`.

</code_context>

<specifics>
## Specific Ideas

- Success criterion 3 ("running the publisher regenerates... digests match") is meant literally: byte-identical regeneration, checked by `--validate` and pytest.
- The publication commit should be easy to audit: `git show --stat` lists only the v2 registry authority, the `ems-aa3-v2/` outputs and the sign-off record.
- A fresh Windows clone (`core.autocrlf=true`) must pass `--validate` and the full authority test suite. This was the failure mode in CR-01.

</specifics>

<deferred>
## Deferred Ideas

- IN-01..05 from the Phase 3 review (dead test line, abbreviation heuristic, test naming, proposals/digest source mix, shared test helpers) — not needed for the publication gate.
- Extending `.gitattributes` to v1 files or repo-wide globs — declined (D-02, D-03); general hardening.
- Annotated git tag for the publication commit, pushing, merging to main — left to the authority (D-22).
- Copying rationale or scope-note rulings into authority rows — declined (D-11). Phase 5 reads them from the records.

</deferred>

---

*Phase: 4-Certified Publication*
*Context gathered: 2026-10-14*
