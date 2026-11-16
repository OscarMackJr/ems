# Phase 12: Verify-at-Pin and Gate Hardening - Pattern Map

**Mapped:** 2026-11-16
**Files analyzed:** 13 (11 modified, 1 new planning ledger, 1 optional doc touch)
**Analogs found:** 13 / 13. Every file is a modification of an existing file, or follows a direct in-repo precedent.

All line numbers are at HEAD `b34263f` (the code has not changed since `663abf7`).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/publish_archive_assessment_applicability_authority_v2.py` (MOD) | utility / CLI publisher + validators | file-I/O + git read (request-response CLI) | itself: `git_show` L359-365, `validate_published` L713-738, `check_publication_record` L742-757, `main` L766-776; builder `load_checked` L90-92; reply `resolve_record_commit` L341-353 | exact (self) |
| `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` (MOD, frozen; IN-04 only) | utility / frozen validator | git read | itself L337-353 (`git`, `resolve_record_commit`); publisher `git_show` L362-364 (OSError wrap) | exact |
| `tests/test_archive_assessment_applicability_authority_v2_publication.py` (MOD) | test | file-I/O + faked git | itself: `env` L226-241, `fake_git_show` L389-405, `superseded_record` L496-503, real-git test L594-606, CLI tests L608-620 | exact |
| `tests/test_archive_assessment_applicability_authority_v2.py` (MOD, move commit) | test | literal / constant | itself L142 (`test_version_and_authority_id_come_from_constants`), L202-204 (`test_supersedes_and_v1_baseline_follow_constants`) | exact |
| `tests/test_archive_assessment_lineage_validation.py` (MOD) | test | git-backed fixtures | itself L25-29 (`git`, `PINNED_COMMITS`), L41-60 (`fx`), L333-353 (D-10 test) | exact |
| `tests/test_archive_assessment_normalisation_claims.py` (MOD, move commit) | test | constant reference | `test_archive_assessment_lineage_validation.py` L29 (same `PINNED_COMMITS` line) | exact |
| `tests/test_archive_assessment_governance_answers.py` (MOD, GATE-09 D-13) | test | real-bytes file copy | itself L134-150 (`answers_copy`, `test_appended_answers_byte_removes_exemption_through_real_paths`) | exact |
| `tests/test_archive_assessment_governance_decisions.py` (MOD, GATE-08) | test | CLI path with real bytes | itself L332-340 (`test_validate_rejects_file_differing_from_rebuild`, which drives `main --validate`); answers L134-150 for the real-bytes copy | exact |
| `tests/test_archive_assessment_demo3_w1_req_001_reply.py` (MOD, IN-03/IN-04) | test | faked git | itself L342-391 (`fake_shallow_git`, `resolve_record_commit` tests); L566-581 `frozen_publisher` (IN-02 reuse) | exact |
| `tests/conftest.py` (MOD, D-10) | test harness / hookwrapper | event (pytest hooks) | itself L24-32 | exact |
| `tests/aa_history.py` (MOD, D-11) | test utility | git read | itself L10, L25-26 | exact |
| `tests/test_archive_assessment_skip_guard.py` (MOD, D-10/D-11) | test (subprocess pytest) | subprocess | itself L36-53 (`run_case`), L93-104, L168-175 | exact |
| `.github/workflows/ems-validate.yml` (MOD, D-09) | config / CI | batch | itself L87-90 | exact |
| `.planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md` (NEW) | planning ledger | n/a | `.planning/phases/09-certified-republication-2-0-2/09-BASELINE-RED.md` | exact |

---

## Pattern Assignments

### `scripts/publish_archive_assessment_applicability_authority_v2.py` (CLI publisher, file-I/O + git)

**Style rule:** compact, single quotes, one-line guards `if ...: raise AuthorityError('...')`, and helpers defined on one line where they fit. Exceptions are `AuthorityError(ValueError)` and `GitHistoryError(AuthorityError)` (L66-67). Do not introduce new exception types.

**Git seam analog: `git_show`, L359-365.** Copy this exactly for the new `git_run` and its typed helpers. It validates the SHA and path first, wraps `OSError` as `GitHistoryError`, and turns a non-zero rc into `GitHistoryError` that carries stderr.
```python
def git_show(commit: str, relative_path: str) -> bytes:
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit): raise AuthorityError(f'{relative_path}: commit must be a 40-character lowercase hex SHA')
    if bad_rel(relative_path): raise AuthorityError(f'{relative_path}: path must be repo-relative without ..')
    try: r = subprocess.run(['git', 'show', f'{commit}:{relative_path}'], cwd=ROOT, capture_output=True)
    except OSError as e: raise GitHistoryError(f'{relative_path}@{commit[:7]}: git unavailable: {e}') from e
    if r.returncode != 0: raise GitHistoryError(f'{relative_path}@{commit[:7]}: git show failed: {r.stderr.decode("utf-8", "replace").strip()}')
    return r.stdout
```
- Pitfall 4 (long paths): the optional change is `['git', 'show', f'{commit}:{relative_path}', '--']`.
- Traps: `git_show('HEAD', …)` raises because of the regex, so resolve HEAD to a SHA first. New helpers (`git_is_ancestor`) must apply the same 40-hex regex to the SHAs they receive before calling git.

**Shallow-check analog (reply builder L342-347).** Use it for `git_not_shallow()`. Because of the IN-09 lesson, the publisher version must show the raw output when it is neither `true` nor `false`:
```python
try:
    s = git('rev-parse', '--is-shallow-repository')
except OSError as e:
    raise AuthorityError(f'cannot check whether the clone is shallow: {e}') from e
if s.returncode != 0 or s.stdout.strip() != 'false':
    raise AuthorityError('shallow clone or unreadable repository: ...; fetch full history')
```

**Ancestry analog (reply builder L349-352).** Use it for `git_is_ancestor()`. The rc meanings are 0 for ancestor, 1 for not an ancestor, and anything else for a git error (raise `GitHistoryError`).
```python
if git('merge-base', '--is-ancestor', sha, 'HEAD').returncode != 0:
    raise AuthorityError(f'the frozen commit {sha} is not an ancestor of HEAD')
```

**Checked JSON loader analog: builder `load_checked`, `scripts/build_archive_assessment_governance_decisions.py` L90-92 (GATE-07).**
```python
def load_checked(path: Path) -> object:
    try: return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e: raise AuthorityError(f'{path.name}: invalid JSON at line {e.lineno} column {e.colno}: {e.msg}')
```
- The publisher's `load` (L86) has no guard, and `validate_published` uses it for AUTHORITY, SCHEMA, SIGNOFF, MANIFEST and RECORD (L716, L717, L722, L725, L744).
- Use `path.name` in messages, not `rel(p)`, which raises for paths outside ROOT.
- Do not change `load()` itself. `build_all_outputs` L588 and the tests use it.

**Domain-error wrapping analog: `validate_governance_decisions`, L629-637.** This is how the publisher already turns schema and shape errors into `AuthorityError`:
```python
    except (ValueError, jsonschema.ValidationError, KeyError, TypeError, AttributeError) as e:
        raise AuthorityError(f'governance decisions rejected: {e}') from e
```
GATE-07 schema-first order: `validate_published` L717 is today `validate_publication(a); jsonschema.Draft202012Validator(load(SCHEMA)).validate(a)`. Swap the two calls, then wrap `SchemaError` and `ValidationError`, and call `check_schema` first. The research gives code for this under Code Examples.

**Existing manifest shape guard style, L726-727.** Copy it for `if not isinstance(manifest, dict): raise AuthorityError(...)`. Place that check before `manifest.get` is called.
```python
ps = manifest.get('publisher_script')
if not isinstance(ps, dict) or ps.get('relative_path') != rel(SCRIPT) or not re.fullmatch(r'[0-9a-f]{64}', str(ps.get('sha256'))) or ps.get('sha256_normalisation') != 'CRLF_TO_LF': raise AuthorityError('manifest publisher_script entry missing or invalid')
```

**`validate_lineage` guard, L367-370 (GATE-07, direct-call shape).** `lin.get(...)` on a list raises `AttributeError`. Add a first line in the `L370` style:
```python
sup = lin.get('supersedes') if isinstance(lin.get('supersedes'), dict) else {}
```
The new first line is `if not isinstance(lin, dict): raise AuthorityError('source_lineage must be an object')`.

**Mode-parameterised record check, current shape L742-757.** Extend this function for D-02, D-06 and D-07. Do not duplicate it.
```python
def check_publication_record(a: dict, pre_publication: bool = False) -> None:
    ...
    if pre_publication:
        want_id, want_version = SUPERSEDED_V2_0_1['authority_id'], SUPERSEDED_V2_0_1['version']
        if record['publication_commit'] != SUPERSEDED_V2_0_1['commit']: raise AuthorityError('pre-publication record must name the 2.0.1 publication commit')
        if record['authority_sha256'] != SUPERSEDED_V2_0_1['sha256']: raise AuthorityError('pre-publication record authority_sha256 must equal the 2.0.1 digest')
    else: want_id, want_version = a['authority_id'], a['version']
    if record['authority_id'] != want_id or record['version'] != want_version: raise AuthorityError(f'publication record must name {want_id} version {want_version}')
    ...
    if hashlib.sha256(lf_bytes(git_show(record['publication_commit'], rel(AUTHORITY)))).hexdigest() != record['authority_sha256']: raise AuthorityError('... at the publication commit')
    if hashlib.sha256(lf_bytes(git_show(record['publication_commit'], rel(OUT / N_MANIFEST)))).hexdigest() != record['manifest_sha256']: raise AuthorityError('... at the publication commit')
```
- D-02: replace `SUPERSEDED_V2_0_1[...]` with `sup = a['source_lineage']['supersedes']`, and compare `authority_id`, `version`, `commit` and `sha256`.
- The messages must not hard-code a version. Use the 09 D-07 pattern, `f"... {sup['version']} ..."`.
- D-06 and D-07 run after L756-757, so the existing message matches (`'publication commit'`, `'git show failed'`) still hold.
- In plain mode, when the record equals `sup` (meaning HEAD is the pin), raise an error that names `--validate --at-pin`.

**D-05 path list.** Derive it from the constants L20-21, L444-458 and `rel` L519. `build_all_outputs` already enumerates the same set at L612-613:
```python
arts = [{'relative_path': rel(SCHEMA), 'sha256': ssh}, {'relative_path': rel(AUTHORITY), 'sha256': ash}, {'relative_path': signoff_rel, 'sha256': signoff_sha}]
arts += [{'relative_path': f'{rel(OUT)}/{n}', 'sha256': sha_text(t)} for n, t in outs.items()]
```
The ordered N_* list is in the test at L255: `[N_MATRIX, N_SEMANTIC, N_NEGATIVE, N_TRACE, N_CERT, N_REPORT, N_MANIFEST]`.

**JSON CLI result analog: `publish`, L711 (D-03 at-pin output).**
```python
print(json.dumps({'status': 'PASS', 'authority_sha256': ash, 'manifest_sha256': sha_text(outs[N_MANIFEST])}))
```
Plain `--validate` keeps `print('PASS')` (L738).

**CLI flag analog: `main`, L767-769 (D-01 rename).**
```python
... parser.add_argument('--pre-publication', action='store_true'); args = parser.parse_args()
if args.pre_publication and not args.validate: parser.error('--pre-publication requires --validate')
if args.validate: validate_published(args.pre_publication)
```
Replace the flag with `--at-pin` and `args.at_pin`. Keep no alias.

**Script digest (GATE-06):**
- Use the `lf_digest` helpers at L69-71 and the manifest `publisher_script` built at L614.
- The pinned check follows the test at L686-694: `lf(git_show(pub, rel(SCRIPT))) == manifest['publisher_script']['sha256']`.
- The `publisher_script_note` text at L615 becomes false. Change it only in the move commit, because the change alters manifest bytes.

**Supersedes move (09 D-07 precedent: commit `69ea357`, "bump to 2.0.2, supersede 2.0.1").** That commit renamed the constant and moved every use in one commit, touching the publisher, the v2 tests, the v2_publication tests and the lineage tests. The uses to move this time:
- L34: `VERSION`
- L36-44: the constant
- L176: `'supersedes': dict(SUPERSEDED_V2_0_1)`
- L243: `if sup != SUPERSEDED_V2_0_1: errors.append('... does not name the 2.0.1 publication')`
- L284: prev authority read for the PUB-08 row comparison
- L315, L318, L341: messages
- L400: schema `pinned(SUPERSEDED_V2_0_1, {...})`
- L559: dry-run `sup = SUPERSEDED_V2_0_1`
- L748-750: these go away with D-02

**Dry run IN-01 (L568-571).** The lead clause "No decision changed" at L569 is printed unconditionally. Make it depend on `same == 'equals' and not diff_ids and not set_differs`, which are already computed at L568 and L570. The gate line at L576 names "pre-publication mode" and "GATE-01 to GATE-05".

---

### `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` (frozen, IN-04 only)

**Analog: itself, L337-353.** `git()` uses `text=True`, so `stdout` is a str. Only the `rev-parse` call is wrapped in `try/except OSError`. The `cat-file` (L349) and `merge-base` (L351) calls are not wrapped, and any non-zero `merge-base` rc is reported as "not an ancestor".
```python
    for sha in (REPLY_RECORD_COMMIT, REPLY_PUBLICATION_COMMIT, REPLY_SCHEMA_COMMIT):
        if not re.fullmatch(r'[0-9a-f]{40}', sha) or git('cat-file', '-e', f'{sha}^{{commit}}').returncode != 0:
            raise AuthorityError(f'the frozen commit {sha} is not in the repository history; fetch full history (git fetch --unshallow)')
        if git('merge-base', '--is-ancestor', sha, 'HEAD').returncode != 0:
            raise AuthorityError(f'the frozen commit {sha} is not an ancestor of HEAD')
```
- Copy the `try/except OSError as e: raise AuthorityError(...) from e` from L343-345 for the two unwrapped calls.
- Keep the exact text "is not an ancestor of HEAD" for rc 1, because the test at L384 matches it.
- Freeze constraints: do not add `importlib`, `V2` or publisher strings, and do not use `exec`/`eval`. The Phase 11 scanner test at L708-728 enforces this.

---

### `tests/test_archive_assessment_applicability_authority_v2_publication.py` (test, faked git)

**Module load pattern (L10-18).** Every publisher test module loads the script this way:
```python
SCRIPT = Path(__file__).parents[1] / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py'
SPEC = importlib.util.spec_from_file_location('aa3_authority_v2_pub', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
```

**Source-scan seam, L88-95 and L966-969.** Update these in the same commit as `git_run`. Strip `git_run` (and every helper that contains `subprocess`) the same way `git_show` is stripped:
```python
def source_without_git_show():
    # D-10: subprocess is confined to git_show (and its import line)
    src = inspect.getsource(MODULE).replace('import subprocess\n', '', 1)
    return src.replace(inspect.getsource(MODULE.git_show), '', 1)

def test_module_does_not_call_git():
    assert 'subprocess' not in source_without_git_show() and 'import git' not in source_without_git_show()
    assert 'subprocess.run' in inspect.getsource(MODULE.git_show)
```

**`env` fixture, L226-241.** This is the temp ROOT with no git repository. It is the place to add the `git_head`, `git_is_ancestor`, `git_not_shallow` and `git_dirty` fakes with `monkeypatch.setattr(MODULE, ...)`.
```python
@pytest.fixture
def env(monkeypatch, lineage_calls):
    real_catalog = MODULE.catalog_bytes()
    monkeypatch.setattr(MODULE, 'catalog_bytes', lambda: real_catalog)
    monkeypatch.setattr(MODULE, 'validate_lineage', lambda lin: lineage_calls.append(lin))
    prev_blob, real_git_show, sup = prev_201_authority_bytes(), MODULE.git_show, MODULE.SUPERSEDED_V2_0_1
    monkeypatch.setattr(MODULE, 'git_show', lambda commit, path: prev_blob if (commit, path) == (sup['commit'], sup['relative_path']) else real_git_show(commit, path))
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for name, value in {'ROOT': root, 'AUTHORITY': root / 'registry' / 'a.json', 'SCHEMA': root / 'schemas' / 's.json', 'SIGNOFF': root / 'registry' / 'signoff.json', 'PUBLICATION_RECORD': root / 'registry' / 'record.json', 'OUT': root / 'generated' / 'out', 'SCRIPT': root / 'scripts' / 'pub.py'}.items():
            monkeypatch.setattr(MODULE, name, value)
        MODULE.dump(MODULE.SCHEMA, MODULE.schema())
        MODULE.write_text(MODULE.SCRIPT, 'print(1)\n')
        yield root
```

**Blob registry fakes, L387-405.** Extend `register_blobs` so it also serves every D-05 path and `rel(SCRIPT)` at `RECORD_COMMIT` and at a fake HEAD SHA (for example `'b' * 40`, returned by the faked `git_head`):
```python
RECORD_COMMIT = 'a' * 40

@pytest.fixture
def fake_git_show(monkeypatch):
    blobs = {(MODULE.SUPERSEDED_V2_0_1['commit'], MODULE.SUPERSEDED_V2_0_1['relative_path']): prev_201_authority_bytes()}
    def fake(commit, path):
        if (commit, path) not in blobs: raise AuthorityError(f'{path}@{commit[:7]}: git show failed: unknown object')
        return blobs[(commit, path)]
    monkeypatch.setattr(MODULE, 'git_show', fake)
    return blobs

def register_blobs(blobs, commit=RECORD_COMMIT):
    blobs[(commit, MODULE.rel(MODULE.AUTHORITY))] = MODULE.AUTHORITY.read_bytes()
    blobs[(commit, MODULE.rel(MODULE.OUT / MODULE.N_MANIFEST))] = (MODULE.OUT / MODULE.N_MANIFEST).read_bytes()
```

**At-pin record fixture (rewrite target): `superseded_record`, L496-503.** For D-02, build the record from `MODULE.load(MODULE.AUTHORITY)['source_lineage']['supersedes']` instead of `MODULE.SUPERSEDED_V2_0_1`.

**Tests to rename or rewrite for D-01 and D-02:**
- L505-515 `test_pre_publication_mode_accepts_only_superseded_record`
- L517-526 `test_pre_publication_binding_names_2_0_1_literals`
- L528-535 and L537-544
- L561-569, which loops over `(False, True)` modes
- L484-490 (`validate_published(True)`)
- L608-620, the CLI tests. The stub at L615, `lambda pre=False: seen.append(pre)`, becomes `at_pin`.

**Real-git integration analog, L594-606.** HEAD is the publication commit and `scripts/pub.py` is committed. Copy this for real-repo D-04, D-06 and D-07 tests: a dirty-path case, a not-ancestor case, a script-edit case, and a commit-after-publication case.
```python
def test_real_git_repo_record_passes_plain_mode(env):
    def run(*args): return subprocess.run(['git', *args], cwd=MODULE.ROOT, capture_output=True)
    require_history(ROOT)
    r = run('init', '-q')
    if r.returncode != 0: pytest.fail(f"git init failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
    run('config', 'user.email', 't@example.com'); run('config', 'user.name', 't'); run('config', 'commit.gpgsign', 'false')
    published(env)
    run('add', '-A')
    r = run('commit', '-q', '-m', 'publish')
    ...
    sha = run('rev-parse', 'HEAD').stdout.decode().strip()
    MODULE.write_publication_record(sha)
    MODULE.validate_published()
```

**GATE-06 inversion: `test_script_edit_after_publication_does_not_break_validate`, L773-776.** Today the test edits the script and expects PASS. Rewrite it to expect `pytest.raises(AuthorityError, match=...)`.

**GATE-07 malformed-shape test style, L898-919.** Add file-level cases in the same parametrised-dict form, for example invalid JSON in each of the five files, a manifest that is a list, a schema of `{"type":7}`, and `validate_lineage([])`. Each case runs through `env` and `published(env)`, then corrupts one file and asserts `pytest.raises(AuthorityError)`.
```python
@pytest.mark.parametrize('name', sorted(MALFORMED_SHAPES))
def test_malformed_authority_shapes_raise_domain_error(name):
    a = copy.deepcopy(build()); MALFORMED_SHAPES[name](a)
    with pytest.raises(AuthorityError):
        validate_publication(a)
```

**IN-06 row-tamper parametrisation, L1025-1033.** Today the test tampers only `a['controls'][0]`. Add `@pytest.mark.parametrize('cid', ['EMS-CTRL-001', 'EMS-CTRL-030'])`, select the row with `row(a, cid)` (L23), and match `f'{cid}: decision content differs from'`.

**IN-02 chain test.** The current `test_superseded_constants_match_git_history` (L702-713) uses its own literals. Bind them by exec'ing the publisher blob at `31addfa`; the analog is reply tests `frozen_publisher(commit)` L566-581:
```python
def frozen_publisher(commit):
    ...
    r = subprocess.run(['git', 'show', f'{commit}:{PUBLISHER_REL}'], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        pytest.fail(f'cannot read {PUBLISHER_REL} at {commit}: ...; fetch full history (git fetch --unshallow)')
    name = f'aa_frozen_publisher_{commit[:7]}'
    m = types.ModuleType(name); m.__file__ = str(PUBLISHER_PATH); sys.modules[name] = m
    try: exec(compile(r.stdout.decode('utf-8'), f'publisher@{commit}', 'exec'), m.__dict__)
    finally: sys.modules.pop(name, None)
```
The exec must not be added to the frozen builders. It lives in tests only.

**Constants-vs-git analog for `SUPERSEDED_V2_0_2`: L715-725.** Copy it with `ae15c74` and the record at `a71257e`:
```python
def test_superseded_v2_0_1_constants_match_git_history():
    require_history(ROOT, commits=(MODULE.SUPERSEDED_V2_0_1['commit'],))
    sup = MODULE.SUPERSEDED_V2_0_1
    auth_bytes = git('show', f"{sup['commit']}:{sup['relative_path']}").stdout
    dec_bytes = git('show', f"{sup['commit']}:{sup['governance_decisions_relative_path']}").stdout
    old = json.loads(auth_bytes.decode('utf-8'))
    assert sup['authority_id'] == old['authority_id'] and sup['version'] == old['version'] == '2.0.1'
    assert sup['sha256'] == lf_sha(auth_bytes) and sup['governance_decisions_sha256'] == lf_sha(dec_bytes) == '4e746d1f…'
    rec = json.loads(git('show', '4d9b7c1…:registry/archive_assessment_applicability_authority_v2_publication_record.json').stdout.decode('utf-8'))
    assert sup['commit'] == rec['publication_commit'] and sup['sha256'] == rec['authority_sha256']
```

**D-05 reuse.** `PUBLICATION_PATHS` at L1050 and the local path build at L1058 should be replaced with `MODULE.publication_paths()`, keeping the `assert len(paths) == 10` form.

---

### `tests/test_archive_assessment_lineage_validation.py` (test)

**GATE-09 D-10 `--validate` test.** The analog is the existing D-10 test at L333-353 (outcome-unchanged loop) combined with the subprocess style of `skip_guard.run_case` (L48-52):
```python
    live = tmp_path / MODULE.CATALOG_REL
    for change in (lambda: live.write_bytes(b'controls: []\n'), live.unlink):
        change()
        assert MODULE.jtext(MODULE.build_authority()) == before_build
        ...
```
- The new test runs `git clone --shared <REAL_ROOT> <tmp>/c` and then `git -C c config core.longpaths true`.
- It runs `[sys.executable, 'scripts/publish_..._v2.py', '--validate']` with `cwd=c`, and records `(returncode, last output line)` before the catalog change, after an overwrite, and after a delete.
- It asserts the three outcomes are equal. It does not assert PASS.
- Guard it with `require_history(REAL_ROOT, commits=PINNED_COMMITS)`.
- Module-level `PINNED_COMMITS` at L29 and `sup = MODULE.SUPERSEDED_V2_0_1` at L46 and L336 move to `SUPERSEDED_V2_0_2` in the move commit. If they are missed, the AttributeError is a collection error.

---

### `tests/test_archive_assessment_governance_answers.py` (GATE-09 D-13)

**Analog: L134-150.** The real-bytes copy pattern looks like this. It replaces the fabricated digest at L121-125 (`sha_text(read_text() + ' ')`).
```python
def answers_copy(tmp_path, monkeypatch, extra=b''):
    p = tmp_path / 'archive_assessment_governance_answers.json'
    p.write_bytes(MODULE.ANSWERS.read_bytes() + extra)
    monkeypatch.setattr(MODULE, 'ANSWERS', p)
    return p
```

### `tests/test_archive_assessment_governance_decisions.py` (GATE-08)

**CLI-path analog: L332-340.** It drives `main --validate` against a patched `DECISIONS`:
```python
    p = TMP / 'decisions.json'; MODULE.V2.dump(p, d)
    monkeypatch.setattr(MODULE, 'DECISIONS', p)
    monkeypatch.setattr('sys.argv', ['x', '--validate'])
    with pytest.raises(AuthorityError): MODULE.main()
```
- The new test copies the answers with `b'\n'` appended (as `answers_copy` does), patches `MODULE.ANSWERS`, and sets the decisions `answers_sha256` to `MODULE.answers_digest(copy)`.
- It dumps that to a temp `DECISIONS` and asserts `match='repeats the note of'`.
- `main --validate` (builder L404-408) calls `validate_decisions` before the rebuild comparison.
- In the publisher tests, the matching path is `PUB.validate_governance_decisions()` with `GOVERNANCE_DECISIONS` and the builder `ANSWERS` patched. The builder module is `PUB.decisions_builder()`, cached in `_BUILDER`.
- Optionally replace L196-199, which uses `monkeypatch.setattr(MODULE, 'CERTIFIED_ANSWERS_SHA256', 'f' * 64)`.

---

### `tests/test_archive_assessment_demo3_w1_req_001_reply.py` (IN-03 / IN-04)

**Analog: L342-356, `fake_shallow_git`.**
- Remove the `log_sha` parameter and the `args[0] == 'log'` branch (L349-350).
- Remove the `log_sha` positional values at L368 and L376, and drop the `not any(a[0] == 'log' ...)` asserts at L372 and L378.
- For IN-04, add `cat_exc` and `mb_exc` parameters that raise `OSError`. Add the cases `mb_rc=128` (expect "cannot check ancestry") and OSError (expect `AuthorityError`) to the parametrised list at L382-385.
```python
def fake_shallow_git(rc, out, log_sha=None, exc=None, cat_rc=0, mb_rc=0):
    seen = []
    def run(*args):
        seen.append(args)
        if args[0] == 'rev-parse' and args[1] == '--is-shallow-repository':
            if exc: raise exc
            return subprocess.CompletedProcess(args, rc, out, '')
        if args[0] == 'log': ...
        if args[0] == 'cat-file': return subprocess.CompletedProcess(args, cat_rc, '', '')
        if args[0] == 'merge-base': return subprocess.CompletedProcess(args, mb_rc, '', '')
        raise AssertionError(f'unexpected git command: {args}')
```
This same fake-`git` shape (a dispatch on `args[0]` with `seen` recording) is the model for the publisher's `git_run` fakes, if the planner fakes at the `git_run` level rather than per helper.

---

### `tests/conftest.py` (D-10)

**Analog: itself, L24-32.** Add the path predicate from the research (Hook scoping) and an early `return` when the collector is not an archive module. The `pytest_runtest_makereport` hook (L13-21) is unchanged.
```python
@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    outcome = yield
    if os.environ.get('EMS_FAIL_ON_SKIP') != '1':
        return
    rep = outcome.get_result()
    if rep.skipped:
        rep.outcome = 'failed'
        rep.longrepr = f'skipped test treated as failure (EMS_FAIL_ON_SKIP=1): {collector.nodeid}: {rep.longrepr}'
```

### `tests/aa_history.py` (D-11)

**Analog: itself.**
- L10: `HINT = 'run git fetch --unshallow, or set EMS_ALLOW_NO_HISTORY=1 for an offline local run'`. The new text must keep "EMS_ALLOW_NO_HISTORY=1" after "fetch full history", which `require_history` adds at L39 (regex at skip_guard L190).
- L25-26: split this into an `out == 'true'` branch ("is a shallow repository") and a branch for any other output ("cannot tell whether … is shallow … printed {out!r}"). Both branches end with `; fetch full history`.

### `tests/test_archive_assessment_skip_guard.py` (D-10 / D-11)

**Analog: `run_case`, L36-53.**
- Add a `module_name='test_case.py'` parameter. For the two module-skip-with-guard tests (L93-104), pass `'test_archive_assessment_case.py'`, because the hook now scopes to archive names.
- New D-10 case: the extra module is the passing `test_archive_assessment_ok.py`, and the skipping module is `test_other_skip.py` (`BODIES['module_skip']`). Run with `-k archive_assessment` and the guard on. Assert rc 0, `'1 passed'`, and that `'treated as failure'` is absent.
- `run_case` builds targets from explicit files. For the `-k` case, add an `extra_args` parameter, or pass the `work` directory as the target.
- Strengthen L168-175: assert `repr(out)` appears in the message for `b''` and `b'maybe'`, and that "is a shallow repository" appears only for `b'true'`.

### `.github/workflows/ems-validate.yml` (D-09)

**Analog: itself, L87-90.** Change only the `run:` line, and leave the glob unquoted:
```yaml
      - name: Archive-assessment tests
        env:
          EMS_FAIL_ON_SKIP: '1'
        run: python -m pytest tests -k archive_assessment -p no:cacheprovider -q
```
The validators step (L92-99) is unchanged. CI keeps plain `--validate` (09 D-04).

### `.planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md` (NEW ledger)

**Analog: `09-BASELINE-RED.md`.** Its structure:
- `## Baseline (before any Phase N code change)`, giving the date, the HEAD SHA and the exact PowerShell command with a fresh `--basetemp=<scratchpad>\pNN-x`. Then **Totals** in bold, the failing node ids as a bullet list, and a sentence saying they match the accepted reds.
- One `## After <plan/task> (commit <sha>)` section per commit, with the command, the totals, the failing ids, and an annotation for each id (baseline red, newly opened by design, or fixture defect fixed).
- An "Accepted red set now" list, which may only shrink or stay as listed.

Phase 12 differences:
- The local command must expand the glob explicitly: `(Get-ChildItem tests/test_archive_assessment_*.py).FullName`, with `EMS_FAIL_ON_SKIP=1`.
- Each entry also records the 6 CI validators' PASS/FAIL. Validator 1 turns red at GATE-06.
- The ledger records pytest's own exit code.

---

## Shared Patterns

### Fail-closed git access
**Source:** publisher `git_show` L359-365. Error-wrapping precedent: `validate_governance_decisions` L629-637.
**Apply to:** every new git call in the publisher (`git_run`, `git_head`, `git_is_ancestor`, `git_not_shallow`, `git_dirty`) and the reply builder IN-04 edit.
**Rules:**
- Validate SHAs with the 40-hex regex and paths with `bad_rel`, both before calling git.
- `OSError` becomes `GitHistoryError`.
- A non-zero rc becomes `GitHistoryError` that carries stderr.
- The shallow check requires exactly `false`.
- All `subprocess` use stays inside the named seam functions, because the source-scan tests at L88-95 and L966-969 enforce this.

### Domain errors only
**Source:** `class AuthorityError(ValueError)` and `class GitHistoryError(AuthorityError)` (L66-67). The mutation gates re-raise `GitHistoryError` (L643, L649, L654).
**Apply to:** all GATE-07 hardening. No `TypeError`, `KeyError`, `AttributeError`, `JSONDecodeError`, `ValidationError` or `SchemaError` may escape `validate_published`.
**Constraint:** the 29 mutation `rejected_by` outcomes and `N_NEGATIVE` bytes stay identical until the move commit (`test_published_negative_file_equals_observed_outcomes` L971-976; L963 asserts 29).

### Version-agnostic messages (09 D-07)
**Source:** `dry_run_summary` L568-576 already uses `sup["version"]`.
**Apply to:** L243, L315, L318, L341, the D-02 record messages, and the test matches at L182, L1032, L1038, L540 and L543.

### Test fixtures without git history
**Source:** the `env` fixture L226-241 plus `fake_git_show` L389-405. Real-git counterpart: L594-606.
**Apply to:** every `validate_published()` test that expects PASS (L407-415, L417-422, L492-494, L773-776). These need fakes for the new git helpers, or must run in the real temp repo.

### History guard in tests
**Source:** `aa_history.require_history(ROOT, commits=(...))` (aa_history L33-39). Every test that reads pinned history calls it first (for example L665, L688, L716).
**Apply to:** the new D-10 clone test, the IN-02 chain test and the `SUPERSEDED_V2_0_2` git test.

### Staging discipline
Stage by explicit path only. Never stage `.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json` or untracked files. Do not touch `registry/`, `schemas/` or `generated/` in Phase 12.

## No Analog Found

None. The nearest gaps are partial matches, covered by the research Code Examples:

| File / element | Role | Data Flow | Note |
|---|---|---|---|
| `git_dirty(paths)` (`git status --porcelain -- <paths>`) in the publisher | utility | git read | No existing `git status` call in the archive-assessment scripts. Follow the `git_show` seam shape. `generated/` is gitignored, so extra OUT files are caught by the L729-730 file-set check, not by porcelain |
| `schema_check` with `check_schema` and the `SchemaError` wrap | utility | validate | No `check_schema` use exists. Use the research's Code Examples snippet, in the wrapping style of L635-636 |

## Metadata

**Analog search scope:** `scripts/publish_archive_assessment_applicability_authority_v2.py`, `scripts/build_archive_assessment_governance_decisions.py`, `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, `tests/test_archive_assessment_*.py` (v2, v2_publication, lineage, normalisation_claims, governance_answers, governance_decisions, reply, skip_guard), `tests/conftest.py`, `tests/aa_history.py`, `.github/workflows/ems-validate.yml`, `.planning/phases/09-*/09-BASELINE-RED.md`, git commit `69ea357` (supersedes-move precedent)
**Files scanned:** 14
**Pattern extraction date:** 2026-11-16
