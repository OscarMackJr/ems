---
phase: 04-certified-publication
reviewed: 2026-10-14T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - scripts/publish_archive_assessment_applicability_authority_v2.py
  - scripts/build_archive_assessment_governance_decisions.py
  - schemas/archive_assessment_applicability_authority_v2.schema.json
  - schemas/archive_assessment_governance_decisions.schema.json
  - tests/test_archive_assessment_applicability_authority_v2.py
  - tests/test_archive_assessment_applicability_authority_v2_publication.py
  - tests/test_archive_assessment_governance_decisions.py
  - .gitattributes
findings:
  critical: 2
  warning: 10
  info: 7
  total: 19
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-10-14
**Depth:** standard (phase-4 diff `a3bccb8..HEAD`)
**Files Reviewed:** 8
**Status:** issues_found

## Summary

I reviewed the v2 publisher (overlay, `validate_publication`, sign-off, publish, dry-run, rebuild-compare validate, publication record), the decisions builder hardening (LF digests, answers binding, supersession, refresh), both schemas, the three test modules and `.gitattributes`.

Baseline checks, all read-only: 214 tests pass. `publish_..._v2.py --validate` and `build_..._governance_decisions.py --validate` both return PASS. The data published at 54a7fd0 is internally consistent: the sign-off role is `EMS_GOVERNANCE_AUTHORITY` and the decisions file passes the builder validator.

The defects are in the gates, not the current data. I tested each gap in memory (no files written) and each one was accepted:

- `validate_signoff` accepts a sign-off with `role: HAYES_VERIFY_DEVELOPER`, an invalid date (`not-a-date`), and text appended after the dual-role statement.
- `build_published_authority` + `validate_publication` + `schema()` accept a governance-decisions document whose records all have `approver: "Someone Else"`, an empty `dual_role_statement` and `disposition: "BOGUS"`.
- The published v2 schema accepts an authority with no `source_lineage.governance_decisions`.
- The published v2 schema accepts a rule that names `production` twice, with opposite states.

The certification artifacts also hard-code `PASS` and `REJECTED_FAIL_CLOSED` results that the publisher never computes.

## Critical Issues

### CR-01: Sign-off gate accepts approval in the Hayes Verify developer role

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:310,340`
**Issue:** `validate_signoff` checks `appr.get('role') not in APPROVER_ROLES`, and `APPROVER_ROLES = ['EMS_GOVERNANCE_AUTHORITY', 'HAYES_VERIFY_DEVELOPER']`. So a publication sign-off made in the consumer (Hayes) role passes the gate, even though the error text says "not an approved EMS governance role". This breaks the project constraint that Oscar Mack approves as the EMS governance authority, and it blurs the dual-role separation the records are meant to make explicit. `APPROVER_ROLES` is correct as the list of roles the approver holds (`approver_roles` on decision records). It is wrong as the set of roles allowed to approve. The shipped sign-off is not affected, because it uses `EMS_GOVERNANCE_AUTHORITY`. The gate itself is fail-open. Tested in memory: a sign-off with `role: HAYES_VERIFY_DEVELOPER` was accepted.
**Fix:**
```python
SIGNOFF_ROLE = 'EMS_GOVERNANCE_AUTHORITY'
...
if appr.get('role') != SIGNOFF_ROLE: errors.append('sign-off role must be EMS_GOVERNANCE_AUTHORITY')
```
Add a test in `test_signoff_value_mutations_fail` that sets `role` to `HAYES_VERIFY_DEVELOPER` and expects rejection.

### CR-02: Publisher never validates the governance-decisions file it cites as authority

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:151-164, 227-229, 399-402`
**Issue:** `build_published_authority` reads `registry/archive_assessment_governance_decisions.json` and copies `decided_outcome` and `decided.rule` into the authority. Nothing checks the records. `validate_publication` only cross-checks the authority against that same file: digest, record count, drafting commit, latest record per control. Those checks are circular, since all of those values were derived from the file just loaded. It never calls `validate_decisions` from the builder, so the publication gate does not enforce any of the following:
- `approver == 'Oscar Mack'`
- `dual_role_statement` equals the approved text
- `disposition` is in the allowed set
- `drafted` matches the frozen proposals
- `answers_sha256` matches the answers file
- supersession is well-formed

Tested in memory: a decisions document with every record set to `approver: "Someone Else"`, `dual_role_statement: ""` and `disposition: "BOGUS"` passed `build_published_authority`, `validate_publication` and `schema()`. The dry-run summary that the human signs shows none of these fields. So the sign-off digest binds an authority that cites unverified, possibly unapproved records as its "named authority". This is the core value Hayes relies on.
**Fix:** Make the publication gate run the decisions validator and the decisions schema before any build, in both `published_authority_checked()` and `validate_published()`:
```python
def validate_governance_decisions() -> dict:
    spec = importlib.util.spec_from_file_location('aa_gov_decisions', ROOT / 'scripts' / 'build_archive_assessment_governance_decisions.py')
    B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
    doc = load(GOVERNANCE_DECISIONS)
    B.validate_decisions(doc)
    jsonschema.Draft202012Validator(load(B.DECISIONS_SCHEMA)).validate(doc)
    return doc
```
The builder already imports this module at load time. To avoid a circular import, either move `validate_decisions` into a shared module or import lazily inside the function, as shown. At minimum, check `approver`, `approver_roles`, `dual_role_statement`, `disposition` and `decided_outcome` against `decided.rule` per record inside `validate_publication`. Add a negative test with a tampered approver.

## Warnings

### WR-01: Certification artifacts assert PASS / REJECTED_FAIL_CLOSED without computing them

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:320, 377-378, 385`
**Issue:**
- The semantic output hard-codes `'result': 'PASS'` and `'semantic_conflict_count': 0`, even when its own computed `unknown_never_not_applicable` were `False`.
- The negative-invariant output lists all 17 `NEGATIVE_MUTATIONS` as `REJECTED_FAIL_CLOSED`, but the publisher never runs any of them. They exist only as pytest cases.
- The certification hard-codes `semantic_conflicts: 0`, `negative_invariants: 'PASS'` and `prohibitions: {... 0}`.

A hash-certified artifact consumed by an external assessor is therefore claiming results that are fixed strings, not results of executed checks.
**Fix:** Run each mutation inside `build_all_outputs`: apply it to a deep copy and assert that `validate_publication` and/or the schema raise. Record the actual outcome, derive `result` from the outcomes, and raise `AuthorityError` if any mutation is accepted or `unknown_never_not_applicable` is false. Otherwise, rename the fields so they cite the pytest module rather than asserting a result.

### WR-02: v2 schema does not require the governance and v1 lineage

**File:** `schemas/archive_assessment_applicability_authority_v2.schema.json` (`source_lineage`), generated by `scripts/publish_archive_assessment_applicability_authority_v2.py:279`
**Issue:** `source_lineage` declares `governance_decisions` under `properties` but has no `required`, and `supersedes` / `catalog_reference` are not constrained at all. A consumer that validates with the published schema alone (Hayes reads EMS read-only) would accept an authority with no decision lineage. Confirmed in memory: popping `governance_decisions` still passes `schema()`. Only the Python validator rejects it, and `test_missing_governance_lineage_fails` does not pass `schema_too=True`.
**Fix:** Add `'required': ['governance_decisions', 'supersedes', 'catalog_reference', 'digest_normalisation']` to `source_lineage`, and give `supersedes` a schema (`commit` const `62a8955`, `version` const `1.0.0`, `sha256` pattern). Then re-emit the schema and republish. Republishing is a coordinated hash change, so plan it as a v2.0.1 / re-sign-off.

### WR-03: Schema allows a field to appear twice in one rule

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:268` (also `build_archive_assessment_governance_decisions.py:188`)
**Issue:** `semantics()` publishes `field_may_appear_once: True`, but the rule schema only bounds `conditions` to 1..4 items. Confirmed in memory: `[{production, KNOWN_FALSE}, {production, KNOWN_TRUE}]` passes `schema()`. A contradictory rule like this can never be met, so it silently means "never NOT_APPLICABLE". A schema-only consumer would accept it.
**Fix:** Express uniqueness of `field` in the schema. One way is `'uniqueItems': True` plus one `contains`/`maxContains: 1` per field:
```python
'allOf': [{'contains': {'properties': {'field': {'const': f}}}, 'minContains': 0, 'maxContains': 1} for f in RULE_FIELDS]
```

### WR-04: Sign-off date, scope and dual-role statement are only loosely validated

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:336-342`
**Issue:**
- `date` and `scope` only need to be truthy, so `date: "not-a-date"` passes (confirmed).
- `DUAL_ROLE_STATEMENT not in dr` is a substring test, so `"<statement> Retracted."` passes (confirmed).
- The record may also carry arbitrary extra keys.

The builder has `is_date()` and exact-equality checks for the same statement, so the two gates hold the same text to different standards.
**Fix:** Use `dr != DUAL_ROLE_STATEMENT`, validate `date` with `date.fromisoformat` and the `DATE_RE` pattern, and require `set(record) == {...}` and `set(appr) == {'approver','role','date','scope'}`.

### WR-05: `--build` can silently rewrite the decisions file under a published, hash-certified authority

**File:** `scripts/build_archive_assessment_governance_decisions.py:350-356, 377-386`
**Issue:** `refreshable` ignores `answers_sha256`, so any edit to the answers file that leaves records unchanged or only appends lets `--build` rewrite the decisions file. Whitespace or key reordering counts as such an edit. The publisher binds `lf_digest(GOVERNANCE_DECISIONS)` into the v2 authority, and the sign-off binds the authority digest. After any such rewrite, `publish_..._v2.py --validate` fails ("published authority differs from a fresh build"). The builder gives no warning that it has just broken the certified publication. This is the "uncoordinated hand edit" failure mode the project constraints call out.
**Fix:** In `--build`, if `registry/archive_assessment_applicability_authority_v2.json` exists and its `source_lineage.governance_decisions.sha256` equals the current decisions file digest, refuse to rewrite unless an explicit `--supersede-published` flag is passed. Print that a v2 republish and re-sign-off are required.

### WR-06: Any edit to the publisher script breaks `--validate` of the published authority; publication date is a code constant

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:304, 392, 425-433`
**Issue:**
- The manifest includes `lf_digest(SCRIPT)`, and `validate_published` compares the generated files to a fresh build that uses the current script digest. Any later change to the script, even a fix for CR-01, CR-02 or WR-04, makes `--validate` fail against the files committed at 54a7fd0. A pinned-commit consumer is unaffected, but the repo's own validation goes red.
- `PUBLISHED_ON = '2026-10-14'` is hard-coded, so a republish after superseding decisions carries the stale date unless the code is edited, which again changes the script digest.

**Fix:** Have `--validate` check the manifest against the committed artifacts, not against a rebuild with the live script digest. Alternatively, record the script digest at publication time and compare to that. Move `PUBLISHED_ON` into the sign-off record (approval date) or a CLI argument, and bind it through the sign-off.

### WR-07: Emit-template test can pass without running the script

**File:** `tests/test_archive_assessment_governance_decisions.py:445-449`
**Issue:** `subprocess.run(['python', ...])` uses whatever `python` is first on PATH, not the interpreter running pytest. If that interpreter lacks `jsonschema` or is Python 2, the import fails with exit code 1, and `returncode != 0` passes the test without testing anything. On Windows, `python` may also resolve to the Store alias.
**Fix:** Use `sys.executable`, and assert on the specific message: `assert 'already exists' in result.stderr`.

### WR-08: Test named "build CLI appends" never runs the CLI

**File:** `tests/test_archive_assessment_governance_decisions.py:421-427`
**Issue:** `test_wr07_build_cli_appends_superseding_record` only calls `refreshable()` and never runs `main(['--build'])`. The actual write path in `main()` (lines 379-385) has no test coverage: the refresh rewrite, the CRLF-to-LF rewrite, and the refusal to rewrite. `monkeypatch` is accepted and never used.
**Fix:** Monkeypatch `MODULE.DECISIONS` and `MODULE.ANSWERS` to temporary paths, set `sys.argv = ['x', '--build']`, call `MODULE.main()`, and assert the file now holds 22 records. Add a refusal case where record 0 is changed.

### WR-09: Guard test weakened to near-vacuous strings

**File:** `tests/test_archive_assessment_applicability_authority_v2.py:136-138`
**Issue:** `test_v2_builder_does_not_use_generated_dir` used to assert `'generated' not in src`. Phase 4 added `OUT = ROOT / 'generated' / ...`, so the assertion was changed to `"'ems-aa3'"` and `'AA2 / '`. Those strings were never likely to appear. The test no longer checks that `build_authority()` / `build_published_authority()` are independent of generated output, which is what its name claims.
**Fix:** Scope the check to the build functions: `src = inspect.getsource(MODULE.build_authority) + inspect.getsource(MODULE.build_published_authority); assert 'generated' not in src and 'OUT' not in src`.

### WR-10: Governance constants duplicated across the two scripts

**File:** `scripts/build_archive_assessment_governance_decisions.py:31-33, 56` vs `scripts/publish_archive_assessment_applicability_authority_v2.py:21, 309-311`
**Issue:** `APPROVER`, `APPROVER_ROLES`, `DUAL_ROLE_STATEMENT` and the 21-ID list (`CONTROL_IDS` / `REQUEST_CONTROL_IDS`) are defined twice. The builder already imports the publisher as `V2`. If the copies drift, the decisions file and the sign-off would be validated against different approved text or a different control set, and no test compares them.
**Fix:** In the builder, use `CONTROL_IDS = V2.REQUEST_CONTROL_IDS`, `APPROVER = V2.APPROVER` and so on, or add a test asserting the copies are equal.

## Info

### IN-01: Malformed decision records raise KeyError, not AuthorityError

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:156-163, 250-251`
**Issue:** `r['control_id']`, `r['decided']['rule']`, `r['decided_outcome']` and `doc['drafting_commit']` are read by direct key access. A record missing one of these keys causes a raw `KeyError`/`TypeError` instead of the domain `AuthorityError`. It still fails closed, but the error does not match the project's fail-closed convention. Fixing CR-02 resolves this.

### IN-02: Module-level shared temporary directory in tests

**File:** `tests/test_archive_assessment_governance_decisions.py:30-31`
**Issue:** One `TemporaryDirectory()` is shared by all tests, with fixed file names (`a.json`, `decisions.json`, `wr07_decisions.json`). This couples tests through shared state, and cleanup relies on interpreter exit. Use the `tmp_path` fixture.

### IN-03: CRLF digest test does not feed CRLF input to the builder

**File:** `tests/test_archive_assessment_governance_decisions.py:293-300`
**Issue:** The CRLF copies are written to TMP but `built()` still reads the real LF files. Because LF and CRLF digests are identical for those files, the test cannot tell `digest` and `lf_digest` apart in the builder. `monkeypatch` is unused. Monkeypatch `MODULE.PROPOSALS` / `MODULE.DRAFTING_RECORD` to the CRLF copies before building.

### IN-04: Working tree has CRLF copies of files now marked `eol=lf`

**File:** `.gitattributes:1,12,13`
**Issue:** `git ls-files --eol` shows `w/crlf attr/text eol=lf` for `registry/archive_assessment_governance_answers.json`, `schemas/archive_assessment_not_applicable_rule_proposals.schema.json` and `schemas/archive_assessment_rule_proposals_drafting_record.schema.json`. The index is LF and `lf_digest` hides the difference, so nothing breaks now. A fresh checkout would differ from this working tree. Also, the v1 authority, `control_catalog.yaml` and the v2 publisher script are digested into the lineage or manifest but are not covered by the attributes. They depend entirely on CRLF-to-LF normalisation, and a lone `\r` would not be normalised.

### IN-05: Tautological meta-test

**File:** `tests/test_archive_assessment_governance_decisions.py:442-443`
**Issue:** `test_wr09_answers_sha_binding_test_still_present` only asserts that another test's name is in `globals()`. It adds nothing a reviewer can rely on. Remove it.

### IN-06: Publish writes are not atomic

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:413-414`
**Issue:** The authority is written first, then the seven outputs one by one. A failure partway leaves a mixed state that `--validate` would reject, with no rollback. Consider writing to a temporary directory and replacing it in one step.

### IN-07: `--validate` does not check the publication record

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:417-434`
**Issue:** `validate_published` never reads `PUBLICATION_RECORD`, so a hand-edited `authority_sha256` or `manifest_sha256` in the record is caught only by the git-dependent pytest, which is skipped on shallow clones. Add a check that, when the record exists, its digests equal `lf_digest(AUTHORITY)` and `lf_digest(OUT / N_MANIFEST)`.

---

_Reviewed: 2026-10-14_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
