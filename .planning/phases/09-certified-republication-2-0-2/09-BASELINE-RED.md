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
