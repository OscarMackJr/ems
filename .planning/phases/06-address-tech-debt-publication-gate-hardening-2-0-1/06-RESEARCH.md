# Phase 6: Address tech debt: publication gate hardening (2.0.1) - Research

**Researched:** 2026-10-14
**Domain:** Python governance-authority publisher hardening (jsonschema 2020-12, hash-certified artifacts, pytest, git commit choreography)
**Confidence:** HIGH (all claims below were read from the repo or executed in this session unless tagged otherwise)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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
- **D-06:** The version is **2.0.1**, and the authority id is `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1`. The data and meaning of all 80 rows are unchanged. The schema is stricter but still accepts every valid 2.0.0-shaped document apart from the version and lineage fields.
- **D-07:** 2.0.1 **overwrites the v2 files in place**: `registry/archive_assessment_applicability_authority_v2.json`, `schemas/archive_assessment_applicability_authority_v2.schema.json`, `generated/archive-assessment/ems-aa3-v2/` outputs, `registry/archive_assessment_applicability_authority_v2_signoff.json`, `registry/archive_assessment_applicability_authority_v2_publication_record.json`. Hayes's read paths do not change. The 2.0.0 versions stay retrievable in git at `54a7fd0` (publication) and `0ce89f2` (publication record). No publication history file is added.
- **D-08:** Lineage:
  - `source_lineage.supersedes` names 2.0.0: authority id, version `2.0.0`, publication commit `54a7fd09114704a97a7a48fce5f89aebeb48c90a`, the 2.0.0 authority LF sha256, and 2.0.0's governance-decisions LF sha256 (D-12).
  - A separate field (working name `v1_baseline`) keeps v1.0.0 @ `62a8955` as the baseline for the 80-row field-by-field v1 comparison (Phase 4 D-13).
  - The schema requires `governance_decisions`, `supersedes`, the v1 baseline, `catalog_reference` and `digest_normalisation`, and pins the constant values (commits, versions) with `const` and sha256 patterns.
  - All values come from the files, never typed by hand. The 2.0.0 digests come from the current publication record before it is overwritten.
- **D-09:** WR-06: the manifest records the publisher-script LF digest it was built with. `--validate` re-derives the authority and every output and compares them with the committed files, checking the script digest against the recorded value rather than the live script. A later script-only edit then no longer turns `--validate` red. A consistent hand edit plus a re-hash of any artifact must still fail.
- **D-10:** `PUBLISHED_ON` is no longer a code constant. The publication date comes from the sign-off record (the approval date) and is bound by the sign-off digest, so outputs stay deterministic with no `now()`.
- **D-11:** WR-05: `build_archive_assessment_governance_decisions.py --build` refuses to rewrite the decisions file when the v2 authority's `source_lineage.governance_decisions.sha256` equals the current decisions-file digest. It proceeds only with an explicit `--supersede-published` flag, and prints that a republish and re-sign-off are then required.
- **D-12:** The 2.0.1 validator (in the publisher, not only in tests) requires the current governance-decisions LF sha256 to equal the 2.0.0 value recorded in `supersedes`. Same records means the same 21 decisions. Every row's decision fields (`not_applicable_decision_state`, `not_applicable_rule`, `not_applicable_authority`, `decision_ids`) and the top-level `applicability_decision_ids` are re-derived from those records.
- **D-13:** When git history is available, a pytest also compares all 80 rows of 2.0.1 with `git show 54a7fd0:registry/archive_assessment_applicability_authority_v2.json`. Only `authority_id`, `version`, the lineage and the stricter-schema reference may differ, and every row is value-equal. On a shallow clone it skips, following the Phase 4 D-21 handling.
- **D-14:** Hold the reply. It is **not** sent at `54a7fd0`. After the 2.0.1 publication commit and publication record exist, `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` regenerates `docs/DEMO3_W1_REQ_001_REPLY.md` and `registry/archive_assessment_demo3_w1_req_001_reply.json` to cite 2.0.1: the new authority id, version and publication SHA, read from the publication record; the new LF digests. Hayes re-pins once, to 2.0.1. The three Hayes-side changes list in the reply (Phase 5 D-16) names the 2.0.1 SHA.
- **D-15:** The reply's review-disclosure section (Phase 5 D-09..D-11) becomes a short history note. It says: 2.0.1 supersedes 2.0.0 (`54a7fd0`) to harden the publication checks; which gates are now enforced: sign-off role, governance decisions validated, certification results computed, stricter schema; none of the 21 decisions changed, citing the D-12 binding. The "do not cite these fields as independent evidence" caveat is removed, because WR-01 is fixed.
- **D-16:** `send_condition` names the 2.0.1 publication SHA on the remote branch `feature/ems-aa3-archive-applicability-authority`. The phase ends with a blocking human checkpoint where Oscar Mack reads the regenerated reply, including the WR-07 first-sentence reason lines and the reworded passages. Nothing is pushed or sent automatically. The last step reports the push command and the read-only remote check.
- **D-17:** The publisher **runs** the checks it certifies. During build, each negative mutation is applied to a deep copy and must be rejected by `validate_publication` and/or the v2 schema. Semantic checks such as `unknown_never_not_applicable` are computed. `result`, conflict counts and the certification's `negative_invariants`/`prohibitions` are derived from the actual outcomes. Any accepted mutation or failed semantic check raises `AuthorityError`, and nothing is written.
- **D-18:** The negative mutations are defined **once**, in the publisher, as named mutation functions with ids and descriptions. The pytest modules import the list and parametrize over it, and they assert that the recorded outcomes in the generated files equal what they observe.
- **D-19:** For each mutation, the negative-invariant output records its id, its description and which gate(s) rejected it (`SCHEMA`, `PYTHON_VALIDATOR`, or both). Hayes can then see which checks a schema-only consumer gets.
- **D-20:** The mutation list covers the existing 17 and adds one per gap the review proved in memory: sign-off role `HAYES_VERIFY_DEVELOPER`; an invalid sign-off date; text appended to the dual-role statement; extra sign-off keys; a decision record with a tampered approver, an empty dual-role statement, or a bogus disposition; a missing `source_lineage.governance_decisions`; a rule naming the same field twice with opposite states; a governance-decisions digest that differs from the `supersedes` binding.
- **D-21:** Follow Phase 4's sequence and gates: review fixes land in their own commits, before the publisher-code commit. Run a dry-run publish, then stop at a blocking sign-off checkpoint. Oscar Mack sees a neutral, complete summary: 21 decided and 59 undecided; each control with its AA4 id and state; the three rules in full; the authority LF digest; and a line stating that 2.0.1 supersedes 2.0.0 with no decision changed. The sign-off record is written with role `EMS_GOVERNANCE_AUTHORITY`, the date and the exact dual-role statement. Then the publication commit, holding only the generated publication (v2 registry authority, `ems-aa3-v2/` outputs, sign-off, schema if regenerated). Then a publication-record commit. Then the reply regeneration commit(s), then the read-through checkpoint.
- **D-22:** Commit hygiene as before: stage only by explicit path; never `git add -A` or `git add .`. Unrelated work stays out of every commit: the modified `registry/adjudication_rules.json` and `registry/policy_decisions.json`, `schemas/archive_assessment_governance_answers.schema.json` (stale index metadata) and all untracked files. New LF-only files are added to the narrow `.gitattributes`. `git show --stat` on the publication commit lists only the publication files.

### Claude's Discretion

- How the decisions validator is shared between the builder and the publisher (shared module vs lazy import), so long as there is one implementation.
- The mechanism for Phase 2 WR-01 (D-03), within the shallow-clone constraint.
- Exact field names (`v1_baseline`, the manifest script-digest field, mutation ids, gate labels), snake_case, in line with existing v2 naming.
- How many commits the fixes take and in what order, provided D-21 ordering holds and tests are never red between commits.
- The wording of the history note in the reply and of the sign-off summary. Both must be neutral and plain, adding no ranking or emphasis.

### Deferred Ideas (OUT OF SCOPE)

- Phase 4 IN-02..IN-06 (shared test temp dir, CRLF test input, CRLF working copies, tautological meta-test, non-atomic publish writes): general test and tooling hygiene.
- Phase 2 WR-02..WR-10 and IN items (CLI flag combinations, shallow-clone git-history tests, absolute-path guard, etc.): not publication-gate defects.
- Phase 3 WR/IN items and the untested amendment path end to end.
- Pushing the branch, tagging and sending the reply stay with the EMS authority.
- Rule-or-no-rule decisions for the other 59 controls (V2-01), and the Hayes-side re-run (V2-02): next milestone.
</user_constraints>

<phase_requirements>
## Phase Requirements

No requirement IDs are mapped to this phase (ROADMAP: "Requirements: TBD"). D-01..D-22 above are the scope. The audit (`.planning/v1.0.0-MILESTONE-AUDIT.md` `tech_debt`) is the traceability source.
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- Python 3.12, `jsonschema`, PyYAML, pytest; Windows-primary; match existing code style. Publisher scripts use single quotes and compact one-line helpers; deterministic JSON (`indent=2, sort_keys=True`, trailing `\n`), `utf-8`, repo-relative forward-slash paths, no absolute paths in registry JSON.
- Fail closed: validators raise `AuthorityError`; unknown never resolves to NOT_APPLICABLE; no `now()`.
- Authority/dual-role/boundary/scope constraints: only the 21 controls; the other 59 stay `NOT_YET_DECIDED`; nothing from Hayes adopted.
- Working tree: unrelated uncommitted work stays out of every commit; the commit Hayes re-pins to holds only deliberate changes.
- CLAUDE.md "Vocabulary" line is itself a D-04 fix target (it is generated from `.planning/PROJECT.md` Constraints; edit PROJECT.md first, then CLAUDE.md).
- GSD workflow: file edits happen through a GSD command (this phase's execute step).
- Recent commit trailer (system reminder): end commits with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

## Summary

All of the work is in five scripts and six test modules that already exist; no new external package is needed. The two critical defects are one-line-class fixes (role equality, call the existing `validate_decisions` before any build). The size of the phase comes from three things that interact: (1) the certification honesty fix (D-17..D-20) makes `build_all_outputs` run ~26 mutations and changes the generated output shapes; (2) the version bump, lineage rewrite, manifest/script-digest change and sign-off-derived date change every generated byte, so the real-file tests go red from the moment the publisher code lands until the publication commit; (3) overwriting the v2 files in place invalidates several existing tests and one dry-run code path that were written assuming the files did not yet exist (details in Pitfalls 1-4).

The circular import (builder imports publisher as `V2`, publisher needs builder's `validate_decisions`) is best solved by a cached lazy loader in the publisher. A shared module is a larger refactor because `validate_decisions` itself depends on about ten publisher symbols. The lazy loader must convert the builder's exception into the publisher's own `AuthorityError`, because each `spec_from_file_location` load creates a distinct module object and therefore a distinct exception class (Pitfall 5).

Phase 2 WR-01 can be fixed without git history in the normal case: the live catalog's LF digest already equals the drafting record's `catalog_sha256` (verified: `12bb1a9d...`), and the catalog git blob id can be computed in pure Python (verified: `03c9faa4...`). Git is needed only when the catalog has actually drifted, and then it skips that single sub-check with a printed notice on a shallow clone.

**Primary recommendation:** Land output-neutral gate fixes first (all green), then one "publisher 2.0.1" code commit (script + regenerated schema + updated tests), dry-run, blocking sign-off checkpoint, publish, publication commit, record commit, then reply script changes + regeneration, then the blocking read-through checkpoint. Plan for a short, explicit red window on four real-file tests between the publisher code commit and the publication commit (Open Question 1).

## Architectural Responsibility Map

This is a script-driven governance repository, not a multi-tier app. Tiers mapped to the repo's layers:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Publication gate (sign-off, decisions validation, mutation harness) | `scripts/publish_..._v2.py` (logic layer) | tests | The publisher owns the certified claims (D-17), so the checks must run there, not only in pytest |
| Decisions validator | `scripts/build_..._governance_decisions.py` | publisher (caller) | One implementation (CLAUDE.md "Duplicated helper code" anti-pattern); publisher calls it |
| Authority schema | `schemas/...v2.schema.json` (emitted from `schema()`) | — | Hayes reads only the schema, so it must carry what it can (WR-02/03) |
| Frozen-input validation (Phase 2 WR-01) | `scripts/validate_archive_assessment_rule_proposals.py` | drafting record | Binds to record digests, not live files |
| Publication date, role, dual-role statement | sign-off record (`registry/..._signoff.json`) | manifest/cert (digest-bound) | D-10: the human-approved record is the source |
| Reply content | `scripts/build_..._reply.py` (generated) | publication record | Reply reads only the record and committed authority, never typed values |
| Commit choreography / pin | git (explicit-path staging) | publication record | D-21/D-22 |

## Standard Stack

No new libraries. Existing, verified locally:

| Library | Version | Purpose | Source |
|---------|---------|---------|--------|
| Python | 3.12.10 | runtime | [VERIFIED: `python --version`] |
| jsonschema | 4.26.0 | Draft 2020-12 validation, `contains`/`maxContains` supported | [VERIFIED: ran a `maxContains: 1` rule schema; duplicate field rejected, distinct fields accepted] |
| pytest | installed (397 tests collected/pass) | tests | [VERIFIED: run] |
| PyYAML | 6.0.3 pinned | catalog parsing | CLAUDE.md |
| stdlib: `hashlib`, `inspect`, `importlib.util`, `dataclasses`, `datetime.date` | — | digests, source inspection, lazy loader, mutation records, ISO date check | stdlib |

**Package Legitimacy Audit:** Not applicable. This phase installs no external packages. (slopcheck not run; nothing to check.)

**Installation:** none.

## Architecture Patterns

### Data flow (publication path)

```
 registry/control_catalog.yaml ──┐
 registry/..._authority.json (v1) ┤
 registry/..._governance_decisions.json ─► [GATE] validate_governance_decisions()
        │                                    (lazy-loaded builder.validate_decisions + decisions schema)
        │                                          │ AuthorityError on any violation, before any build
        ▼                                          ▼
 build_published_authority() ─► validate_publication() ─► authority schema validate
        │
        ├─ dry-run:  print neutral summary (no write) ──► BLOCKING CHECKPOINT: Oscar Mack approves
        │                                                        │
        │                                          sign-off record written (role EMS_GOVERNANCE_AUTHORITY,
        │                                          date, exact dual-role statement, authority LF sha256)
        ▼                                                        │
 publish: validate_signoff ◄─────────────────────────────────────┘
        ▼
 build_all_outputs(authority, signoff, script_sha256)
        ├─ run NEGATIVE_MUTATIONS (authority / signoff / decisions targets) ─► rejected_by gates
        ├─ compute semantic checks over rule rows (and all 80 rows)
        └─ derive result / counts / certification from outcomes; raise before writing if any mutation accepted
        ▼
 write authority + 7 outputs (manifest last)   ──► git add -f generated/…  ──► publication commit
        ▼
 --record-publication <sha> ─► publication record ─► record commit
        ▼
 reply script --build (reads record + committed authority/signoff/decisions) ─► reply JSON + MD ─► commit
        ▼
 BLOCKING CHECKPOINT: Oscar Mack reads reply; push/send stay manual
```

### Recommended structure (no new files required)

Edit in place: `scripts/publish_..._v2.py`, `scripts/build_..._governance_decisions.py`, `scripts/validate_..._rule_proposals.py`, `scripts/build_..._reply.py`, the six test modules, `schemas/..._v2.schema.json` (re-emitted, never hand-edited), `CLAUDE.md`, `.planning/PROJECT.md`. No new LF-only file is introduced, so `.gitattributes` does not need to change (all v2 and reply files are already in its narrow list, verified by reading it).

### Pattern 1: Cached lazy loader for the decisions validator (CR-02, recommended)

**What:** In the publisher, a function that loads the builder script once via `importlib.util`, converts its errors, and exposes `validate_decisions` and `decisions_schema`.
**Why not a shared module:** `validate_decisions` (builder L234-325) uses `V2.AUTHORITY_ID_RE`, `V2.validate_rule`, `V2.contains_absolute`, `V2.lf_digest`, `V2.load`, `AuthorityError`, plus its own constants. A shared module would have to be a third base module that both import (publisher primitives moved out), which touches every test that does `MODULE.V2.dump`, `monkeypatch.setattr(MODULE, ...)` etc. High churn, no benefit.

```python
# publisher (sketch; match single-quote compact style)
_BUILDER = None
def decisions_builder():
    global _BUILDER
    if _BUILDER is None:
        spec = importlib.util.spec_from_file_location('aa_governance_decisions_builder', ROOT / 'scripts' / 'build_archive_assessment_governance_decisions.py')
        _BUILDER = importlib.util.module_from_spec(spec); spec.loader.exec_module(_BUILDER)
    return _BUILDER

def validate_governance_decisions() -> dict:
    B = decisions_builder()
    try:
        doc = B.load_checked(GOVERNANCE_DECISIONS)      # JSON errors -> builder AuthorityError
        B.validate_decisions(doc)
        jsonschema.Draft202012Validator(B.decisions_schema()).validate(doc)   # or load(B.DECISIONS_SCHEMA)
    except (ValueError, jsonschema.ValidationError) as e:    # builder's AuthorityError is a different class object
        raise AuthorityError(f'governance decisions invalid: {e}')
    return doc
```

Call it first in `published_authority_checked()` (L399) and `validate_published()` (L417). Pass the publisher's own `GOVERNANCE_DECISIONS` path (`load_checked(path)` accepts a path) so test monkeypatching of the publisher's path is honoured. Existing test `test_module_does_not_call_git` (publication test L78) forbids the substring `subprocess` and `import git` in the publisher source, so no git use may enter the publisher.

### Pattern 2: Mutation records executed by the publisher (D-17..D-20)

**What:** `NEGATIVE_MUTATIONS` (currently a bare list of 17 id strings, publisher L320, used only at L378) becomes a list of records (stdlib `dataclass` or dicts):
`id`, `description`, `target` (`AUTHORITY` | `SIGNOFF` | `DECISIONS`), `apply(ctx)` mutator on a deep copy, `schema_must_reject: bool`.
A single `run_mutations(authority, signoff_record, decisions_doc) -> list[dict]` applies each to a deep copy and tries the gates for that target:

| Target | PYTHON_VALIDATOR gate | SCHEMA gate |
|--------|----------------------|-------------|
| AUTHORITY | `validate_publication(copy)` | `Draft202012Validator(schema()).validate(copy)` |
| SIGNOFF | `validate_signoff(copy, digest)` | none exists (no sign-off schema; do not add one in this phase) |
| DECISIONS | `builder.validate_decisions(copy)` | `builder.decisions_schema()` |

`rejected_by` = list of gates that raised. If empty: raise `AuthorityError('mutation <id> was accepted')` before anything is written. If `schema_must_reject` is True and SCHEMA did not reject: raise too (this is what proves WR-02/WR-03 stay fixed). Output entry shape (additive, keep the existing `mutation` key so any consumer reading it keeps working): `{'mutation': id, 'id': id, 'description': ..., 'rejected_by': ['PYTHON_VALIDATOR','SCHEMA'], 'result': 'REJECTED_FAIL_CLOSED'}`. Top-level `result` = `'PASS'` only when every entry is rejected.

Mutation inventory (26):
- Existing 17 (ids unchanged, from publisher L320). Each already has a hand-written test in `tests/test_archive_assessment_applicability_authority_v2_publication.py` (e.g. `test_swapped_authority_fails` L82, `test_rule_unused_field_fails` L93): reuse those mutators verbatim.
- New 9 (D-20): `signoff_role_hayes_developer`, `signoff_invalid_date`, `signoff_dual_role_text_appended`, `signoff_extra_keys` (all SIGNOFF), `decision_record_tampered_approver`, `decision_record_empty_dual_role_statement`, `decision_record_bogus_disposition` (DECISIONS; both gates reject: schema has `approver` const, `dual_role_statement` const, `disposition` enum), `rule_same_field_twice_opposite_states` (AUTHORITY, schema_must_reject True after WR-03), `supersedes_governance_digest_differs` (AUTHORITY, PYTHON_VALIDATOR only).
- `missing_governance_lineage` already exists: set `schema_must_reject=True` (today only the Python validator rejects it, review WR-02).

Cost: measured `build_published_authority` 0.026s, `validate_publication` 0.024s, schema validate 0.007s, so ~26 mutations is roughly 1-2s per `build_all_outputs` call. About 12 tests call it; acceptable. If suite time matters, memoize `run_mutations` per `(authority digest, signoff digest)` inside the test module.

Tests parametrize: `@pytest.mark.parametrize('m', MODULE.NEGATIVE_MUTATIONS, ids=lambda m: m.id)`; assert the live harness result for `m` equals the entry in the committed `..._negative_invariant_validation.json`. Keep the existing named tests; they become redundant but are cheap and name the gap.

### Pattern 3: Sign-off record owns the date (D-10) and `build_all_outputs` requires it

`published_on = signoff['approval']['date']` everywhere `PUBLISHED_ON` is used now (publisher L361, 371, 377, 378, 380, 385, 387, 395). `build_all_outputs(authority, signoff)` must take a required `signoff` dict (today `signoff=None` is allowed and the tests call `build_all_outputs(a)`; update those calls to pass `valid_signoff(...)`). The date is bound by `signoff_sha256` already written into the certification (L385) and manifest (L393). The dry-run summary (L361) cannot print a date before sign-off exists: print `Published on: the approval date in the sign-off record` or omit the line.

### Pattern 4: Manifest records the script digest separately (D-09)

Current: the script is `artifacts[0]` (L392) and the live-check loop (L432-433) re-hashes every manifest artifact from disk, so it would fail on any later script edit. Recommended shape: a top-level `publisher_script: {'relative_path','sha256','sha256_normalisation': 'CRLF_TO_LF'}` field in the manifest, removed from `artifacts`, so the generic live-file loop stays unchanged and unconditionally strict for authority/schema/sign-off/outputs. `build_all_outputs(authority, signoff, script_sha256=None)` defaults to `lf_digest(SCRIPT)` (publish) and `validate_published()` passes the value read from the committed manifest. Validity of the recorded script digest rests on (a) the publication record's `manifest_sha256` (IN-07, below) and (b) a git-gated pytest that asserts the recorded digest equals `git show <publication_commit>:scripts/publish_...py`.

Honest limit to state in the plan: D-09 only decouples the digest. Any later edit that changes what the publisher *builds* (output logic, mutation list) will still make the rebuild-compare red, which is correct behaviour.

### Pattern 5: Frozen-input validation without live files (Phase 2 WR-01 / D-03, recommended)

Today's live couplings in `scripts/validate_archive_assessment_rule_proposals.py`:
- `catalog_fingerprint()` L56-59 shells out to `git hash-object` on the *live* catalog; `expected_header()` L61-63 uses it plus live `V2.semantics()` as the frame; `validate_proposals` header comparison L109-111.
- `validate_proposal` L93 compares `catalog_inputs` with the live catalog (`live_catalog()` L65-66, default at L106).
- Tests also couple: `test_catalog_drift_real_proposals_match_live_catalog` (rule_proposals L184), `test_brief_header_equals_expected_header` (L220), fixture `build_fixture` uses `expected_header()` (L31).

Recommended mechanism (no new files, frozen files untouched):
1. `frozen_catalog_source()` builds `catalog_source` from the **drafting record** (`catalog_path`, `catalog_git_blob_id`, `catalog_sha256`) instead of the live file, plus the two constant fields (`entries_have_description: False`, `note`). `expected_header()` returns this, so the fixture and brief-header tests keep working with the same API.
2. Pin the frame by digest: `drafting_frame` is compared with the frame in the proposals file itself, after verifying `V2.lf_digest(PROPOSALS) == record['proposals_sha256']` (non-git integrity anchor; the record is already validated by `--validate-record`). Optionally also hold a `FROZEN_FRAME_SHA256` constant (computed once from the frozen header via a one-line command and verified by a git-gated test against `git show dc3b41c:<proposals>`). Synthetic fixtures keep using live `V2.semantics()` via a `frame=` default argument.
3. `frozen_catalog()` for `catalog_inputs`: if `V2.lf_digest(CATALOG) == record['catalog_sha256']` (true today, verified), use the live parse (identical bytes to the drafting catalog; no git). Otherwise read `git show dc3b41c:registry/control_catalog.yaml`, require its sha256 to equal `record['catalog_sha256']`, and use that. If git or the commit is unavailable (shallow clone), skip only the `catalog_inputs` equality sub-check and print a one-line notice to stderr (do not silently pass).
4. The git blob id can be computed with no git: `hashlib.sha1(b'blob %d\0' % len(b) + b)` over LF-normalised catalog bytes gives `03c9faa44af37860fe268a74bcb4468e8bfd34c4` (verified equal to `record['catalog_git_blob_id']`). Use this to drop the `git hash-object` call from the default path; this also fixes the audit note that proposals `--validate` "cannot re-verify a plain export of the pin".
5. Keep the live-catalog tests but rename/re-document them as drift information (they assert live equals frozen; they are not validity checks). They are green today and stay green unless the catalog is edited.

Out of scope (state it so the planner does not widen): `build_authority()` (publisher L100) and `validate_publication` L262-263 deliberately bind the *authority* to the live catalog digest. A catalog edit legitimately requires a republish. Only the frozen proposals/record are decoupled.

### Anti-Patterns to Avoid

- Hand-editing `schemas/..._v2.schema.json` or any generated file (hash certification breaks): emit via `--emit-schema` and `--publish`.
- Running `build_archive_assessment_governance_decisions.py --emit-schema` casually: it rewrites **both** the answers schema and the decisions schema (builder L376). `schemas/archive_assessment_governance_answers.schema.json` is in the unrelated/"stale index metadata" list (D-22) and `tests/...governance_answers.py:178` asserts the committed file equals `answers_schema()`. Do not change the builder's `rule_schema()` (L186-188) in this phase; WR-03's schema fix belongs to the publisher's v2 authority schema only. The Python validator `V2.validate_rule` (L179) already rejects repeated fields everywhere.
- `git add -A`, `git add .`, `git commit -a`: forbidden by D-22; 119 status entries are present.
- Typing the 2.0.0 digests by hand into the plan or code: derive them with a command, then verify with a git-gated test (see Code Examples).
- Moving `RULE_FIELDS`-style constants into new files: unnecessary; the builder already imports the publisher as `V2` and can take `APPROVER`, `APPROVER_ROLES`, `DUAL_ROLE_STATEMENT`, `REQUEST_CONTROL_IDS` from it (WR-10).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Field-appears-at-most-once in a rule schema | custom Python-only check as the sole gate | `allOf` of per-field `contains` + `maxContains: 1` (`minContains: 0`) inside `conditions` | Hayes validates with the schema alone; verified working in jsonschema 4.26.0 |
| ISO date check | regex only | `date.fromisoformat` plus `^\d{4}-\d{2}-\d{2}$` (builder `is_date` L73-77 already does this; the publisher cannot import the builder at module level, so copy its 5 lines or call it via the lazy loader) | rejects `2026-02-30` |
| Decisions validation | a second validator in the publisher | builder `validate_decisions` via the lazy loader | one implementation (D-01 CR-02, CLAUDE.md anti-pattern "Duplicated helper code") |
| LF digests | new hash helper | `lf_digest`, `lf_bytes`, `sha_text`, `jtext`, `dump`, `write_text` (publisher L47-53, L322-327) | already used by every digest in the repo |
| Git blob id | `git hash-object` subprocess | `sha1(b'blob N\0' + lf_bytes)` | no git dependency (verified equal to recorded id) |
| Shallow-clone handling in tests | new mechanism | copy `git_ready()` pattern (publication test L369-374, record test L34-43) | existing, accepted pattern |

## Review Item Map (exact location today, minimal fix shape, test that fails first)

Line numbers are the current working-tree files (read this session). "P" = `scripts/publish_archive_assessment_applicability_authority_v2.py`, "B" = `scripts/build_archive_assessment_governance_decisions.py`, "V" = `scripts/validate_archive_assessment_rule_proposals.py`, "R" = `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`.

### Phase 4 review

| Item | Location now | Minimal fix | Failing-first test |
|------|--------------|-------------|--------------------|
| CR-01 | P L310 `APPROVER_ROLES`, L340 `not in APPROVER_ROLES` | add `SIGNOFF_ROLE = 'EMS_GOVERNANCE_AUTHORITY'`; `appr.get('role') != SIGNOFF_ROLE`; keep `APPROVER_ROLES` (used by B L32/281/336 and R L70) | `so_fails(lambda r: r['approval'].__setitem__('role','HAYES_VERIFY_DEVELOPER'))` in `test_signoff_value_mutations_fail` (pub test L235-242) |
| CR-02 | P L399-402 `published_authority_checked`, L417-434 `validate_published`; `validate_publication` L227-229 only cross-checks | `validate_governance_decisions()` (Pattern 1) called first in both; do NOT put it inside `validate_publication` (existing tests call it with `build()` output and a monkeypatched `load`, e.g. `test_superseded_record_cited_fails` L139-154 injects a synthetic AA4-GOV-022 that the real validator would reject) | new tests: patch `MODULE.GOVERNANCE_DECISIONS` to a temp copy with every `approver` = `Someone Else` (or `dual_role_statement` ''/`disposition` 'BOGUS'); assert `published_authority_checked()` and `validate_published()` raise `AuthorityError` |
| WR-01 | P L377 (`'result': 'PASS'`, `semantic_conflict_count: 0`), L378 (`NEGATIVE_MUTATIONS` listed, never run), L385 (`semantic_conflicts: 0`, `negative_invariants: 'PASS'`, `prohibitions`) | Pattern 2; compute semantic checks (see Code Examples); derive cert fields from outcomes | parametrized mutation test; a test that monkeypatches a mutator to a no-op and expects `build_all_outputs` to raise; a test that forces `resolve_applicability` to return NOT_APPLICABLE for UNKNOWN and expects raise |
| WR-02 | P L279 `source_lineage` has `properties` only, no `required`; `supersedes`/`catalog_reference` unconstrained | schema: `required: [governance_decisions, supersedes, v1_baseline, catalog_reference, digest_normalisation]`, `additionalProperties` false with the AA1/AA2 digests declared, `const`s per D-08 | `fails(lambda a: a['source_lineage'].pop('governance_decisions'), True)` (currently `schema_too` is not passed in `test_missing_governance_lineage_fails` L132) |
| WR-03 | P L268 `rule`: `conditions` only bounded 1..4 | add `'allOf': [{'contains': {'properties': {'field': {'const': f}}, 'required': ['field']}, 'minContains': 0, 'maxContains': 1} for f in RULE_FIELDS]` to `conditions` | new test: `[{production,F},{production,T}]` rejected by schema and validator. Also update `test_duplicate_field_*_validator_only` in `tests/...authority_v2.py` L79-80: they name "validator_only" and use `invalid()`; keep, and add `schema_rejects` variants |
| WR-04 | P L329-347: L337 truthiness only, L342 substring `in`, no key-set check | `set(record) == {7 keys}`; `set(appr) == {'approver','role','date','scope'}`; `dr != DUAL_ROLE_STATEMENT`; `date.fromisoformat(d)` and pattern; `scope` non-empty string; `version == VERSION` (L344) and `authority_id == AUTHORITY_ID` (L343) from new constants | cases in `test_signoff_value_mutations_fail`: `'not-a-date'`, appended text, extra key on record and on approval |
| WR-05 | B L377-386 `--build`; `refreshable` L350-356 ignores `answers_sha256` | before rewriting an existing decisions file, if `V2.AUTHORITY` exists and its `source_lineage.governance_decisions.sha256 == V2.lf_digest(DECISIONS)` and `not args.supersede_published`: raise `AuthorityError` naming the republish and re-sign-off. New flag `--supersede-published` (prints the same notice and proceeds). Only guard the *rewrite* branches (L382-385); the identical-bytes no-op must still print PASS | CLI test (WR-08 below) with patched `MODULE.DECISIONS`/`ANSWERS`/`V2.AUTHORITY`: refusal without the flag, success with it |
| WR-06 | P L304 `PUBLISHED_ON`, L392 `lf_digest(SCRIPT)`, L425-433 | Patterns 3 and 4 | tests: edit live script bytes (patch `SCRIPT` to a different tmp file after publish) and `validate_published()` still passes; hand-edit + re-hash of any other artifact still fails (`test_validate_rejects_hand_edit_with_consistent_rehash` L299 stays) |
| WR-07 | tests: governance_decisions test, `subprocess.run(['python', ...])` at ~L447 (`test_wr09_emit_template_refuses_existing_answers_file`) | `[sys.executable, str(SCRIPT), '--emit-template']`; `assert 'already exists' in result.stderr` | the test itself |
| WR-08 | `test_wr07_build_cli_appends_superseding_record` ~L421-427 only calls `refreshable()` | monkeypatch `MODULE.DECISIONS`, `MODULE.ANSWERS` to temp files (module-level `TemporaryDirectory`, not `tmp_path`), set `sys.argv`, call `MODULE.main()`; assert 22 records; refusal case with a changed record 0; plus D-11 refusal/flag case. Note `main()` also loads the real `PROPOSALS`/`DRAFTING_RECORD`/`WORDING_APPROVAL` and calls `answers_schema()`; synthetic answers from the file's `filled()` helper already work with `built()` | the test itself |
| WR-09 | `tests/...authority_v2.py` L136-138 | `src = inspect.getsource(MODULE.build_authority) + inspect.getsource(MODULE.build_published_authority); assert 'generated' not in src and 'OUT' not in src` (check: neither function references `OUT`/`generated` today; I read both) | the test itself |
| WR-10 | B L31-33, L56 duplicate P L21, L309-311 | `APPROVER = V2.APPROVER`, `APPROVER_ROLES = list(V2.APPROVER_ROLES)`, `DUAL_ROLE_STATEMENT = V2.DUAL_ROLE_STATEMENT`, `CONTROL_IDS = list(V2.REQUEST_CONTROL_IDS)` after the `V2` load at B L18-21. Optional same treatment for V L29 `CONTROL_IDS` | equality test (cheap, add anyway) |
| IN-01 | P L156-163, L250-251 direct key access | falls out of CR-02 (gate runs before build). Add a test with a record missing `decided` through `published_authority_checked()` | new test |
| IN-07 | P L417-434 never reads `PUBLICATION_RECORD` | see Pitfall 3 for the stale-record window; check `record['authority_sha256'] == lf_digest(AUTHORITY)` and `record['manifest_sha256'] == lf_digest(OUT/N_MANIFEST)` when the record exists and `record['authority_id'] == a['authority_id']` | tests in the `env` fixture: matching, mismatching, stale-other-version, absent |

### Phase 2

| Item | Location | Fix | Test |
|------|----------|-----|------|
| WR-01 | V L56-66, L93, L106, L109-111 | Pattern 5 | new tests: monkeypatch `V.CATALOG` to a modified copy (extra/changed `scope` for a requested control): `validate_proposals(real_proposals)` still passes when git has `dc3b41c` (frozen catalog read from git, sha-checked), and the shallow-clone branch prints the notice and passes; plus the existing git-gated tests unchanged |

### Phase 5 (reply script, D-05)

| Item | Location | Fix |
|------|----------|-----|
| IN-01 unused `manifest` param | R L43 `build_reply(authority, record, signoff, decisions, manifest)` | drop the parameter; update callers R L227, L280 and tests `inputs()`/`build()` (reply tests L35-40) |
| IN-02 unused test imports | reply tests L4 `json`, L7 `tempfile`? | `tempfile` IS used now (module-level `_TMP`, L25); `json` is unused. Remove only `json` (verify with ruff if available) |
| IN-03 bare `StopIteration` | R L60 `next(...)` | `next(..., None)` then `raise V2.AuthorityError('no RULE_PUBLISHED row for the example')` |
| IN-04 shape names not checked | R L72-75 | assert `top_level_field in authority`, `semantics_block in authority`, each `per_control_fields` key in each row, every row `decision_ids == V2.DECISIONS` |
| IN-05 abbreviated typed record commit | R L24 `RECORD_COMMIT_ABBREV = '0ce89f2'`, L72, schema L180 (`^[0-9a-f]{7,40}$`), reply test L329 | resolve at build time with `git log -n1 --format=%H -- registry/..._publication_record.json` (NOT `--diff-filter=A`; see Pitfall 2), store the 40-hex value, schema pattern `^[0-9a-f]{40}$`; `validate_reply()` takes the stored value from the committed reply JSON and only checks its format (so `--validate` needs no git); git-gated pytest asserts it equals the last commit touching the record. Optionally tighten the schema items the review lists (`roles` enum, `not_yet_decided.count` const 59, `example_decided_row` shape) |
| IN-06 CLI flags | R L275-285 | `parser.add_mutually_exclusive_group(required=True)` for the four flags (also removes the trailing `parser.error`) |

Reply content changes (D-14/D-15/D-16), all in R: `build_reply` L92 `disclosure` block and L153-156 Markdown become a `history_note` built from `authority['source_lineage']['supersedes']` (authority id, version, commit read, not typed), the list of enforced gates, and "no decision changed" citing the D-12 binding (the decisions LF sha256 shown equals `supersedes.governance_decisions_sha256`). Drop `review_path`, `verification_path`, `wr_01`, `v2_0_1_possible`, `v2_0_1_date` from the object and the schema (R L186). `send_condition` (L93) already uses `record['publication_commit']` and the remote branch. `REPLY_DATE` (L20) is a typed constant `2026-10-14` (Open Question 2). Tests to rewrite: `test_markdown_content` (needles `'WR-01'`, `'04-VERIFICATION'`, `'v2.0.1'` at reply test ~L225 must be replaced); the `disclosure` mutation/schema tests if any; `test_record_commit_added_the_publication_record` (L188); `test_publisher_still_valid_and_digest_matches_manifest` (~L114, compares live script digest to `artifacts` entry).

## Common Pitfalls

### Pitfall 1: Real-file tests go red between the publisher-code commit and the publication commit
**What goes wrong:** Overwriting the v2 files in place means that as soon as `P` builds a 2.0.1 authority, the committed 2.0.0 files fail validation. Concretely red in the window: `test_real_published_files_validate` (pub test L352), `test_committed_schema_equals_schema_function` if the schema is not committed with the script (authority_v2 test L135), reply `test_real_reply_files_validate` and `test_publisher_still_valid_and_digest_matches_manifest`, plus `--validate` of both scripts. (`test_publication_commit_ancestor_and_file_set` stays green: it reads `54a7fd0` via git and the output file names are unchanged.)
**Why:** CONTEXT's "tests are never red between commits" cannot hold for these four once output-affecting code and the real files disagree; Phase 4 avoided it because the files did not exist yet (`skipif(not exists)`).
**How to avoid:** (a) put every output-neutral fix first (all green, see Plan ordering), (b) commit the re-emitted schema with the publisher script (Phase 4 D-20 requires publication commit = authority + outputs + sign-off only; the existing file-set test expects exactly that set), (c) keep the window to the single publisher-code commit, (d) record in the plan that those four tests are expected red from that commit until the publication commit. Do not add a `skipif(version mismatch)`; that is the fail-open the phase exists to remove. This is Open Question 1 for the planner.

### Pitfall 2: `git log --diff-filter=A` finds 0ce89f2, not the 2.0.1 record commit
**What goes wrong:** The publication record is overwritten (status M), so `--diff-filter=A` still returns `0ce89f2`. Reply test `test_record_commit_added_the_publication_record` (L188-191) and any reply-script resolution built on it would silently pin the *old* record commit.
**How to avoid:** use `git log -n1 --format=%H -- <record>` (latest commit touching the file) in both the script and the test, and assert it differs from the publication commit and the publication commit is its ancestor.

### Pitfall 3: Existing 2.0.0 sign-off and record break the dry-run and `--validate` mid-workflow
**What goes wrong:** (a) `publish(dry_run=True)` (P L407-409) validates an existing sign-off against the new authority digest and raises, because the on-disk sign-off is the 2.0.0 record. (b) After `--publish` but before `--record-publication`, `validate_published()` with the IN-07 check would compare the stale 2.0.0 record's digests with the new files and fail. (c) `--validate-signoff` (L447) has the same issue before the new sign-off is written.
**How to avoid:** the dry-run must not validate a sign-off whose `authority_id`/`version` differ from the one being published (simplest: drop the L408 branch; the dry-run job is the summary). For IN-07: enforce the record check when `record['authority_id'] == authority['authority_id']`; a record naming a different authority id is treated as "publication record pending" and skipped. Test all four states (absent, other-version, matching, mismatching). Note the residual risk: an attacker who can edit the record can name another id; the git-gated tests and the reply's pin cover that. Flag in the plan.

### Pitfall 4: `test_dry_run_...`, `valid_signoff`, `test_version_is_2_0_0`, `test_outputs_deterministic...` encode 2.0.0
**What goes wrong:** `valid_signoff` (pub test L176-177) hard-codes `'version': '2.0.0'` and `MODULE.AUTHORITY_ID`; `test_version_is_2_0_0` (authority_v2 L102); `MODULE.PUBLISHED_ON in first[N_CERT]` (pub test L201); `build_all_outputs(a)` without a sign-off (L195, 206, 212). 
**How to avoid:** introduce `VERSION = '2.0.1'` and `AUTHORITY_ID` constants in P and use them in `build_authority` (L124-125), `validate_authority` (L186), `schema()` (L276), `validate_signoff` (L343-344). Update tests to the constants, never string literals.

### Pitfall 5: Two module objects, two `AuthorityError` classes
**What goes wrong:** every consumer loads the publisher with `spec_from_file_location` (B L18, V L17, R L13, and the tests), producing separate module objects. The builder's `V2.AuthorityError` is a different class from the publisher's. `pytest.raises(AuthorityError)` in a publisher test will not catch an error raised by the builder.
**How to avoid:** the lazy loader converts `ValueError` (both are `ValueError` subclasses) into the publisher's `AuthorityError` (Pattern 1). Also: the builder's own path constants (`DECISIONS`, `ANSWERS`, `PROPOSALS`, ...) are NOT affected by monkeypatching the publisher; pass the document/path explicitly.

### Pitfall 6: The D-12 binding needs constants that must not be self-referential
**What goes wrong:** If the validator compares the current decisions digest with `lineage.supersedes.governance_decisions_sha256` read from the 2.0.1 authority itself, the check is circular (same trap as Phase 4 CR-02).
**How to avoid:** hold the 2.0.0 facts as constants in P (`SUPERSEDED_V2_0_0 = {authority_id, version, commit, authority_sha256, governance_decisions_sha256, relative_path}`), generated once from the files (Code Examples), and have a git-gated pytest recompute them from `git show 54a7fd0:...` and `git show 0ce89f2:...` so a mistyped constant fails. `validate_publication` requires: live decisions LF sha == constant; `lineage.supersedes == constant fields`; `lineage.governance_decisions.sha256 == constant`. Verified values (read this session): authority LF sha `de36e227be4ccc95f4a8a8a08247cf6e49f7682908c7f425f8cc02bbaa1da353` (equals `git show 54a7fd0:` LF digest), decisions LF sha `4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f` (equals `git show 54a7fd0:` LF digest and the current file), manifest sha `64c6c0e0dc216ed157962e2bab804e1b6f252fe25838efd76ed98e935b0e1680`, publication commit `54a7fd09114704a97a7a48fce5f89aebeb48c90a`, record commit `0ce89f29ecc2d1ddb1b53f7721524a1ae78df203`. Consequence to note: any future amendment of a decision makes the 2.0.1 validator red until a new version updates the constants; that is intended (D-11/D-12).

### Pitfall 7: v1 lineage fields move; v1 checks must follow
**What goes wrong:** today `lineage.supersedes` is the v1 entry (P L136), checked at L199-200 and L259-261, and asserted by `test_lineage_records_governance_decisions_and_v1` (pub test L67-76) and `test_wrong_v1_lineage_fails` (L135-137). D-08 moves v1 to `v1_baseline` and puts 2.0.0 in `supersedes`.
**How to avoid:** change `build_authority` L136, `validate_authority` L199-200, `validate_publication` L259-261 and `schema()` together, and the two tests. The `commit` for the v1 baseline is currently the 7-char `62a8955` (full: `62a8955dc28d9458cd1167fad314926e057c31fc`, verified by `git rev-parse`); keep `62a8955` unless Oscar prefers the full SHA (Open Question 3). The 2.0.0 commit must be the full 40-char value.

### Pitfall 8: CRLF working copies
**What goes wrong:** scripts are CRLF in the worktree (`git ls-files --eol`: `i/lf w/crlf`), the index is LF. All digests use `lf_digest`, so this is harmless; the risk is only editing tools that fail to match multi-line strings. Do not "fix" line endings (IN-04 is deferred).

### Pitfall 9: Manifest path traversal (small, optional)
`validate_published` reads `ROOT / art['relative_path']` from a committed manifest (P L433). A `..` or absolute path would read outside the repo. Cheap hardening: reject absolute/`..` paths with `contains_absolute` and a `Path(...).parts` check. Optional; flagged under Security.

## Code Examples

### Derive the 2.0.0 constants from files (run once before any overwrite; do not type them)

```bash
python - <<'EOF'
import json, hashlib, subprocess
def show(rev, path): return subprocess.run(['git','show',f'{rev}:{path}'],capture_output=True,check=True).stdout
lf = lambda b: hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()
rec = json.loads(show('0ce89f2','registry/archive_assessment_applicability_authority_v2_publication_record.json'))
auth = show('54a7fd0','registry/archive_assessment_applicability_authority_v2.json')
dec  = show('54a7fd0','registry/archive_assessment_governance_decisions.json')
assert lf(auth) == rec['authority_sha256']
print(rec['publication_commit'], rec['authority_id'], rec['version'], rec['authority_sha256'], rec['manifest_sha256'], lf(dec))
EOF
```
Run against the *committed* revisions, not the working tree, so it still works after the files are overwritten. [VERIFIED by the equivalent values read in this session]

### Semantic checks computed, not asserted (D-17)

```python
# in build_all_outputs, replacing P L376-377 (sketch)
def semantic_conflicts(rows):
    conflicts = []
    for r in rows:   # all 80 rows, not only the 3 rule rows
        for facts in ({}, {f: 'UNKNOWN' for f in RULE_FIELDS}):
            if resolve_applicability(r, facts) == 'NOT_APPLICABLE': conflicts.append((r['control_id'], 'unknown_resolved_not_applicable'))
        if r['not_applicable_decision_state'] == 'RULE_PUBLISHED':
            for st in CONDITION_STATES:
                want = 'NOT_APPLICABLE' if all(c['state'] == st for c in r['not_applicable_rule']['conditions']) else 'APPLICABLE'
                if resolve_applicability(r, {f: st for f in RULE_FIELDS}) != want: conflicts.append((r['control_id'], f'known_{st}_result'))
    return conflicts
# semantic['result'] = 'PASS' if not conflicts else raise AuthorityError; semantic_conflict_count = len(conflicts)
# cert['semantic_conflicts'] = len(conflicts); cert['negative_invariants'] = 'PASS' only if every mutation outcome rejected
# prohibitions: evaluator_executions / hayes_modifications / target_comparisons are facts about the process; either keep 0 as
# documented constants with a one-line pytest asserting the publisher source has no subprocess/evaluator call, or derive them
# from counters that the harness increments (it never calls an evaluator). State which in the plan.
```

### Schema fragments (emit via `schema()`, then `--emit-schema`)

```python
dup_guard = [{'contains': {'properties': {'field': {'const': f}}, 'required': ['field']}, 'minContains': 0, 'maxContains': 1} for f in RULE_FIELDS]
rule = {..., 'properties': {'combination': {'const': COMBINATION}, 'conditions': {'type': 'array', 'minItems': 1, 'maxItems': len(RULE_FIELDS), 'items': cond, 'allOf': dup_guard}}}
sha = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
sup = {'type': 'object', 'additionalProperties': False, 'required': [...], 'properties': {'authority_id': {'const': SUPERSEDED['authority_id']}, 'version': {'const': '2.0.0'}, 'commit': {'const': SUPERSEDED['commit']}, 'relative_path': {'const': rel(AUTHORITY)}, 'sha256': sha, 'governance_decisions_sha256': sha}}
```
[VERIFIED: the `maxContains` construct, run in jsonschema 4.26.0]

### Test that proves "no decision changed" (D-13, git-gated, shallow skip)

```python
@pytest.mark.skipif(git_ready() is not None, reason='git history unavailable')
def test_rows_equal_2_0_0_at_54a7fd0():
    old = json.loads(git('show', '54a7fd0:registry/archive_assessment_applicability_authority_v2.json').stdout)
    new = MODULE.load(MODULE.AUTHORITY)
    assert old['controls'] == new['controls']                      # all 80 rows value-equal
    differ = {k for k in set(old) | set(new) if old.get(k) != new.get(k)}
    assert differ <= {'authority_id', 'version', 'source_lineage'}
```
Use `git_ready()` evaluated at call time inside the test (as `test_publication_commit_ancestor_and_file_set` does) so a shallow clone skips cleanly.

## Plan Ordering (waves) honoring D-21

Autonomy flags: **only the two checkpoints are non-autonomous**. Everything else can run `autonomous: true`. Never `git add -A`.

**Wave 1 (independent, each its own commit, full archive suite green after each)**
1. Docs: `.planning/PROJECT.md` L92 (Constraints) then `CLAUDE.md` L17 Vocabulary line: "Rule conditions use only the first four of the eight declared classification fields (`production`, `internet_exposed`, `contains_customer_data`, `ai_enabled`) ... the other four remain classification prerequisites". PROJECT.md L33 (Validated list) repeats the "eight declared fields" claim; recommend correcting it in the same commit (Open Question 5).
2. Phase 2 WR-01: V + rule_proposals tests (Pattern 5).
3. Builder: WR-10 constants, WR-05 `--supersede-published`, WR-07/WR-08 tests (needs only existing V2 names).
4. Publisher output-neutral gates: CR-01 + WR-04 (sign-off), CR-02 gate + IN-01 (lazy loader), IN-07, WR-09 test. Verified output-neutral: the existing 2.0.0 sign-off (role `EMS_GOVERNANCE_AUTHORITY`, exact statement, valid date, exact key sets, status/version/id) satisfies the stricter checks, the committed decisions file passes `validate_decisions` (review: "decisions file passes the builder validator"; `--validate` PASS this session), and the 2.0.0 record digests match the committed files. So `--validate` and all 397 tests stay green here. Split into 2 commits if desired (sign-off; decisions gate).

**Wave 2 (one coupled commit): "publisher 2.0.1 code"**
- P: `VERSION`/`AUTHORITY_ID`, lineage (`supersedes` = 2.0.0 constants, `v1_baseline`), D-12 binding, mutation harness + computed outputs (D-17..D-20), sign-off-derived date (D-10), manifest `publisher_script` (D-09), WR-02/WR-03 schema, dry-run no longer validating a stale sign-off.
- Run `python scripts/publish_archive_assessment_applicability_authority_v2.py --emit-schema` and include `schemas/archive_assessment_applicability_authority_v2.schema.json` in this commit (not the publication commit).
- Tests updated in the same commit (constants, `valid_signoff`, parametrized mutation test, D-13 git test, dry-run test).
- Expected red after this commit (Pitfall 1): the four real-file tests. Everything else green.

**Wave 3: BLOCKING CHECKPOINT (non-autonomous, `checkpoint:human-verify`), sign-off**
- Executor runs `--publish --dry-run`, shows the D-21 summary: 21 decided/59 undecided; each of the 21 with control, AA4 id, state; the three rules in full (CTRL-030 and CTRL-039 `production = KNOWN_FALSE`, CTRL-052 `ai_enabled = KNOWN_FALSE`); the authority LF sha256; "2.0.1 supersedes 2.0.0 (54a7fd0); no decision changed: decisions-file LF sha256 equals the 2.0.0 value". Neutral wording only; avoid `best`, `critical`, `important`, `recommended`, `highest` (the dry-run test forbids them).
- Resume signal from Oscar Mack must supply: approval, the approval date, and the scope text. Executor then writes `registry/archive_assessment_applicability_authority_v2_signoff.json` with keys exactly `status` (`PUBLICATION_SIGNOFF`), `approval{approver:'Oscar Mack', role:'EMS_GOVERNANCE_AUTHORITY', date, scope}`, `dual_role_statement` (exact), `authority_id`, `version`, `authority_sha256`, `authority_sha256_normalisation:'CRLF_TO_LF'`. Never infer the date or approval.

**Wave 4: publication (autonomous after the checkpoint)**
- `--publish`, then `--validate` (record check skipped while the record is the stale 2.0.0 one, Pitfall 3), then stage by explicit path: `registry/archive_assessment_applicability_authority_v2.json`, `registry/archive_assessment_applicability_authority_v2_signoff.json`, and `git add -f generated/archive-assessment/ems-aa3-v2/<each file>` (gitignored dir; the `.gitattributes` rule `generated/archive-assessment/ems-aa3-v2/** text eol=lf` already exists). `git show --stat HEAD` must list exactly 2 + 7 files (authority, sign-off, 7 outputs incl. manifest). Check `git diff --cached --name-only` before committing.
- Record commit: `--record-publication <full sha>`, `--validate` (now strict), commit only the record file.

**Wave 5: reply (autonomous)**
- Reply script commit (IN-01..IN-06, history note, schema, tests), `--emit-schema`, then `--build`, `--validate`, commit script+tests+schema in one commit and the regenerated `docs/DEMO3_W1_REQ_001_REPLY.md` + `registry/archive_assessment_demo3_w1_req_001_reply.json` in the next (so the reply files are separable from code).
- Must come after publication: the reply tests read the real 2.0.1 files and `source_lineage.supersedes`.

**Wave 6: BLOCKING CHECKPOINT (non-autonomous), read-through** of the regenerated reply: the 21 first-sentence "Reason:" lines (WR-07 from Phase 5), the history note, the reworded "Hayes's resolver resolves no control..." passage, `send_condition`. Final step only reports `git push origin feature/ems-aa3-archive-applicability-authority` and the read-only `--push-check`; never runs a push.

## Current Shapes (read this session, for the planner)

- **Lineage (2.0.0)**: keys `aa1_manifest_sha256`, `aa2_closure_sha256`, `aa2_approval_sha256`, `catalog_reference{relative_path,sha256,required_for_deterministic_compilation:false}`, `supersedes{authority_id:'...-1.0.0',version:'1.0.0',commit:'62a8955',relative_path,sha256:'f084607c...'}`, `digest_normalisation`, `governance_decisions{relative_path,sha256:'4e746d1f...',record_count:21,drafting_commit:'dc3b41c9...'}`. The three `aa*` digests come from the v1 file (P L134); the 2.0.1 schema should declare them with sha256 patterns (they are not `required` today; D-08 lists the required set without them: keep them optional-but-patterned, or require them if all are always present).
- **Manifest (2.0.0)**: `manifest_type`, `published_on`, `authority_id`, `digest_normalisation`, `artifacts[10]` (script, schema, authority, sign-off, 6 outputs; no manifest self-entry), `self_entry_exclusion_reason`.
- **Certification**: `certification_type`, `certification_version`, `published_on`, `authority_id`, `version`, `authority_sha256`, `schema_sha256`, `signoff_path`, `signoff_sha256`, `digest_normalisation`, `control_population`, `decided_control_count`, `undecided_control_count`, `semantic_conflicts: 0`, `negative_invariants: 'PASS'`, `prohibitions{evaluator_executions,hayes_modifications,target_comparisons: 0}`.
- **Publication record**: exactly `{publication_commit, authority_id, version, authority_sha256, manifest_sha256, digest_normalisation}` (asserted by `test_write_publication_record`, pub test L340). Keep this shape.
- **Reply consumption of the publisher**: R uses `V2.latest_records`, `V2.REQUEST_CONTROL_IDS`, `V2.validate_signoff`, `V2.APPROVER_ROLES`, `V2.rel`, `V2.AUTHORITY/SCHEMA/OUT/SIGNOFF/PUBLICATION_RECORD/GOVERNANCE_DECISIONS`, `V2.N_MANIFEST/N_TRACE`, `V2.DECISION_STATES/DECISIONS`, `V2.RULE_FIELDS/CONDITION_STATES/COMBINATION/AUTHORITY_ID_RE`, `V2.rule_text/jtext/lf_digest/lf_bytes/load/dump/write_text/contains_absolute/DUAL_ROLE_STATEMENT/AuthorityError`. Keep all of these names and signatures stable. `PUBLISHED_ON` is not used by R (grep), so its removal does not ripple. `validate_signoff(record, authority_lf_digest)` signature must not change.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | everything | yes | 3.12.10 | — |
| git (history incl. `dc3b41c`, `54a7fd0`, `0ce89f2`, `62a8955`) | D-13 test, constants derivation, D-03 drifted-catalog path | yes; `rev-parse --is-shallow-repository` = false; all four commits resolve | — | shallow clone: tests skip (existing pattern); D-03 skips only the drifted-catalog sub-check |
| jsonschema | schema validation, `maxContains` | yes | 4.26.0 | — |
| pytest | tests | yes | — | — |
| git remote `origin` / branch on remote | `--push-check` only | not required to succeed (branch not on remote: exit 2 by design) | — | none needed; push is manual |
| Context7/ctx7, Brave, Exa, Firecrawl | n/a | not used | — | repo is self-contained |

Missing dependencies with no fallback: none.

## Validation Architecture

(`workflow.nyquist_validation` is `false` in `.planning/config.json`; this section is included because the orchestrator asked for per-fix test commands.)

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (Python 3.12.10) |
| Config file | none (no pytest.ini/pyproject) |
| Quick run | `python -m pytest tests/test_archive_assessment_applicability_authority_v2_publication.py -q -p no:cacheprovider --basetemp="$TEMP/pt-a6"` |
| Full archive-assessment suite | `python -m pytest tests/test_archive_assessment_*.py -q -p no:cacheprovider --basetemp="$TEMP/pt-a6"` |

**Working command on this machine** [VERIFIED: ran in this session]: `python -m pytest tests/test_archive_assessment_*.py -q -p no:cacheprovider --basetemp="$TEMP/pt-research"` printed `397 passed in 34.22s` (git-bash glob expansion; in PowerShell use `$env:TEMP\pt-a6` and pass the glob via `(Get-ChildItem tests/test_archive_assessment_*.py).FullName`, or run `python -m pytest tests -k archive_assessment`). Keep `--basetemp` OUTSIDE the repo so no new `.pytest-*` directory appears in `git status`. Existing modules and counts: authority 12, authority_v2 71, v2_publication 54, reply 32, governance_answers 51, governance_decisions 89, rule_proposals 75, rule_proposals_record 13 (= 397). New tests must use a module-level `tempfile.TemporaryDirectory()` (as the reply and decisions tests do) instead of `tmp_path`.

CLI validators (all print `PASS` today, verified): 
`python scripts/publish_archive_assessment_applicability_authority_v2.py --validate`,
`python scripts/build_archive_assessment_governance_decisions.py --validate`,
`python scripts/validate_archive_assessment_rule_proposals.py --validate` and `--validate-record`,
`python scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate`.

### Phase Requirements -> Test Map (per fix)

| Item | Behavior | Test type | Command |
|------|----------|-----------|---------|
| CR-01 | role `HAYES_VERIFY_DEVELOPER` rejected | unit | `pytest tests/test_archive_assessment_applicability_authority_v2_publication.py -k signoff` |
| CR-02, IN-01 | tampered / malformed decisions rejected by both publish path and `validate_published` | unit | `pytest ...v2_publication.py -k "governance or malformed"` |
| WR-01, D-17..D-20 | every mutation rejected, outcomes recorded, accepted mutation aborts the build, recorded file equals observed | parametrized unit | `pytest ...v2_publication.py -k mutation` |
| WR-02, WR-03 | schema-only rejection of missing lineage and duplicate field | unit | `pytest tests/test_archive_assessment_applicability_authority_v2.py -k "schema or duplicate"` |
| WR-04 | exact sign-off checks | unit | `-k signoff` |
| WR-05, WR-08 | `--build` refusal / `--supersede-published` via `main()` | unit | `pytest tests/test_archive_assessment_governance_decisions.py -k "wr05 or wr07 or build_cli"` |
| WR-06, D-09, D-10 | script edit does not break validate; date from sign-off; hand edit + re-hash still fails | unit | `pytest ...v2_publication.py -k "validate or published_on or script"` |
| WR-07 | emit-template refusal with `sys.executable` + stderr text | unit | `pytest tests/test_archive_assessment_governance_decisions.py -k emit_template` |
| WR-09 | source-scoped generated-dir guard | unit | `pytest tests/test_archive_assessment_applicability_authority_v2.py -k generated_dir` |
| WR-10 | builder constants equal publisher constants | unit | `pytest tests/test_archive_assessment_governance_decisions.py -k constants` |
| IN-07 | record digest check (4 states) | unit | `pytest ...v2_publication.py -k record` |
| D-03 | frozen proposals valid despite catalog drift; shallow skip | unit + git-gated | `pytest tests/test_archive_assessment_rule_proposals.py tests/test_archive_assessment_rule_proposals_record.py` |
| D-12, D-13 | decisions digest == 2.0.0 constant; 80 rows equal `54a7fd0` | unit + git-gated | `pytest ...v2_publication.py -k "supersed or 54a7fd0"` |
| D-04 | CLAUDE.md/PROJECT.md wording | grep | `git grep -n "eight declared" -- CLAUDE.md .planning/PROJECT.md` must return nothing |
| D-14..D-16, IN-01..06 (reply) | reply cites 2.0.1, history note, no WR-01 caveat, full 40-hex record commit, CLI flags exclusive | unit | `pytest tests/test_archive_assessment_demo3_w1_req_001_reply.py` |
| D-22 | publication commit file set | git-gated | `pytest ...v2_publication.py -k file_set` (expects authority, sign-off and the 7 outputs only) |

### Sampling Rate
- Per task commit: the module(s) touched (30s-class).
- Per wave merge and phase gate: the full archive-assessment suite (about 35s) plus all five CLI `--validate` commands. Expected total after the phase: 397 + new tests; none skipped on this non-shallow machine.
- After Wave 2 the four real-file tests are expected red until Wave 4 (Pitfall 1).

### Wave 0 Gaps
None for framework. New tests are added alongside each fix (module-level temp dir pattern).

## Security Domain

`security_enforcement` is enabled (config). ASVS level 1.

| ASVS Category | Applies | Control |
|---------------|---------|---------|
| V2 Authentication | no (no login) | — |
| V3 Session | no | — |
| V4 Access Control | yes (authority) | CR-01: sign-off role must equal `EMS_GOVERNANCE_AUTHORITY`; approver must equal `Oscar Mack`; dual-role statement exact |
| V5 Input Validation | yes | `jsonschema` 2020-12 + fail-closed Python validators; exact key sets (WR-04); reject absolute paths (`contains_absolute`) |
| V6 Cryptography | yes (integrity only) | stdlib `hashlib.sha256` over LF-normalised bytes; never hand-roll; no secrets |
| V10 Integrity / tamper evidence | yes | sign-off digest binds authority; manifest binds artifacts; publication record binds manifest (IN-07); git-gated ancestor tests |

Known threat patterns:

| Pattern | STRIDE | Mitigation |
|---------|--------|------------|
| Sign-off made in the consumer (Hayes) role | Spoofing / Elevation | CR-01 equality check |
| Forged or edited decision records cited as authority | Tampering | CR-02 gate + D-12 digest binding to the 2.0.0 value |
| Consistent hand edit + re-hash of an artifact | Tampering | rebuild-and-compare (existing) + record digest check (IN-07) + git ancestor test |
| Certification claims not backed by execution | Repudiation / Info | D-17 executed checks and recorded `rejected_by` |
| Manifest `relative_path` with `..` or absolute path reading outside the repo | Tampering | optional: reject non-relative / `..` paths in `validate_published` (Pitfall 9) |
| Stale record bypass (Pitfall 3 residual) | Tampering | git-gated pytest and reply pin; document the limitation |

## State of the Art

| Old approach (2.0.0) | New (2.0.1) | Impact |
|----------------------|-------------|--------|
| Fixed strings for `PASS`/`REJECTED_FAIL_CLOSED` | Computed from executed mutations and semantic checks | Hayes can rely on certification fields as evidence |
| Script digest part of rebuild compare | Recorded in manifest, compared to recorded value | Script-only edits no longer turn `--validate` red |
| Code constant `PUBLISHED_ON` | Sign-off approval date | Date bound by the sign-off digest |
| `supersedes` = v1 | `supersedes` = 2.0.0, `v1_baseline` = v1 | Version history explicit in the authority |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The Hayes side reads the negative-invariant output's `mutation` key, so it should be kept alongside the new `id` | Pattern 2 | Low: an extra key is harmless; dropping it could break a consumer. [ASSUMED] |
| A2 | Moving the script entry out of manifest `artifacts` into `publisher_script` is acceptable to Hayes (no known reader of `artifacts[0]`) | Pattern 4 | Medium: if Hayes iterates `artifacts` expecting the script. Alternative is to keep it in `artifacts` and skip it in the live-file loop. [ASSUMED] |
| A3 | Skipping only the drifted-catalog sub-check on a shallow clone (with a printed notice) satisfies "skips cleanly" in D-03 | Pattern 5 | Low-medium: Oscar may want a hard failure instead. [ASSUMED] |
| A4 | A stale record naming another authority id may be ignored by IN-07 during the publish->record window | Pitfall 3 | Medium: weakens IN-07 slightly; alternative is a `--pending-record` CLI flag that must be passed explicitly. [ASSUMED] |
| A5 | Reply date should follow the sign-off approval date rather than stay at the typed `2026-10-14` | Open Question 2 | Low |
| A6 | Optional extension of WR-03 to the builder's `rule_schema()` is not needed because the validator already rejects duplicates and the answers schema file must stay untouched | Anti-patterns | Low |

## Open Questions (RESOLVED)

1. **Red window between the publisher-code commit and the publication commit.**
   - RESOLVED: user-locked 2026-10-14 - a documented red window is accepted, listed explicitly in plan 06-05, no skip shims.
   - Known: output-affecting publisher changes make the committed 2.0.0 files fail validation (four tests + CLI `--validate`) until 2.0.1 is published; Phase 4 D-20 forbids bundling code and publication.
   - Unclear: whether Oscar accepts a documented short red window or wants the tests to stay green by other means.
   - Recommendation: accept and document (do not add version-mismatch skips); keep the window to one commit.
2. **Reply date.** `REPLY_DATE` (R L20) is typed `2026-10-14`. Recommend deriving it from the 2.0.1 sign-off approval date (a value from a file, per D-05's "never typed" spirit), or have the planner confirm a fixed date.
   - RESOLVED: user-locked - the reply date is the approval date of the 2.0.1 sign-off record (plan 06-08).
3. **`v1_baseline.commit` form.** Keep the existing 7-char `62a8955` (matches Phase 4 D-13 and the v1 lineage today) or switch to `62a8955dc28d9458cd1167fad314926e057c31fc`. Either satisfies "pin with const"; the abbreviation is ambiguity-prone long-term.
   - RESOLVED: full 40-hex `62a8955dc28d9458cd1167fad314926e057c31fc` as a publisher constant, verified by a git-gated test (plan 06-05).
4. **Where the Phase 2 frame pin lives** (Pattern 5 step 2): digest-bound-to-record vs an added `FROZEN_FRAME_SHA256` constant. Recommendation: both (record binding is the non-git anchor, constant gives a drift tripwire).
   - RESOLVED: both - drafting-record binding plus `FROZEN_FRAME_SHA256` (plan 06-02).
5. **PROJECT.md line 33** (a Validated item) repeats the "eight declared classification fields" claim in addition to the Constraints line named in D-04. Recommend correcting both in the D-04 commit; planner to confirm it is within "the same correction".
   - RESOLVED: both PROJECT.md lines (L33, L92) and CLAUDE.md L17 are corrected (plan 06-01).
6. **Sign-off inputs** (date, scope sentence) must come from Oscar Mack at the checkpoint, not from the executor.
   - RESOLVED: sign-off date, approval and scope come only from the checkpoint reply (plan 06-06).

## Sources

### Primary (HIGH confidence, read or executed in this session)
- `scripts/publish_archive_assessment_applicability_authority_v2.py`, `scripts/build_archive_assessment_governance_decisions.py`, `scripts/validate_archive_assessment_rule_proposals.py`, `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` (full reads, line numbers above)
- `tests/test_archive_assessment_applicability_authority_v2.py`, `..._v2_publication.py`, `..._demo3_w1_req_001_reply.py`, `..._governance_decisions.py` (relevant sections), `..._rule_proposals_record.py`, `..._rule_proposals.py` (relevant sections)
- `.planning/phases/04-certified-publication/04-REVIEW.md`, `04-CONTEXT.md`; `02-REVIEW.md` WR-01; `05-REVIEW.md`, `05-REVIEW-FIX.md`; `.planning/v1.0.0-MILESTONE-AUDIT.md`; `.planning/config.json`
- Registry/generated files at the working tree and `git show 54a7fd0:`, `0ce89f2` (digests verified)
- Executed: full archive suite (397 passed), five `--validate` CLIs (PASS), jsonschema `maxContains` probe (4.26.0), blob-id computation, timing of validators

### Secondary / Tertiary
- None. No web sources were needed; behaviour was verified locally.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, no new packages; versions verified.
- Architecture / fix shapes: HIGH for locations and shapes; MEDIUM for choices flagged A1-A4 (design discretion).
- Pitfalls: HIGH for 1-5 and 7 (derived from reading the code/tests; Pitfall 1's red set was reasoned from code, not executed, since no code was changed); MEDIUM for the residual-risk notes.

**Research date:** 2026-10-14
**Valid until:** until any of the four scripts or the v2 files change (repo-local research); otherwise 30 days.
