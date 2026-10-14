---
phase: 03-governance-decisions
reviewed: 2026-10-14T16:54:54Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - scripts/build_archive_assessment_governance_decisions.py
  - tests/test_archive_assessment_governance_answers.py
  - tests/test_archive_assessment_governance_decisions.py
  - schemas/archive_assessment_governance_answers.schema.json
  - schemas/archive_assessment_governance_decisions.schema.json
findings:
  critical: 3
  warning: 9
  info: 5
  total: 17
status: issues_found
---

# Phase 3: Code Review Report

**Reviewed:** 2026-10-14T16:54:54Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Narrative Findings (AI reviewer)

## Summary

I reviewed the governance answers and decisions builder and validator, its two emitted schemas, and the two test modules. I also checked the helpers it imports from `scripts/publish_archive_assessment_applicability_authority_v2.py`. Each finding below was reproduced, either with a probe script against the live module or with a fresh `git clone` of HEAD (966d3a3) on this machine (`core.autocrlf=true`, no `.gitattributes`). This review does not assess the content of the committed answers or decisions.

There are three blocking problems:

1. **Line endings change the hashes.** The frozen-input hashes are computed from the raw file bytes. On a fresh Windows clone, `--validate` fails and 6 of the 99 tests fail.
2. **`--validate` doesn't check the decisions against the answers file.** `answers_sha256` is only checked for format. A hand-edited record that is internally consistent passes.
3. **Superseding answer entries skip strict validation.** The builder then silently drops answer fields that conflict with the disposition, so a record can say something different from the answers it was built from.

The note-uniqueness guard (D-04) also accepts templated notes that differ only by control id. The test fixture that "passes strict" is itself one of these.

## Critical Issues

### CR-01: Frozen-input digests use raw bytes, so validation fails on a CRLF checkout

**File:** `scripts/build_archive_assessment_governance_decisions.py:204, 223-225` (also `tests/test_archive_assessment_governance_answers.py:66-70, 200-202`)
**Issue:** `answers_sha256` is CRLF-normalised (line 71, threat T-03-16), but the other two hashes are not:
- `proposals_sha256` and `drafting_record_sha256` are checked against `V2.digest()`, which hashes the raw bytes.
- The builder records `drafting_record_sha256` from raw bytes too.

The repository has `core.autocrlf=true` and no `.gitattributes`. In the current working tree, the proposals file and the drafting record happen to be `w/lf`. A fresh clone checks them out as `w/crlf` (confirmed with `git ls-files --eol` in the clone). Running from that clone at HEAD:

```
$ python scripts/build_archive_assessment_governance_decisions.py --validate
AuthorityError: proposals_sha256 does not match the live file; drafting_record_sha256 does not match the live file
6 failed, 93 passed  (test_view_byte_identical_and_equals_disk, test_frozen_inputs_hash_matches_drafting_record,
  test_build_validates_and_schema_passes, test_supersession_keeps_old_and_validates,
  test_drafting_record_and_frozen_inputs_unchanged, test_real_decisions_file_valid_and_reproducible)
```

Windows is the primary platform, and Hayes reads EMS at a pinned commit. So an independent checkout on Windows cannot reproduce the validation. The committed `drafting_record_sha256` also depends on how the builder's checkout happened to store the file.

**Fix:** Hash every input the same way and pin line endings in git.
```python
def lf_digest(path: Path) -> str: return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
# build_decisions: 'drafting_record_sha256': drafting_record_sha256 if ... else lf_digest(DRAFTING_RECORD)
# validate_decisions: for k, live in (('proposals_sha256', lf_digest(PROPOSALS)), ('drafting_record_sha256', lf_digest(DRAFTING_RECORD))):
```
Also add a `.gitattributes` with `registry/*.json text eol=lf` and `docs/ARCHIVE_ASSESSMENT_RULE_PROPOSALS_VIEW.md text eol=lf`, commit it by explicit path, and record a normalisation field for these hashes the same way `answers_sha256_normalisation` does. The view test should compare `lf(bytes)`.

### CR-02: `validate_decisions` doesn't check the decisions against the answers file

**File:** `scripts/build_archive_assessment_governance_decisions.py:226-227, 335-338`
**Issue:** `answers_sha256` is only checked against `SHA64_RE`. `validate_decisions` never reads the answers file and never compares the records with it. The CLI `--validate` is the operator gate and the validator that Phase 4 will rely on, and it accepts both of these (probe output):
- `answers_sha256 = 'f'*64`: ACCEPTED.
- A hand edit of `AA4-GOV-001` from `APPROVED_AS_DRAFTED` to `CHANGED`, with a new two-sentence rationale and `amendment_present=True`: ACCEPTED.

So a decision record can differ from what the authority typed and still pass. Only the pytest `test_real_decisions_file_valid_and_reproducible` would catch it, and the CLI never runs that test. Because of this gap, "EMS decided" cannot be traced to the authority's answers with the validator alone.
**Fix:** In `validate_decisions`, when it is checking the live file, compare `d['answers_sha256']` with `answers_digest(ANSWERS)`. Then require the rebuild to be identical:
```python
if d.get('answers_sha256') != answers_digest(ANSWERS): errors.append('answers_sha256 does not match the live answers file')
...
# in main --validate:
if decisions_text(doc) != decisions_text(build_from_files()): raise AuthorityError('decisions file differs from a fresh build of the committed answers')
```
Add a test that changes `answers_sha256`, and one that edits a record consistently, and expect both to fail.

### CR-03: Superseding answer entries skip strict validation, and the builder drops conflicting answer fields

**File:** `scripts/build_archive_assessment_governance_decisions.py:111, 124, 127-160, 188-200`
**Issue:** `strict_checks` runs only on `first = entries[:21]`. `build_decisions` turns every entry into a record, including entries 22 and later. For a superseding entry (the D-12 change-of-mind path), none of these checks run:
- disposition required
- note rules (min length, uniqueness, not a copy of drafted text)
- calendar `decided_on`
- `decided_rule`/`decided_rationale` consistency with the disposition
- `scope_note_ruling` placement

The builder then ignores fields that conflict with the disposition:
- With `APPROVED_AS_DRAFTED`, it copies the drafted side and discards the typed `decided_rule` and `decided_rationale` (line 191).
- On a control with no scope note, it discards a typed `scope_note_ruling` (line 193).

Probe: one superseding entry with `supersedes='AA4-GOV-001'`, `APPROVED_AS_DRAFTED`, a `decided_rule`, `decided_rationale='x'`, a scope ruling on 009 and `decided_on='2026-99-99'`. It passes `validate_answers(strict=True)`, `build_decisions` and `validate_decisions`. The record `AA4-GOV-022` has `decided.rule=None` and `scope_note=None`, unlike the answer. Separately, a fully blank superseding entry (`disposition=None`, `note=''`) gets "PASS" from `--validate-answers`. The builder exists so that records match the answers exactly, and this breaks that for every future supersession.
**Fix:** Run strict checks on every entry, not only the first 21. Keep the order and uniqueness check on the first 21.
```python
if strict and not errors: strict_checks(entries, proposals, errors)
```
`strict_checks` already handles any control id through `by_id`. Note uniqueness then covers all entries. Optionally allow a superseding note to differ only from notes of other controls. Also make `build_decisions` refuse (raise) instead of ignoring fields that conflict with the disposition, so it doesn't depend on the caller having validated.

## Warnings

### WR-01: The copy-paste guard (D-04) accepts templated notes

**File:** `scripts/build_archive_assessment_governance_decisions.py:133-139`
**Issue:** Notes count as identical only after whitespace and case normalisation. Twenty-one notes like `f'Approved {c} as drafted after review.'` pass strict validation (probe: ACCEPTED). The test fixture `filled()` in `tests/test_archive_assessment_governance_answers.py:34` (`f'Reviewed {c} individually and kept the draft.'`) is also a generated blanket approval that passes. CONTEXT accepted exact match as the minimum, but the stated purpose ("18 approvals of no-rule drafts cannot amount to a blanket approval") is not met against a scripted fill. Notes are also compared only with `rationale` and `interpretation.text`, not with `alternative_considered`, `shape_limitation.note` or `catalog_inputs`.
**Fix:** Before comparing, remove control ids and digits (`re.sub(r'ems-ctrl-\d{3}|\d+', '', norm(n))`). Compare against every drafted string of the proposal (reuse `leaves()` from the test). Add a test asserting that notes differing only by control id fail.

### WR-02: The first 21 entries can carry `supersedes`, so `--validate-answers` passes but `--build` fails

**File:** `scripts/build_archive_assessment_governance_decisions.py:122, 141-160`
**Issue:** Line 122 only checks the pattern. Setting `entries[3].supersedes='AA4-GOV-001'` passes strict validation (probe: ACCEPTED), but `validate_decisions` then rejects it because the record supersedes another control. The two validators disagree about the same input.
**Fix:** In `validate_answers`, require `supersedes is None` for `i < 21`. For `i >= 21`, require that `supersedes` names an earlier position (`int(sup[-3:]) <= i`) for the same `control_id`.

### WR-03: An extra entry with an unknown `control_id` crashes the build with `KeyError`

**File:** `scripts/build_archive_assessment_governance_decisions.py:114-122, 189, 314-316`
**Issue:** `validate_answers` never checks `control_id` for entries beyond 21, and `build_from_files` / `--build` never run the answers schema. Probe: an extra entry for `EMS-CTRL-001` with a valid `supersedes` gives `KeyError: 'EMS-CTRL-001'` instead of `AuthorityError`. It does fail closed, but it breaks the error contract and gives a confusing message.
**Fix:** In `validate_answers`: `if cid not in CONTROL_IDS: errors.append(f'entry {i}: unknown control {cid}')`. Also run `jsonschema.Draft202012Validator(answers_schema()).validate(a)` inside `build_from_files`.

### WR-04: `decided_on` is not checked as a real date

**File:** `scripts/build_archive_assessment_governance_decisions.py:62, 140, 254`
**Issue:** `DATE_RE` checks only the shape. `2026-02-31` and `2026-99-99` pass strict validation, `validate_decisions` and both schemas (probe: ACCEPTED). The decision date is part of the governance record that gets cited.
**Fix:** `def is_date(s): try: return bool(re.match(DATE_RE, s)) and date.fromisoformat(s) is not None except ValueError: return False`. Use it in both validators.

### WR-05: The `wording_approval` header is only partly checked against the approval file

**File:** `scripts/build_archive_assessment_governance_decisions.py:217-222`
**Issue:** Only `approver` and `statement_sha256` are checked. `role`, `date`, `scope` and `source_path` can be changed by hand (probe: `scope='forged'`, `date='1999-01-01'` ACCEPTED). The builder copies these from `WORDING_APPROVAL`, but the validator never reads that file.
**Fix:** Load `WORDING_APPROVAL` in `validate_decisions` and require `wa == {**approval['approval'] subset, 'source_path': APPROVAL_REL, 'statement_sha256': approval['statement_sha256']}`. The fields should match exactly what `build_decisions` writes.

### WR-06: `validate_decisions` raises raw Python errors on malformed types

**File:** `scripts/build_archive_assessment_governance_decisions.py:67, 77-79, 244, 266-271`
**Issue:**
- A non-string `decided.rationale` that reaches the `CHANGED` branch calls `norm(5)` and raises `AttributeError: 'int' object has no attribute 'casefold'` (reproduced).
- An unhashable `control_id` (list) or condition `field` raises `TypeError` in `cid not in by_id` / `pairs()`.

`--validate` runs `validate_decisions` before the schema, so the schema can't catch these first. This breaks the "raise `AuthorityError` on any violated invariant" convention.
**Fix:** Check types before use (`if not isinstance(de['rationale'], str): errors.append(...); continue`). Make `pairs()` skip non-string field/state values. Or run the schema check first and turn `ValidationError` into `AuthorityError`.

### WR-07: `--build` can't add a superseding record without deleting the frozen file

**File:** `scripts/build_archive_assessment_governance_decisions.py:330-334`
**Issue:** `--build` refuses whenever the existing decisions file differs from the rebuild. Under D-12, a superseding answer entry always produces a different file (the 21 existing records plus new ones). The only way through is to delete the committed decisions file by hand, which removes the protection the refusal is meant to give.
**Fix:** Allow appending only. Load the existing file and require `existing['records'] == doc['records'][:len(existing['records'])]`, with the other header fields equal apart from `answers_sha256`. Then write. Refuse every other difference.

### WR-08: Decisions file and schemas are written with platform newlines

**File:** `scripts/build_archive_assessment_governance_decisions.py:328-333` (through `V2.dump`, which uses `write_text` without `newline='\n'`)
**Issue:** On Windows, `V2.dump` writes CRLF. The working-tree decisions file has 867 CRs, the schemas are also written by `dump`, and the view uses `newline='\n'` (line 325). The bytes on disk depend on the OS. That conflicts with the deterministic-output convention and makes CR-01 worse: any future raw-byte digest of the decisions file depends on the writer's OS.
**Fix:** Write the files locally with `open(p, 'w', encoding='utf-8', newline='\n')` (as `--view` does), and pin with `.gitattributes` (see CR-01).

### WR-09: The tests don't cover answers-to-record fidelity or the gaps above

**File:** `tests/test_archive_assessment_governance_decisions.py:141-154`, `tests/test_archive_assessment_governance_answers.py:158-162, 172-174`
**Issue:**
- No test asserts that each record's `note`, `decided_on`, `supersedes`, `scope_note.ruling`, `decided.rule` and `decided.rationale` equal the source answer entry. The record-shape test checks layout only, so a builder that mixed up fields between controls would pass.
- No test covers an `answers_sha256` mismatch (CR-02).
- The only superseding-entry test (`test_superseding_entry_needs_reference`) runs lenient mode and copies a valid entry, so CR-03 is untested.
- `test_blank_template_is_blank_and_not_overwritten` never runs `--emit-template` against an existing file.
- The view and hash tests depend on how the files were checked out (CR-01).

**Fix:** Add a fidelity test (`for e, r in zip(answers['entries'], d['records']): assert r['note'] == e['note'] ...`). Add strict-mode superseding-entry tests (blank, `APPROVED`+rule, misplaced ruling, unknown control). Add an `answers_sha256` mismatch test, and a subprocess test that runs `--emit-template` in a temp copy of the file and expects a refusal.

## Info

### IN-01: Dead assignment in `test_changed_equal_to_drafted_rejected`

**File:** `tests/test_archive_assessment_governance_decisions.py:114-115`
**Issue:** Line 114 builds `r['decided']` with a changed rationale, and line 115 immediately overwrites it. The test passes, but line 114 is dead and confusing.
**Fix:** Delete line 114.

### IN-02: `sentences_ok` miscounts abbreviations

**File:** `scripts/build_archive_assessment_governance_decisions.py:69`
**Issue:** `[.!?](\s|$)` counts "e.g. ", "i.e. " and "etc. " as sentence ends. That can wrongly reject a valid 4-sentence rationale typed by the authority, or let a 1-sentence one with an abbreviation count as two.
**Fix:** Document the heuristic in the error message, or remove common abbreviations before counting.

### IN-03: Test names promise more than they assert

**File:** `tests/test_archive_assessment_governance_answers.py:117, 172`
**Issue:** `test_duplicate_control_fails_validator_only` never asserts that the schema accepts the input. `test_blank_template_is_blank_and_not_overwritten` never tests the no-overwrite behaviour.
**Fix:** Add the missing assertions, or rename the tests.

### IN-04: `validate_decisions` mixes the proposals passed in with the live digest

**File:** `scripts/build_archive_assessment_governance_decisions.py:210-212, 223`
**Issue:** `by_id` comes from the `proposals` argument, but the digest check always reads the live `PROPOSALS` file. A caller that passes different proposals gets records checked against one source and the hash checked against another.
**Fix:** Either drop the parameters, or digest the same bytes the dict was loaded from.

### IN-05: Test helpers are duplicated across both test modules

**File:** `tests/test_archive_assessment_governance_answers.py:12-48`, `tests/test_archive_assessment_governance_decisions.py:12-60`
**Issue:** `TERMS`, `scan`, `rule`, `filled`, `ent` and `load` are copied in both modules. The D-19 term list can drift between the two scans.
**Fix:** Move them into a shared `tests/_aa_governance_helpers.py` or a `conftest.py` fixture.

---

_Reviewed: 2026-10-14T16:54:54Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
