# Phase 12 — Baseline red set (red window accounting)

## Baseline (before any Phase 12 code change)

Recorded: 2026-11-16, HEAD 87b5cd59c0564c8877eccb184038057bce107a72, before any edit of scripts/, tests/ or .github/ by Phase 12.

`git status --short scripts tests .github` showed no tracked modification under these paths (only pre-existing
untracked files unrelated to this project).

Command (Git Bash, repo root; bash expands the glob):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-01-baseline
```

Totals: **918 passed, 0 failed, 0 skipped, 0 deselected** (310.51s)

pytest exit code: **exit 0**

Failing node ids: none.

CI validators (each run separately from the repo root):

| # | Validator | Result |
|---|-----------|--------|
| 1 | `scripts/publish_archive_assessment_applicability_authority_v2.py --validate` | PASS |
| 2 | `scripts/build_archive_assessment_governance_decisions.py --validate` | PASS |
| 3 | `scripts/validate_archive_assessment_rule_proposals.py --validate` | PASS |
| 4 | `scripts/validate_archive_assessment_rule_proposals.py --validate-record` | PASS |
| 5 | `scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate` | PASS |
| 6 | `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py --validate` | PASS |

## Planned red window (D-16)

Expected red set per plan:

- 12-01: none
- 12-02: none
- 12-03: none
- 12-04: `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
- 12-05: `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
- 12-06: the above, plus `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate` and CI validator 1
- 12-07: the above, plus `tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function`

Rule: the red set may only grow by the listed ids at the listed plan. Anything red outside this ledger blocks the commit.

## Environmental notes

D-15: a fresh Windows clone fails `test_committed_notice_files_validate` because the notice files have no
`eol=lf` attribute (autocrlf rewrites line endings, so the digests no longer match). The working repo and
ubuntu CI are unaffected. The fix is deferred and out of scope for Phase 12.

## After plan 12-01 (commit 8dd37783bc42f3e047ee3313928f91a8dd3ac3ff)

Measured on the working tree whose four changed files are exactly the content committed in 8dd3778 (run
immediately before the commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-01-full
```

Totals: **919 passed, 0 failed, 0 skipped, 0 deselected** (317.43s). The +1 against the baseline is the new
`test_guard_ignores_skip_in_deselected_non_archive_module`.

pytest exit code: **exit 0**

Failing node ids: none.

CI validators: 1 PASS, 2 PASS, 3 PASS, 4 PASS, 5 PASS, 6 PASS.

Accepted red set now: none.

## After plan 12-02 (commit 1e846ff30cc9abc6317eb5211f6f53d1feb2d636)

Measured on the working tree whose three changed test files are exactly the content committed in 1e846ff (run
immediately before the commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-02-full
```

Totals: **924 passed, 0 failed, 0 skipped, 0 deselected** (321.75s). The +5 against 12-01 are the new
`test_d10_live_catalog_edit_or_delete_does_not_change_validate_outcome`,
`test_validate_cli_rejects_note_collision_for_real_changed_answers`, `test_validate_cli_passes_for_certified_answers`,
`test_publisher_validate_governance_decisions_rejects_note_collision_for_real_changed_answers` and
`test_publisher_validate_governance_decisions_passes_for_certified_answers` (rewritten tests keep their ids).

pytest exit code: **exit 0**

Failing node ids: none.

CI validators: 1 PASS, 2 PASS, 3 PASS, 4 PASS, 5 PASS, 6 PASS.

Accepted red set now: none.

## After plan 12-03 Task 1 (commit e0d929b4b4d83fb599d204fc6a4998b3e612f2a2)

Measured on the working tree whose one changed test file is exactly the content committed in e0d929b (run
immediately before the commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-03-t1-full
```

Totals: **932 passed, 0 failed, 0 skipped, 0 deselected** (323.85s). The +8 against 12-02 come from the D-08
row-tamper test now running 12 cases (3 rows x 4 tampers) instead of 4; the renamed 2.0.0 anchor test keeps a
count of 1.

pytest exit code: **exit 0**

Failing node ids: none.

CI validators: 1 PASS, 2 PASS, 3 PASS, 4 PASS, 5 PASS, 6 PASS.

Accepted red set now: none.

## After plan 12-03 Task 2 (commit a3a9c9beb6fce86e29a7d2d8b46b261c06f5e8ea)

Measured on the working tree whose two changed files (reply builder and reply tests) are exactly the content
committed in a3a9c9b (run immediately before the commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-03-t2-full
```

Totals: **935 passed, 0 failed, 0 skipped, 0 deselected** (331.18s). The +3 against 12-03 Task 1 are the new
`test_resolve_record_commit_fails_when_commit_missing_or_not_ancestor` cases (`mb_rc` 128, `cat_exc` OSError,
`mb_exc` OSError).

pytest exit code: **exit 0**

Failing node ids: none.

CI validators: 1 PASS, 2 PASS, 3 PASS, 4 PASS, 5 PASS, 6 PASS.

Accepted red set now: none.

## After plan 12-04 (commit 68231fce71ca6ed221909311ecc870208028932d) — red window opens

Measured on the working tree whose three changed files (publisher and two test files) are exactly the content
committed in 68231fc (run immediately before the commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-04-full
```

Totals: **945 passed, 1 failed, 0 skipped, 0 deselected** (347.07s). The +11 tests against 12-03 Task 2 are the
eight `test_malformed_published_files_raise_domain_error` cases, `test_dry_run_summary_differ_branch_is_reachable`
and the two `test_validate_lineage_rejects_non_object` cases.

pytest exit code: **exit 1**

Failing node ids:

- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
  — newly opened by design: live publisher differs from manifest publisher_script.sha256 f6b51cca… (live LF digest
  now ee810746…), closes at the 2.0.3 publication (Phase 13).

CI validators: 1 PASS, 2 PASS, 3 PASS, 4 PASS, 5 PASS, 6 PASS.

Mutation invariance check (fresh `run_mutations` equals the committed N_NEGATIVE `negative_invariant_tests`): True.

Accepted red set now:

- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
