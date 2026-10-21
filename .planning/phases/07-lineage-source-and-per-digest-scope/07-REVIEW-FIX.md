---
phase: 07-lineage-source-and-per-digest-scope
fixed_at: 2026-10-20T00:00:00Z
review_path: .planning/phases/07-lineage-source-and-per-digest-scope/07-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 7: Code Review Fix Report

**Source review:** 07-REVIEW.md (WR-01..WR-05; IN-* out of scope)
**Verification:** Tier 1 only (re-read of edits). Python and pytest were not run, per instructions; the orchestrator runs the tests. Fixes WR-01 to WR-03 are logic changes and need that test run to confirm.

## Fixed Issues

### WR-01: validate_lineage fails open when a commit-pinned entry has no commit
**Commit:** 769ddc9
**Files:** `scripts/publish_archive_assessment_applicability_authority_v2.py`, `tests/test_archive_assessment_lineage_validation.py`
**Change:** Added `COMMIT_PINNED = {'supersedes','supersedes_governance_decisions','v1_baseline'}`. `validate_lineage` now records an error and continues when a pinned label has a missing, empty or None commit. Other labels still read the working tree.
**Test:** `test_wr01_commit_pinned_entry_without_commit_raises` (v1_baseline and supersedes; commit absent, empty, None).

### WR-02: non-string commit or normalisation raised TypeError
**Commit:** fb945f5
**Files:** same two
**Change:** `git_show` checks `isinstance(commit, str)` before the regex. `validate_lineage` checks `isinstance(norm, str)` before the `NORMALISERS` lookup.
**Tests:** `test_wr02_non_string_commit_raises_authority_error`, `test_wr02_unhashable_or_non_string_normalisation_raises_authority_error`, `test_wr02_git_show_non_string_commit_raises_authority_error`.

### WR-03: path guard missed drive-relative and backslash-rooted paths
**Commit:** c0c0c05
**Files:** same two
**Change:** New compact helper `bad_rel(p) -> bool`. It rejects non-str, empty, `contains_absolute`, a leading backslash, a `^[A-Za-z]:` prefix and `..` segments. `git_show` and `validate_lineage` both use it.
**Tests:** `test_bad_relative_path_raises` extended with `C:foo`, `c:foo/bar.json`, `\rooted\x.json` and a non-str value. New `test_wr03_git_show_rejects_bad_relative_path_before_subprocess`.

### WR-04: normalisation-claim tests skipped silently
**Commit:** 702c22e
**File:** `tests/test_archive_assessment_normalisation_claims.py`
**Change:** Removed all seven `skipif(not ...exists())` decorators. A missing artifact now fails the test. The `git_ready()` skips for git unavailable or shallow clone are kept.
**Test:** Existing claim tests, now non-skippable.

### WR-05: reply-pin test would break at the Phase 9 republication
**Commit:** aeb312c
**File:** `tests/test_archive_assessment_normalisation_claims.py`
**Change:** `test_reply_pin_normalisation_claim` now reads the authority and manifest blobs with `git show <pin.publication_commit>:<path>` and compares LF digests to the pin. It no longer reads the working files. The reply, its builder, its schema, registry files and generated files are untouched (D-14).
**Test:** The same test, reworked.

## Notes

- Worked directly in the main tree and not in a separate worktree. The caller asked for explicit-path staging, and the unrelated modified files (`registry/adjudication_rules.json`, `registry/policy_decisions.json`, `.planning/config.json`) were never staged.
- Lineage shape, VERSION, `EXPECTED_NORMALISATION` and recorded digests are unchanged.

---

_Fixer: Claude (gsd-code-fixer)_
