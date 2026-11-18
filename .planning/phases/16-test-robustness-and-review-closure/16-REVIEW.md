---
phase: 16-test-robustness-and-review-closure
reviewed: 2026-11-18T00:00:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
  - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
  - tests/test_archive_assessment_lineage_validation.py
  - tests/test_archive_assessment_skip_guard.py
  - tests/test_archive_assessment_demo3_w1_req_001_reply.py
  - tests/test_archive_assessment_applicability_authority_v2_publication.py
findings:
  critical: 0
  warning: 3
  info: 4
  total: 7
status: fixed
---

# Phase 16: Code Review Report

**Reviewed:** 2026-11-18
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

I read the changed regions of the 2.0.3 notice builder and the five test files, using the plan SUMMARYs as a guide. I found no Critical issues.

- Fail-closed behaviour holds. Nothing resolves UNKNOWN to not-applicable.
- The `EXPECTED_LINEAGE_COMMIT` check is sound.
- `render_markdown` and the notice schema are unchanged. The `copy.deepcopy` of the rule does not change the JSON, so the byte-identity claim is plausible. I could not run the build, so I did not re-verify it.
- No absolute paths are introduced into the registry JSON. The `C:\\ems` prerequisite text is untouched.
- I did not read the frozen publisher, reply builder or 2.0.2 builder for edits, and I recommend none.

The warnings concern gaps in the new IN-02 and IN-03 behaviour. In each case the claimed guarantee is wider than the code or tests deliver.

## Warnings

### WR-01: Malformed pinned input of the wrong JSON type escapes as a raw AttributeError, not AuthorityError — FIXED in 08f7301

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:348` and `:384`, with the unwrapped `.get` calls at `:213`, `:362`, `:398`, `:250` and `:255`

**Issue:** The IN-02 wrappers in `load_inputs` and `build_notice` catch only `(ValueError, KeyError, TypeError)`. If a pinned blob parses as valid JSON of the wrong type, the code calls `.get()` on a list or string. Examples are `record.get('publication_commit')` at line 362, `manifest.get('published_on')` at line 398, `negative.get('result')` at line 213 and `old.get('digest_normalisation')` at line 250. This raises `AttributeError`, which is not caught. The run still fails closed, but not with the `AuthorityError` that the Phase 16 contract states ("malformed input raises AuthorityError"). The new test `test_malformed_pinned_input_raises_authority_error` covers only invalid JSON and invalid UTF-8 on the governance-decisions blob. Decisions are consumed inside `_WRAPPED` handling, which includes `AttributeError`, so the gap is hidden.

**Fix:**
```python
except (ValueError, KeyError, TypeError, AttributeError) as e:
```
Apply this in both `load_inputs` and `build_notice`. Add test params such as `b'[]'` and `b'"x"'` for the publication record and manifest blobs (patch `git_show` for `NOTICE_RECORD_COMMIT` and the manifest path).

### WR-02: `write_atomic` is not atomic across the three outputs, and `--build` validates again after replacing — FIXED in 08f7301

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:95-103` and `:620-626`

**Issue:** The temp files are staged first, then `os.replace` is called three times in sequence. If the second or third replace fails (a locked file on Windows, for example), the first output is already replaced. The committed set is then a mix of the new and old versions, and the `finally` only removes leftover temps. After the replaces, `validate_notice()` runs. If it fails, the new files stay in place with no rollback. The docstring-level claim "all three outputs, atomically" overstates this. For hash-certified files that Hayes consumes, a mixed set is the worst failure mode.

**Fix:** Either document and name it honestly (`write_staged`), or add a rollback. Read the old bytes first, then restore them if any replace or the post-write `validate_notice()` raises. The post-write validation can also be dropped, since `validate_notice_object(notice, inputs)` already ran on the same in-memory data. Add a test that monkeypatches `os.replace` to fail on the second call.

### WR-03: `test_failed_build_validation_leaves_no_partial_files` does not exercise `write_atomic` — FIXED in 08f7301

**File:** `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:821-831`

**Issue:** The test forces `validate_notice_object` to raise. In `main()` that call happens before `write_atomic`, so nothing was ever written, and `list(out.iterdir()) == []` is trivially true. The test would pass even if `write_atomic` leaked `.tmp` files or replaced files partially. It guards only the call order (validate then write). The test name and the IN-03 closure claim imply coverage of the write and cleanup path, which does not exist.

**Fix:** Add a case that patches `MODULE.os.replace` to raise on the second call. Assert that no `*.tmp` files remain, and assert the documented state of the outputs. Rename the current test to say it covers validation ordering.

## Info

### IN-01: Lineage commit-mismatch tests need real history but do not call `require_history`

**File:** `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:762-767`

**Issue:** For `catalog_reference`, `v1_baseline`, `supersedes` and `governance_decisions`, `lineage_entries` iterates the keys in sorted order. It calls the real `git_show` for the earlier keys (aa1, aa2) before it reaches the mutated one. In a shallow clone or without git, this raises `GitHistoryError` with a different message, and the test fails confusingly instead of reporting the missing history.

**Fix:** Call `require_history(ROOT, commits=FROZEN_COMMITS)` first, or monkeypatch `git_show` so the test is hermetic.

### IN-02: `run_in_clone` drops stderr and stdout from the reported result

**File:** `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:665-668`

**Issue:** The function returns only `(returncode, last stdout line)`. On a failed clone `--build` or `--validate`, the assertion messages show `(1, '')` and the reason (the builder's error text on stderr) is lost. The call also uses `text=True` with no `encoding`, so on Windows the locale codepage decodes the output. The D-10 baseline test already sets `encoding='utf-8', errors='replace'` for this reason.

**Fix:** Pass `encoding='utf-8', errors='replace'`. Include `r.stderr` in the returned tuple, or raise with it in the assertion messages.

### IN-03: Dead guard in `pinned_mutation_run`

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:305-311`

**Issue:** `pub` is assigned only if `load_pinned_publisher` returns, and the `except` runs only if it raised. So `pub is not None` is always False in that handler, and the `GitHistoryError` branch is unreachable. The guard looks like it detects history errors, but it never does. A history error from the pinned module is classified as a plain `AuthorityError`.

**Fix:** Drop the conditional and use `raise AuthorityError(...)`. Alternatively, classify with the builder's own `GitHistoryError`, which is already re-raised by the earlier `except AuthorityError: raise`.

### IN-04: The D-10 overlay normalises every publication path to LF unconditionally

**File:** `tests/test_archive_assessment_lineage_validation.py:35-46`

**Issue:** `overlay()` replaces CRLF with LF in all `publication_paths()` plus the publisher script. This is correct today, because those paths are all LF-normalised JSON or Python. If a RAW_BYTES artifact (for example the AA1 manifest, which carries `-text`) were ever added to `publication_paths`, the overlay would silently change its raw bytes and create a false red. Separately, the deep-root test's non-Windows branch is only a smoke test, because the bare-`git show` failure cannot be reproduced there.

**Fix:** Add a one-line comment or an assertion that no overlaid path is declared RAW_BYTES. Alternatively, copy bytes unchanged and rely on `-c core.autocrlf=false`.

---

_Reviewed: 2026-11-18_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

## Fix Log

- 2026-11-18, commit 08f7301: WR-01, WR-02 and WR-03 fixed.
  - Checks: 2.0.3 `--build`/`--validate` print PASS; the three 2.0.3 outputs are byte-identical; the frozen files are unchanged; the 2.0.3 notice tests give 120 passed, 0 skipped.
  - WR-02 residual: rollback is best-effort. A crash between `os.replace` calls can still leave a mixed set.
- Info IN-01..IN-04 were not in the fix scope (no `--all`).
