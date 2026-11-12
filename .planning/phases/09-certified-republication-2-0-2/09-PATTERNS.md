# Phase 9: Certified Republication 2.0.2 - Pattern Map

**Mapped:** 2026-11-12
**Files analyzed:** 11 (4 code/test modify groups, 7 generated/published artefacts and records)
**Analogs found:** 11 / 11 (all are self-analogs: the 2.0.0 -> 2.0.1 retarget in Phase 6/7/8 and commits `31addfa` / `4d9b7c1`)

Line numbers are the current working tree (read-only mapping, nothing run).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/publish_archive_assessment_applicability_authority_v2.py` | publisher / validator | batch + transform (fail-closed) | itself at 2.0.1 (`SUPERSEDED_V2_0_0` binding, `CATALOG_COMMIT` style) | exact |
| `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` | publisher (validator) | file-I/O + git-history read | `V2.git_show` + `CATALOG_COMMIT` constant pattern | role-match |
| `tests/test_archive_assessment_applicability_authority_v2.py` | test | request-response | itself L144, L204 | exact |
| `tests/test_archive_assessment_applicability_authority_v2_publication.py` | test | file-I/O + git | itself L485-520, L632-712, L744-760 | exact |
| `tests/test_archive_assessment_lineage_validation.py` | test | file-I/O + git | itself L34, L55 | exact |
| `tests/test_archive_assessment_demo3_w1_req_001_reply.py` | test | file-I/O + git | itself L306-400 | exact |
| `schemas/archive_assessment_applicability_authority_v2.schema.json` | schema (generated) | transform | `--emit-schema` output | exact |
| `registry/archive_assessment_applicability_authority_v2.json` | registry (generated) | batch | commit `31addfa` | exact |
| `registry/archive_assessment_applicability_authority_v2_signoff.json` | registry (sign-off) | CRUD (human gate) | commit `31addfa` (08/06 sign-off shape) | exact |
| `generated/archive-assessment/ems-aa3-v2/*` (7 files) | generated outputs | batch | commit `31addfa` | exact |
| `registry/archive_assessment_applicability_authority_v2_publication_record.json` | registry (record) | CRUD | commit `4d9b7c1` (record-only commit) | exact |

Untouched (assert empty diff): `docs/DEMO3_W1_REQ_001_REPLY.md`, `registry/archive_assessment_demo3_w1_req_001_reply.json`, `schemas/archive_assessment_demo3_w1_req_001_reply.schema.json`.

## Pattern Assignments

### Publisher: replace `SUPERSEDED_V2_0_0` with `SUPERSEDED_V2_0_1` (`scripts/publish_archive_assessment_applicability_authority_v2.py`)

**Constant to mirror** (L34-45; keep the same 9 keys, compact style):
```python
VERSION = '2.0.1'          # -> '2.0.2' (not named in CONTEXT, required)
AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-' + VERSION
SUPERSEDED_V2_0_0 = {
    'authority_id': 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0', 'version': '2.0.0', 'commit': '54a7fd09114704a97a7a48fce5f89aebeb48c90a',
    'relative_path': 'registry/archive_assessment_applicability_authority_v2.json',
    'sha256': 'de36e227be4ccc95f4a8a8a08247cf6e49f7682908c7f425f8cc02bbaa1da353',
    'governance_decisions_sha256': '4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f',
    'normalisation': 'CRLF_TO_LF',
    'governance_decisions_relative_path': 'registry/archive_assessment_governance_decisions.json',
    'governance_decisions_normalisation': 'CRLF_TO_LF',
}
```
New values: id `...-2.0.1`, version `2.0.1`, commit `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb`, sha256 `7be5eb8869a8897ee6d55051f9d872fee9a8a35bdbd2ad5093d40e8a1d489e4f` (from 2.0.1 record). Decisions digest stays `4e746d1f...`. Do not type by hand: derive with git then assert in test (see Tests).

**Every reference to swap** (grep result): L176 `build_authority` (`'supersedes': dict(SUPERSEDED_V2_0_0)`), L243 `validate_authority` (`sup != SUPERSEDED_V2_0_0`, message "2.0.0 publication"), L297 and L300 `validate_publication` (digest binding messages "2.0.0 decisions digest" / "2.0.1 may not change"), L320 (lineage supersedes), L379 schema `'supersedes':pinned(SUPERSEDED_V2_0_0, {'sha256','governance_decisions_sha256'})`, L490 mutation description ("differs from the 2.0.0 value"), L537 `dry_run_summary`, L719-721 pre-publication branch.

**Pre-publication branch** (L717-721) to retarget:
```python
if pre_publication:
    want_id, want_version = SUPERSEDED_V2_0_0['authority_id'], SUPERSEDED_V2_0_0['version']
    if record['publication_commit'] != SUPERSEDED_V2_0_0['commit']: raise AuthorityError('pre-publication record must name the 2.0.0 publication commit')
    if record['authority_sha256'] != SUPERSEDED_V2_0_0['sha256']: raise AuthorityError('pre-publication record authority_sha256 must equal the 2.0.0 digest')
```
Keep the message substrings tests match (`'must name'`, `'... publication commit'`, `'... digest'`) with `2.0.1` swapped in.

**New D-08 row comparison** (add inside `validate_publication` after the existing digest checks; errors-list style, style of L281-304). Use RESEARCH shape:
```python
prev = json.loads(git_show(SUPERSEDED_V2_0_1['commit'], SUPERSEDED_V2_0_1['relative_path']).decode('utf-8'))
prev_rows = {r['control_id']: r for r in prev['controls']}
KEYS = ('not_applicable_decision_state', 'not_applicable_rule', 'not_applicable_authority', 'decision_ids')
for r in rows:
    p = prev_rows.get(r.get('control_id'))
    if p is None or any(r.get(k) != p.get(k) for k in KEYS): errors.append(f"{r.get('control_id')}: decision content differs from 2.0.1")
if set(prev_rows) != {r.get('control_id') for r in rows} or a.get('applicability_decision_ids') != prev.get('applicability_decision_ids'): errors.append('decision set differs from 2.0.1')
```
**git error rule** (L338-344 `git_show`, L610-631 `mutation_gates`): git failures must raise `GitHistoryError` (propagated; `mutation_gates` has `except GitHistoryError: raise` before `except AuthorityError: gates.append(...)`). Content mismatch is `AuthorityError` (via the errors list). `git_show` requires 40-hex commit and repo-relative path:
```python
def git_show(commit: str, relative_path: str) -> bytes:
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit): raise AuthorityError(...)
    ...
    except OSError as e: raise GitHistoryError(f'{relative_path}@{commit[:7]}: git unavailable: {e}') from e
    if r.returncode != 0: raise GitHistoryError(...)
```
Note: `validate_publication` runs 29 times in `run_mutations`; consider caching the 2.0.1 blob (cheap) or accept ~30 `git show` calls.

**`validate_signoff` parameterisation** (L509-528; needed by frozen reply). Today it compares to live constants:
```python
if 'authority_id' in record and record['authority_id'] != AUTHORITY_ID: errors.append('sign-off authority_id does not match')
if 'version' in record and record['version'] != VERSION: errors.append('sign-off version does not match')
```
Change signature to `validate_signoff(record, authority_lf_digest, authority_id=None, version=None)` defaulting to the module constants. Mutation gate call (L621) and `validate_published` (L698) keep the 2-arg form.

**Dry-run summary** (L533-548). Existing last block to retarget plus extend (D-09/D-10):
```python
dsha = lf_digest(GOVERNANCE_DECISIONS); sup = SUPERSEDED_V2_0_0
...
same = 'equals' if dsha == sup['governance_decisions_sha256'] else 'DIFFERS FROM'
lines += ['', f'Version {authority["version"]} supersedes {sup["authority_id"]} version {sup["version"]} (commit {sup["commit"][:7]}). No decision changed: the governance decisions LF sha256 {dsha} {same} the {sup["version"]} value.']
return '\n'.join(lines) + '\n'
```
Append a "What changed in 2.0.2" block built from `authority['source_lineage']` entries (`relative_path`, `normalisation`; AA1 manifest committed + `RAW_BYTES`), `len(NEGATIVE_MUTATIONS)`, a walk of `schema()` for `additionalProperties: False` levels, the D-08 comparison result, and one fixed GATE-01..05 line. Wording must avoid `best, critical, important, recommended, highest` (test checks entire dry-run output, test L744-760) and must not contain `Published on` / `PUBLISHED_ON`.

---

### Reply validator freeze (`scripts/build_archive_assessment_demo3_w1_req_001_reply.py`)

**Analog:** `CATALOG_COMMIT` constant + `V2.git_show` helper in the publisher (L45-46, L93 `catalog_bytes()` = `git_show(CATALOG_COMMIT, CATALOG_REL)`).

**Imports/V2 loader** (L1-16): reply script loads the publisher as `V2` via `importlib.util.spec_from_file_location`; reuse `V2.git_show`, `V2.load`-style JSON parse (`json.loads(V2.git_show(...).decode('utf-8'))`), `V2.lf_bytes`, `V2.jtext`, `V2.AuthorityError`. Script has no `import json`; add it (stdlib block, alphabetical).

**Constants to add** (near L20-31, single constants like `REMOTE_BRANCH`):
```python
REPLY_PUBLICATION_COMMIT = '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb'
REPLY_RECORD_COMMIT = '4d9b7c1f41df5fa7575d4653a7d54ff9cf0a192b'
```

**Live reads to replace** (current code):
- `check_inputs_bound(manifest)` L218-227 reads `V2.SIGNOFF`, `V2.OUT / V2.N_TRACE`, `V2.GOVERNANCE_DECISIONS` live.
- `load_inputs()` L230-236:
```python
authority, record, signoff = V2.load(V2.AUTHORITY), V2.load(V2.PUBLICATION_RECORD), V2.load(V2.SIGNOFF)
decisions, manifest = V2.load(V2.GOVERNANCE_DECISIONS), V2.load(V2.OUT / V2.N_MANIFEST)
if record['manifest_sha256'] != V2.lf_digest(V2.OUT / V2.N_MANIFEST): raise ...
check_inputs_bound(manifest)
```
Re-express with `git_show(REPLY_PUBLICATION_COMMIT, V2.rel(...))` for authority, sign-off, decisions, manifest, trace and `git_show(REPLY_RECORD_COMMIT, V2.rel(V2.PUBLICATION_RECORD))` for the record; digests via `hashlib.sha256(V2.lf_bytes(blob))`.
- `build_reply` L72 `V2.validate_signoff(signoff, record['authority_sha256'])` -> pass `authority_id`/`version` of the 2.0.1 record (parameterised validator above).
- `build_reply` L74-82: `V2.lf_digest(V2.GOVERNANCE_DECISIONS)` (twice, incl. `history_note`) -> use the pinned decisions blob digest. `history_note` is built from `authority['source_lineage']['supersedes']`; with the 31addfa authority this still yields 2.0.0 @ `54a7fd0`, so bytes are unchanged.
- `build_reply` also uses `resolve_record_commit()` for `pin.publication_record_commit` -> use constant.
- `validate_reply()` L239-255: stop comparing against live `V2.AUTHORITY` / `V2.OUT` at its tail (`record['authority_sha256'] != V2.lf_digest(V2.AUTHORITY)` L252). Compare committed reply JSON/MD bytes to the rebuild; keep the reply schema check against `schema()`.

**`resolve_record_commit`** keep the GATE-04 shallow check verbatim (L262-269), drop the `git log` (L270-275). Replace tail with a constant return after confirming existence/ancestry:
```python
try:
    s = git('rev-parse', '--is-shallow-repository')
except OSError as e:
    raise V2.AuthorityError(f'cannot check whether the clone is shallow: {e}') from e
if s.returncode != 0 or s.stdout.strip() != 'false':
    raise V2.AuthorityError('shallow clone or unreadable repository: cannot resolve the publication record commit; fetch full history')
# new: git cat-file -e / merge-base --is-ancestor REPLY_RECORD_COMMIT HEAD, else AuthorityError; return REPLY_RECORD_COMMIT
```
**`push_check`** (L279): currently `V2.load(V2.PUBLICATION_RECORD)['publication_commit']`; RESEARCH recommends `REPLY_PUBLICATION_COMMIT` (open question 1, flag in plan).

**`--build` path** (L305-314) uses `load_inputs()` too; the build and validate must share the frozen loader. Reply files must not change (byte equality).

---

### Tests: retarget and extend (analogs inside each file)

**`test_archive_assessment_applicability_authority_v2.py`**: L144 `MODULE.VERSION == '2.0.1'` -> `'2.0.2'` (same test `test_version_constants_and_published_on_removed` also lives at publication tests, grep shows it asserts `'2.0.1'` and `-2.0.1`); L204 `lin['supersedes'] == MODULE.SUPERSEDED_V2_0_0` -> `_V2_0_1`; L212 `test_committed_schema_equals_schema_function` stays red until the schema is regenerated in the publication commit.

**`test_archive_assessment_applicability_authority_v2_publication.py`**
- Rename L75, L78, L485 (`superseded_record`), L495, L685, L752. Pattern for pre-publication record fixture (L484-491):
```python
def superseded_record(blobs, **over):
    s = MODULE.SUPERSEDED_V2_0_0
    rec = {'publication_commit': s['commit'], 'authority_id': s['authority_id'], 'version': s['version'], 'authority_sha256': s['sha256'], 'manifest_sha256': MODULE.lf_digest(MODULE.OUT / MODULE.N_MANIFEST), 'digest_normalisation': 'CRLF_TO_LF'}
    rec.update(over)
    MODULE.dump(MODULE.PUBLICATION_RECORD, rec)
    blobs[(s['commit'], MODULE.rel(MODULE.AUTHORITY))] = b'superseded ... authority bytes\n'
```
and `test_pre_publication_mode_accepts_only_superseded_record` (L493-505) which fetches the real blob with `git show {commit}:{relative_path}` and asserts its LF sha equals `s['sha256']`. `test_pre_publication_wrong_commit_or_digest_fails` (L514-521) uses `match='2.0.0 publication commit'` and `'2.0.0 digest'`: change to 2.0.1. L183 (`match='2.0.0'`) per RESEARCH.
- `test_publication_commit_ancestor_and_file_set` (L642-663): add schema path to `expected` (`schemas/archive_assessment_applicability_authority_v2.schema.json`) because the 2.0.2 commit includes the regenerated schema; current logic `present == expected` and `set(files) <= expected` and required subset `{auth_rel, signoff_rel, manifest}`. Keep the "no adjudication/policy files" assertion.
- `test_manifest_publisher_script_digest_matches_publication_commit` (L666-): unchanged; requires the publisher script be committed before `--publish`.
- Keep `test_superseded_constants_match_git_history` (L682-694) and `test_rows_equal_2_0_0_rows_and_only_identity_and_lineage_differ` (L696-709) (preferred per CONTEXT) and add 2.0.1 analogues. Template:
```python
def test_superseded_constants_match_git_history():
    reason = git_ready()
    if reason: pytest.skip(reason)
    sup = MODULE.SUPERSEDED_V2_0_0
    auth_bytes = git('show', '54a7fd0:registry/archive_assessment_applicability_authority_v2.json').stdout
    ...
    rec = json.loads(git('show', '0ce89f2:registry/..._publication_record.json').stdout.decode('utf-8'))
    assert sup['commit'] == rec['publication_commit'] and sup['sha256'] == rec['authority_sha256']
```
  2.0.1 version: `31addfa` blob for authority/decisions and `4d9b7c1:...publication_record.json` for record. Row-comparison test: `old['controls'] == new['controls']` pattern, plus a tampered-row case that expects `AuthorityError` via `MODULE.validate_publication`.
- `test_dry_run_summary_lists_decisions_rules_and_supersession` (L744-760): update the asserted strings (`version 2.0.0 (commit 54a7fd0)` -> `version 2.0.1 (commit 31addfa)`, `equals the 2.0.1 value`) and add assertions for the "what changed" section; keep forbidden-word loop.
- `test_mutation_records_shape` (~L762): count 29 stays; update `supersedes_governance_digest_differs` description only if the test inspects it.
- D-04 byte-identity test: copy the `git_ready()` + `@pytest.mark.skipif(not REAL_RECORD.exists(), ...)` pattern from L630-663; assert `git diff --quiet <pub> <recordcommit> -- <paths>` returns 0, with pub from the live record and the record commit from `git log -n1 --format=%H -- <record>`.

**`test_archive_assessment_lineage_validation.py`** L34 (`for commit in (MODULE.V1_BASELINE_COMMIT, MODULE.SUPERSEDED_V2_0_0['commit'])`) and L55 (`sup = MODULE.SUPERSEDED_V2_0_0`): rename.

**`test_archive_assessment_demo3_w1_req_001_reply.py`**
- Helpers to reuse (L300-322): `git(*args)` (`subprocess.run(..., capture_output=True)` wrapped in `CompletedProcess`), `git_ready()`, `lf_sha`.
- Rewrite `test_record_commit_is_last_change_of_the_record` (L332-345; asserts `resolve_record_commit()==git log` of the live record): replace with assertion that `resolve_record_commit() == MODULE.REPLY_RECORD_COMMIT`, that commit changed exactly the record file, and a constant-vs-git test (`4d9b7c1` expands to the 40-hex constant; `31addfa` likewise).
- Fake git pattern (L348-380) stays for the shallow cases, but `fake_shallow_git` raises `AssertionError('unexpected git command')` for anything except `rev-parse` and `log`; extend it to answer the new `cat-file` / `merge-base` calls and rewrite `test_resolve_record_commit_full_clone_passes_through` (`== 'd'*40`) to return the constant. Keep `assert not any(a[0]=='log' ...)`-style negative check (now: no `log` call at all).
- `test_history_note_binds_to_supersedes_and_decisions` (L382-395): `inputs()` reads live files; point it at the frozen loader; still asserts `sup['commit']=='54a7fd09...'`, `r['pin']['authority_id'].endswith('2.0.1')`.
- Add the three tests required by D-02: (1) validator passes with live record/authority at 2.0.2 (run `validate_reply` against the real tree, skip if `git_ready()`), (2) tamper of reply bytes or constants -> `V2.AuthorityError`, (3) fail closed with no history (use `fake_shallow_git`/`monkeypatch.setattr(MODULE.V2, 'git_show', raise GitHistoryError)`).
- Monkeypatching `V2.SIGNOFF` / `V2.GOVERNANCE_DECISIONS` (L79-100 per RESEARCH) no longer proves tamper for frozen inputs: patch `V2.git_show` or the constants instead.
- `test_publication_sha_is_ancestor_and_holds_authority` (L324-330) stays valid against the live 2.0.2 record; pair with an assertion on `REPLY_PUBLICATION_COMMIT`.

---

### Publication artefacts and commits (process analog: `31addfa`, `4d9b7c1`)

`git show --stat 31addfa` (2.0.1): 8 files only: authority, sign-off, matrix, semantic validation, negative-invariant validation, certification, publication md, manifest (traceability was byte-identical and schema unchanged then). For 2.0.2 expect 12 paths: schema, authority, sign-off, plus the 7 generated files in `generated/archive-assessment/ems-aa3-v2/` (all carry `published_on`, so traceability changes too). Record commit `4d9b7c1` touches only `registry/archive_assessment_applicability_authority_v2_publication_record.json` (5 ins/5 del) — repeat exactly.

Sequence mirrors 06-06/06-07: code commits (explicit-path) -> `--emit-schema` -> `--publish --dry-run` (note `--dry-run` works only with `--publish`) -> checkpoint -> write sign-off (keys exactly `status, approval{approver,role,date,scope}, dual_role_statement, authority_id, version, authority_sha256, authority_sha256_normalisation`) -> `--publish` -> `git add -- <12 paths>` -> `git diff --cached --name-only` -> commit -> `--validate --pre-publication` -> `--record-publication <sha>` -> record commit -> plain `--validate`.

## Shared Patterns

### Fail-closed history read
**Source:** `scripts/publish_archive_assessment_applicability_authority_v2.py` L338-344 (`git_show`), L610-631 (`mutation_gates` re-raises `GitHistoryError`).
**Apply to:** D-08 row comparison, frozen reply inputs, any new test fake. Git failure = `GitHistoryError`; content mismatch = `AuthorityError`.

### Deterministic serialisation and LF digests
**Source:** publisher L69-71, L496-497.
```python
def lf_bytes(b: bytes) -> bytes: return b.replace(b'\r\n', b'\n')
def lf_digest(p: Path) -> str: return hashlib.sha256(lf_bytes(p.read_bytes())).hexdigest()
def jtext(value: object) -> str: return json.dumps(value, indent=2, sort_keys=True) + '\n'
def sha_text(text: str) -> str: return hashlib.sha256(text.encode('utf-8')).hexdigest()
```
**Apply to:** all digest checks. Use these; do not add helpers.

### Git test guard
**Source:** publication tests L632-638 / reply tests L306-317 `git_ready()`; `@pytest.mark.skipif(not REAL_RECORD.exists(), ...)`.
**Apply to:** every new test that reads real history (D-04, D-08, constant-vs-git).

### Explicit-path staging
**Apply to:** every commit. Never `git add -A/.`/`-a`. Dirty tree holds ` M .planning/config.json`, ` M registry/adjudication_rules.json`, ` M registry/policy_decisions.json` and many untracked files. Verify with `git diff --cached --name-only` before and `git show --stat --format= <sha>` after.

### Style
Publisher: compact single-quote one-liners (`if cond: errors.append(...)`). Reply script: double-line multi-line formatting with 4-space indent and single quotes already used; match the file being edited. Messages in `raise AuthorityError(...)` are matched by tests with `match=`, so keep stable substrings.

## No Analog Found

| File / function | Role | Data Flow | Reason |
|---|---|---|---|
| D-04 publication-file byte-identity check (`git diff --quiet <pub> <record> -- <paths>`) | test / verification step | git read | No existing pub-vs-record comparison; compose from `git_ready()` + `git()` helpers and `test_publication_commit_ancestor_and_file_set` scaffolding |
| "What changed in 2.0.2" dry-run block | utility | transform | `dry_run_summary` has no change section; derive from `authority['source_lineage']`, `NEGATIVE_MUTATIONS`, `schema()` |
| D-05 push + `gh workflow run` + run watch | process | event-driven | No script; follow STATE.md workaround and Pitfall 7/8 of RESEARCH (workflow triggers: `pull_request`, push to `main`, `workflow_dispatch`; precedent runs 38743651222 and 38744767442) |

## Metadata

**Analog search scope:** `scripts/publish_archive_assessment_applicability_authority_v2.py`, `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, `tests/test_archive_assessment_*.py`, git commits `31addfa`, `4d9b7c1`.
**Files scanned:** 6 source/test files plus 2 commit stats.
**Pattern extraction date:** 2026-11-12
