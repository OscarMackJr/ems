# Phase 9: Certified Republication 2.0.2 - Research

**Researched:** 2026-11-12
**Domain:** Hash-certified authority republication (Python publisher, JSON registry, pytest, GitHub Actions)
**Confidence:** HIGH (everything is from reading the repo code, git history and `gh`; no external libraries involved)

<user_constraints>
## User Constraints (from 09-CONTEXT.md)

### Locked Decisions
- **D-01** The DEMO3 reply (`docs/DEMO3_W1_REQ_001_REPLY.md`, `registry/archive_assessment_demo3_w1_req_001_reply.json`) is a sent 2.0.1 artifact and is frozen; its bytes do not change. `build_archive_assessment_demo3_w1_req_001_reply.py --validate` stops reading the live authority, publication record and sign-off. It rebuilds the reply from the 2.0.1 inputs read with `git_show` at their commits and requires byte equality with the committed reply. Without git history it fails closed (07 D-11, 08 D-09). The Phase 10 notice supersedes the reply for Hayes.
- **D-02** The 2.0.1 anchors are named constants in the reply script (style of `CATALOG_COMMIT`): publication commit `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb`; publication-record commit `4d9b7c1` (use the full SHA). `resolve_record_commit` must no longer derive the record commit from `git log` on the live record path. The GATE-04 shallow-clone check (08 D-11) stays. Tests prove: reply validator still passes after the record and authority change to 2.0.2; tampering with reply bytes or a constant fails it; it fails closed without history.
- **D-03** That change lands in a code commit before the publication commit.
- **D-04** Hayes pins the publication commit. The record still names 2.0.1 at that commit, so plain `--validate` and the reply validator are red there by design. The green CI run is taken on the **publication-record commit**. A test or verification step proves every publication file is byte-identical between the publication commit and the record commit (`git diff --stat <pub>..<record>` limited to publication paths, or digest equality). The plan states this rewording of ROADMAP SC4 explicitly. No gate weakened; no CI auto-detect or pre-publication CI mode.
- **D-05** After the record commit there is a blocking checkpoint. On Oscar Mack's go-ahead Claude pushes `feature/ems-aa3-archive-applicability-authority` with the GitHub CLI token workaround in STATE.md (one-command `http.extraheader` via `GIT_CONFIG_*`, credential.helper cleared), dispatches the `archive-assessment` workflow on the branch (`gh workflow run`), waits, and confirms it passed at the record commit's SHA. Nothing is pushed without the go-ahead. No PR, merge or tag.
- **D-06** CI run id and publication SHA are recorded in planning docs only (`09-VERIFICATION.md`, STATE.md), as run 38744767442 was. The publication record and schemas do not change shape.
- **D-07** `source_lineage.supersedes` names 2.0.1 only. `SUPERSEDED_V2_0_0` is replaced by `SUPERSEDED_V2_0_1`: authority id, version `2.0.1`, commit `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb`, 2.0.1 authority LF sha256 (`7be5eb88…`), 2.0.1 governance-decisions LF sha256 (`4e746d1f…`). Values come from files and git, never typed by hand. Every use follows: validator checks, schema `pinned(...)`, the `supersedes_governance_digest_differs` mutation, the pre-publication branch (L719-721, now checks the 2.0.1 record: commit `31addfa`, authority sha `7be5eb88…`), and the dry-run summary. No separate 2.0.0 anchor entry.
- **D-08** PUB-08 is enforced in the publisher validator and in pytest. Validation reads the 2.0.1 authority with `git_show(31addfa, registry/archive_assessment_applicability_authority_v2.json)`. All 80 rows' decision content value-equal: `not_applicable_decision_state`, `not_applicable_rule`, `not_applicable_authority`, `decision_ids`. Top-level `applicability_decision_ids` also equal. Fails closed without history. Pytest drives a tampered row to failure. The decisions-digest binding to `4e746d1f…` (06 D-12) still holds.
- **D-09** Dry-run/sign-off summary keeps everything in 06 D-21 (21 decided / 59 undecided; each control with AA4 id and state; the 3 rules in full; authority LF digest; supersedes + no-decision-changed line now naming 2.0.1 @ `31addfa`) and adds a short neutral "what changed in 2.0.2" section.
- **D-10** The "what changed" section is derived from the built authority and code where possible: each lineage entry with its declared normalisation (AA1 manifest committed and `RAW_BYTES`); the mutation count (29) and the schema levels with `additionalProperties: false`; the 2.0.1 -> 2.0.2 row-comparison result. One short fixed line names GATE-01..05. Plain wording, no ranking or emphasis.
- **Carried forward:** sequence = code commits, dry-run publish, blocking sign-off checkpoint, sign-off record (role `EMS_GOVERNANCE_AUTHORITY`, date, exact dual-role statement), `--publish`, publication commit, `--validate --pre-publication`, `--record-publication <sha>`, record commit, plain `--validate` PASS + full archive-assessment pytest (closes red window), then D-05 push + CI checkpoint. Overwrite v2 files in place (06 D-07). No publication history file. `PUBLISHED_ON` from the sign-off date (06 D-10). Publication commit holds only: v2 registry authority, `ems-aa3-v2/` outputs, sign-off, regenerated schema. Stage by explicit path only. Orchestrator runs tests/validators via PowerShell with `--basetemp`.

### Claude's Discretion
- Constant/helper names (`SUPERSEDED_V2_0_1`, reply anchor constants), compact single-quote publisher style.
- Whether the D-04 byte-identity check is a pytest or a verification-step command.
- How the pre-publication code commits are split (each stages explicit paths; red set only shrinks or stays as listed).
- Whether the Phase 6 D-13 comparison test against 2.0.0 @ `54a7fd0` is kept alongside the new 2.0.1 comparison (keeping preferred).

### Deferred Ideas (OUT OF SCOPE)
- CI mode validating the publication commit in pre-publication mode; tracked CI-evidence field in the record; a 2.0.0 `decisions_origin` anchor; opening a PR / merge / tag; regenerating the DEMO3 reply for 2.0.2.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PUB-07 | 2.0.2 published with certification, manifest, traceability; lineage supersedes 2.0.1 at `31addfa…` | `VERSION` bump + `SUPERSEDED_V2_0_1`; publisher flow `--emit-schema`, `--publish --dry-run`, sign-off, `--publish`; outputs listed below |
| PUB-08 | No decision changes: digest = `4e746d1f…`, 21/59, per-control decision content identical | Existing digest binding in `validate_publication` (L297/L300) + new `git_show(31addfa)` row comparison (D-08) |
| PUB-09 | Publication commit holds only milestone changes; CI `archive-assessment` passes | Explicit-path staging, `git show --stat` check, D-04 byte-identity, D-05 push + `gh workflow run` |
</phase_requirements>

## Summary

Publication is driven by one script, `scripts/publish_archive_assessment_applicability_authority_v2.py`. It rebuilds the authority deterministically from the frozen v1.0.0 baseline, the catalog at `CATALOG_COMMIT` (via `git_show`), the decisions file and the AA1/AA2 lineage files. It writes every output from the sign-off date, then `--validate` rebuilds all of it and requires byte equality. Because every hash chain (authority -> sign-off -> manifest -> record) is verified by rebuild, a version change cannot be hand-edited: the code constants change first (commits), then the generator rewrites all files at once.

The biggest planning risks are not in the publish flow itself (it worked for 2.0.0 and 2.0.1) but in code changes that must precede it. (1) `VERSION` is still `'2.0.1'` and nothing in the CONTEXT list names the bump; it must be part of the first code commit. (2) `V2.validate_signoff` checks `authority_id`/`version` against the live module constants, so once `VERSION='2.0.2'` the frozen reply path cannot reuse it on the 2.0.1 sign-off unless it is parameterised. (3) The existing test `test_publication_commit_ancestor_and_file_set` asserts every file in the publication commit is in `{authority, signoff, ems-aa3-v2/*}`; the 2.0.2 commit also holds the regenerated schema (changed this milestone), so that expected set must add the schema path. (4) `--publish` does not write the schema; `--emit-schema` must be run first because the manifest digests the schema file.

**Primary recommendation:** Do the code changes in 3 to 4 explicit-path commits (publisher constants + validator + tests; reply freeze + tests; dry-run summary), run `--emit-schema` -> `--publish --dry-run` -> sign-off checkpoint -> sign-off write -> `--publish` -> stage exactly 12 paths (list below) -> `--validate --pre-publication` -> `--record-publication <sha>` -> record-only commit -> plain `--validate` + full `-k archive_assessment` -> push/dispatch checkpoint.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Authority build / validate / publish | Publisher script (`scripts/…_v2.py`) | `registry/`, `schemas/` | Script is the only writer; files are generated artefacts |
| Lineage proof for 2.0.1 | git history (`git_show`) | registry record | 2.0.1 bytes live only in commit `31addfa`; working tree is overwritten |
| Human sign-off gate | `registry/…_v2_signoff.json` + orchestrator checkpoint | `validate_signoff` | Sign-off is data; the gate is a blocking human checkpoint, not code |
| Frozen reply validation | Reply builder script (`--validate`) | git history | Reply is a sent 2.0.1 artefact; inputs come from pinned commits |
| CI evidence | GitHub Actions `archive-assessment` job | planning docs | Run id recorded only in `09-VERIFICATION.md` / STATE.md (D-06) |
| Commit scope control | Orchestrator staging by explicit path | `git show --stat` check | Dirty tree holds unrelated work |

## Standard Stack

Existing, no new packages. [VERIFIED: codebase] Python 3.12, `jsonschema`, `PyYAML`, `pytest`, git, `gh` 2.91.0 (present locally). CI installs `requirements.txt jsonschema pytest`. No package install is proposed, so no Package Legitimacy Audit is needed (**none**).

## Architecture Patterns

### How the publisher works (verified by reading the script)

CLI (`main`, L737): `--validate [--pre-publication]`, `--emit-schema`, `--publish [--dry-run]`, `--validate-signoff`, `--record-publication SHA`. Note `--dry-run` only has effect together with `--publish` (it is passed as `publish(args.dry_run)`); `--dry-run` alone gives a parser error.

- **dry run**: `publish(True)` -> `published_authority_checked()` (validate decisions file, `build_published_authority`, `validate_publication`, jsonschema against `schema()`) -> prints `dry_run_summary(a)` (L533). Writes nothing. The printed "Authority LF sha256" (`sha_text(jtext(a))`) is the value the sign-off must carry.
- **publish**: requires `SIGNOFF` file; `validate_signoff(signoff, ash)`; `build_all_outputs` (runs `semantic_conflicts` and all `NEGATIVE_MUTATIONS`; aborts if any mutation accepted; digests `lf_digest(SCHEMA)` so the schema file must already be regenerated); writes `AUTHORITY` and 7 files under `generated/archive-assessment/ems-aa3-v2/`.
- **validate** (`validate_published`, L684): decisions-file checks; `validate_publication`; schema validation of the committed file; `validate_lineage` (re-reads every lineage source, commit-pinned ones through `git_show`); fresh-build equality; sign-off; every generated file byte-equal to a rebuild; manifest digests; `check_publication_record`.
- **record** (`check_publication_record` L713 / `write_publication_record` L730): six keys exactly `{publication_commit, authority_id, version, authority_sha256, manifest_sha256, digest_normalisation}`. Plain mode requires record id/version = the authority's and digests = the committed files, and re-hashes authority and manifest at `publication_commit` via `git_show`. `--pre-publication` mode requires the record to still be the superseded publication (commit, id, version, authority sha), also git-verified.

### Files a publication writes (all under explicit-path staging)
1. `schemas/archive_assessment_applicability_authority_v2.schema.json` (via `--emit-schema`, before publish)
2. `registry/archive_assessment_applicability_authority_v2.json`
3. `registry/archive_assessment_applicability_authority_v2_signoff.json` (hand/orchestrator-written between dry run and publish)
4-10. `generated/archive-assessment/ems-aa3-v2/`: `archive_assessment_applicability_authority_v2_matrix.json`, `…_semantic_validation.json`, `…_negative_invariant_validation.json`, `…_decision_traceability.json`, `EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION.json`, `EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION.md`, `ems_aa3_v2_archive_applicability_authority_publication_manifest.json`

Every output carries `published_on` (sign-off date), so all of them change in 2.0.2 (in 2.0.1 the traceability file was byte-identical to 2.0.0 and produced no diff; do not rely on that now). Publication record (`…_v2_publication_record.json`) is NOT in the publication commit; it goes in the record commit alone. The publisher script is NOT in the publication commit either: the manifest records `lf_digest(SCRIPT)` at publish time, and `test_manifest_publisher_script_digest_matches_publication_commit` requires that digest to equal the script blob at the publication commit, so the script must be committed, unmodified, before `--publish` runs. [VERIFIED: tests L666]

### How 2.0.1 was published (precedent)
- `31addfa feat(06-06)`: 8 files (authority, sign-off, 6 generated; traceability unchanged so not listed; schema unchanged). Sign-off date 2026-10-14, scope text names version, authority sha, "superseding 2.0.0 with no decision changed".
- `4d9b7c1f41df5fa7575d4653a7d54ff9cf0a192b feat(06-07)`: record file only.
- 2.0.1 record values (source for `SUPERSEDED_V2_0_1`): authority_sha256 `7be5eb8869a8897ee6d55051f9d872fee9a8a35bdbd2ad5093d40e8a1d489e4f` (re-verified now: `git show 31addfa:…v2.json | sha256sum` gives this, no CR in blob), manifest_sha256 `c8a3ca0c…f51b`. Decisions file LF sha256 `4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f` (re-verified from the working-tree file; `.gitattributes` has `eol=lf`).

### Code changes that must precede publication (exact reference points in the v2 publisher)
| Location | Change |
|---|---|
| L34 `VERSION='2.0.1'` | Bump to `'2.0.2'`. AUTHORITY_ID, the schema `version`/`authority_id` consts, `validate_signoff`, and the written record all derive from it. Not mentioned in CONTEXT; required. |
| L36-44 `SUPERSEDED_V2_0_0` | Replace by `SUPERSEDED_V2_0_1` with the same 9 keys (`authority_id, version, commit, relative_path, sha256, governance_decisions_sha256, normalisation, governance_decisions_relative_path, governance_decisions_normalisation`). Same `CRLF_TO_LF` norms. |
| L176, L243, L320, L379, L537 | Swap constant (build, validate_authority, validate_publication, schema `pinned`, dry-run). Update error text ("2.0.0 publication" -> 2.0.1). |
| L297, L300 | Digest binding reads `SUPERSEDED_V2_0_1['governance_decisions_sha256']` (same `4e746d1f…`); messages that say "2.0.0 decisions digest" / "2.0.1 may not change" need rewording. A test matches `match='2.0.0'` (publication test L183); update it. |
| L490 mutation `supersedes_governance_digest_differs` | Description text names 2.0.0; update. Count stays 29 (this changes the negative-validation output text, which is regenerated anyway). |
| L719-721 pre-publication branch | Use `SUPERSEDED_V2_0_1` (commit `31addfa`, sha `7be5eb88…`, id/version 2.0.1); messages. Pre-publication mode then accepts exactly the current on-disk record. |
| `validate_publication` (new) | Add D-08 check: `git_show(SUPERSEDED_V2_0_1.commit, SUPERSEDED_V2_0_1.relative_path)` parsed as JSON; for all 80 rows compare the four decision fields (`not_applicable_decision_state`, `not_applicable_rule`, `not_applicable_authority`, `decision_ids`) and the top-level `applicability_decision_ids`. `GitHistoryError` must propagate (the mutation gate re-raises it, L614), not be counted as a rejection. Mutation `run_mutations` calls `validate_publication` 29 times, each shelling out to git: acceptable, but avoid re-reading git per mutation if runtime matters (cache the 2.0.1 bytes or accept ~30 `git show` calls; tests already do similar). |
| `dry_run_summary` L533 | Add "what changed" block (D-09/D-10) derived from `authority['source_lineage']` entries (path, norm), `len(NEGATIVE_MUTATIONS)`, schema `additionalProperties:false` levels (walk `schema()`), and the row-comparison result. Existing test `test_dry_run_summary_lists_decisions_rules_and_supersession` asserts `version 2.0.0 (commit 54a7fd0)` and "equals the 2.0.0 value"; update. Keep the forbidden-words rule (`best, critical, important, recommended, highest` must not appear in the output; a test checks the whole dry-run output). |

### Reply freeze (D-01/D-02), concrete findings
`build_archive_assessment_demo3_w1_req_001_reply.py` reads live files in `load_inputs` (L231), `check_inputs_bound` (L218), `validate_reply` (L253 digest check against live files) and `resolve_record_commit` (L262). Required reshaping:
- Add constants `REPLY_PUBLICATION_COMMIT = '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb'`, `REPLY_RECORD_COMMIT = '4d9b7c1f41df5fa7575d4653a7d54ff9cf0a192b'`. `git_show` requires 40-hex, so the full SHA is mandatory (confirmed present and a commit object; clone is not shallow).
- Inputs at the commits: authority, sign-off, decisions, manifest, trace from `git_show(31addfa, …)`; record from `git_show(4d9b7c1, …)`. The decisions file at `31addfa` equals the live file today, but read it from the commit so the reply never depends on later edits.
- **Gotcha:** `build_reply` calls `V2.validate_signoff(signoff, record['authority_sha256'])` (L72). After the bump, that function rejects the 2.0.1 sign-off (`authority_id`/`version` compared with the live constants at publisher L524-525). Fix by giving `validate_signoff` optional `authority_id`/`version` parameters defaulting to the module constants and passing the pinned 2.0.1 values from the reply script, or the frozen path fails closed on its own input. Also check `V2.validate_signoff` callers in tests.
- The `history_note` is built from `authority['source_lineage']['supersedes']`; with the authority read from `31addfa` this still yields 2.0.0 @ `54a7fd0`, so the reply bytes stay identical. Test `test_history_note_binds_to_supersedes_and_decisions` currently reads the live authority and asserts `54a7fd0`; point it at the frozen inputs. `V2.lf_digest(V2.GOVERNANCE_DECISIONS)` in `history_note` (L82) and in the Markdown remains valid because the decisions file is unchanged, but should also come from the pinned blob for consistency.
- `resolve_record_commit` becomes: keep the shallow check (`rev-parse --is-shallow-repository`, fail unless `false`), then return the constant after confirming it is an ancestor (`merge-base --is-ancestor`) or that `git cat-file -e` succeeds; do not use `git log` on the live record path. Existing tests `test_record_commit_is_last_change_of_the_record` (asserts `resolve_record_commit()==git log -n1` of the live record) and `test_resolve_record_commit_*` (fake git returning `log_sha`) must be rewritten.
- `--push-check` reads `V2.load(V2.PUBLICATION_RECORD)['publication_commit']`; after 2.0.2 that is the new commit. Decide whether it should use the 2.0.1 constant (reply is the 2.0.1 artefact) or stay live; flag in the plan, low risk.
- Many reply tests use `inputs()` (live files) and `run_validate_reply`; they need the frozen loader. Tests that monkeypatch `V2.SIGNOFF` / `V2.GOVERNANCE_DECISIONS` to prove tampering (L79-100) must instead monkeypatch the git reader or the constants. Required new tests: validator passes with live record/authority at 2.0.2; reply bytes tamper fails; constant tamper (wrong publication/record SHA) fails; no-history (shallow/`git` unavailable) fails closed.
- CI runs this validator at the record commit; `fetch-depth: 0` supplies history. Reply files themselves are untouched (verify with `git diff --stat` empty for the two reply files and the reply schema over the whole phase).

### Recommended commit sequence (explicit paths each)
1. Publisher + publisher tests: `VERSION`, `SUPERSEDED_V2_0_1`, validate/schema/mutation/pre-publication swap, D-08 comparison, `validate_signoff` parameters, tests.
2. Reply freeze + reply tests (D-01..D-03).
3. Dry-run "what changed" section + test.
4. (orchestrator) `--emit-schema` output is part of the publication commit, not a code commit: the schema file on disk must be the regenerated one before `--publish`, and `git status` should show only expected paths.
5. Dry-run, checkpoint, sign-off write, `--publish`, `--validate-signoff`.
6. Publication commit (12 paths: schema, authority, sign-off, 7 generated files; fewer only if a file is byte-identical, which is not expected because `published_on` changes).
7. `--validate --pre-publication` PASS, `--record-publication <sha>`, record commit (1 file).
8. Full suite and five validators; then D-05 checkpoint.

### Anti-patterns to avoid
- `git add -A` / `git add .` / `git commit -a` (tree holds `registry/adjudication_rules.json`, `registry/policy_decisions.json`, `.planning/config.json` modified and many `.pytest-*` and untracked docs/registry files).
- Typing digests by hand into `SUPERSEDED_V2_0_1`; derive and then assert with a git-history test (like `test_superseded_constants_match_git_history`, but against `31addfa` and `4d9b7c1:…publication_record.json`).
- Editing the publisher script after `--publish` and before the publication commit (would break the manifest/script digest test; script edits after the commit are tolerated by validate, but still avoid).
- Weakening the plain `--validate` or adding an auto-detect for the post-publication window (rejected in D-04).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Regenerating hashed files | hand-edited JSON or sed on digests | `--emit-schema`, `--publish`, `--record-publication` | Rebuild-equality validation fails on any hand edit |
| Reading historical bytes | `git checkout` or worktree switching | `git_show(commit, rel)` (40-hex, repo-relative, `GitHistoryError`) | Existing fail-closed helper, no tree mutation |
| LF digests | new hashing helpers | `lf_bytes`, `lf_digest`, `sha_text(jtext(...))` | Keeps CRLF_TO_LF semantics identical |
| Decisions digest compare | new constant | existing `4e746d1f…` binding via `SUPERSEDED_V2_0_1['governance_decisions_sha256']` | Already enforced at L297/L300 |
| Sign-off validation | custom checks | `validate_signoff` / `--validate-signoff` | Enforces exact role and dual-role statement |
| Staging | wildcard adds | explicit path lists; `git diff --cached --name-only` before each commit | Working-tree hygiene (PUB-09) |

## Sign-off record (shape verified from `validate_signoff`, L509)
Exactly the keys `status` (`PUBLICATION_SIGNOFF`), `approval` {`approver` `Oscar Mack`, `role` `EMS_GOVERNANCE_AUTHORITY`, `date` real ISO date, `scope` non-empty string}, `dual_role_statement` (exact text of `DUAL_ROLE_STATEMENT`), `authority_id` (`…-2.0.2`), `version` (`2.0.2`), `authority_sha256` (the dry-run printed value), `authority_sha256_normalisation` (`CRLF_TO_LF`). Extra keys are rejected. The date becomes `published_on` in every output. Written only after Oscar Mack's explicit approval of the dry-run summary at the blocking checkpoint. Dry-run must be re-run (and the digest re-confirmed) if any code or input changes after sign-off.

## Test state and the red window

Known baseline (08-VERIFICATION, orchestrator run): 663 passed, 3 failed. The 3 expected reds: `test_committed_schema_equals_schema_function` (tests/test_archive_assessment_applicability_authority_v2.py L212; committed schema is the 2.0.1 closed-less schema vs the Phase 8 `schema()`), the real-file validation (`test_real_published_files_validate` and/or `test_publisher_still_valid_and_digest_matches_manifest`), and the reply digest-vs-manifest check (`test_real_reply_files_validate`). [CITED: 08-VERIFICATION.md; exact test ids to be confirmed by the orchestrator's first run in Phase 9 and recorded in the plan.]

Expected additional reds after the first Phase 9 code commit until publication: every test that builds the authority and validates against committed 2.0.1 files (anything touching `VERSION`, e.g. `test_archive_assessment_applicability_authority_v2.py` L144 asserts `MODULE.VERSION == '2.0.1'`; must change to `'2.0.2'` in the same commit). Tests that compare `lin['supersedes'] == MODULE.SUPERSEDED_V2_0_0` (v2.py L204; publication tests L75, L485, L495, L685, L752; lineage tests L34, L55) must be renamed/retargeted. Plan guidance: the first plan runs pytest before and after and lists the delta of red ids; the reply tests should go green (via the frozen path) in commit 2, before publication, because they no longer depend on the live 2.0.1 files.

Tests that must be edited for correctness at 2.0.2 (not just red until publish):
- `test_publication_commit_ancestor_and_file_set` (publication tests L642): add the schema path to `expected`, otherwise `set(files) <= expected` fails on the 2.0.2 commit. Keep the "no adjudication/policy files" assertions.
- `test_superseded_constants_match_git_history` (L682) and `test_rows_equal_2_0_0_rows_…` (L696): keep, adding 2.0.1 analogues (compare against `31addfa` blobs and `4d9b7c1:…record.json`) and a 2.0.1 per-row comparison with a tampered-row failure case (D-08).
- `test_pre_publication_mode_accepts_only_superseded_record` / `test_pre_publication_wrong_commit_or_digest_fails` (L493-520): retarget to 2.0.1.
- Reply tests as above; `test_publication_sha_is_ancestor_and_holds_authority` remains valid against the live 2.0.2 record but should be paired with a 2.0.1 anchor assertion.
- Add D-04 verification (test or command): for the publication paths, `git diff --quiet <pub> <record> -- <paths>` returns 0, with `<paths>` = the 10 publication files (and the schema). The test can read `publication_commit` from the live record and `git log -n1 -- record` for the record commit, guarded by `git_ready()` skip pattern.

## Common Pitfalls

### Pitfall 1: Reply validator red at the publication commit by design
At `<pub>` the record still says 2.0.1, so plain `--validate` fails and the reply validator may too. After D-01 the reply validator should pass even then (frozen), but plain `--validate` stays red until the record commit. Verification belongs on the record commit (D-04), and Hayes' pin is `<pub>`. Mention this explicitly in the plan (rewording of ROADMAP SC4).

### Pitfall 2: Unrelated dirty files leaking into commits
`git status` currently shows ` M .planning/config.json`, ` M registry/adjudication_rules.json`, ` M registry/policy_decisions.json` plus about 60 untracked files (docs, registry, `.pytest-*`). Use `git add -- <path> …`, then `git diff --cached --name-only` equals the expected set before committing; after commit `git show --stat --format= <sha>` must list only those paths. Note `.planning/config.json` is modified: planning-doc commits for this phase must not sweep it in unless intended.

### Pitfall 3: `--publish` before `--emit-schema`
Manifest and certification digest the schema file on disk; running `--publish` against the old schema bakes the wrong digest, and `validate` then fails on `test_committed_schema_equals_schema_function`. Run `--emit-schema`, check `git diff --stat` on the schema, then dry-run and publish.

### Pitfall 4: Sign-off digest stale
The sign-off `authority_sha256` must equal the rebuilt authority digest. Any change to code, decisions, catalog pin, or lineage files after the dry run requires a new dry run and a new sign-off. Do not commit code between dry run and publish.

### Pitfall 5: `validate_signoff` bound to live constants (reply freeze)
Described above; fix with parameters, otherwise the frozen reply validator fails once `VERSION` is bumped.

### Pitfall 6: Line endings on Windows
Writers use `newline='\n'`; `.gitattributes` marks authority, sign-off, record, schema `text eol=lf`. AA1/AA2 lineage files are `-text` (RAW_BYTES). Digests used are LF-normalised except RAW_BYTES entries. If `core.autocrlf` rewrites generated files on checkout, validation uses `lf_bytes` for generated files, but confirm `git check-attr` for `generated/archive-assessment/ems-aa3-v2/*` (not checked here) before relying on it. [ASSUMED]

### Pitfall 7: CI for a branch push
Workflow triggers: `pull_request`, `push` to `main`, `workflow_dispatch`. A branch push alone does not run it. Precedent: runs 38743651222 (failure) and 38744767442 (success) were `workflow_dispatch` on this branch on 2026-10-15; `gh run list --workflow=ems-validate.yml` confirms. Use `gh workflow run ems-validate.yml --ref feature/ems-aa3-archive-applicability-authority`, then `gh run list --workflow=ems-validate.yml --branch … -L 1 --json databaseId,headSha,status,conclusion` and `gh run watch <id>`; confirm `headSha` equals the record commit. Also note that the `validate` job runs too. Pushing publishes 65 local commits that are not yet on `origin/feature/ems-aa3-archive-applicability-authority`. [VERIFIED: git log count, gh]

### Pitfall 8: Push credential
Credential-manager push fails in this session (sh.exe crash). Use the STATE.md workaround: `GIT_CONFIG_COUNT/KEY_0/VALUE_0` with `http.extraheader` `AUTHORIZATION: basic <base64 x-access-token:$(gh auth token)>`, credential.helper cleared. The token must not be printed or written to any file or log. Bash currently works here (STATE says flaky); the memory note says use PowerShell and run pytest with `--basetemp`.

### Pitfall 9: Test runtime and git in tests
The D-08 comparison and frozen reply read git history; tests must skip via the existing `git_ready()` pattern for shallow/no-git, and fail-closed tests must use fakes (as `fake_shallow_git` does) rather than a real shallow clone.

### Pitfall 10: Mutation gates and git errors
`mutation_gates` re-raises `GitHistoryError`; if D-08's check raises a plain `AuthorityError` on missing history it would count as a "rejection" (WR-02 class). Raise `GitHistoryError` for git failures and `AuthorityError` only for content mismatch.

## Code Examples

PUB-08 row comparison (shape only, to match file style):

```python
# in validate_publication, after the v1 comparison
prev = json.loads(git_show(SUPERSEDED_V2_0_1['commit'], SUPERSEDED_V2_0_1['relative_path']).decode('utf-8'))
prev_rows = {r['control_id']: r for r in prev['controls']}
KEYS = ('not_applicable_decision_state', 'not_applicable_rule', 'not_applicable_authority', 'decision_ids')
for r in rows:
    p = prev_rows.get(r.get('control_id'))
    if p is None or any(r.get(k) != p.get(k) for k in KEYS): errors.append(f"{r.get('control_id')}: decision content differs from 2.0.1")
if set(prev_rows) != {r.get('control_id') for r in rows} or a.get('applicability_decision_ids') != prev.get('applicability_decision_ids'): errors.append('decision set differs from 2.0.1')
```

Digest check commands (orchestrator, PowerShell or bash):

```
git show 31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb:registry/archive_assessment_applicability_authority_v2.json | sha256sum   # 7be5eb88...
sha256sum registry/archive_assessment_governance_decisions.json                                                         # 4e746d1f... (LF file)
git diff --quiet <pub> <record> -- <publication paths>   # D-04, exit 0
git show --stat --format= <pub>                           # PUB-09 scope check
```

## State of the Art
Not applicable (internal governance code). The nearest precedent is plan 06-06/06-07 (2.0.1 publication), whose steps this phase repeats with more pre-publication code work.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `core.autocrlf`/attributes do not rewrite files under `generated/archive-assessment/ems-aa3-v2/` | Pitfall 6 | Byte-identity checks could differ across OS; validation uses LF normalisation so low risk |
| A2 | The 3 baseline reds are exactly the tests named; ids not re-run in this session (no test execution by researcher) | Test state | Plan lists the wrong red set; orchestrator should run baseline first |
| A3 | `gh workflow run … --ref <branch>` works for the branch without the file on `main` (main's workflow lacks the trigger per empty grep; prior runs on this branch were dispatched successfully, so it should work) | Pitfall 7 | If dispatch is refused, a PR would be needed, which D-05 forbids; ask Oscar Mack |

## Open Questions

1. **Should `--push-check` follow the 2.0.1 constant or the live record?**
   - Known: it reads the live record's `publication_commit`; after 2.0.2 that is the new commit, which is not the commit the reply cites.
   - Recommendation: bind it to the reply's pinned `REPLY_PUBLICATION_COMMIT` (the reply is a 2.0.1 artefact); add a test.
2. **D-04 check as pytest or as a verification command?** Discretion. Recommend a pytest guarded by `git_ready()` plus a verification-step command in the plan for the explicit record.
3. **Is the version bump to 2.0.2 acceptable inside the first code commit?** It turns every real-file test red from that commit (expected, already in the accepted red window). Recommend yes.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| git (full clone, not shallow) | `git_show`, frozen reply, staging | yes | `rev-parse --is-shallow-repository` = false | none needed |
| `gh` CLI | push check, `gh workflow run`, run watch | yes | 2.91.0 | none |
| Python 3.12, pytest, jsonschema | publisher, tests | assumed present (orchestrator runs them) | not probed | none |
| Network / GitHub token | D-05 push | not probed | — | blocking checkpoint, ask user |

Bash executes in this session (STATE says flaky); the orchestrator is responsible for running tests via PowerShell.

## Validation Architecture (relevant parts only; Nyquist disabled)

| Check | Command (orchestrator) |
|---|---|
| Quick | `python -m pytest tests -k archive_assessment -p no:cacheprovider -q --basetemp=<dir>` |
| Publisher | `python scripts/publish_archive_assessment_applicability_authority_v2.py --validate` (`--pre-publication` at the publication commit) |
| Other four validators | as CI: governance decisions `--validate`, rule proposals `--validate` and `--validate-record`, reply `--validate` |
| Scope | `git show --stat --format= <pub>` lists only the 10 publication paths plus schema; none of `adjudication_rules.json`, `policy_decisions.json`, `.planning/config.json`, untracked files |
| Byte identity (D-04) | `git diff --quiet <pub> <record> -- <paths>` |
| Reply frozen | `git diff --stat <HEAD_before_phase> HEAD -- docs/DEMO3_W1_REQ_001_REPLY.md registry/archive_assessment_demo3_w1_req_001_reply.json schemas/archive_assessment_demo3_w1_req_001_reply.schema.json` is empty |
| PUB-08 | `--validate` plus the D-08 test; digest `4e746d1f…`; counts 21 (3 rules, 18 no-rule) / 59 |

Wave 0 gaps: none for infrastructure (pytest exists); new tests listed above.

## Security Domain (threat-model inputs)

| Pattern | STRIDE | Mitigation in this phase |
|---|---|---|
| Hand-edited or stale hashes pass unnoticed | Tampering | Rebuild-equality `--validate`, manifest digests, record digests re-hashed from the publication commit via `git_show` |
| Publication without authority sign-off | Spoofing / Repudiation | Blocking human checkpoint; `validate_signoff` pins approver, role `EMS_GOVERNANCE_AUTHORITY`, exact dual-role statement and authority digest; sign-off written only after approval, re-done if digest changes |
| Decision drift while changing lineage | Tampering | decisions digest `4e746d1f…` binding + D-08 row comparison against `31addfa`; fail closed without history; `UNKNOWN` never resolves to not-applicable (semantic conflict check at build) |
| Unrelated work shipped in the Hayes pin | Information disclosure / Tampering | Explicit-path staging, `git diff --cached --name-only` and `git show --stat` checks; record commit contains one file |
| Wrong commit pinned / mutable anchors | Tampering | 40-hex SHA constants; test recomputing constants from git (`31addfa`, `4d9b7c1`) |
| Frozen reply silently re-pointed to 2.0.2 | Tampering | Reply constants + byte equality; tamper tests |
| Credential exposure during push | Information disclosure | Token only in process env for the one command (`gh auth token`), never echoed or committed; secret-pattern grep in CI |
| Shallow clone causing false pass | Spoofing | GATE-04 shallow check retained; CI uses `fetch-depth: 0` |
| CI evidence claim without proof | Repudiation | Record run id and confirm `headSha` equals the record commit in `09-VERIFICATION.md` |

ASVS mapping is minimal (V5 input validation via jsonschema; V6 SHA-256 via `hashlib`, no custom crypto).

## Sources

### Primary (HIGH)
- `scripts/publish_archive_assessment_applicability_authority_v2.py` (read in full)
- `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` (relevant parts)
- `registry/…_v2_publication_record.json`, `registry/…_v2_signoff.json`, `.github/workflows/ems-validate.yml`
- `tests/test_archive_assessment_applicability_authority_v2_publication.py`, `…_demo3_w1_req_001_reply.py`, `…_lineage_validation.py`, `…_normalisation_claims.py` (grepped/read)
- git history: `31addfa`, `4d9b7c1`, `54a7fd0`; `gh run list`; planning docs 06-06-SUMMARY, 08-VERIFICATION, ROADMAP, STATE, 09-CONTEXT

### Secondary / Tertiary
- None. No tests or validators were executed by the researcher.

## Metadata
**Confidence:** Standard stack HIGH (existing); architecture HIGH (code read); test red set MEDIUM (from 08-VERIFICATION, not re-run); CI dispatch MEDIUM (precedent runs exist).
**Research date:** 2026-11-12
**Valid until:** until the publisher or reply script is edited again
