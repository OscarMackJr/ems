---
phase: 13-certified-republication-2-0-3
plan: 03
subsystem: archive-assessment v2 publisher
tags: [record, red-window, WR-03, D-01, D-02, D-07, PUB-10, PUB-12]
requirements: [PUB-10, PUB-12]
key-files:
  created: []
  modified:
    - registry/archive_assessment_applicability_authority_v2_publication_record.json
    - tests/test_archive_assessment_lineage_validation.py
metrics:
  completed: 2026-11-17
---

# Phase 13 Plan 03: Close the red window Summary

The publication record was written by `--record-publication` from PUB and committed alone as **REC = 87a46d147413bd99e931c71a1ab165eb0903f014**. REC is the direct child of PUB (`git rev-parse REC^` = 1544dc19ba235d732c832d1651895550ed5a265d). At REC, plain `--validate`, all six validators and the full suite pass with 0 failed and 0 skipped. The red window is closed. WR-03 landed alone as **WR03 = 5498002c5eea3a6d9e3bfbb6766119880bb36804** (parent REC), and WR03 is green again. The 10 publication files are byte-identical across PUB, REC and WR03. Nothing was pushed.

## Task 1: Record commit (REC)
- Preconditions:
  - `git cat-file -t PUB` = commit;
  - HEAD = PUB, with no commit after PUB (W1);
  - the index was empty;
  - `Env:GIT_*` count was 0 after in-process clearing.
- `--record-publication 1544dc19ba235d732c832d1651895550ed5a265d`: exit 0 (silent).
- Staged one path; `git diff --cached --name-only` showed only the record. Commit: `feat(13-03): record 2.0.3 publication commit`.
- REC = 87a46d147413bd99e931c71a1ab165eb0903f014, and REC^ = PUB (parentIsPub=True).
- `git show --stat=300 --format= REC`, verbatim:
```
 registry/archive_assessment_applicability_authority_v2_publication_record.json | 10 +++++-----
 1 file changed, 5 insertions(+), 5 deletions(-)
```
- diff-tree shows exactly `registry/archive_assessment_applicability_authority_v2_publication_record.json`.
- Plain `--validate`: PASS, exit 0.
- Suite (`EMS_FAIL_ON_SKIP=1`, fresh basetemp `p13-03-rec`): **1023 passed in 648.48s, exit 0** (0 failed, 0 skipped, 0 errors).
- Validators V1 to V6 each exit 0 with PASS.
- `git diff --quiet PUB REC -- <10 publication_paths()>` exits 0. `git diff --name-only PUB REC -- . ':(exclude).planning'` shows only the record path.
- Record JSON:
  - publication_commit 1544dc19ba235d732c832d1651895550ed5a265d;
  - authority_id EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3, version 2.0.3;
  - digest_normalisation CRLF_TO_LF;
  - authority_sha256 696116e765111c6f15237d876a9aca27f830c756707ee9c4b5e251d03aa0e0a6 (equal to the --publish value);
  - manifest_sha256 3084dd94e7f831f11681621d13be1d6e75cc7db3452cb4189349f4b64cc3830e (equal to the --publish value).

## Closed red-set ledger
| Item | Red at | Closed at |
|------|--------|-----------|
| test_committed_schema_equals_schema_function | pre-dry-run (D-16) | PUB 1544dc1 |
| test_real_published_files_validate | pre-dry-run, PUB | REC 87a46d1 |
| test_publisher_still_valid_and_digest_matches_manifest | pre-dry-run, PUB | REC 87a46d1 |
| test_publication_record_normalisation_claim | PUB | REC 87a46d1 |
| test_manifest_publisher_script_normalisation_claim | PUB | REC 87a46d1 |
| test_manifest_publisher_script_digest_matches_publication_commit | PUB | REC 87a46d1 |
| CI validator 1 (plain --validate) | pre-dry-run (identity/supersedes), PUB ("still names the superseded 2.0.2 publication") | REC 87a46d1 |

## Task 2: WR-03 (D-07)
- Inserted one line after `before = outcome()` in test_d10_live_catalog_edit_or_delete_does_not_change_validate_outcome:
  `    assert before == (0, 'PASS'), f'--validate baseline must be PASS for D-10 to be meaningful: {before!r}'`
  The file stays LF. `git diff --stat` shows 1 insertion and 0 deletions.
- Single-test run: 1 passed (exit 0).
- Commit: `test(13-03): assert D-10 validate baseline is PASS (WR-03)`. WR03 = 5498002c5eea3a6d9e3bfbb6766119880bb36804. WR03^ = REC, and `merge-base --is-ancestor REC WR03` exits 0.
- `git show --stat=300 --format= WR03`, verbatim:
```
 tests/test_archive_assessment_lineage_validation.py | 1 +
 1 file changed, 1 insertion(+)
```
- diff-tree shows exactly `tests/test_archive_assessment_lineage_validation.py`. `Select-String "assert before == \(0, 'PASS'\)"` at HEAD finds 1 match.
- Suite at WR03 (fresh basetemp `p13-03-wr03`): **1023 passed in 572.42s, exit 0** (0 failed, 0 skipped, 0 errors). V1 to V6 each exit 0 with PASS.
- `git diff --quiet PUB WR03 -- <10 paths>` exits 0, and `git diff --quiet REC WR03 -- <record>` exits 0.

## Deviations from Plan
- `GIT_*` variables set by the harness were cleared in-process before every git and validator call (see 13-01).
- N1, as planned: 13-02 and 13-03 SUMMARYs and the wave 2/3 tracking updates are committed together in one .planning-only commit after WR03.

## Self-Check: PASSED
