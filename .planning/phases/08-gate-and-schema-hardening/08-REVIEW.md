---
phase: 08-gate-and-schema-hardening
reviewed: 2026-11-12T00:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
  - scripts/build_archive_assessment_governance_decisions.py
  - scripts/publish_archive_assessment_applicability_authority_v2.py
  - tests/test_archive_assessment_applicability_authority_v2.py
  - tests/test_archive_assessment_applicability_authority_v2_publication.py
  - tests/test_archive_assessment_demo3_w1_req_001_reply.py
  - tests/test_archive_assessment_governance_answers.py
  - tests/test_archive_assessment_governance_decisions.py
  - tests/test_archive_assessment_lineage_validation.py
findings:
  critical: 1
  warning: 7
  info: 9
  total: 17
status: issues_found
---

# Phase 8: Code Review Report

**Reviewed:** 2026-11-12
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

I reviewed the diff `4ff177a..HEAD` across `scripts/` and `tests/` against decisions D-01..D-13 in `08-CONTEXT.md`. The main changes are in place:
- the pre-publication flag;
- the mandatory record gate with a commit-blob check (D-03);
- the narrowed mutation gates;
- catalog reads pinned through `git_show`;
- the shallow-clone guard;
- the digest-grandfathered `norm_templated` uniqueness check;
- `additionalProperties: false` at three schema levels.

Some gaps remain:
- The new publication-record gate never checks the value of `digest_normalisation`. This is the same kind of digest-scope declaration error that the 2.0.2 notice is meant to correct.
- The pre-publication anchor reuses the `SUPERSEDED_V2_0_0` constant, and its error messages hard-code "2.0.0".
- The narrowed mutation gate still counts environment failures from git as domain rejections.
- The validators can still crash with non-domain exceptions on a malformed committed authority.
- The "closed" schema still accepts open nested objects and optional rows and fields that Python requires.
- Several D-10 and D-13 tests only partly prove what the decisions require.

The three known red tests are not counted here.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: Publication record `digest_normalisation` value is never validated

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:689-704`
**Issue:** `check_publication_record` requires the key set to equal `RECORD_KEYS`, which includes `digest_normalisation`. It then checks `authority_id`, `version`, `publication_commit`, `authority_sha256` and `manifest_sha256`, but never the value of `digest_normalisation`. Both digests are recomputed only under `CRLF_TO_LF` (`lf_digest`, `lf_bytes(git_show(...))`). A record that says `"digest_normalisation": "RAW_BYTES"`, or any other string or type, still passes plain `--validate` and `--validate --pre-publication`. Hayes reads this record at the pinned commit. The milestone exists to correct exactly this kind of mismatch between a declared normalisation and the actual one (the 2.0.1 global `CRLF_TO_LF` error), so the new mandatory gate should not let it through.
**Fix:**
```python
if not isinstance(record, dict) or set(record) != RECORD_KEYS: raise AuthorityError('publication record must be an object with exactly the six record keys')
if record['digest_normalisation'] != 'CRLF_TO_LF': raise AuthorityError('publication record digest_normalisation must be CRLF_TO_LF')
```
Add a parametrised test that sets `digest_normalisation` to `'RAW_BYTES'` and to `7`, and expects `AuthorityError` in both modes.

## Warnings

### WR-01: Pre-publication anchor is hard-wired to the 2.0.0 constant and its messages

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:695-698`
**Issue:** D-01 says that in pre-publication mode the record must name the superseded authority, which for 2.0.2 is 2.0.1 at `31addfa`. The code uses `SUPERSEDED_V2_0_0`, and its errors say "must name the 2.0.0 publication commit" and "must equal the 2.0.0 digest". The same constant also drives `source_lineage.supersedes`, the decisions-digest equality check, the schema `pinned(...)` entry and the dry-run summary. Pre-publication mode therefore works in Phase 9 only if that constant is rewritten to 2.0.1 in the same edit. Nothing ties the anchor to the record actually in the repository: the committed record today names 2.0.1. If the constant is not updated, the Phase 9 step `--validate --pre-publication` fails against the real 2.0.1 record. The tests (`superseded_record`, `test_pre_publication_wrong_commit_or_digest_fails` matching `'2.0.0 publication commit'`) lock the hard-coded wording in place.
**Fix:** Rename the constant to `SUPERSEDED` (or `SUPERSEDED_PUBLICATION`) and build the messages from it:
```python
sup = SUPERSEDED
if record['publication_commit'] != sup['commit']: raise AuthorityError(f"pre-publication record must name the {sup['version']} publication commit")
if record['authority_sha256'] != sup['sha256']: raise AuthorityError(f"pre-publication record authority_sha256 must equal the {sup['version']} digest")
```
Make the test regexes version-agnostic. Add a Phase 9 checklist item that `SUPERSEDED` must equal the record committed at `31addfa`.

### WR-02: Narrowed mutation gate still counts environment failures as domain rejections

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:591-607`, `:90`, `:244`, `:308`
**Issue:** D-04 limits a rejection to domain errors. But `validate_publication` now calls `catalog_controls()` and `catalog_bytes()` twice, and both go through `git_show`. `git_show` wraps git-missing, shallow-clone and object-missing failures in `AuthorityError`. If git fails during `run_mutations`, every AUTHORITY mutation is recorded as `rejected_by: ['PYTHON_VALIDATOR', ...]` for an environmental reason. For the 14 AUTHORITY mutations without `schema_must_reject`, the run then "passes" without any domain check. The DECISIONS gate catches bare `ValueError`. That also absorbs `json.JSONDecodeError` and `UnicodeDecodeError` from `V2.load(PROPOSALS/DRAFTING_RECORD)` inside `validate_decisions`. Today the earlier `published_authority_checked()` call usually hides this, but the gate itself does not meet D-04.
**Fix:** Read the pinned catalog once per run, outside the gate, and pass it in (or cache `catalog_bytes()` per process). Also give `git_show` failures a distinct subclass, for example `class GitHistoryError(AuthorityError)`, and re-raise it in `mutation_gates`:
```python
try: validate_publication(doc)
except GitHistoryError: raise
except AuthorityError: gates.append('PYTHON_VALIDATOR')
```
For DECISIONS, catch `AuthorityError`, not `ValueError`.

### WR-03: Validators still crash with non-domain exceptions on malformed authority shapes; `validate_published` runs Python before the schema

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:226-263`, `:666`
**Issue:** D-05 asks that validators "check shape first and raise the domain error". The diff does not harden `validate_authority` at all. These calls still raise `AttributeError` or `TypeError` on wrong shapes:
- `cv = a.get('classification_vocabulary', {}); cv.get(...)` (L226-227) when the value is a list or string;
- `a.get('evidence_boundary', {}).get(...)` (L246);
- `att.get(k)` (L263);
- `dependency.get(...)` (L241-242);
- `r.get(...)` on a non-dict control row (L248-250);
- `a.get(...)` when the loaded JSON is not an object.

`validate_published` calls `validate_publication(a)` before the schema check (L666). A malformed committed authority therefore exits with an uncaught `AttributeError` traceback instead of an `AuthorityError`. The new test `test_python_validators_raise_only_domain_errors` covers only the 29 fixed mutations, so these paths are not tested.
**Fix:** Add shape guards at the top of `validate_authority`:
```python
if not isinstance(a, dict): raise AuthorityError('authority must be an object')
cv = a.get('classification_vocabulary'); cv = cv if isinstance(cv, dict) else {}
eb = a.get('evidence_boundary'); eb = eb if isinstance(eb, dict) else {}
att = a.get('attestation_prohibitions'); att = att if isinstance(att, dict) else {}
rows = a.get('controls'); rows = rows if isinstance(rows, list) else []
# and `if not isinstance(r, dict): errors.append(...); continue` in the row loop
```
Add the mutations "classification_vocabulary is a list" and "a control row is a string" to the domain-error test.

### WR-04: SCHEMA-07 "closed" schema still accepts open nested objects and omits fields Python requires

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:376`, `:383`, `:373`
**Issue:**
- The top-level properties added only to satisfy `additionalProperties:false` are typed loosely:
  - `attestation_prohibitions: {'type':'object'}` is optional and open. The schema accepts an authority with no attestation prohibitions, or with `historical_compliance_attestation: true`, even though `validate_authority` rejects that as "attestation leakage".
  - `classification_vocabulary` and `evidence_boundary` are open objects, so extra fields and `unknown_is_not_false: false` pass.
  - `applicability_vocabulary` accepts any array.
- On control rows, `control_name` and `catalog_scope` are always emitted but not `required`.
- In semantics, `fields_not_usable_in_rules_statement` and `statements` are free strings, while every sibling is `const`-pinned.

Hayes treats the schema as a contract. "The schema rejects unexpected fields itself" holds only at the three named levels, and the schema accepts states the Python gate forbids.
**Fix:** Pin these with `const`, as the builder already produces them:
- `'attestation_prohibitions': {'const': {...three False...}}` and add it to `required`;
- `'classification_vocabulary': {'const': {...}}`;
- `'evidence_boundary': {'const': {...}}`;
- `'applicability_vocabulary': {'const': list(RESULTS)}`;
- `control_name` and `catalog_scope` added to the row `required` list;
- `'statements': {'const': semantics()['statements']}` and `'fields_not_usable_in_rules_statement': {'const': ...}`.

Add `schema_rejects` tests for a missing `attestation_prohibitions` and for `historical_compliance_attestation: true`.

### WR-05: GATE-05 cross-note uniqueness is not enforced on any `--validate` path

**File:** `scripts/build_archive_assessment_governance_decisions.py:152-166`, `:236-325`
**Issue:** The `norm_templated` cross-note check, and the D-13 exemption, live only in `strict_checks`. That runs only from `build_decisions` and `--validate-answers`. `validate_decisions`, the path the v2 publisher's `--validate` and the mutation gate use, has no note-uniqueness check on `records[*].note`. It ties the decisions to the answers only through `answers_sha256`, never by rebuilding the records. A decisions file whose records carry notes that differ only in templated numbers therefore passes the publisher's `--validate`, provided the answers digest matches. So GATE-05 holds at build time only, not at the CI gate.
**Fix:** In `validate_decisions`, rebuild the records from the live answers and compare them, or apply the same `key = norm if d['answers_sha256'] == CERTIFIED_ANSWERS_SHA256 else norm_templated` uniqueness loop over the unsuperseded records' notes. Add a DECISIONS-target test with two records whose notes collide under `norm_templated`.

### WR-06: D-10 "live catalog edit does not change the build or `--validate` result" is not proven

**File:** `tests/test_archive_assessment_lineage_validation.py:334-348`
**Issue:** D-10 requires a test that editing the live catalog in a scratch copy leaves the `--validate` and build results unchanged. The new test only shows that `catalog_bytes()` and `catalog_controls()` return the pinned blob. It never calls `build_authority()`, `validate_publication()` or `validate_published()` after the edit. A later regression that brings back a live-file read elsewhere (for example in the lineage digest, the dry-run summary or a new helper) would not be caught. `test_catalog_commit_is_v1_baseline_and_in_commit_pinned` only asserts `not hasattr(MODULE, 'CATALOG')`, which is a name check, not a behaviour check.
**Fix:** In the same scratch repo, compare `jtext(build_authority())` before and after overwriting the working-tree catalog. Also assert that `validate_publication(build_published_authority())` still passes, or that `validate_lineage(...)['catalog_reference']` passes. Do the same with the live file deleted.

### WR-07: D-13 "changing the answers bytes removes the exemption" is tested with a fabricated digest, not real bytes

**File:** `tests/test_archive_assessment_governance_answers.py:120-125`
**Issue:** `test_changed_answers_bytes_remove_exemption` builds a digest with `sha_text(read_text() + ' ')` and passes it directly as `answers_sha256`. It never runs `answers_digest()` on modified bytes, and never goes through `build_from_files()` or the `--validate-answers` CLI, which are the real paths. A regression in either path would not be detected, for example if `answers_digest` switched to a content-normalised digest, or if a caller stopped passing the digest so the default `None` applied. The exemption is also keyed on a digest the caller supplies, not one computed from the answers object (see IN-03).
**Fix:** Copy the answers file to `tmp_path`, append a byte, monkeypatch `MODULE.ANSWERS` to point at the copy, and assert that `build_from_files()` raises `AuthorityError(match='repeats the note of')`. Also assert that the untouched copy builds.

## Info

### IN-01: Python validator accepts unknown top-level keys, and the test locks this in

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:220-222`; `tests/test_archive_assessment_applicability_authority_v2_publication.py:782`
**Issue:** `validate_authority` checks `req <= set(a)` but not a closed key set. `test_schema_07_mutations_rejected_by_schema` asserts `gates == ['SCHEMA']` for `extra_top_level_field`. That makes the Python validator's openness an intended contract rather than a gap.
**Fix:** Check that the top-level key set equals the built key set in `validate_authority`, and relax the assertion to `'SCHEMA' in gates`.

### IN-02: Shallow-check message is misleading on old git or a non-repository

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:263-268`
**Issue:** Git versions before 2.15 do not know `--is-shallow-repository`. They echo the literal argument with return code 0, so the check fails closed, which is correct, but reports "shallow clone". The OSError path is caught, but the following `git('log', ...)` call is not wrapped. That is harmless today because the first call would have failed.
**Fix:** Distinguish `stdout == 'true'` (shallow) from any other output ("cannot determine clone depth: <stdout/stderr>").

### IN-03: Grandfather exemption trusts a digest the caller supplies

**File:** `scripts/build_archive_assessment_governance_decisions.py:120`, `:153`, `:209-210`
**Issue:** `validate_answers` and `build_decisions` accept `answers_sha256` separately from the answers object. Any programmatic caller that passes `CERTIFIED_ANSWERS_SHA256` with different content gets the weaker `norm` check. `validate_decisions` would later catch the digest mismatch against the live file, so this is defence in depth only.
**Fix:** Have `build_decisions` compute the digest from `ANSWERS` itself, or document that `answers_sha256` must come from `answers_digest(ANSWERS)`.

### IN-04: `CATALOG_COMMIT` is an alias of `V1_BASELINE_COMMIT`

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:46`
**Issue:** Re-pinning the v1 baseline would silently move the catalog pin as well. D-07 chose the same SHA, not a coupled one.
**Fix:** `CATALOG_COMMIT = '62a8955dc28d9458cd1167fad314926e057c31fc'` as a literal. The existing test already asserts that the two are equal.

### IN-05: Formatting slips in the edited lines

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:47`, `:668`, `:321`; `tests/test_archive_assessment_lineage_validation.py:154`
**Issue:**
- `V1_BASELINE_ID ='...'`
- `a !=build_published_authority()`
- `'supersedes','supersedes_governance_decisions'`
- `parametrize('missing',['absent', ...])`

These are inconsistent spacing introduced in this diff.
**Fix:** Run `ruff format` or fix the spacing by hand.

### IN-06: Dead `dependencies` loop in `validate_authority`

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:241-242`
**Issue:** With `additionalProperties:false`, a `dependencies` key can no longer pass the schema, and the builder never emits it. The loop also calls `.get` on unchecked items (see WR-03).
**Fix:** Remove the loop, or reject `dependencies` outright.

### IN-07: "CHANGED shows no change" comparisons still use `norm`, not `norm_templated`

**File:** `scripts/build_archive_assessment_governance_decisions.py:180`, `:186`, `:307`
**Issue:** Under Claude's discretion for GATE-05, `norm_templated` was meant to apply "at every comparison site". A CHANGED rationale that differs from the draft only in a number or control id still counts as a change.
**Fix:** Decide explicitly. Either use `norm_templated` here too (and confirm the change is output-neutral against the committed decisions), or record why these sites keep `norm`.

### IN-08: Pre-publication acceptance test registers the current manifest as the superseded manifest blob

**File:** `tests/test_archive_assessment_applicability_authority_v2_publication.py:484-501`
**Issue:** `superseded_record` sets `manifest_sha256` to the current temp manifest digest and registers the same bytes as the 2.0.0 blob. The D-03 manifest check is then only self-consistent: it would still pass if the code checked the current manifest instead of the one at the superseded commit.
**Fix:** Register the real manifest blob at `SUPERSEDED['commit']` (as the authority blob already is) and set `manifest_sha256` to its LF digest. Or use a distinct synthetic blob and assert that the current manifest digest is not accepted.

### IN-09: `write_publication_record` does not check that the commit contains the bytes it records

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:706-711`
**Issue:** `--record-publication <sha>` writes the record without the D-03 blob check. A typo in the SHA is only found at the next `--validate`, after the record has been committed.
**Fix:** After building `record`, compute the digests of `git_show(sha, rel(AUTHORITY))` and `git_show(sha, rel(OUT / N_MANIFEST))` and compare them before `dump`. Or call `check_publication_record` on the record held in memory.

---

_Reviewed: 2026-11-12_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
