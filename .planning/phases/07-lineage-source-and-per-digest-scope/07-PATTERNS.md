# Phase 7: Lineage Source and Per-Digest Scope - Pattern Map

**Mapped:** 2026-10-20
**Files analyzed:** 8 (1 new test file, 1 data commit, 6 modified)
**Analogs found:** 8 / 8 (all in-file or sibling-file analogs; see notes)

Bash unavailable: Read/Grep only. Line numbers are from direct reads of the files named.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/publish_archive_assessment_applicability_authority_v2.py` (lineage constants, `digest_entry`, `git_show`, `validate_lineage`, `build_authority`, `schema()`, `validate_published` hook) | publisher/validator script | transform + request-response (CLI validate) | itself: `v1_baseline_entry()` L114-115, `pinned()` L298-300, `validate_publication` L258-290, `validate_published` L599-627 | exact (in-file) |
| `.gitattributes` | config | n/a | existing L19 `generated/archive-assessment/ems-aa2/approval/** -text` | exact |
| `generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json` (force-add, no content change) | data artifact | file-I/O | AA2 approval files committed in `35bfc08` | exact (procedure) |
| `tests/test_archive_assessment_lineage_validation.py` (NEW: LIN-02, LIN-03, D-13) | test | file-I/O + git | `tests/test_archive_assessment_applicability_authority_v2_publication.py` L480-526 (`git`, `git_ready`, `lf_sha`, real-file git tests) | role-match |
| `tests/test_archive_assessment_applicability_authority_v2.py` (shape updates ~L31-33, 143-160) | test | request-response | itself | exact |
| `tests/test_archive_assessment_applicability_authority_v2_publication.py` (L67-82, L548-558, L676-678) | test | request-response | itself | exact |
| `publish_..._v2.py` mutation harness | test-support | transform | no edit required if key names survive (research Q2) | n/a |
| D-13 claim tests (inside new test file) | test | file-I/O | L511-514 `lf_sha(git('show', ...)) == rec[...]` pattern | role-match |

Do NOT touch: reply builder, reply schema, reply JSON (D-14), `build_archive_assessment_governance_decisions.py`, v1 publisher.

## Pattern Assignments

### Publisher: `scripts/publish_archive_assessment_applicability_authority_v2.py`

**Style:** compact single-quote, one-line helpers, `from __future__ import annotations`, `AuthorityError(ValueError)` (L60). Match it.

**Imports to extend** (L1-14). Add `import subprocess` only for `git_show`:
```python
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
from datetime import date
from pathlib import Path
```

**Existing normalisation helpers to dispatch on** (L62-64):
```python
def digest(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def lf_bytes(b: bytes) -> bytes: return b.replace(b'\r\n', b'\n')
def lf_digest(p: Path) -> str: return hashlib.sha256(lf_bytes(p.read_bytes())).hexdigest()
```
New (research Pattern 1), module-level constants (referenced by name inside builders; see Pitfall below):
```python
NORMALISATIONS = ['RAW_BYTES', 'CRLF_TO_LF']
NORMALISERS = {'RAW_BYTES': lambda b: b, 'CRLF_TO_LF': lf_bytes}
AA1_MANIFEST_REL = 'generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json'
EXPECTED_NORMALISATION = {'aa1_manifest': 'RAW_BYTES', 'aa2_closure': 'RAW_BYTES', 'aa2_approval': 'RAW_BYTES', 'catalog_reference': 'CRLF_TO_LF', 'governance_decisions': 'CRLF_TO_LF', 'v1_baseline': 'CRLF_TO_LF'}
```
Define `NORMALISERS` after `lf_bytes` (L63) so it resolves.

**Constants with commit (shape to extend)**: `SUPERSEDED_V2_0_0` L36-41 and `v1_baseline_entry()` L114-115:
```python
def v1_baseline_entry() -> dict:
    return {'authority_id': V1_BASELINE_ID, 'version': '1.0.0', 'commit': V1_BASELINE_COMMIT, 'relative_path': V1_BASELINE_REL, 'sha256': lf_digest(V1_AUTHORITY)}
```
Add `'normalisation': 'CRLF_TO_LF'` here and to `SUPERSEDED_V2_0_0` (plus `governance_decisions_relative_path`, `governance_decisions_normalisation`; keep flat `governance_decisions_sha256` because the reply builder reads it, L76-82 of reply script). `validate_authority` L220-221 and `validate_publication` L287-288 then follow automatically.

**Lineage build** (L151-157 to replace). Keep sourcing the three AA digest VALUES from `load(V1_AUTHORITY)['source_lineage']` (L119-120), never from `generated/`:
```python
'source_lineage': {
    'aa1_manifest_sha256': lin['aa1_manifest_sha256'], 'aa2_closure_sha256': lin['aa2_closure_sha256'], 'aa2_approval_sha256': lin['aa2_approval_sha256'],
    'catalog_reference': {'relative_path': 'registry/control_catalog.yaml', 'sha256': lf_digest(CATALOG), 'required_for_deterministic_compilation': False},
    'supersedes': dict(SUPERSEDED_V2_0_0),
    'v1_baseline': v1_baseline_entry(),
    'digest_normalisation': 'CRLF_TO_LF',
},
```
Becomes `aa1_manifest` / `aa2_closure` / `aa2_approval` objects via `digest_entry(...)`, `catalog_reference` gains `normalisation`, and `digest_normalisation` is deleted. `build_published_authority` L182 `governance_decisions` entry gains `'normalisation': 'CRLF_TO_LF'` (keep key `sha256`; read by `build_archive_assessment_governance_decisions.py:367`).

**Schema generation** (L297-308). `pinned()` makes non-sha keys `const`; replace flat keys with object schemas:
```python
sha = {'type':'string','pattern':'^[0-9a-f]{64}$'}
def pinned(entry, sha_keys):
    props = {k: ({'type':'string','pattern':'^[0-9a-f]{64}$'} if k in sha_keys else {'const':v}) for k, v in entry.items()}
    return {'type':'object','additionalProperties':False,'required':list(entry),'properties':props}
lineage = {'type':'object','additionalProperties':False,
    'required':['governance_decisions','supersedes','v1_baseline','catalog_reference','digest_normalisation','aa1_manifest_sha256','aa2_closure_sha256','aa2_approval_sha256'],
```
Drop `digest_normalisation` and the three flat keys from `required`/`properties`; add three object schemas `{relative_path: const, sha256: sha, normalisation: const-from-EXPECTED_NORMALISATION}` and reference the closed `NORMALISATIONS` enum. Never hand-edit the committed schema; do not run `--emit-schema` in Phase 7.

**Validator hook point** (L599-604): insert `validate_lineage(a['source_lineage'])` right after L603, not inside `validate_publication` (26-mutation harness `mutation_gates` L528-533 calls it).
```python
a = load(AUTHORITY)
validate_publication(a); jsonschema.Draft202012Validator(load(SCHEMA)).validate(a)
if a != build_published_authority(): raise AuthorityError('published authority differs from a fresh build')
```

**New `git_show` + `validate_lineage`** (no in-repo publisher analog; copy research Q4/Pattern 1; error accumulation style copies `validate_publication`: `errors = []` ... `if errors: raise AuthorityError('; '.join(errors))` at L291):
```python
def git_show(commit: str, relative_path: str) -> bytes:
    if not re.fullmatch(r'[0-9a-f]{40}', commit or '') or contains_absolute(relative_path) or '..' in relative_path.split('/'): raise AuthorityError(f'{relative_path}: invalid commit or path for git show')
    try: r = subprocess.run(['git', 'show', f'{commit}:{relative_path}'], cwd=ROOT, capture_output=True)
    except OSError as e: raise AuthorityError(f'git is unavailable for {relative_path}@{commit[:7]}: {e}') from e
    if r.returncode != 0: raise AuthorityError(f'{relative_path}@{commit[:7]}: git history unavailable: {r.stderr.decode("utf-8", "replace").strip()}')
    return r.stdout
```
`validate_lineage` loops all entries (supersedes yields two logical digests at one commit), uses `git_show` when `commit` present else `(ROOT / path).read_bytes()` (dynamic `ROOT` so test `env` monkeypatch works), also checks declared == `EXPECTED_NORMALISATION[label]`, missing file = error (fail closed).

**Pitfalls (enforced by existing tests):**
- `test_v2_builder_does_not_use_generated_dir` (v2 test L165-168): source of `build_authority` + `build_published_authority` must not contain `generated`, `OUT`, `ems-aa2`, `'ems-aa3'`, `AA2 / `. Use `AA1_MANIFEST_REL` etc. by name only.
- Two tests ban the word `subprocess` (publication test L80-82 and L676-678): narrow them to allow it only in `git_show`.
- Do not bump `VERSION` (L34); test L560-561 pins 2.0.1.

---

### `.gitattributes` (config)

**Analog:** L19 of the same file.
```
generated/archive-assessment/ems-aa2/approval/** -text
```
Append after L19 (file-specific, write BEFORE `git add -f`):
```
generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json -text
```
Stage explicit paths only: `git add .gitattributes`, `git add -f -- <manifest>` (`generated/` is gitignored at `.gitignore:6`). Check `.gitattributes` has no unrelated uncommitted edits first (git status snapshot does not list it as modified). Read back the blob raw sha via bytes-mode Python, not PowerShell redirection; must equal `f0da8e2e45c306ccc42ae96f25a19922668f3eedecdb26006f13514e24ad9b4b` (D-07).

---

### `tests/test_archive_assessment_lineage_validation.py` (NEW; test, file-I/O + git)

**Analog:** `tests/test_archive_assessment_applicability_authority_v2_publication.py`.

**Module loading** (L8-13, copy; use a distinct module name):
```python
SCRIPT = Path(__file__).parents[1] / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py'
SPEC = importlib.util.spec_from_file_location('aa3_authority_v2_pub', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
```
**Git helpers** (L480-491, copy verbatim; bytes mode, shallow-skip):
```python
def git(*args):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return subprocess.CompletedProcess(r.args, r.returncode, r.stdout, r.stderr.decode('utf-8', 'replace').strip())

def git_ready():
    try: r = git('rev-parse', '--is-shallow-repository')
    except OSError: return 'git is unavailable'
    if r.returncode != 0: return 'not a git repository'
    if r.stdout.decode().strip() == 'true': return 'shallow repository, history is incomplete'
    return None

def lf_sha(b): return hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()
```
**Negative-test shape** (L23-34 `mutated`/`fails` with `pytest.raises(AuthorityError)`). For D-12 use `monkeypatch.setattr(MODULE, 'ROOT', tmp_path)`; CRLF fixture `b'a\r\nb\r\n'` (flipping normalisation only changes the digest when `\r\n` is present, Pitfall 4); temp git repo with `-c core.autocrlf=false` and `* -text`; nonexistent `0*40` commit must raise; missing file must raise.
**D-13 claim tests** copy L511-514 pattern, e.g.:
```python
assert lf_sha(git('show', f'{sha}:{auth_rel}').stdout) == rec['authority_sha256']
manifest = json.loads(git('show', f'{sha}:{out_rel}/{MODULE.N_MANIFEST}').stdout.decode('utf-8'))
for art in manifest['artifacts']:
    assert lf_sha(git('show', f"{sha}:{art['relative_path']}").stdout) == art['sha256']
```
Name tests with `normalisation_claim` and keep filename containing `archive_assessment` (CI selector `-k archive_assessment`). Skip real-file ones with `@pytest.mark.skipif(not REAL_RECORD.exists(), ...)` as at L493/L517. Claims to cover: publication record, certification, manifest artifacts, traceability `decision_record_digest_normalisation`, signoff, reply pin (read only, no reply edits).

---

### Existing tests to update

**`tests/test_archive_assessment_applicability_authority_v2_publication.py`**
- L78 `assert lin['digest_normalisation'] == 'CRLF_TO_LF'` -> per-digest assertions (`lin['aa1_manifest']['normalisation'] == 'RAW_BYTES'`, etc.) and assert `'digest_normalisation' not in lin`.
- L80-82 and L676-678 `subprocess` bans -> allow only in `git_show` (e.g. `inspect.getsource(MODULE.git_show)`).
- L558 `{...} == {'supersedes', 'v1_baseline'}` -> rewrite: keep L556 `differing <= {'authority_id','version','source_lineage'}`; assert new digest VALUES equal old flat ones (`new['aa1_manifest']['sha256'] == ol['aa1_manifest_sha256']`, etc.).
- Keep L534-546 (`test_superseded_constants_match_git_history`) and L67-77.

**`tests/test_archive_assessment_applicability_authority_v2.py`**: L31-33 `with_decisions_lineage` synthetic dict needs `normalisation`; L143-146 required-keys list -> new names plus a negative test that stray `digest_normalisation` is rejected (schema `additionalProperties: False`); L164 `test_committed_schema_equals_schema_function` goes red until Phase 9 (accepted). Do not add mutations to `NEGATIVE_MUTATIONS` (count 26 pinned at publication test L609-611, L673).

## Shared Patterns

### Fail-closed validation
**Source:** publisher L60, L291 (`AuthorityError`, accumulate then `raise AuthorityError('; '.join(errors))`).
**Apply to:** `validate_lineage`, `git_show`. Missing history, file, or unknown normalisation raises; never skip (D-11).

### Repo-relative path hygiene
**Source:** publisher L69-73 `contains_absolute`, and L620 `'..' in rp.replace('\\', '/').split('/')`.
**Apply to:** all `relative_path` values and the `git show` argument.

### Byte-exact handling on Windows
**Source:** publisher L62-64 (`read_bytes`), tests L480-482 (bytes-mode subprocess).
**Apply to:** `git_show`, `validate_lineage`, all new tests. Never `read_text` or text-mode subprocess for CRLF files.

### Deterministic JSON
**Source:** publisher L65-67 `dump` (`indent=2, sort_keys=True`, `newline='\n'`).
**Apply to:** any generated output (none regenerated in Phase 7).

### Staging
Explicit paths only; never `git add -A`; unrelated modified files (`registry/adjudication_rules.json`, `registry/policy_decisions.json`) stay out.

## No Analog Found

| File/Function | Role | Data Flow | Reason |
|---|---|---|---|
| `git_show()` in the publisher | utility | git subprocess | Publisher currently has no subprocess; only tests (L480-482) and reply builder (text mode, unsuitable for blobs) call git. Use research Q4 helper. |
| Temp-git-repo fixture for commit-pinned negative tests | test fixture | git | No existing fixture creates a temp repo; build per research "Don't Hand-Roll" row. |

## Metadata

**Analog search scope:** `scripts/publish_archive_assessment_applicability_authority_v2.py` (L1-230, 255-314, 595-646), `tests/test_archive_assessment_applicability_authority_v2_publication.py` (L1-90, 476-565), `.gitattributes`.
**Files scanned:** 4 read directly; other line refs (reply builder, decisions builder, ems-validate.yml, v2 test) taken from 07-RESEARCH.md and not re-read.
**Pattern extraction date:** 2026-10-20
