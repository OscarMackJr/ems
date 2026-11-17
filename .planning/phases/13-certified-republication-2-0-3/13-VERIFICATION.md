---
phase: 13-certified-republication-2-0-3
verified: 2026-11-17T17:20:00Z
status: passed
requirements: [PUB-10, PUB-11, PUB-12]
publication_commit: 1544dc19ba235d732c832d1651895550ed5a265d
record_commit: 87a46d147413bd99e931c71a1ab165eb0903f014
wr03_commit: 5498002c5eea3a6d9e3bfbb6766119880bb36804
ci_run_id: 44134035073
ci_head_sha: 5498002c5eea3a6d9e3bfbb6766119880bb36804
at_pin_clone_method: "git clone --no-local --no-checkout + checkout --detach <PUB>, system core.autocrlf, python -I"
---

# Phase 13 Verification: Certified republication 2.0.3

**Phase goal:** Publish `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3` once, with certification, manifest and traceability, signed off by the EMS governance authority, with no decision changed.
**Status:** passed. The orchestrator recorded this evidence from 13-01..13-04 (D-04). The independent gsd-verifier pass follows separately.

## Key identifiers

| Item | Value |
|------|-------|
| Publication commit PUB (Hayes pins) | 1544dc19ba235d732c832d1651895550ed5a265d |
| Record commit REC (direct child of PUB) | 87a46d147413bd99e931c71a1ab165eb0903f014 |
| WR-03 commit WR03 (CI head) | 5498002c5eea3a6d9e3bfbb6766119880bb36804 |
| Authority | EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3, version 2.0.3 |
| Authority LF sha256 | 696116e765111c6f15237d876a9aca27f830c756707ee9c4b5e251d03aa0e0a6 |
| Manifest sha256 | 3084dd94e7f831f11681621d13be1d6e75cc7db3452cb4189349f4b64cc3830e |
| Governance decisions LF sha256 | 4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f |
| Supersedes | 2.0.2 @ ae15c7458e49c8f55cc58c61bab04bc716aa9892 |
| Sign-off | Oscar Mack, EMS_GOVERNANCE_AUTHORITY, 2026-11-17 (resume signal `approve, date 2026-11-17`; mechanical date check True), dual-role statement present and byte-equal to the publisher DUAL_ROLE_STATEMENT |
| CI run | 44134035073 (workflow_dispatch, 2026-11-17), conclusion success; jobs validate success and archive-assessment success; headSha 5498002c5eea3a6d9e3bfbb6766119880bb36804 |

## At-pin evidence (PIN-01 demonstrated, D-03)

**In-tree run** (C:\temp\standars\ems, HEAD = PUB). `--validate --at-pin` exited 0. Raw output:
```
{"status": "PASS", "mode": "AT_PIN", "deferred": ["PUBLICATION_RECORD_BINDING: the publication record naming this commit is written in the next commit; run plain --validate at the record commit or any later commit to check it"]}
```

**Fresh-clone run.** Commands:
```
git -c core.longpaths=true clone -q --no-local --no-checkout C:\temp\standars\ems <session scratchpad>\pin13
git -C <S> -c core.longpaths=true checkout -q --detach 1544dc19ba235d732c832d1651895550ed5a265d
cd <S>; C:\temp\standars\ems\.venv\Scripts\python.exe -I scripts\publish_archive_assessment_applicability_authority_v2.py --validate --at-pin
```
- Clone state: HEAD = PUB; is-shallow-repository = false; the hardened status was empty.
- Environment: git version 2.54.0.windows.1, effective core.autocrlf = true (system setting, not overridden).
- Exit 0. Raw output:
```
{"status": "PASS", "mode": "AT_PIN", "deferred": ["PUBLICATION_RECORD_BINDING: the publication record naming this commit is written in the next commit; run plain --validate at the record commit or any later commit to check it"]}
```

Parsed checks for both runs: status PASS, mode AT_PIN, exactly 1 deferred entry, and that entry starts with `PUBLICATION_RECORD_BINDING: `.

**Parent check (W1):** `git rev-parse "87a46d1^"` = 1544dc19ba235d732c832d1651895550ed5a265d. The record is in the commit immediately after the pin, as the at-pin deferred text promises.

## D-02 commit scope

PUB, from `git show --stat=300 --format=`:
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
REC:
```
 registry/archive_assessment_applicability_authority_v2_publication_record.json | 10 +++++-----
 1 file changed, 5 insertions(+), 5 deletions(-)
```
WR03:
```
 tests/test_archive_assessment_lineage_validation.py | 1 +
 1 file changed, 1 insertion(+)
```
- Sorted `git diff-tree --no-commit-id --name-only -r PUB` equals sorted publication_paths() (imported under `python -I`): identical, 10 entries.
- `git diff --name-only PUB~1 PUB -- scripts tests docs` is empty.
- None of registry/adjudication_rules.json, registry/policy_decisions.json, .planning/config.json or any untracked file is in any of the three commits.

## PUB-11: no decision changed (independent, `git show` piped into `python -I`)

- The decisions file LF sha256 at PUB is 4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f.
- The 80 authority rows at PUB were compared with the 80 at ae15c74: same control ids, and **0 rows differ** on any field.
- not_applicable_decision_state counts at PUB: RULE_PUBLISHED 3, NO_RULE_WILL_BE_PUBLISHED 18, NOT_YET_DECIDED 59.
- Rules: EMS-CTRL-030 production=KNOWN_FALSE, EMS-CTRL-039 production=KNOWN_FALSE, EMS-CTRL-052 ai_enabled=KNOWN_FALSE.
- The dry run printed: "No decision changed: the governance decisions LF sha256 4e746d1f… equals the 2.0.2 value" and "80 controls identical to 2.0.2".
- The frozen reply artefacts show an empty `git diff --stat ae15c74 PUB`.

## Red-set ledger

All pytest runs used `EMS_FAIL_ON_SKIP=1`, all `tests/test_archive_assessment_*.py`, and a fresh basetemp.

| Commit | Pytest | Red items |
|--------|--------|-----------|
| pre-dry-run (HEAD 5995192 + working tree) | 3 failed, 1020 passed, 0 skipped | test_committed_schema_equals_schema_function, test_real_published_files_validate, test_publisher_still_valid_and_digest_matches_manifest; V1 (identity/version/status invalid; supersedes not 2.0.2). V2–V6 PASS |
| PUB 1544dc1 | 5 failed, 1018 passed, 0 skipped | test_real_published_files_validate, test_publisher_still_valid_and_digest_matches_manifest, test_manifest_publisher_script_digest_matches_publication_commit, test_publication_record_normalisation_claim, test_manifest_publisher_script_normalisation_claim; V1 ("publication record still names the superseded 2.0.2 publication …"). V2–V6 PASS |
| REC 87a46d1 | **1023 passed** in 648.48s, exit 0 | none; V1–V6 PASS |
| WR03 5498002 | **1023 passed** in 572.42s, exit 0 | none; V1–V6 PASS |

## CI (PUB-12)

- Run 44134035073 was dispatched with `gh workflow run ems-validate.yml --ref feature/ems-aa3-archive-applicability-authority` after the push. Conclusion success; headSha = WR03; jobs validate success and archive-assessment success.
- The plain push succeeded (49c7b08..5498002); the token fallback was not used. `git ls-remote` shows the remote tip = WR03.
- `git merge-base --is-ancestor REC WR03` exits 0.
- `git diff --quiet PUB WR03 -- <10 publication_paths()>` exits 0, and `git diff --quiet REC WR03 -- <record>` exits 0.
- `gh pr list --head feature/ems-aa3-archive-applicability-authority` is empty. No tag points at PUB, REC or WR03.
- `git ls-remote --tags origin` after the push is byte-identical to the pre-push baseline (6 lines: ems-v0.4.5-wave1, ems-v0.5.0-wave2b, ems-v0.6.0-wave2c and their peeled refs).

## Judgment call: SC3 reading (D-01)

- ROADMAP SC3 asks for the CI archive-assessment job to pass "on" the publication commit.
- CI was green at the WR-03 head, not at PUB. At PUB the record still names 2.0.2, so plain `--validate` (CI validator 1) is red there by design: the commit that records a SHA cannot be the commit it names.
- Plain `--validate` at WR03 proves that PUB is an ancestor and that all 10 publication files are byte-identical between PUB and HEAD. The green run therefore certifies exactly the bytes Hayes pins.
- Hayes verifies at the pin itself with `--validate --at-pin`, which passes at PUB in this tree and in a fresh full clone (above).
- No CI change and no at-pin CI mode were added.

## Judgment call: SC4 reading

- ROADMAP SC4 says the red window is closed and all real-file tests are green at the publication commit.
- At PUB the schema test closes and at-pin passes. The record-bound reds close at REC, which is PUB's direct child.
- The window is closed across PUB and REC.

| Item red before/at PUB | Closes at |
|------------------------|-----------|
| tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function | PUB 1544dc1 (green at PUB) |
| tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate | REC 87a46d1 |
| tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest | REC 87a46d1 |
| tests/test_archive_assessment_normalisation_claims.py::test_publication_record_normalisation_claim | REC 87a46d1 |
| tests/test_archive_assessment_normalisation_claims.py::test_manifest_publisher_script_normalisation_claim | REC 87a46d1 |
| tests/test_archive_assessment_applicability_authority_v2_publication.py::test_manifest_publisher_script_digest_matches_publication_commit | REC 87a46d1 |
| CI validator 1 (plain --validate; "still names the superseded 2.0.2 publication" at PUB) | REC 87a46d1 |

## Push scope

- The D-08 push set the remote branch to WR03 exactly, using the refspec `5498002c5eea3a6d9e3bfbb6766119880bb36804:refs/heads/feature/ems-aa3-archive-applicability-authority` (D-01).
- The push published 85 commits (Phases 10–13) and fast-forwarded the remote from 49c7b08.
- These .planning-only commits after WR03 stayed local:
  - 3fd54ac docs(13-02,13-03): publication and record summaries, tracking after waves 2-3
  - docs(13-04): record 2.0.3 publication and CI evidence (this evidence commit; its SHA is in 13-04-SUMMARY.md)
- They change only `.planning/` paths. The Phase 14 push publishes them.

## Requirements

| ID | Status | Evidence |
|----|--------|----------|
| PUB-10 | SATISFIED | Oscar Mack signed off on the full dry run with an explicit date (13-01). 2.0.3 was published at PUB with certification, manifest and traceability, superseding 2.0.2 at ae15c74. The red window is closed at REC. |
| PUB-11 | SATISFIED | Decisions digest 4e746d1f is unchanged, 0 of 80 rows differ against ae15c74, counts are 3/18/59, and the three rules are as above. |
| PUB-12 | SATISFIED (D-01 reading) | PUB holds exactly the 10 publication_paths(), staged by explicit path. CI run 44134035073 is green at WR03, which is byte-identical to PUB over those paths. |
| PIN-01 | DEMONSTRATED | `--validate --at-pin` passes at PUB in this tree and in a fresh full non-shallow clone. |

## Notes

- The Claude Code harness sets `GIT_EDITOR`, `GIT_ASKPASS` and `GIT_TERMINAL_PROMPT`. They were removed in-process before every validator, publisher, at-pin and push call (count 0 each time). The pre-flight pytest run ran with them set, and its result equalled the expected D-16 set.
- No token or credential appears in this file or in any planning file.

---

_Recorded: 2026-11-17 (orchestrator, evidence per D-04)_
