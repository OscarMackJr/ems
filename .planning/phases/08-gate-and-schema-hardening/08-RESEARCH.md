# Phase 8: Gate and Schema Hardening - Research

**Researched:** 2026-11-11
**Domain:** Python fail-closed validators, JSON Schema 2020-12 strictness, git-pinned reference reads (EMS archive-assessment v2 publisher, reply builder, decisions builder)
**Confidence:** HIGH for code locations and mechanics (read and probed in this session). One finding about GATE-05 is a blocker that needs a user decision (see Open Questions, Q1).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** The pre-publication window is an explicit CLI flag, `--validate --pre-publication`. In that mode the publication record must exist and name exactly the superseded authority (for 2.0.2 that is `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1`, version 2.0.1). Its digests and commit are checked against that superseded publication.
- **D-02:** Plain `--validate`, which is what CI runs, requires a publication record whose `authority_id` and `version` match the current authority. If the record is absent, or names any other authority, it fails. Today's skip branch at publisher L679-683 is removed.
- **D-03:** The record cross-check also proves that `publication_commit` really contains the published bytes. It runs `git_show(publication_commit, AUTHORITY_REL)` and `git_show(publication_commit, <manifest rel>)`, reusing the Phase 7 helper, and their LF digests must equal `authority_sha256` and `manifest_sha256`. If history is missing it fails closed.
- **D-04:** `mutation_gates` counts a rejection only for domain errors: AUTHORITY and SIGNOFF targets: `AuthorityError`; DECISIONS target: the builder's `ValueError`; schema gate: `jsonschema.ValidationError`. Any other exception propagates and fails the run. It is never counted as a rejection.
- **D-05:** Any of the 26 existing mutations that is rejected today only through `KeyError`, `TypeError` or `AttributeError` is fixed by hardening the validators (`validate_publication`, `validate_signoff`, the decisions validator path) so they check shape first and raise the domain error. Mutation ids and descriptions do not change, and every mutation must still be rejected.
- **D-06:** The negative-invariant output keeps its current shape (`rejected_by: [PYTHON_VALIDATOR, SCHEMA]`), with no exception-class field.
- **D-07:** The frozen reference is the catalog at a pinned commit. `catalog_reference` gains `commit: 62a8955dc28d9458cd1167fad314926e057c31fc`, the v1 baseline. Its LF digest is `12bb1a9d...`, verified identical at `62a8955`, `31addfa` and HEAD on 2026-10-20; the catalog last changed in `d5c1a73`.
- **D-08:** Every catalog read in the v2 publisher goes through `git_show(CATALOG_COMMIT, CATALOG_REL)` instead of the live file. That covers `catalog_controls()` used by the build (L133), `validate_publication` (L241, L306) and lineage. `catalog_reference` joins `COMMIT_PINNED` in `validate_lineage`. The live `registry/control_catalog.yaml` is no longer read by `--validate`.
- **D-09:** Without git history, or in a shallow clone, catalog validation fails closed, consistent with 07 D-11. CI uses `fetch-depth: 0`.
- **D-10:** Tests prove both directions: editing the live catalog in a scratch copy does not change the `--validate` and build result; tampering with the pinned reference (its commit, path or digest) makes validation fail.
- **D-11:** `resolve_record_commit` in `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` first runs `git rev-parse --is-shallow-repository`. If the answer is `true`, or the command fails, it raises `AuthorityError` with an explicit message along the lines of "shallow clone: cannot resolve the publication record commit; fetch full history". A full clone behaves as before.
- **D-12:** GATE-04 is output-neutral. The reply JSON and MD stay byte-identical and nothing is regenerated in Phase 8. Phase 7 D-14 still holds for reply content.

### Claude's Discretion
- **GATE-05:** cross-note uniqueness in `scripts/build_archive_assessment_governance_decisions.py` compares `norm_templated` forms on both sides, and at every comparison site rather than only L161. Add a test with two notes that differ only in templated values. The change must be output-neutral, so the committed decisions do not change.
- **SCHEMA-07:** `schema()` sets `additionalProperties: false` at the top level, on control rows and on `not_applicable_semantics`. Add three negative mutations (an extra field at each level) with `schema_must_reject=True`, so the negative-invariant output records each as rejected by `SCHEMA`. The mutation count grows from 26 to 29, and the certified outputs pick this up at the Phase 9 republication.
- **Keep the flag minimal:** the exact flag name is `--pre-publication`; the helper names are up to the planner. Match the publisher's compact single-quote style.

### Deferred Ideas (OUT OF SCOPE)
- Recording the exception class in the negative-invariant output (D-06: not now).
- Verifying the reply record's introducing commit beyond the shallow check (D-11 chose shallow detection only).

Other scope limits from CONTEXT: no `VERSION` bump, no regeneration of any committed registry, schema or generated output, no 2.0.2 publication (Phase 9). The red set may grow only by tests named in a plan.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GATE-01 | Record cross-check fails on absent record or other authority; only explicit pre-publication mode excepted | `validate_published` L679-684 is the only site; add `pre_publication` parameter and `--pre-publication` flag (main L694-701); D-03 via `git_show` |
| GATE-02 | Mutation gate counts rejection only on domain error | `mutation_gates` L584-601; probe shows all 26 mutations already raise the domain error today, so D-05 is a regression test, not a validator rewrite |
| GATE-03 | `--validate` uses frozen catalog | Live catalog read at L20, L91, L170, L241 (via `catalog_controls`), L306; replace with `git_show(CATALOG_COMMIT, CATALOG_REL)` |
| GATE-04 | Shallow clone fails explicitly | `resolve_record_commit` reply L262-267 |
| GATE-05 | Cross-note uniqueness on `norm_templated` | Decisions builder L162-163 (only cross-note site). **Conflicts with the committed answers file, see Q1** |
| SCHEMA-07 | `additionalProperties:false` in three places | `schema()` L347-382. **14 properties are used by real documents but undeclared; they must be declared first** |
</phase_requirements>

## Summary

All six requirements are small edits in three scripts: `scripts/publish_archive_assessment_applicability_authority_v2.py` (GATE-01/02/03, SCHEMA-07), `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` (GATE-04) and `scripts/build_archive_assessment_governance_decisions.py` (GATE-05). The Phase 7 helpers (`git_show`, `bad_rel`, `COMMIT_PINNED`, `NORMALISERS`) cover the git-pinned catalog and record-commit checks. Nothing new needs installing; no external packages are involved.

Three findings change the plan beyond what CONTEXT states. (1) GATE-05 as specified would reject the certified real `registry/archive_assessment_governance_answers.json`: all 21 committed notes are the same sentence with a different numeric prefix (for example `009-Frozen nature of snapshot can not be expressed in fields available`), so under `norm_templated` 20 of 21 collide. That breaks `build_decisions` (strict), the CI step `build_archive_assessment_governance_decisions.py --validate`, and `test_committed_answers_strict_when_filled`; it is not output-neutral. This needs a user decision before planning (Q1). (2) SCHEMA-07 cannot simply add `additionalProperties:false`: the current schema does not declare 5 top-level, 6 control-row and 2 `not_applicable_semantics` properties that real documents carry, so the real authority would fail its own schema. (3) D-05 is already satisfied: a probe of all 26 mutations against the real files shows each is rejected with the domain exception (`AuthorityError`), none by `KeyError`/`TypeError`/`AttributeError`. The work is narrowing the `except` tuples and adding tests that prove other exceptions propagate.

**Primary recommendation:** Plan five small waves: (A) schema() declaration completion plus `additionalProperties:false` plus 3 mutations; (B) catalog pin (`CATALOG_COMMIT`, `catalog_bytes()` helper, lineage and schema `commit` field); (C) publication-record gate with `--pre-publication`; (D) `mutation_gates` narrowing; (E) reply shallow check and GATE-05 (after Q1 is answered). Update the `env` fixture once, in wave B, to stub the new git reads.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Record cross-check, pre-publication mode | Publisher script (`validate_published`) | CI workflow runs plain `--validate` | Validation is a script stage; CI only invokes it |
| Mutation gate narrowing | Publisher script | pytest | Gate lives in `mutation_gates`; tests prove failure paths |
| Frozen catalog | Publisher script via `git_show` | `registry/control_catalog.yaml` stays a live, uncontrolled-by-this-phase file | Pin is data in `catalog_reference` plus a code constant |
| Schema strictness | Publisher `schema()` generator | `schemas/archive_assessment_applicability_authority_v2.schema.json` (generated, not edited) | Schema file is regenerated at Phase 9 only |
| Shallow detection | Reply builder (`resolve_record_commit`) | git CLI | Reply owns the lookup |
| Note uniqueness | Decisions builder (`strict_checks`) | answers file (data) | Builder validates answers |

## Standard Stack

No new libraries. Existing, per CLAUDE.md: Python 3.12, `jsonschema` (Draft 2020-12 validator), PyYAML, pytest, stdlib `subprocess`/`hashlib`/`re`. Run tests with `--basetemp` pointing at a scratch dir (project memory note).

### Package Legitimacy Audit
No external packages are installed in this phase. Not applicable. Packages removed: none. Packages flagged: none.

## Architecture Patterns

### Flow (validation path after this phase)

```
CI: publisher --validate [--pre-publication]
  validate_published(pre_publication)
    validate_governance_decisions()            (decisions builder, real file)
    load AUTHORITY -> validate_publication(a)  -> catalog_controls() <- git_show(CATALOG_COMMIT, CATALOG_REL)   [GATE-03]
                                               -> lineage catalog digest <- same pinned blob
    schema check (committed SCHEMA, now additionalProperties:false)                                              [SCHEMA-07]
    validate_lineage(lin)  catalog_reference now in COMMIT_PINNED -> git_show(entry.commit, path)
    rebuild + compare (build_published_authority -> catalog via git)
    ... manifest / output checks ...
    record cross-check (record REQUIRED)                                                                         [GATE-01]
       plain: authority_id+version == current; digests == live files; git_show(publication_commit, AUTHORITY_REL/manifest rel) LF digests == record   [D-03]
       --pre-publication: authority_id+version == SUPERSEDED; digests/commit == SUPERSEDED / git_show at record commit
build_all_outputs -> run_mutations -> mutation_gates (domain errors only)                                         [GATE-02]
reply --build: resolve_record_commit -> rev-parse --is-shallow-repository first                                  [GATE-04]
decisions build/validate: strict_checks -> note uniqueness on norm_templated                                      [GATE-05]
```

### Exact code map (line numbers as of this session)

Publisher `scripts/publish_archive_assessment_applicability_authority_v2.py` (703 lines):
- Constants: `CATALOG = REGISTRY/'control_catalog.yaml'` L20; `CATALOG_REL` L74; `V1_BASELINE_COMMIT` L46; `EXPECTED_NORMALISATION` L75; `SUPERSEDED_V2_0_0` L37-45 (VERSION is still '2.0.1', L35; SUPERSEDED is still the 2.0.0 entry in the working code).
- `catalog_controls()` L90-96 reads live `CATALOG`.
- `build_authority()` L132-175; `catalog_reference` built at L170 with `lf_digest(CATALOG)`.
- `validate_authority` L217-262 (catalog read at L241). `validate_publication` L264-313 (catalog digest at L306, key `required_for_deterministic_compilation` allowed through).
- `bad_rel` L315, `COMMIT_PINNED` L317, `git_show` L319-325 (only place `subprocess` appears), `validate_lineage` L327-345.
- `schema()` L347-382.
- `NEGATIVE_MUTATIONS` L441-468 (26 entries); `Mutation` NamedTuple L415.
- `validate_signoff` L483-502. `validate_governance_decisions` L574-582 (catches KeyError/TypeError/AttributeError and re-raises as `AuthorityError`; this is a different path from the mutation gate, leave as is).
- `mutation_gates` L584-601, `run_mutations` L603-614 (raises `AuthorityError` if not rejected or `schema_must_reject` not met).
- `build_all_outputs` L524 (negative file built at L542-543; outcomes from `run_mutations`).
- `validate_published` L655-684; the skip branch to remove is L679-683 (`if PUBLICATION_RECORD.exists(): record=load(...); if record.get('authority_id') == a['authority_id']: ...`).
- `write_publication_record` L686-691; `main` L693-702 (argparse with `--validate`, `--emit-schema`, `--publish`, `--dry-run`, `--validate-signoff`, `--record-publication`).

Reply `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`: `git()` L258-259 (`subprocess.run(['git',*args], cwd=ROOT, capture_output=True, text=True)`), `resolve_record_commit` L262-267, called from `build_reply` L79. Module name for the publisher is `V2`; error class is `V2.AuthorityError`. `push_check` (L273+) already monkeypatches `git` in tests with `fake_git`.

Decisions builder `scripts/build_archive_assessment_governance_decisions.py`: `norm` L69, `norm_templated` L71, `strict_checks` L151-184; the only cross-note comparison is L162-163 (`seen` keyed by `norm(n)`). L161 compares note to drafted strings with `norm_templated` (already templated). L178, L184, L305 compare decided rationale to drafted rationale with `norm` (rationale vs draft, not note vs note; not cross-note uniqueness). `validate_decisions` (around L280-312) has no cross-record note uniqueness check. `AuthorityError = V2.AuthorityError` (L21) and `AuthorityError` subclasses `ValueError`, so the decisions-target domain error is satisfied by `AuthorityError`.

### Implementation patterns (prescriptive)

**GATE-03 catalog helper** (match single-quote compact style; keep `subprocess` out of everything except `git_show`, enforced by `test_module_does_not_call_git` L91 and `test_publisher_source_runs_no_subprocess_or_evaluator` L702):

```python
CATALOG_COMMIT = V1_BASELINE_COMMIT  # '62a8955dc28d9458cd1167fad314926e057c31fc' per D-07

def catalog_bytes() -> bytes: return git_show(CATALOG_COMMIT, CATALOG_REL)   # git_show defined later at L319; fine at call time

def catalog_controls() -> list[dict]:
    data = yaml.safe_load(lf_bytes(catalog_bytes()).decode('utf-8'))
    ...same 80-control check...
```
- `build_authority` L170: `'catalog_reference': {'relative_path': CATALOG_REL, 'sha256': hashlib.sha256(lf_bytes(catalog_bytes())).hexdigest(), 'normalisation': 'CRLF_TO_LF', 'commit': CATALOG_COMMIT, 'required_for_deterministic_compilation': False}`.
- `validate_publication` L306: compare `cat.get('sha256')` to the pinned-blob digest AND require `cat.get('commit') == CATALOG_COMMIT` and `relative_path == CATALOG_REL` (D-10 tamper directions: commit, path, digest).
- `validate_lineage`: add `'catalog_reference'` to `COMMIT_PINNED` (L317). Its generic loop already calls `git_show(commit, path)` when `commit` is set and errors if a COMMIT_PINNED label has no commit (L341).
- `schema()` `catalog_reference` (L363): add `'commit': {'const': CATALOG_COMMIT}` to properties and `'commit'` to required.
- Remove the live `CATALOG` constant, or keep only if something else needs it. Users found by grep: `tests/...publication.py:78` (`lf_digest(MODULE.CATALOG)`, must be updated) and `scripts/validate_archive_assessment_rule_proposals.py:90` (`live_catalog()` calls `V2.catalog_controls()`; behaviour is unchanged because bytes are identical at the pin, but its tests in `test_archive_assessment_rule_proposals_record.py` that monkeypatch their own `CATALOG` are unaffected). That script's `frozen_catalog()` L78-87 skip-on-missing-git behaviour must NOT be copied (D-09).
- Shallow clone / no history: `git_show` already raises `AuthorityError` when the object is missing; no extra code is needed beyond not catching it. Add a test that proves it (monkeypatch `subprocess.run` to return nonzero, or point `ROOT` at a git repo lacking the commit).

**GATE-01 gate:** change signature to `validate_published(pre_publication: bool = False)`. Replace L679-683 with a `check_publication_record(a, pre_publication)` helper (suggested name) that: raises if `PUBLICATION_RECORD` is absent; validates the key set equals the six keys written by `write_publication_record` L689 (so `KeyError` is impossible); in plain mode requires `record['authority_id'] == a['authority_id']` and `record['version'] == a['version']` and keeps the existing messages `publication record authority_sha256 does not match the committed authority` / `...manifest_sha256...` (existing tests match on `key`); in pre-publication mode requires `authority_id == SUPERSEDED_V2_0_0['authority_id']`, `version == SUPERSEDED['version']`, `publication_commit == SUPERSEDED['commit']`, `authority_sha256 == SUPERSEDED['sha256']`. In both modes then run D-03: `lf digest of git_show(publication_commit, rel(AUTHORITY)) == record['authority_sha256']` and `lf digest of git_show(publication_commit, f'{rel(OUT)}/{N_MANIFEST}') == record['manifest_sha256']`. In pre-publication mode the live AUTHORITY is the new version, so the live-file digest comparison applies only to plain mode. The publication commit's file paths are identical across 2.0.1 and 2.0.2 (`registry/archive_assessment_applicability_authority_v2.json`, `generated/archive-assessment/ems-aa3-v2/...`), so the same `rel()` values work.
- `main`: add `parser.add_argument('--pre-publication', action='store_true')`; call `validate_published(args.pre_publication)`; `parser.error` if `--pre-publication` is given without `--validate`.
- Note: until Phase 9 bumps VERSION and SUPERSEDED, `--pre-publication` in the working tree would require the record to name 2.0.0 while the committed record names 2.0.1; that mismatch is expected inside the red window and is exactly why unit tests must use synthetic records built from `SUPERSEDED_V2_0_0`, not the real record.

**GATE-02:**
```python
if target == 'AUTHORITY':
    try: validate_publication(doc)
    except AuthorityError: gates.append('PYTHON_VALIDATOR')
    try: jsonschema.Draft202012Validator(schema()).validate(doc)
    except jsonschema.ValidationError: gates.append('SCHEMA')
elif target == 'SIGNOFF':
    try: validate_signoff(doc, authority_digest)
    except AuthorityError: gates.append('PYTHON_VALIDATOR')
elif target == 'DECISIONS':
    try: b.validate_decisions(doc)
    except ValueError: gates.append('PYTHON_VALIDATOR')    # AuthorityError subclasses ValueError
    ...
```
Probe result (this session, real files): all 26 mutations raised `AuthorityError` from their Python validator (none `KeyError`/`TypeError`/`AttributeError`). So no validator rewrite is required for the existing mutations; D-05 reduces to a regression test asserting that each mutation's Python rejection is the domain class. Note `jsonschema.ValidationError` is a separate class (not a `ValueError`); `validate_decisions` raising only `AuthorityError` covers it. The three new SCHEMA-07 mutations need no Python-validator hardening for GATE-02 reasons either, see below.

**GATE-04:**
```python
def resolve_record_commit() -> str:
    try: s = git('rev-parse', '--is-shallow-repository')
    except OSError as e: raise V2.AuthorityError(f'cannot check whether the clone is shallow: {e}') from e
    if s.returncode != 0 or s.stdout.strip() != 'false':
        raise V2.AuthorityError('shallow clone or unreadable repository: cannot resolve the publication record commit; fetch full history')
    ...existing log lookup unchanged...
```
Treating anything other than literal `false` as failure is the fail-closed reading of D-11. `git()` returns text (`text=True`), so compare to str `'false'`.

**SCHEMA-07:** `schema()` must declare every property real documents use, then close the three objects. Measured differences versus the real built authority (`build_published_authority()` this session):
- top level missing from `properties`: `$schema`, `applicability_vocabulary`, `attestation_prohibitions`, `classification_vocabulary`, `evidence_boundary`
- `not_applicable_semantics` missing: `fields_not_usable_in_rules_statement`, `statements` (both are in its `required` list already)
- control row missing: `archive_evidence_capability`, `catalog_scope`, `classification_prerequisites`, `control_name`, `required_non_repository_authority`, `unresolved_reason`

Declare them with minimal typing (for example `{'type':'string'}`, `{'type':'array','items':{'type':'string'}}`, or a `const` taken from the same module constants such as `list(CLASSIFICATION_FIELDS)`) and then add `'additionalProperties': False` to the top-level object (L370), the `controls.items` object (L377) and `sem` (L368). The `allOf` branches at L382 rely on `properties` inside `then`; with `additionalProperties:false` on the row object these still work because `additionalProperties` only considers the row's own `properties`, not those in `allOf` subschemas, which is why the row's own `properties` must stay the complete list. (Standard JSON Schema 2020-12 behaviour: `additionalProperties` is evaluated against sibling `properties`/`patternProperties` only.) Do not use `unevaluatedProperties` unless complete listing proves impractical; the requirement text says `additionalProperties: false`. Do not hand-edit `schemas/...v2.schema.json` (Phase 9 regenerates it with `--emit-schema`; `test_committed_schema_equals_schema_function` is already in the accepted red set).

New mutations (append after the 26, ids are up to the planner, for example `extra_top_level_field`, `extra_field_on_control_row`, `extra_field_in_semantics`), all `schema_must_reject=True`, target `AUTHORITY`:
- top-level: `a.__setitem__('rationale','copied')`. Today's Python validator ACCEPTS this (top-level extra keys are not checked by `validate_authority`), so `rejected_by == ['SCHEMA']` alone; `run_mutations` accepts that because rejection by any gate suffices.
- control row: the existing `extra_field_on_decided_row` is rejected by Python (differs from v1) but is NOT `schema_must_reject` today. The new row mutation should target an undecided row (for example `_row(a,'EMS-CTRL-001')`) so it is distinct; Python also rejects via the v1-difference check, so expect `['PYTHON_VALIDATOR','SCHEMA']`.
- semantics: `a['not_applicable_semantics']['extra']='x'`; Python rejects via `pin != expected`; expect both gates.
Update the count assertions: `test_mutation_records_shape` L633-638 (`len(ids)==26`, `ids[:17]==PREVIOUS_17`, `set(ids[17:])==set(NEW_9)` — adjust so slice logic still holds, for example check `ids[26:]` equals the new three) and `test_certification_and_semantic_files_are_derived` L699 (`len(neg['negative_invariant_tests']) == 26`).

**GATE-05:** replace L162-163 with `k = norm_templated(n)` used for both lookup and `setdefault`. Only one cross-note site exists. See Q1 for the data conflict.

### Anti-Patterns to Avoid
- Catching `KeyError`/`TypeError`/`AttributeError` in the mutation gate (this is exactly the defect).
- Adding a new `subprocess` call outside `git_show` in the publisher (breaks two source-scan tests).
- Reading the live catalog anywhere on the validate path (`CATALOG.read_text`, `lf_digest(CATALOG)`).
- Silently skipping when git history is missing (do not copy `frozen_catalog()` NOTICE-and-return behaviour).
- Editing the committed schema or regenerating any registry/generated output in this phase.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Reading a file at a commit | New subprocess helper | existing `git_show` (L319) | Already validates SHA format, rejects `..` and absolute paths, wraps OSError, fail-closed |
| LF digest of bytes | new hashing code | `hashlib.sha256(lf_bytes(b)).hexdigest()` / `NORMALISERS` | Same normalisation as the certified digests |
| Domain error | new exception class | `AuthorityError` (builder aliases it) | Gate matches on this class |
| Temp git repo in tests | new fixture design | pattern from `fx` in `tests/test_archive_assessment_lineage_validation.py` L50-81 (`git init`, `-c core.autocrlf=false`, `.gitattributes '* -text'`) | Already handles CRLF and identity config |

## Runtime State Inventory

Not a rename/refactor/migration phase; omitted.

## Common Pitfalls

### Pitfall 1: `env` fixture breaks once reads go through git
**What goes wrong:** `env` (publication tests L215-225) patches `MODULE.ROOT` to an empty temp dir. `git_show` runs with `cwd=ROOT`, so every catalog read and every D-03 record-commit read fails there; tests like `test_publish_writes_all_and_is_byte_identical`, `test_validate_rejects_*`, `test_validate_record_*` all go red.
**How to avoid:** In `env`, compute the real catalog bytes before patching ROOT and `monkeypatch.setattr(MODULE, 'catalog_bytes', lambda: real_bytes)`; add a recorder/fake for `git_show` used by the record cross-check (dict of `(commit, path) -> bytes` built from the files `published(env)` wrote). Alternative: `git init` the temp root in `env` and commit the published files, which also makes D-03 a real check; use that for at least one test.
**Warning signs:** many `git show failed` AuthorityErrors in tests that never mention git.

### Pitfall 2: Record tests use `'a' * 40` as commit
`test_validate_record_matching_passes` (L452), `test_validate_record_digest_mismatch_fails` (L466) and `test_write_publication_record` (L436) pass `'a'*40`; D-03 would fail them with `git show failed`. They need the fake `git_show` (or a real temp commit). `test_validate_record_absent_passes` (L447) becomes an expected failure; `test_validate_record_other_authority_id_is_pending` (L457) becomes: plain -> raises; pre-publication with a record naming `SUPERSEDED_V2_0_0` -> passes; pre-publication with 9.9.9 -> raises.

### Pitfall 3: Closed schema rejecting the real authority
Closing the three objects before declaring the 14 missing properties makes `jsonschema` reject the real built authority, turning dozens of "valid" tests red (for example `test_published_document_validates_against_validator_and_schema` L37, every `ok()` in `tests/test_archive_assessment_applicability_authority_v2.py`). Write a test that validates `build_published_authority()` and `build_authority()` against `schema()`, and a test that every key of a built document appears in the schema `properties` at each of the three levels.

### Pitfall 4: Lineage test fixture lacks catalog commit
`fx` in `tests/test_archive_assessment_lineage_validation.py` builds `catalog_reference` without a commit (L71); once the label is in `COMMIT_PINNED` the fixture lineage fails. Update it to `digest_entry(..., commit)`. The working-tree tamper parametrization at L93-107 (`('catalog_reference','CRLF_TO_LF')`, kinds `changed_byte`, ...) then no longer applies for the catalog: `changed_byte` on the working file must now NOT fail (blob semantics, mirror `test_d11_commit_pinned_uses_blob_not_working_file` L137) and move `catalog_reference` into the commit-pinned parametrizations at L114, L129, L144, L152, L187.

### Pitfall 5: GATE-05 versus real data (blocker, see Q1)

### Pitfall 6: `validate_published` CLI inside the red window
`--validate` and `--validate --pre-publication` stay red until Phase 9 regardless (committed authority is the old shape). Plans should verify the new CLI path by unit tests, not by running the real CLI to green. Make sure the CLI fails with an `AuthorityError` message, not a traceback from `KeyError`.

### Pitfall 7: Windows CRLF
`git_show` returns raw blob bytes; always `lf_bytes()` before hashing or YAML decoding. Catalog LF digest `12bb1a9d2476e4b0208ff51f9296f51462395f01af8d0543ad3c7eae9f039477` at `62a8955` verified in this session.

## Code Examples

### D-03 record cross-check body (sketch)
```python
def lf_sha_bytes(b: bytes) -> str: return hashlib.sha256(lf_bytes(b)).hexdigest()

def check_publication_record(a: dict, pre_publication: bool = False) -> None:
    if not PUBLICATION_RECORD.exists(): raise AuthorityError('publication record is absent')
    record = load(PUBLICATION_RECORD)
    keys = {'publication_commit','authority_id','version','authority_sha256','manifest_sha256','digest_normalisation'}
    if not isinstance(record, dict) or set(record) != keys: raise AuthorityError(f'publication record keys must be exactly {sorted(keys)}')
    want = SUPERSEDED_V2_0_0 if pre_publication else {'authority_id': a['authority_id'], 'version': a['version']}
    if record['authority_id'] != want['authority_id'] or record['version'] != want['version']:
        raise AuthorityError('publication record names a different authority')
    commit = record['publication_commit']          # git_show validates the SHA shape
    if lf_sha_bytes(git_show(commit, rel(AUTHORITY))) != record['authority_sha256']: raise AuthorityError('publication record authority_sha256 does not match the publication commit')
    if lf_sha_bytes(git_show(commit, f'{rel(OUT)}/{N_MANIFEST}')) != record['manifest_sha256']: raise AuthorityError('publication record manifest_sha256 does not match the publication commit')
    if not pre_publication:
        if record['authority_sha256'] != lf_digest(AUTHORITY): raise AuthorityError('publication record authority_sha256 does not match the committed authority')
        if record['manifest_sha256'] != lf_digest(OUT / N_MANIFEST): raise AuthorityError('publication record manifest_sha256 does not match the committed manifest')
```
Keep the existing message wording where tests `match=key`. The planner may order the live-file comparison first so that `match='authority_sha256'` tests still hit that message.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Record check skipped on absent/other record | Record required, commit-verified | Phase 8 | Closes 06-REVIEW WR-02 |
| Live catalog read in `--validate` | Catalog from pinned commit | Phase 8 | Edits to the shared catalog no longer flip the gate |
| Open schema | `additionalProperties:false` x3 | Phase 8 | Strict negative invariants |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `additionalProperties` ignores properties declared only inside `allOf/then` subschemas (standard JSON Schema 2020-12) | SCHEMA-07 | If wrong, row `then` branches need no duplication; low risk. Verified indirectly: the row `properties` list is complete, so tests will catch it |
| A2 | Phase 9 will bump `VERSION` to 2.0.2 and set `SUPERSEDED` to the 2.0.1 entry, so `--pre-publication` will see a record naming `SUPERSEDED` | GATE-01 | If constants differ, adjust the `want` selection; the flag logic itself is unaffected |

## Open Questions

1. **GATE-05 versus the committed answers (BLOCKER for the plan, needs user decision).**
   - What we know: probe this session shows the 21 notes in `registry/archive_assessment_governance_answers.json` (and the copied `note` in `registry/archive_assessment_governance_decisions.json`) are identical after `norm_templated`: for example `009-Frozen nature of snapshot can not be expressed in fields available`, `010-Frozen ...`. With a `norm_templated` uniqueness check 20 of 21 are flagged. The path `build_decisions` -> `validate_answers(strict=True)` (L208) is used by `--build` and by `--validate` (which rebuilds via `build_from_files`, CI step "Archive-assessment validators"). `tests/test_archive_assessment_governance_answers.py::test_committed_answers_strict_when_filled` (L58) also validates the real file strictly. Test fixtures `filled()` (`tests/test_archive_assessment_governance_answers.py` L34, decisions tests) also generate per-control notes with a control id and would also collide.
   - What's unclear: the intended behaviour for the committed answers. The answers are typed by the authority and feed `answers_sha256` in the decisions file, so editing them changes the decisions and violates output neutrality and PUB-08.
   - Recommendation: ask the user to pick one: (a) grandfather: the templated-duplicate check applies, but is skipped when the answers file digest equals the certified `answers_sha256` recorded in the committed decisions (small constant, explicit, documented); (b) apply the check only to newly added or changed entries (entries beyond the 21, or a `--lenient` style flag); (c) accept that the real answers must be reworded by Oscar Mack (changes decisions, out of scope). Do not plan GATE-05 implementation until one is chosen. The other five requirements are unaffected.

2. **`catalog_reference.commit` in the 2.0.1 committed authority.** The committed schema/authority lack it; this is already red-window territory. No action beyond awareness.

3. **Pre-publication mode with the real record before Phase 9.** Expected not to pass inside the window (see Pitfall 6). Confirm the plan lists no real-CLI-green gate for it.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 + pytest + jsonschema + PyYAML | all tests | yes (venv in use by project) | per project | none needed |
| git (full, non-shallow clone) | GATE-01/03/04 tests with real repo | yes; `git rev-parse --is-shallow-repository` -> `false` on this machine | - | tests skip via `git_ready()` pattern where they depend on real history |
| Commit `62a8955...` in local history | catalog pin | yes (resolves; digest verified) | - | none; fail closed |

No missing blocking dependency.

## Validation Architecture

(`workflow.nyquist_validation` is `false` in `.planning/config.json`, but the request asks for this section, so it is included.)

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (project `requirements-dev.txt`) |
| Config file | none (CI runs `python -m pytest tests -k archive_assessment -p no:cacheprovider -q`) |
| Quick run command | `.\.venv\Scripts\python.exe -m pytest tests -k archive_assessment -p no:cacheprovider -q --basetemp=.pytest-temp/p8` |
| Full suite command | same (the whole archive-assessment suite is the unit of regression) |

Baseline recorded in Phase 7 summary: 499 passed, 3 failed (the accepted red set: `test_committed_schema_equals_schema_function`, `test_real_published_files_validate`, `tests/test_archive_assessment_demo3_w1_req_001_reply.py::test_publisher_still_valid_and_digest_matches_manifest`) plus CLI `--validate`.

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Proposed test (file) | File Exists? |
|--------|----------|-----------|----------------------|--------------|
| GATE-01 | absent record -> `AuthorityError` (plain) | unit, `env` | new in `tests/test_archive_assessment_applicability_authority_v2_publication.py`; replaces `test_validate_record_absent_passes` L447 | edit |
| GATE-01 | record naming other authority -> fails plain; passes `pre_publication=True` only if it names `SUPERSEDED_V2_0_0` with its digests/commit; 9.9.9 fails in both | unit, `env` + fake git | replaces `test_validate_record_other_authority_id_is_pending` L457 | edit |
| GATE-01 | matching record passes; digest mismatch fails (`match=key`) | unit | edit L452, L466 to supply fake `git_show` | edit |
| GATE-01/D-03 | `publication_commit` whose blob digest differs -> fails; unreachable commit -> fails closed | unit with temp git repo (reuse `fx` pattern) | new | new |
| GATE-01 | `--pre-publication` without `--validate` -> parser error; CLI wiring | unit via `monkeypatch sys.argv` | new | new |
| GATE-02 | non-domain exception from validator (monkeypatch `validate_publication` to raise `KeyError`, `TypeError`, `AttributeError`) propagates out of `mutation_gates`, for AUTHORITY, SIGNOFF and DECISIONS targets | unit | new, parametrized | new |
| GATE-02 | `run_mutations` / `publish` aborts (does not count rejection) on non-domain exception; nothing written | unit, `env` | mirror `test_accepted_mutation_aborts_build_and_writes_nothing` L665 | new |
| GATE-02/D-05 | every mutation's Python rejection is `AuthorityError`/`ValueError` | unit | extend `test_each_mutation_is_rejected_by_its_gates` L644 with a direct validator call asserting exception class | edit |
| GATE-03 | editing live `registry/control_catalog.yaml` in a scratch copy does not change build or validate result | unit, temp git repo with `ROOT` patched; scratch catalog edited but pinned commit unchanged | new | new |
| GATE-03 | tamper pinned reference (commit, relative_path, sha256 of `catalog_reference`) -> `validate_lineage`/`validate_publication` fail | unit | extend lineage `fx` tests; add to `tests/test_archive_assessment_applicability_authority_v2.py` schema tests (`commit` const) | edit/new |
| GATE-03 | missing history / unknown commit -> fails closed (no skip) | unit | `test_d10_nonexistent_commit_raises` pattern for `catalog_reference` | new |
| GATE-04 | `rev-parse` returns `true` -> `AuthorityError` containing "shallow"; nonzero exit -> `AuthorityError`; `OSError` -> `AuthorityError`; `false` -> proceeds to log lookup | unit, `monkeypatch.setattr(MODULE,'git',fake)` (pattern at reply tests L260-298) | new in `tests/test_archive_assessment_demo3_w1_req_001_reply.py` | new |
| GATE-04 | output neutrality | existing real-file reply tests (`test_record_commit_is_last_change_of_the_record` L332) stay green on a full clone | - | exists |
| GATE-05 | two notes differing only by control id/digits -> strict validation raises "repeats the note of" | unit with synthetic answers (`filled()` fixture variant) | new in `tests/test_archive_assessment_governance_answers.py` | new (after Q1) |
| GATE-05 | output neutrality | real-answers strict test and decisions rebuild stay green | `test_committed_answers_strict_when_filled` L58; CI `--validate` | exists (blocked by Q1) |
| SCHEMA-07 | extra field at top level, on a control row, and in `not_applicable_semantics` each fails `jsonschema` validation | unit | new, parametrized | new |
| SCHEMA-07 | real/built authority still validates; every built key is declared at the three levels | unit | new | new |
| SCHEMA-07 | negative-invariant records each new mutation with `'SCHEMA'` in `rejected_by`; counts 29 | unit | edit L633-638 and L699; `test_run_mutations_outcomes_shape` L657 still valid | edit |

### Tests that depend on certified real files (red-window relevant)
- Accepted red today (do not count against Phase 8): `test_committed_schema_equals_schema_function` (`tests/test_archive_assessment_applicability_authority_v2.py` L174), `test_real_published_files_validate` (publication test L491-502), `test_publisher_still_valid_and_digest_matches_manifest` (reply tests).
- Read real files but pass today and must stay green (they call `build()` / `build_published_authority()` or real git history): `test_lineage_records_governance_decisions_and_v1` L68, `test_rows_equal_2_0_0_rows_and_only_identity_and_lineage_differ` L572, `test_superseded_constants_match_git_history` L558, `test_publication_commit_ancestor_and_file_set` L517 and `test_manifest_publisher_script_digest_matches_publication_commit` L541 (these use the real record and real git; skip when shallow), `test_real_lineage_*` and `test_real_aa1_manifest_tampered_digest_raises` (lineage tests L263-285), reply tests L321-345 and `test_committed_answers_*` (governance answers). Any new test that expects new behaviour on the real committed 2.0.1 files (for example "real record matches current authority") must be named in the plan's expected red set; prefer synthetic tests under `env` or a temp git repo so the red set does not grow.
- Tests independent of certified files (must pass): everything using `env`, `fx`, `mutated(...)` on a freshly built document, and the pure-function tests.

### Sampling Rate
- Per task commit: the specific test files touched (for example `tests/test_archive_assessment_applicability_authority_v2_publication.py`).
- Per wave merge: whole `-k archive_assessment` suite; confirm failed set is exactly the 3-test red set above.
- Phase gate: same, plus `git diff --stat` shows no change to `registry/`, `schemas/`, `generated/` or `VERSION`.

### Wave 0 Gaps
- [ ] `env` fixture: stub `catalog_bytes` and `git_show` for record cross-check (shared by all `env` tests).
- [ ] Lineage `fx` fixture: `catalog_reference` entry with commit.
- [ ] Decide Q1 before writing GATE-05 tests.

## Security Domain

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | shape checks before key access; `git_show` rejects non-SHA commits and `..`/absolute paths (command-injection and path-traversal guard already present, tested by `test_d10_option_like_commit_rejected_before_subprocess` L195 and `test_wr03_...` L241) |
| V6 Cryptography | yes | SHA-256 via `hashlib`; never hand-roll |
| V2/V3/V4 | no | no authentication or sessions |

| Threat | STRIDE | Mitigation |
|--------|--------|-----------|
| Tampered record naming other authority passes silently | Tampering | GATE-01 required, exact match |
| Live catalog edit alters gate result | Tampering | pinned commit blob, tamper tests |
| Record points at commit not containing the bytes | Spoofing | D-03 `git_show` digest check |
| Git option injection through record `publication_commit` | Tampering/EoP | `git_show` regex `[0-9a-f]{40}` precheck (already present; record commit flows through it) |

## Sources

### Primary (HIGH confidence, read or executed this session)
- `scripts/publish_archive_assessment_applicability_authority_v2.py` (full read, L1-703)
- `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` (L1-100, L245-285)
- `scripts/build_archive_assessment_governance_decisions.py` (L60-215, grep of `norm`, `note`, `AuthorityError`, main)
- `scripts/validate_archive_assessment_rule_proposals.py` (`frozen_catalog` L78-90)
- Tests: `tests/test_archive_assessment_applicability_authority_v2_publication.py`, `tests/test_archive_assessment_lineage_validation.py`, `tests/test_archive_assessment_applicability_authority_v2.py` (selected), `tests/test_archive_assessment_demo3_w1_req_001_reply.py` (L260-345), `tests/test_archive_assessment_governance_answers.py` (L36-62)
- `.github/workflows/ems-validate.yml` L70-96 (`fetch-depth: 0`, validator commands)
- Probes: mutation exception classes (all 26 domain), schema vs built-document property diff, `norm_templated` collision on committed answers, catalog digest at `62a8955`, `git rev-parse --is-shallow-repository` = false
- `.planning/phases/03-governance-decisions/03-REVIEW.md` WR-01 (intent of GATE-05), `.planning/ROADMAP.md` red-window text, Phase 7 summaries (red set)

### Secondary / Tertiary
- None. JSON Schema `additionalProperties` semantics are standard (A1) and covered by the test plan.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH (no new dependencies)
- Architecture and code locations: HIGH (read directly)
- Pitfalls: HIGH for fixtures/schema/catalog; GATE-05 data conflict verified by probe
- Pre-publication semantics before Phase 9 constants change: MEDIUM (A2)

**Research date:** 2026-11-11
**Valid until:** until the next edit to the three scripts (line numbers); otherwise 30 days
