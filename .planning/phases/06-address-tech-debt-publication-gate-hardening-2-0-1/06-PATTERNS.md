# Phase 6: Publication gate hardening (2.0.1) - Pattern Map

**Mapped:** 2026-10-14
**Files analyzed:** 17 (0 brand-new code files; all are in-place edits or regenerated artifacts)
**Analogs found:** 17 / 17 (every file is its own best analog, plus a sibling for each new construct)

Line numbers refer to the current working tree. Scripts are CRLF in the worktree, LF in the index; edits must match multi-line strings accordingly. Do not change line endings.

## File Classification

| Modified / regenerated file | Role | Data flow | Closest analog (for the new construct) | Match |
|---|---|---|---|---|
| `scripts/publish_archive_assessment_applicability_authority_v2.py` | publisher / validator | transform + file-I/O | itself (`validate_signoff` L329, `build_all_outputs` L364, `validate_published` L417); lazy loader copies `V2` loader in `scripts/build_archive_assessment_governance_decisions.py` L18-21 | exact |
| `scripts/build_archive_assessment_governance_decisions.py` | builder / validator | transform + CLI | itself (`main()` L365-397, `refreshable` L350, `is_date` L73) | exact |
| `scripts/validate_archive_assessment_rule_proposals.py` | validator | transform (git-gated) | itself (`git` L51, `catalog_fingerprint` L56, `expected_header` L61, `validate_proposals` L104) | exact |
| `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` | generator | transform + file-I/O | itself (`build_reply` L43, `main` L274) | exact |
| `schemas/archive_assessment_applicability_authority_v2.schema.json` | schema (generated) | n/a | emitted from `schema()` publisher L266-286 via `--emit-schema` | generated |
| `schemas/archive_assessment_demo3_w1_req_001_reply.schema.json` | schema (generated) | n/a | emitted by reply script `--emit-schema` | generated |
| `registry/archive_assessment_applicability_authority_v2.json` | authority (generated) | file-I/O | `--publish` output | generated |
| `registry/archive_assessment_applicability_authority_v2_signoff.json` | sign-off record | human input | existing 2.0.0 record shape (`valid_signoff` test L176) | exact |
| `registry/archive_assessment_applicability_authority_v2_publication_record.json` | publication record | file-I/O | `write_publication_record` L436 | exact |
| `generated/archive-assessment/ems-aa3-v2/*` (7 files) | outputs (generated) | file-I/O | `build_all_outputs` L364 | generated |
| `registry/archive_assessment_demo3_w1_req_001_reply.json`, `docs/DEMO3_W1_REQ_001_REPLY.md` | reply (generated) | file-I/O | reply script `--build` | generated |
| `tests/test_archive_assessment_applicability_authority_v2_publication.py` | test | unit + git-gated | itself (`fails` L28, `so_fails` L218, `env` L179, `git_ready` L369) | exact |
| `tests/test_archive_assessment_applicability_authority_v2.py` | test | unit | itself | exact |
| `tests/test_archive_assessment_governance_decisions.py` | test | unit + CLI | itself (`TMPDIR` L30, `test_wr07_*` L410-427, `test_wr09_emit_template*` L445) | exact |
| `tests/test_archive_assessment_rule_proposals.py`, `..._record.py` | test | unit + git-gated | itself (`git_ready` record test L34) | exact |
| `tests/test_archive_assessment_demo3_w1_req_001_reply.py` | test | unit + git-gated | itself | exact |
| `CLAUDE.md`, `.planning/PROJECT.md` | docs | n/a | one-line wording edit | n/a |

`.gitattributes` needs no change (all v2 and reply files are already in its narrow LF list, per RESEARCH).

## Pattern Assignments

### Publisher: `publish_archive_assessment_applicability_authority_v2.py` (single-quote, compact one-line helpers)

**Header/imports to extend** (L1-10): `from __future__ import annotations`, stdlib block (`argparse, hashlib, json, re`, `from pathlib import Path`), blank, third-party (`jsonschema`, `yaml`). Add `import copy`, `import importlib.util`, `from datetime import date` in the stdlib block. No `subprocess` or `import git` is allowed (`test_module_does_not_call_git`, publication test L78-80).

**Constants block to extend** (L304-320). Add `SIGNOFF_ROLE`, `VERSION`, `SUPERSEDED_V2_0_0`; delete `PUBLISHED_ON` (L304); convert `NEGATIVE_MUTATIONS` (L320):
```python
APPROVER = 'Oscar Mack'
APPROVER_ROLES = ['EMS_GOVERNANCE_AUTHORITY', 'HAYES_VERIFY_DEVELOPER']
DUAL_ROLE_STATEMENT = 'Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it.'
AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0'   # becomes ...-2.0.1, derived from VERSION
NEGATIVE_MUTATIONS = ['swapped_authority', 'rule_field_change', ...]   # 17 bare id strings -> records (id, description, target, apply, schema_must_reject)
```
Replace literal `'2.0.0'` / hardcoded id at L124-125, L186, L276, L343-344 with `VERSION` / `AUTHORITY_ID`.

**Sign-off validator to harden** (L329-347, CR-01 + WR-04). Current weak spots to copy-and-tighten:
```python
if appr.get('role') not in APPROVER_ROLES: errors.append('sign-off role is not an approved EMS governance role')   # -> != SIGNOFF_ROLE
if not isinstance(dr, str) or not dr.strip() or DUAL_ROLE_STATEMENT not in dr: ...                                 # -> dr != DUAL_ROLE_STATEMENT
if 'version' in record and record['version'] != '2.0.0': ...                                                        # -> != VERSION
if errors: raise AuthorityError('; '.join(errors))                                                                  # keep: accumulate then raise
```
Add exact key-set checks (`set(record) == {7 keys}`, `set(appr) == {'approver','role','date','scope'}`) and `date.fromisoformat` plus `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`; copy the 5-line `is_date` from the builder L73-77 verbatim (publisher cannot import the builder at module level). Keep signature `validate_signoff(record, authority_lf_digest)` (reply script calls it, R L64).

**Lazy loader for CR-02** (new). Pattern source is the loader already used at builder L18-21; make it cached and convert exceptions (Pitfall 5, distinct `AuthorityError` classes):
```python
_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V2)
```
Call the new `validate_governance_decisions()` first in `published_authority_checked()` (L399-402) and first in `validate_published()` (L417). Do not put it inside `validate_publication` (L227): existing tests call that with a monkeypatched `load` and a synthetic AA4-GOV-022 (`test_superseded_record_cited_fails`).

**Mutation harness** (new, D-17..D-20). Execution pattern is the existing `fails()` helper in the publication test:
```python
def mutated(mutator):
    value = copy.deepcopy(build())
    mutator(value)
    return value

def fails(mutator, schema_too=False):
    value = mutated(mutator)
    with pytest.raises(AuthorityError):
        validate_publication(value)
    if schema_too:
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(MODULE.schema()).validate(value)
```
Production version: for each record apply to `copy.deepcopy`, try `validate_publication` and `jsonschema.Draft202012Validator(schema()).validate` (authority target), `validate_signoff` (sign-off target, no schema), builder `validate_decisions` + decisions schema (decisions target); collect `rejected_by`; raise `AuthorityError` if empty or if `schema_must_reject` and schema did not reject. Mutators for the existing 17 are copied from `tests/...publication.py` L82-170 (e.g. `lambda a: row(a, 'EMS-CTRL-030')['not_applicable_rule']['conditions'][0].__setitem__('field', 'tier')`).

**Output build to change** (`build_all_outputs` L364-397):
- signature becomes `build_all_outputs(authority, signoff, script_sha256=None)` (signoff required, D-10); `published_on = signoff['approval']['date']` replaces every `PUBLISHED_ON` (L361, 371, 377, 378, 380, 385, 387, 395).
- L377 `'result': 'PASS'`, `'semantic_conflict_count': 0` and L385 `'semantic_conflicts': 0, 'negative_invariants': 'PASS'` become computed from the harness and a `semantic_conflicts(rows)` function (RESEARCH "Semantic checks computed" sketch).
- L378 `[{'mutation': m, 'result': 'REJECTED_FAIL_CLOSED'} for m in NEGATIVE_MUTATIONS]` becomes `{'mutation': id, 'id': id, 'description': ..., 'rejected_by': [...], 'result': 'REJECTED_FAIL_CLOSED'}` (keep `mutation` key additively).
- L392 `arts = [{'relative_path': rel(SCRIPT), 'sha256': lf_digest(SCRIPT)}, ...]` loses the script entry; a top-level `publisher_script` manifest field carries it (D-09, assumption A2).
- Output ordering test requires `[N_MATRIX, N_SEMANTIC, N_NEGATIVE, N_TRACE, N_CERT, N_REPORT, N_MANIFEST]` (manifest last). Keep.

**Authority build / lineage** (`build_authority` L133-138, `build_published_authority` L163, `validate_publication` L259-263). Current v1 entry sits in `supersedes`:
```python
'supersedes': {'authority_id': v1['authority_id'], 'version': '1.0.0', 'commit': '62a8955', 'relative_path': 'registry/archive_assessment_applicability_authority.json', 'sha256': lf_digest(V1_AUTHORITY)},
```
Move this verbatim to `v1_baseline`; `supersedes` takes the `SUPERSEDED_V2_0_0` constants (authority id, version `2.0.0`, 40-char commit `54a7fd09114704a97a7a48fce5f89aebeb48c90a`, authority sha, governance-decisions sha). Change L136, L199-200, L259-261 and `schema()` together (Pitfall 7). `validate_publication` must also require live decisions LF sha == the constant (D-12, non-circular, Pitfall 6).

**Schema fragments** (`schema()` L266-286, emit-only, never hand-edit). Current weak spots:
```python
rule = {...,'conditions':{'type':'array','minItems':1,'maxItems':len(RULE_FIELDS),'items':cond}}}      # L268: add 'allOf': dup_guard (WR-03)
'source_lineage':{'type':'object','properties':{'governance_decisions':{...}}}                          # L279: add required + additionalProperties false, const/sha patterns (WR-02)
```
`dup_guard` and the `sup`/`sha` fragments are in RESEARCH "Schema fragments" (verified on jsonschema 4.26.0).

**Publish / validate flow** (L404-434):
```python
def publish(dry_run: bool) -> None:
    a = published_authority_checked()
    ...
    if dry_run:
        if SIGNOFF.exists(): validate_signoff(load(SIGNOFF), ash)   # L408: remove (Pitfall 3, stale 2.0.0 sign-off)
        print(dry_run_summary(a), end=''); return
```
`dry_run_summary` (L352-362) line `f'Published on: {PUBLISHED_ON}'` must go (no date before sign-off). In `validate_published`, the live manifest loop (L431-433) stays strict; add IN-07 check (`PUBLICATION_RECORD` `authority_sha256`/`manifest_sha256` vs committed files, only when `record['authority_id'] == a['authority_id']`). Optional Pitfall 9: reject `..`/absolute `relative_path` in the manifest loop.

**Error handling**: `class AuthorityError(ValueError): pass` (L45); validators accumulate `errors` then `raise AuthorityError('; '.join(errors))`; CLI `main()` L443-452 prints `PASS`/JSON, failure is an uncaught exception. Keep CLI flag set; do not add flags except what D-11 needs (that is the builder, not here).

---

### Builder: `build_archive_assessment_governance_decisions.py`

**WR-10 constants** (L18-21 loader, L31-33, L56). Replace local copies after the `V2` load:
```python
_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V2)
AuthorityError = V2.AuthorityError
...
APPROVER = V2.APPROVER                    # was 'Oscar Mack' (L31)
APPROVER_ROLES = list(V2.APPROVER_ROLES)  # was literal list (L32)
DUAL_ROLE_STATEMENT = V2.DUAL_ROLE_STATEMENT  # was literal (L33)
CONTROL_IDS = list(V2.REQUEST_CONTROL_IDS)    # was literal comprehension (L56)
```

**WR-05 / D-11 `--build` guard** (`main()` L377-386; guard only the two rewrite branches, leave identical-bytes no-op printing PASS):
```python
elif args.build:
    doc = build_from_files(); validate_decisions(doc)
    if not DECISIONS.exists(): V2.dump(DECISIONS, doc)
    else:
        raw = DECISIONS.read_bytes()
        if V2.lf_bytes(raw) != decisions_text(doc).encode('utf-8'):
            if not refreshable(load_checked(DECISIONS), doc): raise AuthorityError('decisions file already exists with different content and is not overwritten')
            V2.dump(DECISIONS, doc)           # <- add published-digest refusal before this write
        elif raw != V2.lf_bytes(raw): V2.dump(DECISIONS, doc)
    print('PASS')
```
Add `parser.add_argument('--supersede-published', action='store_true')` beside L369; refusal compares `V2.load(V2.AUTHORITY)['source_lineage']['governance_decisions']['sha256']` with `V2.lf_digest(DECISIONS)`; with the flag, print the republish/re-sign-off notice and proceed. Style: single quotes, one-line `parser.add_argument(...); parser.add_argument(...)` chains.

**Do not run** `--emit-schema` casually: L376 rewrites both answers and decisions schemas; `schemas/archive_assessment_governance_answers.schema.json` is in the D-22 do-not-touch list. Do not alter `rule_schema()`.

---

### Validator: `validate_archive_assessment_rule_proposals.py` (Phase 2 WR-01 / D-03)

**Live couplings to replace** (L56-66, L93, L106-111):
```python
def catalog_fingerprint() -> dict:
    blob = git('hash-object', CATALOG_REL).decode('ascii').strip()
    data = git('cat-file', 'blob', blob)
    return {'relative_path': CATALOG_REL, 'git_blob_id': blob, 'sha256': hashlib.sha256(data).hexdigest()}

def expected_header() -> dict:
    src = catalog_fingerprint(); src['entries_have_description'] = False; src['note'] = CATALOG_NOTE
    return {'status': STATUS, 'non_authority_statement': NON_AUTHORITY_STATEMENT, 'drafting_frame': V2.semantics(), 'catalog_source': src}
```
Keep `expected_header()` API (fixture `build_fixture` at rule_proposals test L23-31 and `test_brief_header_equals_expected_header` L220 use it). Build the catalog source from the drafting record (`RECORD`), blob id via `hashlib.sha1(b'blob %d\0' % len(b) + b)` over LF bytes, no `git` subprocess in the default path. Keep the existing `git()` helper (L51-54: `subprocess.run(['git', *args], cwd=ROOT, capture_output=True)` raising `AuthorityError`) for the drifted-catalog branch only, reading `dc3b41c:registry/control_catalog.yaml`, sha-checked against `record['catalog_sha256']`. On shallow clone print a one-line stderr notice and skip only the `catalog_inputs` equality sub-check (L93). `validate_proposals(p, catalog=None)` default (L106) switches from `live_catalog()` to `frozen_catalog()`.

---

### Reply script: `build_archive_assessment_demo3_w1_req_001_reply.py` (IN-01..IN-06, D-14..D-16)

**Style**: single quotes, two blank lines between top-level functions (unlike the publisher's compact style).

- IN-01: drop `manifest` param from `build_reply` (L43) and callers L227, L280.
- IN-03 (L60): `next(r for r in ... if ...)` becomes `next((...), None)` then `raise V2.AuthorityError('no RULE_PUBLISHED row for the example')`.
- IN-05 (L24, L72): replace `RECORD_COMMIT_ABBREV = '0ce89f2'` by a 40-hex value resolved at build via `git log -n1 --format=%H -- registry/archive_assessment_applicability_authority_v2_publication_record.json` (using the script's own `git()` helper at L241-242, `text=True`). NOT `--diff-filter=A` (Pitfall 2). `validate_reply()` only checks the stored value's format so `--validate` needs no git. Schema pattern `^[0-9a-f]{40}$`.
- IN-06 (L274-285): replace four `store_true` + trailing `parser.error` with `parser.add_mutually_exclusive_group(required=True)`.
- D-15: `disclosure` object (L92) and its Markdown (L153-156) become `history_note` built from `authority['source_lineage']['supersedes']`; drop `review_path`, `verification_path`, `wr_01`, `v2_0_1_possible`, `v2_0_1_date` and the module constants `REVIEW_REL`/`VERIFICATION_REL` (L25-26); update `REPLY_KEYS` (L30).
- Hayes-side list (L85-89) already derives the SHA from `record['publication_commit']`; `send_condition` (L93) already uses it and `REMOTE_BRANCH`. Keep.
- `REPLY_DATE` (L20) is typed; Open Question 2 (derive from sign-off approval date).
- FORBIDDEN_WORDS (L33) apply to the reply text; history-note wording must avoid them.

---

### Tests (module-level patterns to copy)

**Mutation parametrization and failing-first helper** (publication test L21-34, shown above). New tests: `@pytest.mark.parametrize('m', MODULE.NEGATIVE_MUTATIONS, ids=lambda m: m.id)` asserting observed `rejected_by` equals the entry in the committed `..._negative_invariant_validation.json`.

**Sign-off cases** (publication test L218-239): extend `so_fails` list:
```python
def so_fails(mutator):
    r = valid_signoff('d' * 64)
    mutator(r)
    with pytest.raises(AuthorityError):
        MODULE.validate_signoff(r, 'd' * 64)
...
so_fails(lambda r: r['approval'].__setitem__('role', 'INTERN'))   # add 'HAYES_VERIFY_DEVELOPER', 'not-a-date', appended dual-role text, extra keys
```
`valid_signoff` (L176-177) hard-codes `'version': '2.0.0'` and `'date'`; change to `MODULE.VERSION`. `build_all_outputs(a)` calls at L195, 206, 212 must pass a signoff. `assert MODULE.PUBLISHED_ON in first[N_CERT]` (L201) becomes the sign-off date.

**Temp dir / env fixture** (publication test L179-187; decisions test L30 `TMPDIR = tempfile.TemporaryDirectory()`): use module-level `TemporaryDirectory`, never `tmp_path` (not writable on this machine). The `env` fixture monkeypatches `ROOT, AUTHORITY, SCHEMA, SIGNOFF, PUBLICATION_RECORD, OUT, SCRIPT`; extend with `GOVERNANCE_DECISIONS` for CR-02 and IN-07 four-state tests.

**Git-gated tests with shallow-clone skip** (publication test L365-394; record test L34-43). Copy exactly; evaluate `git_ready()` at call time inside the test:
```python
def git_ready():
    try: r = git('rev-parse', '--is-shallow-repository')
    except OSError: return 'git is unavailable'
    if r.returncode != 0: return 'not a git repository'
    if r.stdout.decode().strip() == 'true': return 'shallow repository, history is incomplete'
    return None
...
    reason = git_ready()
    if reason: pytest.skip(reason)
```
Use for: D-13 (80 rows equal `git show 54a7fd0:...`), D-12 constants recomputed from `54a7fd0`/`0ce89f2`, manifest `publisher_script` digest equals `git show <publication_commit>:scripts/publish_...py`, reply record-commit test (use `git log -n1 --format=%H --`).

**File-set test** (L379-388) already expects authority + sign-off + all `OUT` files; schema stays in the publisher-code commit, not the publication commit. Keep.

**CLI tests (WR-07/WR-08)** (decisions test L421-427, L445-449). Current:
```python
result = subprocess.run(['python', str(SCRIPT), '--emit-template'], cwd=ROOT, capture_output=True, text=True)
assert result.returncode != 0
```
Change to `[sys.executable, ...]` and `assert 'already exists' in result.stderr`. `test_wr07_build_cli_appends_superseding_record` only calls `refreshable`; rewrite to `monkeypatch.setattr(MODULE, 'DECISIONS', ...)`, `ANSWERS`, `V2.AUTHORITY`, `sys.argv`, then `MODULE.main()` (reuse `filled()` L41, `built()` L60, `extra_entry`).

**WR-09**: `inspect.getsource(MODULE.build_authority) + inspect.getsource(MODULE.build_published_authority)` and assert `'generated' not in src and 'OUT' not in src`.

---

### Docs: `CLAUDE.md` Constraints "Vocabulary" line, `.planning/PROJECT.md` Constraints (L92) and Validated item (L33, Open Question 5)
Edit PROJECT.md first, then CLAUDE.md (CLAUDE.md is generated from it). Single-line edits only. Verify with `git grep -n "eight declared" -- CLAUDE.md .planning/PROJECT.md` returning nothing.

## Shared Patterns

### Fail-closed validators
**Source:** publisher `validate_signoff` L329-347, `validate_publication` L227-264
Accumulate messages in `errors`, `raise AuthorityError('; '.join(errors))`. Never return a bool. Apply to every new validator (sign-off, decisions gate, supersedes binding, IN-07).

### Build / validate pairing
**Source:** `build_published_authority` L151 + `validate_publication` L227; `published_authority_checked` L399-402
```python
def published_authority_checked() -> dict:
    a = build_published_authority(); validate_publication(a)
    jsonschema.Draft202012Validator(schema()).validate(a)
    return a
```
Tests mutate a built object and assert validation fails. The decisions gate goes in front of this.

### Deterministic output and LF digests
**Source:** publisher L47-53, L322-327
```python
def lf_bytes(b: bytes) -> bytes: return b.replace(b'\r\n', b'\n')
def lf_digest(p: Path) -> str: return hashlib.sha256(lf_bytes(p.read_bytes())).hexdigest()
def jtext(value: object) -> str: return json.dumps(value, indent=2, sort_keys=True) + '\n'
def sha_text(text: str) -> str: return hashlib.sha256(text.encode('utf-8')).hexdigest()
def rel(p: Path) -> str: return p.relative_to(ROOT).as_posix()
def write_text(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(text)
```
Use for every new digest, no new hash helper, no `now()`, repo-relative forward-slash paths, `contains_absolute` guard on registry JSON.

### Cross-module loading and the two-`AuthorityError` trap
**Source:** builder L18-21, validator L17-20, reply L13-15 (all use `spec_from_file_location('aa_applicability_publisher_v2', ...)`)
Each load makes a distinct module/exception class. Convert `ValueError` to the caller's own `AuthorityError` at the boundary; pass paths/docs explicitly because monkeypatching the publisher does not affect the builder's own constants.

### Commit hygiene
**Source:** D-21/D-22 and RESEARCH wave plan
Stage by explicit path only (never `-A`, `.`, `-a`); `git add -f` for files under gitignored `generated/archive-assessment/ems-aa3-v2/`; check `git diff --cached --name-only` before each commit; publication commit holds exactly authority + sign-off + 7 outputs; commit trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

### Test command on this machine
`python -m pytest tests/test_archive_assessment_*.py -q -p no:cacheprovider --basetemp="$TEMP/pt-a6"` (basetemp outside the repo).

## No Analog Found

| Item | Role | Data flow | Reason / fallback |
|---|---|---|---|
| Manifest `publisher_script` top-level field (D-09) | manifest schema | file-I/O | No current manifest field separates the script digest; script sits in `artifacts[0]`. Use RESEARCH Pattern 4 (assumption A2: alternative is keep in `artifacts` and skip in the live-file loop). |
| Sign-off file schema | schema | n/a | None exists; sign-off mutations are caught by the Python validator only (`rejected_by: ['PYTHON_VALIDATOR']`). Do not add one this phase. |
| `maxContains` duplicate-field guard in schema | schema | n/a | No existing `contains`/`maxContains` in the repo schemas; use the construct verified in RESEARCH (jsonschema 4.26.0). |
| Semantic-conflict computation over all 80 rows | transform | transform | Only an inline all() at publisher L377; use RESEARCH sketch built on `resolve_applicability` (L288). |

## Planning cautions (from RESEARCH, binding on plans)

- Four real-file tests (`test_real_published_files_validate`, committed-schema test unless schema ships with the code commit, reply real-file tests, reply digest-vs-manifest test) and both `--validate` CLIs are expected red from the publisher-code commit until the publication commit. Document it; do not add version-mismatch skips.
- Dry-run must not validate the stale 2.0.0 sign-off (Pitfall 3); IN-07 skips a record naming a different authority id (assumption A4).
- Derive the 2.0.0 constants from `git show 54a7fd0:` / `0ce89f2:` by command; never type them (known values in RESEARCH Pitfall 6 for cross-checking).
- Sign-off date and scope text come from Oscar Mack at the blocking checkpoint, never inferred.

## Metadata

**Analog search scope:** `scripts/` (4 target scripts), `tests/` (6 archive-assessment modules), `schemas/`, RESEARCH-verified registry shapes
**Files scanned:** 12 read directly (selective ranges), remainder taken from 06-RESEARCH.md verified claims
**Pattern extraction date:** 2026-10-14
