# Phase 3: Governance Decisions - Research

**Researched:** 2026-10-13
**Domain:** Hand-authored governance decision records over a frozen proposals file (Python 3.12, jsonschema, pytest). No new libraries.
**Confidence:** HIGH (everything is local code and files read in this session; no external docs needed)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Dispositions are given through a worksheet, not chat. Two files: a generated, read-only Markdown view of the proposals, and a separate small JSON answers file with one entry per control.
- **D-02:** The answers JSON is what gets validated and committed. The committed, filled answers file is the evidence of the authority's decisions.
- **D-03:** The Markdown view is complete and neutral: all 21 in ascending control order, each showing every drafted field verbatim (`catalog_inputs`, `interpretation`, `proposed_outcome`, `proposed_rule`, `rationale`, `confidence`, `alternative_considered`, `shape_limitation`). No ranking, highlighting, grouping, index or summary.
- **D-04:** Every control needs a disposition and a short note in the authority's own words, including when approved as drafted. The validator rejects an empty note and identical notes repeated across controls.
- **D-05:** The validator refuses the answers file until all 21 entries are individually filled. No instruction or value approves all 21 at once (`APPROVE_ALL_AS_PREPARED` is not available).
- **D-06:** No AI agent contributes to the answers. The answers file starts with all 21 entries blank. No agent pre-fills, suggests a disposition, or writes or rewords a note. Agents only generate the view, run the validator and report its error messages. The decision file states that the answers were typed by the authority.
- **D-07:** Every one of the 21 ends as a rule or as no-rule. A rejection cannot leave a control `NOT_YET_DECIDED`.
- **D-08:** Dispositions are defined by outcome and the validator checks each against the decided outcome: Approved as drafted = drafted outcome, rule and rationale all stand. Changed = same outcome kind, but the rule's conditions or the rationale text altered. Rejected = outcome flips to the other kind.
- **D-09:** For changed or rejected, the authority types the decided rule (field/state pairs) and decided rationale himself. No agent drafts or rewords them.
- **D-10:** A decided rule must pass the Phase 1 rule shape. The validator reports shape errors; it does not correct them.
- **D-11:** For an approved proposal, the decided text is the drafted text copied verbatim by the tooling. The record shows drafted and decided text for every control (same layout for changed and approved).
- **D-12:** Committed answers and decision records are frozen. A change of mind is a new decision record with a new `AA4-GOV` id that names the decision it supersedes; the old record stays. Phase 4 publishes only the latest unsuperseded decision per control.
- **D-13:** One registry JSON file holds all decision records (21 at first).
- **D-14:** Ids in ascending control order: `AA4-GOV-001` = EMS-CTRL-009 ... `021` = EMS-CTRL-079. A superseding decision takes the next free number (`022` onward). One id decides one control.
- **D-15:** Each record carries `approver: Oscar Mack`, `approver_roles: [EMS_GOVERNANCE_AUTHORITY, HAYES_VERIFY_DEVELOPER]`, and the same `dual_role_statement` in every record; the schema requires both.
- **D-16:** Sentence: "Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it." Governance content: Oscar Mack approves the exact final sentence before it is committed.
- **D-17:** The decision file states once, in its header, that the deciding authority knew the per-control result of an earlier assessment when deciding, that the drafts were written without that knowledge, and that no rule was compared with a target during this phase. Each record points to that header statement. The header does not name the assessment. Wording approved by Oscar Mack before commit.
- **D-18:** A decision is reasoned from the control and the approved field definitions only. Notes, rationales and records must not name the assessed repository or use its result as a reason.
- **D-19:** A pytest scans the answers file and the decision records file, case-insensitive, for a fixed term list (assessed repository's name, its commit SHA and short form, the assessment date, the refusal code). The term list lives in the test. "Hayes Verify" is allowed.
- **D-20:** Each record cites the drafting record and drafting commit SHA `dc3b41c9fbb3571a191d2da5164fb73439a0637b`.
- **D-21:** Six drafts carry a `shape_limitation` (EMS-CTRL-022, 030, 042, 052, 062, 075). For each, the authority's answer must say whether he accepts the note as a true limitation of this version. The record carries the drafted note and the ruling. The validator requires the ruling on exactly these six.
- **D-22:** The four approved field definitions are not reworded, extended or given binding readings. If a definition does not safely cover a case, reject the rule and decide no-rule.
- **D-23:** Where a decision turns on how a definition was read (052 / `ai_enabled`), the note says how he read it, labelled as the reason for this decision only.
- **D-24:** Each record carries the drafted `interpretation` and states the authority accepted it as the basis of this applicability decision only. `registry/control_catalog.yaml` is not changed. Disagreement = change or rejection with his own reading in the note.

### Claude's Discretion
- File names/locations for view, answers file, decision records, schema, builder/validator script and tests (snake_case, `archive_assessment_*`, tracked, not under gitignored `generated/`).
- Exact JSON key names and enum values (disposition, scope-note ruling, supersession field), consistent with decisions and AA2 per-decision layout where it fits.
- How records are built from proposals plus answers (`build_*`/`validate_*` pair) and which digests each record/header carries.
- Date/timestamp fields on a record.
- Commit order of tooling, view, blank answers, filled answers, records, provided: tests never red in between (blank answers must not fail the suite); filled answers committed before or with records built from them; every commit contains only this project's files, staged by explicit path.
- How "identical notes" is tested (normalised exact match is the floor).
- Whether the request id may appear in the decision file.
- How the two approved wordings (D-16, D-17) are put to the authority and how sign-off is recorded.
- How the human gate is expressed in the plan (blocking checkpoint).

### Deferred Ideas (OUT OF SCOPE)
- Expressing control scope or target type in a rule condition (future authority version).
- Binding readings of a classification field / rewording a field definition.
- An approved interpretation becoming the control's definition or catalog descriptions.
- Leaving a rejected control `NOT_YET_DECIDED`.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GOV-01 | Authority approves/changes/rejects each of the 21 individually | Answers file with 21 entries, per-entry disposition + note, no bulk value, copy-paste guard, outcome-vs-disposition check (Patterns 1, 2) |
| GOV-02 | Each outcome recorded as governance decision with unique id | `AA4-GOV-NNN` ids by position, pattern reuse of `V2.AUTHORITY_ID_RE`, supersession field (Pattern 3) |
| GOV-03 | Each record states approver holds both roles | `approver_roles` const + `dual_role_statement` const in schema and validator; mutation tests (Pattern 3, Validation) |
| GOV-04 | Machine-readable and schema-validated | Code-emitted schema + `validate_*` raising `AuthorityError`, same two-layer check as proposals validator (Pattern 4) |
</phase_requirements>

## Summary

Nothing external needs to be learned. The phase is tooling plus one human gate, and every building block already exists in the repo. `scripts/validate_archive_assessment_rule_proposals.py` is the template: load hand-authored JSON, accumulate errors, raise `AuthorityError`, emit the schema from code, and a CLI with `--validate` / `--emit-schema`. `V2.validate_rule(cid, rule, errors)` is imported (via `importlib.util.spec_from_file_location`, because the v2 publisher is not a package module) for D-10. The v2 module already defines `AUTHORITY_ID_RE = r'^AA4-GOV-[0-9]{3}$'`, `RULE_FIELDS` (the four usable fields), `CONDITION_STATES`, `COMBINATION`, `load`, `dump`, `digest`, `contains_absolute`.

The hard part is the sequencing, not the code. The authority must type 21 answers by hand outside the session. Plans must therefore: (1) build and commit tooling, the neutral view and a blank answers template with the suite green; (2) get written sign-off on the D-16 and D-17 wordings; (3) stop at a blocking `checkpoint:human-action`; (4) after the authority reports the file filled, run the strict validator, build the decision records, validate them, commit answers then records. Phase 2 state verified this session: drafting commit `dc3b41c9fbb3571a191d2da5164fb73439a0637b` is an ancestor of HEAD, and the SHA-256 of the proposals file on disk (`31684001ba35...a9886d`) equals `proposals_sha256` in the drafting record [VERIFIED: git merge-base, sha256 of working file].

**Primary recommendation:** One script `scripts/build_archive_assessment_governance_decisions.py` with `view`, `validate-answers` (strict), `build`, `validate`, `emit-schema` modes; two schemas (answers, decisions); a lenient "template" check so a blank answers file keeps pytest green; the strict check is a CLI/gate step and a test that runs only against the filled file once the decisions file exists.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Disposition decisions | Human (authority) | — | Cannot be drafted; D-06 |
| Neutral Markdown view | Script (generator) | — | Pure render of frozen proposals, written under tracked path |
| Answers validation | Script (`validate_*`) | JSON schema | Fail closed, errors reported not corrected |
| Record building | Script (`build_*`, pure) | — | proposals + answers -> records; deterministic |
| Schema | Emitted from code (`schema()`) | file in `schemas/` | Repo pattern; hand edits would drift |
| Invariants/mutation/term-scan | pytest | — | Success criteria 3, 4 and D-19 |

## Standard Stack

Existing stack only. No new package is installed, so the Package Legitimacy Audit is not applicable (no installs).

| Library | Version (installed) | Purpose |
|---------|---------------------|---------|
| Python | 3.12.10 | scripts [VERIFIED: python --version] |
| jsonschema | 4.26.0 | `Draft202012Validator` [VERIFIED: pip list] |
| pytest | 8.4.2 | tests [VERIFIED: pip list] |
| stdlib `hashlib`, `json`, `re`, `subprocess`, `importlib.util` | — | digests, ancestor check, loading V2 |

**Alternatives rejected:** a new pydantic/dataclass layer (not used in repo); markdown templating via Jinja2 (overkill, and a view with no logic is safer as a plain string join so nothing steers).

## Architecture Patterns

### Flow
```
frozen proposals (dc3b41c) --> view generator --> docs/*_VIEW.md (read-only, neutral)
                         \
blank answers template  --> [HUMAN GATE: authority types 21 entries] --> filled answers
filled answers + proposals + drafting record --> validate_answers (strict) --> build_decisions --> validate_decisions + schema --> registry/..._governance_decisions.json
```

### Recommended files (discretion; tracked paths)
```
scripts/build_archive_assessment_governance_decisions.py   # view/validate-answers/build/validate/emit-schema
registry/archive_assessment_governance_answers.json        # blank 21 entries first; authority edits
registry/archive_assessment_governance_decisions.json      # 21 records + header
schemas/archive_assessment_governance_answers.schema.json
schemas/archive_assessment_governance_decisions.schema.json
docs/ARCHIVE_ASSESSMENT_RULE_PROPOSALS_VIEW.md             # generated, header says generated and read-only
tests/test_archive_assessment_governance_decisions.py
```
Match the proposals-validator style: single quotes, compact one-line helpers, `from __future__ import annotations`.

### Pattern 1: Answers file shape
A list of entries (not a dict keyed by control) so supersession can append later. Per entry keys, all present from the start with blank values:
`control_id`, `disposition` (`APPROVED_AS_DRAFTED` | `CHANGED` | `REJECTED`), `note`, `decided_rule` (null or rule), `decided_rationale` (null or string), `scope_note_ruling` (null, or `ACCEPTED_AS_TRUE_LIMITATION` | `NOT_ACCEPTED_AS_TRUE_LIMITATION`, required on exactly the six), `decided_on` (date typed by the authority), `supersedes` (null or decision id; only for entries beyond the first 21).
No `all`/bulk key, and the schema uses `additionalProperties: false` so one cannot be added.

Strict validation rules (D-04 to D-10, D-21), per entry versus the proposal with the same `control_id`:
- Approved: `decided_rule` and `decided_rationale` must be null/absent (tooling copies; D-11). Reject authority-typed decided text on approval so the "approved" path cannot silently differ.
- Changed: same kind. Drafted rule -> decided rule present, passes `V2.validate_rule`, and (rule != drafted rule or rationale != drafted rationale). Drafted no-rule -> `decided_rule` null, `decided_rationale` present and != drafted rationale (normalised).
- Rejected: flips kind. Drafted rule -> `decided_rule` null plus `decided_rationale`. Drafted no-rule -> `decided_rule` valid per `V2.validate_rule` plus `decided_rationale`.
- Rationale standard: reuse the 2 to 4 sentence regex from `validate_proposal` (`re.findall(r'[.!?](\s|$)', r.strip())`) on decided rationales. This follows Phase 2 D-27/28 but is not explicitly locked for Phase 3; flag to the planner as a small discretionary choice.
- Note: non-empty after strip; compare normalised (casefold, collapse whitespace) across all entries; any duplicate fails. Recommended extra: also reject a note equal to the drafted rationale or interpretation text (copy-paste guard), and a minimum length (e.g. 20 characters) so "ok" x 18 with trivial variations is caught. Both are inside discretion for D-04's floor.
- Scope ruling required (non-null, valid enum) for 022, 030, 042, 052, 062, 075 and must be null elsewhere. Derive the six from `shape_limitation is not None` in the proposals, and assert they equal the hard-listed six.
- Exactly 21 entries first, each control once; ids are not in the answers file (assigned by position, D-14).

### Pattern 2: Lenient vs strict (keeps tests green)
Blank template: every `disposition` null, notes empty. Provide `validate_answers(a, strict=False)` that checks structure only (keys, control order, 21 unique ids, enums when non-null) and `strict=True` for the gate. pytest asserts the committed answers file passes the lenient check at all times, and runs the strict check plus the build only when the decisions file exists in the tree (or a fixture of synthetic filled answers in `tmp_path`, which is how the build/validate/mutation tests get exercised before the authority answers). Synthetic fixtures must live in the test and be clearly test data; they must never be written to the registry.

### Pattern 3: Decision record (reuse AA2 layout where it fits)
Header: `status` (e.g. `GOVERNANCE_DECISIONS`), `answers_typed_by_authority_statement` (D-06), `earlier_assessment_knowledge_statement` (D-17, approved text, no name), `wording_approval` ({approver, date, scope} like `brief_approval`), `proposals_path` + `proposals_sha256`, `drafting_record_path` + sha256, `drafting_commit` (D-20), `answers_path` + `answers_sha256`, `field_definitions_source` pointer if wanted.
Record: `decision_id`, `control_id`, `disposition`, `decided_outcome` (`RULE_PUBLISHED` | `NO_RULE_WILL_BE_PUBLISHED`, reusing `V2.DECISION_STATES`), `drafted` {outcome, rule, rationale}, `decided` {outcome, rule, rationale} (full copies for all three dispositions; D-11), `interpretation` {drafted text, `accepted_as_basis_of_this_decision_only: true`} (D-24), `note`, `scope_note` {drafted_note, ruling} or null, `approver`, `approver_roles`, `dual_role_statement`, `decided_on`, `drafting_commit`, `drafting_record_path`, `header_statement_ref` (e.g. a fixed key name pointing at the header field), `supersedes` (null or id), `amendment_present` (true when drafted != decided). Phase 4 needs: decision state, rule or null, id, and "latest unsuperseded per control", so keep `supersedes` a decision id and validate that it names an existing earlier record for the same control and that at most one record per control is unsuperseded.

Roles constant: schema `approver_roles` as `{"type":"array","const":["EMS_GOVERNANCE_AUTHORITY","HAYES_VERIFY_DEVELOPER"]}` and `dual_role_statement` as `const` of the approved sentence. Because the sentence is a constant in the script, it must not be committed in a final form until the authority signs off (D-16).

### Pattern 4: Two-layer check
Follow `--validate`: `validate_decisions(d)` (raises `AuthorityError`, checks semantics the schema cannot: ids sequential by control order, outcome-vs-disposition, digests match files, drafted text equals live proposals, ancestor/containment of the drafting commit) then `jsonschema.Draft202012Validator(load(SCHEMA)).validate(d)`. Success criterion 4 needs both layers to fail on a removed `dual_role_statement`, `decision_id`, `disposition` or `control_id`: the schema via `required`, the validator via exact key set.

### Pattern 5: Neutral view
Render with plain string joins in proposal order (already ascending). Print each field verbatim, same layout for rule and no-rule and for all 21; do not sort by outcome, do not print counts, do not bold or reorder `PROPOSE_RULE`. Render `proposed_rule` as the same JSON dump used for the file. Test: view contains every drafted string of every field, contains no count/summary words, and is byte-identical on regeneration. The view is derived and written at a tracked `docs/` path (not `generated/`, which is gitignored [VERIFIED: .gitignore]).

### Anti-Patterns
- Pre-filling or generating any note, disposition or decided text (D-06). The template builder emits only blanks/nulls.
- Mutating the proposals, drafting record, approved field definitions or catalog.
- Blanket value such as `APPROVE_ALL`. Do not add one even as a test fixture value.
- Importing the AA2 closure scripts or the untracked `generated/` AA2 files; only mirror the layout.
- Re-implementing `validate_rule`.

## Don't Hand-Roll

| Problem | Use Instead | Why |
|---------|-------------|-----|
| Rule shape check | `V2.validate_rule` | Phase 1 single source of truth |
| Id pattern | `V2.AUTHORITY_ID_RE` | already `^AA4-GOV-[0-9]{3}$`; excludes AA1-GOV by construction |
| Hash/dump/load | `V2.digest/dump/load` | deterministic output (`indent=2, sort_keys=True` + newline) |
| Absolute path guard | `V2.contains_absolute` | registry rule |
| Commit ancestry | `git merge-base --is-ancestor`, `git cat-file -e <sha>:<path>` as in `tests/test_archive_assessment_rule_proposals_record.py` | pattern already tested (needs a `needs_git` skip for shallow clones) |

## Common Pitfalls

1. **Blank answers turn the suite red.** A strict check against the committed blank template fails. Use lenient mode in the always-run test; strict only against the filled file / synthetic fixtures.
2. **Line endings and the answers digest.** `core.autocrlf=true`, no `.gitattributes` [VERIFIED]. The authority's editor may save CRLF; hashing raw bytes then differs between Windows working tree and CI checkout. Compute `answers_sha256` over bytes with `\r\n` replaced by `\n`, or have the build rewrite the committed answers canonically only if the authority consents (do not rewrite his file otherwise). Record which normalisation is used. The proposals digest is verified against the raw file and currently matches because that file is LF.
3. **Hand-edited JSON that is not valid JSON.** The authority edits by hand; a stray comma gives a `JSONDecodeError`. Catch it and report line/column as an `AuthorityError` message; the agent reports it but does not fix his file (D-06). Consider also accepting that the template contains no comments (JSON has none), so keep any guidance in the view or a sibling instruction line in the plan, not in the answers file.
4. **Term scan false positives.** The Phase 2 list contains `Hayes` and `DEMO3-W1-REQ-001` [VERIFIED: tests/test_archive_assessment_rule_proposals.py line 12]. Phase 3 must drop `Hayes` (the dual-role statement and role enum `HAYES_VERIFY_DEVELOPER` require it). Keep: `RiskMVP`, `42aa362c76980a934fbaa470e603b48c7ef4b0b7`, `42aa362`, `2026-10-01`, `EMS_NOT_APPLICABLE_RULE_ABSENT`. Scan file names too. Request id `DEMO3-W1-REQ-001` is neither target nor result; the discretion call is to leave it out of these files (simplest, and the Phase 2 scan precedent forbids it in drafting files). Also scan the new script source and the view. SHA-256 digests could in theory contain `42aa362` (about 1 in 2.7e8 per position); if it ever happens, it is a coincidence, not a leak.
5. **Wording drift of the approved sentences.** Compare `dual_role_statement` and the D-17 header text by exact equality with constants; the authority-approved text is only final after sign-off, so keep constants in one place and gate the first commit containing them on the sign-off checkpoint.
6. **Supersession logic bugs.** Ids by position: appended entries get 022+, never reused or reordered. Validate no cycles, same control, target earlier, no two unsuperseded records per control. Phase 4 consumes "latest unsuperseded".
7. **Staging.** Working tree has `M registry/adjudication_rules.json`, `M registry/policy_decisions.json` and about 60 untracked files [VERIFIED: gitStatus]. Use `git add <explicit path>` only; verify with `git diff --cached --name-only` before each commit. Never `git add -A`, `.` or `-a`.
8. **Records built before answers committed.** Order: answers commit first (or same commit), then records, since the records carry `answers_sha256`. Do not regenerate the answers after building.
9. **Phase 2 files are frozen.** A test (or the build step) should assert the proposals file and drafting record are unchanged at HEAD versus commit `dc3b41c`/their recorded digests; and `git diff --quiet` on them in the execution checks. Success criterion 5 is satisfied by never touching them: the changed record carries drafted text copied from the proposals file plus the authority's decided text.
10. **"Changed" with no real change.** Compare normalised rule (set of field/state pairs; order shouldn't matter semantically) and rationale; equality on both means the authority must pick Approved. Note that Approved vs Changed compare by pairs, so a reordered-but-identical rule counts as unchanged.
11. **Rationale reuse for rule rejection.** A rejected rule becomes no-rule with a new rationale; records must not retain the drafted rule as decided (decided rule null).

## Code Examples

```python
# Load V2 the same way the proposals validator does [VERIFIED: scripts/validate_archive_assessment_rule_proposals.py]
_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(V2)
AuthorityError = V2.AuthorityError
```

```python
def decided_kind(entry, proposal):  # D-08 check sketch
    drafted_rule = proposal['proposed_outcome'] == 'PROPOSE_RULE'
    d = entry['disposition']
    decided_rule = drafted_rule if d != 'REJECTED' else not drafted_rule
    return decided_rule  # then entry['decided_rule'] must be non-null iff decided_rule, via V2.validate_rule
```

```python
# Mutation test shape (success criterion 4)
@pytest.mark.parametrize('key', ['dual_role_statement', 'decision_id', 'disposition', 'control_id'])
def test_removing_required_key_fails(key):
    d = copy.deepcopy(built_from_synthetic_answers()); del d['records'][0][key]
    with pytest.raises(MODULE.AuthorityError): MODULE.validate_decisions(d)
    with pytest.raises(jsonschema.ValidationError): jsonschema.Draft202012Validator(MODULE.schema()).validate(d)
```

Additional tests to plan: 21 records, ids `AA4-GOV-001..021` in control order and none in `AA1-GOV-001..008`; each record cites `dc3b41c9...` and the sha is an ancestor of HEAD and contains the proposals path; `approver_roles` exact; identical-note rejection; blanket-value rejection; disposition/outcome mismatch cases (approved with a changed rule, changed that flips kind, rejected that keeps kind); decided rule with `owner`, `UNKNOWN`, repeated field, empty conditions; scope ruling present on exactly six; changed record carries drafted and decided text; term scan on answers/decisions/view/script; frozen-input test; deterministic rebuild equals file bytes; no absolute paths; the real committed answers pass lenient mode.

## State of the Art

Not applicable (internal tooling). One precedent change: AA2 used a single blanket `approval_instruction`; this phase deliberately has per-control dispositions only (D-05).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Applying the 2 to 4 sentence rationale rule to decided rationales | Pattern 1 | Authority's typed rationale rejected unexpectedly; relax to non-empty if he objects |
| A2 | Min note length and note-equals-drafted-rationale guard are acceptable additions to D-04 | Pattern 1 | Over-strict validation annoys the authority; both are easy to drop |
| A3 | Leaving the request id out of the decision files | Pitfall 4 | None functionally; Phase 5 reply carries it |
| A4 | Hashing the answers file after CRLF->LF normalisation | Pitfall 2 | Digest mismatch across platforms if raw bytes are used instead |
| A5 | Key and enum names in Patterns 1 and 3 | Patterns | Naming only; planner may rename consistently |

## Open Questions

1. **Who types `decided_on` and where is the sign-off for the D-16/D-17 wordings recorded?**
   - Recommendation: the authority types `decided_on` per entry; the sign-off goes into a `wording_approval` header object (approver, date, scope) filled after the checkpoint where he confirms the two sentences in writing in-session. The plan should present the exact text of both constants at that checkpoint.
2. **Does the strict check need to run in CI?** Recommendation: no extra CI hook; the always-run pytest covers the lenient check and, once the decisions file exists, the strict one.

## Environment Availability

| Dependency | Required By | Available | Version |
|------------|------------|-----------|---------|
| Python | scripts/tests | yes | 3.12.10 |
| jsonschema | schema check | yes | 4.26.0 |
| pytest | tests | yes | 8.4.2 |
| git (full history, not shallow) | ancestor test | yes (dc3b41c is an ancestor of HEAD) | — |

No missing dependencies.

## Validation Architecture

Skipped: Nyquist validation is disabled for this project. (Test plan is nonetheless listed under Code Examples; framework is pytest, run `python -m pytest tests/test_archive_assessment_governance_decisions.py -q`.)

## Security Domain

Low relevance (local governance files, no network, no secrets). Applicable controls: input validation of hand-edited JSON (schema + validator, fail closed), no absolute paths in registry JSON, no execution of file content, git commands called with fixed argument lists (no shell). Integrity: SHA-256 digests tie records to the answers, proposals and drafting record. Authenticity of "typed by the authority" cannot be technically enforced; it is a stated claim in the file (D-06) and should be described as such, not as a verified fact.

## Project Constraints (from CLAUDE.md)

- Python 3.12, `jsonschema`, PyYAML, pytest; Windows-primary; match existing style (single quotes, compact helpers in `publish_*`/validator-style scripts; `from __future__ import annotations`; `pathlib.Path`; explicit `encoding='utf-8'`).
- Deterministic JSON `json.dumps(value, indent=2, sort_keys=True) + '\n'`; no absolute paths in registry JSON; fail closed via `AuthorityError`; unknown never resolves to not-applicable.
- `build_*` pure / `validate_*` raising pair; schema emitted from code.
- Rule vocabulary only the four usable fields and `KNOWN_TRUE`/`KNOWN_FALSE`.
- Oscar Mack is the only approving authority; dual role written into every record; nothing from Hayes adopted into EMS.
- Scope is the 21 controls; the other 59 untouched. Unrelated uncommitted work stays out of commits; stage by explicit path.
- Work through a GSD command (direct repo edits outside GSD are not allowed).

## Sources

### Primary (HIGH confidence, all read in this session)
- `registry/archive_assessment_not_applicable_rule_proposals.json` (21 proposals; 18 no-rule, 3 rule; six shape limitations)
- `registry/archive_assessment_rule_proposals_drafting_record.json`
- `scripts/validate_archive_assessment_rule_proposals.py`, `scripts/publish_archive_assessment_applicability_authority_v2.py`
- `tests/test_archive_assessment_rule_proposals.py` (term list), `tests/test_archive_assessment_rule_proposals_record.py` (git helpers)
- `generated/archive-assessment/ems-aa2/approval/archive_assessment_applicability_governance_approval.json` (AA2 layout)
- `.gitignore`, git config (`core.autocrlf=true`, no `.gitattributes`), `git merge-base --is-ancestor`

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH (existing, installed, verified)
- Architecture: HIGH (direct analog exists)
- Pitfalls: HIGH for local ones (CRLF, staging, term list); MEDIUM for naming choices

**Research date:** 2026-10-13
**Valid until:** 30 days (stable; invalid if Phase 1/2 files change)
