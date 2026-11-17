---
phase: 14-notice-to-hayes-2-0-3
reviewed: 2026-11-17T19:42:55Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
  - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
  - .github/workflows/ems-validate.yml
findings:
  critical: 0
  warning: 3
  info: 5
  total: 8
status: issues_found
---

# Phase 14: Code Review Report

**Reviewed:** 2026-11-17T19:42:55Z
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

I reviewed the 2.0.3 notice builder, its tests and the one-line CI addition against decisions D-01..D-15. To check the pinned-run containment, I also read the pinned publisher (`1544dc1:scripts/publish_archive_assessment_applicability_authority_v2.py`) and the pinned decisions builder.

The derivation chain is sound. Every cited value is either a schema `const` or rebuilt from git at a frozen commit and compared byte-for-byte. The mutation rerun is compared entry by entry with the frozen negative output (D-02). All 7 lineage digests are recomputed with the declared normaliser (D-07). The scope-error claim is computed and requires raw != LF and raw == the 2.0.1 digest (D-05). Shallow clones and missing history fail closed. CI runs with `fetch-depth: 0`.

I found no blocker. The weak points are:

- **Pinned-run containment (D-01).** It is guaranteed by convention and an after-the-fact check, not by construction.
- **Outcome table (PIN-03).** The verification-outcome table gives guidance that contradicts itself and cannot be carried out.
- **CI coverage.** CI does not use the `jsonschema` version that the notice tells Hayes to install.

## Warnings

### WR-01: Pinned-run containment relies on `pub.ROOT = ROOT` plus an after-the-fact check that covers only named constants

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:266`, `:307-311`

**Issue:** `load_pinned_publisher` sets `pub.ROOT` to the live repository root. The comment says this is for "git cwd only; every path constant already points into tmp". But the pinned publisher reads files through `ROOT` at call time in at least three places:
- `validate_lineage`, L458: `(ROOT / path).read_bytes()` for lineage entries without a `commit`. At the pin these are `aa1_manifest`, `aa2_approval`, `aa2_closure` and `governance_decisions`.
- `check_tree_matches_head`, L436.
- `validate_published`, L823.

None of these is reached today from `validate_governance_decisions`, `validate_publication`, `validate_signoff` or `run_mutations`. Nothing enforces that, though. If a future change to the materialised call path reached one of them, the pinned run would silently hash live working-tree data. D-01 forbids this ("the pinned module's path constants do not redirect reads to live files").

The containment check at L307-311 has three gaps:
- It inspects only ten named path constants. It cannot detect runtime `ROOT / ...` reads.
- It runs only after `run_mutations` has finished, so it detects a live execution after it happened rather than preventing it.
- The builder's own `b.V2` copy keeps `ROOT = tmp`. Any `V2.git_show` call would run `git` with `cwd` set to the temp directory. Git then searches the parent directories for a repository and could read an unrelated repository, or fail with a misleading error.

The clone test (`test_live_publisher_and_decisions_builder_edit_does_not_change_notice`) changes only the two live scripts. It never changes live data files, so a live data read would not be caught.

**Fix:** Make containment structural rather than conventional:
- Keep `pub.ROOT` pointing at `tmp`. Pass git's working directory separately, for example by monkeypatching `pub.git_show`, `b.V2.git_show` and `pub.git` with the builder's own `git_show`, which uses `cwd=ROOT`.
- Add a test that overwrites the live `registry/archive_assessment_governance_decisions.json` and the `generated/archive-assessment/ems-aa1|ems-aa2` inputs in the clone, then asserts that `--validate` still prints PASS with identical output. For example:

```python
pub.ROOT = tmp
pub.git_show = git_show          # builder's git_show, cwd=live ROOT
b = pub.decisions_builder(); b.V2.git_show = git_show
```

### WR-02: The verification-outcome table contradicts itself and describes a step 3 run that cannot happen

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:408`, `:413`, `:415`

**Issue:** The second outcome row reads "Step 2 **or** step 3 prints PASS at `87a46d1...` or any later commit", with action "Re-pin to `1544dc1...`". This has three problems:
1. Step 3 cannot run at `87a46d1`, because the notice builder does not exist at that commit. The row describes an outcome that cannot happen.
2. Because of "or", a step 2 PASS alone would justify re-pinning, even if step 3, which checks the notice's claims (CLAIM-01..03), fails. That same failure falls under row 4, "Any other failure... Do not consume the authority". Hayes therefore gets two contradictory actions for the case "step 2 PASS, step 3 FAIL".
3. Step 2's `pass_means` promises "It also passes at any later commit on `feature/ems-aa3-archive-applicability-authority`". This promise about future commits is unconditional and nothing enforces it. Any later commit that edits a publication path breaks it.

Hayes cannot make applicability decisions itself, so the notice's verification guidance must not be ambiguous (PIN-03, D-11).

**Fix:** Split the row into one row per step. State that re-pinning requires steps 1, 2 and 3 all to PASS, and drop "step 3 at `87a46d1`". For example:
- `'Step 2 prints PASS at {rec} or a later commit'`, action `'Run step 3.'`
- `'Step 3 prints PASS at or after the notice commit'`, action `f'Re-pin to {pub}.'`

Change the step 2 wording to "It is expected to pass at later commits that do not change the publication files", or remove that sentence. Then regenerate the notice; do not hand-edit it.

### WR-03: CI does not run the install command the notice gives Hayes

**File:** `.github/workflows/ems-validate.yml:85` (archive-assessment `Install dependencies`), `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:60`

**Issue:** The notice tells Hayes to run `python -m pip install -r requirements.txt jsonschema==4.26.0` (D-09). The archive-assessment job instead runs `pip install -r requirements.txt jsonschema pytest`, which installs whatever `jsonschema` version is newest on the day.

The pinned publisher's SCHEMA gate relies on Draft 2020-12 behaviour, for example `contains`/`minContains`/`maxContains` in its `dup_guard`. The mutation rerun must also match the frozen negative output entry for entry, including the `rejected_by` lists. A gate result that changes between `jsonschema` versions would therefore pass in CI but fail for Hayes, or the reverse.

The green CI run at `c04763d` shows only that the latest `jsonschema` works. It does not show that the version the notice names works.

**Fix:** Pin the archive-assessment job to the version the notice names, or add a step that installs exactly `INSTALL_COMMAND` before running the 2.0.3 notice `--validate`:

```yaml
pip install -r requirements.txt jsonschema==4.26.0 pytest
```

## Info

### IN-01: Unused helpers, and lineage recompute commits taken from the entry without a cross-check

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:47`, `:160-162`, `:219`

**Issue:**
- `pinned_raw_digest` is never called.
- `CATALOG_COMMIT` is defined but never used by the builder; only the test uses it.
- `lineage_entries` takes `at = e.get('commit', NOTICE_PUBLICATION_COMMIT)` straight from the lineage entry. It never asserts that `catalog_reference`/`v1_baseline` resolve to `CATALOG_COMMIT` and `supersedes` resolves to `PREVIOUS_2_0_2_COMMIT`, which D-07 names. The authority is hash-bound at the pin, so the risk is low. Even so, `recomputed_at` is only checked against the authority itself, not independently.

**Fix:** Remove `pinned_raw_digest`. Add `EXPECTED_LINEAGE_COMMIT = {'catalog_reference': CATALOG_COMMIT, 'v1_baseline': CATALOG_COMMIT, 'supersedes': PREVIOUS_2_0_2_COMMIT}` and fail if `at` differs from the expected commit (the pin for all other keys).

### IN-02: Some malformed-input paths raise non-domain exceptions

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:152-153`, `:187`, `:328`, `:280`, `:299`

**Issue:**
- `pinned_json` raises `JSONDecodeError` or `UnicodeDecodeError` on a bad blob.
- `record['manifest_sha256']` and `a['relative_path']` can raise `KeyError`.
- Exceptions outside `_WRAPPED`, such as `RuntimeError` or `SystemExit` from pinned module import, propagate raw.

The script still exits non-zero, but the project convention is a domain `AuthorityError`. Separately, matching `GitHistoryError` by class name (`type(e).__name__ == 'GitHistoryError'`) is fragile, and the re-raise at L299 drops the "pinned baseline" context from the message.

**Fix:** Wrap the bodies of `load_inputs` and `build_notice` in `except (ValueError, KeyError, TypeError) as e: raise AuthorityError(...) from e`. Compare against `pub.GitHistoryError` rather than the class name.

### IN-03: `--build` leaves partially written files on failure and never refreshes the schema

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:571-578`

**Issue:**
- `--build` writes `NOTICE_JSON` and `NOTICE_MD` and only then calls `validate_notice()`. If that fails, for example because the schema file is stale, the new files stay on disk next to an old schema.
- `--build` never writes `NOTICE_SCHEMA`, and `--emit-schema` writes it without any validation.

**Fix:** Have `--build` also write the schema (`dump(NOTICE_SCHEMA, schema())`) before validating, or document the required order `--emit-schema` then `--build`.

### IN-04: The built notice holds references into the input authority

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:399`

**Issue:** `'rule': r['not_applicable_rule']` puts the authority's own dict into the notice. Any caller that mutates the returned notice also changes the cached inputs. In `validate_notice`, the same `inputs` tuple is reused for a second `build_notice` call. The tests avoid this only because `args()` deep-copies the inputs.

**Fix:** Use `copy.deepcopy(r['not_applicable_rule'])`.

### IN-05: Test robustness nits

**File:** `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:619-628`, `:638-641`, `:170-182`

**Issue:**
- `shutil.rmtree(..., onerror=...)` is deprecated in Python 3.12 (use `onexc`).
- `run()` treats the last non-empty line of stdout and stderr together as the result. Any stderr warning (for example a `DeprecationWarning` from the pinned code) would make a passing `--validate` look like a failure.
- `test_pinned_run_paths_stay_in_temp_materialisation` asserts only that the temp directory is outside `ROOT`, which is always true. It does not test that pinned code avoids live files (see WR-01).

**Fix:**
- Use `onexc=`.
- Parse `r.stdout` only, and assert `r.returncode`.
- Extend the containment test with a live-data tamper case, as described in WR-01.

---

_Reviewed: 2026-11-17T19:42:55Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
