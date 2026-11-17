---
phase: 14-notice-to-hayes-2-0-3
fixed_at: 2026-11-17T20:08:28Z
review_path: .planning/phases/14-notice-to-hayes-2-0-3/14-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 14: Code Review Fix Report

**Fixed at:** 2026-11-17
**Source review:** .planning/phases/14-notice-to-hayes-2-0-3/14-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (WR-01, WR-02, WR-03; Info items out of scope)
- Fixed: 3
- Skipped: 0

## Fixed Issues

### WR-01: Pinned-run containment relies on `pub.ROOT = ROOT` plus an after-the-fact check

**Files modified:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`
**Commit:** 1b5f6c2
**Applied fix:** Removed `pub.ROOT = ROOT`. The pinned publisher, the pinned decisions builder and the builder's own `V2` copy now keep `ROOT` inside the temp materialisation. `load_pinned_publisher` loads the builder straight away and checks all three `ROOT`s before any pinned function runs. The `subprocess` global of `pub` and `b.V2` is replaced with a git-only shim (`live_git_subprocess`) that forces `cwd` to the live repository and refuses anything that is not `git`. The pinned `git_show`/`git_run` code keeps its own validation, error classes and messages. The post-run containment check now also covers the three `ROOT`s. D-02 `check_rerun` is unchanged.
**Tests:** extended `test_pinned_run_paths_stay_in_temp_materialisation` (pinned ROOTs are under tmp; pinned `git_run` resolves to the live toplevel; the shim refuses a non-git process). Refactored the clone test into `make_clone` / `run_in_clone` / `assert_live_edit_does_not_change_notice` helpers. Added `test_live_data_file_edit_does_not_change_notice`, which tampers every `PINNED_DATA` file, the no-commit lineage inputs (governance decisions, ems-aa1 and ems-aa2 generated files), the authority, schema, sign-off, publication record and OUT files in a clone, then asserts `--validate` = PASS and `--build` output is byte-identical. I checked this scenario by hand in a clone: PASS.
**Status:** fixed: requires human verification (it changes how containment works)

### WR-02: The verification-outcome table contradicts itself

**Files modified:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`
**Commit:** e15eeb9
**Applied fix:** The outcome table now has 5 rows. Step 1 PASS leads to "Run step 2." Step 2 PASS at the record commit or later leads to "Run step 3." Step 3 PASS, at or after the notice commit and after steps 1 and 2 printed PASS, leads to "Re-pin to 1544dc1..."; its meaning text states "Re-pin only when steps 1, 2 and 3 all print PASS." The plain-at-pin row and the other-failure row are unchanged. The step 2 `pass_means` now says "It is expected to pass at later commits on the branch that do not change the publication files." That replaces the unconditional promise and departs from the D-09 wording. Schema `outcomes` min/max changed from 4 to 5. No forbidden words; `validate_notice_object` passes in-process on the rebuilt notice.
**Tests:** `test_verify_section` now expects 5 outcomes, checks the action order, checks that re-pin appears only in the step 3 row, and checks that the "step 2 or step 3" and "any later commit" wording is gone.
**Status:** fixed: requires human verification (wording; D-14 review of the regenerated Markdown)

### WR-03: CI does not run the install command the notice gives Hayes

**Files modified:** `.github/workflows/ems-validate.yml`
**Commit:** fcd9f7e
**Applied fix:** archive-assessment `Install dependencies`: `pip install -r requirements.txt jsonschema==4.26.0 pytest`. YAML parses.

---

_Fixed: 2026-11-17_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
