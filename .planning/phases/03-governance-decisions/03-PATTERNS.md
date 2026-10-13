# Phase 3: Governance Decisions - Pattern Map

**Mapped:** 2026-10-13
**Files analyzed:** 7 new files (plus one generated view)
**Analogs found:** 7 / 7 (all role-match or exact; none is a copy, see notes)

Files named per 03-RESEARCH.md "Recommended files" (names are discretionary). No existing file is modified.

## File Classification

| New File | Role | Data Flow | Closest Analog | Match Quality |
|----------|------|-----------|----------------|---------------|
| `scripts/build_archive_assessment_governance_decisions.py` | script (build+validate+schema+view CLI) | transform / batch, file-I/O | `scripts/validate_archive_assessment_rule_proposals.py` | exact (structure) |
| `registry/archive_assessment_governance_answers.json` | registry (hand-authored, blank template) | file-I/O | `registry/archive_assessment_not_applicable_rule_proposals.json` | role-match (hand-authored JSON) |
| `registry/archive_assessment_governance_decisions.json` | registry (built, header + records) | transform | `registry/archive_assessment_rule_proposals_drafting_record.json` + proposals file | role-match |
| `schemas/archive_assessment_governance_answers.schema.json` | schema (emitted from code) | n/a | `schemas/archive_assessment_not_applicable_rule_proposals.schema.json` | exact |
| `schemas/archive_assessment_governance_decisions.schema.json` | schema (emitted from code) | n/a | `schemas/archive_assessment_rule_proposals_drafting_record.schema.json` | exact |
| `docs/ARCHIVE_ASSESSMENT_RULE_PROPOSALS_VIEW.md` | generated doc (neutral view) | transform (render) | `docs/ARCHIVE_ASSESSMENT_RULE_DRAFTER_BRIEF.md` (tracked, docs/ path) | partial (no generator analog) |
| `tests/test_archive_assessment_governance_decisions.py` | test | mutation / term-scan / git-ancestry | `tests/test_archive_assessment_rule_proposals.py` + `tests/test_archive_assessment_rule_proposals_record.py` | exact |

## Pattern Assignments

### `scripts/build_archive_assessment_governance_decisions.py` (script, transform)

**Analog:** `scripts/validate_archive_assessment_rule_proposals.py` (194 lines)

**Header, V2 import and constants** (lines 1-50). Copy verbatim, then change the path constants:
```python
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import subprocess
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'registry'
SCHEMAS = ROOT / 'schemas'
DOCS = ROOT / 'docs'

_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V2)
AuthorityError = V2.AuthorityError
...
CONTROL_IDS = [f'EMS-CTRL-{n:03d}' for n in (9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 30, 33, 39, 42, 52, 62, 75, 79)]
HEX40 = r'^[0-9a-f]{40}$'
HEX64 = r'^[0-9a-f]{64}$'
DATE_RE = r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
```
Import `CONTROL_IDS` from `validate_archive_assessment_rule_proposals` the same way (spec_from_file_location) rather than re-listing it, or copy the literal; either is consistent with the repo (duplicated helpers are already the norm). Do NOT put "generated" anywhere in the script source (existing test `test_validator_source_has_no_generated_dir_or_scan_terms` pattern; apply the same to this script).

**git helper** (lines 51-54):
```python
def git(*args: str) -> bytes:
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    if r.returncode != 0: raise AuthorityError(f'git {args[0]} failed: {r.stderr.decode("utf-8", "replace").strip()}')
    return r.stdout
```

**Helper**: `def nonempty(v: object) -> bool: return isinstance(v, str) and bool(v.strip())` (line 68).

**Rule shape check, do not re-implement** (V2 lines 136-150; used at validator line 85):
```python
elif outcome == 'PROPOSE_RULE': V2.validate_rule(cid, p['proposed_rule'], errors)
```
Apply to `entry['decided_rule']` wherever the decided outcome is a rule. `validate_rule(cid, rule, errors)` appends strings to `errors`, never raises.

**Error accumulation, entry-level** (lines 79-82, 97):
```python
def validate_proposal(p: object, catalog: dict, errors: list) -> None:
    if not isinstance(p, dict): errors.append('proposal must be an object'); return
    cid = p.get('control_id')
    if set(p) != set(PROPOSAL_KEYS): errors.append(f'{cid}: proposal keys must be exactly {PROPOSAL_KEYS}'); return
...
    if not nonempty(r) or not 2 <= len(re.findall(r'[.!?](\s|$)', r.strip())) <= 4: errors.append(f'{cid}: rationale must be 2 to 4 sentences')
```
Copy the exact-key-set check (`set(x) != set(KEYS)`) for answers entries, records and header; it is what makes removing `decision_id` / `dual_role_statement` / `disposition` / `control_id` fail the validator (success criterion 4). The sentence-count regex is reusable for decided rationales (research assumption A1).

**Document-level validate (raises)** (lines 104-120):
```python
def validate_proposals(p: dict, catalog: dict | None = None) -> None:
    errors: list = []
    ...
    items = p.get('proposals')
    if not isinstance(items, list): errors.append('proposals must be a list')
    else:
        ids = [x.get('control_id') if isinstance(x, dict) else None for x in items]
        if len(items) != len(CONTROL_IDS) or len(set(ids)) != len(ids) or set(ids) != set(CONTROL_IDS): errors.append('proposals must cover exactly the 21 requested control ids once each')
        for x in items: validate_proposal(x, catalog, errors)
    walk_forbidden(p, 'proposals', errors)
    if V2.contains_absolute(p): errors.append('absolute path used in proposals')
    if errors: raise AuthorityError('; '.join(errors))
```
Pattern for `validate_answers(a, strict=False)` and `validate_decisions(d)`: accumulate into `errors`, one `raise AuthorityError('; '.join(errors))` at end. Include `V2.contains_absolute` check. Note that `walk_forbidden` / `FORBIDDEN_ID_RE` are proposals-specific and must NOT be copied: decision records legitimately contain `AA4-GOV` ids.

**Header equality against expected constants** (lines 61-63, 109-111): copy the `expected_header()` + loop `if p.get(k) != exp[k]` pattern for the fixed `dual_role_statement`, D-17 header statement and D-06 statement (compare by exact equality with module constants, per research pitfall 5). Fixed text constants sit at lines 37-39 as module-level string constants (`NON_AUTHORITY_STATEMENT`, `RECORD_STATEMENT`).

**Record-style validation with regex helper** (lines 122-144):
```python
def validate_record(r: dict) -> None:
    errors: list = []
    if not isinstance(r, dict): raise AuthorityError('record must be an object')
    if set(r) != set(RECORD_KEYS): raise AuthorityError(f'record keys must be exactly {RECORD_KEYS}')
    def rx(k, pat):
        if not isinstance(r[k], str) or not re.match(pat, r[k]): errors.append(f'{k} invalid')
    ...
    rx('drafting_commit', HEX40); rx('proposals_sha256', HEX64) ...
    if V2.contains_absolute(r): errors.append('absolute path used in record')
    if errors: raise AuthorityError('; '.join(errors))
```
Use for the decisions header (digests, `drafting_commit` = `dc3b41c9fbb3571a191d2da5164fb73439a0637b`, approval object with `APPROVAL_KEYS = ['approver','role','date','scope']`, line 48 and 133).

**Schema emitted from code** (lines 146-181). Copy the small-helper idiom:
```python
def schema() -> dict:
    s = lambda: {'type': 'string', 'minLength': 1}
    ...
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': '...', 'type': 'object', 'additionalProperties': False,
        'required': HEADER_KEYS + ['proposals'],
        'properties': {'status': {'const': STATUS}, ... 'proposals': {'type': 'array', 'minItems': len(CONTROL_IDS), 'maxItems': len(CONTROL_IDS), 'items': proposal}}}
```
Reuse `rule_schema()` (lines 146-148) for decided rules (it is built from `V2.RULE_FIELDS`, `V2.CONDITION_STATES`, `V2.COMBINATION`). For ids use `{'type':'string','pattern': V2.AUTHORITY_ID_RE}` (`^AA4-GOV-[0-9]{3}$`). For D-15: `'approver_roles': {'type':'array','const':[...]}` and `'dual_role_statement': {'const': DUAL_ROLE_STATEMENT}`; `additionalProperties: False` plus `required` everywhere (no bulk key possible in answers). For disposition-vs-outcome conditionals copy the `allOf`/`if`/`then` idiom at lines 162-164. Note: decision record `minItems` must be `>= 21` (supersession appends), unlike the proposals' fixed 21.

**CLI** (lines 183-193): argparse with flags, `V2.load`, `V2.dump`, validator then schema:
```python
if args.validate:
    if not PROPOSALS.exists(): raise AuthorityError('proposals file is not present')
    p = V2.load(PROPOSALS); validate_proposals(p); jsonschema.Draft202012Validator(V2.load(SCHEMA)).validate(p); print('PASS')
elif args.emit_schema: V2.dump(SCHEMA, schema()); V2.dump(RECORD_SCHEMA, record_schema())
else: parser.error('one of --validate, --validate-record or --emit-schema is required')
if __name__ == '__main__': main()
```
Extend with `--view`, `--validate-answers` (strict), `--build`, `--validate`, `--emit-schema`. Write via `V2.dump` (deterministic `indent=2, sort_keys=True` + newline, V2 lines 45-47). Caveat: V2.load uses `encoding='utf-8'` and a hand-edited answers file may fail with `JSONDecodeError`; wrap and re-raise as `AuthorityError` with line/column (research pitfall 3). Hash the answers file with CRLF normalised to LF (research pitfall 2); `V2.digest` hashes raw bytes and is only suitable for the (LF) proposals file.

**Helpers to import from V2** (do not re-implement): `V2.validate_rule`, `V2.RULE_FIELDS`, `V2.CONDITION_STATES`, `V2.COMBINATION`, `V2.DECISION_STATES` (`RULE_PUBLISHED`, `NO_RULE_WILL_BE_PUBLISHED`, `NOT_YET_DECIDED`; exclude the last for D-07), `V2.AUTHORITY_ID_RE`, `V2.load`, `V2.dump`, `V2.digest`, `V2.contains_absolute`, `V2.AuthorityError`.

**View rendering:** no analog generator exists. Use plain string joins (research Pattern 5); render `proposed_rule` with `json.dumps(value, indent=2, sort_keys=True)`, as `V2.dump` does. Write to `docs/` (tracked), never `generated/` (gitignored, and the Phase 2 source test forbids the word).

---

### `registry/archive_assessment_governance_answers.json` (hand-authored, blank template)

**Analog:** `registry/archive_assessment_not_applicable_rule_proposals.json` (hand-authored JSON, validated by script + schema, frozen once committed). Pattern only: top-level list of 21 per-control objects in ascending `CONTROL_IDS` order, every key present, values `null`/`""` until the authority types them. Per-decision key layout may mirror AA2 `generated/archive-assessment/ems-aa2/approval/archive_assessment_applicability_governance_approval.json` (`approval_disposition`, `approved_text`, `amendment_present`, `approver`, `approved_at`); the blanket `approval_instruction` is NOT reused. Must contain no scan terms and no absolute paths. Generated by the tool as blanks only (D-06).

### `registry/archive_assessment_governance_decisions.json` (built)

**Analog:** `registry/archive_assessment_rule_proposals_drafting_record.json` (header-style digests, `drafting_commit`, `brief_approval`) with record list shaped like proposals' `proposals` array. Header keys per research Pattern 3. Built by a pure `build_decisions(proposals, answers, record)`; validated by `validate_decisions`. Output via `V2.dump` for byte-determinism (a test rebuilds and compares bytes).

### `schemas/*.schema.json` (two files)

**Analog:** `schemas/archive_assessment_not_applicable_rule_proposals.schema.json` and `schemas/archive_assessment_rule_proposals_drafting_record.schema.json`. Never hand-edit; emit with `--emit-schema` and cover with the equality test `json.loads(MODULE.SCHEMA.read_text(...)) == MODULE.schema()` (test lines 130-134).

### `tests/test_archive_assessment_governance_decisions.py` (test)

**Analog:** `tests/test_archive_assessment_rule_proposals.py` (build fixture + mutation) and `tests/test_archive_assessment_rule_proposals_record.py` (git ancestry).

**Module load, fixture, mutation helpers** (proposals test lines 12-78):
```python
SCRIPT = Path(__file__).parents[1] / 'scripts' / 'validate_archive_assessment_rule_proposals.py'
SPEC = importlib.util.spec_from_file_location('aa_rule_proposals', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
...
def fx(): return copy.deepcopy(FIXTURE)
def invalid(mutator):
    value = fx(); mutator(value)
    with pytest.raises(AuthorityError): MODULE.validate_proposals(value)
def schema_rejects(mutator):
    value = fx(); mutator(value)
    with pytest.raises(jsonschema.ValidationError): jsonschema.Draft202012Validator(MODULE.schema()).validate(value)
def both_reject(mutator): invalid(mutator); schema_rejects(mutator)
```
Copy `invalid` / `ok` / `schema_rejects` / `both_reject`; the one-line `def test_x_fails_closed(): both_reject(lambda a: ...)` style for the success-criterion-4 mutations (remove `dual_role_statement`, `decision_id`, `disposition`, `control_id`; alter `approver_roles`). Fixture of filled answers must be synthetic, built in the test, and never written to `registry/`. Use `rule(*pairs)` helper (line 66).

**Term scan** (lines 12, 153-169). Copy with the list changed (drop `'Hayes'` and `'DEMO3-W1-REQ-001'`; keep `RiskMVP`, the full SHA `42aa362c76980a934fbaa470e603b48c7ef4b0b7`, `42aa362`, `2026-10-01`, `EMS_NOT_APPLICABLE_RULE_ABSENT`):
```python
TERMS = [...]
def scan(text): return [t for t in TERMS if re.search(re.escape(t), text, re.IGNORECASE)]
def test_term_scan_detects_each_term(): ...
```
Scan answers, decisions, view and script source, plus file names.

**Gated/skip pattern so a blank answers file or missing decisions file keeps the suite green** (lines 161-166):
```python
def gated(path): return pytest.mark.skipif(not path.exists(), reason='not yet written')

@pytest.mark.parametrize('path', [pytest.param(MODULE.PROPOSALS, marks=gated(MODULE.PROPOSALS), id='proposals'), ...])
def test_term_scan_real_files(path):
    assert scan(path.read_text(encoding='utf-8')) == []
    assert scan(path.name) == []
```
Use `gated(DECISIONS)` for strict/build tests against real files; the committed blank answers only go through lenient mode.

**Schema-equals-function and schema-valid tests** (lines 130-134): copy for both new schemas.

**Source hygiene tests** (lines 145-151): copy `test_validator_source_has_no_generated_dir_or_scan_terms`; adapt the second to assert the script never writes PROPOSALS / drafting RECORD.

**Git helpers and ancestry** (record test lines 26-43, 65-72, 92-96):
```python
def git(*args, text=True):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return r if not text else subprocess.CompletedProcess(r.args, r.returncode, r.stdout.decode('utf-8').strip(), r.stderr.decode('utf-8').strip())

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
def test_proposals_frozen_since_drafting_commit():
    assert git('rev-parse', f'HEAD:{PROPOSALS}').stdout == git('rev-parse', f"{rec['drafting_commit']}:{PROPOSALS}").stdout
```
Reuse for: each decision record cites `dc3b41c9fbb3571a191d2da5164fb73439a0637b`, it is an ancestor of HEAD, and proposals + drafting record are unchanged (success criterion 5). The record test imports the earlier test module via `load_module(...)` (lines 13-21) to reuse `scan`; the same trick can import `scan` rather than redefining it, but the term list differs here, so define a new `TERMS`.

Note: `test_no_decision_or_v2_authority_at_drafting_commit` (record test line 111-116) greps `AA4-GOV` only at the drafting commit; it stays valid, since new files are added later.

## Shared Patterns

### Fail-closed validation with accumulated errors
**Source:** `scripts/validate_archive_assessment_rule_proposals.py` lines 104-120 (pattern above). Apply to answers, decisions and header validation. Raise `AuthorityError`, never auto-correct (D-10).

### Deterministic JSON and path hygiene
**Source:** `scripts/publish_archive_assessment_applicability_authority_v2.py` lines 45-53 (`dump`, `load`, `contains_absolute`). All registry JSON repo-relative with forward slashes; trailing newline; `sort_keys=True`.

### Two-layer check (semantic validator + JSON schema)
**Source:** validator `main()` line 187: `validate_x(p); jsonschema.Draft202012Validator(V2.load(SCHEMA)).validate(p)`. Apply to answers (schema + lenient/strict) and decisions.

### Term scan (D-19)
**Source:** `tests/test_archive_assessment_rule_proposals.py` lines 12, 153-169 (term list lives in the test only, case-insensitive `re.escape` search, file names included).

### Git staging
No code analog. Stage by explicit path only (`git add <path>`; verify `git diff --cached --name-only`), never `-A`, `.` or `-a`; `registry/adjudication_rules.json`, `registry/policy_decisions.json` and many untracked files are unrelated.

## No Analog Found

| File / Need | Role | Data Flow | Reason |
|-------------|------|-----------|--------|
| Markdown view generator | generator | render | No existing script renders registry JSON to a tracked Markdown view; use plain string joins (and a byte-identical regeneration test). Closest tracked doc location convention: `docs/ARCHIVE_ASSESSMENT_RULE_DRAFTER_BRIEF.md`. |
| Lenient vs strict answers validation | validator | n/a | The proposals validator has a single strict mode; add a `strict` flag (research Pattern 2). |
| Supersession chain check | validator | n/a | No existing authority validates "latest unsuperseded per control"; implement from research Pattern 3 / pitfall 6. |
| Answers digest with CRLF normalisation | utility | file-I/O | `V2.digest` hashes raw bytes; need a normalising variant (research pitfall 2). |

## Metadata

**Analog search scope:** `scripts/`, `tests/`, `registry/`, `schemas/`, `docs/` (targeted at `archive_assessment_*` files named in CONTEXT.md and RESEARCH.md)
**Files read:** 5 (validator, V2 publisher excerpts, two test files, CONTEXT, RESEARCH)
**Pattern extraction date:** 2026-10-13
