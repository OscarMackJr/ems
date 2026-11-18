---
phase: 13-certified-republication-2-0-3
plan: 02
subsystem: archive-assessment v2 publisher
tags: [publication, PUB-10, PUB-11, PUB-12, D-01, D-02, D-03, PIN-01]
requirements: [PUB-10, PUB-11, PUB-12]
requirements-completed: [PUB-10, PUB-11, PUB-12]
key-files:
  created: []
  modified:
    - schemas/archive_assessment_applicability_authority_v2.schema.json
    - registry/archive_assessment_applicability_authority_v2.json
    - registry/archive_assessment_applicability_authority_v2_signoff.json
    - generated/archive-assessment/ems-aa3-v2/ (7 outputs, force-added)
metrics:
  completed: 2026-11-17
---

# Phase 13 Plan 02: Publish 2.0.3 Summary

2.0.3 is published from Oscar Mack's 2026-11-17 sign-off at **PUB = 1544dc19ba235d732c832d1651895550ed5a265d**. The commit holds exactly the 10 publication_paths() files. `--validate --at-pin` passes in the operator tree and in a fresh full `--no-local` clone detached at PUB. At PUB the red set is exactly the planned 5 tests plus validator 1, which carries the superseded-2.0.2 message. No decision changed. The record is untouched, and no commit sits after PUB (W1). Per N1, this SUMMARY is left uncommitted on disk until after WR03.

## Task 1: Emit, publish, commit
- Re-confirmation: `--validate-signoff` PASS. The dry-run Authority LF sha256 was 696116e765111c6f15237d876a9aca27f830c756707ee9c4b5e251d03aa0e0a6, equal to the signed value.
- `--emit-schema`: exit 0 (silent).
- `--publish`: exit 0. Output:
  `{"status": "PASS", "authority_sha256": "696116e765111c6f15237d876a9aca27f830c756707ee9c4b5e251d03aa0e0a6", "manifest_sha256": "3084dd94e7f831f11681621d13be1d6e75cc7db3452cb4189349f4b64cc3830e"}`
- `--validate-signoff` after publishing: PASS.
- Staging: 3 paths with `git add --` and 7 paths with `git add -f --`. `git diff --cached --name-only` listed exactly 10 paths.
- Commit: `feat(13-02): publish EMS-AA3 archive applicability authority 2.0.3`. PUB = 1544dc19ba235d732c832d1651895550ed5a265d.
- `git show --stat=300 --format= $PUB`, verbatim:
```
 generated/archive-assessment/ems-aa3-v2/EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION.md                        |  4 ++--
 generated/archive-assessment/ems-aa3-v2/EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION.json        | 12 ++++++------
 generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_decision_traceability.json         |  2 +-
 generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_matrix.json                        |  6 +++---
 generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_negative_invariant_validation.json |  4 ++--
 generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_semantic_validation.json           |  2 +-
 generated/archive-assessment/ems-aa3-v2/ems_aa3_v2_archive_applicability_authority_publication_manifest.json             | 26 +++++++++++++-------------
 registry/archive_assessment_applicability_authority_v2.json                                                              | 12 ++++++------
 registry/archive_assessment_applicability_authority_v2_signoff.json                                                      | 10 +++++-----
 schemas/archive_assessment_applicability_authority_v2.schema.json                                                        | 10 +++++-----
 10 files changed, 44 insertions(+), 44 deletions(-)
```
- The sorted `git diff-tree --no-commit-id --name-only -r $PUB` equals the sorted publication_paths() loaded via importlib under `python -I`: identical, 10 entries.
- `git diff --name-only $PUB~1 $PUB -- scripts tests docs`: empty.
- The authority at PUB has authority_id EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3 and version 2.0.3; supersedes version 2.0.2, commit ae15c7458e49c8f55cc58c61bab04bc716aa9892.
- Record status: empty (untouched).

## Task 2: At-pin (D-03)
`Env:GIT_*` was cleared in-process first (count 0).

**In-tree** (C:\temp\standars\ems, HEAD = PUB): exit 0. Raw stdout:
```
{"status": "PASS", "mode": "AT_PIN", "deferred": ["PUBLICATION_RECORD_BINDING: the publication record naming this commit is written in the next commit; run plain --validate at the record commit or any later commit to check it"]}
```
Parsed checks: status PASS, mode AT_PIN, deferred length 1, prefix `PUBLICATION_RECORD_BINDING: ` OK.

**Fresh clone:**
- Clone path: `<session scratchpad>\pin13` (new; it did not exist beforehand).
- Commands:
  - `git -c core.longpaths=true clone -q --no-local --no-checkout C:\temp\standars\ems <scratchpad>\pin13`
  - `git -C <S> -c core.longpaths=true checkout -q --detach 1544dc19ba235d732c832d1651895550ed5a265d`
- Checks: rev-parse HEAD = 1544dc19ba235d732c832d1651895550ed5a265d; is-shallow-repository = false; hardened status empty; `git log --oneline -1` = `1544dc1 feat(13-02): publish EMS-AA3 archive applicability authority 2.0.3`.
- `git --version` = git version 2.54.0.windows.1. Effective `core.autocrlf` = true (system setting, not overridden).
- Run from inside the clone: `C:\temp\standars\ems\.venv\Scripts\python.exe -I scripts\publish_archive_assessment_applicability_authority_v2.py --validate --at-pin`. Exit 0. Raw stdout:
```
{"status": "PASS", "mode": "AT_PIN", "deferred": ["PUBLICATION_RECORD_BINDING: the publication record naming this commit is written in the next commit; run plain --validate at the record commit or any later commit to check it"]}
```
- Parsed checks: status PASS, mode AT_PIN, 1 deferred entry, prefix OK.
- The clone was removed afterwards. The record status was still empty after both runs.

## Task 3: Red set at PUB and PUB-11
- HEAD = PUB throughout.
- Pytest (`EMS_FAIL_ON_SKIP=1`, fresh basetemp `p13-02-pub`): **5 failed, 1018 passed, 0 skipped, 0 errors, exit 1** (708 s). The FAILED ids are exactly the planned set:
  - tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate
  - tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest
  - tests/test_archive_assessment_applicability_authority_v2_publication.py::test_manifest_publisher_script_digest_matches_publication_commit
  - tests/test_archive_assessment_normalisation_claims.py::test_publication_record_normalisation_claim
  - tests/test_archive_assessment_normalisation_claims.py::test_manifest_publisher_script_normalisation_claim
- test_committed_schema_equals_schema_function now **passes**: it closed at PUB.
- Validators:
  - V1: exit 1, `AuthorityError: publication record still names the superseded 2.0.2 publication, so HEAD is the publication commit, not the record commit; run --validate --at-pin here, or plain --validate at the record commit or later`
  - V2 to V6: each exit 0, PASS.
- PUB-11 independent check (`git show` piped into `python -I`):
  - decisions LF sha256 at PUB = 4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f;
  - 80 rows at PUB vs 80 at ae15c74: same control ids, **0 differing rows** (full-row dict equality);
  - not_applicable_decision_state counts: RULE_PUBLISHED 3, NO_RULE_WILL_BE_PUBLISHED 18, NOT_YET_DECIDED 59;
  - rules: EMS-CTRL-030 production=KNOWN_FALSE; EMS-CTRL-039 production=KNOWN_FALSE; EMS-CTRL-052 ai_enabled=KNOWN_FALSE.
- Frozen reply artefacts: the `git diff --stat ae15c74 $PUB` over docs/DEMO3_W1_REQ_001_REPLY.md, the reply registry JSON and the reply schema is empty.

## Deviations from Plan
- `GIT_EDITOR`, `GIT_ASKPASS` and `GIT_TERMINAL_PROMPT`, which the harness sets, were cleared in-process before every git and publisher call (see 13-01).
- The clone and checkout commands added `-q`, which only suppresses progress output.
- N1/W1 GSD close-out deviation as planned: no SUMMARY, STATE or ROADMAP commit after PUB.

## Self-Check: PASSED
