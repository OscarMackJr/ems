# Phase 13: Certified Republication 2.0.3 - Research

**Researched:** 2026-11-17
**Domain:** Hash-certified republication of the EMS-AA3 v2 authority (publisher CLI, git staging, at-pin proof, CI dispatch)
**Confidence:** HIGH (every claim is from the code at HEAD aa7249e, git, or a read-only probe run in this session)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**CI evidence (PUB-12, SC3)**
- **D-01: Where the green CI run comes from.** Hayes pins the publication commit. At that commit the publication record still names 2.0.2, so plain `--validate` (CI validator 1) is red there by design and points the operator to `--validate --at-pin`. The green CI run is therefore taken at the branch head after the record commit. Per D-07 that head is the WR-03 test commit, a descendant of the record commit.
  - Plain `--validate` at that head itself proves that the publication commit is an ancestor and that the 10 `publication_paths()` files are byte-identical between the publication commit and HEAD (12 D-06, with the 12-08 working-tree binding). The green run therefore certifies the pinned bytes.
  - The plan states this rewording of ROADMAP SC3 explicitly, as Phase 9 D-04 did.
  - No CI change is made, and no at-pin CI mode or auto-detection is added.
- **D-02: Checking the commit contents (PUB-12 "only deliberate changes").** This is a verification-step command, not a pytest:
  - `git show --stat --format= <pub>` must list exactly the 10 `publication_paths()` files.
  - `git show --stat --format= <record>` must list only `registry/archive_assessment_applicability_authority_v2_publication_record.json`.
  - The WR-03 commit must list only the one test file.
  - The output is recorded in `13-VERIFICATION.md`.

**At-pin proof (PIN-01 demonstrated, SC4)**
- **D-03: Run at-pin in two places.**
  1. In the operator working tree, immediately after the publication commit and before writing the record. This is the gate that replaces Phase 9's `--validate --pre-publication`.
  2. In a fresh full clone (not shallow) of the repo, checked out at the publication SHA with no later commit. This is what Hayes does.

  Both must print `{"status":"PASS","mode":"AT_PIN","deferred":["PUBLICATION_RECORD_BINDING"]}` (key order as the publisher emits it) with exit 0. If either fails, stop. Do not write the record. Report the failure.
- **D-04: Where the evidence goes.** The at-pin JSON outputs, the publication SHA, the clone method and the CI run id go in planning docs only: `13-VERIFICATION.md` and STATE.md, as in 09 D-06. The publication record and the schemas keep their shape.

**Sign-off summary and record**
- **D-05: The dry-run text is used as it stands.** The "What changed in 2.0.3" section of the dry-run summary (publisher `dry_run_summary`, L632-656) is used as is: the derived lineage lines; the negative-mutation count; the closed schema levels; the row comparison 2.0.2 → 2.0.3; the fixed "Gates GATE-01 to GATE-10" line. No publisher edit is made before the dry run. Oscar reads the full dry run at the blocking sign-off checkpoint.
- **D-06: The sign-off record.** It reuses the 2.0.2 wording exactly: role `EMS_GOVERNANCE_AUTHORITY`; `dual_role_statement`: "Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it."; the date of approval. At the blocking checkpoint Claude presents the dry run and the proposed sign-off record. The record is written only after Oscar approves. `PUBLISHED_ON` comes from the sign-off date (06 D-10).

**WR-03 and post-publication commits**
- **D-07: The WR-03 test fix.** Once validator 1 is green at the record commit, `test_d10_live_catalog_edit_or_delete_does_not_change_validate_outcome` (`tests/test_archive_assessment_lineage_validation.py` L357) must assert that its baseline is `(0, 'PASS')`, not only that the result is the same before and after. It lands in a separate test-only commit after the record commit and before the push, so the record commit stays record-only. The full archive suite and all six validators must be green at that commit.
- **D-08: Push and CI.** Same as 2.0.2 (09 D-05): after the WR-03 commit there is a blocking checkpoint; nothing is pushed until Oscar Mack gives the go-ahead. On the go-ahead, Claude pushes `feature/ems-aa3-archive-applicability-authority` using the GitHub CLI token workaround recorded in STATE.md (one-command `http.extraheader` via `GIT_CONFIG_*`, credential.helper cleared), dispatches the `archive-assessment` workflow on the branch (`gh workflow run`), waits for it to finish, and confirms it passed at the head SHA. No PR, merge or tag in this phase.

**Carried forward (not re-asked)**
- Publish sequence (09 carried-forward and 06 D-21, at-pin in place of pre-publication):
  1. The tree is clean and the D-16 red set is confirmed.
  2. `--publish --dry-run`, then the blocking sign-off checkpoint.
  3. Write the sign-off record (D-06), then `--emit-schema` and `--publish`.
  4. The publication commit, staging exactly the 10 publication files by explicit path.
  5. `--validate --at-pin`, in the tree and in a fresh clone (D-03).
  6. `--record-publication <sha>`, then the record commit.
  7. Plain `--validate` PASS, all six CI validators PASS, and the full archive-assessment pytest suite green with `EMS_FAIL_ON_SKIP=1`. This closes the red window.
  8. The WR-03 commit (D-07), then the push and CI checkpoint (D-08).
- Committed schema is re-emitted (`--emit-schema`) as part of the publication; closes `test_committed_schema_equals_schema_function`.
- File handling: v2 files overwritten in place (06 D-07); no publication history file.
- Publication commit holds only the 10 D-05 files: v2 registry authority, regenerated schema, sign-off, 7 `ems-aa3-v2/` outputs (manifest included).
- No decision change (PUB-11): decisions digest stays `4e746d1f…`; all 80 rows value-equal to 2.0.2 via `git_show` at `ae15c74`; 21 decided / 59 undecided; enforced by publisher validator and pytest; shown by the dry run.
- Staging: explicit path only. Unrelated modified/untracked files (`.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json`, untracked onboarding/supply-chain/release/test-quality work) stay out of every commit.
- Red window closes at the publication and record commits. The plan lists which red items close at which commit; the red set may only shrink.
- Tests run by the orchestrator through PowerShell with a fresh `--basetemp` and `-p no:cacheprovider`, recording pytest's own exit code.
- No publication on drafting judgment. Every human gate waits for Oscar Mack.

### Claude's Discretion
- Exactly how the fresh clone for D-03 is made (e.g. `git clone --no-local <repo> <scratch>` then `git checkout <pub-sha>`), provided it is a full, non-shallow clone with no later commit checked out and uses the repo's normal line-ending settings.
- How plan tasks are split around the human checkpoints.
- The wording of verification-step commands and evidence tables.

### Deferred Ideas (OUT OF SCOPE)
- WR-02 (scrubbing ambient `GIT_*` env vars and replace refs in `git_run`): deferred, 12-SECURITY AR-03.
- 12-REVIEW IN-01..IN-04, IN-06, IN-07 and 11-REVIEW IN-01..IN-07: advisory polish, deferred.
- `.gitattributes eol=lf` (12 D-15): still deferred.
- V2-01 and V2-02: still deferred per PROJECT.md.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PUB-10 | 2.0.3 published with certification, manifest and traceability | `--publish` writes the authority + 7 outputs incl. cert, manifest, traceability (publisher L780-790, `build_all_outputs` L658); schema via separate `--emit-schema` (L870). Sequence in "Command Sequence". |
| PUB-11 | No decision change: digest `4e746d1f…`, 80 rows identical to 2.0.2, 21/59 | `validate_publication` enforces digest equality with `SUPERSEDED_V2_0_2` and the 80-row comparison at `ae15c74`; today's dry run already prints "No decision changed … 4e746d1f… equals the 2.0.2 value" and "80 controls identical to 2.0.2", 21/59 (probe output below). |
| PUB-12 | Publication commit holds only deliberate changes; CI `archive-assessment` passes | Explicit-path staging (`git add --` 3 paths, `git add -f --` 7 generated paths); `git show --stat=300 --format=` / `git diff-tree --name-only` check vs `publication_paths()`; D-01 CI at WR-03 head. |
| PIN-01 (demonstrated) | `--validate --at-pin` PASS on a clean checkout of the pub commit | Probe in this session: fresh `--no-local` Windows clone with system `core.autocrlf=true` passes all at-pin git preconditions and lineage recompute (see "At-pin preconditions"). |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- Oscar Mack is the approving authority; nothing is published on drafting judgment. Dual role must be written into the record (sign-off `dual_role_statement`).
- Follow the existing authority pattern (schema, publisher, certification, traceability, pytest); hash-based certification breaks on uncoordinated hand edits — only the publisher writes the authority/outputs/schema; the sign-off is the one hand-written file and must be written before `--publish`.
- Scope: the 21 controls only; the other 59 stay NOT_YET_DECIDED.
- Working tree: unrelated uncommitted work stays untouched and out of this project's commits; the commit Hayes re-pins to contains only deliberate changes.
- Tech: Python 3.12, `jsonschema`, PyYAML, pytest; Windows-primary. Deterministic JSON `json.dumps(indent=2, sort_keys=True)+'\n'`; repo-relative forward-slash paths.
- GSD workflow enforcement: edits only inside `/gsd-execute-phase`.
- Memory note: Bash may be flaky; run pytest from the orchestrator (PowerShell) with `--basetemp <scratchpad>\<fresh>`; push may need the token workaround or one retry.

## Summary

No code is written in this phase except one test assertion (WR-03). Everything else is running the frozen 2.0.3 publisher in a precise order, around two human gates (sign-off and push). The research below pins down each command, what it writes, what it prints, and exactly which tests are red at each commit.

A read-only `--publish --dry-run` was run at HEAD aa7249e (it wrote nothing; `git status` unchanged). It printed 21 decided / 59 undecided, the 3 rules (CTRL-030 production=KNOWN_FALSE, CTRL-039 production=KNOWN_FALSE, CTRL-052 ai_enabled=KNOWN_FALSE), **Authority LF sha256 `696116e765111c6f15237d876a9aca27f830c756707ee9c4b5e251d03aa0e0a6`**, "No decision changed … 4e746d1f… equals the 2.0.2 value", 29 negative mutations, 16 closed schema levels, and "80 controls identical to 2.0.2". A fresh full clone was also made in the scratchpad (since deleted), and the at-pin git preconditions and the lineage recompute both passed there under Windows `core.autocrlf=true`. The same authority digest was rebuilt in the clone.

**Two findings change the plan relative to the CONTEXT assumptions:**
1. **The red set does not only shrink at the publication commit.** Three tests that are green today go red at the working-tree publish and stay red at the publication commit. They compare the *still-2.0.2* publication record (or the script at the record's `publication_commit`, ae15c74) against the *new* live files. All three close at the record commit. The plan must list them as expected transient reds at the publication commit. Otherwise the "may only shrink" rule will appear violated.
2. **The at-pin output is not literally `{"status":"PASS","mode":"AT_PIN","deferred":["PUBLICATION_RECORD_BINDING"]}`.** The publisher prints `json.dumps` with default separators and the full deferred sentence (L825, L828). Acceptance checks must parse the JSON and test `status == 'PASS'`, `mode == 'AT_PIN'`, `len(deferred) == 1` and `deferred[0].startswith('PUBLICATION_RECORD_BINDING: ')`. A string compare would fail.

**Primary recommendation:** Run: dry run → checkpoint → write sign-off (LF) → `--validate-signoff` → `--emit-schema` → `--publish` → stage 3 paths with `git add --` and 7 with `git add -f --` → commit → in-tree at-pin → fresh-clone at-pin → `--record-publication $(git rev-parse HEAD)` → record-only commit → full suite + 6 validators → WR-03 one-line test commit → full suite + 6 validators → push checkpoint → push → `gh workflow run` → watch → verify.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Build/validate authority and outputs | Publisher CLI (`scripts/publish_…_v2.py`) | — | Only the generator writes hashed files |
| Sign-off record | Human authority (Oscar Mack) → hand-written registry JSON | Publisher `validate_signoff` | Human gate; validated, never generated |
| Commit scope | git (operator, explicit-path staging) | `git show/diff-tree` checks | PUB-12 |
| At-pin proof | Publisher `--validate --at-pin` in tree and fresh clone | git (`cat-file`, `ls-files -v`, `status`) | PIN-01 / D-03 |
| Record binding | Publisher `--record-publication` + plain `--validate` | git ancestry | Self-reference forces a later commit |
| CI evidence | GitHub Actions `archive-assessment` (workflow_dispatch) | `gh` CLI | D-01/D-08 |

## Standard Stack

No new packages. Existing: Python 3.12.10 (`.venv`), `jsonschema`, PyYAML, pytest, git 2.54.0.windows.1, gh 2.91.0 [VERIFIED: local `--version` probes].

## Package Legitimacy Audit

Not applicable. This phase installs no external packages. slopcheck was not run because no packages are recommended.

## Command Sequence and CLI Semantics (Question 1)

CLI dispatch (`main`, L866-875) is a single `if/elif` chain in this precedence: `--validate` → `--emit-schema` → `--validate-signoff` → `--publish` → `--record-publication`. Only **one** action runs per invocation. [VERIFIED: publisher L866-875]

| Question | Answer | Evidence |
|----------|--------|----------|
| Does `--publish` write the schema? | **No.** `publish()` writes only `AUTHORITY` and the 7 files in `OUT` (L788-789). The schema is written only by `--emit-schema` (`dump(SCHEMA, schema())`, L870). | L780-790, L870 |
| Must `--emit-schema` precede `--publish`? | **Yes.** `build_all_outputs` digests the schema **file on disk** (`ssh = lf_digest(SCHEMA)`, L662) into the certification and manifest. If the schema is emitted after publishing, the manifest and certification carry the old schema digest and `--validate` fails. | L662 |
| `--emit-schema` together with `--publish`? | No. `elif` means only `--emit-schema` would run. Use two invocations. | L870-873 |
| Does `--dry-run` combine with `--publish`? | **Yes, and only with it.** `--publish --dry-run` → `publish(True)` prints `dry_run_summary` and returns before any write (L782-784). `--dry-run` alone hits `parser.error` (L875). With `--validate`, `--dry-run` is silently ignored. | L783-784, L873 |
| Is the dry run read-only? | **Yes.** It was run this session: exit 0, and `git status` was identical before and after. It needs no sign-off file. | probe |
| How does `--record-publication` take the SHA? | As the flag's value: `--record-publication <40-hex>`. It must be a full lowercase 40-hex SHA or it raises `AuthorityError` (L860). It does **not** check that the SHA is HEAD or that the files match, so pass `(git rev-parse HEAD)` immediately after the publication commit. It reads the live authority and manifest LF digests and writes the record with `dump` (LF, sorted keys). | L859-864 |
| `--at-pin` without `--validate`? | `parser.error('--at-pin requires --validate')` | L868 |

**What each command prints on success** [VERIFIED: code + dry-run probe]:

| Command | stdout on success | Writes |
|---------|-------------------|--------|
| `--publish --dry-run` | Multi-line summary starting `Publication sign-off summary for EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3` | nothing |
| `--validate-signoff` | `PASS` | nothing |
| `--emit-schema` | nothing (silent, exit 0) | `schemas/archive_assessment_applicability_authority_v2.schema.json` (LF) |
| `--publish` | `{"status": "PASS", "authority_sha256": "<64hex>", "manifest_sha256": "<64hex>"}` | authority + 7 outputs (LF, `newline='\n'`) |
| `--validate --at-pin` | `{"status": "PASS", "mode": "AT_PIN", "deferred": ["PUBLICATION_RECORD_BINDING: the publication record naming this commit is written in the next commit; run plain --validate at the record commit or any later commit to check it"]}` | nothing |
| `--record-publication <sha>` | nothing (silent, exit 0) | `registry/…_v2_publication_record.json` |
| `--validate` (plain) | `PASS` | nothing |

Failure in every mode is an uncaught `AuthorityError` traceback with exit 1.

### Recommended exact sequence (PowerShell, repo root; `$py = '.venv\Scripts\python.exe'`; `$P = 'scripts/publish_archive_assessment_applicability_authority_v2.py'`)

```powershell
# 0. Preflight (read-only)
git diff --cached --name-only                    # must be empty
git status --porcelain --untracked-files=all --ignored=matching -- <10 publication_paths> scripts/publish_archive_assessment_applicability_authority_v2.py generated/archive-assessment/ems-aa3-v2 registry/archive_assessment_applicability_authority_v2_publication_record.json   # must be empty (verified empty today)
# full suite + 6 validators: expect the D-16 set (3 tests + V1)

# 1. Dry run -> BLOCKING sign-off checkpoint (present full output + proposed sign-off JSON)
& $py $P --publish --dry-run

# 2. After "approve": write sign-off with the Write tool (LF), then
& $py $P --validate-signoff                      # PASS
& $py $P --publish --dry-run                     # re-run; Authority LF sha256 must equal the signed value
& $py $P --emit-schema                           # silent
& $py $P --publish                               # {"status": "PASS", ...}
& $py $P --validate-signoff                      # PASS again

# 3. Stage exactly 10 paths and commit
git add -- registry/archive_assessment_applicability_authority_v2.json schemas/archive_assessment_applicability_authority_v2.schema.json registry/archive_assessment_applicability_authority_v2_signoff.json
git add -f -- generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_matrix.json generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_semantic_validation.json generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_negative_invariant_validation.json generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_decision_traceability.json generated/archive-assessment/ems-aa3-v2/EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION.json generated/archive-assessment/ems-aa3-v2/EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION.md generated/archive-assessment/ems-aa3-v2/ems_aa3_v2_archive_applicability_authority_publication_manifest.json
git diff --cached --name-only                    # exactly the 10, nothing else
git commit -m "feat(13-xx): publish EMS-AA3 archive applicability authority 2.0.3" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
$PUB = git rev-parse HEAD

# 4. At-pin in the operator tree (before ANY other change, record untouched)
& $py $P --validate --at-pin                     # JSON PASS, exit 0
# 5. At-pin in a fresh clone (recipe below)

# 6. Record
& $py $P --record-publication $PUB               # silent
git add -- registry/archive_assessment_applicability_authority_v2_publication_record.json
git commit -m "feat(13-xx): record 2.0.3 publication commit" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
& $py $P --validate                              # PASS
# full suite + 6 validators: all green

# 7. WR-03 commit (tests/test_archive_assessment_lineage_validation.py only), suite + validators green
# 8. Push checkpoint -> push -> dispatch -> watch
```

## Red-Set Transitions (Question 2)

Labels: **A** `test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function`; **B** `…_v2_publication.py::test_real_published_files_validate`; **C** `…_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`; **V1** CI validator 1 (plain `--validate`).

| Item | Green at | Why |
|------|----------|-----|
| A | **Working-tree `--emit-schema`** (so green at the publication commit) | The test compares the schema file on disk with `schema()` (test L212). Only `--emit-schema` changes that file. |
| B | **Record commit only** (in practice: once `--record-publication` has written the record) | It calls plain `validate_published()` (test L968). After `--publish`, every earlier gate passes. GATE-06 passes because the new manifest records the live script digest (L814). It then fails in `check_publication_record` (L841): "publication record still names the superseded 2.0.2 publication, so HEAD is the publication commit, not the record commit; run --validate --at-pin here…". |
| C | **Record commit only** | Same `validate_published()` call (test L981), same L841 failure. |
| V1 | **Record commit only** | Before publish it fails with "authority identity/version/status invalid; source_lineage supersedes does not name the 2.0.2 publication". After `--publish`, and at the publication commit, **the message changes** to the L841 message. It stays red until the record names 2.0.3. |

**Newly red at the working-tree publish and at the publication commit, closing at the record commit** [VERIFIED: test source; reasoning from code, not yet executed]:

| Test | Reason |
|------|--------|
| `tests/test_archive_assessment_normalisation_claims.py::test_publication_record_normalisation_claim` (L41) | Asserts `record.authority_sha256 == lf_digest(AUTHORITY)` and `record.manifest_sha256 == lf_digest(MANIFEST)`. The record still holds the 2.0.2 digests (`a44eea1f…`, `9991228a…`), but the live files are 2.0.3. |
| `tests/test_archive_assessment_normalisation_claims.py::test_manifest_publisher_script_normalisation_claim` (L65) | Compares the live manifest `publisher_script.sha256`, which is now the current script, with the script at `record.publication_commit`, which is still ae15c74 (the 2.0.2 script, `f6b51cca…`). |
| `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_manifest_publisher_script_digest_matches_publication_commit` (L1015) | Same comparison as the row above. |

So the expected red set **at the publication commit** is: B, C, V1 (new message), plus these 3. A is green. The total is 5 tests + V1. The plan's ledger must state this explicitly as a planned, record-bound transient. All of them close at the record commit.

**Transient red only between `--record-publication` and the record commit (do not run the suite there):** `…_v2_publication.py::test_publication_files_byte_identical_between_publication_and_record_commit` (L1442). It finds the record commit with `git log -n1 -- <record>`, which is still a71257e until the commit. It then diffs the new pub against a71257e and fails. It is green at the record commit. At that point it also enforces that the record commit touches only the record file, and that anything between pub and record is `.planning/` only.

**Green at the record commit, but with new strict preconditions:**
- `test_publication_paths_match_the_publication_commit_file_list` (L1699) requires the publication commit to touch **exactly** the 10 `publication_paths()`. Every file will differ from 2.0.2, because version and `published_on` change. The semantic-validation and traceability outputs differ from 2.0.2 **only** by `published_on`. A sign-off date of `2026-11-12`, the 2.0.2 date, would leave them byte-identical, they would drop out of the commit, and this test would go red. Any date from 2026-11-17 on is safe.
- `test_d10_live_catalog_edit_or_delete_does_not_change_validate_outcome` stays green at every step. It compares the before and after outcomes of a `git clone --shared` of committed HEAD. At the record commit its baseline becomes `(0, 'PASS')`. That is the precondition for WR-03.

**Frozen validators 5 and 6 (reply, notice 2.0.2)** resolve fixed commits and need them to be ancestors of HEAD (notice builder L150-164). They are unaffected by new commits. Re-run them at every checkpoint anyway.

## Sign-off Record (Question 3)

`validate_signoff` (L607-627) requires [VERIFIED: code]:
- Top-level keys exactly `{status, approval, dual_role_statement, authority_id, version, authority_sha256, authority_sha256_normalisation}`.
- `approval` keys exactly `{approver, role, date, scope}`.
- `status == "PUBLICATION_SIGNOFF"`; `approver == "Oscar Mack"`; `role == "EMS_GOVERNANCE_AUTHORITY"`; `date` is a real ISO `YYYY-MM-DD` (`is_date`, L601); `scope` is a non-empty string (its content is not checked).
- `dual_role_statement ==` the `DUAL_ROLE_STATEMENT` constant (L527), byte-for-byte.
- `authority_id == "EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3"`, `version == "2.0.3"`.
- `authority_sha256 ==` the LF digest of the freshly rebuilt authority (`publish` passes `ash`, L786). `authority_sha256_normalisation == "CRLF_TO_LF"`.

Proposed 2.0.3 record. The keys are shown sorted, as in the 2.0.2 file. The digest is from today's dry run and must be re-confirmed by a dry run just before writing. `<DATE>` is the date Oscar gives.

```json
{
  "approval": {
    "approver": "Oscar Mack",
    "date": "<DATE>",
    "role": "EMS_GOVERNANCE_AUTHORITY",
    "scope": "Publication of EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3 version 2.0.3 (authority LF sha256 696116e765111c6f15237d876a9aca27f830c756707ee9c4b5e251d03aa0e0a6), superseding 2.0.2 at ae15c74 with no decision changed."
  },
  "authority_id": "EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3",
  "authority_sha256": "696116e765111c6f15237d876a9aca27f830c756707ee9c4b5e251d03aa0e0a6",
  "authority_sha256_normalisation": "CRLF_TO_LF",
  "dual_role_statement": "Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it.",
  "status": "PUBLICATION_SIGNOFF",
  "version": "2.0.3"
}
```

The scope wording mirrors the 2.0.2 file at HEAD. Write it with 2-space indent, sorted keys, LF line endings and a trailing newline.

**PUBLISHED_ON derivation.** `build_all_outputs` sets `published_on = signoff['approval']['date']` (L660). It is copied into the matrix, semantic, negative, traceability, certification, report and manifest. Nothing is computed from the clock (the publisher imports only `date` for `fromisoformat`).

**Stale date or digest:**
- **Stale digest, id or version: refused.** `publish()` calls `validate_signoff(signoff, ash)` before any write (L786). If the old 2.0.2 sign-off is left in place, publish fails with "sign-off authority_id does not match; sign-off version does not match; sign-off authority_sha256 does not match the rebuilt authority", and nothing is written.
- **Stale date: NOT refused.** Only the ISO format is checked. Nothing compares the date with today or with the commit date. The plan must take the date from Oscar's approval message, as Phase 9 did ("Approve, date 2026-11-12"), and must not reuse 2026-11-12. See the transient-red note above about identical outputs.
- **Edits after publish: caught.** The manifest and certification record `lf_digest(SIGNOFF)` (L663). Editing the sign-off after `--publish` makes `--validate` fail.

**Date and timezone.** The operator machine is on UTC-05:00. HEAD's commit time is 2026-11-17 08:18 -0500, and the local and UTC dates are both 2026-11-17 now. After 19:00 local the UTC date rolls over. The sign-off date is a human-supplied value, so use the date Oscar states (his local date) and record it verbatim. Phase 12's completion tool stamped planning docs in UTC. That affects only `.planning` dates, never the sign-off. If the dates differ, note it in 13-VERIFICATION.md.

## At-pin Preconditions in the Operator Tree (Question 4)

What at-pin checks, in order (L792-799, L431-440, L403-409): not shallow → `check_tree_matches_head` over the 10 paths plus the script → hardened `git status --porcelain --untracked-files=all --ignored=matching` over those 11 paths plus `generated/archive-assessment/ems-aa3-v2`, which must be empty → the full domain validation → `check_publication_record(at_pin=True)`. The record must still name 2.0.2 at ae15c74 with authority `a44eea1f…` (L836-839).

**Line endings** [VERIFIED: code + `git ls-files --eol` + `git check-attr`]:
- The publisher writes **LF** for everything: `write_text` and `dump` use `newline='\n'` (L83-85, L597-599).
- `.gitattributes` sets `text eol=lf` on the authority, sign-off, record and schema, and on `generated/archive-assessment/ems-aa3-v2/**`. Today all of them are `i/lf w/lf`.
- The publisher **script** has no attribute: `i/lf w/crlf` (CRLF on disk via `core.autocrlf=true`, set in both the system gitconfig and `.git/config`). Every comparison is LF-normalised (`lf_bytes` in `check_tree_matches_head` L438, `lf_digest` for the manifest script digest), so the CRLF script passes.
- Therefore, right after the commit: `check_tree_matches_head` passes (LF disk equals the LF blob; index tag `H` after a normal `git add`). `git_dirty` reports nothing, because the files are tracked and clean, and the output folder holds exactly the 7 tracked files (verified today: no extras, all 10 index tags `H`).
- The sign-off is hand-written. Write it LF. If CRLF slips in, git normalises it on `add` (`eol=lf`), and both the manifest digest and `check_tree_matches_head` use LF normalisation, so it would still pass. Verify with `git ls-files --eol -- registry/archive_assessment_applicability_authority_v2_signoff.json`, which should show `w/lf`.

**Order constraint:** at-pin reads the **working-tree** record (not one of the pinned paths), so run the in-tree at-pin **before** `--record-publication`. After the record is written, at-pin fails with "at-pin record must name the superseded 2.0.2 publication commit".

**Fresh-clone recipe (D-03 #2), PowerShell.** It was probed this session at HEAD (the probe clone is deleted):

```powershell
$S = "<session scratchpad>\pin13"            # new, empty
git -c core.longpaths=true clone --no-local --no-checkout C:\temp\standars\ems $S
git -C $S -c core.longpaths=true checkout --detach $PUB
git -C $S rev-parse HEAD                      # must equal $PUB
git -C $S rev-parse --is-shallow-repository   # false
git -C $S status --porcelain --untracked-files=all --ignored=matching   # empty
Push-Location $S
& C:\temp\standars\ems\.venv\Scripts\python.exe -I scripts\publish_archive_assessment_applicability_authority_v2.py --validate --at-pin
$LASTEXITCODE                                  # 0
Pop-Location
```

- `--no-local` forces a real object copy and a full, non-shallow history, including the unpushed local commits. `--no-checkout` plus `checkout --detach $PUB` guarantees nothing later is checked out.
- The clone inherits the **system** `core.autocrlf=true` (Git for Windows), which is what a default Windows Hayes checkout sees. `.git/config` from the source repo is not copied. Do not pass `-c core.autocrlf=...`. D-03 says "normal line-ending settings".
- Run the clone's own script path, because `ROOT` comes from `__file__` (L17). Use `-I` so nothing is imported from the cwd.
- **Probe result at HEAD aa7249e in such a clone:** `ls-files --eol` showed the script as `w/crlf`, the authority as `w/lf`, and the AA1 manifest as `-text w/crlf` (RAW_BYTES preserved). `git_not_shallow` and `check_tree_matches_head` (11 paths) passed, and `git_dirty` returned `[]`. `validate_governance_decisions`, `published_authority_checked` and `validate_lineage` passed, and the rebuilt authority digest was `696116e7…`, identical to the operator tree. The CLI `--validate --at-pin` at HEAD failed only at the domain check ("authority identity/version/status invalid…"), which is expected before publication, after every git precondition had passed. The 12 D-15 fresh-clone notice-file issue does not touch the publisher.

## WR-03 Change (Question 5)

Current code (`tests/test_archive_assessment_lineage_validation.py` L357-377): `before = outcome()` at L371, then only `assert after == before` at L376.

Exact change: insert one assertion immediately after L371:

```python
    before = outcome()
    assert before == (0, 'PASS'), f'--validate baseline must be PASS for D-10 to be meaningful: {before!r}'
```

Leave everything else unchanged. No new test id, so the total count stays the same.

What the test needs from the repo state:
- It clones **committed HEAD** with `git clone --shared` and runs plain `--validate` in the clone. The working tree is ignored.
- So `(0, 'PASS')` holds only when HEAD is the record commit or a descendant of it, with the record naming 2.0.3, the pub commit as an ancestor, and the 10 files byte-identical (L849-857).
- `outcome()` returns the last non-empty line of stdout+stderr. Plain PASS prints exactly `PASS` (L825).
- It needs full history (`require_history(..., PINNED_COMMITS)`), and CI has `fetch-depth: 0` (workflow L75).
- Run it in the operator tree with the WR-03 edit uncommitted and HEAD at the record commit. It passes, because the clone is of the record commit. In CI it clones the WR-03 commit, a descendant, which also passes.
- If it were committed before the record commit, it would go red. That is why D-07 orders it after the record commit.

## PUB-12 Verification Commands (Question 6)

**Pitfall:** the default `git show --stat` truncates long paths to `...` at 80 columns. This was verified on ae15c74, where every generated path appeared as `..._ARCHIVE_…`. Use `--stat=300`, or a name-only form, for a path-exact comparison.

```powershell
git show --stat=300 --format= $PUB      # 10 lines + "10 files changed, ..."
git diff-tree --no-commit-id --name-only -r $PUB | Sort-Object
& $py -I -c "import importlib.util as u;s=u.spec_from_file_location('p','scripts/publish_archive_assessment_applicability_authority_v2.py');m=u.module_from_spec(s);s.loader.exec_module(m);print('\n'.join(sorted(m.publication_paths())))"
# the two sorted lists must be identical (10 entries)

git show --stat=300 --format= $REC      # exactly: registry/archive_assessment_applicability_authority_v2_publication_record.json (1 file changed)
git diff-tree --no-commit-id --name-only -r $REC   # exactly that one path

git show --stat=300 --format= $WR03     # exactly: tests/test_archive_assessment_lineage_validation.py | 1 + (1 file changed)
git diff-tree --no-commit-id --name-only -r $WR03

git diff --name-only $PUB~1 $PUB -- scripts tests   # empty (no code in the publication commit)
git diff --quiet $PUB HEAD -- <10 paths>; $LASTEXITCODE   # 0 at the CI head
```

Expected 2.0.2 precedent format, from `git show --stat=300 --format= ae15c74`: 10 lines, 7 under `generated/archive-assessment/ems-aa3-v2/`, then the authority, sign-off and schema, then `10 files changed`. Record the outputs verbatim in 13-VERIFICATION.md (D-02).

PUB-11 independent check, as 09-VERIFICATION did: recompute the LF sha of `registry/archive_assessment_governance_decisions.json` at `$PUB` (it must be `4e746d1f…`). Then compare all 80 rows of the authority at `$PUB` with those at ae15c74 on every field (expect 0 differing), and count 3 RULE_PUBLISHED, 18 NO_RULE_WILL_BE_PUBLISHED and 59 NOT_YET_DECIDED. Use `git show <sha>:<path>` plus `python -I`.

## Push and CI Procedure (Question 7). Do not run until the D-08 go-ahead

The workflow `.github/workflows/ems-validate.yml` triggers on `pull_request`, `push` to `main`, and `workflow_dispatch` (L3-8). A branch push alone does **not** run it, so dispatch is required. The `archive-assessment` job (L70-100) runs pytest over `tests/test_archive_assessment_*.py` with `EMS_FAIL_ON_SKIP=1`, then the six validators. The `validate` job runs as well.

The branch is 74 commits ahead of `origin/feature/ems-aa3-archive-applicability-authority` (origin tip `49c7b08`). The push publishes all of Phases 11-13. [VERIFIED: `git rev-list --count`]

```powershell
# 1. Try the normal push first (it worked in Phase 9; 09-05-SUMMARY)
$HEADSHA = git rev-parse HEAD
git push origin feature/ems-aa3-archive-applicability-authority

# 2. Only if that fails (credential helper / sh.exe crash): STATE.md workaround, scoped to one process.
#    The token is read into a variable, never echoed, logged or written to disk.
$b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("x-access-token:" + (gh auth token)))
$env:GIT_CONFIG_COUNT = '2'
$env:GIT_CONFIG_KEY_0 = 'credential.helper'; $env:GIT_CONFIG_VALUE_0 = ''
$env:GIT_CONFIG_KEY_1 = 'http.https://github.com/.extraheader'; $env:GIT_CONFIG_VALUE_1 = "AUTHORIZATION: basic $b64"
try { git push origin feature/ems-aa3-archive-applicability-authority }
finally { Remove-Item Env:GIT_CONFIG_COUNT,Env:GIT_CONFIG_KEY_0,Env:GIT_CONFIG_VALUE_0,Env:GIT_CONFIG_KEY_1,Env:GIT_CONFIG_VALUE_1 -ErrorAction SilentlyContinue; Remove-Variable b64 }

# 3. Dispatch and watch (Phase 9 commands, 09-05-PLAN L94/L97)
gh workflow run ems-validate.yml --ref feature/ems-aa3-archive-applicability-authority
gh run list --workflow=ems-validate.yml --branch feature/ems-aa3-archive-applicability-authority -L 1 --json databaseId,headSha,status,conclusion
gh run watch <databaseId> --exit-status
gh run view <databaseId> --json conclusion,headSha,jobs

# 4. Confirm: conclusion success; jobs validate + archive-assessment success; headSha == $HEADSHA (the WR-03 commit);
#    git merge-base --is-ancestor $REC $HEADSHA -> 0;  git diff --quiet $PUB $HEADSHA -- <10 paths> -> 0
#    gh pr list --head feature/ems-aa3-archive-applicability-authority -> empty; no new tag
```

`gh run list` right after dispatch can return the previous run, because the run takes a few seconds to register. Re-list until `headSha` equals `$HEADSHA` and `status` is `queued` or `in_progress`. Then watch. Remove the `GIT_CONFIG_*` variables before running any validator. The publisher's `git_run` inherits ambient `GIT_*` env (WR-02 / AR-03), so they must not linger in the session.

## Common Pitfalls (Question 8)

### Pitfall 1: Unrelated working-tree files leak into a commit
**What goes wrong:** `registry/adjudication_rules.json`, `registry/policy_decisions.json`, `.planning/config.json`, about 60 untracked files and `.pytest-*` dirs end up staged.
**Avoid:** Use `git add --`/`git add -f --` with explicit paths only. Never use `-A`, `.`, or `commit -a`. The index is empty today; confirm with `git diff --cached --name-only` before each commit. `.planning/config.json` is modified, so never stage `.planning` with a directory pathspec.

### Pitfall 2: `generated/` is gitignored
**What goes wrong:** `git add -- generated/...` refuses with "paths are ignored … Use -f". This was verified with `git add --dry-run` today, even though the 7 files are tracked.
**Avoid:** Use `git add -f --` for exactly the 7 output paths (the 04-06 and 06-06 precedent). Then confirm 10 entries in `git diff --cached --name-only`.

### Pitfall 3: Emitting the schema after publishing
**What goes wrong:** The certification and manifest carry the old schema digest (L662). `--validate` and `test_certification_normalisation_claim` fail.
**Avoid:** Run `--emit-schema` before `--publish`, and re-run neither afterwards.

### Pitfall 4: Editing anything after the dry run or publish
**What goes wrong:** A stale sign-off digest, a stale manifest script digest (GATE-06, L814) or a stale sign-off digest in the manifest.
**Avoid:** Make no edit to `scripts/`, decisions, v1 authority, schema or sign-off after the dry run. Re-run the dry run just before `--publish` and compare the digest.

### Pitfall 5: The at-pin output string compare
**What goes wrong:** D-03 shows an abbreviated JSON. The real output has spaces and a long deferred sentence (L825/L828).
**Avoid:** Parse it with `ConvertFrom-Json` and assert the fields, as `test_real_git_repo_at_pin_passes_and_dirty_fails` does (`deferred[0].startswith('PUBLICATION_RECORD_BINDING: ')`, test L549).

### Pitfall 6: `.planning` commits between pub and record
Tests allow `.planning/`-only commits between them (L1442 test), and Phase 9 had one (06eb7aa). Committing planning docs **in** the pub or record commit breaks D-02 and the file-set tests. Keep SUMMARY and STATE commits separate, staged by explicit path.

### Pitfall 7: Running the suite at the wrong moment
Between `--record-publication` and the record commit, the L1442 test is transiently red. Between writing the sign-off and `--publish`, `test_signoff_authority_normalisation_claim` is transiently red. Measure only at committed states: before the dry run, at the publication commit, at the record commit and at the WR-03 commit.

### Pitfall 8: Short or wrong SHA to `--record-publication`
It accepts any 40-hex SHA (L860). Pass `git rev-parse HEAD` captured immediately after the publication commit. Plain `--validate` would then catch a wrong one through the git_show digest checks (L847-848).

### Pitfall 9: PowerShell glob for pytest
PowerShell does not expand `tests/test_archive_assessment_*.py` for native commands. Pass `(Get-ChildItem tests\test_archive_assessment_*.py).FullName`, or `tests -k archive_assessment` as in Phase 9. Always use a fresh `--basetemp <scratchpad>\…`, because the default temp dir raises WinError 5 (memory note). Set `$env:EMS_FAIL_ON_SKIP='1'`.

### Pitfall 10: Sign-off date
The date is not checked against the clock. Use Oscar's stated date, not 2026-11-12 (see the transient-red note), and record any local/UTC difference.

### Pitfall 11: `gh run list` returns the previous run
Re-list until `headSha` matches the pushed HEAD.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Authority, outputs, manifest, certification | Hand edits | `--publish` |
| Schema | Hand edits | `--emit-schema` |
| Publication record | Hand-written JSON | `--record-publication <sha>` |
| At-pin cleanliness check | Ad-hoc `git status` | `--validate --at-pin` (hardened status + HEAD blobs + index flags) |
| No-decision-change proof | Manual diff | `validate_publication` (digest + 80-row comparison) and the dry-run line |

## Runtime State Inventory

Not a rename phase. Relevant runtime state:
- **Remote:** origin branch tip `49c7b08`, 74 local commits not pushed.
- **CI:** `workflow_dispatch` runs. No stored data, OS registrations or secrets change.
- **Secret in use:** the `gh auth token`, held only in process env for one push.

## Environment Availability

| Dependency | Required By | Available | Version |
|------------|------------|-----------|---------|
| Python (.venv) | publisher, pytest | ✓ | 3.12.10 |
| git | staging, at-pin | ✓ | 2.54.0.windows.1 |
| gh CLI | dispatch/watch | ✓ | 2.91.0 |
| Bash tool | read-only probes | ✓ this session (flaky historically) | — |

There are no missing dependencies. Per STATE, the orchestrator runs tests and validators in PowerShell.

## Validation Architecture

Skipped. `workflow.nyquist_validation` is `false` in `.planning/config.json`. The test-and-validator checkpoints are specified under "Red-Set Transitions".

## Security Domain

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session | no | — |
| V4 Access Control | yes (human approval gate) | Blocking checkpoints; `validate_signoff` pins approver, role and dual-role text |
| V5 Input Validation | yes | 40-hex SHA regex (L860), `bad_rel` path checks, schema-first validation |
| V6 Cryptography | yes (integrity only) | stdlib `hashlib` SHA-256, LF-normalised; never hand-rolled |
| V8/V14 Secrets | yes | Token only in single-process env; never echoed or written; CI secret-pattern grep |

| Threat | STRIDE | Mitigation |
|--------|--------|------------|
| Sign-off bypass or forged approval | Spoofing/Repudiation | Blocking checkpoint; sign-off written only after "approve" |
| Commit contamination | Tampering | Explicit-path staging; `diff --cached`, `diff-tree` checks |
| Stale or hand-edited hashes | Tampering | Generator-only writes; `--validate` rebuild equality; GATE-06 |
| Ambient `GIT_*` env during validation | Tampering | Clear `GIT_CONFIG_*` before validators (AR-03 accepted) |
| Token exposure | Info disclosure | Token in process env only, `Remove-Item` in `finally` |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The three normalisation and script-digest tests go red at the publication commit and green at the record commit | Red-Set Transitions | Derived from test source, not executed. If the set differs, the plan's ledger needs updating at the checkpoint, so measure and record it. |
| A2 | `gh workflow run … --ref <branch>` still dispatches on this branch | Push/CI | Low. It worked in Phase 9 (run 43332405316). If refused, stop and ask Oscar, since D-08 forbids a PR. |
| A3 | Plain `git push` works this session; otherwise the env workaround does | Push/CI | Low. Both are documented as working. |

## Open Questions (RESOLVED)

1. **Sign-off date.** Use the date Oscar gives at the checkpoint. The planner should make it part of the resume signal ("approve, date YYYY-MM-DD"). **RESOLVED:** 13-01 uses the resume signal "approve, date YYYY-MM-DD", with the date rule cited from 13-CONTEXT D-06.
2. **Will the ledger accept the transient reds?** The CONTEXT says the red set "may only shrink", but three tests necessarily go red at the publication commit. Recommendation: the plan states them up front as planned, record-bound transients that close at the record commit. This is the same self-reference reasoning as D-01. **RESOLVED:** by the 13-CONTEXT post-research clarification ("The red window"), which lists the three record-bound reds as expected at the publication commit and closing at the record commit.

## Sources

### Primary (HIGH confidence)
- `scripts/publish_archive_assessment_applicability_authority_v2.py` at aa7249e: L17, L34-46, L83-85, L395-440, L527, L596-627, L632-662, L780-875.
- `tests/test_archive_assessment_lineage_validation.py` L357-377.
- `tests/test_archive_assessment_applicability_authority_v2_publication.py` L966-1019, L1442-1455, L1699-1704.
- `tests/test_archive_assessment_normalisation_claims.py` L41-73.
- `tests/test_archive_assessment_applicability_authority_v2.py` L212.
- `.github/workflows/ems-validate.yml` L3-8, L70-100.
- `.gitattributes`, `git ls-files --eol`, `git check-attr`, `git config --show-origin core.autocrlf`.
- Read-only probes this session: `--publish --dry-run` at HEAD; fresh `--no-local` clone with at-pin preconditions and lineage recompute; `git add --dry-run` on the ignored path; `git show --stat` truncation on ae15c74.
- Planning: 13-CONTEXT, 12-BASELINE-RED, 12-08-SUMMARY, 12-REVIEW WR-03, 12-SECURITY AR-03, 09-04/09-05 PLAN and SUMMARY, 09-VERIFICATION, STATE.md, memory note.

## Metadata

**Confidence breakdown:**
- Command semantics: HIGH (code read + dry-run probe)
- Red-set transitions: HIGH for A/B/C/V1; MEDIUM-HIGH for the three new transient reds (derived, not executed)
- At-pin and fresh clone: HIGH (probed in a real clone)
- Push/CI: HIGH (Phase 9 precedent)

**Research date:** 2026-11-17
**Valid until:** the next commit that touches the publisher, tests, `.gitattributes` or the record.
