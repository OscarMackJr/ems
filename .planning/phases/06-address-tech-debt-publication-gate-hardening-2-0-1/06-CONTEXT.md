# Phase 6: Address tech debt: publication gate hardening (2.0.1) - Context

**Gathered:** 2026-10-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Harden the gates that guard the AA3 v2 applicability authority, then republish it as `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1` with a fresh sign-off from Oscar Mack as EMS governance authority and a new publication commit for Hayes to pin to. Then regenerate the unsent reply to `DEMO3-W1-REQ-001` so it cites 2.0.1.

The phase fixes the defects found in the Phase 4 review (`04-REVIEW.md`: CR-01, CR-02, WR-01..WR-10, IN-01, IN-07), Phase 2 WR-01 (frozen proposals validated against the live catalog), and the CLAUDE.md vocabulary wording.

It does **not** change:
- any of the 21 governance decisions (`AA4-GOV-001`..`021`), the decisions file, the answers file, the proposals or the drafting record;
- the 59 undecided controls (they stay `NOT_YET_DECIDED`);
- the v1.0.0 authority or its outputs.

It does not decide any of the other 59 controls, make any Hayes-side change, push, tag, merge or send the reply. Pushing and sending stay with the EMS authority.

</domain>

<decisions>
## Implementation Decisions

### Fix scope
- **D-01:** Fix every Phase 4 review critical and warning: CR-01, CR-02 and WR-01..WR-10 from `.planning/phases/04-certified-publication/04-REVIEW.md`. Each gets a test that fails before the fix. One republish and one sign-off cover all of them.
  - CR-01: the sign-off role must equal `EMS_GOVERNANCE_AUTHORITY` (a dedicated `SIGNOFF_ROLE` constant). `HAYES_VERIFY_DEVELOPER` is rejected. `APPROVER_ROLES` stays as the list of roles the approver holds.
  - CR-02: the publication gate (both the publish path and `--validate`) runs the governance-decisions validator and the decisions schema on `registry/archive_assessment_governance_decisions.json` before any build. It checks approver, approver roles, the exact dual-role statement, the disposition set, drafted vs frozen proposals, `answers_sha256` and supersession. Avoid a circular import (shared module or lazy import).
  - WR-02: `source_lineage` requires its entries, and each lineage entry is constrained in the schema (see D-08).
  - WR-03: the schema forbids a field appearing twice in one rule.
  - WR-04: sign-off checks use exact equality for the dual-role statement, a real ISO date check (`date.fromisoformat` plus pattern), and exact key sets for the record and the approval.
  - WR-05: see D-11.
  - WR-06: see D-09/D-10.
  - WR-07..WR-09: test fixes as the review describes (`sys.executable` plus a specific stderr assertion; actually run `main(['--build'])` with patched paths, including a refusal case; scope the generated-dir guard to the build functions with `inspect.getsource`).
  - WR-10: governance constants (`APPROVER`, `APPROVER_ROLES`, `DUAL_ROLE_STATEMENT`, the 21-id list) are defined once and imported. The builder takes them from the publisher, or a test asserts the copies are equal.
- **D-02:** Of the Phase 4 info items, fix only IN-01 (malformed records raise `AuthorityError`, which falls out of CR-02) and IN-07 (`--validate` checks the publication record's `authority_sha256` and `manifest_sha256` against the committed files). IN-02..IN-06 are deferred.
- **D-03:** Fix Phase 2 WR-01: the frozen proposals and drafting record are validated against the control catalog and frame **as they were at the drafting commit `dc3b41c`**, not the live files, so a later catalog edit cannot turn `--validate` red. The frozen files themselves are not touched. The planner chooses the mechanism, for example a recorded catalog digest plus the frozen values, or reading the catalog at `dc3b41c`. It must not make `--validate` depend on full git history unless it skips cleanly on shallow clones, following the existing pattern.
- **D-04:** Fix the CLAUDE.md wording in the Constraints section ("Vocabulary"). It currently says rule conditions use "the eight declared classification fields". In 2.0.0 and 2.0.1, rules may use only the first four (`RULE_FIELDS = CLASSIFICATION_FIELDS[:4]`: `production`, `internet_exposed`, `contains_customer_data`, `ai_enabled`). The other four remain classification prerequisites. Edit only that line (CLAUDE.md is tracked). The `.planning/PROJECT.md` Constraints line makes the same claim and gets the same correction.
- **D-05:** The Phase 5 reply-script info items IN-01..IN-06 (`.planning/phases/05-reply-to-hayes/05-REVIEW.md`) are in scope, because the reply is regenerated (D-14).

### Version, files and lineage
- **D-06:** The version is **2.0.1**, and the authority id is `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1`. The data and meaning of all 80 rows are unchanged. The schema is stricter but still accepts every valid 2.0.0-shaped document apart from the version and lineage fields.
- **D-07:** 2.0.1 **overwrites the v2 files in place**:
  - `registry/archive_assessment_applicability_authority_v2.json`
  - `schemas/archive_assessment_applicability_authority_v2.schema.json`
  - `generated/archive-assessment/ems-aa3-v2/` outputs
  - `registry/archive_assessment_applicability_authority_v2_signoff.json`
  - `registry/archive_assessment_applicability_authority_v2_publication_record.json`

  Hayes's read paths do not change. The 2.0.0 versions stay retrievable in git at `54a7fd0` (publication) and `0ce89f2` (publication record). No publication history file is added.
- **D-08:** Lineage:
  - `source_lineage.supersedes` names 2.0.0: authority id, version `2.0.0`, publication commit `54a7fd09114704a97a7a48fce5f89aebeb48c90a`, the 2.0.0 authority LF sha256, and 2.0.0's governance-decisions LF sha256 (D-12).
  - A separate field (working name `v1_baseline`) keeps v1.0.0 @ `62a8955` as the baseline for the 80-row field-by-field v1 comparison (Phase 4 D-13).
  - The schema requires `governance_decisions`, `supersedes`, the v1 baseline, `catalog_reference` and `digest_normalisation`, and pins the constant values (commits, versions) with `const` and sha256 patterns.
  - All values come from the files, never typed by hand. The 2.0.0 digests come from the current publication record before it is overwritten.
- **D-09:** WR-06: the manifest records the publisher-script LF digest it was built with. `--validate` re-derives the authority and every output and compares them with the committed files, checking the script digest against the recorded value rather than the live script. A later script-only edit then no longer turns `--validate` red. A consistent hand edit plus a re-hash of any artifact must still fail.
- **D-10:** `PUBLISHED_ON` is no longer a code constant. The publication date comes from the sign-off record (the approval date) and is bound by the sign-off digest, so outputs stay deterministic with no `now()`.
- **D-11:** WR-05: `build_archive_assessment_governance_decisions.py --build` refuses to rewrite the decisions file when the v2 authority's `source_lineage.governance_decisions.sha256` equals the current decisions-file digest. It proceeds only with an explicit `--supersede-published` flag, and prints that a republish and re-sign-off are then required.

### Proving no decision changed
- **D-12:** The 2.0.1 validator (in the publisher, not only in tests) requires the current governance-decisions LF sha256 to equal the 2.0.0 value recorded in `supersedes`. Same records means the same 21 decisions. Every row's decision fields (`not_applicable_decision_state`, `not_applicable_rule`, `not_applicable_authority`, `decision_ids`) and the top-level `applicability_decision_ids` are re-derived from those records.
- **D-13:** When git history is available, a pytest also compares all 80 rows of 2.0.1 with `git show 54a7fd0:registry/archive_assessment_applicability_authority_v2.json`. Only `authority_id`, `version`, the lineage and the stricter-schema reference may differ, and every row is value-equal. On a shallow clone it skips, following the Phase 4 D-21 handling.

### Reply and pin order
- **D-14:** Hold the reply. It is **not** sent at `54a7fd0`. After the 2.0.1 publication commit and publication record exist, `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` regenerates `docs/DEMO3_W1_REQ_001_REPLY.md` and `registry/archive_assessment_demo3_w1_req_001_reply.json` to cite 2.0.1:
  - the new authority id, version and publication SHA, read from the publication record;
  - the new LF digests.

  Hayes re-pins once, to 2.0.1. The three Hayes-side changes list in the reply (Phase 5 D-16) names the 2.0.1 SHA.
- **D-15:** The reply's review-disclosure section (Phase 5 D-09..D-11) becomes a short history note. It says:
  - 2.0.1 supersedes 2.0.0 (`54a7fd0`) to harden the publication checks;
  - which gates are now enforced: sign-off role, governance decisions validated, certification results computed, stricter schema;
  - none of the 21 decisions changed, citing the D-12 binding.

  The "do not cite these fields as independent evidence" caveat is removed, because WR-01 is fixed.
- **D-16:** `send_condition` names the 2.0.1 publication SHA on the remote branch `feature/ems-aa3-archive-applicability-authority`. The phase ends with a blocking human checkpoint where Oscar Mack reads the regenerated reply, including the WR-07 first-sentence reason lines and the reworded passages. Nothing is pushed or sent automatically. The last step reports the push command and the read-only remote check.

### Certification honesty (WR-01)
- **D-17:** The publisher **runs** the checks it certifies.
  - During build, each negative mutation is applied to a deep copy and must be rejected by `validate_publication` and/or the v2 schema.
  - Semantic checks such as `unknown_never_not_applicable` are computed.
  - `result`, conflict counts and the certification's `negative_invariants`/`prohibitions` are derived from the actual outcomes.
  - Any accepted mutation or failed semantic check raises `AuthorityError`, and nothing is written.
- **D-18:** The negative mutations are defined **once**, in the publisher, as named mutation functions with ids and descriptions. The pytest modules import the list and parametrize over it, and they assert that the recorded outcomes in the generated files equal what they observe.
- **D-19:** For each mutation, the negative-invariant output records its id, its description and which gate(s) rejected it (`SCHEMA`, `PYTHON_VALIDATOR`, or both). Hayes can then see which checks a schema-only consumer gets.
- **D-20:** The mutation list covers the existing 17 and adds one per gap the review proved in memory:
  - sign-off role `HAYES_VERIFY_DEVELOPER`;
  - an invalid sign-off date;
  - text appended to the dual-role statement;
  - extra sign-off keys;
  - a decision record with a tampered approver, an empty dual-role statement, or a bogus disposition;
  - a missing `source_lineage.governance_decisions`;
  - a rule naming the same field twice with opposite states;
  - a governance-decisions digest that differs from the `supersedes` binding.

### Process (carried forward)
- **D-21:** Follow Phase 4's sequence and gates:
  - Review fixes land in their own commits, before the publisher-code commit.
  - Run a dry-run publish, then stop at a blocking sign-off checkpoint. Oscar Mack sees a neutral, complete summary: 21 decided and 59 undecided; each control with its AA4 id and state; the three rules in full; the authority LF digest; and a line stating that 2.0.1 supersedes 2.0.0 with no decision changed.
  - The sign-off record is written with role `EMS_GOVERNANCE_AUTHORITY`, the date and the exact dual-role statement.
  - Then the publication commit, holding only the generated publication (v2 registry authority, `ems-aa3-v2/` outputs, sign-off, schema if regenerated). Then a publication-record commit.
  - Then the reply regeneration commit(s), then the read-through checkpoint.
- **D-22:** Commit hygiene as before:
  - Stage only by explicit path; never `git add -A` or `git add .`.
  - Unrelated work stays out of every commit: the modified `registry/adjudication_rules.json` and `registry/policy_decisions.json`, `schemas/archive_assessment_governance_answers.schema.json` (stale index metadata) and all untracked files.
  - New LF-only files are added to the narrow `.gitattributes`.
  - `git show --stat` on the publication commit lists only the publication files.

### Claude's Discretion
- How the decisions validator is shared between the builder and the publisher (shared module vs lazy import), so long as there is one implementation.
- The mechanism for Phase 2 WR-01 (D-03), within the shallow-clone constraint.
- Exact field names (`v1_baseline`, the manifest script-digest field, mutation ids, gate labels), snake_case, in line with existing v2 naming.
- How many commits the fixes take and in what order, provided D-21 ordering holds and tests are never red between commits.
- The wording of the history note in the reply and of the sign-off summary. Both must be neutral and plain, adding no ranking or emphasis.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source of the tech debt
- `.planning/v1.0.0-MILESTONE-AUDIT.md`: the tech_debt list by phase that defines this phase
- `.planning/phases/04-certified-publication/04-REVIEW.md`: CR-01, CR-02, WR-01..WR-10, IN-01, IN-07 (in-memory probes and suggested fixes)
- `.planning/phases/02-blind-drafting/02-REVIEW.md` §WR-01: frozen artifacts validated against the live catalog and semantics
- `.planning/phases/05-reply-to-hayes/05-REVIEW.md`: IN-01..IN-06 (reply script); `05-REVIEW-FIX.md` WR-07 note (first-sentence rule needs human confirmation)

### Prior phase decisions that still bind
- `.planning/phases/04-certified-publication/04-CONTEXT.md`: D-04/D-05 (LF digests and LF output), D-08..D-13 (what a decided control carries, the v1 field-by-field comparison), D-15 (output set), D-17 (rebuild-and-compare), D-19..D-22 (sign-off, publication commit, publication record, no push)
- `.planning/phases/05-reply-to-hayes/05-CONTEXT.md`: D-01..D-18 (reply form, generated not hand-written, pin and send gating, the disclosure section being replaced, commit hygiene)
- `.planning/phases/01-rule-shape-and-decision-states/01-CONTEXT.md`: rule shape, the four rule fields, decision states
- `.planning/PROJECT.md`: constraints (authority, dual role, publication pattern, working tree)

### Code to change
- `scripts/publish_archive_assessment_applicability_authority_v2.py`: `validate_signoff`, `validate_publication`, `build_published_authority`, `schema()`, `build_all_outputs`, `validate_published`, `PUBLISHED_ON`, `APPROVER_ROLES`, `NEGATIVE_MUTATIONS`
- `scripts/build_archive_assessment_governance_decisions.py`: `validate_decisions`, `refreshable`, `main()` `--build`, duplicated constants
- `scripts/validate_archive_assessment_rule_proposals.py`: Phase 2 WR-01 (live catalog and frame)
- `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`: reply regeneration; IN-01..IN-06
- `schemas/archive_assessment_applicability_authority_v2.schema.json`: regenerated from `schema()`, never hand-edited
- `tests/test_archive_assessment_applicability_authority_v2.py`, `tests/test_archive_assessment_applicability_authority_v2_publication.py`, `tests/test_archive_assessment_governance_decisions.py`, `tests/test_archive_assessment_rule_proposals.py`, `tests/test_archive_assessment_rule_proposals_record.py`, `tests/test_archive_assessment_demo3_w1_req_001_reply.py`
- `CLAUDE.md` (Constraints → Vocabulary line) and `.planning/PROJECT.md` (Constraints → Vocabulary line)
- `.gitattributes`: the narrow LF list

### Published 2.0.0 (inputs to the supersedes binding; overwritten by 2.0.1)
- `registry/archive_assessment_applicability_authority_v2.json`, `registry/archive_assessment_applicability_authority_v2_signoff.json`, `registry/archive_assessment_applicability_authority_v2_publication_record.json`, `generated/archive-assessment/ems-aa3-v2/`, all at `54a7fd0` / `0ce89f2`
- `registry/archive_assessment_demo3_w1_req_001_reply.json`, `docs/DEMO3_W1_REQ_001_REPLY.md`: the current reply citing 2.0.0 (regenerated)

### Frozen inputs (read-only)
- `registry/archive_assessment_governance_decisions.json`, `registry/archive_assessment_governance_answers.json`, `registry/archive_assessment_not_applicable_rule_proposals.json`, `registry/archive_assessment_rule_proposals_drafting_record.json`, `registry/archive_assessment_applicability_authority.json` (v1.0.0), `registry/control_catalog.yaml`

### Conventions
- `.planning/codebase/CONVENTIONS.md`, `.planning/codebase/TESTING.md`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `lf_digest`, `lf_bytes`, `dump`, `jtext`, `rule_text`, `latest_records` in the v2 publisher: LF digests, deterministic output, rule rendering
- `validate_decisions` in the governance-decisions builder: the validator that CR-02 must call from the publication gate
- `NEGATIVE_MUTATIONS` (17 entries) in the v2 publisher: currently only listed in the output and exercised in pytest; it becomes the single executed list (D-18)
- The `invalid(mutator)` test pattern and the git-gated SHA-ancestor test with shallow-clone skip in `tests/test_archive_assessment_applicability_authority_v2_publication.py`
- The reply script's `--build`/`--validate`/`--push-check`, already reading the SHA from the publication record

### Established Patterns
- `build_*` (pure) / `validate_*` (raises `AuthorityError`) pairs. The schema is emitted from `schema()`; hand edits are overwritten.
- Deterministic JSON (`indent=2, sort_keys=True`, trailing newline, `newline='\n'`), with no `now()`
- Fail closed; the CLI prints `PASS` or exits non-zero
- On this Windows machine pytest's `tmp_path` basetemp is not writable. Use a module-level `TemporaryDirectory` or `--basetemp`.
- Generated outputs under the gitignored `generated/` are force-added (`git add -f`).

### Integration Points
- The builder already imports the publisher as `V2`. Watch for a circular import when the publisher calls the builder's validator (CR-02).
- The reply script imports helpers from the publisher. Publisher API changes (`PUBLISHED_ON` removal, the lineage shape) ripple into it.
- `core.autocrlf=true`, with the narrow `.gitattributes` covering this project's files.
- `RULE_FIELDS = CLASSIFICATION_FIELDS[:4]` in the v2 publisher: the source for the D-04 wording fix.

</code_context>

<specifics>
## Specific Ideas

- The reply told Hayes: "a hardening release (v2.0.1) may follow, with a new sign-off and a new pin, not intended to change any of the 21 decisions." This phase delivers that promise, and D-12 makes "no decision changed" something the validator enforces.
- The audit's priority order: the CR-01 and CR-02 gate defects matter most, because the sign-off and the cited "named authority" are what Hayes relies on.
- A fresh Windows clone and ubuntu CI must pass `--validate` and the full archive-assessment test suite (today 397 tests across 8 modules).

</specifics>

<deferred>
## Deferred Ideas

- Phase 4 IN-02..IN-06 (shared test temp dir, CRLF test input, CRLF working copies, tautological meta-test, non-atomic publish writes): general test and tooling hygiene.
- Phase 2 WR-02..WR-10 and IN items (CLI flag combinations, shallow-clone git-history tests, absolute-path guard, etc.): not publication-gate defects.
- Phase 3 WR/IN items and the untested amendment path end to end.
- Pushing the branch, tagging and sending the reply stay with the EMS authority.
- Rule-or-no-rule decisions for the other 59 controls (V2-01), and the Hayes-side re-run (V2-02): next milestone.

</deferred>

---

*Phase: 06-address-tech-debt-publication-gate-hardening-2-0-1*
*Context gathered: 2026-10-14*
