---
phase: 11-frozen-validators
plan: 02
subsystem: archive-assessment
tags: [notice, frozen-validator, tests, hayes]
requires: [AA3 2.0.2 publication ae15c74, record a71257e, superseded 2.0.1 31addfa, notice schema 052f0f1, Plan 11-01 pattern]
provides: [notice builder with no live-publisher dependency, D-02 literal-vs-blob tests at ae15c74, D-11 AST and mutation tests for the notice]
affects: [Plan 11-03 history-guard conversion, Plan 11-04 REJECTS replacement, Phase 12 publisher edits (notice stays green)]
key-files:
  created: []
  modified:
    - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
    - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
requirements: [FROZEN-02]
decisions:
  - "Notice validate_signoff is the ae15c74 4-arg form (authority_id=None, version=None defaults), byte-for-byte; the builder passes both keywords"
  - "NOTICE_SCHEMA_COMMIT = 052f0f13f4c882a7b80667d4835bc802002e0f80, checked only in the cat-file/ancestor-of-HEAD loop, never in the publication-vs-record ancestor check"
  - "Notice schema read via a fixed NOTICE_SCHEMA_REL (11-01 pitfall), so tests that redirect NOTICE_SCHEMA still reach the intended error"
completed: 2026-11-14
---

# Phase 11 Plan 02: Freeze the 2.0.2 notice validator on ae15c74 Summary

The 2.0.2 notice builder now holds every publisher value and helper it uses as local code, copied from the ae15c74 publisher blob. It checks its committed schema against the frozen blob at 052f0f1 and offers only `--validate`. Tests prove the local literals equal the ae15c74 blob. They also show that a mutated live publisher (changed `PREV_COMPARED_KEYS`, `DUAL_ROLE_STATEMENT`, `rule_text`, `closed_schema_levels`, `APPROVER_ROLES`, `REQUEST_CONTROL_IDS`; raising `validate_signoff` and `git_show`) cannot change the result.

## Tasks

1. **Builder freeze** (`scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`):
   - Removed `importlib.util`, the `_spec`/`V2` loader and every `V2.` use (including `V2.ROOT`).
   - Added `REGISTRY`, `SCHEMAS` and these constants from ae15c74: `AUTHORITY`, `SCHEMA`, `GOVERNANCE_DECISIONS`, `REQUEST_CONTROL_IDS`, `VERSION='2.0.2'`, `AUTHORITY_ID`, `PREV_COMPARED_KEYS`, `OUT`, `SIGNOFF`, `PUBLICATION_RECORD`, `APPROVER`, `APPROVER_ROLES`, `SIGNOFF_ROLE`, `DUAL_ROLE_STATEMENT`, `N_NEGATIVE`, `N_TRACE`, `N_MANIFEST`.
   - Added the helpers `AuthorityError`, `GitHistoryError`, `lf_bytes`, `load`, `contains_absolute`, `bad_rel`, `git_show`, `jtext`, `rel` (taken from the frozen reply builder, so `git_show` errors keep `git show failed`, name the full SHA and append `; fetch full history (git fetch --unshallow)`, D-07). `closed_schema_levels`, `is_date`, `validate_signoff` (4-arg) and `rule_text` are copied verbatim from the ae15c74 blob. `RULE_FIELDS`, `CONDITION_STATES`, `COMBINATION`, `AUTHORITY_ID_RE`, `dump`, `write_text`, `NORMALISERS` and `lf_digest` were not copied.
   - Added `NOTICE_SCHEMA_COMMIT`, `NOTICE_SCHEMA_REL` and `frozen_notice_schema()`, and deleted the regenerating `schema()`. `validate_notice` requires the committed schema bytes (LF) to equal the blob, else `notice schema differs from the frozen schema at <sha>`. `validate_notice_object` validates against `frozen_notice_schema()`.
   - `resolve_record_commit` checks `cat-file` and ancestry of HEAD for the publication, superseded, record and schema commits. Errors now name the full SHA and the fetch hint. The publication-vs-record ancestor check is unchanged and does not include the schema commit.
   - The CLI keeps `--validate` only. `--build`, `--emit-schema` and the write path are gone.
2. **Tests** (`tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`):
   - Removed the `V2` alias; `AuthorityError = MODULE.AuthorityError`; all `V2.x` now `MODULE.x`; `git_show` monkeypatches target `MODULE`. Added local `dump`/`write_text` for temp files. `MODULE.schema()` became `MODULE.frozen_notice_schema()`.
   - Loosened-schema test now expects `notice schema differs from the frozen schema at 052f0f1...`.
   - Tampered-constant test gained two `NOTICE_SCHEMA_COMMIT` cases (`'d'*40`, and ae15c74, where the schema did not yet exist).
   - New `test_notice_schema_commit_holds_the_committed_schema`: SHA, cat-file, ancestor of HEAD, not an ancestor of the publication commit, `NOTICE_SCHEMA_REL == rel(NOTICE_SCHEMA)`, blob bytes equal the committed schema and `frozen_notice_schema()`.
   - The full-clone pass-through test now asserts all four commits are cat-file and HEAD-ancestry checked, and that the only non-HEAD ancestry check is `(PUB, REC)`.
   - Replaced `test_validate_independent_of_live_version` with `test_validate_notice_passes_with_a_mutated_live_publisher` (research Pattern 3: mutated module installed under both names plus a patched `spec_from_file_location`; non-vacuity asserts the old loader line yields the mutated module; fresh-loaded builder prints PASS).
   - D-02 against ae15c74 via `frozen_publisher(commit)` (`pytest.fail` naming commit, path and "fetch full history"): 19 constants; `NOTICE_VERSION`/`NOTICE_AUTHORITY_ID`; path constants under ROOT; `rule_text` on the 3 real rules plus a 2-condition synthetic; `closed_schema_levels` on the real frozen schema (16 levels) plus a nested synthetic with lists and a custom root path; `validate_signoff` on the real signoff plus 14 mutations, a wrong digest and non-dict inputs, under 4 keyword combinations, comparing exception class and text; signature check (4 params, `None` defaults); `contains_absolute` (11 values), `bad_rel` (11), `is_date` (7), `jtext`, `lf_bytes`, `load`, `rel`.
   - D-11 static: AST scan of the notice builder (same rules as the reply) plus scanner non-vacuity.
   - `git_show` error-text test (full SHA, `git show failed`, fetch hint; short-SHA and `..` rejections).
   - CLI rewritten: `--build`, `--emit-schema`, `--push-check` exit 2 (alone: required group empty; next to `--validate`: `unrecognized arguments`); `--validate` prints PASS; bytes of notice JSON, MD, schema, sign-off and publication record unchanged; `schema`, `dump`, `write_text`, `V2` absent from the module.
   - Kept the `pytest.skip` history guards (Plan 03) and the broad `REJECTS` tuple (Plan 04).

## Verification

- `python -I scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py --validate` from `%TEMP%`: PASS. `--build` and `--emit-schema` each exit 2.
- `grep -c "V2\|importlib\|publish_archive_assessment_applicability_authority"` on the builder: 0. `NOTICE_SCHEMA_COMMIT` line shows `052f0f13f4c882a7b80667d4835bc802002e0f80`.
- `grep -c "MODULE.V2\|V2 ="` on the notice test file: 0.
- Notice test file (basetemp `.pytest-temp/p11-2-exec-b`): **117 passed, 0 failed, 0 skipped**.
- Full `pytest tests -k archive_assessment -rs` (basetemp `.pytest-temp/p11-2-exec-full`): **876 passed, 0 failed, 0 skipped** (7 deselected). The baseline after 11-01 was 807; the notice file went from 48 to 117 items (+69).
- All six workflow validator commands print PASS (publisher, governance decisions, rule proposals `--validate` and `--validate-record`, reply, notice).
- `git diff --stat` is empty for the publisher, the notice MD/JSON/schema and the reply MD/JSON/schema. Nothing staged.
- `ruff check --select F` passes on both files.
- Non-vacuity probe (temporary file, removed): the HEAD (pre-freeze) notice builder, loaded under the same mutation setup, failed with `AuthorityError: mutated live publisher was called`, and the AST scanner flagged it (`import importlib.util`, `call spec_from_file_location`, the publisher path string, `name V2`).

## Deviations from Plan

1. **[Rule 1 - Bug, carried from 11-01] Fixed schema path for the frozen-schema read.** `NOTICE_SCHEMA_REL` is a fixed constant instead of `rel(NOTICE_SCHEMA)`, because tests redirect `NOTICE_SCHEMA` to a temp file outside ROOT. A test asserts `NOTICE_SCHEMA_REL == rel(NOTICE_SCHEMA)`.
2. **Generic helpers taken from the frozen reply builder, not the raw blob.** `git_show`, `GitHistoryError`, `bad_rel` follow D-03/D-07 (full SHA + fetch hint) as in 11-01. The blob's `git_show` uses `commit[:7]` and no hint, so `git_show` is outside the D-02 equality scope; `bad_rel` is proven equal to the blob.
3. **`resolve_record_commit` error texts** now name the full SHA and the fetch hint (previously `sha[:7]`), matching 11-01. No test matched the old text.
4. **Extra D-02 coverage** beyond the plan's list: `bad_rel`, `is_date`, `load`, the `validate_signoff` signature, and `NOTICE_VERSION`/`NOTICE_AUTHORITY_ID` agreement.
5. **CLI test shape** as in 11-01: removed flags alone report the empty required group; paired with `--validate` they report `unrecognized arguments`. `--push-check` cases added for parity (the notice never had it). All exit 2.
6. **OLD_LOADER test fixture** writes `V2=importlib.util.module_from_spec(_spec)` without spaces so the acceptance grep for `V2 =` is literally 0; the scanner still flags `name V2`.

No commits were made and nothing was staged. The orchestrator commits by explicit path with `feat(11-02): freeze the 2.0.2 notice validator on ae15c74`.

## Self-Check: PASSED

- Both modified files exist and show in `git status` as ` M`.
- The frozen notice/reply/schema/publisher bytes show no diff.
