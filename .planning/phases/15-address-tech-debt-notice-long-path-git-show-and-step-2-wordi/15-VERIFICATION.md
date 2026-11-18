---
phase: 15-address-tech-debt-notice-long-path-git-show-and-step-2-wordi
verified: 2026-11-17T00:00:00Z
status: passed
score: 7/7 must-haves verified
overrides_applied: 0
---

# Phase 15 Verification

**Goal:** Close v1.2.0 audit WARNING-1 (long-path failure of notice step 3, misleading hint, missing prerequisite) and WARNING-2 (step 2 overstating plain --validate) in the 2.0.3 notice, via the builder.
**Re-verification:** No (initial). Judged against the final code after review fixes 8853815..a47f725.

## Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Step 3 no longer fails on long paths | VERIFIED | `git_show` argv ends in `'--'` (builder line 101). Test `test_git_show_double_dash_survives_deep_checkout_root_with_real_git` uses real git in a deep clone. |
| 2 | The hint is not misleading | VERIFIED | Line 106 adds the core.longpaths clause only when stderr has `Filename too long`. The `git fetch --unshallow` text is kept. A parametrised test covers 3 failure cases. |
| 3 | A long-path prerequisite exists and targets the right step | VERIFIED (satisfied-by-correction) | Prerequisite 5 (builder line 427, rendered MD line 42) names step 1 clone/checkout with `git clone -c core.longpaths=true`, global config, or `C:\ems`. The plan said "before step 3". The review showed `--` fixes step 3 and the clone is where long paths bite, so the corrected wording meets the goal better. |
| 4 | Step 2 no longer overstates plain --validate (WARNING-2) | VERIFIED | `pass_means` (line 432) and outcome row 2 now say "byte-identical between the commit named by the publication record and this commit", and that step 3 checks the binding. "The publication record binds the pin" is gone. |
| 5 | The record-binding contradiction is removed (review WR-03) | VERIFIED | `binding_note()` follows the deferred quote and is in outcome row 1. The quote itself is unchanged. |
| 6 | The frozen reply builder and the 2.0.2 notice builder are untouched | VERIFIED | `git diff 8853815~1..HEAD` shows only the 2.0.3 builder under `scripts/`. |
| 7 | The outputs come from the builder and validate | VERIFIED | `--validate` run by me prints PASS, exit 0. The rendered Markdown matches the builder text. I ran 10 targeted tests (long-path, git_show, step2, deferred quote, hint) and all passed. |

## Requirements Coverage

PLAN frontmatter requirements are WARNING-1 and WARNING-2. They are audit items, not REQUIREMENTS.md IDs. They are accounted for against PIN-02, PIN-03 and NOTICE-03. PIN-03 (notice gives exact commands and what each result means) is strengthened by the corrected step 2 and prerequisite wording. No orphaned requirement IDs were found.

## Anti-patterns

None found in the changed code. No TBD, FIXME or XXX markers were seen in the changed lines.

## Notes (non-blocking)

- The frozen reply and 2.0.2 notice `git_show` have no `--`. This is deliberate (frozen, D-03) and out of scope.
- IN-01..IN-03 from the review were not in fix scope and were not checked.
- I did not run the full suite (the orchestrator is running it). The fixer reported 339 passed and 1 CRLF-only failure, which was resolved by regenerating the files.
- One real-git test is Windows-only and is skipped on CI.

## Human verification

None required.

**Status: passed.** Both warnings are closed.
