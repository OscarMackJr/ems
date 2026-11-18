# Phase 16: Test Robustness and Review Closure - Pattern Map

**Mapped:** 2026-11-18
**Files analyzed:** 13 (edits to existing files, plus 1 new ledger)
**Analogs found:** 13 / 13 (the ledger has a role-match analog only)

Line numbers are from HEAD 9a10810 and from the files as read on 2026-11-18. Excerpts in 16-RESEARCH.md (sketches for overlay, mode selection, atomic write) are the primary code to copy. This map adds the in-repo style analogs for them.

## File Classification

| File | Role | Data Flow | Closest Analog | Match Quality |
|------|------|-----------|----------------|---------------|
| `tests/test_archive_assessment_lineage_validation.py` (D-10 test, lines 357-378) | test | request-response (subprocess + clone) | same file, `test_d10_...` plus the `make_clone` helpers in the notice 2.0.3 test | exact (self-edit) |
| `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` (deep-root test 714-736; hint tests 346 and 744; `run()` 170-182; rmtree 643/719/736) | test | request-response | same file | exact (self-edit) |
| `tests/test_archive_assessment_demo3_w1_req_001_reply.py` (line 386) | test | request-response | same file, adjacent parametrised cases | exact |
| `tests/test_archive_assessment_applicability_authority_v2_publication.py` (lines 548-550) | test | transform | same file | exact |
| `tests/test_archive_assessment_skip_guard.py` (new HINT assertion) | test | transform | existing `test_history_problem_unrecognised_shallow_output_is_problem` (lines ~175-189) | exact |
| `tests/aa_history.py` (BASE-04, verify only) | utility (test helper) | request-response | itself, already fixed in `8dd3778` | exact |
| `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` | utility (standalone builder) | batch/transform + file-I/O | itself (behaviour-only edits) | exact (self-edit) |
| `.planning/phases/16-.../16-REVIEW-CLOSURE.md` (new) | doc (ledger) | n/a | `.planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md` and `.planning/phases/14-notice-to-hayes-2-0-3/14-REVIEW-FIX.md` | role-match |
| `.planning/REQUIREMENTS.md` | doc | n/a | itself (GATE-13 lines 23-30, GATE-15 lines 37-40, traceability, V2-01/V2-02 at 73-74 and 111-112) | exact |
| `.planning/ROADMAP.md` | doc | n/a | itself (Phase 16/17/19 success criteria) | exact |
| `.planning/phases/11-*/11-0{1..6}-SUMMARY.md`, `12-*/12-0{1..8}-SUMMARY.md`, `13-*/13-0{1..4}-SUMMARY.md` | doc (frontmatter) | n/a | `14-01-SUMMARY.md` line 15, `14-02-SUMMARY.md` line 12 (`requirements-completed:`) | exact |

Not modified, byte-unchanged gates: the publisher, the reply builder, the 2.0.2 notice builder, and the three 2.0.3 notice outputs.

## Pattern Assignments

### `tests/test_archive_assessment_lineage_validation.py` (test, request-response) - BASE-01, BASE-03

**Analog:** the existing test at lines 357-378 (same file).

**Imports and helpers to reuse** (lines 1-30):
```python
import copy, hashlib, importlib.util, subprocess, sys
from pathlib import Path
import pytest
from aa_history import require_history
...
REAL_ROOT = MODULE.ROOT
def git(*args, cwd=REAL_ROOT):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True)
PINNED_COMMITS = (MODULE.V1_BASELINE_COMMIT, MODULE.SUPERSEDED_V2_0_2['commit'])
```
Add `import json` and `import os`. The file uses single quotes and 4-space indent.

**Guard and clone pattern to keep** (lines 357-363):
```python
require_history(REAL_ROOT, commits=PINNED_COMMITS)   # asserts, never skips
clone = tmp_path / 'c'
cloned = subprocess.run(['git', '-c', 'core.longpaths=true', 'clone', '--shared', '-q', str(REAL_ROOT), str(clone)], capture_output=True)
if cloned.returncode != 0:
    pytest.fail(f'git clone --shared of {REAL_ROOT} failed: {cloned.stderr.decode(errors="replace")}', pytrace=False)
assert git('config', 'core.longpaths', 'true', cwd=clone).returncode == 0
```

**`outcome()` to replace** (lines 365-369, locale codec, stdout+stderr merged):
```python
def outcome():
    r = subprocess.run([sys.executable, 'scripts/publish_archive_assessment_applicability_authority_v2.py', '--validate'],
                       cwd=clone, capture_output=True, text=True)
    lines = [line for line in (r.stdout + r.stderr).splitlines() if line.strip()]
    return r.returncode, (lines[-1] if lines else '')
```
Target (D-07, D-08): add `encoding='utf-8', errors='replace'`, `env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}`, and `args = validate_mode(clone)`. Read `r.stdout` only. Accept `PASS` or `json.loads(line)['status'] == 'PASS'`, and fall back to the raw line if the JSON does not parse. Put `r.stderr` only in the assert message.

**Overlay and mode selection:** copy the sketch from 16-RESEARCH.md ("D-10 overlay and mode selection"). Key points:
- Rels are `[*MODULE.publication_paths(), MODULE.rel(MODULE.SCRIPT)]`, which is 10 paths plus the publisher.
- Copy bytes with `.replace(b'\r\n', b'\n')`.
- Run `git -c core.autocrlf=false -c user.name=t -c user.email=t@t -c commit.gpgsign=false --literal-pathspecs add -- ...`.
- Commit only when `git diff --cached --quiet` returns non-zero.
- Mode: `--validate --at-pin` iff the clone's `MODULE.PUBLICATION_RECORD` has `authority_id` and `version` equal to the working-tree authority's `source_lineage.supersedes`. This mirrors the publisher's own check at publisher line 841.

**Assertion tail to keep** (lines 371-378): `before == (0, 'PASS')`, mutate `clone / MODULE.CATALOG_REL` by overwrite and then `unlink`, and assert `after == before`. Add a short comment on the D-08a red window (the test goes red from Phase 17's first publisher edit until the 2.0.4 publication; do not weaken it).

---

### `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` (test) - BASE-02, GATE-14 IN-05, GATE-15 IN-02/IN-03

**Analog:** same file. Deep-root test, current form (lines 714-736):
```python
long_rel = f'{MODULE.rel(MODULE.OUT)}/{MODULE.N_NEGATIVE}'
base = TMP / 'deep'
...
while len(str(clone)) + 1 + len(long_rel) <= 270:
    clone = clone / ('d' * 20)
clone = clone / 'c'
deep = len(str(clone)) < 240
if not deep:
    clone = base / 'c'
...
assert git('config', 'core.longpaths', 'false', cwd=clone).returncode == 0
monkeypatch.setattr(MODULE, 'ROOT', clone)
assert MODULE.git_show(PUB, long_rel) == git('show', f'{PUB}:{long_rel}', '--', cwd=clone).stdout
```
Change: on `sys.platform == 'win32'`, assert the preconditions (`len(clone) + 1 + len(f'{PUB}:{long_rel}') > 260`, `len(clone) <= 200`) and run `git -c core.longpaths=false show <sha>:<rel>` without `--`. It must exit non-zero with `b'Filename too long' in stderr`, using `assert` or `pytest.fail`, never `pytest.skip`. Remove the silent shallow fallback (the `deep` branch). On other platforms assert equality with the `--` form only.

**Mocked `--` guard to keep** (lines 702-711, `test_git_show_passes_double_dash`): patch `MODULE.subprocess.run` with a fake that records argv, then `assert seen[0][-1] == '--'`.

**Hint-test fold (15 IN-02):** the parametrised pattern at lines 739-749 is the one to fold into `test_git_show_error_names_full_sha_and_fetch_hint` (~line 346):
```python
@pytest.mark.parametrize('stderr, long_path_hint', [...])
...
monkeypatch.setattr(MODULE.subprocess, 'run', lambda argv, **kwargs: subprocess.CompletedProcess(argv, 128, stdout=b'', stderr=stderr))
with pytest.raises(GitHistoryError, match='git show failed') as e:
    MODULE.git_show('e' * 40, 'registry/x.json')
assert 'fetch full history (git fetch --unshallow)' in str(e.value)
assert ('core.longpaths' in str(e.value)) is long_path_hint
```
Keep the positive `Filename too long` case. Delete the standalone line-744 test after folding.

**New git-missing hint test (15 IN-03):** same `monkeypatch.setattr(MODULE.subprocess, 'run', ...)` style with a function that raises `FileNotFoundError('git')`. Then `pytest.raises(GitHistoryError, match='git unavailable')`, `'install git' in msg`, `'fetch' not in msg`.

**IN-05 test nits:** replace `rmtree(..., onerror=_rm_readonly)` with `onexc=_rm_readonly` (lines 643, 719, 736; the 3-arg callback at 634 is compatible). In `run_in_clone` (655-658) stop joining stdout+stderr; take the last non-empty line of stdout and assert `returncode`. Note in the ledger that the always-true `is_relative_to(ROOT)` half at line 183 is covered by tests at 674/683 and assertions at 187-192.

**New tests (add in the file's style: single quotes, `pytest.raises(..., match=...)`):** wrong-commit lineage entry raises `AuthorityError`; malformed pinned blob raises `AuthorityError`; `--build` with a forced validation failure leaves no partial files; mutating the built notice rule does not alter the inputs (deepcopy).

---

### `tests/test_archive_assessment_demo3_w1_req_001_reply.py` (test) - 12 IN-07 test part

**Analog:** same file, line 386:
```python
({'cat_exc': OSError('git gone')}, 'in the repository history')
```
Change only the match text to `'cannot check whether the frozen commit'`. The frozen builder message is at `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:354`; do not edit it.

### `tests/test_archive_assessment_applicability_authority_v2_publication.py` (test) - 12 IN-07 test part

Lines 548-550, `test_at_pin_binding_reads_supersedes_from_authority`: remove the `inspect.getsource` lines (`src = ...` and the `SUPERSEDED_V2_0_` grep assert). Keep the behavioural `other`-authority assertion with `pytest.raises(... superseded {sup['version']} publication commit)`. Check whether `inspect` is still used elsewhere before removing the import (ruff F401).

### `tests/test_archive_assessment_skip_guard.py` and `tests/aa_history.py` (BASE-04)

**Analog:** `test_history_problem_unrecognised_shallow_output_is_problem` (~lines 175-189), which asserts `repr(out) in msg`, `'cannot tell whether'` and not `'is a shallow repository'`. `aa_history.py` lines 10-11 (`HINT`) and 26-31 are already fixed in `8dd3778`. Add one assertion only:
```python
assert 'only skips tests guarded by require_history' in aa_history.HINT and 'still fail' in aa_history.HINT
```
Do not edit `aa_history.py`, unless a re-read shows the wording differs from the research claim.

---

### `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` (standalone builder, behaviour-only)

**Style:** single quotes, compact one-line helpers, `AuthorityError` / `GitHistoryError` domain exceptions. Working copy is CRLF and the index is LF.

**14 IN-01, lineage commit cross-check** (current lines 219-228). Analog: the existing `LINEAGE_NORMALISATION[key]` check at 221-223:
```python
norm = e.get('normalisation') if isinstance(e, dict) else None
if norm != LINEAGE_NORMALISATION[key]:
    raise AuthorityError(f'source_lineage {key}: normalisation {norm!r} differs from {LINEAGE_NORMALISATION[key]}')
at = e.get('commit', NOTICE_PUBLICATION_COMMIT)
```
Copy that shape for the new `EXPECTED_LINEAGE_COMMIT` dict, with `catalog_reference` and `v1_baseline` mapped to `CATALOG_COMMIT` and `supersedes` to `PREVIOUS_2_0_2_COMMIT`. After computing `at`, add `if at != EXPECTED_LINEAGE_COMMIT.get(key, NOTICE_PUBLICATION_COMMIT): raise AuthorityError(f'source_lineage {key}: commit {at} differs from the expected commit')`. Delete `pinned_raw_digest` (lines ~165-167).

**14 IN-02, domain-wrapping and class matching.** Analog: the existing try/except at 296-301 and 311-326:
```python
except AuthorityError: raise
except _WRAPPED as e:
    cls = GitHistoryError if type(e).__name__ == 'GitHistoryError' else AuthorityError
    raise cls(f'pinned mutation run failed: {type(e).__name__}: {e}') from e
```
Replace the name match with an `isinstance` check against the pinned `pub.GitHistoryError` where `pub` is bound. At line 319, re-raise `GitHistoryError(f'pinned baseline rejected the unmutated inputs: {type(e).__name__}: {e}')` so the "pinned baseline" context is kept. Do not change `_WRAPPED` (line 290). Wrap `load_inputs` and `build_notice` bodies with `except (ValueError, KeyError, TypeError) as e: raise AuthorityError(...) from e`. Do not wrap `jsonschema.ValidationError` in `validate_notice_object`.

**14 IN-03, atomic `--build`.** Current `main` (lines 596-603):
```python
if args.emit_schema: dump(NOTICE_SCHEMA, schema())
elif args.build:
    inputs = load_inputs()
    notice = build_notice(*inputs)
    validate_notice_object(notice, inputs)
    json_text, md_text = jtext(notice), render_markdown(notice)
    write_text(NOTICE_JSON, json_text); write_text(NOTICE_MD, md_text)
    validate_notice()
```
Helper analog for the write style (lines 89-91):
```python
def write_text(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(text)
```
Add a `write_atomic` sibling (temp file `p.with_name(p.name + '.tmp')`, then `os.replace`). In `--build`, compute `schema_text = jtext(schema())`, run `jsonschema.Draft202012Validator.check_schema(schema())`, then stage the three temps, `os.replace` all three, remove temps in a `finally`, and run `validate_notice()` as the post-check. Keep the `dump` and `write_text` helpers for `--emit-schema`. Add `import os` and `import copy` if absent.

**14 IN-04:** line ~423 `'rule': r['not_applicable_rule']` becomes `copy.deepcopy(r['not_applicable_rule'])`.

**15 IN-03, git-missing hint** (line 102):
```python
except OSError as e: raise GitHistoryError(f'{relative_path}@{commit}: git unavailable: {e}; fetch full history (git fetch --unshallow)') from e
```
Change the tail to `; install git and ensure it is on PATH`. Leave the `Filename too long` hint at line 106 and `contains_absolute` (92-96) unchanged (15 IN-01 is DEFERRED-19).

**Byte-identity gate (D-02), run by the plan.** Take a `git show HEAD:<path>` snapshot of the three outputs before any `--build`. Then run `--build` and `--validate` (must print `PASS`). Then run `git diff --exit-code -- registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md schemas/archive_assessment_demo3_w1_req_001_notice_2_0_3.schema.json`. Then compare each file's `read_bytes()` with the snapshot.

---

### `.planning/phases/16-test-robustness-and-review-closure/16-REVIEW-CLOSURE.md` (new ledger)

**Analogs:** `12-BASELINE-RED.md` (title line, a record line, a markdown table with a header row, and a rule sentence) and `14-REVIEW-FIX.md` (YAML frontmatter with counts, then per-item sections with `Files modified`, `Commit` and `Status`).

Frontmatter pattern from `14-REVIEW-FIX.md` lines 1-10: `phase`, `review_path`, `status`, plus counts. Table pattern from `12-BASELINE-RED.md` lines 24-31:
```
| # | Validator | Result |
|---|-----------|--------|
```
Use columns `Item | Disposition | Reason | Evidence`. Allowed dispositions are `FIXED`, `CLOSED`, `DEFERRED-17`, `DEFERRED-19` and `SUPERSEDED-BY-SEC-0x`. Rows (21 items, split rows allowed): 11 IN-08 and IN-09; 12 IN-01..IN-07; 14 IN-01..IN-05; 15 IN-01..IN-03. The seed content for each row's disposition is in the 16-RESEARCH.md "Closure ledger rows" table. Fill Evidence with real test names and commit hashes after the commits land. Add a state line like "Recorded: <date>, HEAD <sha>", and a note that the 2.0.3 send commit `91d8847` is only captured here, with the artifact itself deferred to Phase 19.

---

### `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` (D-10)

Self-edit. Reword GATE-13 (lines 23-30) and GATE-15 (lines 37-40). Add traceability rows for Phase 17 and Phase 19 in the existing table, matching the row format of the V2-01/V2-02 `Deferred` rows (lines 111-112). Confirm V2-01 and V2-02 (lines 73-74, 111-112) for BOOK-02 with no edit. Adjust the Phase 16, 17 and 19 success criteria in the ROADMAP. Put all of this in the same commit as the ledger.

---

### SUMMARY frontmatter (BOOK-01)

**Analog:** `14-01-SUMMARY.md` line 15 and `14-02-SUMMARY.md` line 12, which use `requirements-completed: [..]`. The values come from the PLAN `requirements:` lists, mapped in 16-RESEARCH.md ("Pattern: BOOK-01").
- 11-0x and 13-0x: add `requirements-completed:` directly after the existing `requirements:` line.
- 12-0x: add only `requirements-completed:`, since there is no existing key.

Stage with `git add -- <18 explicit paths>`. The files are CRLF in the working tree and LF in the index, so edit them keeping CRLF. Before committing, check `git diff --cached --name-only` and `git diff --cached --stat` (about 1 line per file). Never use `git add -A`, `git add .` or `git add .planning`.

## Shared Patterns

### Fail loudly, never skip
**Source:** `tests/aa_history.py` `require_history`, `tests/conftest.py` (`EMS_FAIL_ON_SKIP=1` collect-skip guard).
**Apply to:** the D-10 test, the deep-root test, and any new clone or history test. Use `assert` or `pytest.fail(..., pytrace=False)`, never `pytest.skip`. The clone failure message pattern is `pytest.fail(f'git clone --shared ... failed: {cloned.stderr.decode(errors="replace")}', pytrace=False)`.

### Domain exceptions with specific `match=`
**Source:** notice test line 746, `pytest.raises(GitHistoryError, match='git show failed')`. Builder classes are `AuthorityError` and `GitHistoryError`.
**Apply to:** all new builder and test error cases.

### Per-command git config in clones
**Source:** research sketch. Use `git -c user.name=t -c user.email=t@t -c commit.gpgsign=false -c core.autocrlf=false`, with no writes to `.git/config`.
**Apply to:** the D-10 overlay commit. The existing `git(*args, cwd=...)` helper at line 26 of the lineage test, and the matching helper in the notice test, accept `cwd`.

### Builder output gate
**Source:** the builder's `validate_notice()` rebuild compare (about lines 584-588), plus `git diff --exit-code` and a `git show HEAD:` byte compare.
**Apply to:** every builder edit.

### Test-environment constraints
Bash and local `git clone` are unreliable on this machine (`sh.exe` crash). Clone-based tests (D-10, `make_clone`, deep-root) get authoritative evidence from the CI `archive-assessment` job via `workflow_dispatch`. The orchestrator runs pytest in PowerShell with a fresh `--basetemp`, `EMS_FAIL_ON_SKIP=1`, and `-p no:cacheprovider`.

### Frozen-file guard (phase gate)
The publisher, `build_archive_assessment_demo3_w1_req_001_reply.py` and `build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` must show no diff against HEAD blobs. Use `--ignore-cr-at-eol` or blob compare because of CRLF noise.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `16-REVIEW-CLOSURE.md` | ledger doc | n/a | No existing per-finding disposition ledger. `12-BASELINE-RED.md` and `14-REVIEW-FIX.md` supply table and frontmatter style only. |
| `write_atomic` helper in the builder | utility | file-I/O | No atomic temp-and-replace writer exists in the builder. Use the stdlib sketch in 16-RESEARCH.md, in the builder's compact-helper style. |

## Metadata

**Analog search scope:** `tests/`, `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `.planning/phases/12-*`, `.planning/phases/14-*`. Everything else comes from the line-level citations in 16-RESEARCH.md, which were not re-read here.
**Files scanned:** about 8 read directly.
**Pattern extraction date:** 2026-11-18
