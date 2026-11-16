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
