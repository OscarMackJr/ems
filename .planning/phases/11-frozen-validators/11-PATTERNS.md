# Phase 11: Frozen Validators - Pattern Map

**Mapped:** 2026-11-14
**Files analyzed:** 14 (2 builders modified, 2 builder test files modified, 1 new conftest, 1 new helper, 1 new skip-guard test, 1 new freeze-proof test location, 7 other test files, 1 workflow)
**Analogs found:** 13 / 14 (the only no-analog item is the pytest skip-to-fail hook)

All excerpts are from the repo at HEAD b97e805. Line numbers are as of that commit.
The publisher (`scripts/publish_archive_assessment_applicability_authority_v2.py`) is the SOURCE of the literals and is read-only in this phase. The frozen values must come from its blobs at 31addfa (reply) and ae15c74 (notice); at HEAD the live file differs from the ae15c74 blob only by line endings, so the live line numbers below are valid for copying and the D-02 test is what proves it.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` (modify) | utility/validator | batch (git read -> rebuild -> byte compare) | itself (V2 uses) + publisher helper bodies | exact |
| `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` (modify) | utility/validator | batch | itself + publisher helper bodies | exact |
| `tests/test_archive_assessment_demo3_w1_req_001_reply.py` (modify) | test | request-response | `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` | exact |
| `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` (modify) | test | request-response | the reply test file | exact |
| D-02 literal-vs-blob tests (in the two files above) | test | transform | existing `test_frozen_constants_match_git` (reply test L346) | role-match |
| D-11 static AST and mutation tests (same files) | test | transform | existing `test_validate_independent_of_live_version` (reply L423, notice L219) | role-match |
| `tests/conftest.py` (new): D-10 skip-to-fail hook, `require_history` fixture | config/test | event-driven (pytest hook) | none in repo (no conftest exists) | no analog |
| `tests/aa_history.py` (new, optional shared helper) | utility | request-response | the 7 `git_ready()` copies, e.g. reply test L319 | role-match |
| `tests/test_archive_assessment_skip_guard.py` (new) | test | request-response (subprocess pytest) | reply tests' `subprocess.run(['git', ...])` helper L315 | partial |
| `tests/test_archive_assessment_applicability_authority_v2_publication.py` (modify) | test | CRUD | `git_ready` L653, `prev_201_authority_bytes` L217 | exact |
| `tests/test_archive_assessment_governance_decisions.py` (modify) | test | CRUD | `needs_git` L242-251 | exact |
| `tests/test_archive_assessment_lineage_validation.py`, `_normalisation_claims.py`, `_rule_proposals.py`, `_rule_proposals_record.py`, `_governance_answers.py` (modify) | test | CRUD | `git_ready` copies at lineage L28, claims L36, record L34 | exact |
| `.github/workflows/ems-validate.yml` (modify, `archive-assessment` job) | config | batch | the same job L87-88 | exact |

## Pattern Assignments

### Reply builder (utility, batch): freeze

**Analog:** the builder itself. Replace every `V2.x` by a local definition; copy helper bodies from the publisher.

**Remove the live-import block** (reply L3-5, L14-17). Delete `import importlib.util`, `import sys` (only if `--push-check` goes, D-06 recommendation: remove), and:
```python
_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V2)
```
Keep `ROOT = Path(__file__).resolve().parents[1]` (reply L14). Add `import subprocess` (already imported) and `from datetime import date` for `is_date`.

**Local literals to copy (publisher lines):**
```python
# publisher L17-33, L444-451
AUTHORITY = REGISTRY / 'archive_assessment_applicability_authority_v2.json'      # L20
SCHEMA = SCHEMAS / 'archive_assessment_applicability_authority_v2.schema.json'    # L21
GOVERNANCE_DECISIONS = REGISTRY / 'archive_assessment_governance_decisions.json'  # L23
GOVERNANCE_DECISIONS_REL = 'registry/archive_assessment_governance_decisions.json' # L24
REQUEST_CONTROL_IDS = [f'EMS-CTRL-{n:03d}' for n in (9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 30, 33, 39, 42, 52, 62, 75, 79)]  # L25
DECISIONS = [f'AA1-GOV-{n:03d}' for n in range(1, 9)]                              # L26
DECISION_STATES = ['RULE_PUBLISHED','NO_RULE_WILL_BE_PUBLISHED','NOT_YET_DECIDED'] # L31
OUT = ROOT / 'generated' / 'archive-assessment' / 'ems-aa3-v2'                    # L444
SIGNOFF = REGISTRY / 'archive_assessment_applicability_authority_v2_signoff.json' # L445
PUBLICATION_RECORD = REGISTRY / 'archive_assessment_applicability_authority_v2_publication_record.json'  # L446
APPROVER = 'Oscar Mack'                                                           # L448
APPROVER_ROLES = ['EMS_GOVERNANCE_AUTHORITY', 'HAYES_VERIFY_DEVELOPER']           # L449
SIGNOFF_ROLE = 'EMS_GOVERNANCE_AUTHORITY'                                         # L450
DUAL_ROLE_STATEMENT = 'Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it.'  # L451
N_NEGATIVE = 'archive_assessment_applicability_authority_v2_negative_invariant_validation.json'  # L454
N_TRACE = 'archive_assessment_applicability_authority_v2_decision_traceability.json'            # L455
N_MANIFEST = 'ems_aa3_v2_archive_applicability_authority_publication_manifest.json'             # L458
```
Reply frozen version: `VERSION = '2.0.1'`, `AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1'` (NOT the live 2.0.2 values at L34-35). `RULE_FIELDS`, `CONDITION_STATES`, `COMBINATION`, `AUTHORITY_ID_RE` are needed only by `schema()`; if `schema()` is deleted (D-04) they are not needed.

**Helper bodies to copy** (publisher L66-91, 355-365, 517-519, 182-189, 524-553):
```python
class AuthorityError(ValueError): pass
class GitHistoryError(AuthorityError): pass
def lf_bytes(b: bytes) -> bytes: return b.replace(b'\r\n', b'\n')
def load(p: Path) -> dict: return json.loads(p.read_text(encoding='utf-8'))
def contains_absolute(value: object) -> bool:
    if isinstance(value, str): return value.startswith(('/', '\\\\')) or (len(value) > 2 and value[1] == ':' and value[2] in '\\/')
    if isinstance(value, dict): return any(contains_absolute(v) for v in value.values())
    if isinstance(value, list): return any(contains_absolute(v) for v in value)
    return False
def bad_rel(p: object) -> bool: return not isinstance(p, str) or not p or contains_absolute(p) or p.startswith('\\') or re.match(r'[A-Za-z]:', p) is not None or '..' in p.replace('\\', '/').split('/')
def git_show(commit: str, relative_path: str) -> bytes:
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit): raise AuthorityError(f'{relative_path}: commit must be a 40-character lowercase hex SHA')
    if bad_rel(relative_path): raise AuthorityError(f'{relative_path}: path must be repo-relative without ..')
    try: r = subprocess.run(['git', 'show', f'{commit}:{relative_path}'], cwd=ROOT, capture_output=True)
    except OSError as e: raise GitHistoryError(f'{relative_path}@{commit[:7]}: git unavailable: {e}') from e
    if r.returncode != 0: raise GitHistoryError(f'{relative_path}@{commit[:7]}: git show failed: {r.stderr.decode("utf-8", "replace").strip()}')
    return r.stdout
def jtext(value: object) -> str: return json.dumps(value, indent=2, sort_keys=True) + '\n'
def rel(p: Path) -> str: return p.relative_to(ROOT).as_posix()
def latest_records(doc: dict) -> list[dict]:
    recs = doc.get('records', [])
    superseded = set()
    for r in recs:
        sup = r.get('supersedes')
        if isinstance(sup, str): superseded.add(sup)
        elif isinstance(sup, list): superseded.update(x for x in sup if isinstance(x, str))
    return [r for r in recs if r.get('decision_id') not in superseded]
def rule_text(rule: dict) -> str:
    return f"{rule['combination']}: " + ' AND '.join(f"{c['field']} = {c['state']}" for c in rule['conditions'])
```
Pitfall 7: keep the text `git show failed` in the `GitHistoryError` (tests match it). Improve per D-07: use the full SHA and append `; fetch full history (git fetch --unshallow)`. `git_show` must stay a module-global called by name at call time (tests monkeypatch `MODULE.git_show`).

**`validate_signoff` (reply = 31addfa 2-arg form; do NOT copy the live 4-arg form).** The live form is at publisher L530-550:
```python
def is_date(value: object) -> bool:                                   # L524
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value): return False
    try: date.fromisoformat(value)
    except ValueError: return False
    return True
def validate_signoff(record, authority_lf_digest, authority_id=None, version=None):   # L530 (notice copies this, byte-for-byte from ae15c74)
    ...
```
Extract the exact 2-arg body with `git show 31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb:scripts/publish_archive_assessment_applicability_authority_v2.py` and change the call site (reply L88) from `V2.validate_signoff(signoff, record['authority_sha256'], authority_id=..., version=...)` to `validate_signoff(signoff, record['authority_sha256'])`.

**Existing calls to retarget (mechanical):** reply L38-47 (`pinned_bytes`/`pinned_json`/`pinned_digest` use `V2.git_show`, `V2.rel`, `V2.lf_bytes`); all `raise V2.AuthorityError(...)` (L53, 62, 65, 68, 70, ...); L59 `V2.latest_records`; L88 `V2.validate_signoff`; L102/110-111 `V2.APPROVER_ROLES`/`V2.DECISION_STATES`/`V2.DECISIONS`; L106-108 `V2.rel(V2.AUTHORITY)`, `V2.SCHEMA`, `V2.OUT`, `V2.N_MANIFEST`, `V2.N_TRACE`, `V2.GOVERNANCE_DECISIONS_REL`; L145/152 `V2.rule_text`; L174 `V2.jtext`; L226-232 `V2.contains_absolute`, `V2.DUAL_ROLE_STATEMENT`.

**Frozen schema check (D-04), replacing reply L198-221 `schema()` and L270-271:**
```python
# add: REPLY_SCHEMA_COMMIT = '7debe4aa544b425f2b80306a8510bfe74e568bae'   # RESEARCH: last commit that changed the schema; e781f08eaaf45b227c4cb2c96d110ecec85d584c has identical bytes
def frozen_schema() -> dict: return json.loads(git_show(REPLY_SCHEMA_COMMIT, rel(REPLY_SCHEMA)).decode('utf-8'))
# validate_reply: replace the `schema() ...` compare with
if lf_bytes(REPLY_SCHEMA.read_bytes()) != lf_bytes(git_show(REPLY_SCHEMA_COMMIT, rel(REPLY_SCHEMA))):
    raise AuthorityError('reply schema differs from the frozen schema at 7debe4a')
# validate_reply_object: jsonschema.Draft202012Validator(frozen_schema()).validate(reply)
```
Add `REPLY_SCHEMA_COMMIT` to `resolve_record_commit()` ancestor loop (reply L283-295; notice L75-79 already loops over several SHAs; copy that loop shape).

**Main (reply L327-338):** keep only `--validate`. Recommended: drop `--push-check`, `push_check()`, `PUSH_*` (L298-324), `sys` import; keep `REMOTE_BRANCH` (used in `send_condition`).
```python
def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--validate', action='store_true')
    args = parser.parse_args()
    if args.validate: validate_reply()
```

**Error handling pattern (copy as-is, reply L283-295):** shallow check -> `cat-file -e` -> `merge-base --is-ancestor`, all raising `AuthorityError` naming the commit.

---

### Notice builder (utility, batch): freeze

**Analog:** the notice builder itself plus the publisher at ae15c74.

V2 uses (notice L14-16 load; L48, 56, 61, 72, 77, 87-93, 98-109, 120, 125-127, 256, 261-262, 275, 281, 288-312, 322, 327). Extra locals beyond the reply list: `PREV_COMPARED_KEYS`, `closed_schema_levels`, `validate_signoff` 4-arg form, `write_text`/`dump` are NOT needed once `--build`/`--emit-schema` go.
```python
# publisher L281
PREV_COMPARED_KEYS = ('not_applicable_decision_state', 'not_applicable_rule', 'not_applicable_authority', 'decision_ids')
# publisher L290-297
def closed_schema_levels(node: object, path: str = '$') -> list:
    out = []
    if isinstance(node, dict):
        if node.get('additionalProperties') is False: out.append(path)
        for k, v in node.items(): out += closed_schema_levels(v, f'{path}.{k}')
    elif isinstance(node, list):
        for i, v in enumerate(node): out += closed_schema_levels(v, f'{path}[{i}]')
    return out
```
Notice frozen version: `VERSION = '2.0.2'`, `AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-' + VERSION`; the notice already has `NOTICE_VERSION`/`NOTICE_AUTHORITY_ID`; the copied `validate_signoff` defaults refer to `AUTHORITY_ID`/`VERSION`, so define both. Copy the 4-arg `validate_signoff` (publisher L530-550) verbatim.

`V2.ROOT` (notice L303) becomes local `ROOT`. Notice already has its own `git`, `resolve_record_commit` with the three-SHA ancestor loop (notice L64-82); add the schema commit `052f0f13f4c882a7b80667d4835bc802002e0f80` to that loop (note: it post-dates `NOTICE_PUBLICATION_COMMIT`, so do not add it to the `is-ancestor NOTICE_PUBLICATION_COMMIT, NOTICE_RECORD_COMMIT` check).

**Frozen schema check (notice L286-287, L310):** same shape as the reply: `NOTICE_SCHEMA_COMMIT = '052f0f13f4c882a7b80667d4835bc802002e0f80'`, compare committed bytes to `git_show(NOTICE_SCHEMA_COMMIT, rel(NOTICE_SCHEMA))`, validate with `json.loads` of that blob. Existing `load_inputs` already reads `frozen_schema = pinned_json(NOTICE_PUBLICATION_COMMIT, V2.SCHEMA)` (L103) which is the AUTHORITY schema, a different file; name the new function distinctly (e.g. `frozen_notice_schema`).

**Main (notice L317-328):** keep only `--validate`, same shape as the reply main above.

---

### Reply and notice tests (test, request-response): freeze proof and rigor

**Analog:** the two test files against each other.

**Module loading / MODULE alias (reply tests L12-20, notice tests L13-19):**
```python
ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / 'scripts' / 'build_archive_assessment_demo3_w1_req_001_reply.py'
SPEC = importlib.util.spec_from_file_location('aa_reply_demo3', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
V2 = MODULE.V2                      # REMOVE
AuthorityError = V2.AuthorityError  # becomes MODULE.AuthorityError
REJECTS = (AuthorityError, jsonschema.ValidationError)   # REMOVE: replace by specific class/match (D-12, D-13)
```
Anti-pattern: do not alias `V2` in tests. Tests that still need the live publisher (e.g. reply `V2.validate_published()` test, Pitfall 1) must load it themselves under another name or move to `tests/test_archive_assessment_applicability_authority_v2_publication.py`.

**D-02 blob loader (new, from RESEARCH Pattern 2; analog is existing git helper at reply tests L315-316):**
```python
def git(*args):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return subprocess.CompletedProcess(r.args, r.returncode, r.stdout, r.stderr.decode('utf-8', 'replace').strip())
```
```python
def frozen_publisher(commit):
    src = subprocess.run(['git', 'show', f'{commit}:scripts/publish_archive_assessment_applicability_authority_v2.py'], cwd=ROOT, capture_output=True, check=True).stdout.decode('utf-8')
    m = types.ModuleType('aa_frozen_publisher')
    m.__file__ = str(ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
    sys.modules['aa_frozen_publisher'] = m
    try: exec(compile(src, f'publisher@{commit[:7]}', 'exec'), m.__dict__)
    finally: sys.modules.pop('aa_frozen_publisher', None)
    return m
```
Wrap `check=True` failure in `pytest.fail(f'cannot read {path} at {commit}; fetch full history')`. Compare constants by value and `rel(path)` for Path constants; compare functions on representative inputs (list in RESEARCH Pattern 2) including exception text.

**Existing "frozen constants vs git" pattern to extend (reply tests L346-354):**
```python
def test_frozen_constants_match_git():
    reason = git_ready()
    if reason:
        pytest.skip(reason)
    assert git('rev-parse', '31addfa').stdout.decode().strip() == MODULE.REPLY_PUBLICATION_COMMIT
    assert git('rev-parse', '4d9b7c1').stdout.decode().strip() == MODULE.REPLY_RECORD_COMMIT
```
After FROZEN-03 the `pytest.skip` becomes `require_history()` (see shared pattern).

**D-11 test: replace the narrow test (reply L423-429, notice L219-227):**
```python
def test_validate_independent_of_live_version(monkeypatch):
    def boom(*a, **k):
        raise AssertionError('validator read a live file digest')
    monkeypatch.setattr(V2, 'lf_digest', boom)
    monkeypatch.setattr(V2, 'VERSION', '9.9.9')
    monkeypatch.setattr(V2, 'AUTHORITY_ID', 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-9.9.9')
    MODULE.validate_reply()
```
This is vacuous after freeze (and was weak before: patched attributes of a module the builder no longer owns). New test: build mutated copy of live publisher via exec (use `frozen_publisher`-style loader on the working-tree file), overwrite `PREV_COMPARED_KEYS`, `DUAL_ROLE_STATEMENT`, `rule_text`, set `validate_signoff` to raise; register in `sys.modules` under `'aa_applicability_publisher_v2'` and `'publish_archive_assessment_applicability_authority_v2'` and monkeypatch `importlib.util.spec_from_file_location` for the publisher path; then FRESH-load the builder (new `spec_from_file_location` + `exec_module`, as at test L14-17) and call `validate_reply()` / `validate_notice()` with `capsys`, asserting `PASS`. Do not reuse `MODULE` (Pitfall 5).

**Static AST test (Pattern 4, RESEARCH):** walk `ast.parse(SCRIPT.read_text())`; fail on `Import`/`ImportFrom` containing `publish_archive_assessment_applicability_authority`, any string `Constant` containing `publish_archive_assessment_applicability_authority_v2`, `Name`/`Attribute` `V2`, calls to `import_module`, `__import__`, `spec_from_file_location`, `SourceFileLoader`, `exec`, `eval`.

**Specific-match pattern to copy (already used in reply tests):**
```python
with pytest.raises(AuthorityError, match='differs from a fresh build'):    # reply tests L439
    ...
with pytest.raises(MODULE.AuthorityError, match='shallow'):                # reply tests L388 (currently MODULE.V2.AuthorityError)
```
Apply per RESEARCH "Test rigor findings": `absolute path`, `dual role statement differs`, `reply controls differ from the 21 requested controls`, `global CRLF_TO_LF claim` etc. Confirm each `match=` by running once (A4).

**Committed-files test:** reply already has `test_real_reply_files_validate` (keep, D-13). Notice needs (D-12):
```python
def test_committed_notice_files_validate(capsys):
    require_history()
    MODULE.validate_notice()
    assert capsys.readouterr().out.strip() == 'PASS'
```
No monkeypatching; also assert no `\r` and no absolute path in the committed JSON, mirroring the reply's real-files test.

**CLI-flag test rewrite (reply L541, notice L365):** parametrised `['--build','--validate']` / `['--emit-schema','--validate']` expected-failure becomes: `--build`, `--emit-schema` (and `--push-check` on the reply) exit with code 2 as unrecognised; `--validate` is the only accepted flag; assert nothing was written (compare `git status --porcelain` on the five frozen paths or file mtimes).

**Tests that catch `V2.AuthorityError`/`V2.GitHistoryError`:** retarget to `MODULE.AuthorityError`/`MODULE.GitHistoryError`; tests that monkeypatch `V2.git_show` (notice L207-216) must patch `MODULE.git_show`.

---

### `tests/conftest.py` (config/test, event-driven): D-08 shared helper and D-10 hook

**Analog:** no conftest exists. Use RESEARCH D-10 snippet; for the history check, factor the seven duplicated `git_ready()` bodies.

**Existing `git_ready` (identical in reply L319, governance_decisions L242, others):**
```python
def git_ready():
    try:
        r = git('rev-parse', '--is-shallow-repository')
    except OSError:
        return 'git is unavailable'
    if r.returncode != 0:
        return 'not a git repository'
    if r.stdout.decode().strip() == 'true':
        return 'shallow repository, history is incomplete'
    return None
```
Variants: lineage L28 and normalisation_claims L36 also check that specific commits exist (give the helper an optional `commits=()` argument); `rule_proposals_record` L34 uses a stripped-string `git()`.

**Target shape (D-08):**
```python
# tests/aa_history.py  (not named test_*; importable under pytest prepend mode, assumption A2)
import os, subprocess, pytest
def history_problem(root, commits=()): ...      # returns None or a message naming the commit/path and 'fetch full history'
def require_history(root, commits=()):
    msg = history_problem(root, commits)
    if not msg: return
    if os.environ.get('EMS_ALLOW_NO_HISTORY') == '1': pytest.skip(msg)
    pytest.fail(msg + '; run git fetch --unshallow, or set EMS_ALLOW_NO_HISTORY=1 for an offline local run')
```
```python
# tests/conftest.py  (hook; inert unless EMS_FAIL_ON_SKIP=1)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if os.environ.get('EMS_FAIL_ON_SKIP') == '1' and rep.skipped and not hasattr(rep, 'wasxfail'):
        rep.outcome = 'failed'
        rep.longrepr = f'skipped test treated as failure (EMS_FAIL_ON_SKIP=1): {item.nodeid}: {rep.longrepr}'
```
Pitfall 3: collection-time `needs_git` (governance_decisions L249-251, rule_proposals_record L41) is
```python
def needs_git(fn):
    reason = git_ready()
    return pytest.mark.skipif(reason is not None, reason=reason or '')(fn)
```
and cannot fail; replace with `@pytest.mark.usefixtures('require_git_history')` (a fixture in conftest that calls `require_history`). Same for `skipif(not REAL_AUTHORITY.exists())` / `not REAL_RECORD.exists()` (publication L636/662/686/1057): delete the guard, add `assert path.exists(), '<msg>'` if the natural error is unclear.

---

### `tests/test_archive_assessment_skip_guard.py` (new, test)

**Analog:** none exact; use `subprocess.run` as in reply tests L315. Write a one-test temp file that calls `pytest.skip`, run `python -m pytest <file> -p no:cacheprovider -q --basetemp=<tmp>` in a subprocess with `EMS_FAIL_ON_SKIP=1` (expect non-zero) and without (expect 0); also a case with both `EMS_FAIL_ON_SKIP=1` and `EMS_ALLOW_NO_HISTORY=1` and a missing-history call (Pitfall 4: must end red). Name contains `archive_assessment` so `-k archive_assessment` collects it (A1: verify the hook converts `skipif` setup-skips on first run).

---

### `.github/workflows/ems-validate.yml` (config, batch)

**Analog:** the job itself, L87-88:
```yaml
      - name: Archive-assessment tests
        run: python -m pytest tests -k archive_assessment -p no:cacheprovider -q
```
Add `env:` on that step: `EMS_FAIL_ON_SKIP: '1'`. Never set `EMS_ALLOW_NO_HISTORY`. `fetch-depth: 0` (L75) is already present. Optionally add `-rs`. Do not touch L90-97 validator steps.

---

### Skip-site tests (test, CRUD): FROZEN-03 conversion

**Analogs:** the `git_ready()`/`needs_git` copies above. Per-file treatment from RESEARCH skip inventory (line numbers as of b97e805; confirm with grep before editing):

- publication tests: L217 `prev_201_authority_bytes()` (31addfa) -> `pytest.fail` naming commit and path; L598/602 temp-repo `git unavailable` -> opt-out helper, failed `git commit` -> real failure; L636/662/686/1057 `skipif(...exists())` -> delete; L665/689/705/719/732/745/1060 `if reason: pytest.skip(reason)` -> `require_history()`. Also receives the relocated reply-test `V2.validate_published()` test (Pitfall 1).
- lineage L53, 267, 293, 300, 313, 336-361, 380 (L361 pinned blob -> `pytest.fail`); governance_decisions L242-251, 285/290, 352 (`eed4a5f` short SHA: message must name it); governance_answers L63-154 (`'answers not yet filled'` -> assert filled); rule_proposals L161 `gated()` (remove), L175 `git_out` `FileNotFoundError`; rule_proposals_record L34-43; normalisation_claims L36-102 (checks V1_BASELINE and 2.0.1 commits).

---

## Shared Patterns

### Fail-closed git history read
**Source:** publisher `git_show` L359-365 and builder `resolve_record_commit` (reply L283-295, notice L68-82)
**Apply to:** both builders; error text must name the full commit and path and say "fetch full history" (D-07).
```python
if s.returncode != 0 or s.stdout.strip() != 'false':
    raise AuthorityError('shallow clone or unreadable repository: cannot resolve the frozen commits; fetch full history')
for sha in (...):
    if not re.fullmatch(r'[0-9a-f]{40}', sha) or git('cat-file', '-e', f'{sha}^{{commit}}').returncode != 0:
        raise AuthorityError(f'the frozen commit {sha[:7]} is not in the repository history')
    if git('merge-base', '--is-ancestor', sha, 'HEAD').returncode != 0:
        raise AuthorityError(f'the frozen commit {sha[:7]} is not an ancestor of HEAD')
```

### Style
Keep each builder's compact single-quote style (CLAUDE.md "match the style of the file being edited"); `from __future__ import annotations`; deterministic JSON `json.dumps(value, indent=2, sort_keys=True) + '\n'`; repo-relative forward-slash paths; no absolute paths in registry JSON.

### Frozen-byte and no-edit checks (every plan)
After each commit `git diff` must be empty for the publisher, `docs/DEMO3_W1_REQ_001_REPLY.md`, `registry/archive_assessment_demo3_w1_req_001_reply.json`, `docs/DEMO3_W1_REQ_001_NOTICE_2_0_2.md`, `registry/archive_assessment_demo3_w1_req_001_notice_2_0_2.json`, and both schemas. Stage by explicit path only; never stage `.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json`. Run `-k archive_assessment` with `--basetemp=.pytest-temp/p11-N` from PowerShell (orchestrator; subagents cannot).

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `tests/conftest.py` skip-to-fail hook | config | event-driven | No conftest, `pytest.ini` or pyproject exists; use RESEARCH D-10 snippet (assumption A1, verify by running the skip-guard test) |

## Metadata

**Analog search scope:** `scripts/` (both builders, publisher), `tests/test_archive_assessment_*.py`, `.github/workflows/ems-validate.yml`
**Files read:** 2 builders (reply in full, notice L1-130 and L200-331), publisher (targeted ranges), reply and notice test excerpts, governance_decisions test excerpt, workflow
**Pattern extraction date:** 2026-11-14
