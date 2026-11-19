# Phase 17: Security Hardening and Schema Pinning - Pattern Map

**Mapped:** 2026-11-18
**Files analyzed:** 14 (new or modified)
**Analogs found:** 14 / 14 (all are in-place edits of existing files or direct siblings of existing tests)

Decisions applied (user amendments to CONTEXT):
- **D-09 amended:** `core.longpaths` is passed with `GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=core.longpaths`, `GIT_CONFIG_VALUE_0=true` in the sanitized env. It is NOT passed as `-c` in argv. Existing argv-shape tests (`test_git_show_argv_ends_with_double_dash`) therefore stay valid.
- **`.gitattributes`:** `text eol=lf` for the publisher and decisions-builder scripts goes in an early green-safe commit, before any publisher byte changes.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `.gitattributes` | config | n/a | itself (L1-18 `text eol=lf` lines) | exact |
| `.github/workflows/ems-validate.yml` (L60-68) | config (CI) | batch | itself | exact |
| `tests/test_archive_assessment_ci_workflow.py` (new) | test | file-I/O (reads workflow text) | `source_without_git_show` style source-introspection tests in `tests/test_archive_assessment_applicability_authority_v2_publication.py` L95-104 | role-match |
| `tests/aa_history.py` | utility (test helper) | request-response (git subprocess) | publisher `git_run` L375-377 | role-match |
| `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` | service (builder) | request-response + file-I/O | itself (`load_pinned_publisher` L281-297, `live_git_subprocess` L300-306, `pinned_mutation_run` L312-324) | exact |
| `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` | test | request-response | itself (wrappers L144-200) | exact |
| `scripts/publish_archive_assessment_applicability_authority_v2.py` | service (publisher) | request-response + transform | itself | exact |
| `tests/test_archive_assessment_applicability_authority_v2_publication.py` | test | request-response | itself (L95-104, L1680-1687) | exact |
| `tests/test_archive_assessment_applicability_authority_v2.py` | test | transform | itself (schema equality test, SUPERSEDED use L204) | exact |
| `tests/test_archive_assessment_lineage_validation.py` | test | transform | itself (L32, L83, L373 rename sites; D-10 baseline) | exact |
| `tests/test_archive_assessment_normalisation_claims.py` | test | transform | itself (L36 rename site) | exact |
| `schemas/archive_assessment_applicability_authority_v2.schema.json` | config (generated) | transform | emitted by `--emit-schema`; regenerated in Phase 18 only | exact |
| `.planning/phases/17-.../17-BASELINE-RED.md` (new) | doc (ledger) | n/a | `12-BASELINE-RED.md` | exact |
| hostile-env and policy-equality tests (new, in publication test file and notice test file) | test | request-response | `test_git_show_argv_ends_with_double_dash` (fake `subprocess.run`), `make_repo` style scratch repos in the publication tests | role-match |

## Pattern Assignments

### `scripts/publish_archive_assessment_applicability_authority_v2.py` (service, request-response/transform)

Style: single quotes, compact one-line helpers, `AuthorityError` / `GitHistoryError`. The word `subprocess` must appear ONLY inside `git_show`/`git_run` and the import line (enforced by `source_without_git_show`, test L95-104). `git_env()` must not mention it in code, comments or docstrings. The publisher needs a new `import os`.

**Git seam to modify** (lines 367-377, current):
```python
def git_show(commit: str, relative_path: str) -> bytes:
    ...
    try: r = subprocess.run(['git', 'show', f'{commit}:{relative_path}', '--'], cwd=ROOT, capture_output=True)
    except OSError as e: raise GitHistoryError(f'{relative_path}@{commit[:7]}: git unavailable: {e}') from e
    ...
def git_run(*args: str) -> subprocess.CompletedProcess:
    try: return subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    except OSError as e: raise GitHistoryError(f"git {next((a for a in args if not a.startswith('-')), 'command')}: git unavailable: {e}") from e
```
Change: add `env=git_env()` to both `subprocess.run(...)` calls. Keep the argv `['git','show',f'{commit}:{path}','--']` unchanged (D-09 amended). Keep `git show` and the Phase 15 `--`.

**New helper (D-09 amended; one copy per script, D-10)**, defined next to the seam, before `git_show`:
```python
def git_env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('GIT_')}
    env.update({'GIT_NO_REPLACE_OBJECTS': '1', 'GIT_LITERAL_PATHSPECS': '1', 'GIT_CONFIG_NOSYSTEM': '1',
                'GIT_CONFIG_GLOBAL': os.devnull,
                'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'core.longpaths', 'GIT_CONFIG_VALUE_0': 'true'})
    return env
```
Keep `--literal-pathspecs` in `git_dirty` (L407) and `git_index_flags`.

**Lineage constants (D-01, D-13, D-14).** Replace `SUPERSEDED_V2_0_2` (L36-44) with `SUPERSEDED_V2_0_3`. `VERSION` L34 becomes `'2.0.4'`. Rename sites: L184, L251, L292, L323, L326, L334-335, L349, L476, L587, L636 (grep `SUPERSEDED_V2_0_2` to confirm). Values come from git, not typed (decisions LF sha256 `4e746d1f...`, authority `696116e7...`, commit `1544dc19ba235d732c832d1651895550ed5a265d`). Add `V1_BASELINE_SHA256` (CRLF_TO_LF of `V1_BASELINE_REL` at `V1_BASELINE_COMMIT`) and reuse `SUPERSEDED_V2_0_3['governance_decisions_sha256']` for `governance_decisions.sha256` rather than a second literal.

**Schema pin (GATE-11)**, `schema()` L467-478, current:
```python
sha = {'type':'string','pattern':'^[0-9a-f]{64}$'}
def pinned(entry, sha_keys):
    props = {k: ({'type':'string','pattern':'^[0-9a-f]{64}$'} if k in sha_keys else {'const':v}) for k, v in entry.items()}
    return {'type':'object','additionalProperties':False,'required':list(entry),'properties':props}
...
'supersedes':pinned(SUPERSEDED_V2_0_2, {'sha256','governance_decisions_sha256'}),
'v1_baseline':pinned({'authority_id':V1_BASELINE_ID,...,'sha256':None,'normalisation':'CRLF_TO_LF'}, {'sha256'}),
'governance_decisions':{... 'properties':{'relative_path':{'const':GOVERNANCE_DECISIONS_REL},'sha256':sha,...
```
Change: `supersedes: pinned(SUPERSEDED_V2_0_3, set())`; `v1_baseline` gets the real `V1_BASELINE_SHA256` with `set()`; `governance_decisions.sha256` becomes `{'const': <decisions constant>}`. `catalog_reference`, `aa1_manifest`, `aa2_closure` and `aa2_approval` stay on `sha`.

**Mutations (GATE-11).** Add `Mutation(name, text, 'AUTHORITY', lambda a: ..., True)` entries, with the final arg `True` so `run_mutations` asserts the schema itself rejects. One per pinned field:
```python
Mutation('v1_baseline_digest_differs', '...', 'AUTHORITY', lambda a: a['source_lineage']['v1_baseline'].__setitem__('sha256','0'*64), True)
```
Plus `supersedes_digest_differs` and `governance_decisions_digest_differs`. The existing `supersedes_governance_digest_differs` (near L587) also gets `True`. The `== 29` count rises everywhere it is asserted (publication test around L1349; grep `== 29`). The notice builder runs the PINNED publisher, so its own count of 29 stays.

**Sign-off scope (GATE-12)**, `validate_signoff` L620-621 current:
```python
scope = appr.get('scope')
if not isinstance(scope, str) or not scope.strip(): errors.append('sign-off scope must be a non-empty string')
```
Add after it, gated on `want_version >= 2.0.4` parsed with a strict `^[0-9]+\.[0-9]+\.[0-9]+$` regex (D-12), following the same `errors.append(...)` accumulation style:
```python
if isinstance(scope, str) and scope.strip():
    if re.search(r'[0-9a-fA-F]{7,}', scope): errors.append('sign-off scope must not contain a hex run of 7 or more characters; digests live in checked fields')
    if want_id not in scope or want_version not in scope: errors.append('sign-off scope must name the authority id and version')
```
The notice builder's own `validate_signoff` copy (L149) is frozen and must NOT gain this.

**Manifest builder entry (SEC-02 / D-06).** Sibling of `publisher_script`, `build_all_outputs` L693-694:
```python
publisher_script = {'relative_path': rel(SCRIPT), 'sha256': script_sha256 or lf_digest(SCRIPT), 'sha256_normalisation': 'CRLF_TO_LF'}
manifest = {..., 'publisher_script': publisher_script, 'publisher_script_note': '...', ...}
```
Add `builder_sha256: str | None = None` to `build_all_outputs`, plus `'decisions_builder_script': {'relative_path': rel(BUILDER_SCRIPT), 'sha256': builder_sha256 or lf_digest(BUILDER_SCRIPT), 'sha256_normalisation': 'CRLF_TO_LF'}` and a `'decisions_builder_script_note'`. `validate_published` passes `builder_sha256=` from the manifest, as it does `script_sha256=ps['sha256']` at L815. Grep callers of `build_all_outputs` in tests first.

**Hash-before-exec in `decisions_builder` (L701-706), current:**
```python
def decisions_builder():
    global _BUILDER
    if _BUILDER is None:
        spec = importlib.util.spec_from_file_location('aa_governance_decisions_builder', BUILDER_SCRIPT)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); _BUILDER = module
    return _BUILDER
```
Change: `decisions_builder(expected_sha256=None)`. When given, compare `lf_digest(BUILDER_SCRIPT)` on every call, outside the `_BUILDER` cache, and raise `AuthorityError` before `exec_module`. `validate_governance_decisions()` takes and forwards the expected digest.

**`validate_published` reorder (L792-825; D-03 IN-04/IN-06, D-06).** Current order: shallow (at-pin only) -> tree checks -> `validate_governance_decisions()` (L798, execs the builder) -> authority -> signoff -> manifest load (L810) -> `ps` shape (L812-813) -> `lf_digest(SCRIPT)` (L814). Target order:
1. `git_not_shallow()` first, both modes (IN-04).
2. At-pin tree checks. Add `rel(BUILDER_SCRIPT)` to the `check_tree_matches_head` and `git_dirty` lists next to `rel(SCRIPT)` (L795-796).
3. Manifest existence checks and `load_checked(OUT / N_MANIFEST)`.
4. Shape check of `publisher_script` and `decisions_builder_script`, using one shared helper so the two entries cannot drift. The existing shape check to generalise is:
```python
ps = manifest.get('publisher_script')
if not isinstance(ps, dict) or ps.get('relative_path') != rel(SCRIPT) or not re.fullmatch(r'[0-9a-f]{64}', str(ps.get('sha256'))) or ps.get('sha256_normalisation') != 'CRLF_TO_LF': raise AuthorityError('manifest publisher_script entry missing or invalid')
if lf_digest(SCRIPT) != ps['sha256']: raise AuthorityError('publisher script differs from the certified manifest digest (manifest publisher_script.sha256); a publisher edit needs a certified republication')
```
   Keep these exact messages (tests match them). The builder entry gets the analogous message with `decisions_builder_script`.
5. `lf_digest(SCRIPT)` check (IN-06), then `lf_digest(BUILDER_SCRIPT)` check.
6. `validate_governance_decisions(expected_sha256=...)`, then the rest.
7. Plain mode also checks the builder blob at the publication commit (`git_show(pub, rel(BUILDER_SCRIPT))` LF digest equals the manifest digest), next to the existing publisher-at-commit check near L856.

**Error-message fixes (D-03).** IN-01 around L845-846: "committed authority/manifest" becomes "the authority/manifest in the working tree". IN-02 at L841: keep both phrases in order for the test at L714, "still names the superseded {v} publication (HEAD is the publication commit or earlier)" then "run --validate --at-pin here". IN-03 at L836-839: at-pin branch raises "the record already names this publication; run plain --validate here" when the record's `authority_id` and `version` equal the authority's, before the superseded-commit check.

---

### `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` (service, behaviour-only; output stays byte-identical)

**Own git seam**, L120-130 (`git_show`) and L187-188 (`git()`, `text=True`):
```python
try: r = subprocess.run(['git', 'show', f'{commit}:{relative_path}', '--'], cwd=ROOT, capture_output=True)
...
def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)
```
Add its own `git_env()` (copy of the publisher's, D-10) and `env=git_env()` to every `subprocess.run`. Check the L305 shim as well.

**Shim (L300-306), current:**
```python
def live_git_subprocess() -> SimpleNamespace:
    def run(cmd, *args, **kwargs):
        if not isinstance(cmd, (list, tuple)) or not cmd or cmd[0] != 'git':
            raise AuthorityError(f'pinned code started a process that is not git: {cmd!r}')
        kwargs['cwd'] = ROOT
        return subprocess.run(cmd, *args, **kwargs)
```
Add `kwargs['env'] = git_env()` next to `kwargs['cwd'] = ROOT`, so pinned code cannot override it.

**SEC-01 / SEC-02 hash-before-exec (D-05, D-07).** Current `load_pinned_publisher(tmp)` L281-297 materialises files, then `spec.loader.exec_module(pub)` (L289), then `pub.decisions_builder()` (L290). The digest check sits later at L322-324 in `pinned_mutation_run`:
```python
publisher_bytes = (tmp / PINNED_CODE[0]).read_bytes()
if hashlib.sha256(lf_bytes(publisher_bytes)).hexdigest() != manifest['publisher_script']['sha256']:
    raise AuthorityError('pinned publisher differs from the certified publisher_script digest')
```
Change: `load_pinned_publisher(tmp, manifest)`. After the materialisation loop and BEFORE `spec_from_file_location` and `exec_module`, validate `manifest.get('publisher_script')` shape (so a missing key becomes `AuthorityError`, not a wrapped `KeyError`). Then check both the publisher digest against the manifest, and the builder blob digest against a new frozen constant `PINNED_DECISIONS_BUILDER_SHA256`. Value from git at `1544dc19...`, LF-normalised: `8ccd93c3036a706b6b39ee50ca81ff8a29778bf1b98765f3c44e36d90251a153`. A test recomputes it; it is not typed by the executor. Do both checks before the first `exec_module` (RESEARCH recommendation). Keep the exact message `pinned publisher differs from the certified publisher_script digest`. Remove or keep as redundant the L322-324 check. Update the call at L317.

---

### `tests/aa_history.py` (utility, request-response)

Current L14-15:
```python
def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=root, capture_output=True)
```
Add a module-local `git_env()` (copy, D-10; uses the `os` already imported at L3) and pass `env=git_env()`.

---

### `.github/workflows/ems-validate.yml` L60-68 (config, batch) - SEC-03

Current L64-65:
```bash
if grep -RInE "$secret_pattern" . \
  --exclude-dir=.git --exclude-dir=.venv --exclude='*.md'; then
```
Drop `--exclude='*.md'`. Research verified zero `.md` hits. Do not write literal token examples in any `.md` (this file avoids them).

### `tests/test_archive_assessment_ci_workflow.py` (new; the name must match the CI glob `test_archive_assessment_*.py`)

Pattern: a source-introspection test in the style of `test_module_does_not_call_git` (publication tests L101-104). Read the workflow text, assert the secret-scan step contains no `--exclude='*.md'` and that the `secret_pattern=` line is unchanged.

---

### `.gitattributes` (config) - early green-safe commit

Append, in the same format as the existing lines:
```
scripts/publish_archive_assessment_applicability_authority_v2.py text eol=lf
scripts/build_archive_assessment_governance_decisions.py text eol=lf
```
This changes working-tree bytes only, not the index. Reason: under `GIT_CONFIG_NOSYSTEM` a fresh Windows clone loses system autocrlf, so `git_dirty` at-pin would flag the CRLF scripts as modified. Stage this commit by explicit path. Check afterwards that `git ls-files --eol` shows `attr/text eol=lf` for both.

---

### Tests (modify)

**`tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`.** Update the four `load_pinned_publisher` wrappers (L148, L161, L175, plus the group near L819-828) from `def wrapper(tmp): pub = real(tmp)` to `def wrapper(tmp, *a): pub = real(tmp, *a)`, in the same commit as the signature change. Copy the style of `test_pinned_run_rejects_publisher_digest_mismatch` (L195-200) for the new SEC-01 and SEC-02 tests:
```python
a = args(); manifest = a[6]; manifest['publisher_script']['sha256'] = '0' * 64
with pytest.raises(AuthorityError, match='pinned publisher differs from the certified publisher_script digest'):
    MODULE.pinned_mutation_run(a[0], a[4], a[5], manifest)
```
New tests, using `monkeypatch.setattr(MODULE, 'git_show', ...)`:
- A tampered publisher blob plus a sentinel side effect (`open(SENTINEL,'w')` appended to the returned bytes). Assert `AuthorityError`, `not SENTINEL.exists()`, and that `importlib.util.spec_from_file_location` was not called (exec spy).
- A tampered builder blob: the builder does not run.
- The frozen-constant-recompute-from-git test: model on the existing `test_frozen_constants_match_git`.
- A missing `publisher_script` entry gives `AuthorityError`.
- A hostile-env test through `MODULE.git_show` and the `live_git_subprocess` shim.
- The byte-identical gate is a command, not a test: rebuild, then `git diff --exit-code` on the 2.0.3 JSON, MD and schema.

**`tests/test_archive_assessment_applicability_authority_v2_publication.py`.** Fake-subprocess pattern, L1680-1687, already kept valid by env-based longpaths:
```python
def test_git_show_argv_ends_with_double_dash(monkeypatch):
    seen = []
    def fake(argv, **kwargs):
        seen.append(argv)
        return subprocess.CompletedProcess(argv, 0, b'x', b'')
    monkeypatch.setattr(MODULE.subprocess, 'run', fake)
    assert MODULE.git_show(SHA40, 'registry/a.json') == b'x'
    assert seen == [['git', 'show', f'{SHA40}:registry/a.json', '--']]
```
Extend with a sibling asserting `kwargs['env']` has no key other than the controlled `GIT_*` set. New tests: hostile env (see below), the three-copy same-policy test, IN-01..IN-04 and IN-06, the SEC-02 manifest-entry negatives, the GATE-12 scope cases, the D-14 const-recompute test, and the GATE-12 positive that a 2.0.3-version call accepts the old scope text. Rename `SUPERSEDED_V2_0_2` sites at L82, 85, 191, 226, 241, 409, 1065 (the hard-coded `'ae15c74'`), 1069, 1178, 1428, 1485, 1490.

**`tests/test_archive_assessment_applicability_authority_v2.py`.** Rename at L204; `test_committed_schema_equals_schema_function` (around L212) goes red when `schema()` changes. This is a known red-set entry that Phase 18 clears.

**`tests/test_archive_assessment_lineage_validation.py`** (L32, 83, 373) and **`tests/test_archive_assessment_normalisation_claims.py`** (L36): rename only. The D-10 baseline test joins the red ledger and must not be weakened (16 D-08a).

**Hostile-env test skeleton (research, preserved):**
```python
def test_git_seam_ignores_hostile_environment(tmp_path, monkeypatch):
    repo, decoy = make_repo(tmp_path/'r'), make_repo(tmp_path/'d')
    # commit registry/a.json in repo; create a refs/replace substitute for the blob
    for k, v in {'GIT_DIR': str(decoy/'.git'), 'GIT_WORK_TREE': str(decoy), 'GIT_INDEX_FILE': str(decoy/'idx'),
                 'GIT_OBJECT_DIRECTORY': str(decoy/'.git'/'objects')}.items(): monkeypatch.setenv(k, v)
    monkeypatch.setattr(MODULE, 'ROOT', repo)
    assert MODULE.git_head() == sha and MODULE.git_show(sha, 'registry/a.json') == b'real\n'
```
Include a non-vacuity assertion: an unsanitized call returns the replacement bytes. Use a scratch repo built in `tmp_path`, not a clone. Apply the same test to the notice builder (`git_show` and the shim) and to `aa_history`. The scratch repo is the one place where tests may need a local `.git/config` autocrlf choice; cover `git_dirty` on a CRLF working file with and without it.

---

### `17-BASELINE-RED.md` (new ledger)

Follow `12-BASELINE-RED.md`: a Baseline section (date, HEAD sha, the exact pytest command with `EMS_FAIL_ON_SKIP=1`, totals, "Failing node ids: none", and a 6-row CI validator table), then a "Planned red window" list per plan, then the rule "the red set may only grow by the listed ids at the listed plan. Anything red outside this ledger blocks the commit." Planned red ids at the first publisher edit, from RESEARCH Pitfall 5:
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`
- `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate`
- CI validator 1
- `tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function` (once `schema()` changes)
- real-file sign-off and supersedes tests, once VERSION and SUPERSEDED change
- the D-10 baseline test in `tests/test_archive_assessment_lineage_validation.py`

Record measured node ids per commit, not these predictions. The ledger also lists the frozen reply and 2.0.2 builders as CLOSED (frozen).

## Shared Patterns

### Sanitized git env (SEC-04), one copy per script (D-10)
**Source:** the `git_env()` above. **Apply to:** the publisher, the 2.0.3 notice builder (plus the `live_git_subprocess` shim) and `tests/aa_history.py`. Do not touch the 2.0.1 reply or 2.0.2 notice builders. The same-policy test loads all three copies, sets a controlled env with hostile `GIT_*` (including `GIT_CONFIG_PARAMETERS`), and asserts the returned dicts are equal.

### Fail-closed digest-before-exec
**Source:** `lf_digest` and `lf_bytes` plus `hashlib.sha256` (see the notice builder `pinned_digest` L183-184). **Apply to:** `load_pinned_publisher`, `decisions_builder`, `validate_published`. Compare, raise `AuthorityError`, and only then call `spec.loader.exec_module`.

### Error handling and test style
Domain exceptions are `AuthorityError` (invariant) and `GitHistoryError` (git). Tests use `pytest.raises(X, match='specific text')`. Keep the existing messages that tests already match.

### Red-window commit discipline
Green-safe commits first: `.gitattributes`, SEC-03 workflow and its test, notice-builder behaviour-only fixes and tests, `aa_history`. Then the publisher edits, each commit staging explicit paths and listing its red set. Unrelated tracked changes in the working tree (`.planning/*`, `registry/adjudication_rules.json`, `registry/policy_decisions.json`, `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md`, `registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json`) must never be staged. Tests run from the main session with `--basetemp`.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| hostile-env scratch-repo helper | test fixture | request-response | The publication tests build repos through direct `subprocess.run(['git', ...])` calls (L227, L523, L718 and others), and there is no shared `make_repo` helper. The planner should add a small local helper and reuse RESEARCH's skeleton. |
| publication-manifest JSON schema | config | n/a | No schema file exists for the publication manifest. "Manifest schema and validation" (D-06) means the inline shape check at `validate_published` L812-813. Extend it with the shared helper. |

## Metadata

**Analog search scope:** `scripts/` (publisher, 2.0.3 notice builder), `tests/` (aa_history, publication, notice, lineage and normalisation tests), `.github/workflows/`, `.gitattributes`, `12-BASELINE-RED.md`.
**Files read:** about 12, using targeted line ranges. Bash was broken in this session (cygwin fatal error), so Read was used throughout.
**Pattern extraction date:** 2026-11-18
