# Phase 3: Governance Decisions - Context

**Gathered:** 2026-10-13
**Status:** Ready for planning

<domain>
## Phase Boundary

The EMS governance authority (Oscar Mack) personally gives an individual disposition (approved as drafted, changed, or rejected) for each of the 21 draft proposals, and each outcome becomes a machine-readable, schema-validated governance decision record with its own `AA4-GOV-NNN` id, a dual-role statement and a citation of the Phase 2 drafting commit (GOV-01..04).

This phase delivers: a read-only view of the 21 drafts, an answers file that the authority fills in by hand, a validator for it, the decision records file with its schema, builder/validator script and tests. It writes no v2 authority registry file, no certification, no manifest and no reply. It does not edit the frozen proposals file, the drafting record, the approved field definitions or the control catalog. No rule is compared with any target.

**Human gate:** the phase cannot finish on drafting judgment. Execution stops until the authority has filled in all 21 answers himself.

</domain>

<decisions>
## Implementation Decisions

### How the 21 dispositions are given
- **D-01:** Dispositions are given through a worksheet, not through chat answers. Two files: a generated, read-only Markdown view of the proposals, and a separate small JSON answers file with one entry per control.
- **D-02:** The answers JSON is what gets validated and committed. The committed, filled answers file is the evidence of the authority's decisions.
- **D-03:** The Markdown view is complete and neutral: all 21 in ascending control order, each showing every drafted field verbatim (`catalog_inputs`, `interpretation`, `proposed_outcome`, `proposed_rule`, `rationale`, `confidence`, `alternative_considered`, `shape_limitation`). The tooling adds no ranking, highlighting, grouping, index or summary of its own.
- **D-04:** Every control needs a disposition and a short note in the authority's own words, including when the disposition is approved as drafted. The validator rejects an empty note and rejects identical notes repeated across controls.
- **D-05:** The validator refuses the answers file until all 21 entries are individually filled. There is no instruction or value that approves all 21 at once (the AA2 `APPROVE_ALL_AS_PREPARED` precedent is not available).
- **D-06:** No AI agent contributes to the answers. The answers file starts with all 21 entries blank. No agent pre-fills, suggests a disposition, or writes or rewords a note. Agents only generate the view, run the validator and report its error messages. The decision file states that the answers were typed by the authority.

### Changed and rejected
- **D-07:** Every one of the 21 ends as a rule or as no-rule. A rejection cannot leave a control `NOT_YET_DECIDED`. (Phase 4 publishes 21 decided and 59 undecided, unchanged.)
- **D-08:** The three dispositions are defined by outcome, and the validator checks each against the decided outcome:
  - **Approved as drafted:** drafted outcome, drafted rule and drafted rationale all stand.
  - **Changed:** same outcome kind (a rule stays a rule, no-rule stays no-rule), but the rule's conditions or the rationale text are altered.
  - **Rejected:** the outcome flips to the other kind. Rejecting a drafted rule means deciding no rule; rejecting a drafted no-rule means supplying a rule.
- **D-09:** For a changed or rejected proposal, the authority types the decided rule (field/state pairs) and the decided rationale into the answers file himself. No agent drafts or rewords them.
- **D-10:** A decided rule must pass the Phase 1 rule shape (flat list, all conditions must match, at least one condition, the four usable fields, `KNOWN_TRUE`/`KNOWN_FALSE` only, no repeated field). The validator reports shape errors; it does not correct them.
- **D-11:** For an approved proposal, the decided text is the drafted text copied verbatim by the tooling. The record shows both drafted and decided text for every control, so a changed record and an approved record have the same layout.
- **D-12:** Committed answers and committed decision records are frozen, like the proposals file. A change of mind before publication is a new decision record with a new `AA4-GOV` id that names the decision it supersedes; the old record stays in the file. Phase 4 publishes only the latest unsuperseded decision per control.

### Record contents and ids
- **D-13:** One registry JSON file holds all decision records (21 at first).
- **D-14:** Ids are issued in ascending control order: `AA4-GOV-001` = EMS-CTRL-009, `002` = 010, ... `021` = EMS-CTRL-079. A superseding decision takes the next free number (`022` onward). One id decides one control.
- **D-15:** Each record carries a fixed dual-role sentence and structured role fields; the schema requires both, so removing either fails validation:
  - `approver`: `Oscar Mack`
  - `approver_roles`: `EMS_GOVERNANCE_AUTHORITY`, `HAYES_VERIFY_DEVELOPER`
  - `dual_role_statement`: the same approved sentence in every record
- **D-16:** The sentence selected in discussion is: "Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it." It is governance content: the exact final sentence is approved by Oscar Mack before it is committed (same handling as the Phase 1 field definitions).
- **D-17:** The decision file states once, in its header, that the deciding authority knew the per-control result of an earlier assessment when deciding, that the drafts were written without that knowledge, and that no rule was compared with a target during this phase. Each record points to that header statement. The header refers to "an earlier assessment" without naming it. The wording is governance content and is approved by Oscar Mack before it is committed.
- **D-18:** A decision is reasoned from the control and the approved field definitions only. Notes, decided rationales and records must not name the assessed repository or use its result as a reason.
- **D-19:** A pytest scans the answers file and the decision records file, case-insensitive, for a fixed term list: the assessed repository's name, its commit SHA and short form, the assessment date, and the refusal code. The term list lives in the test, not in the scanned files. "Hayes Verify" is allowed in these files because the dual-role statement requires it.
- **D-20:** Each record cites the drafting record and the drafting commit SHA `dc3b41c9fbb3571a191d2da5164fb73439a0637b` (roadmap success criterion 2; Phase 2 D-24).

### The drafter's open points
- **D-21:** Six drafts carry a `shape_limitation` scope note (EMS-CTRL-022, 030, 042, 052, 062, 075). For each of these, the authority's answer must also say whether he accepts the note as a true limitation of this version. The record carries the drafted note and that ruling. The validator requires the ruling on exactly these six.
- **D-22:** The four approved field definitions are not reworded, extended or given binding readings in this phase. A decision is made within the definition as written. If the authority judges that a definition as written does not safely cover a case, the rule is rejected and the control is decided as no rule.
- **D-23:** Where a decision turns on how a definition was read (the 052 draft asks whether `ai_enabled` covers AI-assisted authoring), the authority's note says how he read it. That reading is labelled as the reason for this decision only and is not a change to the definition.
- **D-24:** Each record carries the drafted `interpretation` and states that the authority accepted it as the basis of this applicability decision only. It does not become the definition of the control, and `registry/control_catalog.yaml` is not changed. If the authority disagrees with the reading, that is a change or a rejection, with his own reading given in the note.

### Claude's Discretion
- File names and locations for the Markdown view, the answers file, the decision records file, its schema, the builder/validator script and the tests (snake_case, matching the `archive_assessment_*` naming; tracked, not under gitignored `generated/`).
- Exact JSON key names and enum values (disposition values, scope-note ruling values, supersession field), consistent with the decisions above and with the AA2 per-decision layout where it fits.
- How records are built from the frozen proposals plus the answers (a `build_*`/`validate_*` pair), and which digests each record or the header carries (proposals SHA-256, answers SHA-256, drafting record).
- What date or timestamp fields a record carries.
- Commit order of tooling, view, blank answers, filled answers and records, provided: tests do not sit red in between (a blank answers file must not make the suite fail before the authority has answered); the filled answers are committed before or with the records built from them; every commit contains only this project's files, staged by explicit path.
- How "identical notes" is tested (exact match after whitespace/case normalisation is the floor).
- Whether the request id may appear in the decision file (it is neither the target nor its result).
- How the two approved wordings (D-16, D-17) are put to the authority for sign-off, and how that sign-off is recorded.
- How the human gate is expressed in the plan (a blocking checkpoint where execution stops until the authority reports the answers file is filled).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and requirements
- `.planning/PROJECT.md` — constraints (authority, dual role, vocabulary, boundary, working tree), key decisions, the 21 controls
- `.planning/REQUIREMENTS.md` — GOV-01..04 for this phase; PUB-01, PUB-04 for what Phase 4 expects from the records
- `.planning/ROADMAP.md` — Phase 3 success criteria and human gate, ordering guarantees, "Notes for Planning" (AA2 precedent, commit SHA note, working tree)
- `.planning/STATE.md` — blockers/concerns (blanket approval does not satisfy GOV-01; stage by explicit path only)

### Inputs to the decisions (frozen, read-only)
- `registry/archive_assessment_not_applicable_rule_proposals.json` — the 21 drafts: 18 `PROPOSE_NO_RULE`, 3 `PROPOSE_RULE` (030 and 039 on `production` `KNOWN_FALSE`; 052 on `ai_enabled` `KNOWN_FALSE`); six `shape_limitation` notes; `drafting_frame` with the field definitions and resolution semantics
- `registry/archive_assessment_rule_proposals_drafting_record.json` — drafting commit, digests, drafter statement; cited by every decision record
- `docs/ARCHIVE_ASSESSMENT_RULE_DRAFTER_BRIEF.md` — the approved brief the drafts were written from (rationale standard, posture)

### Rule shape and prior phase decisions
- `.planning/phases/01-rule-shape-and-decision-states/01-CONTEXT.md` — D-01..D-16: rule shape, usable fields, decision states, `AA4-GOV-NNN` pattern, authority carries the decision id for both decided outcomes
- `.planning/phases/01-rule-shape-and-decision-states/01-FIELD-DEFINITIONS.md` — the four approved field definitions (not to be altered, D-22)
- `.planning/phases/02-blind-drafting/02-CONTEXT.md` — D-15 (proposals frozen), D-24 (drafting record), D-25 (term scan pattern), D-27/D-28 (rationale standard; each rationale is the drafted text of its decision record)

### Code to reuse
- `scripts/publish_archive_assessment_applicability_authority_v2.py` — `validate_rule()`, `RULE_FIELDS`, `CONDITION_STATES`, `COMBINATION`, `FIELD_DEFINITIONS`, helpers, `AuthorityError`; the `AA4-GOV-NNN` id pattern in `schema()`
- `schemas/archive_assessment_applicability_authority_v2.schema.json` — what a decided control must look like when Phase 4 publishes it
- `scripts/validate_archive_assessment_rule_proposals.py` — closest analog: hand-authored JSON checked by a validator that also emits its schema
- `tests/test_archive_assessment_rule_proposals.py`, `tests/test_archive_assessment_rule_proposals_record.py` — test style, term-scan test, ancestor-commit test

### Governance precedent (AA2, local and untracked)
- `generated/archive-assessment/ems-aa2/approval/archive_assessment_applicability_governance_approval.json` — per-decision layout (`prepared_text`, `approval_disposition`, `approved_text`, `amendment_present`, `approver`, `approved_at`) is reusable; the blanket `approval_instruction` is not

### Conventions
- `.planning/codebase/CONVENTIONS.md` — naming, code style, error handling, data artifact conventions
- `.planning/codebase/ARCHITECTURE.md` — authority publication flow

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `validate_rule(cid, rule, errors)` in the v2 publisher: checks a decided rule against the Phase 1 shape. Import it; do not re-implement.
- `digest()`, `dump()`, `load()`, `contains_absolute()`, `AuthorityError` helper pattern from the v2 publisher and the proposals validator.
- The proposals validator's structure (load hand-authored JSON, accumulate errors, raise, emit schema from code) fits the answers file and the decision records.
- Phase 2 tests give the pattern for the term-scan test (term list in the test) and for checking that a recorded commit SHA is an ancestor that contains the cited file.

### Established Patterns
- `build_*` (pure) and `validate_*` (raises) pairs so tests can deep-copy, mutate and expect failure. Success criterion 4 needs mutation tests that remove the dual-role statement, the decision id, the disposition and the control id.
- Schema emitted from code by `schema()`; deterministic JSON (`indent=2, sort_keys=True`, trailing newline); no absolute paths in registry JSON.
- New work uses `snake_case.py`, single quotes and compact helpers in `publish_*`-style scripts.

### Integration Points
- Phase 4 builds the v2 authority from the decision records: per control, the latest unsuperseded record gives the decision state, the rule (or null) and the `AA4-GOV` id for `not_applicable_authority`.
- Phase 5 reads the records for the per-control reply, including the scope-note rulings (D-21).
- The answers file is hand-edited by the authority outside the session. Plans need a blocking checkpoint, then validation, then record building.
- Phase 2's term scan forbids "Hayes" in the proposals file, brief and drafting record. The decision files are separate files and are not added to that scan; they get their own scan (D-19).
- Working tree holds unrelated modified and untracked files: stage by explicit path only.

</code_context>

<specifics>
## Specific Ideas

- Record layout selected in discussion:
  ```json
  "approver": "Oscar Mack",
  "approver_roles": ["EMS_GOVERNANCE_AUTHORITY", "HAYES_VERIFY_DEVELOPER"],
  "dual_role_statement": "Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it."
  ```
- The copy-paste guard (D-04) exists so that 18 approvals of no-rule drafts cannot amount to a blanket approval.
- The view must not steer: nothing in it points the authority towards the 3 rules or away from the 18 no-rules.
- "No rule" is a real claim (the control applies to every target), so an approval of a no-rule draft is a decision with a consequence, not a default.

</specifics>

<deferred>
## Deferred Ideas

- Expressing control scope (PLATFORM, SERVICE, ORGANIZATION, APPLICATION, EMS) or target type in a rule condition, so the six scope-limited controls can be decided on their real reason — future authority version; the scope-note rulings (D-21) are the input.
- Binding readings of a classification field published with a rule, or rewording a field definition — declined for this phase (D-22); future authority version if needed.
- An approved interpretation becoming the control's definition, or adding descriptions to the control catalog — declined (D-24); wider than the request.
- Leaving a rejected control `NOT_YET_DECIDED` — declined (D-07); would need PUB-04 and the roadmap amended.

</deferred>

---

*Phase: 3-Governance Decisions*
*Context gathered: 2026-10-13*
