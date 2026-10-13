---
phase: 02-blind-drafting
reviewed: 2026-10-13T18:59:59Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - scripts/validate_archive_assessment_rule_proposals.py
  - tests/test_archive_assessment_rule_proposals.py
  - tests/test_archive_assessment_rule_proposals_record.py
  - schemas/archive_assessment_not_applicable_rule_proposals.schema.json
  - schemas/archive_assessment_rule_proposals_drafting_record.schema.json
  - registry/archive_assessment_rule_proposals_drafting_record.json
  - docs/ARCHIVE_ASSESSMENT_RULE_DRAFTER_BRIEF.md
findings:
  critical: 0
  warning: 10
  info: 10
  total: 20
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-10-13T18:59:59Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Narrative Findings (AI reviewer)

## Summary

Reviewed the proposals validator, its two schemas, both test modules, the drafting record and (for consistency only) the approved drafter brief. `registry/archive_assessment_not_applicable_rule_proposals.json` was not opened, in line with the scope rule; statements about it are derived from code and git metadata only.

Method: read every in-scope file, read the helpers the validator imports from `scripts/publish_archive_assessment_applicability_authority_v2.py` (`validate_rule`, `contains_absolute`, `semantics`, `catalog_controls`, `load`, `dump`), ran both test modules (88 passed, 0 skipped on this full clone), and ran mutation probes against `validate_proposals`, `validate_record` and both generated schemas using the test module's own synthetic fixture. Findings marked "confirmed" were reproduced by a probe or a git query, not inferred.

Assessment:

- The core fail-closed property holds. A rule with state `UNKNOWN`, a non-rule field, zero conditions, a repeated field, an extra key or a wrong combination is rejected by both the validator and the schema. No path was found by which `UNKNOWN` can resolve to not-applicable through this validator.
- Authority and decision-id keys are rejected, but only because every object has an exact-key check; the dedicated `walk_forbidden` key branch is never exercised on its own (WR-09).
- No BLOCKER was found. Every defect below either fails closed with the wrong exception, is unreachable without a second change elsewhere, or weakens an assurance without producing a wrong applicability result. They are reported as WARNING rather than inflated.
- The findings that most deserve attention before the next phase are WR-01 (frozen artifacts are validated against live inputs, so an unrelated catalog or publisher change makes them permanently invalid), WR-02 (the CLI prints `PASS` while skipping a requested check), WR-03 (the record's hashes and paths are not bound to anything by the validator) and WR-04 (the absolute-path guard only catches strings that begin with a path).

On the specific question about the baseline count lowered from 4 to 2: see WR-08. Short answer: the lowering did not weaken the test relative to what exists, because exactly two files match the filter at the baseline, so 4 was unsatisfiable. The real gap is the filter, which leaves the v2 schema and both publisher scripts unguarded.

## Warnings

### WR-01: Frozen artifacts are validated against live catalog and live semantics

**Classification:** WARNING
**File:** `scripts/validate_archive_assessment_rule_proposals.py:56-66`, `:109-111`; `tests/test_archive_assessment_rule_proposals.py:180-222`
**Issue:** `validate_proposals` requires `catalog_source` to equal the fingerprint of the working-tree catalog (`catalog_fingerprint()`), `drafting_frame` to equal the current `V2.semantics()`, and every `catalog_inputs` value to equal the live catalog. The proposals file and the brief are frozen: `test_drafting_commit_is_sole_commit_of_proposals_file` and `test_proposals_frozen_since_drafting_commit` forbid any later commit to them. The two rules collide. Any later byte change to `registry/control_catalog.yaml` (including to one of the 59 controls outside this project) or any edit to `semantics()` in the v2 publisher (which the publication phase is likely to touch) makes `--validate` fail permanently and breaks `test_real_proposals_validate_under_validator_and_schema`, `test_catalog_fingerprint_matches_blob_bytes`, `test_real_proposals_header_status_and_ids`, `test_catalog_drift_real_proposals_match_live_catalog`, `test_brief_catalog_extract_equals_live_catalog` and `test_brief_header_equals_expected_header`, with no permitted way to repair the frozen files. The likely outcome is pressure to hand-edit a frozen draft or delete tests. The record tests already do this correctly by reading the catalog at `drafting_commit`.
**Fix:** Once a drafting record exists, pin the comparison to it instead of to the working tree. For example:
```python
def catalog_fingerprint(rev: str | None = None) -> dict:
    blob = git('rev-parse', f'{rev}:{CATALOG_REL}').decode('ascii').strip() if rev else git('hash-object', CATALOG_REL).decode('ascii').strip()
    data = git('cat-file', 'blob', blob)
    return {'relative_path': CATALOG_REL, 'git_blob_id': blob, 'sha256': hashlib.sha256(data).hexdigest()}
```
and have `validate_proposals` take the catalog (parsed from `git show <drafting_commit>:registry/control_catalog.yaml`) and the frame from the record's `drafting_commit` when `RECORD` exists. Keep one separate, clearly named drift test that reports live-catalog divergence as information for the approver, not as invalidity of the draft.

### WR-02: CLI prints PASS while silently skipping a requested validation

**Classification:** WARNING
**File:** `scripts/validate_archive_assessment_rule_proposals.py:184-192`
**Issue:** The three flags are independent `store_true` options dispatched by `if / elif / elif`. Confirmed: `--validate --validate-record` validates only the proposals, never loads the record, and prints a single `PASS` with exit code 0. `--validate --emit-schema` likewise never emits. A wrapper or operator passing both flags gets a pass for a check that did not run, which is a fail-open in a validator whose purpose is to fail closed.
**Fix:**
```python
parser = argparse.ArgumentParser()
g = parser.add_mutually_exclusive_group(required=True)
g.add_argument('--validate', action='store_true'); g.add_argument('--validate-record', action='store_true'); g.add_argument('--emit-schema', action='store_true')
```
This also removes the need for the trailing `parser.error(...)` branch.

### WR-03: Record validation binds nothing; hashes and paths are checked only for shape

**Classification:** WARNING
**File:** `scripts/validate_archive_assessment_rule_proposals.py:122-144`, `:130-131`; `schemas/archive_assessment_rule_proposals_drafting_record.schema.json:37-40,49-52,110-113,127-130`; `tests/test_archive_assessment_rule_proposals_record.py:22-24,81-96`
**Issue:** `--validate-record` is purely structural. Confirmed by probe: a record with `proposals_path`, `brief_path`, `catalog_path` and `validator_script` set to arbitrary strings (including `../../outside.json` and backslash-separated paths, contrary to the repository convention of repo-relative forward-slash paths) is accepted by both validator and schema. The validator never compares `proposals_sha256`, `brief_sha256`, `catalog_sha256` or `catalog_git_blob_id` with any file or git object, so the operator-facing command returns `PASS` for a record whose hashes describe nothing. Binding exists only in pytest, and there the tests use their own hard-coded `PROPOSALS` / `BRIEF` / `CATALOG` constants and never read the record's path fields, so those four fields are untested everywhere. In addition `test_proposals_frozen_since_drafting_commit` compares `HEAD` with the drafting commit, so an uncommitted working-tree edit to either frozen file is not detected by it.
**Fix:** In `validate_record`, require the path fields to equal the module constants and verify the hashes against git objects:
```python
exp = {'proposals_path': PROPOSALS.relative_to(ROOT).as_posix(), 'catalog_path': CATALOG_REL, 'brief_path': BRIEF.relative_to(ROOT).as_posix(), 'validator_script': 'scripts/validate_archive_assessment_rule_proposals.py'}
for k, v in exp.items():
    if r[k] != v: errors.append(f'{k} does not equal {v}')
```
and add a `verify_record_bindings(r)` step to `--validate-record` that hashes `git cat-file blob <drafting_commit>:<path>` for proposals and catalog and `<brief_commit>:<path>` for the brief. Emit matching `const` values in `record_schema()`. Add a test that `git hash-object` of each working-tree file equals the blob at the recorded commit.

### WR-04: Absolute-path guard only detects strings that start with a path

**Classification:** WARNING
**File:** `scripts/validate_archive_assessment_rule_proposals.py:119`, `:143` (helper at `scripts/publish_archive_assessment_applicability_authority_v2.py:49-53`)
**Issue:** `V2.contains_absolute` tests `value.startswith(('/', '\\\\'))` or a drive letter at index 0. That is adequate for registry fields whose whole value is a path, but the proposals document consists mostly of free text (`interpretation.text`, `rationale`, `alternative_considered.why`, `shape_limitation.note`) and the record carries the long free-text `isolation_method`. Confirmed by probe: `'see C:/temp/x.json and /etc/passwd'` and a value with one leading space before a drive path are both accepted by validator and schema. `test_absolute_path_fails_closed` (test line 122) only covers the value-is-a-path case, so it gives false comfort for exactly the fields where a path could plausibly appear. The helper also inspects dict values only, never keys.
**Fix:** Add a local embedded-path check in this validator rather than changing the shared helper's behaviour for other callers:
```python
ABS_RE = re.compile(r'(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|\\\\[^\\\s]|(?:^|\s)/[A-Za-z0-9._-]+/)')
def walk_absolute(value: object) -> bool:
    if isinstance(value, str): return bool(ABS_RE.search(value))
    if isinstance(value, dict): return any(walk_absolute(k) or walk_absolute(v) for k, v in value.items())
    if isinstance(value, list): return any(walk_absolute(v) for v in value)
    return False
```
and add tests for an embedded drive path, an embedded POSIX path and a UNC path inside `rationale`.

### WR-05: catalog_inputs is not checked when the control is missing from the catalog

**Classification:** WARNING
**File:** `scripts/validate_archive_assessment_rule_proposals.py:87-93`
**Issue:** `entry = catalog.get(cid)` followed by `if entry is not None and (...)` means that when a requested control is absent from the supplied catalog, every `catalog_inputs` value is accepted unchecked. Confirmed by probe: calling `validate_proposals(value, catalog)` with one requested control removed from `catalog` and that proposal's `scope_owner` altered returns without error. `live_catalog()` (line 65-66) silently drops missing ids, and `V2.catalog_controls()` only asserts 80 unique ids, not that the 21 requested ids are among them. Absence of the authoritative entry therefore resolves to "accepted", the opposite of the project's fail-closed convention. `shape_limitation` (line 102) does handle `entry is None` correctly, which shows the inconsistency.
**Fix:**
```python
entry = catalog.get(cid) if isinstance(cid, str) else None
if entry is None: errors.append(f'{cid}: control is not present in the catalog')
```
and in `live_catalog()` raise `AuthorityError` when `set(CONTROL_IDS) - set(result)` is non-empty. Add a test passing a catalog with one entry removed.

### WR-06: Non-string control_id raises TypeError instead of AuthorityError

**Classification:** WARNING
**File:** `scripts/validate_archive_assessment_rule_proposals.py:115-116`, `:87`
**Issue:** `set(ids)` at line 116 and `catalog.get(cid)` at line 87 require a hashable `control_id`. Confirmed by probe: a proposal whose `control_id` is a list or an object raises `TypeError: unhashable type` from `validate_proposals`. The process still exits non-zero, but the domain-exception contract (`AuthorityError` on any violated invariant) is broken, the accumulated error list is lost, and because the CLI runs `validate_proposals` before the schema (line 187) the schema never gets the chance to report it cleanly. Any caller that catches `AuthorityError` to report a controlled failure would crash instead.
**Fix:**
```python
ids = [x.get('control_id') if isinstance(x, dict) and isinstance(x.get('control_id'), str) else None for x in items]
```
plus the `isinstance(cid, str)` guard shown in WR-05, and a test for a list-valued `control_id`.

### WR-07: All nine git-history assertions skip on a shallow clone and report success

**Classification:** WARNING
**File:** `tests/test_archive_assessment_rule_proposals_record.py:34-43`, applied at `:65-131`
**Issue:** `needs_git` converts "git unavailable", "not a git repository" and "shallow repository" into `pytest.mark.skipif`. Every assertion that proves drafting independence (ancestor, single-path drafting commit, brief precedes drafting, blob hashes, frozen since drafting, sole commit, no decision at drafting commit, published files unchanged) is in that group. `.github/workflows/ems-validate.yml:13` uses `actions/checkout@v4` with no `fetch-depth`, which is a depth-1 shallow clone, so if pytest is ever added to that workflow these tests will all skip and the run will be green. The workflow does not run pytest today, so the guarantees currently rest entirely on local runs. A skipped test is indistinguishable from a passed one in a summary line. On this full clone all 88 tests ran and none skipped.
**Fix:** Fail instead of skipping, with an explicit opt-out:
```python
def needs_git(fn):
    reason = git_ready()
    if reason is None: return fn
    if os.environ.get('EMS_ALLOW_HISTORY_SKIP') == '1': return pytest.mark.skip(reason=reason)(fn)
    def fail(): pytest.fail(f'history assertions cannot run: {reason}')
    fail.__name__ = fn.__name__
    return fail
```
and set `fetch-depth: 0` in the workflow when pytest is wired in.

### WR-08: "Published authority files unchanged" test guards two files and excludes the v2 schema and both publishers

**Classification:** WARNING
**File:** `tests/test_archive_assessment_rule_proposals_record.py:123-131`
**Issue:** Assessment of the count lowered from 4 to 2. Confirmed with `git ls-tree` at the baseline (parent of the commit that added the validator): exactly two paths satisfy the filter at line 128, `registry/archive_assessment_applicability_authority.json` and `schemas/archive_assessment_applicability_authority.schema.json`. A minimum of 4 was therefore unsatisfiable, and lowering it to 2 did not remove any file from coverage. The guarantee is nonetheless weaker than the test name states, for three reasons that are independent of the number:

1. The `'_v2' not in Path(p).name` filter excludes `schemas/archive_assessment_applicability_authority_v2.schema.json`, which exists at the baseline and defines the rule vocabulary the drafts are written in.
2. `ls-tree` is restricted to `registry` and `schemas`, so `scripts/publish_archive_assessment_applicability_authority.py` and `..._v2.py` are not covered. The v2 publisher is the source of `drafting_frame` (`V2.semantics()`), `validate_rule` and `contains_absolute`; a change to it between baseline and drafting commit would alter what the draft was validated against without failing this test.
3. `len(paths) >= 2` is a floor, not an identity. If the name filter drifted to match fewer real files plus an unrelated one, the test would still pass.

For the record, `git diff --name-only <baseline> <drafting_commit>` shows that none of those files changed in this phase, so the property holds today; the test just does not prove it.
**Fix:**
```python
GUARDED = ['registry/archive_assessment_applicability_authority.json', 'schemas/archive_assessment_applicability_authority.schema.json',
    'schemas/archive_assessment_applicability_authority_v2.schema.json', 'scripts/publish_archive_assessment_applicability_authority.py',
    'scripts/publish_archive_assessment_applicability_authority_v2.py']
for p in GUARDED:
    a = git('rev-parse', '--verify', f'{dc}:{p}'); b = git('rev-parse', '--verify', f'{baseline}:{p}')
    assert a.returncode == 0 and b.returncode == 0 and a.stdout == b.stdout
```
Also assert `added` is non-empty with a message instead of relying on `added[-1]` raising `IndexError`.

### WR-09: Forbidden-key tests are satisfied by the exact-key check; walk_forbidden's key branch is untested

**Classification:** WARNING
**File:** `tests/test_archive_assessment_rule_proposals.py:44-48`, `:113-115`; `scripts/validate_archive_assessment_rule_proposals.py:70-77`
**Issue:** `test_authority_key_fails_closed` and `test_decision_id_key_fails_closed` add the forbidden key to a proposal. That is rejected at validator line 82 by the exact-key check, identically to `test_extra_proposal_key_fails_closed` on the line above. `invalid()` uses `pytest.raises(AuthorityError)` with no `match`, so the tests cannot tell which rule fired. Deleting lines 72-73 of the validator (the `FORBIDDEN_KEYS` branch) would leave all 88 tests green. The same weakness applies generally: no fail-closed test asserts the reason for rejection, so a mutation that happens to trip a different rule can mask a broken one. `not_applicable_decision_state` and `decision_ids` have no test at all.
**Fix:** Test the walker directly and assert messages:
```python
@pytest.mark.parametrize('key', sorted(MODULE.FORBIDDEN_KEYS))
def test_walk_forbidden_flags_each_key_at_any_depth(key):
    errors = []; MODULE.walk_forbidden({'a': [{'b': {key: 'x'}}]}, 'root', errors)
    assert errors == [f"root.a[0].b: forbidden key {key!r}"]
```
and give `invalid()` an optional `match` argument used by the targeted tests (`match='forbidden key'`, `match='absolute path'`, `match='governance decision id'`, `match='2 to 4 sentences'`).

### WR-10: Two incompatible SHA-256 conventions for the same catalog file under core.autocrlf

**Classification:** WARNING
**File:** `scripts/validate_archive_assessment_rule_proposals.py:56-59`; `registry/archive_assessment_rule_proposals_drafting_record.json:10,13,25` (contrast `scripts/publish_archive_assessment_applicability_authority_v2.py:44,130`)
**Issue:** `catalog_fingerprint()` hashes git blob bytes, which is the right choice for determinism across platforms. The existing publisher's `digest()` hashes working-tree bytes and writes that into `source_lineage.catalog_reference.sha256`. Confirmed on this checkout: `core.autocrlf=true`, no `.gitattributes`, and `git ls-files --eol` reports `i/lf w/crlf` for `registry/control_catalog.yaml`; the working-tree SHA-256 differs from the blob SHA-256 recorded in `catalog_sha256`. So two EMS artifacts will state different SHA-256 values for the same catalog at the same commit, and anyone verifying `catalog_sha256`, `brief_sha256` or `proposals_sha256` with `Get-FileHash` on a Windows checkout may get a mismatch. Nothing in the record, the schema or the proposals header says the hashes are over blob bytes. Separately, `catalog_fingerprint()` runs `git hash-object` without `-w` and then `git cat-file blob`, so an uncommitted catalog edit fails with the opaque message `git cat-file failed: ... bad file` rather than saying the catalog differs from any committed version.
**Fix:** State the basis in the artifacts and make the failure legible. Add a schema-level description (does not alter validation) or a `hash_basis: 'GIT_BLOB_BYTES'` field to the record on its next revision; add a `.gitattributes` entry such as `registry/** text eol=lf` and `docs/*.md text eol=lf` in a separate deliberate commit so both conventions agree; and wrap the `cat-file` call:
```python
try: data = git('cat-file', 'blob', blob)
except AuthorityError: raise AuthorityError(f'{CATALOG_REL} in the working tree does not match any committed version') from None
```

## Info

### IN-01: Validator equality treats 1 and True as equal

**Classification:** WARNING (minor; compensated by the schema)
**File:** `scripts/validate_archive_assessment_rule_proposals.py:93`, `:111`
**Issue:** `p.get(k) != exp[k]` and `entry[k] != v` use Python equality. Confirmed by probe: `requires_explicit_controlled_rule: 1`, `min_conditions: true` and an integer `inheritance_allowed` pass `validate_proposals`; only the JSON Schema rejects them. Safe today because the CLI and the real-file tests run both, but the validator alone is not type-strict.
**Fix:** Compare canonical JSON: `json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True)`.

### IN-02: Anchored patterns accept a trailing newline; dates are not calendar-checked

**Classification:** WARNING (minor)
**File:** `scripts/validate_archive_assessment_rule_proposals.py:42-44`, `:127`, `:133`; `schemas/archive_assessment_rule_proposals_drafting_record.schema.json:13,34,42,46,54,78,103,115`
**Issue:** `re.match(r'^...$', s)` matches when `s` ends with `\n`. Confirmed: a 40-hex `drafting_commit` followed by a newline passes validator and schema. `drafted_on` / `brief_approval.date` accept `2026-99-99`. Line 133 also coerces with `str(...)` before matching, which is harmless only because `nonempty` runs first.
**Fix:** Use `re.fullmatch` with unanchored patterns in the validator and `\A...\z`-equivalent handling (or `datetime.date.fromisoformat`) for dates.

### IN-03: Governance-id detection is narrow

**Classification:** WARNING (minor)
**File:** `scripts/validate_archive_assessment_rule_proposals.py:41`, `:77`; `tests/test_archive_assessment_rule_proposals_record.py:115`
**Issue:** `FORBIDDEN_ID_RE` is case-sensitive and applied to string values only, not dict keys. Confirmed: a lower-case id in `rationale` is accepted. The record test greps the drafting-commit tree for the literal `AA4-GOV` in `registry` only.
**Fix:** `re.compile(r'AA[0-9]+[-_ ]?GOV', re.IGNORECASE)`, apply to keys as well, and use the same pattern in the record test.

### IN-04: Sentence counter is a heuristic that both over- and under-counts

**Classification:** WARNING (minor)
**File:** `scripts/validate_archive_assessment_rule_proposals.py:97`
**Issue:** `[.!?](\s|$)` counts terminators, not sentences. Confirmed: a one-sentence rationale containing `e.g.` passes as two sentences, and `One. Two. Three` (no final terminator) passes as two. The brief asks for periods only; the validator also accepts `!` and `?`. Not enforced by the schema, which the tests acknowledge by naming.
**Fix:** Require the stripped text to end with a terminator and document the rule as "2 to 4 sentence terminators"; no change to frozen content is implied.

### IN-05: git is executed at import time; one skip path is unreachable; missing git raises a raw exception

**Classification:** WARNING (minor)
**File:** `tests/test_archive_assessment_rule_proposals.py:33`, `:173-177`; `tests/test_archive_assessment_rule_proposals_record.py:21`, `:41-43`; `scripts/validate_archive_assessment_rule_proposals.py:17-19`, `:51-54`
**Issue:** `FIXTURE = build_fixture()` calls `expected_header()` and therefore `git hash-object` / `git cat-file` while pytest is collecting. Without git, or in an exported tree with no `.git`, the whole module errors at collection, so the `pytest.skip('git unavailable')` branch in `git_out` can never be reached. The record test module re-executes the first test module at import (`EARLIER`) and calls `git_ready()` once per decorated test. In the validator, `git()` lets `FileNotFoundError` escape instead of `AuthorityError`, and `_spec.loader` is dereferenced without the `is not None` check that both test modules perform.
**Fix:** Build the fixture in a module-scoped pytest fixture, compute `git_ready()` once, catch `OSError` in `git()` and raise `AuthorityError('git is unavailable')`.

### IN-06: Existence gating is obsolete now that the artifacts are committed

**Classification:** WARNING (minor)
**File:** `tests/test_archive_assessment_rule_proposals.py:161-163`, `:179`, `:183`, `:189`, `:196`, `:210`, `:219`, `:224`, `:231`
**Issue:** `gated(path)` skips eleven real-file tests when the file is missing. That was needed before drafting; now a deleted proposals file, brief or record would turn those tests into skips. The only thing that still fails is `test_proposals_brief_and_record_exist` in the other module.
**Fix:** Remove the `gated` marks so absence fails in the module that owns the assertions.

### IN-07: History assertions leave two gaps

**Classification:** WARNING (minor)
**File:** `tests/test_archive_assessment_rule_proposals_record.py:75-78`, `:119-120`, `:26-28`
**Issue:** (a) `brief_commit` is only required to be an ancestor of the drafting commit at which the brief has the recorded hash. Because the brief is frozen, any commit between the one that added the brief and the drafting commit satisfies this; the test does not assert that `brief_commit` is the commit that introduced the brief. (b) `git log -- <path>` uses default history simplification, so a change made and undone on a side branch that was later merged would not be listed; `--full-history` closes that. (c) The `git` helper never checks `returncode` for `rev-parse` / `show`; the comparisons are only safe because a failing `rev-parse` echoes its distinct argument to stdout, which is accidental.
**Fix:** Assert `git log --diff-filter=A --format=%H -- <brief>` equals `[brief_commit]`, add `--full-history`, and assert `returncode == 0` in the helper callers.

### IN-08: Dead and redundant code

**Classification:** WARNING (minor)
**File:** `scripts/validate_archive_assessment_rule_proposals.py:22`; `tests/test_archive_assessment_rule_proposals.py:70`, `:156`, `:168-169`; `tests/test_archive_assessment_rule_proposals_record.py:102-103`
**Issue:** `CATALOG` is defined and never used in the validator (only `CATALOG_REL` is). `to_rule(r, alt=True)` never reads `alt`. In `test_term_scan_detects_each_term` the left disjunct `scan(...) == [t]` is redundant with `t in scan(...)`. `test_term_scan_file_names` duplicates an assertion already made in `test_term_scan_real_files` and in the record module. The `catalog['controls'] if ... else catalog` and `e.get('control_id') or e.get('id')` fallbacks handle catalog shapes that `V2.catalog_controls()` does not accept.
**Fix:** Delete the unused names and fallbacks.

### IN-09: Brief and validator differ on four soft points (informational only; brief is approved and not editable)

**Classification:** WARNING (informational; no edit to the brief is proposed)
**File:** `docs/ARCHIVE_ASSESSMENT_RULE_DRAFTER_BRIEF.md:59`, `:63`, `:377`, `:382`
**Issue:** Headings (`## Catalog extract`, `## Header to copy`), the header block, the catalog fingerprint, the 1-to-4 condition limit, the key list and the skeletons all agree with the validator and schema, and the "six entries are not REPOSITORY scoped" statement matches the extract. Differences, all on the validator side: (1) the brief requires proposals "in the same order" as the extract; the validator and schema compare as a set (confirmed: a reversed list is accepted). (2) The brief says sentences end with a period; the validator also counts `!` and `?`. (3) The brief forbids cross-references between entries; nothing checks that a rationale does not name another control id (confirmed accepted). (4) The brief calls `inheritance_allowed` and `classification_status` optional copies, which the validator honours.
**Fix:** If stricter conformance is wanted, tighten the validator (order check `ids == CONTROL_IDS`; reject any `EMS-CTRL-` id other than the proposal's own inside its text fields) in a way that is first confirmed, from code and tests alone, not to invalidate the frozen draft. No change to the brief.

### IN-10: Several record fields are self-asserted and unverifiable

**Classification:** WARNING (minor)
**File:** `registry/archive_assessment_rule_proposals_drafting_record.json:2-7,14-16,28-29`; `scripts/validate_archive_assessment_rule_proposals.py:133-138`
**Issue:** `validator_result` is constrained to the constant `PASS`, so it records nothing a reader could not assume; the validator that produced it is identified by path only, not by commit or hash, and that script has since been free to change. `correction_rounds`, `discarded_attempts` and `drafted_on` are not cross-checked against anything (for example the drafting commit's author date). `brief_approval.approver` accepts any non-empty string (confirmed), although project instructions name a single approving authority. The record content itself is internally consistent: sorted keys, trailing newline, no absolute paths, none of the scan terms, and its hashes match the git objects (the passing history tests confirm this).
**Fix:** On the next revision of the record shape, add `validator_commit` or `validator_sha256`, and constrain `approver` in `validate_record` / `record_schema()` to the approved authority value held in one module constant.

---

_Reviewed: 2026-10-13T18:59:59Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
