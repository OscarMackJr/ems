# Phase 2: Blind Drafting - Context

**Gathered:** 2026-10-13
**Status:** Ready for planning

<domain>
## Phase Boundary

A committed, machine-readable proposals file holds a rule-or-no-rule proposal with rationale for each of the 21 requested controls (EMS-CTRL-009, 010, 011, 012, 013, 014, 015, 017, 018, 019, 020, 021, 022, 030, 033, 039, 042, 052, 062, 075, 079), drafted from the control catalog entries alone, and fixed in git history before any governance decision (DRAFT-01..03).

This phase delivers: an approved drafter brief, the proposals file with its schema, validator script and tests, and a drafting record that names the drafting commit. It issues no `AA4-GOV-NNN` ids, records no governance decision, writes no v2 authority registry file, and changes nothing in the published v1.0.0 authority. No rule is compared with any target.

</domain>

<decisions>
## Implementation Decisions

### Permitted drafting inputs
- **D-01:** The only EMS-source input to a proposal is that control's entry in `registry/control_catalog.yaml`. No other registry file (`control_scope_registry.yaml`, `applicability_profiles.yaml`, `wave2d/applicability_rules.json`, `github_control_mapping.yaml`, `wave1_evidence_strategies.yaml`, `adjudication_rules.json`, `policy_applicability.yaml`) is an input.
- **D-02:** Fact found while scouting: none of the 21 catalog entries has a `description`. Each carries `control_name`, `scope`, `scope_owner`, `inheritance_allowed`, `evidence_authority`, a boilerplate seed `rationale` and `classification_status`. The proposals file states this once in its header.
- **D-03:** A rationale may rely on general engineering knowledge of what the named practice is. That reading is recorded per proposal in a separate, labelled `interpretation` field and is marked as the drafter's assumption, not an EMS source.
- **D-04:** Each proposal embeds the exact catalog field values it used (`control_name`, `scope`, `scope_owner`, `evidence_authority` at minimum). The file records the SHA-256 (and git blob id) of `registry/control_catalog.yaml` once. A test re-reads the catalog and fails if any embedded value differs.
- **D-05:** The Phase 1 rule shape/semantics and the approved field definitions are declared once in the file header as the "drafting frame" (the language proposals are written in). They are not per-proposal inputs.

### Drafting posture
- **D-06:** Lean to "no rule". A rule is proposed only when the control name itself points at one of the four rule fields. Otherwise the proposal is "no rule" (which resolves to `APPLICABLE` for every target). A control is never proposed as switchable-off on a guess.
- **D-07:** A proposed rule uses the fewest conditions that justify it, normally one. A condition is added only when the rationale needs it; each added field is one more that can be `UNKNOWN`.
- **D-08:** Every proposal carries `confidence` (`HIGH` / `MEDIUM` / `LOW`) and `alternative_considered`: the outcome the drafter rejected and why, or null.
- **D-09:** Six of the 21 are not REPOSITORY-scoped (022, 042 PLATFORM; 030 SERVICE; 052 ORGANIZATION; 062 APPLICATION; 075 EMS). Drafts stay inside the Phase 1 shape. Where scope is the real reason a control might not apply and the four fields cannot say so, the proposal carries a structured `shape_limitation` note. There is no third "defer" outcome: every entry is rule or no-rule.
- **D-10:** A control that would need an "or" is drafted as a narrower single list or as "no rule" (carried from Phase 1 D-02).

### Proposals file form
- **D-11:** One JSON file under `registry/`, named so it reads as a draft (working name `registry/archive_assessment_not_applicable_rule_proposals.json`), with top-level status `DRAFT_NO_AUTHORITY` and a statement that it is not an authority, binds nothing and must not be cited as a decision.
- **D-12:** Per-proposal fields: `control_id`, `proposed_outcome` (rule or no-rule), `proposed_rule` (Phase 1 shape: `combination` + `conditions`, or null), `catalog_inputs`, `interpretation`, `rationale`, `confidence`, `alternative_considered`, `shape_limitation`. No `not_applicable_authority`, no decision id.
- **D-13:** The JSON is hand-authored content (the drafter's output). A validator script checks it and emits its schema, following the publisher pattern (`build`/`validate` split, `AuthorityError`-style accumulate-then-raise). Proposed rules are validated with the existing `validate_rule()` from the v2 publisher. A pytest module covers it.
- **D-14:** No digest certification or publication manifest in this phase; that is Phase 4.
- **D-15:** The proposals file is frozen after the drafting commit. No edits, not even typo fixes. Changes are expressed in Phase 3 decision records (drafted text vs decided text).

### Proving blindness
- **D-16:** The 21 proposals are written by one isolated AI drafter working from a fixed brief. Not the normal GSD executor (it loads planning files that mention the assessment), and not the user (who knows the per-control result).
- **D-17:** The brief inlines everything the drafter may use: verbatim extract of the 21 catalog entries only (not all 80), the v2 rule shape and resolution semantics, the approved field definitions, the posture rules (D-06..D-10), the rationale standard (D-27, D-28) and the output format. The drafter needs no file tools, is told to use only that text, and returns JSON. The orchestrator writes the returned content to the file unchanged.
- **D-18:** The brief states the task and semantics only: for each control, propose a not-applicable rule or "no rule" for an archived repository snapshot target, and what each outcome resolves to. It says nothing about who asked, any assessment, any target, or any consumer.
- **D-19:** The brief is governance content. It is drafted in this phase, approved by Oscar Mack, committed, and only then used. The user sees the instructions before the drafting commit, never the proposals.
- **D-20:** The user does not read proposal content before the drafting commit. Once the validator passes, the drafter's output is committed as produced. First review is Phase 3.
- **D-21:** If the validator fails, the same drafter receives only the validator's error messages and corrects them. No other agent edits proposal content. The number of correction rounds is recorded.
- **D-22:** If a run is unusable for a non-mechanical reason, a fresh isolated drafter starts over with the same approved brief. The discarded attempt is not kept or compared; the drafting record says an attempt was discarded and why. No selecting between attempts.
- **D-23:** One drafter, one run. No second independent drafter.
- **D-24:** A drafting-record JSON file is committed in Phase 2 immediately after the drafting commit. It holds: drafting commit SHA, proposals file SHA-256, catalog SHA-256, brief SHA-256, validator result, correction rounds, any discarded attempt, date, isolation method (by instruction and brief design), and the statement that an AI agent (model id named) drafted, holds no EMS authority, and that the proposals bind nothing until decided by the EMS governance authority. A test checks the recorded SHA is an ancestor commit that contains the proposals file. Phase 3 decision records cite this file.
- **D-25:** A pytest scans the proposals file, the brief and the drafting record, case-insensitive, for a fixed term list: `RiskMVP`, the RiskMVP commit SHA and its short form, `Hayes`, the `2026-10-01` assessment date, `EMS_NOT_APPLICABLE_RULE_ABSENT`, `DEMO3-W1-REQ-001`. The term list lives in the test, not in the scanned files. Consequence: the brief, the proposals file header and the drafting record must be worded without those terms (including the request id).

### Requirement wording
- **D-26:** DRAFT-02 and roadmap Phase 2 success criterion 2 are amended (applied in the same commit as this context) to say: EMS-source inputs are catalog definitions only; the drafter's reading of a control name is a labelled interpretation, not an EMS source; the Phase 1 shape and approved field definitions are the declared drafting frame.

### Rationale standard
- **D-27:** Each rationale is two to four sentences and covers fixed points: why the outcome follows from the interpretation; for a rule, why the named field and state mark the control as not applying, in terms of the approved field definition; for no-rule, why none of the four fields gives a sound exemption.
- **D-28:** Each rationale stands alone and names its own control's practice. No shared reason codes or cross-references between proposals; repetition is accepted. Each rationale becomes the "drafted text" of its own Phase 3 decision record.

### Claude's Discretion
- Exact file names for the proposals file, schema, validator script, test, brief and drafting record (snake_case, matching the v2 naming).
- Where the brief and drafting record live (tracked, not under gitignored `generated/`).
- Exact JSON key names and enum values (for example the two `proposed_outcome` values), consistent with D-12 and the v2 decision-state names.
- Order of the tooling commits relative to the brief commit, provided: brief approved and committed before the drafter runs; one drafting commit contains all 21 proposals; the drafting record comes in a later commit; tests do not sit red in between.
- How the ancestor-commit test behaves in shallow clones (CI).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and requirements
- `.planning/PROJECT.md` — constraints (drafting independence, vocabulary, boundary, working tree)
- `.planning/REQUIREMENTS.md` — DRAFT-01..03 (DRAFT-02 as amended 2026-10-13)
- `.planning/ROADMAP.md` — Phase 2 success criteria (criterion 2 as amended), ordering guarantees, "Notes for Planning"
- `.planning/STATE.md` — blockers/concerns (stage by explicit path only)

### Drafting input (the only EMS source)
- `registry/control_catalog.yaml` — entries for the 21 controls; no `description` on any of them

### Drafting frame (Phase 1 outputs)
- `.planning/phases/01-rule-shape-and-decision-states/01-CONTEXT.md` — D-01..D-16: rule shape, usable fields, decision states, resolution semantics
- `.planning/phases/01-rule-shape-and-decision-states/01-FIELD-DEFINITIONS.md` — approved definitions of the four rule-condition fields
- `scripts/publish_archive_assessment_applicability_authority_v2.py` — `validate_rule()`, `RULE_FIELDS`, `CONDITION_STATES`, `COMBINATION`, `semantics()`, `RESOLUTION`, `catalog_controls()`, helper pattern
- `schemas/archive_assessment_applicability_authority_v2.schema.json` — the published rule shape
- `tests/test_archive_assessment_applicability_authority_v2.py` — test style (`invalid(mutator)`, validator-only cases)

### Conventions
- `.planning/codebase/CONVENTIONS.md` — naming, code style, error handling, data artifact conventions
- `.planning/codebase/STRUCTURE.md` — where registry, schema, script and test files go; `generated/` is gitignored

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `validate_rule(cid, rule, errors)` in the v2 publisher: validates a proposed rule against the Phase 1 shape (combination, at least one condition, four usable fields, two states, no repeated field). Import it; do not re-implement.
- `catalog_controls()`, `digest()`, `dump()`, `load()`, `contains_absolute()`, `AuthorityError` in the v2 publisher: same helper pattern for the proposals validator.
- `semantics()` / `FIELD_DEFINITIONS` / `RESOLUTION` in the v2 publisher: source text for the inlined drafting frame in the brief.

### Established Patterns
- `build_*` (pure) and `validate_*` (raises) pairs so tests can deep-copy, mutate and expect failure.
- Schema emitted from code by `schema()`; deterministic JSON (`indent=2, sort_keys=True`, trailing newline); no absolute paths in registry JSON.
- New work uses `snake_case.py`, single quotes and compact helpers in `publish_*`-style scripts.

### Integration Points
- Phase 3 reads the proposals file and the drafting record; each decision record cites the drafting commit SHA and quotes the drafted rationale.
- Phase 4 publishes the v2 authority from the Phase 3 decisions, not from the proposals file.
- Mentions of the target assessment exist only under `.planning/` in tracked files. An agent that reads planning files has seen that an assessment happened; hence the isolated drafter (D-16).
- Working tree holds unrelated modified and untracked files: stage by explicit path only.

</code_context>

<specifics>
## Specific Ideas

- The JSON layout previewed in discussion used EMS-CTRL-052 with `ai_enabled` / `KNOWN_FALSE` purely to show field layout. It is not a proposal. The brief must not contain a worked example that uses any of the 21 controls or suggests an outcome for one.
- The brief must be clean of the D-25 terms, so it cannot say "do not consider <target>"; it says "use only the text in this brief".
- "No rule" is a real claim (applies to every target), not a neutral default; the brief should make the consequence of each outcome plain to the drafter.

</specifics>

<deferred>
## Deferred Ideas

- Using other EMS files (scope registry, applicability profiles, Wave 2D general rules) as drafting inputs — declined for this phase; revisit only by a requirement change.
- Writing approved catalog descriptions for controls that lack them — considered and not chosen; no backlog item was requested.
- A second independent drafter with per-control agreement recorded — declined for this milestone.
- A generated Markdown view of the proposals for reading in Phase 3 — not chosen here; Phase 3 may decide how proposals are presented for decision.

</deferred>

---

*Phase: 2-Blind Drafting*
*Context gathered: 2026-10-13*
