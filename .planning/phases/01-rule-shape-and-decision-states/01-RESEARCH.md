# Phase 1: Rule Shape and Decision States - Research

**Researched:** 2026-10-13
**Domain:** Python authority publisher + JSON Schema (Draft 2020-12) + pytest, in-repo pattern (no new external packages)
**Confidence:** HIGH (all findings come from reading the repo and running the existing tests; one design area, D-10 field definitions, is governance content, not technical)

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** A `not_applicable_rule` holds one flat list of conditions. Each condition is a field/state pair. The rule is satisfied only when every condition matches (logical AND).
- **D-02:** No nesting, no negation, no `ANY`/"or" in this version. A control that would need an "or" is drafted as a narrower single list or as "no rule" (Phase 2 concern; the shape does not accommodate it).
- **D-03:** A rule has at least one condition. An empty (unconditional) rule fails validation.
- **D-04:** Each field appears at most once in a rule. Repeats fail validation (this also excludes contradictory rules).
- **D-05:** The AA2 rule-language proposal (`ALL`, `ANY`, `NOT`, `EQ`, `IN`, `KNOWN`, `UNKNOWN`) is not adopted. It was never approved (`PROPOSED_FOR_APPROVAL`) and is wider than the `KNOWN_TRUE`/`KNOWN_FALSE` constraint.
- **D-06:** A condition state is `KNOWN_TRUE` or `KNOWN_FALSE` only. `UNKNOWN`, any other value, and any free-text rule (for example the string `absence_of_evidence`) fail validation.
- **D-07:** Rule conditions may name only the four yes/no fields: `production`, `internet_exposed`, `contains_customer_data`, `ai_enabled`.
- **D-08:** `owner`, `tier`, `service_criticality` and `data_classification` remain declared classification fields (the eight-field vocabulary and `classification_prerequisites` are unchanged) but are not usable in a rule in this version. A condition naming one of them fails validation, as does any field outside the eight.
- **D-09:** The authority publishes the four rule-condition fields as an explicit list in its semantics block, separate from the eight classification fields, with a statement that the other four are not usable in rules in this version. The restriction is not left to the schema enum alone.
- **D-10:** The authority publishes a short definition for each of the four rule-condition fields, stating what `KNOWN_TRUE` asserts about the target. The wording is governance content: it is drafted in this phase from EMS sources only and must be approved by Oscar Mack before it is committed.
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
- **D-17:** The new shape lives in new versioned files beside v1.0.0: a new publisher, a new schema and a new test. The v1.0.0 publisher, schema, authority, test and manifest are not edited, so v1.0.0 digests stay valid and the existing tests pass unchanged. Some duplicated helper code is accepted.
- **D-18:** The new authority version is `2.0.0` (breaking shape change); the authority id becomes `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0` or equivalent with the 2.0.0 suffix.
- **D-19:** Phase 1 commits publisher code, schema and tests only. Tests exercise all three states with synthetic example controls. No new registry authority file is written until Phase 4, so nothing that looks published exists before the governance decisions.

### Claude's Discretion
- Exact JSON key names inside a condition and for the decision-state field (`not_applicable_decision_state` was used as a working name), matching existing registry naming.
- File names for the v2 publisher, schema and test.
- Whether the semantics are also described in a `docs/` page for readers, in addition to the semantics block.
- How much of D-15 is enforced in JSON Schema (`if`/`then`) versus `validate_*` code; both layers should fail closed.
- How validation errors are worded (follow the existing accumulate-then-raise `AuthorityError` style).

### Deferred Ideas (OUT OF SCOPE)
- "Or" between condition lists (alternative condition lists per control).
- Rule conditions over `owner`, `tier`, `service_criticality`, `data_classification`, each with an approved meaning.
- Shared helper module for the v1 and v2 publishers.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SCHEMA-01 | Schema accepts structured `not_applicable_rule` | Rule object shape + `oneOf [object, null]` (Pattern 1, Code Examples) |
| SCHEMA-02 | Schema accepts `not_applicable_authority` naming a decision id | Pattern `^AA4-GOV-[0-9]{3}$` or null; if/then coupling |
| SCHEMA-03 | Three-valued decision state per control | `not_applicable_decision_state` enum of 3, required on every control |
| SCHEMA-04 | Reject inconsistent combos | JSON Schema `if/then` (three branches) AND `validate_authority` code; mutate-test each |
| SCHEMA-05 | Conditions only declared fields, only KNOWN_TRUE/KNOWN_FALSE | Enum of 4 fields (D-07) in schema + validator; state enum of 2; free text rejected by type |
| SCHEMA-06 | Rule semantics stated in full | Top-level `not_applicable_semantics` block + reference `resolve_applicability()` tested against it |
</phase_requirements>

## Project Constraints (from CLAUDE.md)
- Python 3.12, `jsonschema`, PyYAML, pytest; match existing code style. `publish_*` scripts use single quotes and compact one-line helpers; mirror that in the v2 publisher.
- Fail closed: validators raise `AuthorityError`; UNKNOWN/missing never resolves to NOT_APPLICABLE or PASS.
- Registry JSON must contain no absolute paths (`contains_absolute`); deterministic JSON `json.dumps(v, indent=2, sort_keys=True) + '\n'`; `encoding='utf-8'` explicit.
- `build_*` (pure) / `validate_*` (raises) pairs; `main()` with argparse.
- Follow the authority pattern (schema, publisher script, certification, traceability, pytest). Hash-based certification breaks on uncoordinated hand edits: do not edit v1 files.
- Working tree has unrelated uncommitted work: stage by explicit path only (never `git add -A` / `.`).
- Do not add new `Verb-PascalCase.py` scripts; use `snake_case.py`.
- GSD workflow enforcement: file changes go through GSD execution.

## Summary

The v1.0.0 publisher (`scripts/publish_archive_assessment_applicability_authority.py`, 139 lines) is a single file that does everything: `build_authority()`, `validate_authority()`, `schema()` (hand-written dict emitted to the schema file), and `publish()` (writes registry, schema, generated certification/manifest/traceability). Its constants block the new shape in exactly the places ROADMAP notes list: `version` const `1.0.0`, `not_applicable_rule`/`not_applicable_authority` typed `null`, exactly eight `AA1-GOV-00[1-8]` ids at top level and per control. The 12 existing tests pass today (verified: `12 passed`). Per D-17 the v2 work is a copy-and-adapt into new files; v1 is untouched, so its manifest digests stay valid.

The one non-obvious engineering problem is that v1 `build_authority()` reads `generated/archive-assessment/ems-aa2/approval/archive_assessment_applicability_governance_closure.json`, which is gitignored (`.gitignore` line 6: `generated/`). CI on ubuntu does not have it. The v2 builder should NOT read it. The AA1 manifest, AA2 closure and AA2 approval digests are already recorded in the committed v1 registry file `registry/archive_assessment_applicability_authority.json` (`source_lineage`), so v2 can read lineage from that tracked file (and record `supersedes: v1.0.0 @ 62a8955`) and run anywhere. `registry/control_catalog.yaml` is tracked, so the 80-control population is also CI-safe.

The second design point: JSON Schema cannot express "each `field` appears at most once" across a list of objects, nor the "no short-circuit" semantics. Those belong in `validate_authority` (D-04) and in a pure reference function `resolve_applicability(control, facts)` that tests use to prove each D-12 branch, including the no-short-circuit case. This also makes SCHEMA-06 verifiable rather than prose-only.

**Primary recommendation:** Create `scripts/publish_archive_assessment_applicability_authority_v2.py`, `schemas/archive_assessment_applicability_authority_v2.schema.json` (emitted once from `schema()`), and `tests/test_archive_assessment_applicability_authority_v2.py`; build all 80 controls as `NOT_YET_DECIDED`; enforce D-15 in both JSON Schema `if/then` and validator code; add `resolve_applicability()`; do not write a v2 registry file; gate D-10 field-definition wording behind an Oscar Mack approval checkpoint.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Rule/decision-state schema | Declarative authority layer (`schemas/`) | publisher code (emits it) | Schema is generated from `schema()`; hand edits are overwritten |
| Consistency validation (D-04, D-15) | Publisher `validate_authority()` | JSON Schema `if/then` | Uniqueness and cross-field rules are not fully expressible in schema |
| Resolution semantics (D-12) | Authority semantics block (data) | Reference `resolve_applicability()` in publisher (test oracle) | Readable without other source; executable check keeps prose honest |
| Field definitions (D-10) | Governance content (Oscar approval) | semantics block | Not a technical decision |
| Lineage to v1.0.0 | Tracked v1 registry file | `62a8955` | Avoids gitignored local AA2 file |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.10 local; 3.12 CI | Publisher + tests | Project-pinned [VERIFIED: `python --version`; ems-validate.yml] |
| jsonschema | 4.26.0 installed | `Draft202012Validator` | Already used by v1 publisher [VERIFIED: pip import] |
| PyYAML | 6.0.3 pinned | Read `registry/control_catalog.yaml` | Existing [CITED: CLAUDE.md] |
| pytest | 8.4.2 (from pycache tag) | Tests | Existing [VERIFIED: pycache filename `pytest-8.4.2`] |

No new packages. Package Legitimacy Audit: not applicable (nothing installed). Environment Availability: Python, jsonschema, pytest all present and the baseline suite passes; no other external dependency.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| List of `{field,state}` conditions + validator uniqueness (D-01) | Mapping `{field: state}` | Mapping makes D-04 structural, but D-01 locks the list-of-pairs shape; keep the list |
| Hand-written `schema()` dict | Separate schema file edited by hand | Rejected: hand edits are overwritten; codebase emits schema from code |

## Architecture Patterns

### Data flow
```
registry/control_catalog.yaml (tracked) --\
registry/archive_..._authority.json (v1, tracked; lineage hashes) --> build_authority() [pure, 80 x NOT_YET_DECIDED]
                                                                          |
        test mutators (synthetic RULE_PUBLISHED / NO_RULE / bad combos)  -+--> validate_authority() raises AuthorityError
                                                                          |
                                           schema() --> schemas/..._v2.schema.json (emitted once, committed)
                                                                          |
                          Draft202012Validator(schema()).validate(authority)   [second fail-closed layer]
        resolve_applicability(control, facts) --> APPLICABLE | NOT_APPLICABLE | APPLICABILITY_UNRESOLVED  [test oracle for D-12]
```
`publish()` (registry file, certification, manifest, traceability) is a Phase 4 concern (D-19); Phase 1 must not run it or write `registry/..._v2.json`.

### Recommended file set
```
scripts/publish_archive_assessment_applicability_authority_v2.py
schemas/archive_assessment_applicability_authority_v2.schema.json   # emitted by schema(); committed
tests/test_archive_assessment_applicability_authority_v2.py
docs/ (optional, discretion) AA3_V2_NOT_APPLICABLE_RULE_SEMANTICS.md
```
All stage by explicit path. The registry JSON and generated outputs are not created.

### Recommended key names (discretion; match v1 snake_case style)
- Per control: `not_applicable_decision_state` (enum `RULE_PUBLISHED`, `NO_RULE_WILL_BE_PUBLISHED`, `NOT_YET_DECIDED`), `not_applicable_rule`, `not_applicable_authority`.
- Rule: `{"combination": "ALL_CONDITIONS_MUST_MATCH", "conditions": [{"field": "production", "state": "KNOWN_FALSE"}, ...]}`. The explicit `combination` constant makes AND self-describing in the data rather than convention (SCHEMA-06). Alternative: bare `conditions` array only; but the constant costs nothing and aids readers. `additionalProperties: false` on rule and condition.
- Top-level `not_applicable_semantics` (extends the v1 block, keeps the three v1 booleans) with: `decision_states`, `rule_condition_fields` (the 4), `fields_not_usable_in_rules` (the other 4) plus a statement, `condition_states` (`KNOWN_TRUE`,`KNOWN_FALSE`), `condition_combination: ALL`, `min_conditions: 1`, `field_may_appear_once: true`, `field_definitions` (D-10), `resolution` (the five D-12 rows as structured entries with `decision_state`, `condition`, `result`), `no_short_circuit: true`, `decision_state_governs_resolved_result: true`, `per_control_default_describes_result_absent_a_decision: true`, `unknown_is_never_not_applicable: true`, plus a human-readable `statement` string for each rule.

### Pattern 1: schema with if/then coupling (Draft 2020-12)
```python
# per-control item fragment, emitted from schema()
cond = {'type':'object','additionalProperties':False,'required':['field','state'],
        'properties':{'field':{'enum':RULE_FIELDS},'state':{'enum':['KNOWN_TRUE','KNOWN_FALSE']}}}
rule = {'type':'object','additionalProperties':False,'required':['combination','conditions'],
        'properties':{'combination':{'const':'ALL_CONDITIONS_MUST_MATCH'},
                      'conditions':{'type':'array','minItems':1,'maxItems':4,'items':cond}}}
authority_id = {'type':'string','pattern':'^AA4-GOV-[0-9]{3}$'}
'allOf':[
 {'if':{'properties':{'not_applicable_decision_state':{'const':'RULE_PUBLISHED'}},'required':['not_applicable_decision_state']},
  'then':{'properties':{'not_applicable_rule':rule,'not_applicable_authority':authority_id}}},
 {'if':{'properties':{'not_applicable_decision_state':{'const':'NO_RULE_WILL_BE_PUBLISHED'}},'required':['not_applicable_decision_state']},
  'then':{'properties':{'not_applicable_rule':{'type':'null'},'not_applicable_authority':authority_id}}},
 {'if':{'properties':{'not_applicable_decision_state':{'const':'NOT_YET_DECIDED'}},'required':['not_applicable_decision_state']},
  'then':{'properties':{'not_applicable_rule':{'type':'null'},'not_applicable_authority':{'type':'null'}}}}]
```
Base property types: `not_applicable_rule` and `not_applicable_authority` required on every control; base type `anyOf [object|null]` / `[string|null]`; the decision-state enum is required on every control so an absent state fails (the `required` inside each `if` prevents vacuous match when the property is missing; the control-level `required` list catches absence). `maxItems: 4` plus validator uniqueness bounds the list. A free-text string like `absence_of_evidence` fails because rule must be `object` or `null`.

### Pattern 2: validator (accumulate-then-raise, as v1)
Per control, check: state in the 3 values; `RULE_PUBLISHED` -> rule is dict with `combination` and non-empty list, every item has exactly keys `field`,`state`, `field` in `RULE_FIELDS` (4), `state` in `{KNOWN_TRUE, KNOWN_FALSE}`, no repeated `field`, authority matches `^AA4-GOV-\d{3}$`; `NO_RULE...` -> rule `is None`, authority matches pattern; `NOT_YET_DECIDED` -> both None. Also keep every v1 invariant that still applies (80 unique catalog ids, `default_applicability_result` and `classification_unknown_treatment` remain `APPLICABILITY_UNRESOLVED`, no absolute paths, attestation prohibitions False, evidence boundary, AA1-GOV-001..008 provenance per control, `classification_vocabulary` unchanged). Validate that `not_applicable_semantics` carries the required semantic flags and the exact four `rule_condition_fields`, so weakening the semantics block fails closed (mutation tests).

### Pattern 3: reference resolver (test oracle)
```python
def resolve_applicability(control: dict, facts: dict) -> str:
    st = control['not_applicable_decision_state']
    if st == 'NOT_YET_DECIDED': return 'APPLICABILITY_UNRESOLVED'
    if st == 'NO_RULE_WILL_BE_PUBLISHED': return 'APPLICABLE'
    conds = control['not_applicable_rule']['conditions']
    states = [facts.get(c['field'], 'UNKNOWN') for c in conds]   # missing fact == UNKNOWN
    if any(s not in ('KNOWN_TRUE','KNOWN_FALSE') for s in states): return 'APPLICABILITY_UNRESOLVED'  # no short-circuit
    return 'NOT_APPLICABLE' if all(s == c['state'] for s, c in zip(states, conds)) else 'APPLICABLE'
```
Unreadable/unrecognized fact values map to unresolved (fail closed), never to a match.

### Anti-Patterns to Avoid
- Editing any v1 file (publisher, schema, registry, test, manifest) - breaks digests (D-17).
- Calling v2 `publish()` or writing `registry/..._v2.json` in Phase 1 (D-19).
- Reading the gitignored AA2 closure in the v2 builder (breaks on CI/other machines).
- Implementing short-circuit on a failed known condition when another field is UNKNOWN (D-12 forbids it).
- Letting the schema enum alone carry the four-field restriction (D-09 requires the explicit published list).
- Adding `ANY`/`NOT`/operators (D-02, D-05).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Schema validation | Custom type checkers | `jsonschema.Draft202012Validator` | Existing pattern; `if/then` supported in 2020-12 |
| Hashing / deterministic dump | New helpers | Copy `digest`, `dump`, `load`, `contains_absolute` from v1 | D-17 accepts duplication |
| Control population | Parsing catalog differently | Copy `catalog_controls()` | Same 80-id invariant |

## Common Pitfalls

### Pitfall 1: Vacuous `if` match
**What goes wrong:** `if: {properties: {state: {const: X}}}` matches objects with no `state` key, applying the wrong `then`.
**How to avoid:** include `required: [not_applicable_decision_state]` inside each `if`, and also list it in the control's `required`. Test: control with state key deleted fails.

### Pitfall 2: Schema cannot express field uniqueness
**What goes wrong:** `uniqueItems` compares whole objects; two conditions on `production` with different states pass.
**How to avoid:** enforce in `validate_authority`; test with `[{production:KNOWN_TRUE},{production:KNOWN_FALSE}]` and with an exact duplicate.

### Pitfall 3: Schema only vs validator only
**What goes wrong:** one layer misses a case. **How to avoid:** every negative test should assert both `validate_authority` raises and `Draft202012Validator.validate` raises `jsonschema.ValidationError` for the schema-expressible cases; document that uniqueness/semantics-block cases are validator-only.

### Pitfall 4: v2 builder depends on gitignored file
See Summary. Test must pass with `generated/` absent; verify by running the v2 test with `generated/archive-assessment/ems-aa2` temporarily unreachable is optional, but the builder must simply never open it.

### Pitfall 5: Committed schema drifting from `schema()`
Hand edits or a stale emit. **How to avoid:** a test comparing `json.loads(committed schema file)` to `schema()`; the schema file is emitted once via `python scripts/..._v2.py --emit-schema` (a small flag that writes only the schema file, not the registry). Use `dump()` for deterministic bytes.

### Pitfall 6: Truthiness on `UNKNOWN`
Using `if facts.get(f)` treats `UNKNOWN`/missing as false. Compare against explicit strings only. Test a missing fact and the string `UNKNOWN` and a boolean `False`.

### Pitfall 7: Staging unrelated files
`registry/adjudication_rules.json` and `registry/policy_decisions.json` are modified and ~60 files untracked. Stage the three new files (plus optional doc) by exact path.

## Code Examples
See Patterns 1-3. Test layout mirroring v1:
```python
def invalid(mutator):
    v = copy.deepcopy(build_authority()); mutator(v)
    with pytest.raises(AuthorityError): validate_authority(v)
def rule(*pairs): return {'combination':'ALL_CONDITIONS_MUST_MATCH','conditions':[{'field':f,'state':s} for f,s in pairs]}
def decide(c, state, r, a): c.update(not_applicable_decision_state=state, not_applicable_rule=r, not_applicable_authority=a)
# positive: three states pass validate + Draft202012Validator
# negative (SCHEMA-04): rule w/o authority; NOT_YET_DECIDED with rule; NOT_YET_DECIDED with authority only;
#   RULE_PUBLISHED/NO_RULE with authority None; NO_RULE with a rule; state 'MAYBE'; state missing
# negative (SCHEMA-05): field 'tier' (D-08); field 'region' (outside eight); state 'UNKNOWN'; state 'KNOWN'; rule string 'absence_of_evidence';
#   empty conditions; duplicate field; extra key in condition; authority 'AA1-GOV-001' (wrong pattern); authority 'AA4-GOV-1'
# semantics (SCHEMA-06): drop flags / change rule_condition_fields / unknown_is_never_not_applicable False -> fails
# resolver: 5 D-12 branches + no-short-circuit (production KNOWN_TRUE fails cond, ai_enabled UNKNOWN -> UNRESOLVED) + missing fact
# regression: v1 test file unchanged and passing (run both); v1 registry/schema/publisher bytes unchanged (git diff --quiet 62a8955 -- those paths)
```

## State of the Art
Not a moving domain. JSON Schema Draft 2020-12 `if/then/else` and `unevaluatedProperties` are stable [ASSUMED: from training knowledge; `Draft202012Validator` use is confirmed in v1 code]. The AA2 operator proposal is superseded by D-05.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | JSON Schema 2020-12 `if/then` with `required` in `if` behaves as described under jsonschema 4.26.0 | Pattern 1 | Low; the first test run will show it |
| A2 | Key names `combination`/`conditions`/`field`/`state` | Recommended keys | Low; discretion area, cheap to rename before Phase 2 drafts |
| A3 | `maxItems: 4` on conditions is acceptable given D-04 | Pattern 1 | Low; redundant with uniqueness |
| A4 | pytest is not run in CI (ems-validate.yml only does py_compile and JSON/YAML parse); so the v2 files must py_compile on ubuntu and the schema JSON must parse | Pitfalls | Low |

## Open Questions

1. **Field definitions (D-10) wording**
   - Known: EMS sources only hold example values (`config/repository_overrides.example.yaml`, `registry/wave2d/applicability_rules.json` repository attributes and rule descriptions such as "AI-specific controls apply when ai_enabled=true"). The AA2 vocabulary file lists the fields but gives no definitions and is `PROPOSED_FOR_APPROVAL`. No authoritative definition text was found in tracked EMS sources.
   - Unclear: precise `KNOWN_TRUE` wording per field.
   - Recommendation: planner includes a task that drafts the four definitions citing source paths and a `checkpoint:human-verify` for Oscar Mack approval before commit; the schema/tests must not depend on the wording (only on presence and non-empty string), so code work can proceed and wording is filled after approval.
2. **Top-level `approved_governance_decision_ids` in v2**
   - Known: v1 fixes it to eight AA1 ids; new `AA4-GOV-NNN` ids are issued in Phase 3.
   - Recommendation: keep the eight AA1 ids unchanged at top level and per control (`decision_ids`), and let `not_applicable_authority` carry the AA4 ids; have `validate_authority(a, known_decision_ids=None)` optionally cross-check authority ids against a supplied set (used by Phase 4), pattern-only in Phase 1.
3. **Should v2 `publish()` exist in Phase 1?** Recommend defining `publish()` is deferred; provide only `--validate`-style hooks that fail if the v2 registry file is absent, and `--emit-schema`. Planner decides; either way no registry file is written.

## Validation Architecture
Skipped as a separate section: `workflow.nyquist_validation` is `false` in `.planning/config.json`. Verification commands: `python -m pytest tests/test_archive_assessment_applicability_authority.py tests/test_archive_assessment_applicability_authority_v2.py -q`; `git diff --quiet 62a8955 -- scripts/publish_archive_assessment_applicability_authority.py schemas/archive_assessment_applicability_authority.schema.json registry/archive_assessment_applicability_authority.json tests/test_archive_assessment_applicability_authority.py generated/archive-assessment/ems-aa3` (must exit 0, proves SC-5); `python -m py_compile scripts/publish_archive_assessment_applicability_authority_v2.py`; `git status --short registry/archive_assessment_applicability_authority_v2.json` must show nothing.

## Security Domain
ASVS level 1, no network, auth or user input surface. Relevant: V5 input validation (strict schema with `additionalProperties: false`, enum-only fields/states, regex-anchored ids) and fail-closed semantics (UNKNOWN never maps to NOT_APPLICABLE). Threat: tampering via free-text rule or smuggled extra keys -> rejected by schema and validator; absolute-path leakage -> `contains_absolute` check retained. No secrets, no crypto beyond SHA-256 reuse.

## Sources

### Primary (HIGH confidence, read from repo)
- `scripts/publish_archive_assessment_applicability_authority.py`, `tests/test_archive_assessment_applicability_authority.py` (12 tests pass), `.planning/ROADMAP.md` Notes for Planning, `.gitignore` (generated/ ignored), `.github/workflows/ems-validate.yml`, `git show --stat 62a8955`
- `generated/archive-assessment/ems-aa2/archive_assessment_classification_vocabulary.json` (status `PROPOSED_FOR_APPROVAL`; AA1-GOV-003/004 approved texts)
- `config/repository_overrides.example.yaml`, `registry/wave2d/applicability_rules.json` (field usage; no formal definitions)

### Tertiary (LOW)
- JSON Schema `if/then` semantics from training knowledge (A1).

## Metadata
**Confidence breakdown:** Standard stack HIGH (no new deps); Architecture HIGH (direct code reading); Pitfalls HIGH/MEDIUM (schema-behaviour items are verified by first test run).
**Research date:** 2026-10-13. **Valid until:** 30 days (stable internal code).
