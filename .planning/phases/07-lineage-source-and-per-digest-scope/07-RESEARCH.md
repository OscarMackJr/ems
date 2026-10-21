# Phase 7: Lineage Source and Per-Digest Scope - Research

**Researched:** 2026-10-20
**Domain:** Python publisher/validator refactor (AA3 v2 authority `source_lineage`), git blob recomputation, `.gitattributes` byte protection
**Confidence:** HIGH on code facts (read directly); MEDIUM on facts that need a command run (listed in "Facts the orchestrator must confirm")

Method note: Bash and PowerShell were unavailable, so nothing was executed. Every code fact below is from Read/Grep with file:line references `[VERIFIED: codebase grep]`. Facts that depend on git history or on file bytes are marked `[ASSUMED]` and have an exact confirmation command in the section "Facts the orchestrator must confirm".

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Each lineage digest becomes an object: `{relative_path, sha256, normalisation}`, plus `commit` where the digest is pinned to a commit. The flat `aa1_manifest_sha256` / `aa2_closure_sha256` / `aa2_approval_sha256` keys are replaced by objects (for example `aa1_manifest`, `aa2_closure`, `aa2_approval`; the planner picks the exact key names). This is a deliberate breaking shape change in a new version, 2.0.2. The Phase 10 notice must describe it.
- **D-02:** The global `source_lineage.digest_normalisation` field is removed. Nothing in the lineage may state a scope that contradicts a digest.
- **D-03:** Every digest in the lineage carries an explicit `normalisation`. This includes the nested `governance_decisions`, `supersedes`, `v1_baseline` and `catalog_reference` entries. The validator treats all of them uniformly.
- **D-04:** The normalisation vocabulary is a closed enum, `RAW_BYTES | CRLF_TO_LF`, enforced by the generated schema (fail closed).
- **D-05:** The file is `generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json`, which already exists at this path and is gitignored. Verified 2026-10-20: raw-byte SHA-256 = `f0da8e2e45c306ccc42ae96f25a19922668f3eedecdb26006f13514e24ad9b4b` (exact match). It has 87 CRLF line endings, and its LF-normalised digest would be `06e39f7b...`. It is committed in place with `git add -f`, in a commit of its own that stages only that file and `.gitattributes`.
- **D-06:** Add `.gitattributes` rule `generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json -text` (file-specific, like `ems-aa2/approval/** -text`) so git never converts its CRLF bytes.
- **D-07:** If the committed file's raw-byte hash read back from a fresh checkout does not equal `f0da8e2e...`, stop and do not commit. Never change the recorded digest to fit the file.
- **D-08:** Commit the manifest only. The 13 AA1 artifacts the manifest lists stay untracked. Lineage cites only the manifest's hash.
- **D-09:** Lineage recomputation is a new `validate_lineage(...)` inside `scripts/publish_archive_assessment_applicability_authority_v2.py`, called from the existing `--validate` path. CI already runs that path. No separate script.
- **D-10:** Digests that carry a `commit` (`supersedes`, `v1_baseline`) are recomputed from `git show <commit>:<relative_path>`. All other digests are recomputed from the checked-out file. The declared normalisation is applied in both cases.
- **D-11:** If git history is unavailable for a commit-pinned digest, validation fails closed. Unlike the frozen-catalog behaviour of 06 D-03, it never passes silently. The CI `archive-assessment` job already checks out with `fetch-depth: 0`.
- **D-12:** Negative tests: a changed byte in a cited file, a changed declared normalisation, and a changed recorded digest each make `validate_lineage` fail. Tests cover both `RAW_BYTES` and `CRLF_TO_LF` entries.
- **D-13:** Audit every other `digest_normalisation` claim (publication record, certification, publication manifest, `decision_record_digest_normalisation` in the traceability, and the record and pin fields the reply builder reads). For each claim, add a pytest that recomputes the digest and proves the claim. Change the shape only where a claim is false. Expected result: these claims are genuinely LF and stay as they are.
- **D-14:** Do not touch the DEMO3 reply, its builder or its schema in Phase 7. Its two digests really are LF, and it is a sent 2.0.1 artifact. Hayes learns of 2.0.2 through the Phase 10 notice.

### Claude's Discretion
- Exact object key names in `source_lineage` and the structure of the `validate_lineage` helper, matching the publisher's compact style.
- How the `lf_digest` / raw `digest` helpers are selected by normalisation, for example a small mapping `{'RAW_BYTES': raw, 'CRLF_TO_LF': lf}`.

### Deferred Ideas (OUT OF SCOPE)
- Committing the 13 AA1 analysis artifacts the manifest lists.
- Re-pointing the DEMO3 reply to 2.0.2.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LIN-01 | Each `source_lineage` digest declares its own normalisation; no global field contradicts any digest | Digest inventory table (Q1), new lineage shape, schema generation (`schema()` v2.py:301-308) |
| LIN-02 | Each digest recomputable from a cited path (and commit); validator fails on mismatch | `validate_lineage` design, `git_show` helper, hook point in `validate_published` (v2.py:599), negative tests incl. CRLF-file pitfall |
| LIN-03 | AA1 manifest committed, `-text`, raw sha equals `f0da8e2e...` | `.gitattributes` + `git add -f` procedure, verification commands, ignore rules |
</phase_requirements>

## Summary

The v2 publisher (`scripts/publish_archive_assessment_applicability_authority_v2.py`, ~646 lines, compact one-line style) builds `source_lineage` in `build_authority()` (lines 151-157) and `build_published_authority()` (line 182), validates it in `validate_authority()` (218-221) and `validate_publication()` (258-290), generates its schema in `schema()` (301-308) and asserts nothing about the three AA digests anywhere except a 64-hex pattern. The three AA digests are not computed in v2 at all: they are copied from the v1 authority JSON (v2.py:120, 152), where v1 computed AA2 digests with raw `digest()` (v1 script line 78) and hard-coded the AA1 manifest digest. So the 2.0.1 global `digest_normalisation: CRLF_TO_LF` is false for exactly those three, true for all the others. Verified directly: the AA2 approval/closure files contain CRLF line endings (grep counts 122 and 24 lines with `\r`), so raw and LF digests differ for them.

Three non-obvious collisions will bite the plan if not handled:
1. Two existing tests ban the word `subprocess` from the publisher source (`tests/..._v2_publication.py:80-82` and `:676-678`). D-10 needs `git show`. Those two tests must be deliberately narrowed.
2. `test_v2_builder_does_not_use_generated_dir` (`tests/..._v2.py:165-168`) asserts the source of `build_authority` + `build_published_authority` contains none of `generated`, `OUT`, `ems-aa2`, `'ems-aa3'`, `AA2 / `. So lineage paths must be module-level constants referenced by name, and the builders must keep copying digest values from the v1 authority rather than reading `generated/`.
3. The reply builder (must not change, D-14) reads `source_lineage.supersedes.{authority_id,version,commit,governance_decisions_sha256}` (reply script :76-82; test :350-356) and `governance_decisions_build` reads `source_lineage.governance_decisions.sha256` (`build_archive_assessment_governance_decisions.py:367`). Those key names must survive the reshape.

**Primary recommendation:** Add module-level path/normalisation constants and a `digest_entry()` helper; reshape lineage into per-digest objects while keeping the existing key names the reply builder and decisions builder read; add `git_show()` + `validate_lineage()` in the publisher, hooked into `validate_published()` (not into `validate_publication`, so mutation gates stay hermetic); do not regenerate any committed output in Phase 7 (the committed schema and authority stay at 2.0.1 and the real-file tests go red until Phase 9).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Lineage shape + normalisation vocabulary | Publisher script (`schema()`, `build_*`) | Generated schema file (derived, not hand-edited) | Schema is generated by the publisher (CONTEXT canonical refs) |
| Lineage recomputation | Publisher `validate_lineage` (`--validate`) | CI `archive-assessment` job | D-09; CI already runs `--validate` (ems-validate.yml:92) |
| AA1 manifest byte preservation | `.gitattributes` `-text` | `git add -f` past `.gitignore` `generated/` | D-05/D-06 |
| Git history access | `git_show` helper (subprocess, list args, no shell) | Test fixture temp repo | D-10/D-11 |
| Normalisation-claim audit (D-13) | pytest | — | Tests only; code shape unchanged where claims are true |

## Q1. Source and true normalisation of every digest in `source_lineage` (2.0.1)

| Lineage key (2.0.1) | Where set | Where the value comes from | True normalisation | Current claim |
|---|---|---|---|---|
| `aa1_manifest_sha256` | v2.py:152 | Copied from `load(V1_AUTHORITY)['source_lineage']` (v2.py:119-120). v1 hard-codes the constant `f0da8e2e...` (v1 script line 78) | RAW_BYTES (raw hex matches file per D-05; LF digest would be `06e39f7b...`) | global `CRLF_TO_LF` (FALSE) |
| `aa2_closure_sha256` | v2.py:152 | Copied from v1; v1 = `digest(AA2 / '..._governance_closure.json')` raw (v1 line 78) | RAW_BYTES (file has CRLF: 24 lines contain `\r`) | FALSE |
| `aa2_approval_sha256` | v2.py:152 | Copied from v1; v1 = `digest(AA2 / '..._governance_approval.json')` raw | RAW_BYTES (122 CRLF lines) | FALSE |
| `catalog_reference.sha256` | v2.py:153 | `lf_digest(CATALOG)` (computed live) | CRLF_TO_LF | true |
| `supersedes.sha256` | const `SUPERSEDED_V2_0_0` v2.py:36-41 | Hard-coded literal; proved by test against `git show 54a7fd0:registry/archive_assessment_applicability_authority_v2.json` with `lf_sha` (tests v2_publication.py:538-542) | CRLF_TO_LF | true |
| `supersedes.governance_decisions_sha256` | same const | Hard-coded; proved against `git show 54a7fd0:registry/archive_assessment_governance_decisions.json` with `lf_sha` (tests :539,542) | CRLF_TO_LF | true |
| `v1_baseline.sha256` | `v1_baseline_entry()` v2.py:114-115 | `lf_digest(V1_AUTHORITY)` of the LIVE v1 file (not of the blob at `V1_BASELINE_COMMIT`) | CRLF_TO_LF | true (but see confirm item C4) |
| `governance_decisions.sha256` | `build_published_authority` v2.py:182 | `lf_digest(GOVERNANCE_DECISIONS)` | CRLF_TO_LF (the file is also `text eol=lf` in .gitattributes:2, so raw == LF) | true |

Notes for the plan:
- `supersedes` holds TWO digests (`sha256` for the 2.0.0 authority file, `governance_decisions_sha256` for the 2.0.0 decisions file). The second has no path of its own. For D-03 each needs its own normalisation and (for recompute) a path. Both live at the same `commit` 54a7fd0. The decisions path is `registry/archive_assessment_governance_decisions.json` (tests :539 proves the blob exists at 54a7fd0).
- `drafting_commit` and `record_count` in `governance_decisions` are not digests; leave them.
- Only blob-vs-working-file differences matter for `v1_baseline`. Existing code never checks the blob at `V1_BASELINE_COMMIT`; see C4.

## Q2. Every place that reads or asserts the lineage shape

**Publisher (v2.py)**
- `build_authority` 151-157 (builds 2.0.1 shape, reads v1 lineage 119-120); `build_published_authority` 182 (adds `governance_decisions`).
- `validate_authority` 218-221 (`sup != SUPERSEDED_V2_0_0`; `v1b` minus `sha256` must equal `v1_baseline_entry()` minus `sha256`). If `SUPERSEDED_V2_0_0` / `v1_baseline_entry()` gain a `normalisation` key, both checks follow automatically.
- `validate_publication` 258-290 (`governance_decisions` fields 259-267; `supersedes` 287; `v1_baseline == v1_baseline_entry()` 288 which compares the live v1 digest too; `catalog_reference` 289-290).
- `schema()` 301-308: `required` list names `digest_normalisation`, `aa1_manifest_sha256`, `aa2_closure_sha256`, `aa2_approval_sha256`; `pinned()` helper 298-300 makes every non-sha key a `const`. Needs: object schemas per digest with `normalisation: {'enum': ['RAW_BYTES','CRLF_TO_LF']}`.
- Mutation harness `_m_wrong_v1` 375, `_gd` 368, mutations at 398-401, 411 touch `governance_decisions`, `v1_baseline`, `supersedes.governance_decisions_sha256` only; none touches the three AA keys or `digest_normalisation`, so the harness does not need edits for the reshape provided those key names survive. The harness pins 26 mutations (tests `:609-611`, `:673`).
- `dry_run_summary` 455-465 reads `sup['governance_decisions_sha256']`, `sup['commit']`, `sup['authority_id']`, `sup['version']` and prints "Digest normalisation: CRLF_TO_LF" at 463 (a global-looking statement about the authority's own LF sha; it describes `sha_text(jtext(authority))`, which is true; consider rewording to "Authority sha256 normalisation" only if the plan wants to avoid the word global; not required).
- Certification / manifest / traceability builders (`build_all_outputs` 468-506): they do NOT read `source_lineage`. They hold their own `digest_normalisation` claims (see Q5).
- `validate_published` 599-627 is the `--validate` path; `main` 636-645.

**Other scripts**
- Reply builder `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`: reads `authority['source_lineage']['supersedes']` at :76; uses `sup['governance_decisions_sha256']` (:77) and `sup['authority_id'/'version'/'commit']` (:82). It does NOT read the three AA keys, `digest_normalisation`, `v1_baseline` or `catalog_reference`. `PIN_KEYS` / `pin.digest_normalisation` (:28, :87, :197) come from the publication record, not the lineage. It is safe provided `supersedes` keeps those four flat key names. Its CI step `--validate` (ems-validate.yml:96) reads the committed (2.0.1) authority and so stays green until Phase 9 republication, at which point the reply rebuild (`pin` version `2.0.1` asserted by test :360) will differ. That is Phase 9/10 territory (D-14); note only.
- `scripts/build_archive_assessment_governance_decisions.py:367` `is_published()` reads `source_lineage.governance_decisions.sha256`. Keep key `sha256` inside the `governance_decisions` entry.
- `scripts/publish_archive_assessment_applicability_authority.py` (v1, line 78, 126): untouched; its `aa1_manifest_sha256` stays flat.

**Tests**
- `tests/test_archive_assessment_applicability_authority_v2.py`: :31-33 `with_decisions_lineage` (synthetic governance_decisions dict with 4 keys; schema will require `normalisation` too -> update); :105 absolute path under `source_lineage.bad_path`; :143-146 required keys list (replace names; add check that `digest_normalisation` is now rejected as extra); :148-153 pin checks (still valid if supersedes keeps pinned consts); :155-160; :164 `test_committed_schema_equals_schema_function` (RED until Phase 9 regenerates the committed schema); :165-168 hermeticity test (constraint above).
- `tests/test_archive_assessment_applicability_authority_v2_publication.py`: :67-78 lineage test (line 78 asserts `lin['digest_normalisation'] == 'CRLF_TO_LF'` -> replace with per-digest assertions); :73 `lin['supersedes'] == MODULE.SUPERSEDED_V2_0_0` (fine); :80-82 and :676-678 `subprocess` bans (see Pitfall 1); :128-143 mutation checks on governance_decisions/v1/supersedes (keep valid); :155,168 build `governance_decisions.sha256`; :227-228, :416-417 claim assertions (keep; they are true); :538-558 `test_superseded_constants_match_git_history` (keep) and `test_rows_equal_2_0_0_rows...` where :558 asserts the diff of old vs new `source_lineage` keys equals `{'supersedes','v1_baseline'}` -> will go red; must be rewritten (old 2.0.0 lineage is the flat shape, new differs in most keys; assert the controls equality and `differing <= {'authority_id','version','source_lineage'}` only, and instead assert digest VALUES are carried over: new `aa1_manifest.sha256 == old['aa1_manifest_sha256']`, etc.); :560-561 version stays 2.0.1 in Phase 7 (do NOT bump `VERSION`, that is Phase 9); :609-611 / :673 mutation count 26 (unchanged unless mutations are added).
- `tests/test_archive_assessment_demo3_w1_req_001_reply.py:348-361` reads `supersedes` flat keys from the COMMITTED authority; unaffected in Phase 7.
- `tests/test_archive_assessment_governance_decisions.py:468` writes `{'source_lineage': {'governance_decisions': {'sha256': digest}}}`; unaffected if key `sha256` is kept.
- `tests/test_archive_assessment_applicability_authority.py:31`: v1 test, unaffected.

**CI**: `.github/workflows/ems-validate.yml` job `archive-assessment` (lines 70-96): `fetch-depth: 0` (:75), `pytest tests -k archive_assessment` (:88), then the five validator commands incl. `publish_..._v2.py --validate` (:92) and the reply `--validate` (:96). No workflow edit is needed for LIN-02. (D-11 satisfied by `fetch-depth: 0`.)

## Q3. `SUPERSEDED_V2_0_0`, `supersedes`, `v1_baseline_entry`, and 2.0.1's "supersedes 2.0.0"

- `SUPERSEDED_V2_0_0` (v2.py:36-41) = `{authority_id (...-2.0.0), version '2.0.0', commit '54a7fd09114704a97a7a48fce5f89aebeb48c90a' (40-hex), relative_path 'registry/archive_assessment_applicability_authority_v2.json', sha256 'de36e227...', governance_decisions_sha256 '4e746d1f...'}`. It carries a full commit. `build_authority` embeds `dict(SUPERSEDED_V2_0_0)` (v2.py:154); `validate_authority` and `validate_publication` require equality with the constant; `schema()` pins every key as `const` except the two sha keys (pattern).
- `v1_baseline_entry()` (v2.py:114-115) = `{authority_id, version '1.0.0', commit V1_BASELINE_COMMIT '62a8955d...', relative_path V1_BASELINE_REL, sha256 lf_digest(live V1 file)}`. It carries a full commit.
- Representation of "2.0.1 supersedes 2.0.0": exactly this `supersedes` object. Phase 9 will replace the constant with the 2.0.1 identity at `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb` (note only; do not plan).
- Recommended Phase 7 shape (keeps reply-builder keys): add `'normalisation': 'CRLF_TO_LF'` (applies to `sha256`), `'governance_decisions_relative_path': 'registry/archive_assessment_governance_decisions.json'` and `'governance_decisions_normalisation': 'CRLF_TO_LF'`, keeping the flat `governance_decisions_sha256`. For `v1_baseline` add `'normalisation': 'CRLF_TO_LF'`. Because the schema's `pinned()` makes non-sha keys `const`, the extra keys flow through with no extra code except adding them to the constants (and putting `normalisation` in the pinned dict; make the enum check explicit for uniformity, see Pattern 1).
  - Alternative (cleaner but breaks the reply builder): nest `supersedes.governance_decisions = {relative_path, sha256, normalisation}`. REJECTED because D-14 forbids touching the reply builder, and it reads `sup['governance_decisions_sha256']` (:77).

## Q4. The `--validate` flow and git invocation patterns

`--validate` -> `validate_published()` (v2.py:599-627):
`validate_governance_decisions()` -> load authority -> `validate_publication(a)` + jsonschema against the COMMITTED schema file -> `a != build_published_authority()` (604) -> canonical bytes check (605) -> sign-off -> manifest/outputs rebuild -> manifest artifact digests (618-621) -> publication record cross-check (622-626) -> `print('PASS')`.

Hook point: call `validate_lineage(a['source_lineage'])` right after `validate_publication(a)` at line 603 (before the fresh-build comparison, so lineage errors report their own message). Do NOT put it inside `validate_publication`: `mutation_gates` (v2.py:528-533) calls `validate_publication` on 26 mutated copies, and `build_all_outputs` runs all mutations; adding git/disk IO there slows it and couples the harness to repo history. Also call it from `published_authority_checked()` (581-585)? Not needed in Phase 7; if added, `--publish --dry-run` would also verify lineage (good for Phase 9) but it requires the AA1/AA2 files and git on the machine; recommended to add in Phase 9, not now.

Git invocation patterns already in repo (reuse the shape, bytes mode):
- `tests/..._v2_publication.py:480-482`: `subprocess.run(['git', *args], cwd=ROOT, capture_output=True)`, returns bytes, and `git_ready()` :484-489 skips on shallow repo.
- Reply builder :258-259: `subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)` (text mode: NOT suitable for blob bytes).
- Frozen-catalog check from 06 D-03 is NOT in the publisher; `rg` found no subprocess in v2.py (consistent with the tests' ban). Do not copy its "pass silently" behaviour (D-11).

Recommended helper (bytes, list args, no shell, validated inputs):
```python
def git_show(commit: str, relative_path: str) -> bytes:
    if not re.fullmatch(r'[0-9a-f]{40}', commit or '') or contains_absolute(relative_path) or '..' in relative_path.split('/'): raise AuthorityError(f'{relative_path}: invalid commit or path for git show')
    try: r = subprocess.run(['git', 'show', f'{commit}:{relative_path}'], cwd=ROOT, capture_output=True)
    except OSError as e: raise AuthorityError(f'git is unavailable for {relative_path}@{commit[:7]}: {e}') from e
    if r.returncode != 0: raise AuthorityError(f'{relative_path}@{commit[:7]}: git history unavailable (shallow clone or unknown commit): {r.stderr.decode("utf-8", "replace").strip()}')
    return r.stdout
```
`git show <rev>:<path>` prints the stored blob bytes (no smudge/eol conversion), which is what we need. Require the full 40-hex commit (schema already pins `commit` as const for both entries; `abcdef0` short forms are rejected by existing tests, :141-142 / v2 test :150-151).

## Q5. D-13 sweep: every other normalisation claim

| Claim | Where produced | Helper | True? | Test to add (recompute) |
|---|---|---|---|---|
| Publication record `digest_normalisation: CRLF_TO_LF` | `write_publication_record` v2.py:632; fields `authority_sha256 = lf_digest(AUTHORITY)`, `manifest_sha256 = lf_digest(OUT/N_MANIFEST)` | `lf_digest` | TRUE | Real-file test: load `PUBLICATION_RECORD`, assert both digests equal `lf_digest` of the file AND equal sha256 of `git show <publication_commit>:path` LF-normalised (existing test :511 does the git part; add an explicit claim test that also asserts the RAW digest equals LF digest or differs, documenting which). Skip when record absent. |
| Certification `digest_normalisation` + `authority_sha256` (`ash = sha_text(jtext(authority))`), `schema_sha256` (`lf_digest(SCHEMA)`), `signoff_sha256` (`lf_digest(SIGNOFF)`) | build_all_outputs v2.py:471-473, 494 | `sha_text` of canonical LF text; `lf_digest` | TRUE | Recompute from the committed files in `generated/archive-assessment/ems-aa3-v2/` and registry; assert equality and the claim string. |
| Manifest `digest_normalisation`, artifacts[].sha256 (`lf_digest` for schema/authority/signoff; `sha_text(t)` for the six generated outputs), `publisher_script.sha256` (`lf_digest(SCRIPT)`) + `sha256_normalisation` | v2.py:501-504 | same | TRUE (validated at 618-621 for artifacts; script digest by design not re-checked, D-09 / WR-01 out of scope) | Recompute every artifact entry with LF normalisation from disk. For `publisher_script`: existing test :534/:518-526 already proves it against `git show <publication_commit>:scripts/...`; reference it, do not duplicate. |
| Traceability `decision_record_digest_normalisation` and `decision_record_sha256` | v2.py:488,492 | `lf_digest(GOVERNANCE_DECISIONS)` | TRUE | Recompute for every `decision_records[*]`. |
| Sign-off `authority_sha256_normalisation` | `validate_signoff` v2.py:445 | compared with `authority_lf_digest` | TRUE | Real signoff file: recompute `lf_digest(AUTHORITY)`. |
| Reply `pin.digest_normalisation` and text "both digests are computed over bytes with CRLF replaced by LF" | reply builder :87, :145, :197 | value copied from the record | TRUE (record uses `lf_digest`) | Reply test file already binds pin to record; add one test asserting `pin.authority_sha256 == lf_digest(AUTHORITY)` and `pin.manifest_sha256 == lf_digest(manifest)` from the committed reply JSON. Do not edit the reply, its builder, or its schema (D-14); a new test in the existing reply test file or the v2 publication test file only. |
| Dry-run summary "Digest normalisation: CRLF_TO_LF" and report line (v2.py:463, 499) | prints `sha_text(jtext(authority))` | `sha_text` | TRUE (LF text) | Covered by existing summary tests; no new test needed. |

Why the claims hold even on a Windows checkout: `.gitattributes:6,8,9,15-18` mark the authority, record, schema, signoff and `generated/archive-assessment/ems-aa3-v2/**` as `text eol=lf`, and every comparison goes through `lf_bytes`/`lf_digest`, so CRLF working-tree conversion cannot change them. Expected result per D-13: no shape change.

## Q6. Red window and dry/out-dir mode

- The publisher has NO out-dir option. `OUT`, `AUTHORITY`, `SCHEMA`, `SIGNOFF`, `PUBLICATION_RECORD`, `SCRIPT` are module constants (v2.py:20-21, 344-347). The tests redirect them by monkeypatching `MODULE` attributes in the `env` fixture (tests v2_publication.py:200-206). `--publish --dry-run` (v2.py:587-591) validates a fresh build against `schema()` in memory and prints the summary, writing NOTHING. `--emit-schema` WRITES `schemas/...v2.schema.json` (v2.py:639): DO NOT run it in Phase 7. `--record-publication` also writes. Phase 7 therefore never regenerates committed outputs; the committed schema, authority, manifest, certification stay 2.0.1.
- Tests that go red when the shape changes (committed 2.0.1 files vs new code), all accepted until Phase 9:
  - `test_committed_schema_equals_schema_function` (v2 test :164): committed schema (old shape) != `schema()` (new).
  - `test_real_published_files_validate` (publication test :467-478) -> `validate_published()`: fails at `a != build_published_authority()` (v2.py:604) and, earlier, `validate_publication`/schema on the committed old-shape authority.
  - `validate_published` also fails on CI step `publish_..._v2.py --validate` (ems-validate.yml:92) -> the `archive-assessment` CI job goes red on pushes in the window.
  - Possibly `test_publication_commit_ancestor_and_file_set` / `test_manifest_publisher_script_digest_matches_publication_commit` are unaffected (they compare to git history at the publication commit); `test_manifest_publisher_script_digest...` compares manifest script digest to the blob at the publication commit, which is unchanged: stays green.
  - `test_rows_equal_2_0_0_rows_and_only_identity_and_lineage_differ` (:548-558): red until rewritten (it compares against 54a7fd0, which is a stable git object, so rewrite makes it green in Phase 7).
- Synthetic (tmp env) tests stay green iff the plan updates them with the new shape: they call `build()`/`publish()` against patched paths; they only require the builders, validators and schema to agree with each other. These must be green at the end of every plan that touches publisher code (except the explicit real-file ones above).
- Roadmap says the window opens at the first publisher edit; Plan 1 (AA1 commit) is pure data and keeps everything green.

## Q7. `.gitattributes` / `.gitignore` implications for the AA1 manifest

- `.gitignore:6` contains `generated/` (only line matching `generated|archive`), so `git add -f <path>` is required (CONTEXT D-05; same pattern used for `ems-aa2` approval files, `35bfc08`, and `ems-aa3-v2` outputs). After the force-add the file is tracked and later changes are normal.
- `.gitattributes` has `generated/archive-assessment/ems-aa2/approval/** -text` at line 19 and `generated/archive-assessment/ems-aa3-v2/** text eol=lf` at 15. The AA1 folder has no rule. Add (append after line 19, file-specific): `generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json -text`.
- Order matters on Windows: write the `.gitattributes` line BEFORE `git add -f`, so the CRLF bytes are never normalised on add (if `core.autocrlf=true` were set and no attribute existed, git would store LF and the committed blob would hash to `06e39f7b...`, not `f0da8e2e...`). Stage both files in one commit with explicit paths only: `git add .gitattributes` then `git add -f -- generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json`.
- Working-tree warning: `git status` shows unrelated modified files (`registry/adjudication_rules.json`, `registry/policy_decisions.json`) and many untracked ones. Check whether `.gitattributes` itself has unrelated uncommitted edits before staging it (C2); if it does, stage only the intended hunk (`git add -p` is interactive-unsupported here; instead the user must stash/commit the others or the plan must produce the line via a clean patch). Never `git add -A`.
- Fresh-checkout read-back (D-07): see C3 for a byte-exact method. Do NOT pipe `git show` through PowerShell redirection or `Get-Content`/`Out-File`; Windows PowerShell 5 re-encodes. Use Python bytes or `cmd /c "... > file"`.

## Standard Stack

No new dependencies. Use what the publisher already imports: `hashlib`, `json`, `re`, `pathlib`, `jsonschema`, `yaml`; add stdlib `subprocess` only for `git_show`. `[VERIFIED: codebase grep]` CLAUDE.md pins Python 3.12, jsonschema, PyYAML, pytest. No packages to install, so the Package Legitimacy Audit is not applicable (none recommended).

## Architecture Patterns

### Data flow
```
v1 authority JSON (recorded raw AA digests) --copy--> build_authority (lineage objects)
live files: GOVERNANCE_DECISIONS, CATALOG, V1_AUTHORITY --lf_digest--> lineage objects
constants SUPERSEDED_V2_0_0 / V1_BASELINE_* --> lineage objects
                     |
                     v  (committed authority JSON, regenerated only in Phase 9)
--validate: validate_published -> validate_publication (shape) -> validate_lineage:
    for each entry: bytes = git_show(commit, rel) if 'commit' in entry else (ROOT/rel).read_bytes()
                    got = NORMALISERS[entry['normalisation']](bytes); compare to entry['sha256']
```

### Pattern 1: one uniform recompute loop (D-03)
```python
NORMALISATIONS = ['RAW_BYTES', 'CRLF_TO_LF']
NORMALISERS = {'RAW_BYTES': lambda b: b, 'CRLF_TO_LF': lf_bytes}
AA1_MANIFEST_REL = 'generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json'   # module-level constants only
EXPECTED_NORMALISATION = {'aa1_manifest': 'RAW_BYTES', 'aa2_closure': 'RAW_BYTES', 'aa2_approval': 'RAW_BYTES', 'catalog_reference': 'CRLF_TO_LF', 'governance_decisions': 'CRLF_TO_LF', 'v1_baseline': 'CRLF_TO_LF'}

def digest_entry(rel_path, sha, norm, commit=None) -> dict:
    e = {'relative_path': rel_path, 'sha256': sha, 'normalisation': norm}
    if commit: e['commit'] = commit
    return e

def lineage_digests(lin: dict) -> list[tuple[str, dict, str]]:
    # (label, entry, sha_key); supersedes yields two logical digests: authority file and decisions file at the same commit
    ...

def validate_lineage(lin: dict) -> None:
    errors = []
    for label, path, sha, norm, commit in lineage_digests(lin):
        if norm not in NORMALISERS: errors.append(f'{label}: normalisation {norm!r} not in {NORMALISATIONS}'); continue
        try: b = git_show(commit, path) if commit else (ROOT / path).read_bytes()
        except (OSError, AuthorityError) as e: errors.append(f'{label}: {e}'); continue
        if hashlib.sha256(NORMALISERS[norm](b)).hexdigest() != sha: errors.append(f'{label}: recorded sha256 does not match {path} under {norm}')
    if errors: raise AuthorityError('; '.join(errors))
```
Use `ROOT` dynamically (not bound as a default arg) so the existing `env` fixture's `ROOT` monkeypatch works. Missing file => error (fail closed; never "skip").

### Recommended key layout (planner may rename)
```
source_lineage: {
  aa1_manifest:        {relative_path, sha256, normalisation: RAW_BYTES},
  aa2_closure:         {relative_path, sha256, normalisation: RAW_BYTES},
  aa2_approval:        {relative_path, sha256, normalisation: RAW_BYTES},
  catalog_reference:   {relative_path, sha256, normalisation: CRLF_TO_LF, required_for_deterministic_compilation: false},
  governance_decisions:{relative_path, sha256, normalisation: CRLF_TO_LF, record_count, drafting_commit},
  supersedes:          {authority_id, version, commit, relative_path, sha256, normalisation, governance_decisions_sha256, governance_decisions_relative_path, governance_decisions_normalisation},
  v1_baseline:         {authority_id, version, commit, relative_path, sha256, normalisation}
}  # no digest_normalisation
```
`build_authority` keeps sourcing the three AA digest VALUES from `load(V1_AUTHORITY)['source_lineage']` (hermetic, passes the hermeticity test); only paths/normalisation come from constants.

### Schema
In `schema()` replace `'digest_normalisation':{'const':'CRLF_TO_LF'}` and the three flat sha entries with object schemas: `additionalProperties: False`, `required: [relative_path, sha256, normalisation]`, `relative_path: {'const': <path>}`, `sha256: sha`, `normalisation: {'const': <expected>}` (per-key const is stronger than a bare enum and still expressed through `NORMALISATIONS`; also assert the enum membership in a shared definition so D-04's closed enum is visible in the schema). The `required` list at line 302 loses `digest_normalisation` and the three flat keys and gains the three new keys. `additionalProperties: False` (v2.py:301) means a surviving `digest_normalisation` key is rejected by the schema (add a negative test).

### Anti-Patterns
- Computing the three AA digests inside `build_authority` by reading `generated/` (breaks the hermeticity test and makes builds non-reproducible on CI where AA2/AA1 files might be missing).
- Putting `validate_lineage` inside `validate_publication` (mutation harness IO/coupling).
- Declaring `RAW_BYTES` vs `CRLF_TO_LF` freely without a pinned expected value: on an LF-only file the two digests are identical, so a wrong declaration would go undetected by recompute. Pin the expected normalisation per key in code (EXPECTED_NORMALISATION) and check declared == expected.
- Hand-editing the committed schema or authority (hash certification; generated by the publisher).
- Opening git via `shell=True` or string commands; passing unvalidated JSON values to git.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| SHA-256 / LF normalisation | New hash helpers | `digest`, `lf_bytes`, `lf_digest` (v2.py:62-64) with a `NORMALISERS` dict | Keeps one definition of each normalisation |
| Schema | Hand-edited JSON | `schema()` + `--emit-schema` in Phase 9 | Generated artifact, test :164 compares them |
| Git history access | Python git libs / `import git` | `subprocess.run(['git', 'show', f'{commit}:{path}'])` | No new dependency; existing pattern |
| Temp git repo for tests | Mocking everything | `git init` in `tmp_path` with `-c user.name=t -c user.email=t@t -c core.autocrlf=false`, plus `monkeypatch` of `MODULE.ROOT` | Exercises real `git show` bytes, incl. CRLF blobs |

## Common Pitfalls

### Pitfall 1: Existing `subprocess` bans in tests
`test_module_does_not_call_git` (publication test :80-82) and `test_publisher_source_runs_no_subprocess_or_evaluator` (:676-678) assert the substring `subprocess` is absent from the publisher source. D-10 requires `git show`. Plan must narrow them deliberately and record why. Recommended replacement: keep banning `os.system`, `Evaluate-`, `Popen`, `import git`, and assert `subprocess` appears only inside `git_show` (e.g. `inspect.getsource(MODULE)` with `inspect.getsource(MODULE.git_show)` removed contains `subprocess` at most in the `import subprocess` line). Alternative (rejected as sidestepping intent): move `git_show` to a sibling module loaded by importlib.
**Warning signs:** two unrelated-looking test failures after adding the helper.

### Pitfall 2: Hermeticity test bans substrings in builder source
`test_v2_builder_does_not_use_generated_dir` (v2 test :165-168) checks `inspect.getsource(build_authority) + inspect.getsource(build_published_authority)` for `generated`, `OUT`, `ems-aa2`, `'ems-aa3'`, `AA2 / `. Do not inline `'generated/archive-assessment/...'` strings or constants named with `OUT` (case-sensitive) in those two functions; reference module-level constants (e.g. `AA1_MANIFEST_REL`) by name. Beware `OUT` substrings inside identifiers.

### Pitfall 3: Reply/decision-builder key coupling (D-14)
Renaming `supersedes.governance_decisions_sha256` or `governance_decisions.sha256` breaks scripts and tests that must not change. Keep both.

### Pitfall 4: Declared-normalisation negative test on LF-only files
Flipping `RAW_BYTES`<->`CRLF_TO_LF` changes the recomputed digest only if the cited bytes contain `\r\n`. The negative test for "changed declared normalisation" must use a CRLF-containing target: the real AA2 approval file (122 CRLF lines), the AA1 manifest, or a synthetic temp file written with `b'a\r\nb\r\n'`. The `governance_decisions`, supersedes blobs and catalog are LF in git (`eol=lf` for decisions), so flipping their normalisation is caught by the pinned `EXPECTED_NORMALISATION` check, not by recompute. Cover both enum values with CRLF fixtures.

### Pitfall 5: Windows byte handling
Reading with `read_text` or git text mode corrupts CRLF. Use `read_bytes()` and bytes-mode subprocess. In PowerShell never redirect `git show` output to a file; Windows PowerShell 5 writes UTF-16 and mangles bytes.

### Pitfall 6: `.gitattributes` order and autocrlf (see Q7)
Add the `-text` rule before `git add -f`; verify with `git ls-files --eol`.

### Pitfall 7: Catalog digest is recomputed from the live file
D-10 recomputes `catalog_reference` from the checked-out file. `validate_publication` already does the same (v2.py:290), so nothing new is fragile, but Phase 8 (GATE-03) will replace this with a frozen reference; do not design `validate_lineage` so that Phase 8 must rewrite it: treat `catalog_reference` via the same loop and let Phase 8 add a `commit` to that entry (the loop already switches to `git show` when `commit` is present).

### Pitfall 8: Shallow / absent history must fail
`git show` on an absent commit returns non-zero (128). The helper turns every non-zero or `OSError` into `AuthorityError` (D-11). A test must prove that a nonexistent 40-hex commit fails, and that a missing cited file fails.

### Pitfall 9: Do not bump `VERSION`/`AUTHORITY_ID` in Phase 7
Test `:560-561` pins `2.0.1`; sign-off and cert reference it. The version bump is Phase 9.

## Code Examples

Hermetic validate_lineage test skeleton (synthetic CRLF + temp git repo):
```python
def test_lineage_changed_normalisation_fails(tmp_path, monkeypatch):
    f = tmp_path / 'f.bin'; f.write_bytes(b'a\r\nb\r\n')
    monkeypatch.setattr(MODULE, 'ROOT', tmp_path)
    good = {'relative_path': 'f.bin', 'sha256': hashlib.sha256(b'a\r\nb\r\n').hexdigest(), 'normalisation': 'RAW_BYTES'}
    ... # build a lineage via a helper that accepts overrides; assert OK for RAW_BYTES; flipping to CRLF_TO_LF raises AuthorityError
```
Commit-pinned test: `subprocess.run(['git','init'], cwd=tmp_path)`; commit CRLF blob using `-c core.autocrlf=false` and a `.gitattributes` `* -text` line; call `validate_lineage` with entry carrying that commit. Guard with the existing `git_ready()` skip pattern (tests :484-489). Also test a nonexistent `0*40` commit raises.

## State of the Art

| Old (2.0.1) | New (2.0.2 lineage, designed in Phase 7) |
|---|---|
| Global `digest_normalisation: CRLF_TO_LF` + three flat raw-byte digests | Per-digest `{relative_path, sha256, normalisation[, commit]}` |
| No recompute of AA digests | `validate_lineage` recompute in `--validate` |
| AA1 manifest untracked | Committed with `-text` |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The user accepts narrowing the two `subprocess` ban tests (Phase 6 invariants) to allow one `git_show` helper | Pitfall 1 | If not accepted, helper must live in a sibling module; plan 2 task changes |
| A2 | The 87-CRLF-line / `f0da8e2e...` facts for the AA1 manifest from CONTEXT D-05 still hold at plan time | Q1, Q7 | Commit would be wrong; D-07 gate catches it |
| A3 | AA2 recorded digests `ed589d76...` (closure) and `de170ebc...` (approval) equal the raw sha256 of the committed AA2 files | Q1 | If not, recompute fails; see C1. Treat as a finding, not a reason to change digests |
| A4 | `git show 62a8955:registry/archive_assessment_applicability_authority.json` LF-normalised equals the recorded `v1_baseline.sha256` (computed from the live file) | Q1 | If not, `validate_lineage` would fail for `v1_baseline`; see C4 |
| A5 | Leaving the committed schema/authority at 2.0.1 during Phase 7 is the intended red window (no regeneration) | Q6 | If Phase 7 should regenerate, it changes committed hashed files, widening the red window |
| A6 | `supersedes.governance_decisions_*` extra flat keys are acceptable to the user (vs. nesting) because D-14 forbids reply-builder changes | Q3 | Nesting would require reply builder edits |

## Open Questions

1. **Key shape for the second digest in `supersedes`.** What we know: reply builder reads flat `governance_decisions_sha256`. What's unclear: whether the user prefers an object. Recommendation: flat keys plus `*_relative_path`/`*_normalisation` siblings (A6).
2. **Should `validate_lineage` also run in `--publish --dry-run`?** Recommendation: defer to Phase 9.
3. **Add lineage mutations to `NEGATIVE_MUTATIONS`?** Would change the count 26 (tests :609-611, :673) and the published negative file. Recommendation: no, use standalone pytest negatives (D-12); Phase 8 touches the mutation gate (GATE-02).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 + pytest + jsonschema | tests, publisher | Not probed (no shell) | confirm C5 | none |
| git (full history) | `git show`, commit step | Not probed | confirm C5 | none; D-11 fails closed |
| PowerShell | operator commands | Available to the orchestrator, not to this agent | — | — |

## Facts the orchestrator must confirm (PowerShell, from `C:\temp\standars\ems`)

Use the venv Python (`$env:VIRTUAL_ENV\Scripts\python.exe` or `.venv\Scripts\python.exe`); `-I` for isolation.

- **C1: AA digests are raw digests of the committed AA2 files and the AA1 file.**
  `.\.venv\Scripts\python.exe -I -c "import hashlib,pathlib as P; r=P.Path('generated/archive-assessment'); [print(n, hashlib.sha256(p.read_bytes()).hexdigest(), hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()) for n,p in (('aa1',r/'ems-aa1/ems_aa1_analysis_artifact_manifest.json'),('closure',r/'ems-aa2/approval/archive_assessment_applicability_governance_closure.json'),('approval',r/'ems-aa2/approval/archive_assessment_applicability_governance_approval.json'))]"`
  Expected raw: aa1 `f0da8e2e...`, closure `ed589d76febe255665fd11697a9c0b9f8c7f036487e26b6f765ef8046c55887b`, approval `de170ebcf60aabe593b3e9766c11170c3c597730ef0f342028c8f844614f745c`; LF values must differ from the raw ones for all three.
- **C2: `.gitattributes` and tracking state.**
  `git status --short -- .gitattributes generated/archive-assessment/ems-aa1` ; `git check-ignore -v generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json` ; `git ls-files --eol -- generated/archive-assessment/ems-aa2/approval` ; `git config core.autocrlf`. Confirms `.gitattributes` has no unrelated edits and which eol mode AA2 files carry (expect `i/-text w/-text`).
- **C3: Byte-exact read-back after the AA1 commit (D-07).**
  `.\.venv\Scripts\python.exe -I -c "import subprocess,hashlib; b=subprocess.run(['git','show','HEAD:generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json'],capture_output=True,check=True).stdout; print(hashlib.sha256(b).hexdigest())"` must print `f0da8e2e45c306ccc42ae96f25a19922668f3eedecdb26006f13514e24ad9b4b`. Also `git ls-files --eol -- generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json` should show `i/-text w/-text`, and `git show --stat HEAD` must list only `.gitattributes` and the manifest. For a true fresh checkout: `git worktree add $env:TEMP\aa1chk HEAD` then hash the file there and `git worktree remove --force $env:TEMP\aa1chk`.
- **C4: v1_baseline and supersedes blobs at their commits equal the recorded digests under CRLF_TO_LF.**
  `.\.venv\Scripts\python.exe -I -c "import subprocess,hashlib; f=lambda c,p: hashlib.sha256(subprocess.run(['git','show',c+':'+p],capture_output=True,check=True).stdout.replace(b'\r\n',b'\n')).hexdigest(); print(f('62a8955dc28d9458cd1167fad314926e057c31fc','registry/archive_assessment_applicability_authority.json')); print(f('54a7fd09114704a97a7a48fce5f89aebeb48c90a','registry/archive_assessment_applicability_authority_v2.json')); print(f('54a7fd09114704a97a7a48fce5f89aebeb48c90a','registry/archive_assessment_governance_decisions.json'))"`
  Expected: first equals `v1_baseline.sha256` in `registry/archive_assessment_applicability_authority_v2.json` (read via `Select-String -Path registry\archive_assessment_applicability_authority_v2.json -Pattern '"sha256"'`), second `de36e227be4ccc95f4a8a8a08247cf6e49f7682908c7f425f8cc02bbaa1da353`, third `4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f`. The first one is the only unproven link in the existing tests (they compare the live v1 file, not the blob).
- **C5: Baseline green before any edit.**
  `.\.venv\Scripts\python.exe -m pytest tests -k archive_assessment -p no:cacheprovider -q` and `.\.venv\Scripts\python.exe scripts\publish_archive_assessment_applicability_authority_v2.py --validate` (expect `PASS`). Record the count so the red window is measurable. Also `git rev-parse --is-shallow-repository` (expect `false`).
- **C6: After the shape change (end of Plan 2)** run the same pytest command and list red tests; expected red set is exactly: `test_committed_schema_equals_schema_function`, `test_real_published_files_validate`, plus any parametrised real-file cases, and `--validate` fails at the fresh-build comparison. Anything else red is a plan bug.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (`requirements-dev.txt`), existing |
| Config file | none (no pyproject/pytest.ini; CI uses `-p no:cacheprovider`) |
| Quick run command | `python -m pytest tests/test_archive_assessment_applicability_authority_v2.py tests/test_archive_assessment_applicability_authority_v2_publication.py -p no:cacheprovider -q` |
| Full suite command | `python -m pytest tests -k archive_assessment -p no:cacheprovider -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LIN-01 | Each lineage entry has `{relative_path, sha256, normalisation}`; `digest_normalisation` absent and rejected by schema; enum closed; per-key expected normalisation | unit (build + schema) | `pytest tests/test_archive_assessment_applicability_authority_v2.py -k lineage -q` | extend existing (lines 143-160) |
| LIN-02 | `validate_lineage` passes on real repo files; fails on byte change, flipped normalisation (CRLF fixture), changed digest, missing file, missing/unknown commit; both enum values; supersedes/v1 via git show | unit + temp git repo | `pytest tests/test_archive_assessment_applicability_authority_v2_publication.py -k lineage -q` | Wave 0 (new tests; new file `tests/test_archive_assessment_lineage_validation.py` is acceptable and matches the CI `-k archive_assessment` selector) |
| LIN-03 | AA1 manifest tracked; blob raw sha == `f0da8e2e...`; `.gitattributes` rule present | integration (git) | `pytest tests/test_archive_assessment_lineage_validation.py -k aa1 -q` | Wave 0 |
| D-13 | Each normalisation claim recomputed (record, cert, manifest, trace, signoff, reply pin) | real-file unit | `pytest tests -k "normalisation_claim" -q` | Wave 0 |

### Sampling Rate
- Per task commit: the quick command above.
- Per wave merge: full `-k archive_assessment` suite (expect only the accepted red set after Plan 2).
- Phase gate: red set equals the documented set; `git status` shows only intended files.

### Wave 0 Gaps
- [ ] `tests/test_archive_assessment_lineage_validation.py` — LIN-02/LIN-03/D-13 tests and temp-git fixture helper
- [ ] Narrow the two `subprocess` tests (Pitfall 1)
- [ ] Rewrite `test_rows_equal_2_0_0_rows_and_only_identity_and_lineage_differ` lineage assertion

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | Regex-validate `commit` (`^[0-9a-f]{40}$`) and repo-relative path (`contains_absolute`, no `..`) before building the `git show` argument; list-form `subprocess.run`, never `shell=True`; jsonschema closed enums |
| V6 Cryptography | yes | `hashlib.sha256` only; no custom hashing |
| V2/V3/V4 | no | Not applicable (offline governance scripts) |

### Known Threat Patterns
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Argument/option injection into `git show` via lineage JSON values | Tampering | Full 40-hex commit regex, path checks, `rev:path` single argument, list args |
| Silent pass when history missing | Repudiation/Tampering | Fail closed (D-11) |
| Digest edited to fit file | Tampering | D-07; per-key pinned expected normalisation; paths pinned by schema `const` |
| Path traversal in cited `relative_path` | Tampering | Reject absolute and `..` (also existing `contains_absolute`) |

## Suggested Plan Breakdown (coarse)

**Plan 1: Commit the AA1 manifest (LIN-03). Red window: not opened (data only).**
- Run confirm C1, C2, C5 first. Append the `-text` line to `.gitattributes` (after line 19). `git add .gitattributes` and `git add -f -- <manifest>` (explicit paths). Commit with only those two files. Run C3; if hash differs, `git reset` the commit and stop (D-07). Add LIN-03 tests (blob raw sha, `.gitattributes` rule text) in the new test file; those tests can land in plan 2's commit or this plan if the commit stays "its own" (D-05 says the manifest commit stages only the manifest and `.gitattributes`; so tests go into plan 2).
- Note: STATE/ROADMAP say "ask the user for the AA1 manifest path", but D-05 already records the path and the verified hash; the plan should treat it as resolved and only re-verify (C1).

**Plan 2: Lineage shape, schema and `validate_lineage` (LIN-01, LIN-02). Opens the accepted red window at the first publisher edit.**
- Publisher: constants (paths, `NORMALISATIONS`, `EXPECTED_NORMALISATION`); `digest_entry`; reshape `SUPERSEDED_V2_0_0` / `v1_baseline_entry()`; `build_authority` lineage objects (values from v1 lineage, no `generated` strings in function source); remove `digest_normalisation`; update `validate_authority`/`validate_publication` checks; update `schema()`; add `git_show`, `validate_lineage`; hook into `validate_published` after line 603.
- Tests: update tests listed in Q2; narrow subprocess-ban tests; new D-12 negative tests (CRLF fixtures, both enum values, temp git repo, missing commit); schema negative tests (extra `digest_normalisation`, bad enum, missing key). Do NOT run `--emit-schema` or `--publish` (writes). Verify `publish_..._v2.py --publish --dry-run` prints the summary and writes nothing.
- Red set after this plan: the documented items in Q6. Synthetic tests green.

**Plan 3: Normalisation sweep tests (D-13). Red window unchanged (adds only green tests on committed 2.0.1 files, plus reply-pin test).**
- One test per claim in the Q5 table, recomputing from disk/git; no code shape change. No edits to the reply builder, schema or reply files (D-14). If any claim is found false (unexpected), stop and raise to the user instead of editing.

Hand-off to Phase 9: regenerate schema (`--emit-schema`), authority and outputs, bump `VERSION`, set `supersedes` to 2.0.1 at `31addfa9...`, rewrite reply/pin tests, close the window.

## Sources

### Primary (HIGH confidence, direct file reads)
- `scripts/publish_archive_assessment_applicability_authority_v2.py` (lines cited inline)
- `scripts/publish_archive_assessment_applicability_authority.py:17,46-47,78,126`
- `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:28,76-87,145,197,203,218-227,258-267`
- `scripts/build_archive_assessment_governance_decisions.py:365-368`
- `tests/test_archive_assessment_applicability_authority_v2.py`, `..._v2_publication.py`, `test_archive_assessment_demo3_w1_req_001_reply.py`, `test_archive_assessment_governance_decisions.py`
- `.gitattributes:1-19`, `.gitignore:6`, `.github/workflows/ems-validate.yml:70-96`
- `registry/archive_assessment_applicability_authority_v2.json:3068-3076` and v1 `:2869-2871` (recorded digest values)

### Secondary / Tertiary
- None. No external documentation was needed; `git show <rev>:<path>` behaviour (raw blob output) is standard git `[ASSUMED]`, covered by confirm C3/C4.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH (no new dependencies)
- Architecture / coupling constraints: HIGH (direct reads, line refs)
- Digest truth table: HIGH for code provenance; MEDIUM for byte-level claims until C1/C4 run
- Pitfalls: HIGH

**Research date:** 2026-10-20
**Valid until:** 2026-11-19 (stable repo; invalidated by any edit to the v2 publisher or its tests)
