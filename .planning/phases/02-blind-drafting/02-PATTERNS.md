# Phase 2: Blind Drafting - Pattern Map

**Mapped:** 2026-10-13
**Files analyzed:** 7 (new files; no existing file is modified)
**Analogs found:** 6 / 7 (one file has a partial analog only; one sub-feature has none)

Scope note: analogs were taken only from the v2 publisher, its schema output and the two archive-assessment test modules. `registry/control_catalog.yaml` was inspected for structure only (see below); no control definitions are reproduced here and no proposal outcome is stated or implied.

## File Classification

| New File (names discretionary) | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/validate_archive_assessment_rule_proposals.py` | validator/schema emitter | transform (load, validate, raise) | `scripts/publish_archive_assessment_applicability_authority_v2.py` | exact (role), imports from it |
| `schemas/archive_assessment_not_applicable_rule_proposals.schema.json` | config (schema) | emitted by code | `schemas/archive_assessment_applicability_authority_v2.schema.json` (written by `schema()` + `dump()`) | exact |
| `registry/archive_assessment_not_applicable_rule_proposals.json` | registry data (hand-authored, frozen) | file-I/O (written verbatim) | `registry/archive_assessment_applicability_authority.json` (shape of header/controls only) | partial: it is drafter output, not built |
| `tests/test_archive_assessment_rule_proposals.py` | test | request-response (mutate, assert raises) | `tests/test_archive_assessment_applicability_authority_v2.py` | exact |
| `docs/<drafter brief>.md` | governance doc (brief) | file-I/O (generated from code and catalog extract) | `docs/*_REQUIREMENTS.md` convention; frame text from `semantics()` | role-match |
| `registry/archive_assessment_rule_proposals_drafting_record.json` | registry data | file-I/O | `dump()` output convention of the v2 publisher | role-match |
| Git ancestor / blob-hash / term-scan tests (inside the test module) | test | subprocess (git), file scan | none in `tests/` (grep for `subprocess.run`, `merge-base`, `hash-object` found nothing) | no analog |

## Pattern Assignments

### `scripts/validate_archive_assessment_rule_proposals.py` (validator, transform)

**Analog:** `scripts/publish_archive_assessment_applicability_authority_v2.py`

Style rules: `from __future__ import annotations`, single quotes, compact one-line helpers, `ROOT`/`REGISTRY`/`SCHEMAS` path constants, `AuthorityError(ValueError)`.

**Imports and path constants** (lines 1-17):
```python
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'registry'
SCHEMAS = ROOT / 'schemas'
CATALOG = REGISTRY / 'control_catalog.yaml'
```
Add `PROPOSALS`, `SCHEMA` constants the same way. Import the v2 module by file location (it is a script, not a package), as the tests do:
```python
SPEC = importlib.util.spec_from_file_location('aa3_authority_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(V2)
```
Module import has no side effects (argparse is inside `main()`), so this is safe.

**Helpers to copy or reuse** (lines 42-61): `AuthorityError`, `digest`, `dump`, `load`, `contains_absolute`, `catalog_controls`. Prefer `V2.AuthorityError`, `V2.contains_absolute`, `V2.digest`, `V2.load`, `V2.dump`, `V2.catalog_controls` rather than copying them (D-13; "do not re-implement"). Use the same `AuthorityError` class so tests can use one exception type.
```python
class AuthorityError(ValueError): pass
def digest(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p: Path, value: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
def load(p: Path) -> dict: return json.loads(p.read_text(encoding='utf-8'))
```
Note: `dump()` is only for the emitted schema. The proposals file itself is written verbatim (Open Question 2 in RESEARCH); the validator must parse it and not require sorted keys.

**Rule validation to reuse, not re-implement** (lines 136-150): `V2.validate_rule(cid, rule, errors)` appends messages to `errors` and returns None. Call it only when `proposed_outcome` is the rule outcome:
```python
def validate_rule(cid: str, rule: object, errors: list) -> None:
    if not isinstance(rule, dict) or set(rule) != {'combination', 'conditions'}:
        errors.append(f'{cid}: rule must be an object with exactly combination and conditions'); return
    if rule['combination'] != COMBINATION: errors.append(f'{cid}: rule combination invalid')
    ...
```
Constants to reuse: `V2.RULE_FIELDS`, `V2.NON_RULE_FIELDS`, `V2.CONDITION_STATES`, `V2.COMBINATION`, `V2.FIELD_DEFINITIONS`, `V2.RESOLUTION`, `V2.semantics()`.

**Accumulate-then-raise validation pattern** (lines 152-195, shape only):
```python
def validate_authority(a: dict, known_decision_ids: set | None = None) -> None:
    errors = []
    req = {...}
    if not req <= set(a): errors.append('missing required top-level authority fields')
    ...
    catalog_ids = {c['control_id'] for c in catalog_controls()}; rows = a.get('controls', []); ids = [r.get('control_id') for r in rows]
    if len(ids) != 80 or len(set(ids)) != 80: errors.append('duplicate or incorrect control population count')
    if set(ids) != catalog_ids: errors.append('missing or unknown control ID')
    for r in rows:
        cid = r.get('control_id')
        ...
        if state == 'RULE_PUBLISHED': validate_rule(cid, rule, errors)
        elif rule is not None: errors.append(f'{cid}: NO_RULE_WILL_BE_PUBLISHED requires null rule')
    if contains_absolute(a): errors.append('absolute local path used as authority identity')
    if errors: raise AuthorityError('; '.join(errors))
```
Adapt to `validate_proposals(p, catalog=None)`: exactly 21 fixed ids, no duplicates, status `DRAFT_NO_AUTHORITY`, rule present iff rule outcome, forbid keys `not_applicable_authority` / `decision_id` / `AA4-GOV-` strings (the v2 `AUTHORITY_ID_RE = r'^AA4-GOV-[0-9]{3}$'` at line 26 can be reused as the pattern to reject), header frame equals `V2.semantics()` pieces (mirror lines 164-168: pin everything except `field_definitions`, then check definitions separately), `contains_absolute`.

**Frame-pinning idiom** (lines 164-168):
```python
pin = {k: v for k, v in sem.items() if k != 'field_definitions'}
expected = {k: v for k, v in semantics().items() if k != 'field_definitions'}
if pin != expected: errors.append('not_applicable_semantics does not match the published semantics')
fd = sem.get('field_definitions')
if not isinstance(fd, dict) or set(fd) != set(RULE_FIELDS) or any(not isinstance(v, str) or not v.strip() for v in fd.values()): errors.append('field_definitions must define exactly the four rule fields with non-empty text')
```

**Schema emission pattern** (lines 197-215): `schema()` returns a dict with `'$schema': 'https://json-schema.org/draft/2020-12/schema'`, `additionalProperties: False` on every object, `required` lists, `enum`/`const` built from the module constants, and an if/then `branch(...)` helper to tie `proposed_outcome` to rule-present / rule-null:
```python
def branch(state, rule_s, auth_s):
    return {'if':{'properties':{'not_applicable_decision_state':{'const':state}},'required':['not_applicable_decision_state']},'then':{'properties':{'not_applicable_rule':rule_s,'not_applicable_authority':auth_s}}}
```
Rule sub-schema to reuse verbatim (line 198-199): `cond` and `rule` objects with `field` enum from `RULE_FIELDS`, `state` enum from `CONDITION_STATES`, `combination` const, `conditions` minItems 1, maxItems `len(RULE_FIELDS)`. Use `anyOf: [rule, {'type':'null'}]` for `proposed_rule`. Set `additionalProperties: False` on proposal objects so `not_applicable_authority` and decision ids cannot appear (Pitfall 8).

**CLI pattern** (lines 233-240):
```python
def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument('--validate', action='store_true'); parser.add_argument('--emit-schema', action='store_true'); args = parser.parse_args()
    if args.validate:
        if not AUTHORITY.exists(): raise AuthorityError('v2 registry authority file is not published')
        a = load(AUTHORITY); validate_authority(a); jsonschema.Draft202012Validator(load(SCHEMA)).validate(a); print('PASS')
    elif args.emit_schema: dump(SCHEMA, schema())
    else: parser.error('one of --validate or --emit-schema is required')
if __name__ == '__main__': main()
```

**Build/validate split caveat:** the convention is `build_x()` plus `validate_x(x)`. Here the real object is hand-authored, so there is nothing to `build_` for production. Provide a `build_fixture()`-style helper only inside the tests (neutral placeholder text), keeping the validator pure.

**Catalog structure (structure only):** `registry/control_catalog.yaml` has top-level key `controls`, a list of mappings. Each entry carries the same eight keys: `control_id`, `control_name`, `scope`, `scope_owner`, `inheritance_allowed`, `evidence_authority`, `rationale`, `classification_status`. The 21 requested entries have no `description` key. Load with `yaml.safe_load(CATALOG.read_text(encoding='utf-8'))['controls']` (as `catalog_controls()` does, lines 55-61). The file is CRLF; hash raw bytes.

---

### `schemas/archive_assessment_not_applicable_rule_proposals.schema.json` (config, emitted)

**Analog:** `schemas/archive_assessment_applicability_authority_v2.schema.json`, produced by `dump(SCHEMA, schema())` via `--emit-schema`. Never hand-edit. Committed file must equal `schema()` output:

**Test pattern** (v2 tests line 135):
```python
def test_committed_schema_equals_schema_function(): assert json.loads(MODULE.SCHEMA.read_text(encoding='utf-8')) == schema()
```

---

### `tests/test_archive_assessment_rule_proposals.py` (test)

**Analog:** `tests/test_archive_assessment_applicability_authority_v2.py`

**Module loading and imports** (lines 1-18):
```python
import copy
import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py'
SPEC = importlib.util.spec_from_file_location('aa3_authority_v2', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
```
Use the same `spec_from_file_location` for the new validator script; no `scripts` package import.

**Mutator helpers** (lines 20-44): copy exactly, swapping `build_authority()`/`validate_authority` for the fixture builder and `validate_proposals`:
```python
def invalid(mutator):
    value = copy.deepcopy(build_authority())
    mutator(value)
    with pytest.raises(AuthorityError):
        validate_authority(value)

def rule(*pairs): return {'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': f, 'state': s} for f, s in pairs]}

def ok(mutator):
    value = copy.deepcopy(build_authority())
    mutator(value)
    validate_authority(value)
    jsonschema.Draft202012Validator(schema()).validate(value)

def schema_rejects(mutator): ...
def both_reject(mutator):
    invalid(mutator)
    schema_rejects(mutator)
```

**One-liner test style** (lines 48-100): `def test_<case>_fails_closed(): both_reject(lambda a: ...)`. Reuse for: unusable field in rule (`tier`, `owner`, `service_criticality`, `data_classification`, `region`), `UNKNOWN` as a condition state, empty conditions, duplicate field (`invalid` only, validator-only), extra key in rule or condition, wrong combination, rule with no-rule outcome, no-rule outcome with a rule, missing/duplicate/unknown control id, wrong count, `not_applicable_authority` or decision-id key present, absolute path, status other than `DRAFT_NO_AUTHORITY`, frame tampering (compare lines 108-121 for the `sem(a)` mutation pattern: `both_reject(lambda a: sem(a).__setitem__('unknown_is_never_not_applicable', False))`, `resolution` row removal, `field_definitions` pop/empty).

**Fixtures:** the real file does not exist while tooling is built, so build an in-test fixture object with neutral placeholder text and ids from the fixed list. Fixture text must not be a plausible per-control outcome.

**Real-file tests:** gate on `pytest.mark.skipif(not PROPOSALS.exists(), ...)` so nothing sits red before the drafting commit (RESEARCH Pitfall 3). The tests to gate: validator passes on the real file; embedded `catalog_inputs` equal the live catalog entries (D-04); recorded catalog SHA-256 equals `hashlib.sha256(CATALOG.read_bytes())`; blob id equals `git hash-object`.

**Regression guard worth copying** (lines 136-138):
```python
def test_v2_builder_does_not_use_generated_dir():
    src = SCRIPT.read_text(encoding='utf-8')
    assert 'ems-aa2' not in src and 'generated' not in src
```
Adapt to assert the new validator does not reference `generated`.

**Also keep passing unchanged:** `tests/test_archive_assessment_applicability_authority.py` and the v2 test (regression run; Pitfall 7). The v1 test uses the same `invalid(mutator)` and `spec_from_file_location` conventions (lines 1-19).

---

### Git / hashing / term-scan tests (no analog)

No test in `tests/` shells out to git (grep for `subprocess.run`, `merge-base`, `hash-object` returned no matches). Use RESEARCH "Code Examples" and "Recording the SHA later" as the pattern source:
- `subprocess.run(['git', ...], cwd=ROOT, capture_output=True, text=True)`, list args, no shell strings.
- `git merge-base --is-ancestor <sha> HEAD` returncode 0.
- Skip when `git rev-parse --is-shallow-repository` prints `true`, or git is unavailable.
- Hash `git show <sha>:<path>` bytes (not the working file; autocrlf is on) for the proposals file and the brief.
- `git diff-tree --no-commit-id --name-only -r <sha>` equals exactly the proposals path.
- Term scan: terms live in the test module only; `re.IGNORECASE` over raw text of proposals file, brief and drafting record. Obtain the SHA values from the user or STATE.md at execution time; do not copy them into any scanned file.

---

### `docs/<drafter brief>.md` (governance doc, generated frame text)

**Analog:** frame text comes from code, not from `.planning/` files. Inline these from `V2` at brief-authoring time:
- Rule shape, from `semantics()` keys `condition_states`, `condition_combination`, `rule_condition_fields`, `fields_not_usable_in_rules_statement`, `min_conditions`, `field_may_appear_once` (lines 63-81).
- Field definitions: the four sentences in `FIELD_DEFINITIONS` (lines 28-33) only; not the `Source:` lines in `01-FIELD-DEFINITIONS.md`.
- Resolution table: `RESOLUTION` (lines 34-40) and `semantics()['statements']` (lines 82-91); these are already free of the D-25 terms.
- 21 catalog entries: extract programmatically (`yaml.safe_load`, filter the fixed id list, dump), never hand-edited, never all 80.
- Output skeleton uses placeholders only (`"control_id": "<ID>"`), no worked example using any of the 21 controls.
Placement: tracked under `docs/` (not `generated/`, which is gitignored). Existing `docs/*_REQUIREMENTS.md` naming is uppercase snake; filename must contain no D-25 term.

---

### `registry/archive_assessment_rule_proposals_drafting_record.json` (registry data)

**Analog:** deterministic JSON convention of `dump()` (`json.dumps(value, indent=2, sort_keys=True) + '\n'`, line 47) with repo-relative forward-slash paths only (`contains_absolute` check, lines 49-53). Fields from D-24. Hashes are computed over committed blob bytes, not the working copy. Follow the lineage style of `source_lineage.catalog_reference` (v2 lines 130): `{'relative_path': 'registry/control_catalog.yaml', 'sha256': digest(CATALOG), ...}`.

---

## Shared Patterns

### Fail-closed accumulate-then-raise
**Source:** `scripts/publish_archive_assessment_applicability_authority_v2.py` lines 152-195
**Apply to:** the proposals validator, record validation
Append every violation to `errors`, raise `AuthorityError('; '.join(errors))` once. Unknown, missing or extra keys are errors, never defaults.

### No absolute paths
**Source:** same file, lines 49-53 and 171
**Apply to:** proposals file, drafting record, schema
`if contains_absolute(a): errors.append('absolute local path used as authority identity')`

### Deterministic JSON and schema-from-code
**Source:** same file lines 44-48, 197-215, 238; test line 135
**Apply to:** emitted schema only (proposals file is written verbatim; drafting record may use `dump()` convention)

### Mutator-based negative tests
**Source:** `tests/test_archive_assessment_applicability_authority_v2.py` lines 20-44
**Apply to:** all validator tests

### Explicit-path staging
**Source:** RESEARCH "Single drafting commit without the dirty tree"
**Apply to:** every commit in this phase (the working tree holds unrelated modified and untracked files, including `registry/adjudication_rules.json` and `registry/policy_decisions.json`)
`git diff --cached --name-only` empty before; `git add -- <explicit path>`; `git diff --cached --name-only` lists exactly the intended paths; no `-a`, `-A`, `.`, or `-u`.

## No Analog Found

| File / feature | Role | Data Flow | Reason |
|---|---|---|---|
| Git ancestor, blob-hash and shallow-clone tests | test | subprocess | No existing test shells out to git; use RESEARCH code examples |
| Term-scan test | test | file scan | No existing scan-by-term test; build from RESEARCH D-25 notes |
| Verbatim-written, drafter-authored registry JSON | registry data | file-I/O | Every existing registry file is built by a publisher with `dump()`; this one is written as returned, so the validator must not demand sorted keys |

## Metadata

**Analog search scope:** `scripts/` (v2 publisher), `tests/test_archive_assessment_*.py`, `schemas/` (naming), `tests/` grep for git usage; `registry/control_catalog.yaml` structure only.
**Files read:** 4 (CONTEXT, RESEARCH, v2 publisher, two test modules partly)
**Pattern extraction date:** 2026-10-13
