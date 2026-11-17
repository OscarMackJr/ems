# Phase 13: Certified Republication 2.0.3 - Pattern Map

**Mapped:** 2026-11-17
**Files analyzed:** 15 (10 publication files, record, 1 test, 3 planning docs)
**Analogs found:** 15 / 15 (Phase 9 is the direct precedent; every file existed in 2.0.2 form)

The phase is procedural. No code is written except one test assertion. The analogs are the 2.0.2 file contents and the Phase 9 plans 09-04 and 09-05. Copy their task structure, checkpoint form and evidence layout, and change only what 13-CONTEXT D-01..D-08 changes: at-pin instead of pre-publication, CI at the WR-03 head, six validators instead of five, and three record-bound transient reds.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `registry/archive_assessment_applicability_authority_v2_signoff.json` | config (hand-written human gate record) | request-response (human approval -> data) | same file at HEAD (2.0.2) | exact |
| `registry/archive_assessment_applicability_authority_v2.json` | model (generated authority) | transform (publisher `--publish`) | same file, 2.0.2 at `ae15c74` | exact |
| `schemas/archive_assessment_applicability_authority_v2.schema.json` | config (generated schema) | transform (`--emit-schema`) | same file at `ae15c74` | exact |
| 7 files under `generated/archive-assessment/ems-aa3-v2/` (matrix, semantic, negative, traceability, certification, report `.md`, manifest) | generated outputs | transform (`--publish`) | same files at `ae15c74` | exact |
| `registry/archive_assessment_applicability_authority_v2_publication_record.json` | config (generated record) | transform (`--record-publication <sha>`) | same file at HEAD (written at `a71257e`) | exact |
| `tests/test_archive_assessment_lineage_validation.py` (L371, one line) | test | subprocess / request-response | same test, L357-377 | exact |
| `.planning/phases/13-.../13-VERIFICATION.md` | planning evidence | batch (record evidence) | `09-VERIFICATION.md` | exact |
| `.planning/STATE.md` | planning evidence | batch | Phase 9 update in 09-05 Task 2 | exact |
| `13-0x-PLAN.md` (publication plan, record/push plan) | plan | n/a | `09-04-PLAN.md`, `09-05-PLAN.md` | exact |

## Pattern Assignments

### Sign-off record `registry/archive_assessment_applicability_authority_v2_signoff.json`

**Analog:** current file (2.0.2), lines 1-14. Copy it and change only `date`, `scope` (version, digest, superseded version and commit), `authority_id`, `authority_sha256` and `version`:

```json
{
  "approval": {
    "approver": "Oscar Mack",
    "date": "2026-11-12",
    "role": "EMS_GOVERNANCE_AUTHORITY",
    "scope": "Publication of EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2 version 2.0.2 (authority LF sha256 a44eea1f...), superseding 2.0.1 at 31addfa with no decision changed."
  },
  "authority_id": "EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2",
  "authority_sha256": "a44eea1f98ec361ab100c554eb3a8d3529cfeb1fec78ec6d38193a675f0b8beb",
  "authority_sha256_normalisation": "CRLF_TO_LF",
  "dual_role_statement": "Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it.",
  "status": "PUBLICATION_SIGNOFF",
  "version": "2.0.2"
}
```

- 2.0.3 values: `scope` = "... 2.0.3 version 2.0.3 (authority LF sha256 <dry-run digest>), superseding 2.0.2 at ae15c74 with no decision changed." The proposed full record is in 13-RESEARCH "Sign-off Record".
- `dual_role_statement` must equal publisher `DUAL_ROLE_STATEMENT` (L527) byte-for-byte.
- Date: take it from Oscar's resume signal. Do not reuse `2026-11-12`, because identical semantic and traceability outputs would drop out of the commit (RESEARCH, L1699 test).
- Write with the Write tool: LF line endings, sorted keys, 2-space indent and a trailing newline. Write it only after the approve signal.
- Phase 9 wrote this in 09-04 Task 2 (`<action>` L105). Copy that action text.

### The 10 generated publication files

**Analog:** 09-04 Task 1 (L65-85) and Task 3 (L119-140). Single source of the list is publisher L596:

```python
def publication_paths() -> list[str]: return [rel(AUTHORITY), rel(SCHEMA), rel(SIGNOFF)] + [f'{rel(OUT)}/{n}' for n in (N_MATRIX, N_SEMANTIC, N_NEGATIVE, N_TRACE, N_CERT, N_REPORT, N_MANIFEST)]
```

These files must not be hand-edited. Differences from 09-04:
- **Order.** 09-04 ran `--emit-schema` before the dry run. For 13, follow RESEARCH: dry run -> checkpoint -> sign-off -> `--validate-signoff` -> re-run the dry run and compare the digest -> `--emit-schema` -> `--publish`. Either way, `--emit-schema` must come before `--publish` (L662 digests the schema on disk).
- **Staging.** 09-04 used plain `git add --` for all 10. For 13, use `git add --` for the 3 registry/schema paths and `git add -f --` for the 7 `generated/` paths, because `generated/` is gitignored (RESEARCH Pitfall 2).
- **Post-commit gate.** Replace 09-04 Task 3's `--validate --pre-publication` with `--validate --at-pin`, run in the operator tree and in a fresh `--no-local` clone (D-03). Parse the JSON; do not string-compare it. The printed form is at publisher L825/L828:

```python
print(json.dumps({'status': 'PASS', 'mode': 'AT_PIN', 'deferred': [AT_PIN_DEFERRED]}) if at_pin else 'PASS')
AT_PIN_DEFERRED = 'PUBLICATION_RECORD_BINDING: the publication record naming this commit is written in the next commit; ...'
```

Test-side assertion shape to mirror in acceptance criteria (`tests/test_archive_assessment_applicability_authority_v2_publication.py` L549):

```python
assert len(doc['deferred']) == 1 and doc['deferred'][0].startswith('PUBLICATION_RECORD_BINDING: ')
```

- **Acceptance criteria.** Copy 09-04 Task 3 L133-138: only listed paths; `git diff --name-only HEAD~1 HEAD -- scripts tests` empty; frozen-reply diff empty. Change `git show --stat` to `--stat=300`, because long paths are truncated otherwise (RESEARCH Q6).

### Publication record `registry/archive_assessment_applicability_authority_v2_publication_record.json`

**Analog:** current file (2.0.2, written at `a71257e`):

```json
{
  "authority_id": "EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2",
  "authority_sha256": "a44eea1f98ec361ab100c554eb3a8d3529cfeb1fec78ec6d38193a675f0b8beb",
  "digest_normalisation": "CRLF_TO_LF",
  "manifest_sha256": "9991228ab7ff0a0c52c61b77a4d4c0e58b56d68b0c382caa83496621f092bac2",
  "publication_commit": "ae15c7458e49c8f55cc58c61bab04bc716aa9892",
  "version": "2.0.2"
}
```

- Written only by `--record-publication <40-hex>` (publisher L859-864). Do not hand-write it.
- Task pattern: 09-05 Task 1 (L52-75): record -> record-only commit -> plain `--validate` -> validators -> full suite -> byte identity.
- Changes for 13:
  - Run six validators, not five (per `.github/workflows/ems-validate.yml` `archive-assessment` job).
  - Use `EMS_FAIL_ON_SKIP=1` and a fresh `--basetemp`.
  - Do not run the suite between `--record-publication` and the commit (RESEARCH Pitfall 7).
  - At-pin must run before `--record-publication` (RESEARCH Q4 order constraint).

### WR-03 test edit `tests/test_archive_assessment_lineage_validation.py`

**Analog:** the test itself, L357-377. Current core:

```python
    before = outcome()
    live = clone / MODULE.CATALOG_REL
    for change in (lambda: live.write_bytes(b'controls: []\n'), live.unlink):
        change()
        after = outcome()
        assert after == before, f'--validate outcome changed after live catalog change: before={before!r} after={after!r}'
```

Insert one line after L371 (RESEARCH Q5), in the file's single-quote f-string style:

```python
    assert before == (0, 'PASS'), f'--validate baseline must be PASS for D-10 to be meaningful: {before!r}'
```

Commit it alone, after the record commit (D-07). The test clones committed HEAD with `git clone --shared`, so the record commit must already exist.

### `13-VERIFICATION.md`

**Analog:** `09-VERIFICATION.md`.

- **Frontmatter** (L1-12): `publication_commit`, `record_commit`, `ci_run_id`, `ci_head_sha`, `requirements`. For 13, also add the WR-03 commit and the clone method.
- **"Key identifiers" table** (L35-47): copy its rows (publication SHA, record SHA, authority LF sha, manifest sha, decisions sha `4e746d1f…`, supersedes, sign-off, CI run). For 13, add rows for the at-pin outputs (tree and clone).
- **"Independent checks" bullets** (L49-66): stat scopes, the `diff --name-only pub record -- . ':(exclude).planning'` check, the no-code-in-pub check, recomputed digests, and the 80-row comparison with counts 3/18/59. Reuse them, with the comparison made against `ae15c74`.
- **"Judgment calls on the SC4 / PUB-09 reading (D-04)"** (L128-132): the template for the explicit D-01 rewording of SC3. The 13 version names the WR-03 head as the CI head.
- **D-02 evidence:** record verbatim `git show --stat=300 --format=` output for the pub, record and WR-03 commits.

## Shared Patterns

### Human-gate checkpoints (both blocking)

**Sign-off** (source: `09-04-PLAN.md` L87-95). Frontmatter `autonomous: false` (L18); `must_haves.truths` names the gate (L22).

```xml
<task type="checkpoint:decision" gate="blocking">
<decision>Sign-off of EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2 by Oscar Mack as EMS governance authority</decision>
<context>The orchestrator presents the full dry-run summary (...). Oscar Mack also holds the Hayes developer role; this is written into the sign-off via the exact dual-role statement. Publication must not proceed on drafting judgment alone.</context>
<options>
<option id="approve"><name>Approve</name><pros>Proceeds to write sign-off and publish</pros><cons>None; sign-off date becomes published_on in every output</cons></option>
<option id="reject"><name>Reject or request changes</name><pros>Stops before any publication file is written</pros><cons>Any code change requires a new dry run and new digest</cons></option>
</options>
<resume-signal>Oscar Mack replies "approve" (and the sign-off date, or accepts today's date) or describes required changes</resume-signal>
</task>
```

For 13:
- Change the resume signal to require an explicit date ("approve, date YYYY-MM-DD"), per RESEARCH Open Question 1.
- Add the proposed sign-off JSON to `<context>` (D-06).

**Push go-ahead** (source: `09-05-PLAN.md` L77-84). Frontmatter `autonomous: false` (L11).

```xml
<task type="checkpoint:human-verify" gate="blocking">
<what-built>2.0.2 published (publication commit), recorded (record commit), plain validate and full suite green locally. The branch has about 65 local commits not on origin; pushing publishes the whole milestone branch.</what-built>
<how-to-verify>
1. Review `git log --oneline origin/feature/ems-aa3-archive-applicability-authority..HEAD` and the publication/record SHAs.
2. Confirm go-ahead to push `feature/ems-aa3-archive-applicability-authority` and dispatch the workflow. No PR, merge or tag will be made.
</how-to-verify>
<resume-signal>Oscar Mack types "push approved" or describes concerns. Nothing is pushed before this.</resume-signal>
</task>
```

For 13:
- 74 commits are ahead of origin `49c7b08`.
- `<what-built>` must also name the WR-03 commit.

### Push, dispatch and CI confirmation

**Source:** `09-05-PLAN.md` Task 2 (L86-109). Reuse:
- the `gh workflow run ems-validate.yml --ref <branch>` / `gh run list ... --json databaseId,headSha,status,conclusion` / `gh run watch` sequence;
- the acceptance checks: headSha equals the pushed HEAD; `merge-base --is-ancestor <record> <headSha>`; `diff --quiet` on the 10 paths; no token in `.planning`; no PR or tag.

For 13:
- Try a plain push first, and use the `GIT_CONFIG_*` workaround only on failure (RESEARCH Q7).
- Clear the `GIT_CONFIG_*` variables before running any validator.
- Re-list the runs until `headSha` matches.

### Commit hygiene (all commits)

**Source:** 09-04 Task 3 `<action>` (L127) and 09-05 Task 1 (L61).
- Stage with explicit paths only, then check with `git diff --cached --name-only`.
- Use the commit messages `feat(13-xx): publish EMS-AA3 archive applicability authority 2.0.3` and `feat(13-xx): record 2.0.3 publication commit`, each ending with the Co-Authored-By line.
- Planning-only commits (SUMMARY, STATE) between pub and record are allowed, but must be separate commits. Never stage `.planning/config.json`.

### Threat model block

**Source:** `09-04-PLAN.md` L144-163 and `09-05-PLAN.md` L113-132 (T-09-13..T-09-22). Renumber them as T-13-xx. For 13, add one threat: ambient `GIT_*` environment variables during validation (AR-03 accepted; clear them after the push).

### Red-set ledger per commit

**Source:** `09-BASELINE-RED.md`, plus the 13-RESEARCH "Red-Set Transitions" table. The plan must state the expected red set at each commit:

| Commit | Expected red set |
|---|---|
| Pre-dry-run | 3 tests + V1 |
| Publication commit | B, C, the 3 record-bound tests, V1 (new message) |
| Record commit | none |
| WR-03 commit | none |

## No Analog Found

| File / step | Reason |
|-------------|--------|
| Fresh-clone at-pin run (D-03 #2) | New in Phase 13; Phase 9 had no at-pin mode. Use the recipe in 13-RESEARCH "Fresh-clone recipe" (`clone --no-local --no-checkout`, `checkout --detach $PUB`, run with `python -I`). |

## Metadata

**Analog search scope:**
- `.planning/phases/09-certified-republication-2-0-2/`;
- `registry/archive_assessment_applicability_authority_v2_{signoff,publication_record}.json`;
- `scripts/publish_archive_assessment_applicability_authority_v2.py` (grep only);
- `tests/test_archive_assessment_lineage_validation.py` L350-379;
- `tests/test_archive_assessment_applicability_authority_v2_publication.py` (grep only).

**Files scanned:** 9
**Pattern extraction date:** 2026-11-17
