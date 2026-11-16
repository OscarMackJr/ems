# Phase 12: Verify-at-Pin and Gate Hardening - Research

**Researched:** 2026-11-16
**Domain:** Python governance publisher, validators, pytest harness, GitHub Actions CI (EMS archive-assessment authority v2)
**Confidence:** HIGH. Every red-set claim below was measured in a scratch clone at HEAD `663abf7`, not inferred.

## Summary

Phase 12 has two kinds of work. The new work is verify-at-pin (PIN-01), byte identity at the record commit (PIN-02) and the publisher-script digest in `--validate` (GATE-06). The other kind closes review findings, and more of that is already done than REQUIREMENTS.md implies. The 08-REVIEW fixes for WR-03, WR-05, WR-06 and WR-07 landed in Phase 8 (commits `af37b01`, `a9ff5d1`, `b72c3e9` and `6893164`, all ancestors of HEAD). The v1.1.0 audit listed them as open because it read 08-REVIEW.md and not 08-REVIEW-FIX.md. So GATE-07, GATE-08 and GATE-09 are **residual-gap** tasks, not rewrites. What is left:
- GATE-07: `validate_published` still runs the Python checks before the schema check. JSON decoding and the manifest shape can still escape as non-domain exceptions.
- GATE-08: the logic is in place. What is missing is a test that drives the `--validate` CLI path with real changed bytes.
- GATE-09: the D-10 test covers `validate_publication` but not `validate_published` (`--validate`), and a D-13 test with a fabricated digest still exists.

The red window can be controlled precisely. In a scratch clone:
- A comment-only edit to the publisher turned **exactly one** test red: `test_publisher_still_valid_and_digest_matches_manifest`. All six CI validators stayed green.
- Simulating the 2.0.3 version and supersedes move turned CI validator 1 red, plus 8 tests. Five of those are literal or expectation tests that the move commit must update. Three are real-file tests that stay red until Phase 13 publishes.
- GATE-06 itself turns CI validator 1 and `test_real_published_files_validate` red the moment the publisher bytes differ from the manifest, which happens in the GATE-06 commit itself.

Commits that edit the publisher but do not add the script-digest check keep CI green. So GATE-06 should come after the other publisher hardening, and the supersedes move should come last.

There are also three design traps that the CONTEXT does not mention:
1. `test_module_does_not_call_git` and `test_publisher_source_runs_no_subprocess_or_evaluator` require `subprocess` to appear only inside `git_show`. The new `git merge-base`, `git status`, `git rev-parse` calls need a planned seam, and those two tests need updating in the same commit.
2. `git_show` rejects `HEAD`, because it requires a 40-hex commit. D-06 must resolve HEAD to a SHA first.
3. The `env` fixture runs under a temp ROOT with no git repository. Every env test that expects plain `--validate` to PASS needs fakes for the new git calls.

**Primary recommendation:** Use six commits:
1. D-09/D-10/D-11 test and CI. Green.
2. GATE-09, GATE-08 and the GATE-10 test-only items. Green.
3. GATE-10 IN-04 in the frozen reply builder. Green.
4. GATE-07 and IN-01. Opens the window with one test.
5. PIN-01/PIN-02, then GATE-06 as its own step. Adds one test and CI validator 1.
6. The supersedes move to 2.0.2 and the 2.0.3 constants. Adds `test_committed_schema_equals_schema_function`.

Route every new git call through one new helper. Record the red set per commit in a `12-BASELINE-RED.md` ledger, following `09-BASELINE-RED.md`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Verify-at-pin mode (PIN-01)
- **D-01:** Rename `--pre-publication` to `--at-pin`. The command is `--validate --at-pin`, and `--pre-publication` is removed, with no alias. The publish sequence uses `--at-pin` in the step where it used `--validate --pre-publication` before (the 09 carried-forward sequence). `--at-pin` without `--validate` is a parser error, as today.
- **D-02:** In at-pin mode the identity of the superseded authority comes from the authority's own `source_lineage.supersedes` entry: authority id, version, commit and authority sha256. That entry is already checked against the pinned constant by `validate_publication` and `validate_lineage`. `check_publication_record` no longer hard-codes `SUPERSEDED_V2_0_1[...]`. The record must name exactly that superseded publication, and its digests must match the blobs at the superseded commit, so the existing `git_show` cross-checks still apply.
- **D-03:** At-pin mode prints a single JSON object when it passes, for example `{"status":"PASS","mode":"AT_PIN","deferred":["PUBLICATION_RECORD_BINDING: the record naming this commit is written in the next commit; run plain --validate at the record commit"]}`. The exact deferred wording is up to the planner, but it must name the record-to-commit binding as the only deferred check. Plain `--validate` still prints `PASS`, so CI and existing output are unchanged.
- **D-04:** At-pin mode fails closed if any of the publication paths (the D-05 set) is modified or untracked in the working tree, using `git status --porcelain -- <paths>`. The script cannot tell whether HEAD is the pin, so a clean tree is what it can enforce. If git is unavailable or the clone is shallow, it fails closed, as 07 D-11 and 08 D-09 require.

#### Byte identity at the record commit or later (PIN-02)
- **D-05:** The "publication files" are the 10 files the publication commit contains: `AUTHORITY`, `SCHEMA`, `SIGNOFF`, and every file in `OUT` (the 7 generated files, manifest included). The list is derived from the publisher's path constants and is defined once, so at-pin's dirty check (D-04) and the Phase 13 PUB-12 commit check can reuse it. The publication record is not in the list, because it is written in the next commit.
- **D-06:** Plain `--validate` requires `record['publication_commit']` to be an ancestor of HEAD, checked with `git merge-base --is-ancestor`. For each D-05 file it then requires `git show <publication_commit>:<path>` to be byte-identical to `git show HEAD:<path>`. The existing LF-digest checks still cover the working-tree bytes. It fails closed without history or in a shallow clone. When run at the publication commit itself, plain `--validate` fails because the record names the previous authority. Its error message should point to `--validate --at-pin`.

#### Publisher-script digest (GATE-06)
- **D-07:** Plain `--validate` requires `lf_digest(live publisher script)` to equal `manifest.publisher_script.sha256`. It also requires the LF digest of `git show <publication_commit>:<script path>` to equal the same value. The consequence is accepted: any later edit to the publisher, even a comment, turns `--validate` red until the next certified republication. This is the existing red-window model, and it matches the project rule that hash-based certification breaks on uncoordinated hand edits.
- **D-08:** In at-pin mode, the live publisher script must equal the manifest digest. At the pin, the live script is the pinned one, and D-04 guarantees it is unmodified. The script check is not deferred.

#### WR-05, IN-08, IN-09 (folded in from 11-REVIEW)
- **D-09:** Narrow the CI `archive-assessment` step in `.github/workflows/ems-validate.yml` from `pytest tests -k archive_assessment` to `pytest tests/test_archive_assessment_*.py`. The planner should check how the glob expands on ubuntu bash; quoting may be needed. The step keeps `-p no:cacheprovider -q` and `EMS_FAIL_ON_SKIP=1`.
- **D-10:** Scope the `pytest_make_collect_report` hook in `tests/conftest.py` to collectors whose node id or path is an archive-assessment test module (`test_archive_assessment_*`). Skips in other modules are left alone. Add a subprocess case to `tests/test_archive_assessment_skip_guard.py` with a deselected, non-archive skipping module next to an archive module. With the guard on, the archive tests must still run and pass. A module-level skip in an archive-assessment module must still fail.
- **D-11:** Fix the wording in `tests/aa_history.py`. IN-08: the HINT must state accurately how far `EMS_ALLOW_NO_HISTORY=1` reaches. IN-09: when the shallow-check output is unrecognised (neither `true` nor `false`), the message must say so and show the raw output, not claim the repository is shallow. Fail-closed behaviour is unchanged. D-09, D-10 and D-11 go in one small test/CI commit. It should land first, while everything is still green.

#### Carried forward (not re-asked)
- **Red window:** it opens at the first publisher edit in this phase and closes at the 2.0.3 publication commit and record commit (Phase 13). Each plan that touches the publisher lists every test or CI step it turns red. The red set may only shrink or stay as listed.
- **Final form:** "Final 2.0.3 form" means the publisher's supersedes binding moves to 2.0.2, following the 09 D-07 pattern. A `SUPERSEDED_V2_0_2` constant names authority id, version 2.0.2, commit `ae15c7458e49c8f55cc58c61bab04bc716aa9892`, the 2.0.2 authority LF sha256 (`a44eea1f…`) and the decisions LF sha256 (`4e746d1f…`). Values come from files and git, never typed by hand. All dependent uses move with it: validators, schema `pinned(...)`, mutations, the PUB-08 row comparison (2.0.3 against 2.0.2) and the dry-run summary. Version and id constants for 2.0.3 follow the existing pattern.
- **Grandfathering (08 D-13):** the certified answers digest still falls back to `norm`. Any other digest gets the strict check. GATE-08 applies that same rule on the `--validate` path of `validate_decisions`.
- **Domain errors only (08 D-04/D-05):** mutation gates count only domain errors. GATE-07 hardens shapes so no `TypeError`, `KeyError` or `AttributeError` escapes. `validate_published` runs the schema check before the Python checks.
- **Frozen builders (Phase 11):** the reply and 2.0.2 notice builders are frozen and must stay green, along with their freeze tests. The GATE-10 item "`resolve_record_commit` handles git errors the same way everywhere" touches `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:341`. Any change there must leave the reply validator result, the frozen literals and the Phase 11 independence tests unchanged.
- **Staging:** stage only by explicit path. Never stage `.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json` or the unrelated untracked files.
- **Who runs tests:** the orchestrator runs pytest and validators through PowerShell with a fresh `--basetemp`. Report pytest's own exit code, not one from a pipe.
- **No CI weakening:** no CI auto-detect mode is added (09 D-04). CI keeps running plain `--validate`.

### Claude's Discretion
- Helper names, such as the D-05 path-list function and the at-pin result builder, in the publisher's compact single-quote style.
- Exact deferred-check wording and error messages, including the D-06 pointer to `--at-pin`.
- How GATE-07..10 are split into commits. Preferred order: (1) the D-09/D-10/D-11 test/CI commit while green; (2) the GATE-09 and GATE-10 test-only items where possible; (3) the publisher changes, which open the red window; (4) the supersedes move to 2.0.2. Each commit stages explicit paths and lists its red set.
- Whether at-pin mode and plain mode share one function with a mode argument, or are separate functions.

### Deferred Ideas (OUT OF SCOPE)
- 11-REVIEW IN-01..IN-07 (frozen-builder and test polish). Not in Phase 12's requirements, and touching the frozen builders has its own risk. Revisit after 2.0.3.
- V2-01 (decisions for the other 59 controls) and V2-02 (Hayes re-run) stay deferred, per PROJECT.md.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PIN-01 | `--validate` at a clean checkout of the 2.0.3 publication commit gives PASS and names the one deferred check | §Pattern 2 (at-pin flow); §Pitfalls 1-4 (git seam, HEAD resolution, ignored `generated/`, Windows long paths); D-02 verified against git (record digests match the `ae15c74` blobs) |
| PIN-02 | Plain `--validate` passes at the record commit or later, by ancestry and D-05 blob identity | §Pattern 3. Measured: `ae15c74` contains exactly the 10 D-05 files, record commit `a71257e` contains only the record, and D-06 is green at the current HEAD |
| GATE-06 | `--validate` checks the publisher-script digest | §Pattern 4. Live and pinned (`ae15c74`) script LF digests both equal the manifest value `f6b51cca…` today. This step turns validator 1 red (measured) |
| GATE-07 | Only `AuthorityError` from malformed shapes; schema before Python in `validate_published` | §GATE-07 probe table: 6 escaping shapes found |
| GATE-08 | `--validate` path of `validate_decisions` enforces `norm_templated` uniqueness | Already implemented (`a9ff5d1`, builder L321-327). Probed with real changed bytes (20 rejections). The gap is a CLI-path test |
| GATE-09 | D-10 test covers build and `--validate`; D-13 test uses real changed bytes | The D-10 test exists for `validate_publication` only. A real-bytes D-13 test exists, but the fabricated-digest test `test_changed_answers_bytes_remove_exemption` is still present |
| GATE-10 | IN-01, IN-02, IN-03, IN-04, IN-06 | §GATE-10 locator table |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- Python 3.12, `jsonschema`, PyYAML, pytest. Match the existing code style: the publisher uses single quotes and compact one-line guards that raise `AuthorityError`.
- Fail closed. Unknown or missing evidence never becomes PASS or NOT_APPLICABLE. Validators raise a domain exception (`AuthorityError`).
- Use deterministic JSON: `json.dumps(value, indent=2, sort_keys=True) + '\n'`. Use SHA-256 via `hashlib`.
- Registry JSON contains no absolute paths. Use repo-relative forward-slash paths.
- Follow the publication pattern: schema, publisher, certification, traceability, pytest. Hash-based certification breaks on uncoordinated hand edits.
- The working tree has unrelated uncommitted work. Stage by explicit path only. Never stage `.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json` or untracked files.
- GSD workflow: edits only inside `/gsd-execute-phase`.
- No new third-party packages. This phase installs nothing.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| At-pin / plain `--validate` modes, script digest, byte identity | Publisher CLI (`scripts/publish_..._v2.py`) | Git history (read-only) | All checks are offline, file- and git-based; the publisher already owns `validate_published` and `check_publication_record` |
| Cross-note uniqueness on `--validate` | Decisions builder (`build_archive_assessment_governance_decisions.py`) | Publisher (`validate_governance_decisions` calls it) | Logic lives in `validate_decisions`; the publisher only wraps it |
| Shape hardening (GATE-07) | Publisher validators | JSON Schema (committed `schemas/..._v2.schema.json`) | Schema first, then Python, both raising domain errors |
| Skip guard / history helper | pytest harness (`tests/conftest.py`, `tests/aa_history.py`) | — | Test infrastructure only |
| CI test selection | GitHub Actions (`ems-validate.yml`) | — | bash glob expansion |
| `resolve_record_commit` error handling | Frozen reply builder | — | Frozen script, minimal edit, output-neutral |

## Standard Stack

No new libraries. The existing, verified environment:

| Library | Version (venv) | Purpose |
|---------|---------------|---------|
| CPython | 3.12.10 | runtime [VERIFIED: `.venv/Scripts/python.exe --version`] |
| pytest | 9.1.1 | tests, collect hook [VERIFIED: `pytest --version`] |
| jsonschema | 4.26.0 | `Draft202012Validator` [VERIFIED: importlib.metadata] |
| PyYAML | 6.0.3 | catalog parse [VERIFIED] |
| git | 2.54.0.windows.1 (local) | `git show`, `merge-base`, `status`, `rev-parse` [VERIFIED] |

`jsonschema.ValidationError` and `SchemaError` subclass `Exception`, not `ValueError` [VERIFIED: MRO printed]. So they are not domain errors unless wrapped.

## Package Legitimacy Audit

Not applicable. This phase installs no external packages. `requirements*.txt` stay unchanged.

## Current State at HEAD `663abf7` (baseline, measured)

- All 6 CI validators print PASS in the working repo and in a fresh scratch clone.
- `pytest tests/test_archive_assessment_*.py` with `EMS_FAIL_ON_SKIP=1`: **918 collected**, pytest exit **0** in the working repo.
- The record names `2.0.2` at `ae15c7458e49c8f55cc58c61bab04bc716aa9892`.
  - Record `authority_sha256` `a44eea1f98ec361ab100c554eb3a8d3529cfeb1fec78ec6d38193a675f0b8beb` equals the LF digest of the authority blob at `ae15c74`.
  - Record `manifest_sha256` `9991228ab7ff…` equals the manifest blob at `ae15c74`.
  - Decisions LF sha256 at `ae15c74`: `4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f`. These are the SUPERSEDED_V2_0_2 source values; read them from git and files, not by hand.
- Manifest `publisher_script.sha256` = `f6b51cca0fae899aa51170f7b14a5b936fc3fae7372a68ead5de90a8c5af89b6`. This equals the live script's LF digest and the script's LF digest at `ae15c74`. The publisher has not changed since `251cb30`, which comes before `ae15c74`.
- `git diff-tree ae15c74` lists exactly the 10 D-05 files. `git diff-tree a71257e` lists only the record.
- `--validate --pre-publication` at HEAD fails with "pre-publication record must name the 2.0.1 publication commit". This is expected, because HEAD is not a pin.

## Red-Window Inventory (answers planner question 1)

### Measured in a scratch clone (`git clone --shared`, `core.longpaths=true`)

| Stage | CI validators red | Tests red (excluding 1 environmental, see note) |
|---|---|---|
| base (HEAD) | none | none |
| comment-only publisher edit | **none** (all 6 PASS) | `v2_publication::test_publisher_still_valid_and_digest_matches_manifest` |
| VERSION→2.0.3 + supersedes values→2.0.2 (constant name kept) | **#1 publisher `--validate`** ("authority identity/version/status invalid; source_lineage supersedes does not name the 2.0.1 publication") | 8: see the split below |

Note: in a fresh **Windows** clone, `notice_2_0_2::test_committed_notice_files_validate` fails in every stage. The notice docs, registry and schema files have no `eol=lf` attribute, so `autocrlf=true` checks them out as CRLF, and the test asserts `b'\r' not in bytes`. This is not caused by Phase 12. The working repo and ubuntu CI are unaffected. See Open Question 4.

Version-move reds, split by kind:
- **Literal or expectation tests. The move commit must update them, so they never land red:**
  - `v2::test_version_and_authority_id_come_from_constants` (asserts `'2.0.2'`)
  - `v2_publication::test_version_constants_and_published_on_removed` (`'2.0.2'`)
  - `v2_publication::test_pre_publication_binding_names_2_0_1_literals` (2.0.1 literals; renamed or rewritten for `--at-pin` anyway)
  - `v2_publication::test_superseded_v2_0_1_constants_match_git_history` (becomes a SUPERSEDED_V2_0_2-vs-git test)
  - `v2_publication::test_dry_run_summary_lists_decisions_rules_and_supersession` (`'2.0.1'`, `'What changed in 2.0.2'`, `'row comparison 2.0.1 -> 2.0.2'`, `'GATE-01 to GATE-05'`)
- **Real-file tests that stay red until the 2.0.3 publication (accepted window):**
  - `v2::test_committed_schema_equals_schema_function` (`schema()` pins VERSION, AUTHORITY_ID and the supersedes constants)
  - `v2_publication::test_real_published_files_validate`
  - `v2_publication::test_publisher_still_valid_and_digest_matches_manifest`

Renaming `SUPERSEDED_V2_0_1` to `SUPERSEDED_V2_0_2` also breaks these, by AttributeError, unless they are updated in the same commit. Each is a reference to the module constant:
- **Module-level** `PINNED_COMMITS = (..., MODULE.SUPERSEDED_V2_0_1['commit'])` in `test_archive_assessment_lineage_validation.py:29` and `test_archive_assessment_normalisation_claims.py:36`. An AttributeError here is a collection error, which takes out the whole module (80 and 7 tests).
- The `fx` fixture (lineage L46), `test_d10_live_catalog_edit_or_delete...` (lineage L336), and the `env`/`fake_git_show`/`prev_201_authority_bytes`/`superseded_record` helpers in v2_publication.
- `v2::test_supersedes_and_v1_baseline_follow_constants`, `v2_publication::test_lineage_records_governance_decisions_and_v1` and `test_validate_signoff_accepts_frozen_2_0_1_signoff_with_explicit_identity`.
- Message-match tests on `'2.0.1'`: L182, L1032, L1038, and L540/L543 (the pre-publication ones).

13 references in v2_publication, 3 in lineage, 1 each in v2 and normalisation_claims, and 12 in the publisher [VERIFIED: git grep]. Make messages version-agnostic (`f"...differs from {sup['version']}"`, the 09 D-07 pattern) so tests can match on `sup['version']`.

### Per planned publisher change (derived from measurements and code reading)

| Change | Opens red (tests) | Opens red (CI) | Stays green (notable) |
|---|---|---|---|
| Any publisher byte edit (first edit) | `test_publisher_still_valid_and_digest_matches_manifest` | — | `test_real_published_files_validate`, all 6 validators, `test_manifest_publisher_script_digest_matches_publication_commit` (reads the pinned blob, not the live file), `normalisation_claims::test_manifest_publisher_script_normalisation_claim` (pinned) |
| GATE-07 (schema first, wrapped errors, manifest guards) | none beyond the above, if the 29 mutation outcomes are unchanged | — | Must not change `rejected_by` for any mutation. For example, do NOT add a closed top-level key check to `validate_authority` (08 IN-01). It would flip `extra_top_level_field` from `['SCHEMA']` to both gates and change `N_NEGATIVE`, which turns validator 1 and L843 red |
| IN-01 dry-run text | none (the dry run is not a committed output) | — | `test_dry_run_*` must be updated in the same commit |
| D-01 rename, D-02, D-03, D-04 (at-pin) | none at real files (no CI step uses at-pin) | — | env tests are rewritten in the same commit |
| D-05 + D-06 (ancestry + blob identity) | none. D-06 is **green at the current HEAD** (`ae15c74` is an ancestor and the 10 blobs are identical) | — | `test_real_published_files_validate` stays green |
| GATE-06 (D-07 live + pinned script) | `test_real_published_files_validate` | **#1 publisher `--validate`** (the live script differs from `f6b51cca…` from this commit on) | #2–#6 |
| Supersedes move + VERSION 2.0.3 | `test_committed_schema_equals_schema_function` (+ the literal tests, updated in the same commit) | #1 (already red) | #2 decisions, #3/#4 rule proposals, #5 reply, #6 notice: all PASS (measured) |

The final accepted red set at the end of Phase 12 (closed by Phase 13) is these 3 tests plus CI validator 1:
- `v2::test_committed_schema_equals_schema_function`
- `v2_publication::test_real_published_files_validate`
- `v2_publication::test_publisher_still_valid_and_digest_matches_manifest`

Three tests should be checked as red-or-green at each commit:
- `test_decisions_gate_rejects_tampered_file`: calls `validate_published()` expecting AuthorityError, and stays green because it fails earlier, in `validate_governance_decisions`.
- `test_publication_commit_ancestor_and_file_set` and `test_publication_files_byte_identical_between_publication_and_record_commit`: green throughout, because the record is unchanged.

**Tests asserting `--validate` PASS against the live repo:** only `test_real_published_files_validate` (L637) and `test_publisher_still_valid_and_digest_matches_manifest` (L650, which calls `validate_published()`). `test_cli_validate_pre_publication_passes_true` stubs `validate_published`. CI step "Archive-assessment validators" line 1 runs it for real.

## Frozen Builder Dependencies (planner question 2)

Neither `build_archive_assessment_demo3_w1_req_001_reply.py` nor `..._notice_2_0_2.py` imports the publisher, calls its `--validate`, or mentions `--pre-publication` [VERIFIED: grep and the Phase 11 `publisher_refs` AST scanner test]. Both read only pinned blobs through their own `git_show`. Their tests compare against **pinned** publisher blobs at `31addfa` and `ae15c74`, not the live script.

`test_validate_reply_passes_with_a_mutated_live_publisher` execs the live publisher source. Any edit must still compile and define `AuthorityError` at module level. With the publisher edited and the version moved, validators #5 and #6 stayed PASS (measured). The rename has no impact on them.

## `--pre-publication` References (planner question 3)

| Location | Kind | Action |
|---|---|---|
| `scripts/publish_..._v2.py` L576 (`dry_run_summary` fixed gate line "publication-record check and pre-publication mode") | dry-run text | Update; dry-run output is not committed |
| L713, L737, L742, L747, L749, L750, L753 (`pre_publication` parameter and messages "pre-publication record must…") | code | Rename to `at_pin`; messages derive from `sup['version']` |
| L767-769 (`--pre-publication` argparse, `parser.error('--pre-publication requires --validate')`) | CLI | Replace with `--at-pin`, no alias |
| tests v2_publication L490, L505, L517, L533-535, L537-544, L567-569, L608-620 | tests | Rename and rewrite (`validate_published(True)` positional calls, `'--pre-publication'` argv, the stub lambda `pre=False`) |
| `docs/` (2.0.2 notice, reply) | — | **No occurrences** [VERIFIED: git grep]. Nothing frozen changes |
| `.planning/**` (08, 09, MILESTONES, PROJECT, RETROSPECTIVE, milestone archives) | historical docs | Leave as history. Optionally update the PROJECT.md "Validated" line (L81) to note the rename. Phase 13 plans should use `--at-pin` |

## GATE-07: Malformed Shapes That Still Escape (planner question 4)

Probe: `validate_published()` on a scratch clone, with one file mutated per row [VERIFIED: probe_gate07.py output].

| Input | Today | Fix |
|---|---|---|
| authority file is invalid JSON | `JSONDecodeError` | checked loader → `AuthorityError` (mirror the builder's `load_checked`) |
| sign-off file is invalid JSON | `JSONDecodeError` | same |
| manifest invalid JSON | `JSONDecodeError` | same |
| manifest is a list | **`AttributeError`** (`manifest.get`) | `if not isinstance(manifest, dict): raise AuthorityError(...)` |
| record invalid JSON | `JSONDecodeError` | same loader |
| committed schema invalid JSON | `JSONDecodeError` | same loader |
| committed schema not a valid schema (`{"type":7}`) | **`TypeError`** | `Draft202012Validator.check_schema` + wrap `SchemaError` |
| schema violation on authority (once schema-first) | `jsonschema.ValidationError` | wrap: `raise AuthorityError(f'published authority fails the schema: {e.message}') from e` |
| `validate_lineage([])` (direct call) | **`AttributeError`** | `if not isinstance(lin, dict): raise AuthorityError(...)` (unreachable through `validate_published` today, but GATE-07 names it) |

The following already raise `AuthorityError`:
- an authority that is a list, string or number;
- `source_lineage`, `supersedes`, `governance_decisions`, `v1_baseline`, `catalog_reference`, `not_applicable_semantics` or `field_definitions` that are lists or strings;
- rule `conditions` as a string, a rule as a list, unhashable condition fields, `decision_ids` as a dict;
- unhashable decision state or authority;
- a sign-off that is a list or has a list `approval`, or an int date;
- manifest `publisher_script` as a list;
- every malformed `artifacts` shape (caught first by the manifest byte-compare);
- a record `publication_commit` that is an int (in both modes), a record `authority_id` that is a list.

Ordering: `validate_published` L717 runs `validate_publication(a)` and then the schema. Swap the two, and wrap `ValidationError`. The 08 fix log kept Python first to avoid changing exception types in tests, and wrapping removes that concern. In the probe, no existing test expects a raw `ValidationError` from `validate_published` [VERIFIED: grep].

Keep the 29 mutation `rejected_by` outcomes byte-identical. The planner should assert `run_mutations` output equals the committed `N_NEGATIVE` until the move commit.

## GATE-08 (planner question 5)

`validate_decisions` (builder L321-327) already has the logic: `key = norm if d.get('answers_sha256') == CERTIFIED_ANSWERS_SHA256 else norm_templated` over unsuperseded record notes. It was added by `a9ff5d1`. It runs on both `--validate` paths: the builder `main --validate` (L406) and the publisher's `validate_governance_decisions` (L633).

Probe with real bytes [VERIFIED]:
- With the committed decisions and certified answers, the check passes.
- Copy the answers and append `\n`, set `ANSWERS` to the copy, and set the decisions `answers_sha256` to that real digest: `AuthorityError` with **20** "repeats the note of" entries.
- The same changed copy with the stale certified digest in the decisions: "answers_sha256 does not match the live answers file", and no uniqueness errors. This is still fail-closed.

D-13 grandfathering holds. Keep it exactly as it is.

Residual work, all tests:
- (a) Drive the builder CLI `main()` with `--validate` on a decisions document whose `answers_sha256` equals the real digest of a changed answers copy. Assert `repeats the note of`.
- (b) Do the same through `PUB.validate_governance_decisions()` with `GOVERNANCE_DECISIONS` and the builder `ANSWERS` monkeypatched.
- (c) Optionally, replace `test_validate_decisions_rejects_templated_note_collision_for_uncertified_answers`, which monkeypatches `CERTIFIED_ANSWERS_SHA256` to `'f'*64`, with the real-bytes form.

Note: `main --validate` calls `validate_decisions` before the rebuild comparison, so the first error raised is the uniqueness error.

## GATE-09 (planner question 6)

**D-10 (WR-06).** `test_d10_live_catalog_edit_or_delete_does_not_change_build_or_validation` (lineage L333-353) runs in a temp repo where only the catalog is committed. It proves that `build_authority`, `build_published_authority` and `validate_publication` are unchanged after the live catalog is overwritten or deleted. It does **not** cover `validate_published` / `--validate`, which is what GATE-09 asks for.

Recommended test:
- `git clone --shared <ROOT> <tmp>/c` (fast, uses alternates).
- Run `python scripts/publish_..._v2.py --validate` in the clone with `subprocess` and record `(returncode, last stderr/stdout line)`.
- Overwrite `registry/control_catalog.yaml` in the clone, rerun, then delete it and rerun.
- **Assert the outcome is unchanged, not that it PASSes.** This makes the test robust across the red window: while the window is open, `--validate` is red with the same message before and after the edit.
- Set `git -C clone config core.longpaths true`, because of Windows path length (Pitfall 4).
- Guard with `require_history`. A run takes about 3 s per `--validate`.

**D-13 (WR-07).**
- The real-bytes tests already exist: `test_untouched_answers_copy_builds_through_real_paths` and `test_appended_answers_byte_removes_exemption_through_real_paths` (answers L134-150). They go through `build_from_files()` and the `--validate-answers` CLI.
- The fabricated-digest test `test_changed_answers_bytes_remove_exemption` (L121-125, `sha_text(read_text() + ' ')`) still exists. Rewrite it to use a real changed copy, or delete it and rely on the real-bytes pair.
- Add the decisions-side real-bytes test from GATE-08 (a), so the `--validate` path, not only build, is covered.

## GATE-10 Locator (planner question 7)

| Item | Location | What to do |
|---|---|---|
| IN-01 conditional "No decision changed" + reachable DIFFER | publisher `dry_run_summary` L568-571 | The lead clause becomes conditional on `same == 'equals' and not diff_ids and not set_differs`. Prove the DIFFER branch is reachable with a test that calls `dry_run_summary(tampered)` directly; `publish(True)` cannot reach it because `published_authority_checked` raises first. Assert "DIFFER" text and the absence of "No decision changed" |
| IN-02 restore the 2.0.0 constant check | test v2_publication `test_superseded_constants_match_git_history` L702-713 (uses its own literals) | Bind the literals to real constants: (1) exec the publisher blob at `31addfa` (pattern: reply tests' `frozen_publisher(commit)`, reply test L566-585) and assert its `SUPERSEDED_V2_0_0` equals the literal dict; (2) assert the 2.0.1 authority at `31addfa` has `source_lineage.supersedes` equal to it (verified to hold: `{authority_id …-2.0.0, commit 54a7fd0…, governance_decisions_sha256 4e746d1f…, relative_path, sha256 de36e227…, version 2.0.0}`); (3) chain: the 2.0.2 authority at `ae15c74` supersedes 2.0.1, and the new `SUPERSEDED_V2_0_2` names `ae15c74`. Rename to e.g. `test_2_0_0_anchor_matches_frozen_2_0_1_publisher_and_chain` |
| IN-03 dead `log` handling | test reply `fake_shallow_git` L342-353 (`log_sha` param and `log` branch), call sites L368, L376 | Remove `log_sha` and the `log` branch. Unknown commands already raise `AssertionError`, so the `not any(a[0]=='log')` assertions become implicit. Test-only, frozen builder untouched |
| IN-04 uneven `resolve_record_commit` errors | **reply builder** L341-353 | Wrap the `cat-file` and `merge-base` calls in `try/except OSError → AuthorityError`. Distinguish `merge-base` rc 1 ("is not an ancestor of HEAD", keep the exact text because the test at L383 matches it) from other non-zero codes ("cannot check ancestry … git merge-base exit {rc}"). Add tests: `mb_rc=128`, OSError raised on `cat-file` and on `merge-base`. The builder must not gain `importlib`, `V2`, publisher strings or `exec`/`eval` (scanner L708-728). The reply output does not depend on this function's messages, so `--validate` stays PASS |
| IN-06 D-08 tamper on a rule row | test v2_publication L1025-1033 (`a['controls'][0]` only) | Parametrise over `('EMS-CTRL-001', 'EMS-CTRL-030')` × the four tampers, select the row with `row(a, cid)`, and match `f'{cid}: decision content differs from'` (version-agnostic suffix). Verified safe: tamper funcs on a RULE_PUBLISHED row raise only `AuthorityError` |

The notice builder (`..._notice_2_0_2.py` L150-165) has the same uneven `resolve_record_commit` pattern. CONTEXT scopes IN-04 to the reply builder. See Open Question 2.

## CI Glob and Collect-Hook Scoping (planner question 8)

**Glob.** GitHub Actions runs `run:` with no `shell:` key on ubuntu as `bash -e {0}` [CITED: docs.github.com workflow-syntax, "defaults.run.shell" table]. An **unquoted** `tests/test_archive_assessment_*.py` expands in bash to the 12 modules, in sorted order. **Do not quote it.** A quoted glob reaches pytest literally, and pytest does not expand globs, so it stops with "file or directory not found" (exit 4). If nothing matches, bash passes the literal through and pytest fails closed. Recommended step:

```yaml
      - name: Archive-assessment tests
        env:
          EMS_FAIL_ON_SKIP: '1'
        run: python -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q
```

**Local PowerShell pitfall** [VERIFIED]: PowerShell does not glob arguments to native commands. `python -m pytest tests/test_archive_assessment_*.py` collects nothing and exits **4**. Run it locally with either:
- `python -m pytest (Get-ChildItem tests/test_archive_assessment_*.py).FullName …`, or
- the old `tests -k archive_assessment` form, which still works after D-10.

**Hook scoping** [VERIFIED: prototype under pytest 9.1.1]:
- Collectors reaching `pytest_make_collect_report` are `Dir` (nodeid `tests`) and `Module` (nodeid `tests/test_*.py`). Class collectors also reach it when present.
- A module-level `pytest.skip`/`importorskip` produces a skipped report on the `Module`.
- Scope by path, not nodeid. In the skip-guard subprocess, `--rootdir` changes the nodeid prefix:

```python
def _archive_module(collector) -> bool:
    p = getattr(collector, 'path', None)
    return p is not None and p.suffix == '.py' and p.name.startswith('test_archive_assessment_')
```

This covers `Module` and `Class`, and excludes `Dir`, `Package` and `Session`, whose paths are directories.

Prototype results:
- Non-archive module skip with `tests -k archive_assessment`: `1 passed, 1 skipped`, rc 0.
- Archive module skip: `ERROR … skipped module treated as failure`, `Interrupted`, rc 2.
- Explicit glob: rc 0.

**Skip-guard tests that break under scoping:** `test_module_importorskip_with_guard_fails` and `test_module_skip_with_guard_fails` write the skipping module as `test_case.py`, which is not an archive name. They would go red. Give `run_case` a module-name parameter and use `test_archive_assessment_case.py` for those two. Add the new D-10 case: a `test_other_skip.py` module-level skip next to `test_archive_assessment_ok.py`, guard on, `-k archive_assessment`. Assert rc 0, `1 passed`, and that `treated as failure` is absent.

A skip raised in `conftest.py` would no longer be converted. In that case nothing runs, pytest exits 5, and CI still fails. Acceptable, but record it in the plan.

**aa_history wording (D-11).** These tests constrain the text:
- `test_missing_history_fails_by_default` needs `'EMS_ALLOW_NO_HISTORY=1'` and `'fetch full history'` in the output.
- `test_require_history_fail_and_opt_out` uses the regex `MISSING.*fetch full history.*EMS_ALLOW_NO_HISTORY=1`, so the HINT must still mention the variable after "fetch full history".
- `test_history_problem_unrecognised_shallow_output_is_problem` with `b''`, `b'maybe'`, `b'true'` needs `'shallow'` and `'fetch full history'`.

Suggested text:
- HINT: `'run git fetch --unshallow; EMS_ALLOW_NO_HISTORY=1 only skips tests guarded by require_history, and tests that read pinned history directly still fail'`.
- Shallow branch: `out == 'true'` keeps "is a shallow repository". Any other output: `f'cannot tell whether {root} is shallow: git rev-parse --is-shallow-repository printed {out!r}{pinned}; fetch full history'`.
- Strengthen the parametrised test so it asserts `repr(out)` appears for `''` and `'maybe'`, and that "is a shallow repository" appears only for `'true'`.

## Architecture Patterns

### System Architecture Diagram

```
                ┌──────────────── CLI main() ────────────────┐
 argv ──────────┤ --validate            --validate --at-pin  │
                └─────┬──────────────────────────┬───────────┘
                      ▼                          ▼
          validate_published(at_pin=False)   validate_published(at_pin=True)
                      │  (shared core, same order)
   decisions gate ──► validate_governance_decisions (norm/norm_templated, D-13)
   load(checked) ───► AUTHORITY ─► SCHEMA (wrapped) ─► validate_publication ─► validate_lineage
                      ─► fresh-build equality ─► SIGNOFF ─► OUT file set + bytes ─► manifest artifacts
                      ─► script digest: lf_digest(SCRIPT) == manifest.publisher_script.sha256  (GATE-06/D-08)
                      │
            ┌─────────┴───────────┐
            ▼ plain                ▼ at-pin
   check_publication_record     check_publication_record(at_pin)
   record names CURRENT          record names a['source_lineage']['supersedes'] (D-02)
   git_show(pub, AUTH/MANIFEST)  git_show(sup.commit, AUTH/MANIFEST) digests == record
   D-06: is_ancestor(pub,HEAD)   D-04: not shallow; git status --porcelain -- D-05 paths empty
         blob(pub,p)==blob(HEADsha,p) for p in D-05
   D-07: lf(blob(pub, SCRIPT)) == manifest
   wrong record → error pointing to --at-pin
            ▼                       ▼
         print('PASS')          print(json {"status":"PASS","mode":"AT_PIN","deferred":[...1 item]})
                 all git access ──► git_show(commit,path) | git_run(*args)  (single subprocess seam)
```

### Pattern 1: One git seam (required by existing tests)
**What:** All `subprocess.run` calls live in two helpers: the existing `git_show`, kept byte-for-byte apart from an optional `--` (see Pitfall 4), and one new `git_run(*args) -> CompletedProcess` that raises `GitHistoryError` on `OSError`. Small typed helpers sit on top of `git_run`, for example:
- `git_head()`: `rev-parse HEAD`, validated as 40-hex;
- `git_is_ancestor(a, b)`: rc 0 → True, rc 1 → False, other → `GitHistoryError`;
- `git_not_shallow()`: output must be exactly `false`, and the message shows the raw output (IN-09 lesson);
- `git_dirty(paths)`.

**Why:** `test_module_does_not_call_git` (L93) and `test_publisher_source_runs_no_subprocess_or_evaluator` (L966) strip only `git_show` from the source and assert that `subprocess` appears nowhere else. Update `source_without_git_show()` in the same commit to strip `git_run` too, and assert `'subprocess.run'` is in `git_run`. The `env` fixture can then monkeypatch `git_head`, `git_is_ancestor`, `git_dirty` and `git_not_shallow` like it does `git_show`.

```python
def git_run(*args: str) -> subprocess.CompletedProcess:
    try: return subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    except OSError as e: raise GitHistoryError(f'git {args[0]}: git unavailable: {e}') from e
```

### Pattern 2: At-pin (PIN-01, D-01..D-04, D-08)
- `sup = a['source_lineage']['supersedes']`. It has already been validated equal to the constant by `validate_publication` and the schema.
- The record must have `authority_id`, `version`, `publication_commit` and `authority_sha256` equal to `sup`'s. Then the existing `git_show(record['publication_commit'], …)` digest cross-checks run. These are verified to hold for the 2.0.2 record against `ae15c74` blobs.
- D-04: `git_not_shallow()`, then `git status --porcelain -- <D-05 paths>` must print nothing.
- D-08: compare the live script digest with the manifest.
- Print `json.dumps({'status': 'PASS', 'mode': 'AT_PIN', 'deferred': [ONE_ITEM]})`.

The D-05 helper, defined once:

```python
def publication_paths() -> list[str]: return [rel(AUTHORITY), rel(SCHEMA), rel(SIGNOFF)] + [f'{rel(OUT)}/{n}' for n in (N_MATRIX, N_SEMANTIC, N_NEGATIVE, N_TRACE, N_CERT, N_REPORT, N_MANIFEST)]
```

Build the list from the N_* names, not `OUT.iterdir()`, so it is deterministic and 10 long. Have `test_publication_files_byte_identical_between_publication_and_record_commit` reuse it in place of its local `PUBLICATION_PATHS`.

### Pattern 3: Plain mode at record commit or later (PIN-02, D-06, D-07)
After the existing record checks:
- `git_not_shallow()`;
- `git_is_ancestor(pub, 'HEAD')`;
- `head = git_head()`;
- `for p in publication_paths(): git_show(pub, p) == git_show(head, p)`, comparing raw blobs, which are LF in the index, so CRLF in the working tree does not matter;
- `lf(git_show(pub, rel(SCRIPT))) == manifest sha`.

If the record names `sup` (meaning HEAD is the pin), raise an error that names `--validate --at-pin`.

### Pattern 4: Script digest (GATE-06)
Pass the manifest's `ps['sha256']` into the check. The live check runs in both modes, the pinned check in plain mode only. Remove `publisher_script_note` claims that contradict this? The `build_all_outputs` manifest text "is not recomputed on validation" (L615) becomes **false** after GATE-06. Changing it changes the manifest bytes, so it can only change in the move commit, where the outputs are re-certified in Phase 13 anyway. Do it there, and flag it for the Phase 14 notice.

### Anti-Patterns to Avoid
- **Passing `'HEAD'` to `git_show`:** it raises "commit must be a 40-character lowercase hex SHA". Resolve HEAD first.
- **`git status --porcelain` without explicit paths, or relying on it to see extra files in `OUT`:** `generated/` is in `.gitignore`. Untracked files there only show with `--ignored` (`!!`) [VERIFIED]. Extra files are already caught by the `OUT` file-set check. D-04 should pass the 10 explicit paths. Modified (` M`) and deleted (` D`) tracked files still show.
- **Changing mutation descriptions or `rejected_by` before the move commit:** this changes `N_NEGATIVE` and turns validator 1 red early.
- **Typing SUPERSEDED_V2_0_2 values by hand:** derive them with `git show ae15c74:…` and the record file in a one-off check, and assert them in a test against git.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Reading a blob at a commit | new subprocess calls | existing `git_show` (fails closed, validates the SHA and path) | Already tested for traversal, short SHAs, OSError |
| Executing a historical publisher for IN-02 | ad-hoc parsing of constants | the reply tests' `frozen_publisher(commit)` pattern (exec the blob into a module) | Established Phase 11 pattern |
| Shallow detection | inferring from `git log` | `git rev-parse --is-shallow-repository` == `'false'` exactly | Old git echoes the argument back (08 IN-02, 11 IN-09) |
| JSON loading with domain errors | try/except at every call | one checked loader like the builder's `load_checked` | Consistent messages |

## Common Pitfalls

### Pitfall 1: Source-scan tests forbid new subprocess calls
**What goes wrong:** D-04 and D-06 add `subprocess.run` outside `git_show`, and two tests fail.
**How to avoid:** Use Pattern 1, and update `source_without_git_show()` in the same commit.
**Warning signs:** `test_module_does_not_call_git` red.

### Pitfall 2: The env fixture has no git repo
**What goes wrong:** `env` sets ROOT to a `tempfile.TemporaryDirectory()` and fakes only `git_show`. Plain `validate_published()` will then fail on `merge-base` or `rev-parse`. These tests expect PASS:
- `test_publish_writes_all_and_is_byte_identical`
- `test_validate_published_calls_validate_lineage`
- `test_validate_record_matching_passes`
- `test_script_edit_after_publication_does_not_break_validate`: GATE-06 inverts it, so rewrite it to expect rejection.

The `test_pre_publication_*` tests must become at-pin tests. `test_unreachable_publication_commit_fails_closed` matches `'git show failed'`.

**How to avoid:**
- Extend `fake_git_show` and `register_blobs` to also serve the D-05 blobs and `scripts/pub.py` at `RECORD_COMMIT` and at a fake HEAD SHA.
- Fake `git_head`, `git_is_ancestor`, `git_not_shallow` and `git_dirty`.
- Keep `test_real_git_repo_record_passes_plain_mode` (real temp repo, HEAD == publication commit) as the real-git integration test. It already commits `scripts/pub.py`, so D-07 works there.
- Run D-06 after the existing `git_show` record cross-checks so the existing error matches hold.

### Pitfall 3: An extra file in `OUT` is invisible to `git status`
**What goes wrong:** `generated/` is gitignored, so `??` never appears. **How to avoid:** rely on the existing `OUT` file-set check, and do not claim D-04 detects extra files.

### Pitfall 4: Windows "Filename too long" in `git show <sha>:<long path>`
**What goes wrong:** In a checkout under a longer directory (83 characters was enough), `git show ae15c74:generated/archive-assessment/ems-aa3-v2/ems_aa3_v2_…manifest.json` fails with `fatal: failed to stat '…': Filename too long`. Git stats the argument to decide whether it is a revision or a path [VERIFIED in the scratch clone]. `--validate` and `--at-pin` then fail closed with `GitHistoryError`. Hayes could hit this.
**How to avoid:** Append `--` (`git show <sha>:<path> --`). This gives identical bytes (`9991228a…`) and still returns rc 128 for a missing object or path [VERIFIED]. Alternatively, `git -c core.longpaths=true`. Adding `--` changes `git_show`, which the source-scan tests reference by function, so that is fine. The frozen builders' tests compare their own `git_show` with **pinned** publisher blobs, so they are unaffected. The D-10 clone test must set `core.longpaths` either way.

### Pitfall 5: The PowerShell glob reaches pytest literally
See the CI section. Locally, use `(Get-ChildItem tests/test_archive_assessment_*.py).FullName`.

### Pitfall 6: D-08 says D-04 guarantees the script is unmodified, but D-05 excludes the script
The D-04 dirty check covers the 10 D-05 files. The discussion log shows "10 files + publisher script" was **not** selected. Integrity at the pin still holds, because the live-script digest must equal the manifest digest. The guarantee comes from that equality, not from D-04. See Open Question 1.

### Pitfall 7: Stale manifest note and dry-run gate line
`publisher_script_note` (L615) says the digest "is not recomputed on validation", and dry-run L576 names "pre-publication mode". After GATE-06 and the rename, both are false. Fix them in the move commit (manifest) and the IN-01 commit (dry run).

## Code Examples

### Schema-first, wrapped (GATE-07)
```python
def load_checked(p: Path) -> object:
    try: return json.loads(p.read_text(encoding='utf-8'))
    except (OSError, ValueError) as e: raise AuthorityError(f'{rel(p)}: cannot be read as JSON: {e}') from e

def schema_check(doc: object, schema_doc: object, what: str) -> None:
    try: jsonschema.Draft202012Validator.check_schema(schema_doc); jsonschema.Draft202012Validator(schema_doc).validate(doc)
    except jsonschema.SchemaError as e: raise AuthorityError(f'{what}: committed schema is invalid: {e.message}') from e
    except jsonschema.ValidationError as e: raise AuthorityError(f'{what} fails the schema: {e.message}') from e
```
Note: `rel(p)` raises `ValueError` for paths outside ROOT. Use `p.name` in the message if the loader may get such paths.

### Version-agnostic messages (09 D-07 pattern)
```python
sup = SUPERSEDED_V2_0_2
for cid in diff_ids: errors.append(f"{cid}: decision content differs from {sup['version']}")
```

## State of the Art

| Old | Current (after Phase 12) | Impact |
|---|---|---|
| `--validate --pre-publication` hard-coded to `SUPERSEDED_V2_0_1` | `--validate --at-pin`, superseded identity read from `source_lineage.supersedes` | Survives future republications without code edits |
| Script digest checked only by pytest | Checked by `--validate` (live + pinned) | CI validator 1 red on any uncertified publisher edit |
| CI `pytest tests -k archive_assessment` | `pytest tests/test_archive_assessment_*.py` | Unrelated module skips no longer abort the gate |

## Recommended Commit Split (planner question 9)

| # | Commit | Paths (explicit) | Red set after commit |
|---|---|---|---|
| 1 | D-09/D-10/D-11: CI glob, scoped collect hook, skip-guard cases (rename the two module cases, add the deselected non-archive case), aa_history HINT and shallow message plus tests | `.github/workflows/ems-validate.yml`, `tests/conftest.py`, `tests/aa_history.py`, `tests/test_archive_assessment_skip_guard.py` | none |
| 2 | Test-only: GATE-09 (D-10 `--validate` outcome-unchanged clone test; D-13 fabricated test → real bytes), GATE-08 CLI-path real-bytes tests, GATE-10 IN-02, IN-03, IN-06 | `tests/test_archive_assessment_lineage_validation.py`, `tests/test_archive_assessment_governance_answers.py`, `tests/test_archive_assessment_governance_decisions.py`, `tests/test_archive_assessment_applicability_authority_v2_publication.py`, `tests/test_archive_assessment_demo3_w1_req_001_reply.py` | none |
| 3 | GATE-10 IN-04 (frozen reply builder) plus tests | `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, `tests/test_archive_assessment_demo3_w1_req_001_reply.py` | none (verify reply `--validate` PASS and all reply freeze tests) |
| 4 | **Window opens.** GATE-07 (checked loader, schema-first wrapped, manifest/lineage guards, new malformed-shape tests) + IN-01 dry-run text + git seam refactor (Pattern 1, with the source-scan tests updated) + optional `--` in `git_show` | publisher + v2_publication tests | `test_publisher_still_valid_and_digest_matches_manifest` |
| 5a | PIN-01/PIN-02: rename to `--at-pin` (D-01), D-02, D-03, D-04, D-05 helper, D-06 + env-fixture fakes | publisher + v2_publication tests | unchanged (D-06 green at HEAD) |
| 5b | GATE-06 (D-07/D-08) + tests; rewrite `test_script_edit_after_publication_does_not_break_validate` to expect rejection | publisher + v2_publication tests | + `test_real_published_files_validate`, + **CI validator 1** |
| 6 | Supersedes move: `SUPERSEDED_V2_0_2`, `VERSION='2.0.3'`, version-agnostic messages, mutation description, manifest note; update every `SUPERSEDED_V2_0_1` reference and literal test | publisher + `tests/test_archive_assessment_applicability_authority_v2.py`, v2_publication, lineage, normalisation_claims | + `test_committed_schema_equals_schema_function` |

Commit 5a and 5b can merge if the planner prefers fewer commits. Keeping them apart shows D-06 passing against real history while CI is still green. Do **not** run `--emit-schema`, `--publish` or `--record-publication`, and do not edit `registry/`, `schemas/` or `generated/`. That is Phase 13.

## Runtime State Inventory

The supersedes move is a rename and refactor inside code only.

| Category | Items Found | Action |
|---|---|---|
| Stored data | Committed authority, schema, sign-off, `generated/…/ems-aa3-v2/*`, record: all still 2.0.2 and **must not change in Phase 12** | none (Phase 13 regenerates) |
| Live service config | None. GitHub Actions has only the workflow file in git | code edit (commit 1) |
| OS-registered state | None. Verified: no scheduled tasks or services involved | none |
| Secrets/env vars | `EMS_FAIL_ON_SKIP`, `EMS_ALLOW_NO_HISTORY`: names unchanged | none |
| Build artifacts | None. `.pytest-*` dirs are untracked and local | none |

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| Python venv | all | ✓ | 3.12.10 | — |
| pytest | tests | ✓ | 9.1.1 | — |
| git (full history) | D-04/D-06/D-07, history tests | ✓ (not shallow) | 2.54.0.windows.1 | none: fails closed by design |
| `core.longpaths` | deep checkouts only | not set globally | — | `git show … --` (Pitfall 4) |

## Security Domain

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2/V3 Authentication, Session | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | JSON Schema first, then Python validators; every malformed shape → `AuthorityError` (GATE-07); `bad_rel` and 40-hex SHA checks before any `git` call |
| V6 Cryptography | yes (integrity) | `hashlib.sha256` over LF-normalised bytes; never hand-roll |
| V10/V14 Integrity of code/config | yes | GATE-06 binds the publisher script to the certified digest; D-06 blob identity |

| Threat | STRIDE | Mitigation |
|---|---|---|
| Option injection through a commit or path argument to git | Tampering | Existing `git_show` regex and `bad_rel`; new helpers must validate SHAs the same way (record SHA regex) before `merge-base` |
| Uncertified publisher edit passes CI | Tampering | GATE-06 live + pinned digest |
| Shallow clone or missing history yields false PASS | Repudiation | `--is-shallow-repository` must be exactly `false`; all git failures → `GitHistoryError` |
| Skip silently hides archive tests | Repudiation | Scoped collect hook + runtest hook; pytest exit 5 when nothing runs |
| Dirty tree at the pin certifies the wrong bytes | Tampering | D-04 porcelain check + LF-digest and fresh-build equality |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Hayes may run verification on Windows in a deep directory, so the long-path risk is real for PIN-01 | Pitfall 4 | Low. Fails closed either way; adding `--` is cheap |
| A2 | A `pytest.skip` inside `conftest.py` produces "no tests ran" (exit 5) under the scoped hook | CI section | Low. CI still fails |

## Open Questions (RESOLVED)

1. **Should the at-pin dirty check also cover the publisher script?**
   - Known: D-08 says "D-04 guarantees it is unmodified", but D-05 (and so D-04) excludes the script, and "10 files + script" was rejected for D-05.
   - Recommendation: keep D-05 at 10 files. The live-digest == manifest check is the guarantee. Optionally pass `[*publication_paths(), rel(SCRIPT)]` to the at-pin dirty check only. The planner or user should confirm the reading.
   - RESOLVED: CONTEXT D-12 (the at-pin dirty check covers the 10 D-05 paths plus the publisher script; the D-05 byte-identity set for plain --validate stays at 10 files).
2. **IN-04 "everywhere": reply only, or the notice builder too?**
   - Known: CONTEXT names reply L341 only. The notice builder has the identical pattern, and its polish items are deferred.
   - Recommendation: reply only, as scoped. Note the notice for after 2.0.3.
   - RESOLVED: CONTEXT D-13 (IN-04 is fixed in the reply builder only; the same pattern in the frozen 2.0.2 notice builder is deferred).
3. **Fixed gate line in the dry run, and the manifest `publisher_script_note`.** The wording is the planner's choice. The Phase 14 notice may quote the dry run, so name GATE-06..10 and `--at-pin` plainly.
   - RESOLVED: CONTEXT D-14 (the dry-run gate line and manifest publisher_script_note must be true after GATE-06 and the --at-pin rename; wording is the planner's choice).
4. **A fresh Windows clone fails `test_committed_notice_files_validate`,** because the notice files have no `eol=lf` in `.gitattributes`. This is outside Phase 12 scope and affects only local fresh clones. Record it as tech debt. Adding `eol=lf` lines for the three notice files would fix it, but it touches `.gitattributes`, so it needs a decision.
   - RESOLVED: CONTEXT D-15 (marking the notice files eol=lf in .gitattributes is out of scope and deferred).

## Validation Architecture

Skipped: `workflow.nyquist_validation` is `false` in `.planning/config.json`. For per-commit verification:
- Use `.venv/Scripts/python.exe -m pytest (Get-ChildItem tests/test_archive_assessment_*.py).FullName -p no:cacheprovider -q -rf --basetemp=.pytest-temp/<fresh>` with `EMS_FAIL_ON_SKIP=1`.
- Run the 6 validators.
- Compare against the red-set table, recorded in `12-BASELINE-RED.md`.
- The full suite takes about 5 minutes.

## Sources

### Primary (HIGH confidence)
- Codebase: the publisher (all 776 lines), decisions builder, reply/notice builders, `tests/conftest.py`, `tests/aa_history.py`, skip-guard, v2_publication, lineage, answers, decisions tests (read in full or in the relevant ranges).
- Measurements in the scratch clone: `redset.out` (3 stages), `probe_gate07.out`, GATE-08 real-bytes probe, hook prototype, PowerShell glob test, `git show --` / long-path test.
- `.planning`: 08-REVIEW, 08-REVIEW-FIX, 09-REVIEW, 11-REVIEW, 08/09/12 CONTEXT, 12-DISCUSSION-LOG, 09-BASELINE-RED, v1.1.0 audit, STATE, PROJECT.
- GitHub Docs, workflow syntax `defaults.run.shell` table: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

## Metadata

**Confidence breakdown:**
- Red-window inventory: HIGH. Measured, with one environmental red identified and explained.
- GATE-07..10 residuals: HIGH. Probed.
- PIN-01/PIN-02 design: HIGH for feasibility (record digests and blobs verified). The exact error wording is MEDIUM and left to the planner.
- CI glob and hook: HIGH. Official docs plus prototype.

**Research date:** 2026-11-16
**Valid until:** the first publisher commit of Phase 12 (the red-set baseline moves with every commit).
