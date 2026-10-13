# Phase 1: Rule Shape and Decision States - Context

**Gathered:** 2026-10-13
**Status:** Ready for planning

<domain>
## Phase Boundary

EMS chooses and makes machine-checkable the shape of a not-applicable rule, its named authority, and a three-valued decision state per control, with the rule semantics written out in full (SCHEMA-01..06).

This phase delivers publisher code, a schema and tests. It drafts no rules, records no governance decisions, writes no new registry authority file, and uses no target information. The published v1.0.0 authority at `62a8955` is not altered.

</domain>

<decisions>
## Implementation Decisions

### How conditions combine
- **D-01:** A `not_applicable_rule` holds one flat list of conditions. Each condition is a field/state pair. The rule is satisfied only when every condition matches (logical AND).
- **D-02:** No nesting, no negation, no `ANY`/"or" in this version. A control that would need an "or" is drafted as a narrower single list or as "no rule" (Phase 2 concern; the shape does not accommodate it).
- **D-03:** A rule has at least one condition. An empty (unconditional) rule fails validation.
- **D-04:** Each field appears at most once in a rule. Repeats fail validation (this also excludes contradictory rules).
- **D-05:** The AA2 rule-language proposal (`ALL`, `ANY`, `NOT`, `EQ`, `IN`, `KNOWN`, `UNKNOWN`) is not adopted. It was never approved (`PROPOSED_FOR_APPROVAL`) and is wider than the `KNOWN_TRUE`/`KNOWN_FALSE` constraint.
- **D-06:** A condition state is `KNOWN_TRUE` or `KNOWN_FALSE` only. `UNKNOWN`, any other value, and any free-text rule (for example the string `absence_of_evidence`) fail validation.

### Fields usable in a rule
- **D-07:** Rule conditions may name only the four yes/no fields: `production`, `internet_exposed`, `contains_customer_data`, `ai_enabled`.
- **D-08:** `owner`, `tier`, `service_criticality` and `data_classification` remain declared classification fields (the eight-field vocabulary and `classification_prerequisites` are unchanged) but are not usable in a rule in this version. A condition naming one of them fails validation, as does any field outside the eight.
- **D-09:** The authority publishes the four rule-condition fields as an explicit list in its semantics block, separate from the eight classification fields, with a statement that the other four are not usable in rules in this version. The restriction is not left to the schema enum alone.
- **D-10:** The authority publishes a short definition for each of the four rule-condition fields, stating what `KNOWN_TRUE` asserts about the target. The wording is governance content: it is drafted in this phase from EMS sources only and must be approved by Oscar Mack before it is committed.

### Decision states and outcomes
- **D-11:** Every control carries a decision state with exactly three values: `RULE_PUBLISHED`, `NO_RULE_WILL_BE_PUBLISHED`, `NOT_YET_DECIDED`. Any other value fails validation.
- **D-12:** Resolution semantics, stated in full in the authority:
  - `NOT_YET_DECIDED` resolves to `APPLICABILITY_UNRESOLVED` (same meaning as v1.0.0).
  - `NO_RULE_WILL_BE_PUBLISHED` resolves to `APPLICABLE` for every target, whatever the classification facts.
  - `RULE_PUBLISHED`, every named field known, all conditions met: `NOT_APPLICABLE`.
  - `RULE_PUBLISHED`, every named field known, conditions not all met: `APPLICABLE`.
  - `RULE_PUBLISHED`, any named field `UNKNOWN`: `APPLICABILITY_UNRESOLVED`. There is no short-circuit: this holds even when another named field is known and already fails its condition.
- **D-13:** `not_applicable_authority` carries the governance decision id for both decided outcomes (rule and no-rule). It is null only for `NOT_YET_DECIDED`.
- **D-14:** New governance decision ids follow the pattern `AA4-GOV-NNN`. The schema fixes the pattern now; ids are issued in Phase 3. They cannot collide with `AA1-GOV-001`..`008`.
- **D-15:** Consistency rules the schema/validator must enforce (SCHEMA-04): `RULE_PUBLISHED` requires a rule and an authority; `NO_RULE_WILL_BE_PUBLISHED` requires an authority and a null rule; `NOT_YET_DECIDED` requires a null rule and a null authority.
- **D-16:** The per-control v1.0.0 fields stay as they are, including `default_applicability_result: APPLICABILITY_UNRESOLVED` on every control. The resolution semantics of D-12 are stated once in a top-level semantics block, which must also say that the decision state governs the resolved result and the per-control default describes the result absent a decision. The existing AA1-GOV-001..008 provenance on each control is kept.

### Files and versioning
- **D-17:** The new shape lives in new versioned files beside v1.0.0: a new publisher, a new schema and a new test. The v1.0.0 publisher, schema, authority, test and manifest are not edited, so v1.0.0 digests stay valid and the existing tests pass unchanged. Some duplicated helper code is accepted.
- **D-18:** The new authority version is `2.0.0` (breaking shape change); the authority id becomes `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0` or equivalent with the 2.0.0 suffix.
- **D-19:** Phase 1 commits publisher code, schema and tests only. Tests exercise all three states with synthetic example controls. No new registry authority file is written until Phase 4, so nothing that looks published exists before the governance decisions.

### Claude's Discretion
- Exact JSON key names inside a condition and for the decision-state field (`not_applicable_decision_state` was used as a working name), matching existing registry naming.
- File names for the v2 publisher, schema and test.
- Whether the semantics are also described in a `docs/` page for readers, in addition to the semantics block.
- How much of D-15 is enforced in JSON Schema (`if`/`then`) versus `validate_*` code; both layers should fail closed.
- How validation errors are worded (follow the existing accumulate-then-raise `AuthorityError` style).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and requirements
- `.planning/PROJECT.md` — constraints (vocabulary, semantics, boundary, working tree), key decisions, the 21 controls
- `.planning/REQUIREMENTS.md` — SCHEMA-01..06 for this phase
- `.planning/ROADMAP.md` — Phase 1 success criteria and "Notes for Planning"
- `.planning/STATE.md` — Phase 1 blockers/concerns

### Existing v1.0.0 authority (pattern to follow, not to edit)
- `scripts/publish_archive_assessment_applicability_authority.py` — `build_authority()`, `validate_authority()`, `schema()`, `publish()`; generates both the registry file and the schema file
- `schemas/archive_assessment_applicability_authority.schema.json` — v1.0.0 constants (`version`, null rule/authority, eight `AA1-GOV-00[1-8]` ids)
- `registry/archive_assessment_applicability_authority.json` — published v1.0.0 content; per-control field set
- `tests/test_archive_assessment_applicability_authority.py` — mutate-and-expect-`AuthorityError` test pattern; `test_implicit_not_applicable_fails_closed`
- `generated/archive-assessment/ems-aa3/ems_aa3_archive_applicability_authority_publication_manifest.json` — v1.0.0 manifest hashing publisher, schema and authority

### Prior governance material (AA2, local and untracked)
- `generated/archive-assessment/ems-aa2/approval/archive_assessment_applicability_governance_decisions_approved.json` — approved text of AA1-GOV-003 (required UNKNOWN yields unresolved) and AA1-GOV-004 (explicit rule evaluation and authority citation)
- `generated/archive-assessment/ems-aa2/archive_assessment_rule_language_design.json` — the unapproved operator proposal that D-05 declines
- `generated/archive-assessment/ems-aa2/archive_assessment_classification_vocabulary.json` — the eight fields and attribution requirement

### Conventions
- `.planning/codebase/CONVENTIONS.md` — naming, code style, error handling, data artifact conventions
- `.planning/codebase/ARCHITECTURE.md` — authority publication flow

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `digest`, `dump`, `load`, `contains_absolute`, `catalog_controls`, `AuthorityError` in the v1.0.0 publisher: copy the pattern into the v2 publisher (D-17 accepts the duplication).
- `CLASSIFICATION_FIELDS` constant: the eight fields; the v2 publisher adds a separate four-field rule-condition list.
- Test helper `invalid(mutator)`: build, deep-copy, mutate, expect `AuthorityError`.

### Established Patterns
- `build_*` (pure) and `validate_*` (raises) pairs so tests can mutate a built object.
- Schema is emitted from code by `schema()`; hand edits to a schema file are overwritten on publish.
- Deterministic JSON: `json.dumps(value, indent=2, sort_keys=True) + '\n'`; no absolute paths in registry JSON.
- v1.0.0 `validate_authority` hard-codes `version == '1.0.0'`, `decision_ids == DECISIONS` and null rule/authority; the v2 validator needs its own equivalents.

### Integration Points
- `build_authority()` reads `generated/archive-assessment/ems-aa2/approval/archive_assessment_applicability_governance_closure.json`, which is not tracked in git. A v2 builder that reuses this lineage depends on a local-only file; planning must decide how v2 handles it (and CI runs on ubuntu without it).
- Phase 2 drafts proposals in this shape; Phase 4 publishes the v2 registry file with this publisher.
- Working tree holds unrelated modified and untracked files: stage by explicit path only.

</code_context>

<specifics>
## Specific Ideas

- The free-text rule `absence_of_evidence` must be rejected by the v2 validator, as it is by v1.0.0.
- State names mirror the request wording one for one: rule published, no rule will be published, not yet decided.
- The semantics must be readable without any other source: how conditions combine, what a satisfied rule yields, what an unmet rule yields, what "no rule" yields, and that `UNKNOWN` never yields not-applicable.

</specifics>

<deferred>
## Deferred Ideas

- "Or" between condition lists (alternative condition lists per control) — not supported in 2.0.0; revisit if a later control needs it.
- Rule conditions over `owner`, `tier`, `service_criticality`, `data_classification`, each with an approved meaning — future authority version.
- Shared helper module for the v1 and v2 publishers — out of scope (general hardening).

</deferred>

---

*Phase: 1-Rule Shape and Decision States*
*Context gathered: 2026-10-13*
