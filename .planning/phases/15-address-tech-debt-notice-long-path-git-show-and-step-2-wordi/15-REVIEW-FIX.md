---
phase: 15-address-tech-debt-notice-long-path-git-show-and-step-2-wordi
fixed_at: 2026-11-17T00:00:00Z
review_path: .planning/phases/15-address-tech-debt-notice-long-path-git-show-and-step-2-wordi/15-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 15: Code Review Fix Report

**Fixed at:** 2026-11-17T00:00:00Z
**Source review:** .planning/phases/15-address-tech-debt-notice-long-path-git-show-and-step-2-wordi/15-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (WR-01..WR-05; fix_scope critical_warning, so IN-01..IN-03 were not attempted)
- Fixed: 5
- Skipped: 0

The notice JSON and Markdown were never hand-edited. Every wording change was made in `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, then regenerated with `--emit-schema` and `--build`, and `--validate` printed PASS. The regenerated outputs were committed in the same commit as the builder change. The schema was regenerated each time and did not change. The frozen reply and 2.0.2 notice builders were not touched. The quoted `AT_PIN_DEFERRED` text is still verbatim.

## Fixed Issues

### WR-01: The long-path prerequisite names the wrong step, and its command cannot run before the clone exists

**Files modified:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json`, `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md`
**Commit:** 8853815
**Applied fix:** The fifth prerequisite now reads: "On Windows with a deep checkout root, the clone and checkout in step 1 need long paths: clone with git clone -c core.longpaths=true (or run git config --global core.longpaths true before step 1), or clone to a short checkout root such as C:\ems". "before step 3" is gone. `test_notice_has_long_path_prerequisite` now checks that the prerequisite names step 1, does not name step 3, and contains both working command forms. The `C:\ems` example was kept because the reviewer's suggested text keeps it; IN-01 (out of scope) still applies.

### WR-02: The new error hint is now misleading for every `git show` failure

**Files modified:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `.planning/phases/15-address-tech-debt-notice-long-path-git-show-and-step-2-wordi/15-01-SUMMARY.md`
**Commit:** a43ae79
**Applied fix:** `git_show` now adds the `core.longpaths` clause only when git's stderr contains `Filename too long`. The `fetch full history (git fetch --unshallow)` substring is kept. The old `test_git_show_error_hint_names_long_paths_and_unshallow` is replaced by a parametrised test with faked git stderr for three cases: an invalid object, a missing path, and Filename too long. Only the last one gets the long-path hint. In the 15-01-SUMMARY, the decision line that called `--` "defensive only" is replaced with the correct finding: `--` fixes the step 3 failure, and `core.longpaths` matters only for the step 1 clone/checkout. The verification paragraph gets a correction note. The notice outputs did not change; `--validate` printed PASS.

### WR-03: The rendered notice contradicts itself about where the record binding is checked

**Files modified:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json`, `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md`
**Commit:** e551ba7
**Applied fix:** Added a `binding_note(pub)` helper: "Plain --validate at the record commit checks that the record is consistent with the commit it names; step 3 checks that this commit is {pub}." `render_markdown` places it right after the verbatim deferred quote, and it is appended to the meaning of outcome row 1. The new test `test_deferred_quote_is_followed_by_binding_note` checks the note in the built notice, in the rendered Markdown and in the committed Markdown, and that `at_pin_deferred` still equals the frozen literal at 1544dc1.

### WR-04: Step 2's outcome row still says more than plain `--validate` checks

**Files modified:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json`, `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md`
**Commit:** b93a14f
**Applied fix:** Step 2 `pass_means` now says the files are byte-identical "between the commit named by the publication record and this commit", and "Step 3 checks that the record names {pub}, and all three steps are required before re-pinning". The trailing later-commits sentence is unchanged. Outcome row 2's meaning now says "between the commit named by the publication record and the checked-out commit. Step 3 checks that this is the pin." `test_step2_wording_does_not_overstate` was updated to match. It also checks that "between the two commits" and "between the pin and" are gone.

### WR-05: No test covers the real long-path failure, and the clone tests hide it

**Files modified:** `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`
**Commit:** a47f725
**Applied fix:** New test `test_git_show_double_dash_survives_deep_checkout_root_with_real_git`:
- It runs only on Windows (`skipif sys.platform != 'win32'`).
- It runs `git clone --shared --no-checkout` into a nested TMP directory. The directory is deep enough that the root plus the 120-character negative-invariant path is over 270 characters.
- It sets `core.longpaths false`.
- It first confirms that `git show <pub>:<path>` without `--` fails with `Filename too long`. If this machine does not reproduce that (for example, Windows long paths are enabled system-wide), the test skips rather than passing vacuously.
- It then monkeypatches `MODULE.ROOT` to the clone and asserts that `git_show` returns the same blob as in the main repository.

Checked locally: it passes with `--`, and it fails with GitHistoryError when `--` is temporarily removed from `git_show`. That temporary edit was reverted before the commit. It is skipped on the ubuntu CI runner.

## Verification

- `python scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py --validate` printed PASS after every fix and again in the main checkout after the fast-forward.
- Full test run in the main checkout (`--basetemp .pytest-phase15-fix`) over the 2.0.3 notice, frozen reply and 2.0.2 notice test files: 339 passed, 1 failed, 0 skipped. The 98 tests in the 2.0.3 file include the new real-git long-path test, which ran and was not skipped.
  - The one failure was `test_committed_notice_files_validate`. It checks that the working-copy files contain no `\r`, and the fast-forward had checked the regenerated files out as CRLF because `core.autocrlf` is on.
  - Re-running the builder (`--emit-schema`, `--build`) rewrote them as LF. There was no content diff against HEAD. After that, `--validate` printed PASS and the test passed.
- Side observation: run from the deep scratch worktree, the frozen reply and 2.0.2 notice tests failed with `Filename too long`. Their frozen `git_show` has no `--`, which is the same WARNING-1 behaviour. This comes from the deep worktree path, not from these fixes. Those files were not changed.

---

_Fixed: 2026-11-17T00:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
