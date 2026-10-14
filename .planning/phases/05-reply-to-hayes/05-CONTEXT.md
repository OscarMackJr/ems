# Phase 5: Reply to Hayes - Context

**Gathered:** 2026-10-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 5 writes the reply to Hayes Verify request `DEMO3-W1-REQ-001` and commits it. It does not send it.

The reply tells Hayes:
- what EMS decided for each of the 21 requested controls;
- which authority, version, commit and digests to cite;
- how to find the rule, the authority and the decision state for a control in the published shape;
- what publication does not change: the 59 controls stay not yet decided, three Hayes-side changes are still needed, and the classification-prerequisites gap is untouched.

The phase does not cover:
- changing the published authority or the v2 publisher (Phase 4);
- hardening the publication checks (a possible v2.0.1);
- deciding any of the other 59 controls (V2-01);
- any Hayes-side change;
- pushing the branch or sending the reply. Both stay with the EMS authority.

Requirements: REPLY-01, REPLY-02, REPLY-03.

</domain>

<decisions>
## Implementation Decisions

### Reply form and source
- **D-01:** The reply has two files with the same content:
  - a Markdown letter for people;
  - a JSON file Hayes can read by machine, listing each of the 21 controls with its decision state, AA4-GOV id and rule (or null).
- **D-02:** Both files are generated from the published authority by a new script, not written by hand.
  - The script has `--build` and `--validate`; `--validate` rebuilds both in memory and requires byte equality with the committed files, like the Phase 4 publisher.
  - A pytest runs the same check, and also fails if any of the 21 entries disagrees with `registry/archive_assessment_applicability_authority_v2.json` (state, AA4 id, rule) or the decision records.
  - Fixed prose (opening, limits, disclosure) may be template text inside the script. Every value taken from the authority (ids, states, rules, SHA, digests, counts) is filled in from the files, never typed.
- **D-03:** Locations follow the repo pattern (docs/<NAME>.md plus registry/<name>.json). Working names:
  - `docs/DEMO3_W1_REQ_001_REPLY.md`
  - `registry/archive_assessment_demo3_w1_req_001_reply.json`
  - a JSON schema in `schemas/`
  - the new script in `scripts/`
  - a test in `tests/`
  Add the new files to the narrow `.gitattributes` as `text eol=lf`, and write them LF-only.
- **D-04:** The reply is written as from the EMS governance authority, Oscar Mack. It stays unsigned in the repo until he sends it; sending is his.

### The commit Hayes pins to
- **D-05:** The pin is the publication commit `54a7fd09114704a97a7a48fce5f89aebeb48c90a`, given as the full SHA, along with the authority id `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0` and version `2.0.0`.
  - The reply also names the publication-record commit `0ce89f2` and says the reply's own commit exists. It states that neither changes the authority.
  - The SHA is read from `registry/archive_assessment_applicability_authority_v2_publication_record.json`, never typed. A test checks that it is an ancestor of HEAD and holds the authority with the recorded digest; reuse the Phase 4 D-21 test approach.
- **D-06:** Before the reply is sent, `54a7fd0` must be on the remote branch, or Hayes cannot reach it.
  - The plan's last step reports the push command (`git push origin feature/ems-aa3-archive-applicability-authority`).
  - A read-only check (for example `git branch -r --contains 54a7fd0` after a fetch, or `git ls-remote`) reports whether the commit is on the remote.
  - The reply notes that it must not be sent until the pin is pushed.
  - Nothing is pushed automatically.
- **D-07:** The reply gives values Hayes can check:
  - the authority LF sha256 (`de36e227be4ccc95f4a8a8a08247cf6e49f7682908c7f425f8cc02bbaa1da353`);
  - the publication manifest digest.
  It says both are computed over CRLF→LF-normalised bytes. All values are read from the publication record and manifest, never typed.
- **D-08:** The reply describes the published shape:
  - the file paths: the registry authority, the v2 schema and the `generated/archive-assessment/ems-aa3-v2/` outputs, including the decision traceability file;
  - the per-control fields `not_applicable_decision_state`, `not_applicable_rule` and `not_applicable_authority`, and the three state values;
  - the top-level `applicability_decision_ids`;
  - that `decision_ids` still carries the eight AA1-GOV ids on every row;
  - one example of a decided row, taken from the authority;
  - where the full meaning of a rule is defined (the semantics block in the authority and the v2 schema).

### Disclosing the review findings
- **D-09:** One short, factual section covers the gaps the Phase 4 review found in the publication checks (`04-REVIEW.md`). It says:
  - the published data was checked independently and is correct, citing `04-VERIFICATION.md`;
  - there are known gaps in the checks that guard publication;
  - the gaps don't change any of the 21 decisions.
  It does not list every finding.
- **D-10:** The section names WR-01 specifically: the semantic, negative-invariant and certification outputs record `PASS` / `REJECTED_FAIL_CLOSED` results for checks the publisher does not actually run. Hayes should not cite those fields as independent evidence.
- **D-11:** The reply says a hardening release (v2.0.1) may follow, with no date. That release would need a new sign-off and a new pin, and is not intended to change any of the 21 decisions.

### What each control entry says
- **D-12:** Each of the 21 entries gives:
  - the control id;
  - the decision state (`RULE_PUBLISHED` or `NO_RULE_WILL_BE_PUBLISHED`);
  - the AA4-GOV id;
  - the rule in full, or "no rule";
  - one reason line: the first sentence of the record's `decided.rationale`, copied word for word.
  The decision records file is cited for the full rationale.
- **D-13:** The opening paragraph states the dual role, quoting `DUAL_ROLE_STATEMENT` exactly as it appears in the decision records and the sign-off. The text is read from the source, not retyped.
- **D-14:** For the other 59 controls, the reply says they remain `NOT_YET_DECIDED` and that EMS gives no date. A rule for any of them would need a new governance decision and a new authority version.
- **D-15:** The three rules' effect is given in plain words as well as the machine condition. The reply also states:
  - `UNKNOWN` never resolves to not applicable;
  - nothing resolves until Hayes's target description carries the eight classification facts.
  The three rules: EMS-CTRL-030 and EMS-CTRL-039 are not applicable only when `production` is `KNOWN_FALSE`; EMS-CTRL-052 is not applicable only when `ai_enabled` is `KNOWN_FALSE`.

### What publication does not do (REPLY-03, fixed by the roadmap)
- **D-16:** The reply lists the three Hayes-side changes still needed before any control resolves:
  1. the target description must carry the eight classification facts;
  2. Hayes must read the published v2 shape;
  3. Hayes must re-pin to `54a7fd0`.
  It also states that the classification-prerequisites gap is untouched, and that the live count of resolved controls stays at zero until those changes land.

### Commit hygiene
- **D-17:** Phase 5 must not edit `scripts/publish_archive_assessment_applicability_authority_v2.py`, the v2 schema, or any published registry or generated file. The publication manifest binds the publisher script's digest (WR-06), so any edit would turn `--validate` red against `54a7fd0`. The reply generator is a separate script that may import read-only helpers from the publisher.
- **D-18:** The reply goes in a commit after the publication commit. That commit (or commits) contains only this project's files, staged by explicit path. Unrelated work stays out:
  - the modified `registry/adjudication_rules.json` and `registry/policy_decisions.json`;
  - `schemas/archive_assessment_governance_answers.schema.json`, which shows as modified but whose content is identical to the committed blob;
  - the untracked files.
  The publisher's `--validate` must still print PASS after Phase 5.

### Claude's Discretion
- Exact file names, the JSON field names and the schema layout of the reply JSON (snake_case, `archive_assessment_*` naming).
- Section order and headings of the Markdown letter, provided the opening carries the dual role and every item in D-05..D-16 appears.
- Whether code, schema and test go in one commit and the generated reply files in a second (preferred, mirroring Phase 4 D-20), or all in one.
- How "first sentence" is cut (for example, up to the first ". " followed by a capital letter). It must be deterministic and tested.
- Wording of the fixed prose. It must be neutral and plain, and add no ranking or emphasis between controls.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The request and project scope
- `.planning/PROJECT.md` (Context section): the request `DEMO3-W1-REQ-001` / `EMSREQ-APPLIC-RULES`, the 21 controls, what Hayes's resolver needs, the old pin `62a8955`, and the RiskMVP observation
- `.planning/REQUIREMENTS.md`: REPLY-01, REPLY-02 and REPLY-03; V2-01 and V2-02, which are deferred
- `.planning/ROADMAP.md` (Phase 5): the four success criteria

### Published authority (read-only inputs)
- `registry/archive_assessment_applicability_authority_v2.json`: the published v2.0.0 authority; source of every per-control value
- `registry/archive_assessment_applicability_authority_v2_publication_record.json`: publication SHA, authority id and version, manifest and authority LF digests
- `registry/archive_assessment_applicability_authority_v2_signoff.json`: the sign-off (approver, role, dual-role statement)
- `registry/archive_assessment_governance_decisions.json`: AA4-GOV-001..021 records; `decided.rationale` gives the reason line
- `schemas/archive_assessment_applicability_authority_v2.schema.json`: the published shape
- `generated/archive-assessment/ems-aa3-v2/`: manifest, certification and decision traceability outputs

### Phase 4 results that the reply discloses
- `.planning/phases/04-certified-publication/04-REVIEW.md`: CR-01, CR-02 and WR-01..10; WR-01 is named in the reply
- `.planning/phases/04-certified-publication/04-VERIFICATION.md`: independent check that the published data is correct
- `.planning/phases/04-certified-publication/04-CONTEXT.md`: D-08..D-13 (what a decided control carries), D-21 (publication record and SHA ancestor test)

### Code to reuse
- `scripts/publish_archive_assessment_applicability_authority_v2.py`: `lf_digest`, `dump`, `load`, `jtext`, `rule_text`, `DUAL_ROLE_STATEMENT`, and the `--validate` rebuild-and-compare pattern. Import only; do not edit (D-17).
- `tests/test_archive_assessment_applicability_authority_v2_publication.py`: the git-gated SHA-ancestor test with shallow-clone handling, and the module-level TemporaryDirectory workaround
- `.gitattributes`: the narrow LF list to extend with the reply files

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `lf_digest` / `lf_bytes` / `dump` / `jtext` in the v2 publisher: LF-normalised digests and deterministic LF JSON output
- `rule_text(rule)` in the v2 publisher: renders a rule as `ALL_CONDITIONS_MUST_MATCH: production = KNOWN_FALSE`; reuse it so the reply and the sign-off summary show the same text
- `DUAL_ROLE_STATEMENT`, defined in both the builder and the publisher (WR-10 notes there are two copies); the reply should take it from the sign-off record or the decision records, so it quotes what was actually published
- `latest_records(doc)` in the v2 publisher: picks the latest unsuperseded decision record for each control

### Established Patterns
- Each authority comes with `docs/<NAME>.md`, `registry/<name>.json`, a schema, a `scripts/<verb>_<name>.py` with `--build`/`--validate`, and a pytest
- Deterministic output: a fixed date constant with no `now()`, `json.dumps(indent=2, sort_keys=True) + '\n'`, written with `newline='\n'`
- Fail closed: validation raises an error on any mismatch; the CLI prints `PASS` or exits non-zero
- Registry JSON stores repo-relative forward-slash paths only (`contains_absolute`)
- On this Windows machine, pytest's `tmp_path` fails (the default basetemp is not writable); tests use a module-level `TemporaryDirectory`, or run with `--basetemp` pointing at a writable directory

### Integration Points
- Read-only inputs: the v2 authority, the publication record, the sign-off, the decision records and the manifest
- New outputs: the reply Markdown in `docs/` and the reply JSON in `registry/`, plus a schema, a script, a test and the `.gitattributes` lines

</code_context>

<specifics>
## Specific Ideas

- The reply is EMS's complete answer under the request's own terms ("the rules with the authority for each; a statement that no rule will be published"). It should say so plainly.
- The reply restates the semantics that matter most to Hayes's resolver: an explicit controlled rule is required, unknown is not false, and absence of evidence is not not-applicable.
- Hayes's own test asserting that all 21 refuse will go red by design once Hayes re-pins and reads the shape. The reply may note this as an expected Hayes-side change, with no instruction on how Hayes fixes it.

</specifics>

<deferred>
## Deferred Ideas

- Hardening the publication checks (CR-01, CR-02, WR-01..WR-10) as a v2.0.1 republish with a new sign-off and a new pin: a later phase or milestone. The reply mentions it only as possible, with no date.
- Rule-or-no-rule decisions for the other 59 controls (V2-01): next milestone.
- Confirmation from a Hayes re-run that the 21 resolve at the new pin (V2-02): Hayes-side, next milestone.
- Adding V2-01 and V2-02 to the traceability table in REQUIREMENTS.md: a housekeeping warning raised by `phase.complete`, not part of this phase's deliverable.

</deferred>

---

*Phase: 05-reply-to-hayes*
*Context gathered: 2026-10-14*
