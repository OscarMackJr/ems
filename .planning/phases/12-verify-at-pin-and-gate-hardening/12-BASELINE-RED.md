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

## After plan 12-05 Task 1 (commit bc3d47e22d949ef01a3121212e6e4ec70501dcb2)

Measured on the working tree whose two changed files (publisher and v2_publication tests) are exactly the content
committed in bc3d47e (run immediately before the commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-05-t1-full
```

Totals: **974 passed, 1 failed, 0 skipped, 0 deselected** (328.67s). The +29 passing tests against 12-04 are the
new git-seam helper unit tests (git_head, git_is_ancestor, git_not_shallow, git_dirty, git_run, git_show `--`) and
the two publication_paths tests.

pytest exit code: **exit 1**

Failing node ids:

- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
  (accepted window opener from 12-04)

CI validators: 1 PASS, 2 PASS, 3 PASS, 4 PASS, 5 PASS, 6 PASS.

Accepted red set now (unchanged):

- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`

## After plan 12-05 Task 2 (commit 1b83c425565a83010b060efd0e108161bb16f8e2)

Measured on the working tree whose two changed files (publisher and v2_publication tests) are exactly the content
committed in 1b83c42 (run immediately before the commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-05-t2-full
```

Totals: **979 passed, 1 failed, 0 skipped, 0 deselected**. pytest printed a wall time of 44138.13s; this is a
host clock/sleep artefact, not test time (the v2_publication module alone took 151.89s in the same session). The +5
against Task 1 are `test_at_pin_record_blobs_must_match_the_superseded_commit`, `test_at_pin_dirty_tree_fails_closed`,
`test_at_pin_shallow_fails_closed`, `test_real_git_repo_at_pin_passes_and_dirty_fails` and
`test_cli_pre_publication_flag_is_removed`; the five pre-publication tests were renamed to their at-pin ids.

pytest exit code: **exit 1**

Failing node ids:

- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
  (accepted window opener from 12-04)

CI validators: 1 PASS, 2 PASS, 3 PASS, 4 PASS, 5 PASS, 6 PASS.

`.venv/Scripts/python.exe scripts/publish_archive_assessment_applicability_authority_v2.py --validate --at-pin` at the
working HEAD 1b83c42 (clean D-05 paths and publisher script): exit 1,
`AuthorityError: at-pin record must name the superseded 2.0.1 publication commit`. This is correct: HEAD is not a
publication pin (the committed record names 2.0.2 at ae15c74). It is not a red.

Accepted red set now (unchanged):

- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`

## After plan 12-06 Task 1 (commit 0054f2cb012f9a616b3083a2db59296f650e9d8c)

Measured on the working tree whose two changed files (publisher and v2_publication tests) are exactly the content
committed in 0054f2c (run immediately before the commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-06-t1-full
```

Totals: **987 passed, 1 failed, 0 skipped, 0 deselected** (405.51s). The +8 against 12-05 Task 2 are
`test_plain_validate_requires_ancestry`, the three `test_plain_validate_requires_blob_identity_at_head` cases
(authority, schema, manifest), `test_plain_validate_shallow_fails_closed`,
`test_plain_validate_at_pin_record_points_to_at_pin`,
`test_real_git_repo_plain_passes_after_record_and_later_commits_and_catches_head_drift` and the
`record_is_a_list` case of `test_malformed_published_files_raise_domain_error`.

pytest exit code: **exit 1**

Failing node ids:

- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
  (accepted window opener from 12-04)

CI validators: 1 PASS, 2 PASS, 3 PASS, 4 PASS, 5 PASS, 6 PASS. Validator 1 (plain `--validate`) passes against real
history: the record's publication commit ae15c74 is an ancestor of HEAD and the 10 D-05 blobs are identical.

Accepted red set now (unchanged):

- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`

## After plan 12-06 (commits 0054f2cb012f9a616b3083a2db59296f650e9d8c, c24f1d30f7a15a5e3fe73e594883ae46905795d7) — Task 2, GATE-06 opens the planned red

Commit 1 (0054f2c, D-06): 987 passed, 1 failed, exit 1; validators 1-6 PASS; red set unchanged (see the Task 1
section above).

Commit 2 (c24f1d3, GATE-06): measured on the working tree whose two changed files (publisher and v2_publication tests)
are exactly the content committed in c24f1d3 (run immediately before the commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-06-t2-full
```

Totals: **987 passed, 2 failed, 0 skipped, 0 deselected** (368.31s). The +1 test against commit 1 is
`test_pinned_script_digest_mismatch_fails_plain_validate`; `test_script_edit_after_publication_does_not_break_validate`
was rewritten as `test_script_edit_after_publication_fails_validate`.

pytest exit code: **exit 1**

Failing node ids:

- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
  (accepted window opener from 12-04; it now fails inside `validate_published` with the GATE-06 message)
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate`
  — newly opened by design, GATE-06 compares the live publisher with manifest f6b51cca…; closes at the 2.0.3
  publication (Phase 13).

CI validators:

| # | Validator | Result |
|---|-----------|--------|
| 1 | `scripts/publish_archive_assessment_applicability_authority_v2.py --validate` | **FAIL** (exit 1, by design): `AuthorityError: publisher script differs from the certified manifest digest (manifest publisher_script.sha256); a publisher edit needs a certified republication` |
| 2 | `scripts/build_archive_assessment_governance_decisions.py --validate` | PASS |
| 3 | `scripts/validate_archive_assessment_rule_proposals.py --validate` | PASS |
| 4 | `scripts/validate_archive_assessment_rule_proposals.py --validate-record` | PASS |
| 5 | `scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate` | PASS |
| 6 | `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py --validate` | PASS |

Frozen builders: `pytest tests/test_archive_assessment_demo3_w1_req_001_reply.py tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py --basetemp=.pytest-temp/p12-06-frozen`: 242 passed, exit 0.

Accepted red set now:

- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate`
- CI validator 1 (`publish_archive_assessment_applicability_authority_v2.py --validate`, script-digest message)

## After plan 12-07 (commit 8a519ba4effbc5692e32633a9461eaab5b96c1fc) — end of Phase 12

The suite and validators were run on the working tree that equals commit 8a519ba (run immediately before the
commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-07-full
```

Totals: **986 passed, 3 failed, 0 skipped, 0 deselected** (362.25s). Total test count unchanged at 989:
`test_superseded_v2_0_1_constants_match_git_history` was replaced by `test_superseded_v2_0_2_constants_match_git_history`.

pytest exit code: **exit 1**

Targeted run (`pytest` on the v2, v2_publication, lineage_validation and normalisation_claims modules,
`--basetemp=.pytest-temp/p12-07-t2`): 454 passed, 3 failed (the same three ids), no collection errors.

Failing node ids:

- `tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function`
  — newly opened by design: `schema()` now pins 2.0.3 / `SUPERSEDED_V2_0_2`, and the committed schema is
  re-emitted only in Phase 13 (`--emit-schema` was not run).
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate`
  (accepted since 12-06; the committed files are still the 2.0.2 publication)
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
  (accepted since 12-04)

CI validators:

| # | Validator | Result |
|---|-----------|--------|
| 1 | `scripts/publish_archive_assessment_applicability_authority_v2.py --validate` | **FAIL** (exit 1, by design): `AuthorityError: authority identity/version/status invalid; source_lineage supersedes does not name the 2.0.2 publication` (the committed authority is 2.0.2; the publisher now expects 2.0.3 superseding 2.0.2, so validation fails before the GATE-06 script-digest check is reached) |
| 2 | `scripts/build_archive_assessment_governance_decisions.py --validate` | PASS |
| 3 | `scripts/validate_archive_assessment_rule_proposals.py --validate` | PASS |
| 4 | `scripts/validate_archive_assessment_rule_proposals.py --validate-record` | PASS |
| 5 | `scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate` | PASS |
| 6 | `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py --validate` | PASS |

`git grep -n "SUPERSEDED_V2_0_1" -- scripts tests`: no output.

### Accepted red set at end of Phase 12 (closed by the Phase 13 publication and record commits)

- `tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function`
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate`
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
- CI validator 1 (`publish_archive_assessment_applicability_authority_v2.py --validate`)

Note for Phase 13: the publish sequence uses `--validate --at-pin` at the publication commit where Phase 09 used
`--validate --pre-publication` (removed in 12-05, no alias), then plain `--validate` at the record commit or later.

## After plan 12-08 Task 1 (commit d7a98f76a4f7ee455681d24dfc0cd922aec68667) — CR-01 / WR-01 publisher fix

The suite and validators were run on the working tree that equals commit d7a98f7 (run immediately before the
commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-08-t1-full
```

Totals: **986 passed, 3 failed, 0 skipped, 0 errors** (338.64s). Total test count unchanged at 989 versus 12-07
(Task 1 adapts existing tests; it adds none).

pytest exit code: **exit 1**

Targeted run (`tests/test_archive_assessment_applicability_authority_v2_publication.py`,
`--basetemp=.pytest-temp/p12-08-t1-pub`): 273 passed, 2 failed (`test_real_published_files_validate`,
`test_publisher_still_valid_and_digest_matches_manifest`), as expected.

Failing node ids:

- `tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function`
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate`
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`

CI validators:

| # | Validator | Result |
|---|-----------|--------|
| 1 | `scripts/publish_archive_assessment_applicability_authority_v2.py --validate` | **FAIL** (exit 1, by design): `AuthorityError: authority identity/version/status invalid; source_lineage supersedes does not name the 2.0.2 publication` (unchanged) |
| 2 | `scripts/build_archive_assessment_governance_decisions.py --validate` | PASS |
| 3 | `scripts/validate_archive_assessment_rule_proposals.py --validate` | PASS |
| 4 | `scripts/validate_archive_assessment_rule_proposals.py --validate-record` | PASS |
| 5 | `scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate` | PASS |
| 6 | `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py --validate` | PASS |

Accepted red set: unchanged (the D-16 end state: the three ids above plus CI validator 1).

## After plan 12-08 Task 2 (commit ce4caa7018065b25012d5bf437ceb0671fade867) — seam unit tests

The suite and validators were run on the working tree that equals commit ce4caa7 (run immediately before the
commit; no edit in between).

Command (Git Bash, repo root):

```
EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-08-t2-full
```

Totals: **1008 passed, 3 failed, 0 skipped, 0 errors** (339.37s). Total test count 1011 = 989 + 22 new test ids
(`test_git_commit_blob_argv_and_failures` x8, `test_git_index_flags_reports_flagged_and_missing_paths`,
`test_git_index_flags_rejects_bad_input_before_git` x5, `test_git_index_flags_rc_failure`,
`test_check_tree_matches_head_cases` x5, `test_plain_validate_binds_working_tree_to_head`,
`test_git_run_oserror_names_the_command`).

pytest exit code: **exit 1**

Seam run (`-k "git_commit_blob or git_index_flags or check_tree_matches_head or git_run_oserror or binds_working_tree"`,
`--basetemp=.pytest-temp/p12-08-t2-seam`): 23 passed (the 22 new ids plus `test_git_run_oserror_is_git_history_error`), 0 failed.

Failing node ids:

- `tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function`
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate`
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`

CI validators:

| # | Validator | Result |
|---|-----------|--------|
| 1 | `scripts/publish_archive_assessment_applicability_authority_v2.py --validate` | **FAIL** (exit 1, by design): `AuthorityError: authority identity/version/status invalid; source_lineage supersedes does not name the 2.0.2 publication` (unchanged) |
| 2 | `scripts/build_archive_assessment_governance_decisions.py --validate` | PASS |
| 3 | `scripts/validate_archive_assessment_rule_proposals.py --validate` | PASS |
| 4 | `scripts/validate_archive_assessment_rule_proposals.py --validate-record` | PASS |
| 5 | `scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate` | PASS |
| 6 | `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py --validate` | PASS |

Accepted red set: unchanged (the D-16 end state).
