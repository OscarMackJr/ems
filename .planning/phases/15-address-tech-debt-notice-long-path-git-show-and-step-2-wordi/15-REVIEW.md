---
phase: 15-address-tech-debt-notice-long-path-git-show-and-step-2-wordi
reviewed: 2026-11-17T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
  - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
  - schemas/archive_assessment_demo3_w1_req_001_notice_2_0_3.schema.json
findings:
  critical: 0
  warning: 5
  info: 3
  total: 8
status: issues_found
---

# Phase 15: Code Review Report

**Reviewed:** 2026-11-17
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Scope: `git diff 0ce0c79..HEAD` for the 2.0.3 notice builder, its test and its generated schema. The changes are: `--` added to `git_show`, a `core.longpaths` error hint, a fifth prerequisite, and new wording for step 2 and its outcome row. The schema change (`prerequisites` set to exactly 5 items) matches the builder.

The `--` fix works. I reproduced it with a `--no-checkout --shared` clone at a 211-character root with `core.longpaths=false`:
- Without `--`, `git show 1544dc1…:generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_negative_invariant_validation.json` exits 128 with `fatal: failed to stat '<rev>:<path>': Filename too long`. Without `--`, git calls lstat on the argument to check whether it is also a file name.
- With `--`, the same command exits 0.

So `--` alone fixes the step 3 failure from audit WARNING-1. This contradicts the phase SUMMARY ("'--' is defensive only; core.longpaths is the actual long-path mitigation"). It also means the new hint and the new prerequisite point the reader at the wrong step and the wrong cause. The step 2 rewording removes the old sentence. However, the outcome row still says more than plain `--validate` checks, and the notice quotes the frozen `at_pin_deferred` text, which contradicts the new wording. No blockers. The issues are in the accuracy of text sent to an external assessor and in test coverage.

## Warnings

### WR-01: The long-path prerequisite names the wrong step, and its command cannot run before the clone exists

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:419`
**Issue:** The prerequisite reads "On Windows, run git config core.longpaths true, or clone to a short checkout root such as C:\ems, before step 3".
- Now that `git_show` passes `--`, step 3's `git show` no longer touches the filesystem path (verified above). Step 3 no longer needs `core.longpaths`.
- The remaining Windows long-path exposure is in step 1. `git clone` and `git checkout <pub>` must create the 120-character tracked path `generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_negative_invariant_validation.json`. That fails once the checkout root is longer than about 139 characters.
- The prerequisite is listed before step 1, but `git config core.longpaths true` without `--global` cannot run before the repository exists. The clone happens inside step 1. Run outside a repo, it fails with "not in a git directory".
- The test suite already uses the correct form: `git -c core.longpaths=true clone` (test line 644).

The notice therefore sends the reader to the wrong step with a command that does not work at that point.
**Fix:**
```python
'On Windows with a deep checkout root, clone with git clone -c core.longpaths=true (or run git config --global core.longpaths true first), or clone to a short checkout root such as C:\\ems'
```
Drop "before step 3", or replace it with "before step 1". Then regenerate with `--build`.

### WR-02: The new error hint is now misleading for every `git show` failure

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:103`
**Issue:** The hint "if the path is long on Windows, run git config core.longpaths true or use a shorter checkout root" is added to every non-zero `git show`. With `--` in the argv, `git show <sha>:<path> --` no longer stats a worktree file, so a long checkout root can no longer cause this failure. Failures that can still happen are an unknown object or a path missing at that commit. For those, the hint sends the reader to fix something that is not wrong. Audit WARNING-1 was itself about a misleading hint, and this repeats it. The SUMMARY's claim that `--` is "defensive only" is wrong, and Phase 16 work may rely on it.
**Fix:** Add the long-path clause only when stderr shows that cause, and correct the SUMMARY's decision line:
```python
err = r.stderr.decode('utf-8', 'replace').strip()
hint = 'fetch full history (git fetch --unshallow)'
if 'Filename too long' in err: hint += '; on Windows set core.longpaths true or use a shorter checkout root'
raise GitHistoryError(f'{relative_path}@{commit}: git show failed: {err}; {hint}')
```
Keep the `fetch full history (git fetch --unshallow)` substring, because test line 350 checks for it. Change `test_git_show_error_hint_names_long_paths_and_unshallow` to match.

### WR-03: The rendered notice contradicts itself about where the record binding is checked

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:424, 428-429, 476`
**Issue:**
- Step 2 now says "The binding of the record to {pub} is enforced by step 3".
- The notice also quotes the frozen publisher's `AT_PIN_DEFERRED` word for word (line 476, "The deferred item printed at the pin reads:"). That text says: "...run plain --validate at the record commit or any later commit to check it". In other words, the step 1 output tells the reader that plain `--validate` (step 2) checks the binding.
- Outcome row 1 then says "Run step 2." straight after the deferred item.

A Hayes reader sees two different answers to "which step checks the binding". The phrase "any later commit" also survives here, although `test_verify_section` (test line 570) tries to keep it out of steps and outcomes. That check passes only because `at_pin_deferred` is a separate key. The deferred text is frozen at the pin and cannot change, but the notice can add context around it.
**Fix:** In `render_markdown`, after the deferred quote, and in outcome row 1's `meaning`, add a sentence such as: "Plain --validate at the record commit checks that the record is consistent with the commit it names; step 3 checks that this commit is {pub}." Add a test that the rendered Markdown contains this sentence.

### WR-04: Step 2's outcome row still says more than plain `--validate` checks

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:424, 429`
**Issue:** The row says step 2 PASS means "The publication files are byte-identical between the pin and the checked-out commit." Plain `--validate` (publisher `check_publication_record`, lines 849-855) compares `record['publication_commit']` with HEAD. It never checks that this commit is `1544dc1`. That commit is "the pin" only if the record names the pin, and step 3 is what enforces that (`load_inputs`, line 342). This is a narrower form of the WARNING-2 overstatement. Step 2's `pass_means` says "between the two commits" without naming them, so the reader will take them to be `{pub}` and `{rec}`, with the same effect.
**Fix:**
```python
'pass_means': f'Plain --validate at this commit checks that the publication files are byte-identical between the commit named by the publication record and this commit. Step 3 checks that the record names {pub}, and all three steps are required before re-pinning. ...'
'meaning': 'The publication files are byte-identical between the commit named by the publication record and the checked-out commit. Step 3 checks that this is the pin.'
```

### WR-05: No test covers the real long-path failure, and the clone tests hide it

**File:** `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:644, 647, 702-711`
**Issue:**
- `test_git_show_passes_double_dash` replaces `subprocess.run` and only checks the argv. It does not show that git behaves differently.
- `make_clone` forces `core.longpaths=true` both on the clone command and in the clone's config. So every CLI test run in a clone (`test_live_*`) has the WARNING-1 failure turned off.

If `--` is ever removed, or moved before the revision, no test fails on a real git call.
**Fix:** Add a test, skipped when not on Windows, that does the following:
1. Run `git clone --shared --no-checkout` into a directory nested under TMP so the root is longer than about 120 characters.
2. Set `core.longpaths false` in that clone.
3. Run the builder's `git_show` against it, for example by setting `MODULE.ROOT` to the clone, and check that it returns the blob.

This is the reproduction used in this review: without `--` the exit code is 128, with `--` it is 0.

## Info

### IN-01: Hard-coded absolute Windows path in a registry JSON string

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:419`
**Issue:** `C:\ems` now appears in `registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json`. `contains_absolute` (line 93) only looks at the start of a string, so it does not catch this. The project convention is that registry JSON contains no absolute paths. Here it is an example, not a reference, but it shows the guard has a gap.
**Fix:** Write "a short checkout root (for example a top-level folder on the drive)", or accept it deliberately and note why.

### IN-02: The new error-hint test repeats the existing one

**File:** `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:714-717`
**Issue:** It makes the same missing-commit call as `test_git_show_error_names_full_sha_and_fetch_hint` (line 346) and repeats the `git fetch --unshallow` check. It also needs a real git subprocess, although it only checks message text.
**Fix:** Add the `core.longpaths` check to the existing test, or rework it as described in WR-02.

### IN-03: The hint for a missing git binary tells the reader to fetch history

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py:102`
**Issue:** This existing line was next to the edited one. When git is not installed (`OSError`), the message still says "fetch full history (git fetch --unshallow)", which cannot help.
**Fix:** Use `'... git unavailable: {e}; install git and ensure it is on PATH'`.

---

_Reviewed: 2026-11-17_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
