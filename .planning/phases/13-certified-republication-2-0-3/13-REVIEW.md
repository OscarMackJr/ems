---
phase: 13-certified-republication-2-0-3
reviewed: 2026-11-17T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - tests/test_archive_assessment_lineage_validation.py
  - registry/archive_assessment_applicability_authority_v2_signoff.json
  - registry/archive_assessment_applicability_authority_v2_publication_record.json
  - schemas/archive_assessment_applicability_authority_v2.schema.json
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: issues_found
---

# Phase 13: Code Review Report

**Reviewed:** 2026-11-17
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Narrative Findings (AI reviewer)

## Summary

Diff range reviewed: `git diff 5995192 5498002`. I checked these facts directly:

- The authority at `1544dc1` and at `5498002` hashes to LF sha256 `696116e765111c6f15237d876a9aca27f830c756707ee9c4b5e251d03aa0e0a6`. That matches `authority_sha256` in both the sign-off and the publication record.
- `publication_commit` `1544dc19ba235d732c832d1651895550ed5a265d` resolves to `feat(13-02): publish ... 2.0.3`.
- The schema's `supersedes.commit` `ae15c74...` resolves to `feat(09-04): publish ... 2.0.2`. Its `authority_id` and `version` consts (2.0.3 at the top level, 2.0.2 for supersedes) match `VERSION` and `SUPERSEDED_V2_0_2` in the publisher.
- The sign-off's `scope` text names the correct digest and the correct superseded commit. Its `dual_role_statement` matches `DUAL_ROLE_STATEMENT` exactly.

The 2.0.3 registry artifacts are internally consistent. No finding requires changing them for 2.0.3 to be valid.

The one hand-written change, the WR-03 baseline assertion, fixes the vacuous-pass problem. But it hard-codes plain `--validate`, and that mode fails by design at every future publication commit. The schema finding below is pre-existing and would need a certified republication to fix.

## Warnings

### WR-01: The D-10 baseline assertion will fail at the next publication commit (the commit Hayes pins)

**File:** `tests/test_archive_assessment_lineage_validation.py:371`
**Issue:** `test_d10_live_catalog_edit_or_delete_does_not_change_validate_outcome` clones the committed `HEAD` of `REAL_ROOT`. It runs plain `--validate` there and now asserts `before == (0, 'PASS')`.

Publication happens in two commits: first the publication commit, then the record commit. At the publication commit, the record still names the superseded version. `check_publication_record` (publisher lines 839-840) then deliberately raises "publication record still names the superseded ... run --validate --at-pin here". So for 2.0.4 or any later republication, this test is red at the publication commit. That is the exact commit Hayes re-pins to and the commit `--validate --at-pin` exists to certify. The assertion only holds today because it was added in `5498002`, after record commit `87a46d1`.

Before WR-03, the test passed vacuously at the pin commit (FAIL == FAIL). Now it fails outright, and the publication runbook needs a red test suite at the pin commit. It also means the test no longer works as a regression guard during the pin-commit validation step.
**Fix:** Choose the mode to match the state of the clone, and accept either PASS form.
```python
def outcome(at_pin):
    args = [sys.executable, 'scripts/publish_archive_assessment_applicability_authority_v2.py', '--validate'] + (['--at-pin'] if at_pin else [])
    ...
rec = json.loads((clone / MODULE.rel(MODULE.PUBLICATION_RECORD)).read_text(encoding='utf-8'))
at_pin = rec['version'] == MODULE.SUPERSEDED_V2_0_2['version']
before = outcome(at_pin)
assert before[0] == 0 and (before[1] == 'PASS' or json.loads(before[1]).get('status') == 'PASS'), ...
```
Or document in the publication runbook that this test is expected to fail between the publication and record commits, and run the at-pin path in a dedicated test.

### WR-02: The published schema does not pin the superseded 2.0.2 digests (fixing it forces a republication)

**File:** `schemas/archive_assessment_applicability_authority_v2.schema.json:835-846`
**Issue:** In `source_lineage.supersedes`, the schema pins `authority_id`, `version`, `commit`, `relative_path` and both normalisation fields with `const`. But `sha256` and `governance_decisions_sha256` are only `pattern: ^[0-9a-f]{64}$`.

The Python validator enforces exact equality (publisher lines 251, 323, 349: `sup != SUPERSEDED_V2_0_2`). The schema is the machine-readable contract Hayes can validate against, and a consumer relying on it alone would accept any 64-hex value as "the 2.0.2 digest". That weakens the "no decision changed since 2.0.2" lineage claim at the consumer boundary. The same applies to the analogous `v1_baseline` digest fields, if they follow the same pattern.
**Fix:** In `schema()` in the publisher, emit `{"const": SUPERSEDED_V2_0_2['sha256']}` and `{"const": SUPERSEDED_V2_0_2['governance_decisions_sha256']}`. This changes the schema and the manifest digests, so it would force a certified republication (2.0.4). Defer it to the next planned republication rather than hand-editing.

## Info

### IN-01: The sign-off `scope` repeats the digest in free text that is never checked

**File:** `registry/archive_assessment_applicability_authority_v2_signoff.json:6`
**Issue:** `validate_signoff` (publisher line 620-621) only checks that `scope` is a non-empty string. The digest `696116e7...`, the version and the superseded commit `ae15c74` inside the hand-written scope text are not checked. Today they are correct; I verified them. A future hand-written sign-off could carry a stale scope while every machine check passes. Phase 13 is the second time this text has been hand-copied from a template.
**Fix:** In a future publisher revision, require the scope to contain `AUTHORITY_ID`, `VERSION`, the authority LF digest and `SUPERSEDED_V2_0_2['commit'][:7]`. That would be a publisher change and so a republication. Until then, add a pre-flight grep to the runbook.

### IN-02: The D-10 validate test checks committed HEAD, not the working tree under test

**File:** `tests/test_archive_assessment_lineage_validation.py:358-366`
**Issue:** `git clone --shared` copies `HEAD`, so uncommitted publisher or registry edits in the working tree are invisible to this test. Combined with the new PASS assertion, the result reflects the last commit, not the code being tested. A developer can get a green result here while the working tree would fail `--validate`, or the reverse. This is pre-existing design, but WR-03 makes the test's verdict depend on it.
**Fix:** Name this in the test (for example in the assertion message, "validates committed HEAD"), or copy the working-tree publication paths into the clone before running.

### IN-03: `outcome()` decodes subprocess output with the locale codec and merges stderr after stdout

**File:** `tests/test_archive_assessment_lineage_validation.py:362-365`
**Issue:** `text=True` without `encoding=` uses the Windows locale codec, cp1252 on the primary platform. A non-ASCII `AuthorityError` message, or any stray stderr line emitted after `PASS`, would make `lines[-1]` something other than `PASS`, or raise in decoding. Either way the new baseline assertion would fail for a reason unrelated to D-10.
**Fix:** Pass `encoding='utf-8', errors='replace'` and take the last line of `r.stdout` only for the PASS check. Keep stderr in the failure message.

---

_Reviewed: 2026-11-17_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
