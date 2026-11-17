# Phase 13: Certified Republication 2.0.3 - Context

**Gathered:** 2026-11-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Publish `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3` once. It uses the publisher and validators in the final 2.0.3 form that Phase 12 left them in. 2.0.3 supersedes 2.0.2 at `ae15c74`, and every applicability decision stays identical to 2.0.2. The steps:

- a dry run;
- sign-off by Oscar Mack as EMS governance authority;
- the publication commit;
- `--validate --at-pin`, run in two places;
- the publication-record commit;
- the WR-03 test commit;
- a push and a green CI run.

Covers PUB-10, PUB-11 and PUB-12.

This phase closes the D-16 red window: 3 tests plus CI validator 1 (`12-BASELINE-RED.md`). It does not write the notice to Hayes, which is Phase 14 (NOTICE-03, PIN-03, CLAIM-01..03). It does not change the frozen reply or the frozen 2.0.2 notice. It does not decide any of the other 59 controls.

Unlike Phase 9, no publisher code change is planned before the publication. Phase 12 already put the publisher into its final 2.0.3 form: `VERSION = '2.0.3'`, `SUPERSEDED_V2_0_2`, at-pin mode, plain-mode byte identity, GATE-06 digest, and the truthful dry-run and manifest texts.

</domain>

<decisions>
## Implementation Decisions

### CI evidence (PUB-12, SC3)
- **D-01: Where the green CI run comes from.** Hayes pins the publication commit. At that commit the publication record still names 2.0.2, so plain `--validate` (CI validator 1) is red there by design and points the operator to `--validate --at-pin`. The green CI run is therefore taken at the branch head after the record commit. Per D-07 that head is the WR-03 test commit, a descendant of the record commit.
  - Plain `--validate` at that head itself proves that the publication commit is an ancestor and that the 10 `publication_paths()` files are byte-identical between the publication commit and HEAD (12 D-06, with the 12-08 working-tree binding). The green run therefore certifies the pinned bytes.
  - The plan states this rewording of ROADMAP SC3 explicitly, as Phase 9 D-04 did.
  - No CI change is made, and no at-pin CI mode or auto-detection is added.
- **D-02: Checking the commit contents (PUB-12 "only deliberate changes").** This is a verification-step command, not a pytest:
  - `git show --stat --format= <pub>` must list exactly the 10 `publication_paths()` files.
  - `git show --stat --format= <record>` must list only `registry/archive_assessment_applicability_authority_v2_publication_record.json`.
  - The WR-03 commit must list only the one test file.
  - The output is recorded in `13-VERIFICATION.md`.

### At-pin proof (PIN-01 demonstrated, SC4)
- **D-03: Run at-pin in two places.**
  1. In the operator working tree, immediately after the publication commit and before writing the record. This is the gate that replaces Phase 9's `--validate --pre-publication`.
  2. In a fresh full clone (not shallow) of the repo, checked out at the publication SHA with no later commit. This is what Hayes does.

  Both must print `{"status":"PASS","mode":"AT_PIN","deferred":["PUBLICATION_RECORD_BINDING"]}` (key order as the publisher emits it) with exit 0. If either fails, stop. Do not write the record. Report the failure.
- **D-04: Where the evidence goes.** The at-pin JSON outputs, the publication SHA, the clone method and the CI run id go in planning docs only: `13-VERIFICATION.md` and STATE.md, as in 09 D-06. The publication record and the schemas keep their shape.

### Sign-off summary and record
- **D-05: The dry-run text is used as it stands.** The "What changed in 2.0.3" section of the dry-run summary (publisher `dry_run_summary`, L632-656) is used as is:
  - the derived lineage lines;
  - the negative-mutation count;
  - the closed schema levels;
  - the row comparison 2.0.2 → 2.0.3;
  - the fixed "Gates GATE-01 to GATE-10" line.

  No publisher edit is made before the dry run. Oscar reads the full dry run at the blocking sign-off checkpoint.
- **D-06: The sign-off record.** It reuses the 2.0.2 wording exactly:
  - role `EMS_GOVERNANCE_AUTHORITY`;
  - `dual_role_statement`: "Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it.";
  - the date of approval.

  At the blocking checkpoint Claude presents the dry run and the proposed sign-off record. The record is written only after Oscar approves. `PUBLISHED_ON` comes from the sign-off date (06 D-10).

### WR-03 and post-publication commits
- **D-07: The WR-03 test fix.** Once validator 1 is green at the record commit, `test_d10_live_catalog_edit_or_delete_does_not_change_validate_outcome` (`tests/test_archive_assessment_lineage_validation.py` L357) must assert that its baseline is `(0, 'PASS')`, not only that the result is the same before and after.
  - It lands in a separate test-only commit after the record commit and before the push, so the record commit stays record-only.
  - The full archive suite and all six validators must be green at that commit.
- **D-08: Push and CI.** This is the same as 2.0.2 (09 D-05):
  - After the WR-03 commit there is a blocking checkpoint. Nothing is pushed until Oscar Mack gives the go-ahead.
  - On the go-ahead, Claude pushes `feature/ems-aa3-archive-applicability-authority` using the GitHub CLI token workaround recorded in STATE.md: a one-command `http.extraheader` via `GIT_CONFIG_*`, with credential.helper cleared.
  - Claude then dispatches the `archive-assessment` workflow on the branch (`gh workflow run`), waits for it to finish, and confirms it passed at the head SHA.
  - No PR, merge or tag is made in this phase.

### Carried forward (not re-asked)
- **Publish sequence.** This follows the 2.0.2 sequence (09 carried-forward and 06 D-21), with at-pin in place of pre-publication:
  1. The tree is clean and the D-16 red set is confirmed.
  2. `--publish --dry-run`, then the blocking sign-off checkpoint.
  3. Write the sign-off record (D-06), then `--emit-schema` and `--publish`.
  4. The publication commit, staging exactly the 10 publication files by explicit path.
  5. `--validate --at-pin`, in the tree and in a fresh clone (D-03).
  6. `--record-publication <sha>`, then the record commit.
  7. Plain `--validate` PASS, all six CI validators PASS, and the full archive-assessment pytest suite green with `EMS_FAIL_ON_SKIP=1`. This closes the red window.
  8. The WR-03 commit (D-07), then the push and CI checkpoint (D-08).
- **Committed schema.** It is re-emitted (`--emit-schema`) as part of the publication. This closes the red test `test_committed_schema_equals_schema_function`.
- **File handling.** The v2 files are overwritten in place (06 D-07), and there is no publication history file.
- **Contents of the publication commit.** It holds only the generated publication, which is the 10 D-05 files: the v2 registry authority, the regenerated schema, the sign-off and the 7 `ems-aa3-v2/` outputs, manifest included.
- **No decision change (PUB-11).** The decisions digest stays `4e746d1f…`. All 80 rows are value-equal to 2.0.2, read via `git_show` at `ae15c74`, and the counts are 21 decided and 59 undecided. This is enforced by the publisher validator and by pytest, and the dry run shows it.
- **Staging.** Stage only by explicit path. Unrelated modified and untracked files (`.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json` and the untracked onboarding/supply-chain/release/test-quality work) stay out of every commit.
- **The red window.** It closes at the publication and record commits. The plan lists which red items close at which commit; the red set may only shrink.
- **Running tests.** The orchestrator runs tests and validators through PowerShell with a fresh `--basetemp` and `-p no:cacheprovider`, recording pytest's own exit code.
- **Approval.** No publication happens on drafting judgment. Every human gate waits for Oscar Mack.

### Claude's Discretion
- Exactly how the fresh clone for D-03 is made (e.g. `git clone --no-local <repo> <scratch>` then `git checkout <pub-sha>`), provided it is a full, non-shallow clone with no later commit checked out and uses the repo's normal line-ending settings.
- How plan tasks are split around the human checkpoints.
- The wording of verification-step commands and evidence tables.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope
- `.planning/ROADMAP.md`: the Phase 13 goal and success criteria (SC3 is reworded by D-01).
- `.planning/REQUIREMENTS.md`: PUB-10, PUB-11, PUB-12, and PIN-01 (demonstrated here).
- `.planning/PROJECT.md`: constraints (authority, dual role, working tree) and the Phase 12 validated entry.
- `.planning/STATE.md`: the push token workaround, CI run history and environment notes.

### Prior decisions
- `.planning/phases/12-verify-at-pin-and-gate-hardening/12-CONTEXT.md`:
  - D-01..D-04: at-pin mode and its output;
  - D-05: `publication_paths()`;
  - D-06..D-08: plain-mode identity and the digest rules;
  - D-16: the red ledger.
- `.planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md`: the accepted red set at the end of Phase 12, and the notes for Phase 13 (at-pin replaces pre-publication; 11 pinned paths).
- `.planning/phases/12-verify-at-pin-and-gate-hardening/12-08-SUMMARY.md`: what at-pin now checks (HEAD blobs, index flags, hardened status over the 11 paths plus OUT) and the deferred WR-03.
- `.planning/phases/12-verify-at-pin-and-gate-hardening/12-REVIEW.md`: the WR-03 description.
- `.planning/phases/12-verify-at-pin-and-gate-hardening/12-SECURITY.md`: AR-03 (WR-02 deferred).
- `.planning/phases/09-certified-republication-2-0-2/09-CONTEXT.md`: the 2.0.2 sequence and these decisions:
  - D-04: CI at the record commit;
  - D-05: the push and CI checkpoint;
  - D-06: where evidence is recorded;
  - D-09/D-10: the sign-off summary.
- `.planning/phases/09-certified-republication-2-0-2/09-VERIFICATION.md`: what the 2.0.2 evidence looked like.
- `.planning/phases/06-address-tech-debt-publication-gate-hardening-2-0-1/06-CONTEXT.md`: D-07 overwrite in place; D-10 published-on; D-12/D-13 proof that no decision changed; D-21/D-22 process and hygiene.
- `.planning/phases/04-certified-publication/04-CONTEXT.md`: D-19 sign-off; D-20 publication commit contents; D-21 publication record.

### Code
- `scripts/publish_archive_assessment_applicability_authority_v2.py`:
  - `VERSION` L34 and `SUPERSEDED_V2_0_2` L36;
  - `check_tree_matches_head` L431;
  - `publication_paths()` L596;
  - `validate_signoff` L607;
  - `dry_run_summary` L632 ("What changed" L652-655);
  - `publish` L780;
  - `validate_published` L792;
  - `check_publication_record` L830;
  - `write_publication_record` L859;
  - `main` and the CLI L866.
- `registry/archive_assessment_applicability_authority_v2_signoff.json`: the 2.0.2 sign-off, the source of the D-06 wording.
- `registry/archive_assessment_applicability_authority_v2_publication_record.json`: the 2.0.2 record, written at `a71257e`.
- `.github/workflows/ems-validate.yml`: the `archive-assessment` job (pytest over `tests/test_archive_assessment_*.py` plus six validators, `fetch-depth: 0`, `EMS_FAIL_ON_SKIP=1`).
- `tests/test_archive_assessment_lineage_validation.py` L357: the D-10 subprocess test that D-07 strengthens.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `publication_paths()` is the single list of the 10 files, used for staging, the D-02 `git show --stat` check and the at-pin check.
- The `--publish --dry-run` output is the sign-off artefact. `--validate --at-pin` prints the D-03 JSON. `--record-publication <sha>` writes the record.
- The scratchpad `check.ps1` pattern (full suite plus six validators) is reused for each red-set checkpoint.

### Established Patterns
- **The red set.** Exactly 3 tests plus validator 1 before publication. At the publication commit, `test_committed_schema_equals_schema_function` and the real-file tests should turn green as their files change. Validator 1 and the publication-record checks turn green only at the record commit. The plan must state the expected red set at each commit.
- **At-pin requirements.** At-pin needs a clean state for the 11 pinned paths and the OUT folder: no extras, no index flags, and files equal to the HEAD blobs after LF normalisation. The real repo is clean today; this was verified after 12-08.
- **Line endings.** The publisher is CRLF. `core.autocrlf=true` is set system-wide and in `.git/config`. Generated files are force-added under the gitignored `generated/`.

### Integration Points
- After the record commit, the full archive suite and all six validators must pass at the same SHA, and again at the WR-03 commit.
- Many local commits are not yet on origin. The D-08 push publishes the whole milestone branch.
- Phase 14's notice cites the 2.0.3 publication SHA and the at-pin and plain commands. The D-04 evidence feeds it.

</code_context>

<specifics>
## Specific Ideas

- Hayes pins the publication commit. The fresh-clone at-pin run (D-03) is the exact check Hayes will repeat, so its output is the strongest evidence for PIN-01.
- The CI head is the record commit plus 1 (the WR-03 commit). Plain `--validate` there proves the publication files are unchanged, so the run still certifies the pinned bytes.

</specifics>

<deferred>
## Deferred Ideas

- WR-02 (scrubbing ambient `GIT_*` env vars and replace refs in `git_run`): deferred, recorded as 12-SECURITY AR-03.
- 12-REVIEW IN-01..IN-04, IN-06, IN-07 and 11-REVIEW IN-01..IN-07: advisory polish, deferred until after the milestone.
- `.gitattributes eol=lf` (12 D-15): still deferred.
- V2-01 and V2-02: still deferred per PROJECT.md.

</deferred>

---

*Phase: 13-certified-republication-2-0-3*
*Context gathered: 2026-11-17*
