# Phase 4: Certified Publication - Pattern Map

**Mapped:** 2026-10-14
**Files analyzed:** 14 new/modified
**Analogs found:** 13 / 14 (only `.gitattributes` has none)

All excerpts are from files read this session. Line numbers refer to the current working tree.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/publish_archive_assessment_applicability_authority_v2.py` (modify: `lf_digest`, `build_published_authority`, `validate_publication`, `publish`, schema change, new CLI flags) | publisher / validator | batch, transform | same file (build/validate/schema) + `scripts/publish_archive_assessment_applicability_authority.py` (`publish()`) | exact |
| `scripts/build_archive_assessment_governance_decisions.py` (modify: CR-01..03, WR-01..09) | builder / validator | transform | itself | exact |
| `schemas/archive_assessment_applicability_authority_v2.schema.json` (regenerated, never hand-edited) | config (schema) | n/a | `schema()` in v2 publisher, emitted via `--emit-schema` | exact |
| `registry/archive_assessment_governance_decisions.json` (possible header-only rewrite) | registry | file-I/O | `V2.dump` / `--build` in builder | exact |
| `schemas/archive_assessment_governance_decisions.schema.json` (regenerated if header key added) | config (schema) | n/a | `decisions_schema()` in builder | exact |
| `.gitattributes` (new, narrow) | config | n/a | none in repo | no analog |
| `registry/archive_assessment_applicability_authority_v2.json` (generated) | registry authority | batch | `registry/archive_assessment_applicability_authority.json` (v1) | exact |
| `registry/archive_assessment_applicability_authority_v2_signoff.json` (new; name is discretion) | registry record | file-I/O | `registry/archive_assessment_governance_wording_approval.json` | role-match |
| `registry/archive_assessment_applicability_authority_v2_publication_record.json` (new, follow-up commit) | registry record | file-I/O | `registry/archive_assessment_rule_proposals_drafting_record.json` | role-match |
| `generated/archive-assessment/ems-aa3-v2/*` (matrix, semantic, negative, AA4 traceability, certification, report `.md`, manifest) | generated outputs | batch | `generated/archive-assessment/ems-aa3/*` written by v1 `publish()` | exact |
| `tests/test_archive_assessment_applicability_authority_v2_publication.py` (new) | test | request-response | `tests/test_archive_assessment_applicability_authority_v2.py` | exact |
| git-gated tests (ancestor SHA, publication commit file set, blob digests) inside the new test file | test | git history | `tests/test_archive_assessment_rule_proposals_record.py` | exact |
| `tests/test_archive_assessment_governance_decisions.py` (add review-fix tests, `eed4a5f` equality test) | test | transform | itself | exact |
| `tests/test_archive_assessment_governance_answers.py` (add CR-02/WR-03 tests) | test | transform | itself | exact |

## Pattern Assignments

### `scripts/publish_archive_assessment_applicability_authority_v2.py` (publisher, batch)

**Analog A (same file, extend in place):** keep one-line helper style, single quotes, `AuthorityError`, `build_*`/`validate_*` split.

**Imports and constants** (lines 1-27):
```python
from __future__ import annotations
import argparse, hashlib, json, re   # one per line in source
from pathlib import Path
import jsonschema
import yaml
ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = REGISTRY / 'archive_assessment_applicability_authority_v2.json'
V1_AUTHORITY = REGISTRY / 'archive_assessment_applicability_authority.json'
DECISIONS = [f'AA1-GOV-{n:03d}' for n in range(1, 9)]
AUTHORITY_ID_RE = r'^AA4-GOV-[0-9]{3}$'
class AuthorityError(ValueError): pass
```
Note: the module-level name `DECISIONS` here is the eight AA1 ids. Do not reuse that name for the decisions file path; the builder's `DECISIONS` is the file path. Name the new path constant differently (e.g. `GOVERNANCE_DECISIONS`).

**Helpers to replace (WR-08, CR-01)** (lines 44-48). Current `digest` is raw bytes and `dump` uses `write_text` (CRLF on Windows). Target per research Pattern 4:
```python
def digest(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()          # current, CRLF-dependent
def dump(p: Path, value: object) -> None:                                              # current
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
# new:
def lf_bytes(b: bytes) -> bytes: return b.replace(b'\r\n', b'\n')
def lf_digest(p: Path) -> str: return hashlib.sha256(lf_bytes(p.read_bytes())).hexdigest()
def dump(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(json.dumps(value, indent=2, sort_keys=True) + '\n')
```
The builder already has the `newline='\n'` write idiom at its line 325 (`with open(VIEW, 'w', encoding='utf-8', newline='\n') as f: f.write(...)`) and the LF rule at its line 71 (`answers_digest`); `answers_digest` should delegate to `V2.lf_digest`.

**Lineage digests to switch to LF** (lines 130-131):
```python
'catalog_reference': {'relative_path': 'registry/control_catalog.yaml', 'sha256': digest(CATALOG), 'required_for_deterministic_compilation': False},
'supersedes': {'authority_id': v1['authority_id'], 'version': '1.0.0', 'commit': '62a8955', 'relative_path': 'registry/archive_assessment_applicability_authority.json', 'sha256': digest(V1_AUTHORITY)},
```
Add beside them a `governance_decisions` entry (`relative_path`, LF `sha256`, `record_count`, `drafting_commit`) and a normalisation field. Copy the AA1/AA2 lineage values from the v1 registry file as lines 97-98, 129 already do (`lin = v1['source_lineage']`).

**Overlay (Pattern 1):** keep `build_authority()` (lines 94-134) returning all-undecided so the existing 156-line test file stays green; add `build_published_authority()` that calls it then overlays. Row construction fields to remember (lines 112-115): `not_applicable_decision_state`, `not_applicable_rule`, `not_applicable_authority`, `decision_ids: list(DECISIONS)`.

**Validator pattern** (lines 152-195): accumulate `errors` list, `raise AuthorityError('; '.join(errors))`. Per-row decided-state logic at lines 184-192:
```python
state = r.get('not_applicable_decision_state'); rule = r.get('not_applicable_rule'); auth = r.get('not_applicable_authority')
if state not in DECISION_STATES: errors.append(f'{cid}: not_applicable_decision_state invalid'); continue
...
elif known_decision_ids is not None and auth not in known_decision_ids: errors.append(f'{cid}: authority {auth} is not an approved decision id')
```
New `validate_publication(a)` should call `validate_authority(a, known_decision_ids=...)` first, then add the D-09, D-10, D-12 and D-13 checks in the same errors-list style. Do not put the 21-control pin into `validate_authority` (existing tests mutate `controls[0]` = EMS-CTRL-001).

**Schema change** (lines 197-215): `schema()` is one nested dict. Add to the top-level `required` (line 206) and `properties` (line 207-208) an `applicability_decision_ids` entry modelled on the existing `approved_governance_decision_ids`:
```python
'approved_governance_decision_ids':{'type':'array','minItems':8,'maxItems':8,'items':{'type':'string','pattern':'^AA1-GOV-00[1-8]$'},'uniqueItems':True},
```
New list items use `AUTHORITY_ID_RE` (`^AA4-GOV-[0-9]{3}$`), `uniqueItems: True`, `maxItems: 21`, `minItems: 0` so the base builder can emit `[]`. Per-row `decision_ids` stays 8 items (line 214). The `branch()` helper (lines 201-202) already enforces state/rule/authority combinations.

**CLI pattern** (lines 233-240): argparse flags as `store_true`, one-line `if/elif`, `parser.error(...)` for none. Extend with `--publish` and `--dry-run`; `--validate` must keep the "not published" `AuthorityError` when the file is absent (line 236) and then run `validate_publication`, jsonschema, and the D-17 rebuild-and-compare. Do not call git from the publisher (D-18).

**Analog B (`publish()` in v1, lines 111-128): output set to mirror.**

Output set and artifact list (lines 116-127):
```python
trace = {'traceability_type':'AA2_TO_AA3_ARCHIVE_APPLICABILITY_TRACEABILITY','created_at':now, ... 'control_traceability_records':[{'control_id':r['control_id'],'decision_ids':DECISIONS} for r in authority['controls']]}
matrix = {'authority_id':authority['authority_id'],'control_population':80,'unique_control_count':80,'missing_controls':0,'duplicate_controls':0,'unmapped_controls':0,'controls':authority['controls']}
semantic = {'result':'PASS','semantic_conflict_count':0,'offline_deterministic_authority':True,'checks':[...]}
negative = {'result':'PASS','negative_invariant_tests':[{'mutation':x,'result':'REJECTED_FAIL_CLOSED'} for x in [...]]}
cert = {'certification_type':'EMS_AA3_..._PUBLICATION_CERTIFICATION','certification_version':'1.0','created_at':now,'authority_id':...,'authority_sha256':ash,'schema_sha256':ssh, ..., 'prohibitions':{'evaluator_executions':0,'hayes_modifications':0, ...}}
manifest = {'manifest_type':'EMS_AA3_..._PUBLICATION_MANIFEST','created_at':now,'authority_id':...,'artifacts':[{'relative_path':p,'sha256':digest(ROOT/p)} for p in artifact_paths],'self_entry_exclusion_reason':'A SHA-256 manifest cannot include a hash of itself without recursion.'}
```
v1 output file names to mirror with a v2 marker (all under `GENERATED = ROOT/'generated'/'archive-assessment'/'ems-aa3'`): `archive_assessment_applicability_authority_matrix.json`, `archive_assessment_applicability_semantic_validation.json`, `archive_assessment_applicability_negative_invariant_validation.json`, `EMS_AA3_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION.json`, `EMS_AA3_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION.md`, `ems_aa3_archive_applicability_authority_publication_manifest.json`, plus `aa2_to_aa3_decision_traceability.json` (the AA4 traceability file replaces this role).

Things to change when copying (do not copy):
- `now = datetime.now(UTC).isoformat()` (line 115) becomes a fixed `PUBLISHED_ON` constant (D-16); drop the `datetime` import.
- `digest(...)` for artifacts and cert/manifest hashes becomes `lf_digest(...)`; add a `digest_normalisation: 'CRLF_TO_LF'` field to cert and manifest (precedent: `answers_sha256_normalisation`).
- Report write at line 124 uses `write_text(..., encoding='utf-8')`; use `newline='\n'`.
- `RP1B_A_READY` / `RP1C_AUTHORITY_READY` flags and AA2 closure reads (`AA2 / ...` under gitignored `generated/ems-aa2`, lines 17, 46) must not be copied; D-18 says read only tracked inputs and take AA2 digests from the v1 registry.
- Print result as a JSON line on success (line 128): `print(json.dumps({'status':'PASS','authority_sha256':ash,'manifest_sha256':...}))`.

---

### `scripts/build_archive_assessment_governance_decisions.py` (review fixes, transform)

Edit-in-place; the fix map is research "Phase 3 Review Fix Map". Concrete anchors in the current file:

- **CR-01 / WR-08 (line 71, 204, 223, 325, 332):** `answers_digest` already normalises CRLF; replace with `V2.lf_digest`. Lines 204 and 223 use raw `V2.digest(DRAFTING_RECORD)` / `V2.digest(PROPOSALS)`; switch to `V2.lf_digest`. Add a `frozen_input_sha256_normalisation` key to `HEADER_KEYS` (line 40), `build_decisions` (line 201-205), `validate_decisions` (header key check line 213 and normalisation check at line 227), and `decisions_schema()` (lines 306-310) following the existing `answers_sha256_normalisation` handling in all four places.
- **CR-02 (lines 226-227, 335-338):** line 226 only regex-checks `answers_sha256`; compare it to `answers_digest(ANSWERS)`. `--validate` (lines 335-338) should also require `decisions_text(doc) == decisions_text(build_from_files())`.
- **CR-03 (lines 111, 124, 127-160, 188-200):** `strict_checks(first, ...)` runs on the first 21 only (line 124); run on all entries.
- **WR-07 (lines 330-334):** `--build` equality check uses `DECISIONS.read_bytes().replace(b'\r\n', b'\n')`; keep the LF-compare idiom when extending to append-only / header-only differences.
- Module loading pattern for the shared helper is already in place (lines 17-20):
```python
_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V2)
AuthorityError = V2.AuthorityError
```
Import `lf_digest` and `dump` via `V2.`; do not duplicate the rule.

- Latest-unsuperseded logic to reuse as a reference (lines 235-287): `superseded.add(sup)` then `counts[cid]` over records not in `superseded`. The v2 overlay needs the same computation (research "Code Examples", `latest_records`).

---

### `registry/archive_assessment_applicability_authority_v2_signoff.json` (registry record, file-I/O)

**Analog:** `registry/archive_assessment_governance_wording_approval.json` (Phase 3 approval, same approver, same status-tag style).

Shape to copy:
```json
{
  "approval": {"approver": "Oscar Mack", "date": "2026-10-13", "role": "EMS_GOVERNANCE_AUTHORITY", "scope": "..."},
  "settings": {...},
  "statement_sha256": {...},
  "statements": {...},
  "status": "WORDING_APPROVAL"
}
```
For the sign-off use `status` such as `PUBLICATION_SIGNOFF`, an `approval` object (`approver`, `role`, `date`, `scope`), plus `authority_sha256` (LF), `authority_sha256_normalisation: 'CRLF_TO_LF'`, and the dual-role statement (`DUAL_ROLE_STATEMENT`, builder line 32; `APPROVER_ROLES`, line 31). Keys are alphabetical (`sort_keys=True`). Must not reference the certification (avoids a hash cycle). It is written only after the blocking human checkpoint (D-19).

---

### `registry/archive_assessment_applicability_authority_v2_publication_record.json` (registry record, follow-up commit)

**Analog:** `registry/archive_assessment_rule_proposals_drafting_record.json`, which carries `drafting_commit`, `proposals_sha256`, `brief_commit`, etc. (key names confirmed from `tests/test_archive_assessment_rule_proposals_record.py` lines 81-90). Use the same flat record style: `publication_commit` (40-hex), `authority_id`, `version`, `authority_sha256`, `manifest_sha256`, normalisation field. The 40-hex pattern constant already exists as `SHA40_RE` (builder line 51); the 64-hex as `SHA64_RE` (line 52).

---

### `tests/test_archive_assessment_applicability_authority_v2_publication.py` (new test, request-response)

**Analog:** `tests/test_archive_assessment_applicability_authority_v2.py`.

Module-load and helper pattern (lines 1-44):
```python
SCRIPT = Path(__file__).parents[1] / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py'
SPEC = importlib.util.spec_from_file_location('aa3_authority_v2', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError

def invalid(mutator):
    value = copy.deepcopy(build_authority())
    mutator(value)
    with pytest.raises(AuthorityError):
        validate_authority(value)

def rule(*pairs): return {'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': f, 'state': s} for f, s in pairs]}
def decide(c, state, r, a): c.update({'not_applicable_decision_state': state, 'not_applicable_rule': r, 'not_applicable_authority': a})
def ok(mutator): ...validate_authority(value); jsonschema.Draft202012Validator(schema()).validate(value)
def both_reject(mutator): invalid(mutator); schema_rejects(mutator)
```
Copy this verbatim, but point `invalid` at a deep copy of `build_published_authority()` and `validate_publication`. One-line `def test_x(): both_reject(lambda a: ...)` style. Mutation tests: replace one of the 21 authority ids, swap a rule field, flip a state, add a 22nd decided control, change a v1 field on an undecided row, remove an id from `applicability_decision_ids`, cite one id twice.

Real-file tests gate (Pitfall 3, D-Claude's discretion): `pytest.mark.skipif(not MODULE.AUTHORITY.exists(), reason='v2 authority not yet published')`, and the same for the publication record. Resolution tests use `resolve_applicability(control, facts)` (v2 lines 217-231) with `KNOWN_TRUE`/`KNOWN_FALSE`/`UNKNOWN` for CTRL-030/039 (`production`) and CTRL-052 (`ai_enabled`).

**Git-gated tests** (copy from `tests/test_archive_assessment_rule_proposals_record.py` lines 26-43, 65-67, 81-85):
```python
def git(*args, text=True):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return r if not text else subprocess.CompletedProcess(r.args, r.returncode, r.stdout.decode('utf-8').strip(), r.stderr.decode('utf-8').strip())
def sha(b): return hashlib.sha256(b).hexdigest()
def git_ready():
    try: r = git('rev-parse', '--is-shallow-repository')
    except OSError: return 'git is unavailable'
    if r.returncode != 0: return 'not a git repository'
    if r.stdout == 'true': return 'shallow repository, history is incomplete'
    return None
def needs_git(fn):
    reason = git_ready()
    return pytest.mark.skipif(reason is not None, reason=reason or '')(fn)

@needs_git
def test_recorded_commit_is_ancestor():
    assert git('merge-base', '--is-ancestor', record()['drafting_commit'], 'HEAD').returncode == 0
@needs_git
def test_drafting_commit_changed_exactly_one_path():
    r = git('diff-tree', '--no-commit-id', '--name-only', '-r', record()['drafting_commit'])
    assert r.stdout.splitlines() == [PROPOSALS]
```
Reuse these shapes for: publication SHA is an ancestor of HEAD; `git diff-tree --no-commit-id --name-only -r <sha>` equals exactly {v2 authority, `ems-aa3-v2/*` outputs, sign-off record} and excludes `registry/adjudication_rules.json` and `registry/policy_decisions.json` (PUB-06); LF digest of `git show <sha>:<authority>` bytes equals the recorded digest (use `lf_bytes` on `git(..., text=False).stdout`). For the eed4a5f record-equality test (D-07), use `git('show', f'eed4a5f:{path}', text=False).stdout` and compare parsed `records`.

Also import-by-path pattern for a second module (lines 13-21 of the record test) if the new test needs the builder module.

---

### `.gitattributes` (config) - no analog

No `.gitattributes` exists in the repo. Use research guidance: explicit file list, `text eol=lf`, plus `generated/archive-assessment/ems-aa3-v2/** text eol=lf`. Do not list v1 files or use broad globs (D-02, D-03). Verify with `git status --short -- <listed paths>` afterwards; renormalise by explicit path only if needed.

---

## Shared Patterns

### Deterministic JSON writes
**Source:** `scripts/publish_archive_assessment_applicability_authority_v2.py` lines 45-47 (to be fixed with `newline='\n'`)
**Apply to:** every generated file, the authority, the sign-off record, the publication record, any rewritten decisions file.
`json.dumps(value, indent=2, sort_keys=True) + '\n'`, no `now()`, no absolute paths (`contains_absolute`, lines 49-53).

### LF digest + normalisation field
**Source:** `answers_digest` (builder line 71) and `'answers_sha256_normalisation': 'CRLF_TO_LF'` (builder lines 205, 227, 309)
**Apply to:** manifest, certification, lineage, frozen-input digests, sign-off, publication record. One shared `lf_digest` in the v2 module; the builder imports it via `V2`.

### Fail-closed validation
**Source:** v2 `validate_authority` (lines 152-195) and builder `validate_decisions` (lines 207-289)
**Apply to:** `validate_publication`, review fixes. Accumulate messages in `errors`, `raise AuthorityError('; '.join(errors))`; type-guard before indexing (WR-06); expected data states return values, invariant violations raise.

### Build/validate pairs and mutation tests
**Source:** v2 test `invalid(mutator)` (lines 20-24) with `copy.deepcopy`
**Apply to:** all new validator tests; every review fix needs one failing-mutation test (WR-09).

### Schema emitted from code
**Source:** `schema()` and `--emit-schema` (`dump(SCHEMA, schema())`, v2 line 238); builder `--emit-schema` (line 329)
**Apply to:** the v2 schema and (if the header gains a key) the decisions schema. Never hand-edit; regenerate in the same commit as the code change.

### CLI shape
**Source:** v2 `main()` lines 233-240; builder `main()` lines 318-343
`argparse` flags, `PASS` print on success, uncaught `AuthorityError` as failure, `if __name__ == '__main__': main()`.

### Git staging protocol (PUB-06)
**Source:** research "Git staging protocol"
**Apply to:** every commit: `git add -f -- <explicit paths>` (`-f` only for `generated/`), `git diff --cached --name-only` must equal the intended list, no `-A`, `.` or `-a`. The tree holds two modified registry files and about 60 untracked unrelated files.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `.gitattributes` | config | n/a | No `.gitattributes` exists; follow D-02 and the research line-ending section |
| In-memory rebuild-and-compare `--validate` (D-17) | validator | transform | v1 `--validate` only validates the registry file and schema (v1 lines 132-133); the rebuild-and-byte-compare logic is new. Use research "Byte-identical re-run check" snippet |
| Dry-run summary and blocking human gate (D-19) | publisher CLI | request-response | No existing script prints a sign-off summary; the Phase 3 wording approval is the record precedent only, not code |

## Metadata

**Analog search scope:** `scripts/` (v1/v2 publishers, builder), `tests/test_archive_assessment_*.py`, `registry/archive_assessment_*`, `generated/archive-assessment/ems-aa3/`
**Files read in full:** 4 scripts/tests (v2 publisher, v1 publisher, builder, record test), v2 test (first 70 of 156 lines), v1 test (33 lines), wording approval JSON
**Pattern extraction date:** 2026-10-14
