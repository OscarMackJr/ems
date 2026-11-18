---
phase: 16-test-robustness-and-review-closure
plan: 02
subsystem: tests, notice-builder
tags: [pytest, notice-2.0.3, review-closure, byte-identity]
requirements-completed: [BASE-02, GATE-14, GATE-15]
key-files:
  modified:
    - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
    - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
metrics:
  completed: 2026-11-18
---

# Phase 16 Plan 02: 2.0.3 notice builder fixes and honest deep-root test Summary

Behaviour-only fixes to the 2.0.3 notice builder (14 IN-01..IN-05, 15 IN-02/IN-03) and a deep-root git_show test that can now fail; the sent 2.0.3 notice output is byte-identical.

## Commits
- 66c2b23: test file only. BASE-02 deep-root test rewritten (win32: bare `git show` without `--` must fail with `Filename too long`, preconditions on root length, no shallow fallback, `pytest.fail` not skip; other platforms assert the `--` form only). Hint cases folded into `test_git_show_error_names_full_sha_and_fetch_hint` (fetch hint, negative core.longpaths, positive Filename too long); standalone parametrised hint test deleted. `onerror=` became `onexc=` (3 sites). `run_in_clone` parses stdout only, asserts and reports returncode and output in messages.
- e7d60ff: builder plus new tests.
  - 14 IN-01: `pinned_raw_digest` removed; `EXPECTED_LINEAGE_COMMIT` added; a lineage commit that differs raises `AuthorityError('... differs from the expected commit')`; `CATALOG_COMMIT` kept and now used.
  - 14 IN-02: `load_inputs` and `build_notice` re-raise AuthorityError and wrap ValueError/KeyError/TypeError (incl. JSON/UTF-8 decode errors) as AuthorityError; GitHistoryError detected with `isinstance(e, pub.GitHistoryError)` (guarded where `pub` is unbound); baseline rejection keeps 'pinned baseline rejected the unmutated inputs' and re-raises as GitHistoryError for history errors.
  - 14 IN-03: `--build` validates in memory (notice object, schema check), stages `.tmp` files, `os.replace`s all three outputs, removes temps in `finally`, then runs `validate_notice()`.
  - 14 IN-04: rule dict `copy.deepcopy`.
  - 15 IN-03: missing-git hint is "install git and ensure it is on PATH" (no fetch advice).
  - New tests: lineage commit mismatch (5 params), constants, malformed pinned blob (2 params), missing key, pinned GitHistoryError context, failed-validation leaves no files, successful atomic build equals fresh build, deep-copy, missing-git hint.

## 14 IN-05 test-nit record
- Deleted the always-true assertion `not seen[0][0].resolve().is_relative_to(ROOT.resolve())` from `test_pinned_run_paths_stay_in_temp_materialisation` (kept `assert len(seen) == 1`, the module-root containment and git_run containment assertions unchanged; not strengthened).
- Live-tamper coverage is `test_live_data_file_edit_does_not_change_notice` and `test_live_publisher_and_decisions_builder_edit_does_not_change_notice` (both exist; both passed locally).

## D-02 byte-identity gate (evidence)
1. Pre-build snapshot of `git show HEAD:<path>` for the three outputs saved to the scratchpad; the working-tree files already had identical sha256 (the `M` status in `git status` is EOL-only; `git diff --ignore-cr-at-eol` is empty).
2. `--build` exit 0 (PASS), then `--validate` PASS.
3. `git diff --ignore-cr-at-eol --exit-code` on the three outputs: exit 0.
4. LF-normalised byte compare against the HEAD snapshot: equal for all three. sha256 before and after the build are identical:
   - registry JSON `c61af44babcad6b578b3f7da8ac7cfcfe4c2a9d9bd4845714e1690ac11cba086`
   - docs MD `1b01eab9a0c975a7bd07d45d1838094dbbea95c4ed55b2016362e0c95eaa2387`
   - schema `9550e8382e12043ab0638b732043be4b282624b91feb7bcd2162cca346207513`
5. No `*.tmp` leftovers under registry/, docs/, schemas/.
6. Output files were not edited or staged. `git diff --ignore-cr-at-eol` on the publisher, reply builder and 2.0.2 notice builder is empty. No diff hunk touches `contains_absolute` or the `C:\ems` text (D-03).

## Verification
- Full notice test file: 107 passed (excluding the two clone tests), then the two clone-based live-edit tests passed locally (2 passed), under `EMS_FAIL_ON_SKIP=1`. No skips added.
- The deep-root test passed locally on win32 (the bare `git show` reproduced `Filename too long`).

## Deviations from Plan
- [Rule 3 - minor] `build_notice` was split into a thin wrapper `build_notice(*inputs)` over `_build_notice(...)` (and `load_inputs` over `_load_inputs`) to apply the IN-02 wrapping without re-indenting the bodies. Behaviour and return values unchanged.
- `--build` now also writes the schema file (the plan asked for all three); content is byte-identical to the committed schema.
- The "pinned-run `run()` helper" named in the plan does not exist as a separate helper in the test file; only `run_in_clone` runs a subprocess, and it was updated.

## Self-Check: PASSED
