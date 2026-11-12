# Phase 09 — Baseline red set (red window accounting)

## Baseline (before any Phase 9 code change)

Recorded: 2026-11-12, HEAD 766062f, before any edit of scripts/ or tests/ by Phase 9.

Command (PowerShell, repo root):

```
python -m pytest tests -k archive_assessment -p no:cacheprovider -q -rf --basetemp=<scratchpad>\p9-baseline
```

Totals: **694 passed, 3 failed, 7 deselected** (182.10s)

Failing node ids:

- tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function
- tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate
- tests/test_archive_assessment_demo3_w1_req_001_reply.py::test_publisher_still_valid_and_digest_matches_manifest

Matches the 3 reds accepted in 08-VERIFICATION. The second and third fail with
`AuthorityError: source_lineage supersedes does not name the 2.0.0 publication; source_lineage v1_baseline entry missing or invalid`
(the committed 2.0.1 artifacts against the hardened Phase 8 validator).

`git status --short scripts tests` at the time of writing shows only pre-existing untracked
files unrelated to this project (Wave 2D / test-quality scripts); no tracked file under
scripts/ or tests/ is modified.

## After Task 2a (commit 69ea357)

Command: `python -m pytest tests/test_archive_assessment_applicability_authority_v2.py tests/test_archive_assessment_applicability_authority_v2_publication.py tests/test_archive_assessment_lineage_validation.py -p no:cacheprovider -q -rf --basetemp=<scratchpad>\p9-01a`

Totals: **376 passed, 2 failed**

- tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function (baseline red; committed schema predates 2.0.2, re-emitted in 09-04)
- tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate (baseline red; now `authority identity/version/status invalid; source_lineage supersedes does not name the 2.0.1 publication` because the committed artifacts are still 2.0.1 until 09-04)

No new failing ids. The three new behavior tests pass. The reply test red is outside these modules (plan 09-02).

## After Task 2b (commit 23cfad6) and fixture fix

First run after 23cfad6: **383 passed, 3 failed**. The new id was
tests/test_archive_assessment_lineage_validation.py::test_d10_live_catalog_edit_or_delete_does_not_change_build_or_validation,
a fixture defect: it points ROOT at a throwaway repo with no 2.0.1 history, so the D-08 comparison
correctly failed closed with GitHistoryError. Fixed in the test by serving the real 2.0.1 blob through git_show
(same approach as the publication `env` fixture).

After the fix, same three modules: **384 passed, 2 failed** — the "after plan 01" set equals the "after 2a" set:

- tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function
- tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate

The D-04 byte-identity test skips until the real 2.0.2 record exists (plan 09-05).

## After plan 02 (commits 82cff90, 02a4ea3)

`python scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate` -> PASS (frozen on 2.0.1 @ 31addfa / record @ 4d9b7c1).

Command: `python -m pytest tests/test_archive_assessment_demo3_w1_req_001_reply.py -p no:cacheprovider -q -rf --basetemp=<scratchpad>\p9-02`

Totals: **63 passed, 1 failed**

- tests/test_archive_assessment_demo3_w1_req_001_reply.py::test_publisher_still_valid_and_digest_matches_manifest

This is the baseline red unchanged. It calls the live `V2.validate_published()` and compares the live publisher
script digest to the live manifest, so it tests the live publication, not the frozen reply validator. It
goes green only when 2.0.2 is published (09-04). Every reply-validator test is green.

Accepted red set now (all clear at 09-04 publication):
- tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function
- tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate
- tests/test_archive_assessment_demo3_w1_req_001_reply.py::test_publisher_still_valid_and_digest_matches_manifest

## After plan 03 (commit 251cb30) — pre-publication freeze point

Command: `python -m pytest tests -k archive_assessment -p no:cacheprovider -q -rf --basetemp=<scratchpad>\p9-03`

Totals: **717 passed, 3 failed, 7 deselected** — exactly the accepted red set above, no new ids. Publisher and tests are frozen from here until 09-04 publishes.
