---
phase: 09-certified-republication-2-0-2
reviewed: 2026-11-12T00:00:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
  - scripts/publish_archive_assessment_applicability_authority_v2.py
  - tests/test_archive_assessment_applicability_authority_v2.py
  - tests/test_archive_assessment_applicability_authority_v2_publication.py
  - tests/test_archive_assessment_demo3_w1_req_001_reply.py
  - tests/test_archive_assessment_lineage_validation.py
findings:
  critical: 0
  warning: 4
  info: 6
  total: 10
status: issues_found
---

# Phase 9: Code Review Report

**Reviewed:** 2026-11-12
**Depth:** standard (scope: `git diff 766062f HEAD` on the six files)
**Files Reviewed:** 6
**Status:** issues_found

## Narrative Findings (AI reviewer)

## Summary

Phase 9 changed three things:

- It moved the supersession binding from 2.0.0 to 2.0.1 (`SUPERSEDED_V2_0_1`).
- It added the D-08 row comparison with 2.0.1 (`rows_differing_from_previous`) and the D-10 "What changed" section of the sign-off summary.
- It froze the DEMO3 reply validator on 2.0.1 inputs read through `git_show`.

The supersession swap is consistent. All seven references follow the new constant: validator, schema `pinned`, mutation, pre-publication branch, dry-run summary, and the `validate_publication` digest checks. The D-08 comparison fails closed without history, because `GitHistoryError` propagates and is re-raised through `mutation_gates`.

No blocker was found. The main defect is in the frozen reply validator. `REPLY_PUBLICATION_COMMIT` is never bound to the frozen publication record. I confirmed empirically that `validate_reply()` prints PASS when the constant is changed to the record commit `4d9b7c1…` or to `b3c0411…`, the parent of `ae15c74`. This contradicts D-02 and the 09-02 plan ("tampering ... either constant (monkeypatch to a different valid commit ...) raises").

**Certification facts I checked (not assumed):**

- The publication manifest at `ae15c74` lists 9 artifacts: the schema, the authority, the sign-off and the 6 generated outputs. Its `publisher_script` entry names only `scripts/publish_archive_assessment_applicability_authority_v2.py`, with sha `f6b51cca…`. The live LF digest of the publisher equals `f6b51cca…`.
- The reply builder, `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, is **not** in the manifest. The reply JSON/MD carries no digest of the builder. Fixes limited to the reply builder or the tests do not affect certification.
- Plain `--validate` does not recompute the publisher script digest. This is by design (`publisher_script_note`; `test_script_edit_after_publication_does_not_break_validate`). An edit to the publisher is detected only by pytest `test_publisher_still_valid_and_digest_matches_manifest` (reply test file, L258-263) and by the CI run of that test. See IN-05.

## Warnings

### WR-01: Frozen reply validator does not bind `REPLY_PUBLICATION_COMMIT` to the frozen record; a wrong constant passes

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:22, 248-255, 272, 300`
**Republication required:** No. The reply builder is not in the publication manifest.
**Issue:** `load_inputs` reads the authority, sign-off, decisions and manifest at `REPLY_PUBLICATION_COMMIT`, and reads the record at `REPLY_RECORD_COMMIT`. Nothing checks `record['publication_commit'] == REPLY_PUBLICATION_COMMIT`. The only commit check is `record_commit == record['publication_commit']` (L97), which compares the record constant against the record's contents.

Any commit where the 2.0.1 publication files are byte-identical is therefore accepted. That covers every commit from `31addfa` up to `ae15c74^`, 100+ commits. I verified this by loading the module and setting the constant:

```
ACCEPTED with REPLY_PUBLICATION_COMMIT = 4d9b7c1f41df5fa7575d4653a7d54ff9cf0a192b
ACCEPTED with REPLY_PUBLICATION_COMMIT = b3c041146a5360e582b0161183414ec70059919d
```

`push_check` (L300) also uses this unbound constant. D-02 requires that "tampering with ... a constant fails it". `test_validate_rejects_tampered_constant` (tests reply L438-452) only tries `'d'*40` and `54a7fd0`, and both fail for unrelated reasons (missing blob; 2.0.0 digests differ). The reply bytes themselves stay correct, because `pin` is taken from the record. That is why this is a WARNING and not a BLOCKER.
**Fix:**
```python
def load_inputs() -> tuple:
    ...
    record = pinned_json(REPLY_RECORD_COMMIT, V2.PUBLICATION_RECORD)
    if record.get('publication_commit') != REPLY_PUBLICATION_COMMIT:
        raise V2.AuthorityError('frozen publication record does not name the frozen publication commit')
    ...
```
Also add `('REPLY_PUBLICATION_COMMIT', '4d9b7c1f41df5fa7575d4653a7d54ff9cf0a192b')` to the `test_validate_rejects_tampered_constant` parameters.

### WR-02: The "frozen" reply validation still depends on live publisher code and constants

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:15-17, 88, 102, 145, 152, 174, 199-212, 231, 236-243`
**Republication required:** No (reply builder only).
**Issue:** D-01 freezes the reply bytes at 2.0.1. The rebuild and the checks still run through the **live** publisher module `V2`:

- `V2.validate_signoff` (L88);
- `V2.DUAL_ROLE_STATEMENT` (L231);
- `V2.APPROVER_ROLES`, `V2.RULE_FIELDS`, `V2.CONDITION_STATES`, `V2.COMBINATION`, `V2.AUTHORITY_ID_RE` in `schema()` (L199-212);
- `V2.rule_text` and `V2.jtext` in `render_markdown`;
- the path constants `V2.SIGNOFF`, `V2.OUT`, `V2.N_TRACE`, `V2.N_MANIFEST`, `V2.AUTHORITY`.

`validate_reply` compares the committed `REPLY_SCHEMA` against a `schema()` built from those live constants (L268). A later publisher change (2.0.3 renaming a path, tightening the sign-off keys, editing the dual-role text) would break the frozen validator. Worse, `--emit-schema` or `--build` could silently rewrite "frozen" bytes. `test_validate_independent_of_live_version` (tests reply L423) only covers `VERSION`, `AUTHORITY_ID` and `lf_digest`.
**Fix:** Load the publisher as it was at `REPLY_PUBLICATION_COMMIT`, for example by exec'ing `V2.git_show(REPLY_PUBLICATION_COMMIT, 'scripts/publish_archive_assessment_applicability_authority_v2.py')` into a module object, and use it for every 2.0.1-semantics call. Alternatively, snapshot the needed constants and paths as literals in the reply script, and refuse `--build` and `--emit-schema` (exit with an error) now that the reply is frozen.

### WR-03: The D-10 "What changed" section omits content required by D-10 and 09-03

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:573-576`
**Republication required:** Yes, if fixed in the publisher, because the script digest `f6b51cca…` is recorded in the manifest at `ae15c74`. A republication is not recommended for this. Put the missing statement in the Phase 10 notice and in `09-VERIFICATION.md`.
**Issue:** D-10 and the 09-03 must-have require "each lineage entry with its declared normalisation (AA1 manifest committed, RAW_BYTES)". The loop prints only `lineage {label}: {relative_path} ({normalisation})`. It does not state that the AA1 manifest is committed, and it prints no commit pins (`catalog_reference`, `supersedes`, `v1_baseline`). The supersedes entry has two declared normalisations, but only the authority one is printed; `governance_decisions_normalisation` / `supersedes_governance_decisions` is not listed. The signed summary is therefore less complete than the decision record specifies. The dry-run test (publication test L791+) asserts only what the code emits, so it did not catch the gap.
**Fix (for a future version):**
```python
for label, e in authority['source_lineage'].items():
    if isinstance(e, dict) and 'relative_path' in e:
        pin = f", commit {e['commit'][:7]}" if e.get('commit') else (', committed working-tree file' if label in ('aa1_manifest', 'aa2_closure', 'aa2_approval') else '')
        lines.append(f"  lineage {label}: {e['relative_path']} ({e.get('normalisation')}{pin})")
        if 'governance_decisions_normalisation' in e: lines.append(f"  lineage {label} governance decisions: {e['governance_decisions_relative_path']} ({e['governance_decisions_normalisation']})")
```
For 2.0.2, record the AA1 "committed, RAW_BYTES" statement in the Phase 10 notice.

### WR-04: The PUB-08 evidence tests skip silently when the 2.0.1 blob is unreachable

**File:** `tests/test_archive_assessment_applicability_authority_v2_publication.py:214-218, 230, 388-389, 1017-1023`
**Republication required:** No (test only).
**Issue:** `prev_201_authority_bytes()` calls `pytest.skip` when `31addfa` cannot be read. The `env` and `fake_git_show` fixtures and `test_built_rows_equal_2_0_1_rows_on_the_four_decision_fields` all call it. Consider a full clone of a branch that has `62a8955` (the catalog commit) but not the feature-branch commit `31addfa`, for example `main` before the merge. In that clone, `real_catalog` succeeds and every `env`-based test plus the D-08 equality test reports SKIPPED instead of failing. The publisher itself fails closed on missing history, but the test evidence for PUB-08 fails open. The CI job runs pytest `-k archive_assessment`, and skips do not turn it red.
**Fix:** Fail instead of skip for the history that PUB-08 requires, or count skips as failures in CI:
```python
if r.returncode != 0: pytest.fail('2.0.1 authority blob is not reachable; PUB-08 cannot be evidenced (fetch full history)')
```

## Info

### IN-01: The dry-run text says "No decision changed" without condition, and the DIFFER branch cannot be reached

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:568-571`
**Issue:** The supersedes line always begins "No decision changed:", even when `same == 'DIFFERS FROM'`. The new `same_rows` DIFFER branch (L571) can never run, because `publish(True)` reaches `dry_run_summary` only after `published_authority_checked()`, and that has already raised on any row difference. This is dead code that looks like a reporting path. Fixing it requires republication, so defer it to the next version.
**Fix:** Drop the unreachable branches, or make the leading clause depend on the condition.

### IN-02: `test_superseded_constants_match_git_history` no longer checks any module constant for 2.0.0

**File:** `tests/test_archive_assessment_applicability_authority_v2_publication.py:703-715`
**Issue:** `sup` is now a literal dict in the test. Apart from `V1_BASELINE_COMMIT`, the test checks git history against its own literals and says nothing about the publisher. Keeping it was the stated preference (Claude's discretion in 09-CONTEXT). Its name now overstates what it checks.
**Fix:** Rename it, for example `test_2_0_0_anchor_literals_match_git_history`. Optionally assert that the 2.0.1 authority's own `source_lineage.supersedes` equals this dict, which would prove the 2.0.1 → 2.0.0 chain that D-07 relies on.

### IN-03: Dead `log` handling remains in the reply test helper

**File:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py:360-374, 393-397`
**Issue:** `fake_shallow_git` still accepts `log_sha` and serves `git log`. `resolve_record_commit` no longer calls `log`, and `test_resolve_record_commit_full_clone_passes_through` passes `'d'*40` only to assert it is unused.
**Fix:** Remove `log_sha` and the `log` branch. Keep the `not any(a[0] == 'log' ...)` assertion by making the fake raise on `log`, which it already does for unknown commands.

### IN-04: `resolve_record_commit` handles git errors unevenly, and one message is misleading

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:281-293`
**Issue:** Only the first `git(...)` call is wrapped for `OSError`. The `cat-file` and `merge-base` calls are not. `merge-base --is-ancestor` returns 1 for "not an ancestor" and 128 for an error, and both produce "is not an ancestor of HEAD".
**Fix:** Wrap all three calls, and tell rc 1 apart from other non-zero codes in the message.

### IN-05: Certification of the publisher script is enforced only by pytest, not by `--validate`

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:726-728`; `tests/test_archive_assessment_demo3_w1_req_001_reply.py:258-263`
**Issue:** This is for orchestrator awareness. `validate_published` rebuilds the outputs with the **recorded** script digest and never compares it with `lf_digest(SCRIPT)`. An edit to the publisher therefore keeps plain `--validate` green. The only guard is `test_publisher_still_valid_and_digest_matches_manifest`, and it sits in the DEMO3 reply test file, which is a frozen 2.0.1 artifact. If that file is retired or deselected, nothing catches an uncertified publisher edit. No change to the publisher is needed for 2.0.2.
**Fix:** Move or duplicate the live-script-digest assertion into `tests/test_archive_assessment_applicability_authority_v2_publication.py`, next to `test_manifest_publisher_script_digest_matches_publication_commit`.

### IN-06: The isolated D-08 tamper test covers only an undecided row

**File:** `tests/test_archive_assessment_applicability_authority_v2_publication.py:1031-1038`
**Issue:** Every tamper is applied to `a['controls'][0]` (EMS-CTRL-001, NOT_YET_DECIDED). The isolated D-08 path, with `validate_authority` stubbed, is never driven on a decided row, for example by flipping a condition state on EMS-CTRL-030. That is the case where the decision-record check and the 2.0.1 comparison would most plausibly diverge.
**Fix:** Parametrize over one undecided control and one RULE_PUBLISHED control, and match on that control's id.

---

_Reviewed: 2026-11-12_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
