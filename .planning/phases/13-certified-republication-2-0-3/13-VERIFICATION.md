---
phase: 13-certified-republication-2-0-3
verified: 2026-11-17T17:20:00Z
status: passed
score: 4/4 roadmap success criteria verified (SC3 under the D-01 reading, SC4 under the PUB+REC reading); 3/3 requirements satisfied (PUB-10, PUB-11, PUB-12)
overrides_applied: 0
re_verification: false
independent_verifier: "gsd-verifier, 2026-11-17, read-only git + gh + python -I over git show blobs"
gaps: []
human_verification: []
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
**Status:** passed. The orchestrator recorded this evidence from 13-01..13-04 (D-04). The independent gsd-verifier pass follows separately. That pass is recorded in "Independent verifier re-check" below and confirms the status: passed.

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

## Independent verifier re-check

The gsd-verifier re-ran these checks itself. It used only read-only git, `gh run view`, `git ls-remote`, and `python -I` (the repo venv interpreter, with the scripts kept in the session scratchpad, not the repo) over `git show <sha>:<path>` blobs. Per instruction it did not run pytest, the six validators or any publisher action. The red-set ledger, the at-pin outputs and the dry-run text above are the orchestrator's results, cited from 13-01..13-04 SUMMARY. They were not re-run here.

### Commit scope (D-02, PUB-12)

| Check | Result |
|-------|--------|
| `git diff-tree --no-commit-id --name-status -r PUB` | 10 paths, all `M`: the v2 authority, the sign-off, the schema and the 7 `generated/archive-assessment/ems-aa3-v2/` outputs, manifest included |
| Those 10 paths vs `publication_paths()` at PUB (L596: AUTHORITY, SCHEMA, SIGNOFF + OUT/{MATRIX, SEMANTIC, NEGATIVE, TRACE, CERT, REPORT, MANIFEST}) | same set, 10 entries |
| `git diff-tree ... REC` | only `registry/archive_assessment_applicability_authority_v2_publication_record.json` |
| `git diff-tree ... WR03` | only `tests/test_archive_assessment_lineage_validation.py`; a single added line, `assert before == (0, 'PASS'), ...` (D-07) |
| `git diff --name-only PUB~1 PUB -- scripts tests docs .github` | empty |
| `registry/adjudication_rules.json`, `registry/policy_decisions.json`, `.planning/config.json` in any of PUB/REC/WR03 | none |
| `git diff --stat PUB WR03 -- . ':(exclude).planning'` | only the record file (+5/-5) and the one test line |
| Commits after WR03 (3fd54ac, 144934b, f1212f9) | `git diff --name-only WR03 HEAD` outside `.planning/` is empty (0 paths) |

### Parentage and byte identity

- `git rev-parse REC^` = 1544dc19ba235d732c832d1651895550ed5a265d = PUB (W1).
- `git rev-parse WR03^` = REC. `git merge-base --is-ancestor REC WR03` exits 0.
- `git merge-base --is-ancestor ae15c74 PUB` exits 0.
- `git diff --quiet PUB WR03 -- <the 10 PUB paths>` exits 0, so the publication bytes at the CI head are identical to the pinned bytes.
- Published once: `git log ae15c74..HEAD` over the 10 publication paths and the record lists only 1544dc1 (publish) and 87a46d1 (record). No other 2.0.3 publication commit exists.

### Recomputation (`python -I`, from `git show` blobs)

| Item | Recomputed | Matches record |
|------|------------|----------------|
| Authority at PUB, LF sha256 | 696116e765111c6f15237d876a9aca27f830c756707ee9c4b5e251d03aa0e0a6 | yes: sign-off, certification, manifest entry and record@REC |
| Authority `authority_id` / `version` | EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3 / 2.0.3 | yes |
| `source_lineage.supersedes` | 2.0.2, commit ae15c7458e49c8f55cc58c61bab04bc716aa9892, sha a44eea1f…, decisions sha 4e746d1f… | yes (SC1) |
| Governance decisions file LF sha256 at ae15c74 / PUB / WR03 | 4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f at all three | yes (SC2) |
| Manifest at PUB, sha256 | 3084dd94e7f831f11681621d13be1d6e75cc7db3452cb4189349f4b64cc3830e | yes: record@REC `manifest_sha256` |
| Manifest artifact entries (9; the manifest excludes itself) | every entry's LF sha256 recomputed at PUB: 0 mismatches | yes |
| Manifest `publisher_script` digest cf694a06… | equals the publisher LF sha256 at PUB and at WR03 | yes |
| Certification | version 2.0.3, control_population 80, decided 21, undecided 59, semantic_conflicts 0, negative_invariants PASS, prohibitions all 0, signoff_sha256 equals the manifest entry | yes |
| Traceability | decided_count 21 (21 decision_records), undecided_count 59 (59 undecided_controls), published_on 2026-11-17 | yes |

### No decision changed (PUB-11, SC2)

- PUB has 80 `controls` rows and ae15c74 has 80. The control_id sets are equal, and **0 rows differ** on any field (full dict equality).
- The only top-level keys that differ from 2.0.2 are `authority_id`, `version` and `source_lineage`. `applicability_decision_ids`, `approved_governance_decision_ids`, the vocabularies and the semantics are equal.
- `not_applicable_decision_state` counts: RULE_PUBLISHED 3, NO_RULE_WILL_BE_PUBLISHED 18, NOT_YET_DECIDED 59 (21 decided / 59 undecided).
- Rules (ALL_CONDITIONS_MUST_MATCH): EMS-CTRL-030 production=KNOWN_FALSE, EMS-CTRL-039 production=KNOWN_FALSE, EMS-CTRL-052 ai_enabled=KNOWN_FALSE.

### Sign-off and record fields (PUB-10, SC1)

- Sign-off at PUB:
  - status PUBLICATION_SIGNOFF; approver Oscar Mack; role EMS_GOVERNANCE_AUTHORITY; date 2026-11-17;
  - authority_id and version 2.0.3; authority_sha256 696116e7… (CRLF_TO_LF);
  - the scope names "superseding 2.0.2 at ae15c74 with no decision changed".
- `dual_role_statement` is byte-equal to the publisher `DUAL_ROLE_STATEMENT` at PUB and to the 2.0.2 sign-off at ae15c74 (D-06). The role is also equal to 2.0.2's.
- The human gate is evidenced in 13-01-SUMMARY (resume signal `approve, date 2026-11-17`) and 13-04-SUMMARY (resume signal `push approved`).
- Record at REC: authority_id and version 2.0.3; authority_sha256 696116e7…; manifest_sha256 3084dd94…; publication_commit 1544dc19ba235d732c832d1651895550ed5a265d; CRLF_TO_LF.
- Record at PUB: still names 2.0.2 / ae15c74 / a44eea1f… / manifest 9991228a…. This is the designed reason why plain `--validate` is red at PUB (see SC3/SC4 below).

### CI and remote (PUB-12)

- `gh run view 44134035073 --json conclusion,headSha,jobs` returned: conclusion success, status completed, event workflow_dispatch, headBranch feature/ems-aa3-archive-applicability-authority, headSha 5498002c5eea3a6d9e3bfbb6766119880bb36804 (WR03), created 2026-11-17T17:10:31Z. Jobs: `validate` success, `archive-assessment` success.
- `git ls-remote origin refs/heads/feature/ems-aa3-archive-applicability-authority` = 5498002c5eea3a6d9e3bfbb6766119880bb36804 (WR03).
- `git ls-remote --tags origin`: 6 lines, consistent with the unchanged baseline. No local tag points at PUB, REC or WR03.
- `gh pr list --head feature/ems-aa3-archive-applicability-authority`: empty.

### Observable truths (roadmap success criteria)

| # | Success criterion | Status | Evidence |
|---|-------------------|--------|----------|
| SC1 | 2.0.3 published with certification, manifest and traceability, supersedes 2.0.2 at ae15c74, sign-off by Oscar Mack as EMS governance authority with the dual-role statement | VERIFIED | All 10 artifacts are present at PUB and their digests recompute. supersedes = ae15c74. Sign-off fields and dual-role byte equality are shown above. The approval signal is in 13-01-SUMMARY. |
| SC2 | Decisions digest 4e746d1f…, all 80 rows identical to 2.0.2, 21 decided / 59 undecided | VERIFIED | Independent recomputation: digest equal at ae15c74, PUB and WR03; 0 of 80 rows differ; 3/18/59. |
| SC3 | Publication commit holds only deliberate changes, staged by explicit path, and CI archive-assessment passes "on it" | VERIFIED (D-01 reading) | Scope: exactly `publication_paths()`, with no excluded or untracked file. CI is green at WR03, not at PUB. See the judgment below. |
| SC4 | Red window closed; all real-file tests green "at the publication commit" | VERIFIED (PUB+REC reading) | 1 red closes at PUB. 5 record-bound reds plus validator 1 close at REC = PUB's direct child (orchestrator pytest: 1023 passed at REC and at WR03). See the judgment below. |

### Verifier judgment: SC3 under D-01

The literal SC3 wording cannot be met by design. At PUB the publication record still names 2.0.2, because a commit cannot record its own SHA, so plain `--validate` (CI validator 1) must fail there. D-01 made the rewording explicit before execution, as Phase 9 D-04 did.

The substitute evidence is equivalent for what SC3 protects, which is that the bytes Hayes pins are the bytes CI certified. The verifier confirmed independently that:

- PUB is an ancestor of WR03;
- the 10 publication paths are byte-identical between PUB and WR03 (`git diff --quiet` exit 0);
- between PUB and WR03 the only non-planning changes are the record file and one added test assertion, neither of which the at-pin check or the pinned bytes depend on;
- CI run 44134035073 has headSha = WR03, and both jobs succeeded.

The "only deliberate changes" half of SC3 is met literally at PUB. **Accepted.** No override is needed, because D-01 is a planned decision that predates execution, not a deviation found afterwards.

### Verifier judgment: SC4

Read literally, "all real-file tests are green at the publication commit" is false at PUB. The orchestrator's own ledger shows 5 failures there. All 5, plus validator 1, are record-bound: they compare the record (which at PUB still names 2.0.2) with the new files. 13-CONTEXT ("Clarification after research") listed this exact red set as expected at PUB before execution. The ledger at PUB matches that set exactly, with no other red.

The window closes at REC, PUB's direct child (verified: `REC^` = PUB). The suite is fully green at REC and at WR03 (orchestrator: 1023 passed, 0 skipped, `EMS_FAIL_ON_SKIP=1`). The one non-record-bound red, `test_committed_schema_equals_schema_function`, is green at PUB itself. Hayes's own check at the pin (`--validate --at-pin`) passes at PUB in tree and in a fresh full clone, naming exactly one deferred check (PUBLICATION_RECORD_BINDING).

The verifier accepts the reading that the red window is closed across the PUB→REC pair, for the same structural reason as SC3. **Advisory, not a gap:** the ROADMAP SC4 sentence was not reworded the way D-01 reworded SC3. Phase 14's notice should therefore not claim "all tests green at the publication commit". It should say they are green at the record commit, and that the at-pin check passes at PUB.

### Requirements cross-reference

- The PLAN frontmatter IDs are PUB-10 and PUB-11 (13-01), PUB-10, PUB-11 and PUB-12 (13-02), PUB-10 and PUB-12 (13-03), and PUB-10, PUB-11 and PUB-12 (13-04). Together they cover exactly PUB-10, PUB-11 and PUB-12.
- REQUIREMENTS.md maps these three to Phase 13 and no others, so nothing is orphaned.
- PIN-01 is mapped to Phase 12 (Complete) and is demonstrated here only.
- REQUIREMENTS.md still shows PUB-10..12 as `[ ]` / Pending. Updating them is a tracking step for the orchestrator, not a verification gap.

### Anti-patterns, spot-checks, probes

- No TBD/FIXME/XXX markers in the Phase 13 planning docs. The only code change in this phase is the one-line WR-03 assertion, which is clean.
- No `scripts/*/tests/probe-*.sh` were declared. The at-pin runs are cited from the orchestrator. Per instruction, the verifier did not run any validator, pytest or publisher action.

### Verifier conclusion

The re-check matches every orchestrator claim it covered, with no discrepancy. Status: **passed**, score 4/4 roadmap SCs and 3/3 requirements. No gaps and no outstanding human items: the two human gates (sign-off and push go-ahead) were completed and are evidenced in the SUMMARYs.

## Notes

- The Claude Code harness sets `GIT_EDITOR`, `GIT_ASKPASS` and `GIT_TERMINAL_PROMPT`. They were removed in-process before every validator, publisher, at-pin and push call (count 0 each time). The pre-flight pytest run ran with them set, and its result equalled the expected D-16 set.
- No token or credential appears in this file or in any planning file.

---

_Recorded: 2026-11-17 (orchestrator, evidence per D-04)_
_Independently re-checked: 2026-11-17 (gsd-verifier)_
