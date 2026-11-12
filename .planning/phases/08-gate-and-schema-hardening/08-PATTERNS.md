# Phase 8: Gate and Schema Hardening - Pattern Map

**Mapped:** 2026-11-11
**Files analyzed:** 8 (3 scripts modified, 5 test files modified or extended)
**Analogs found:** 8 / 8 (all analogs are in-file or sibling code; no new files are created)

All line numbers are from the working tree on 2026-11-11 and are valid until the scripts are next edited. No new source files are created. Style: the publisher is single-quote, compact one-line helpers, `errors = []` joined and raised as `AuthorityError`.

## File Classification

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/publish_archive_assessment_applicability_authority_v2.py` (catalog pin, GATE-03) | utility/validator | file-I/O via git blob | same file `git_show` L319 + `COMMIT_PINNED` L317 + `v1_baseline` entry | exact |
| same file (record gate + `--pre-publication`, GATE-01) | validator/CLI | request-response | same file `validate_published` L679-684, `write_publication_record` L686, `main` L693 | exact |
| same file (`mutation_gates`, GATE-02) | validator | transform | same file L584-601 (narrow the `except` tuples) | exact |
| same file (`schema()`, SCHEMA-07) | config generator | transform | same file `schema()` L347-382 (existing `additionalProperties:False` on `cond`, `rule`, `lineage`, `field_definitions`) | exact |
| `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` (GATE-04) | utility | request-response (git CLI) | same file `git()` L258, `resolve_record_commit` L262; sibling `git_ready()` in tests | exact |
| `scripts/build_archive_assessment_governance_decisions.py` (GATE-05) | validator | transform | same file `strict_checks` L151-163, `answers_digest` L87 | exact |
| `tests/test_archive_assessment_applicability_authority_v2_publication.py` | test | unit with `env` fixture | same file `env` L215-225, record tests L436-470, mutation tests L633-671 | exact |
| `tests/test_archive_assessment_lineage_validation.py` | test | temp git repo | same file `fx` L50-81, tamper tests L93-149 | exact |
| `tests/test_archive_assessment_demo3_w1_req_001_reply.py` | test | monkeypatched git | same file `fake_git` L266-298 | exact |
| `tests/test_archive_assessment_governance_answers.py` (and `..._governance_decisions.py`) | test | unit | same file `filled()` L30-37, `strict_invalid` L41 | exact |
| `tests/test_archive_assessment_applicability_authority_v2.py` | test | unit | schema tests (L37, L174) | role-match |

## Pattern Assignments

### Publisher: catalog pin (GATE-03, D-07..D-10)

**Analog:** `git_show` and the `v1_baseline` commit-pinned entry in the same script.

**git_show (the only subprocess site; reuse, do not add another)** (L319-325):
```python
def git_show(commit: str, relative_path: str) -> bytes:
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit): raise AuthorityError(f'{relative_path}: commit must be a 40-character lowercase hex SHA')
    if bad_rel(relative_path): raise AuthorityError(f'{relative_path}: path must be repo-relative without ..')
    try: r = subprocess.run(['git', 'show', f'{commit}:{relative_path}'], cwd=ROOT, capture_output=True)
    except OSError as e: raise AuthorityError(f'{relative_path}@{commit[:7]}: git unavailable: {e}') from e
    if r.returncode != 0: raise AuthorityError(f'{relative_path}@{commit[:7]}: git show failed: {r.stderr.decode("utf-8", "replace").strip()}')
    return r.stdout
```

**Catalog read to replace** (L90-95, currently `CATALOG.read_text`):
```python
def catalog_controls() -> list[dict]:
    data = yaml.safe_load(CATALOG.read_text(encoding='utf-8'))
    controls = data.get('controls', [])
    ids = [c.get('control_id') for c in controls]
    if len(controls) != 80 or len(set(ids)) != 80 or any(not x for x in ids):
        raise AuthorityError('controlled catalog does not contain exactly 80 unique control IDs')
```
Replace the first line with a decode of `lf_bytes(git_show(CATALOG_COMMIT, CATALOG_REL))` (add `def catalog_bytes()`; `CATALOG_COMMIT = V1_BASELINE_COMMIT` defined at L46, `CATALOG_REL` at L74). Always `lf_bytes()` before hashing or YAML decode (CRLF pitfall).

**Commit-pinned join** (L317, L341-342):
```python
COMMIT_PINNED = {'supersedes', 'supersedes_governance_decisions', 'v1_baseline'}   # add 'catalog_reference'
...
if label in COMMIT_PINNED and not commit: errors.append(f'{label}: commit-pinned entry must carry a commit'); continue
try: data = git_show(commit, path) if commit else (ROOT / path).read_bytes()
```
`validate_lineage` already includes `catalog_reference` in its label loop (L331) and reads `e.get('commit')`, so only the set membership and the entry's `commit` field are needed.

**Schema entry to extend** (L363, `catalog_reference`): add `'commit':{'const':CATALOG_COMMIT}` to `properties` and `'commit'` to `required`. Pattern for a pinned `const` commit: `pinned(...)`/`v1_baseline` entry at L361.

**Build site** (L170): `catalog_reference` uses `lf_digest(CATALOG)`; replace with `hashlib.sha256(lf_bytes(catalog_bytes())).hexdigest()` and add `'commit': CATALOG_COMMIT`. Other live reads: L241 (via `catalog_controls`) and L306 (digest in `validate_publication`); that L306 check must also require `commit == CATALOG_COMMIT` and `relative_path == CATALOG_REL` (D-10 tamper directions).

**Other users of live `CATALOG`** (research grep): `tests/test_archive_assessment_applicability_authority_v2_publication.py:78` (`lf_digest(MODULE.CATALOG)`) must be updated; `scripts/validate_archive_assessment_rule_proposals.py:90` calls `V2.catalog_controls()` (behaviour unchanged, bytes identical at pin). Do NOT copy `frozen_catalog()` skip-on-missing-history behaviour from that script (L78-87); D-09 requires fail closed.

### Publisher: record gate and `--pre-publication` (GATE-01, D-01..D-03)

**Analog:** same file. The block to replace (L679-683):
```python
    if PUBLICATION_RECORD.exists():
        record = load(PUBLICATION_RECORD)
        if record.get('authority_id') == a['authority_id']:
            if record.get('authority_sha256') != lf_digest(AUTHORITY): raise AuthorityError('publication record authority_sha256 does not match the committed authority')
            if record.get('manifest_sha256') != lf_digest(OUT / N_MANIFEST): raise AuthorityError('publication record manifest_sha256 does not match the committed manifest')
    print('PASS')
```
Keep the two message strings (existing tests match on `key`). Record keys are exactly the six written by `write_publication_record` (L689):
```python
record = {'publication_commit': sha, 'authority_id': a['authority_id'], 'version': a['version'], 'authority_sha256': lf_digest(AUTHORITY), 'manifest_sha256': lf_digest(OUT / N_MANIFEST), 'digest_normalisation': 'CRLF_TO_LF'}
```
Check the key set before indexing so `KeyError` is impossible (shape-first, D-05 style). Pre-publication mode compares against `SUPERSEDED_V2_0_0` (L37-45: has `authority_id`, `version`, `commit`, `sha256`, `relative_path`, ...). D-03 uses `git_show(record['publication_commit'], rel(AUTHORITY))` and `git_show(..., f'{rel(OUT)}/{N_MANIFEST}')`, hashed with `hashlib.sha256(lf_bytes(...))`. A full sketch is in 08-RESEARCH.md "D-03 record cross-check body".

**CLI wiring pattern** (L693-701, one-line argparse chain; add `--pre-publication` the same way):
```python
parser = argparse.ArgumentParser(); parser.add_argument('--validate', action='store_true'); ... parser.add_argument('--record-publication', metavar='SHA'); args = parser.parse_args()
if args.validate: validate_published()
...
else: parser.error('one of --validate, --emit-schema, --validate-signoff, --publish or --record-publication is required')
```
Change to `validate_published(args.pre_publication)` and `parser.error(...)` when `--pre-publication` is given without `--validate`.

### Publisher: mutation gate (GATE-02, D-04..D-06)

**Analog:** `mutation_gates` L584-601. Narrow every tuple (current):
```python
try: validate_publication(doc)
except (AuthorityError, KeyError, TypeError, AttributeError): gates.append('PYTHON_VALIDATOR')   # -> except AuthorityError
...
try: validate_signoff(doc, authority_digest)
except (AuthorityError, KeyError, TypeError, AttributeError): ...                                 # -> except AuthorityError
...
try: b.validate_decisions(doc)
except (ValueError, KeyError, TypeError, AttributeError): ...                                     # -> except ValueError
```
Schema gates already catch only `jsonschema.ValidationError`. Output shape unchanged (`sorted(gates)`, D-06). Research probe: all 26 existing mutations already raise `AuthorityError`, so D-05 needs no validator rewrite; add a regression test. Do not touch `validate_governance_decisions` L574-582 (it deliberately wraps KeyError/TypeError/AttributeError into `AuthorityError`, a different path).

### Publisher: schema strictness (SCHEMA-07)

**Analog:** the already-closed objects in the same `schema()`:
```python
cond = {'type':'object','additionalProperties':False,'required':['field','state'],'properties':{...}}      # L348
lineage = {'type':'object','additionalProperties':False, ...}                                              # L357
```
Add `'additionalProperties':False` to `sem` (L368), the top-level dict (L370) and the control-row `items` (L377). First declare the 14 properties real documents use (research measured against `build_published_authority()`): top level `$schema, applicability_vocabulary, attestation_prohibitions, classification_vocabulary, evidence_boundary`; `not_applicable_semantics` `fields_not_usable_in_rules_statement, statements`; row `archive_evidence_capability, catalog_scope, classification_prerequisites, control_name, required_non_repository_authority, unresolved_reason`. Use minimal typing in the same terse style as the existing property dicts. The row `allOf` branches (L382) rely on the row's own `properties` staying complete.

**New mutations** follow the `Mutation` NamedTuple (L415) / `NEGATIVE_MUTATIONS` (L441-468) pattern; read those lines when planning (not excerpted here). Use `target='AUTHORITY'`, `schema_must_reject=True`. Update count assertions at publication tests L633-637 (`len(ids)==26`, `ids[:17]==PREVIOUS_17`, `set(ids[17:])==set(NEW_9)`) and `test_certification_and_semantic_files_are_derived` (~L699, `len(...)==26`).

### Reply builder: shallow check (GATE-04, D-11)

**Analog:** same file L258-267:
```python
def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)

def resolve_record_commit() -> str:
    r = git('log', '-n1', '--format=%H', '--', V2.rel(V2.PUBLICATION_RECORD))
    sha = r.stdout.strip()
    if r.returncode != 0 or not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise V2.AuthorityError('cannot resolve the publication record commit from git')
    return sha
```
Insert, before the `log` call, a `git('rev-parse', '--is-shallow-repository')` guard: wrap `OSError` into `V2.AuthorityError`, and raise `V2.AuthorityError` containing "shallow" when returncode != 0 or `stdout.strip() != 'false'` (text mode, so compare to str). Error class is `V2.AuthorityError`. Existing in-file pattern for the same git-CLI-with-return-code style: `push_check` (L273+).

### Decisions builder: cross-note uniqueness (GATE-05, D-13 grandfather by digest)

**Analog:** `strict_checks` L151-163 and normalisers L69-71.
```python
def norm(text: str) -> str: return ' '.join(text.casefold().split())
def norm_templated(text: str) -> str: return ' '.join(re.sub(r'ems-ctrl-[0-9]+|[0-9]+', '', norm(text)).split())
...
if norm_templated(n) in {norm_templated(x) for x in drafted_strings(p)}: errors.append(f'{cid}: note repeats drafted text')
if norm(n) in seen: errors.append(f'{cid}: note repeats the note of {seen[norm(n)]}')
seen.setdefault(norm(n), cid)
```
Only cross-note site is L162-163. Strict form: `k = norm_templated(n)` for lookup and `setdefault`. Grandfather: pick the key function via a named module constant holding the SHA-256 of the committed answers (equal to the committed decisions' `answers_sha256`; digest recipe is `answers_digest(path) = V2.lf_digest(path)` L87, LF-normalised file bytes).

Wiring risk the planner must resolve: `validate_answers(a, proposals, strict)` L119 and `strict_checks(entries, proposals, errors)` L151 receive the parsed object, not bytes or a path. Callers: `build_decisions` L208 (receives `answers_sha256` already as a parameter), `build_from_files` L358-363 (has `answers_digest(ANSWERS)`), CLI L402 (loads `ANSWERS`). Options: add an optional `answers_sha256: str | None = None` parameter threaded `validate_answers -> strict_checks` and passed from all three callers; or recompute from the object with `sha_text(V2.jtext(a))` only if the committed file is byte-identical to canonical `jtext` (verify before relying on it; `V2.dump` L80 writes it). The threaded-parameter option is safer. With `None` digest the strict `norm_templated` check applies (default strict, so synthetic test inputs get strict behaviour).

**Test fixture hazard:** `filled()` in `tests/test_archive_assessment_governance_answers.py` L34 builds `note=f'Reviewed {c} individually and kept the draft.'`, which collapses to one string under `norm_templated`. Every strict-passing test (`test_strict_matrix_base_passes` L101, `test_changed_*_passes` L129-148, plus the decisions-test fixtures behind `tests/test_archive_assessment_governance_decisions.py` L340-409) will fail unless the fixture notes are made to differ by non-numeric words (for example a per-control word list). This is a test edit that is expected and must be named in the plan. Also check `test_notes_differing_in_case_and_whitespace_fail` L110 and `test_identical_notes_fail` L107, which should still fail.

### Tests: `env` fixture and record tests (publication test file)

**Analog:** `env` L215-225:
```python
@pytest.fixture
def env(monkeypatch, lineage_calls):
    monkeypatch.setattr(MODULE, 'validate_lineage', lambda lin: lineage_calls.append(lin))
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for name, value in {'ROOT': root, 'AUTHORITY': root / 'registry' / 'a.json', ... 'PUBLICATION_RECORD': root / 'registry' / 'record.json', 'OUT': root / 'generated' / 'out', 'SCRIPT': root / 'scripts' / 'pub.py'}.items():
            monkeypatch.setattr(MODULE, name, value)
        ...
        yield root
```
Once catalog reads and the D-03 check go through `git_show` (which runs with `cwd=ROOT`, now an empty temp dir), this fixture must also stub `catalog_bytes` (capture real bytes before patching `ROOT`) and provide a fake `git_show` for record commit reads (dict `(commit, path) -> bytes`), or `git init` the temp root. Record tests that use `'a' * 40` (L436-470: `test_write_publication_record`, `test_validate_record_matching_passes`, `test_validate_record_digest_mismatch_fails`) need the fake. `test_validate_record_absent_passes` L447 becomes a must-raise test; `test_validate_record_other_authority_id_is_pending` L457 becomes: plain raises, `pre_publication=True` with a record naming `SUPERSEDED_V2_0_0` passes, 9.9.9 raises in both modes.

**Mutation tests analog:** L644-655 `test_each_mutation_is_rejected_by_its_gates` (parametrized over `MODULE.NEGATIVE_MUTATIONS`, calls `mutation_gates`), and L665-671 `test_accepted_mutation_aborts_build_and_writes_nothing` as the model for the "non-domain exception propagates and nothing is written" test:
```python
monkeypatch.setattr(MODULE, 'NEGATIVE_MUTATIONS', noop)
write_signoff()
with pytest.raises(AuthorityError, match='was accepted'):
    MODULE.publish(False)
assert not MODULE.AUTHORITY.exists() and not MODULE.OUT.exists()
```
For GATE-02, monkeypatch `MODULE.validate_publication` / `validate_signoff` / the decisions builder's `validate_decisions` to raise `KeyError`, `TypeError`, `AttributeError` and assert `pytest.raises(<that class>)` out of `mutation_gates`.

### Tests: temp git repo for catalog pin and tamper (lineage test file)

**Analog:** `fx` L50-81 (`git init`, `.gitattributes '* -text'`, `-c core.autocrlf=false`, identity config, commit, then a `lin` dict of `MODULE.digest_entry(...)`). Required fixture change (Pitfall 4): L71 builds `catalog_reference` without a commit:
```python
'catalog_reference': MODULE.digest_entry(MODULE.CATALOG_REL, sha('CRLF_TO_LF', rd(MODULE.CATALOG_REL)), 'CRLF_TO_LF'),
# -> pass the commit as the v1_baseline entry does (L73): ..., 'CRLF_TO_LF', commit)
```
Then the working-tree tamper parametrization L93-107 (`('catalog_reference','CRLF_TO_LF')`, `changed_byte`) no longer applies to the catalog: move `catalog_reference` into the commit-pinned parametrizations at L114, L129, L144 (and the later ones at ~L152, L187), and mirror `test_d11_commit_pinned_uses_blob_not_working_file` (L137-141) to prove a live working-tree edit does not change the result:
```python
(root / MODULE.V1_BASELINE_REL).write_bytes(b'changed in working tree\r\n')
assert MODULE.validate_lineage(lin) is None
```
`test_d10_nonexistent_commit_raises` L144-149 (`lin[label]['commit'] = '0' * 40`) is the model for fail-closed on missing history. The `git_ready()` helper (L28-37) is the pattern for skipping tests that need real full history; it already checks `--is-shallow-repository`.

### Tests: reply shallow check

**Analog:** `fake_git` and monkeypatch pattern in `tests/test_archive_assessment_demo3_w1_req_001_reply.py` L266-298:
```python
def fake_git(ls_remote_rc=0, cat_file_rc=0, merge_base_rc=0):
    def run(*args):
        if args[0] == 'ls-remote': ...
        raise AssertionError(f'push-check ran an unexpected git command: {args}')
    return run
monkeypatch.setattr(MODULE, 'git', fake_git(**kwargs))
```
Write a `fake_git` variant answering `rev-parse` (stdout `'true\n'`, `'false\n'`, nonzero rc, or raising `OSError`) and `log`. Return `subprocess.CompletedProcess(args, rc, out, '')`. Existing real-file tests (`test_record_commit_is_last_change_of_the_record` ~L332) must remain green on a full clone.

## Shared Patterns

### Fail closed with `AuthorityError`, errors list joined
**Source:** `validate_lineage` L327-345 (`errors = []`, per-label `errors.append(...)`, `continue`, `raise AuthorityError('; '.join(errors))`).
**Apply to:** the new record-check helper, catalog validation, any shape guards.

### Shape before key access
**Source:** `validate_lineage` L330-336 (`e = e if isinstance(e, dict) else {}`; `.get`) and `git_show`/`bad_rel` L315.
**Apply to:** the record check (verify `isinstance(record, dict)` and key set before indexing) and validator hardening for D-05.

### Git access only through `git_show` (publisher) and `git()` (reply)
**Apply to:** all new git reads. Two source-scan tests (`test_module_does_not_call_git` ~L91, `test_publisher_source_runs_no_subprocess_or_evaluator` ~L702 in the publication test file) forbid new `subprocess` use in the publisher outside `git_show`.

### LF-normalised digests
**Source:** `lf_bytes` L67, `lf_digest` L68; `NORMALISERS` (used at L344).
**Apply to:** every digest of a git blob or file (`hashlib.sha256(lf_bytes(b)).hexdigest()`).

### Deterministic JSON
**Source:** `jtext` L470 (`json.dumps(value, indent=2, sort_keys=True) + '\n'`). Not changed this phase; nothing committed is regenerated.

## No Analog Found

None. Every change extends an existing function with an in-file or sibling pattern. The one genuinely new design is the digest-threading for the GATE-05 grandfather (see wiring risk above), which has no existing precedent in the decisions builder; `answers_digest` and the `answers_sha256` parameter of `build_decisions` L207 are the nearest hooks.

## Metadata

**Analog search scope:** `scripts/` (three target scripts, `validate_archive_assessment_rule_proposals.py` referenced via research), `tests/test_archive_assessment_*.py`.
**Files read this session:** 3 scripts (targeted ranges), 5 test files (targeted ranges), plus CONTEXT.md and RESEARCH.md.
**Not re-read:** `NEGATIVE_MUTATIONS` L415-468 and `validate_signoff` L483-502 (planner should read them before editing; not excerpted here).
**Pattern extraction date:** 2026-11-11
