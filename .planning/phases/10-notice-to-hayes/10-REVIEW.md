---
phase: 10-notice-to-hayes
reviewed: 2026-11-12T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
  - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
  - .github/workflows/ems-validate.yml
findings:
  critical: 0
  warning: 5
  info: 2
  total: 7
status: issues_found
---

# Phase 10: Code Review Report

**Reviewed:** 2026-11-12
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

The builder reads frozen git bytes, binds the record commit, checks shallow clones and ancestry, and rebuilds all three files byte for byte. I found no blocker. The weaknesses are a claim in the notice that the builder does not verify, a dependency on live publisher code that contradicts D-04/D-05, and several tests that cannot fail for the reason they name. The CI line at `ems-validate.yml:97` is correct and sits in the archive-assessment validator list.

## Warnings

### WR-01: Notice claims "each rejected and failing closed" but the builder only counts the tests

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py:187-188, 195` (rendered at 235)
**Issue:** `tests = negative['negative_invariant_tests']` uses only `len(tests)`. The publisher writes `negative['result']` as PASS or FAIL, and each outcome carries its own status (publisher line 598). The builder never reads either. If a frozen output recorded a non-rejected mutation, the notice would still say "29 mutations, each rejected and failing closed". This is a signed statement to an external assessor that nothing checks. The same holds for "closes 16 levels", where the count is taken but nothing confirms the 16 are the object levels of the authority schema.
**Fix:** In `build_notice`, raise `V2.AuthorityError` unless `negative.get('result') == 'PASS'` and every outcome in `tests` shows rejection. Use the key the publisher actually writes in the outcome records. Add a test that edits the frozen negative file; the edit must also be reflected in the manifest check, so test `build_notice` directly with a mutated `negative` argument.

### WR-02: Notice validity depends on live publisher code, contrary to D-04/D-05

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py:14-16, 87, 135, 162, 164, 178, 187, 191, 195, 197, 261-281`
**Issue:** Frozen inputs are read from git, but the logic and constants come from the working-tree publisher: `V2.validate_signoff`, `V2.DUAL_ROLE_STATEMENT`, `V2.REQUEST_CONTROL_IDS`, `V2.PREV_COMPARED_KEYS`, `V2.closed_schema_levels`, `V2.rule_text`, `V2.APPROVER_ROLES`, `V2.RULE_FIELDS`, `V2.AUTHORITY_ID_RE`, and the V2 path constants. A 2.0.3 publisher that changes any of these will break `--validate`, or silently change the notice's `compared_keys`, `machine_form` or the generated schema. D-04 says a later 2.0.3 must not break or re-point the notice. `test_validate_independent_of_live_version` patches only `VERSION`, `AUTHORITY_ID` and `lf_digest`, so it gives false assurance. Because the notice is compared byte for byte, a change in live code fails closed, but it breaks the notice instead of leaving it stable.
**Fix:** Either pin the values the notice depends on as local constants (including `PREV_COMPARED_KEYS`, `DUAL_ROLE_STATEMENT` and the request control ids), or load the publisher at the frozen publication commit. Extend the live-version test to patch the other V2 attributes listed above.

### WR-03: Several tests cannot fail for the check they name

**File:** `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py:277-285, 309-313, 338-342, 94-98`
**Issue:**
- `test_digest_scope_error_fails_when_previous_authority_edited` (283-285): after `serve_edited` at the superseded commit, `build_notice` fails at the `pinned_digest(SUPERSEDED_COMMIT, ...) != sup['sha256']` check (builder line 171). It never reaches `digest_scope_error`. Only the direct call at line 282 exercises that function.
- `test_changed_row_blocks_no_decision_changed` (309-313): it only asserts `rows_differing(...)[0] == 1`. It never asserts that `build_notice` refuses to state "no decision changed". The guard at builder lines 185-186 is also effectively unreachable, because the previous authority's digest and the cited decision ids are already bound earlier. The name overstates what is tested.
- `test_absolute_path_is_rejected` (338-342) and the first assertion of `test_validate_rejects_tampered_cited_value` (98): `REJECTS` includes `AuthorityError`, and `validate_notice_object` ends with a `build_notice(...) != notice` check that raises `AuthorityError` for any change. Deleting `contains_absolute`, or the schema constants, would leave these tests green.
**Fix:** Assert specific messages: `match='absolute path'`, and `match='schema'` or `jsonschema.ValidationError` for the schema-driven cases. Call `build_notice` with an edited `previous` argument directly, so the target guard is the one that fires. Rename the row test, or make it assert that `build_notice` raises.

### WR-04: Four of the seven lineage digests are echoed into the notice without being checked against git

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py:114-128`
**Issue:** `lineage_entries` re-hashes only the three `RAW_LINEAGE_KEYS` against git. The `catalog_reference`, `governance_decisions`, `supersedes` and `v1_baseline` digests are copied from the authority as stated. Only `governance_decisions` is checked elsewhere (line 174). The notice presents each as the hash of that input, so a wrong digest in the frozen authority would be repeated to Hayes. The authority itself is bound by hash, so exposure is limited to an already-published error, but the notice claims more than it checks.
**Fix:** For every entry, hash the frozen bytes at the publication commit with the declared normaliser (`V2.NORMALISERS[e['normalisation']]`) and compare. For `catalog_reference` and `v1_baseline`, resolve the commit that the lineage names, if it has one.

### WR-05: "Declared under the wrong scope" is asserted, not demonstrated

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py:138-152`; rendered at 240
**Issue:** The notice says three digests "were declared under the wrong scope". `digest_scope_error` shows only that 2.0.1 declared the global CRLF_TO_LF claim, that 2.0.2 declares RAW_BYTES, and that the digest strings are equal. The claim is an error only if the raw and LF-normalised digests of those files differ, that is, if the files contain CRLF. The code never computes the LF-normalised digest of the three files. If any were LF-only, the 2.0.1 declaration would have been correct for it. D-06 requires that `--validate` fails if the stated digests do not match what git shows.
**Fix:** For each of the three, compute `sha256(lf_bytes(raw))` at the publication commit. Require it to differ from the raw digest, or word the notice to say only that the declared scope changed.

## Info

### IN-01: No pytest case validates the committed notice files

**File:** `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py:45-53, 73-75`
**Issue:** Every validation test redirects `NOTICE_JSON`, `NOTICE_MD` and `NOTICE_SCHEMA` to temp files regenerated from `build()`. Only the CI `--validate` step reads the committed files. A drift between the committed files and the builder is caught in CI but not by pytest.
**Fix:** Add one non-monkeypatched test that runs `MODULE.validate_notice()` against the repo files, skipped only when `git_ready()` returns a reason.

### IN-02: `--build` writes outputs non-atomically and skips a post-write check

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py:323-327`
**Issue:** The JSON is written before the Markdown. A failure between the two leaves a mismatched pair on disk. The result is not re-validated after writing, and `--emit-schema` output is not checked against the notice.
**Fix:** Build all three payloads first, write them, then call `validate_notice()`.

---

_Reviewed: 2026-11-12_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
