---
phase: 11-frozen-validators
plan: 04
subsystem: archive-assessment
tags: [tests, frozen-validator, negative-tests, hayes]
requires: [Plan 11-01 (fe5f5b2), Plan 11-02 (de6c678), Plan 11-03 (2e11045)]
provides: [committed-notice-files test, guard-specific negative assertions in the notice and reply tests, direct digest_scope_error and rows_differing guard calls]
affects: [Phase 12 publisher edits (notice and reply tests now name the guard that must fire)]
key-files:
  created: []
  modified:
    - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
    - tests/test_archive_assessment_demo3_w1_req_001_reply.py
requirements: [FROZEN-04]
decisions:
  - "Schema-level rejections assert jsonschema.ValidationError plus the failing keyword and instance path (validator/absolute_path), not only the class"
  - "Every match= string was taken from a run of the unmodified validator (A4); none of the builder code was changed"
  - "The reply has no derived-values check; zeroed reply digests are asserted at the fresh-build comparison ('reply JSON differs from a fresh build'), which is the guard that actually rejects them"
completed: 2026-11-14
---

# Phase 11 Plan 04: Guard-specific notice and reply tests Summary

The notice and reply negative tests now each name the guard they are for. Every `pytest.raises` gives a specific class, and every `AuthorityError` case gives a `match=` string. Each string was confirmed against the unmodified validator. A new test runs `validate_notice()` on the committed notice files with no monkeypatching. The `REJECTS` tuple is gone from both files, and neither builder was edited.

## Tasks

1. **Notice tests** (`tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`):
   - Removed `REJECTS`.
   - New `test_committed_notice_files_validate`: `require_history`, `MODULE.validate_notice()` on the committed files, stdout `PASS`, no `\r` in the JSON, MD and schema, and `contains_absolute(...) is False`.
   - `test_validate_rejects_tampered_cited_value` is now two tests:
     - `test_validate_rejects_tampered_cited_constant_by_schema`: 4 params. Asserts `ValidationError` with `validator == 'const'` at `['pin', key]`, then the file path `'notice JSON differs from a fresh build'`.
     - `test_validate_rejects_tampered_cited_digest_by_derivation`: 2 params. Checks that the zeroed digest passes the schema, then asserts `'notice differs from the values derived from the frozen inputs'` and the file path message.
   - `test_validate_rejects_tampered_constant`: each of the 8 params now carries its own class and message.
   - `test_resolve_record_commit_fails_when_commit_missing_or_not_ancestor`: each param has its own message. New `test_resolve_record_commit_fails_when_publication_not_before_record` covers the third `resolve_record_commit` guard.
   - `test_digest_scope_error_fails_when_previous_authority_edited`:
     - Each mutation has its own `match=`.
     - The `build_notice` half now passes the edited `previous` as an argument, so `digest_scope_error` is the guard that fires inside `build_notice`.
     - The old `serve_edited` path proved a different guard. It is now its own test, `test_supersedes_digest_rejects_an_edited_superseded_authority_in_git`.
   - `test_changed_row_blocks_no_decision_changed`: asserts `rows_differing == (1, 80)` and that `build_notice` raises `'1 of 80 control rows differ from the superseded version, ...'`. New `test_changed_control_set_or_decision_ids_block_no_decision_changed` has 3 params (popped row, swapped id, shortened `applicability_decision_ids`). It asserts on `rows_differing` and on `build_notice`.
   - `test_forbidden_word_is_rejected` is parametrised over all five `FORBIDDEN_WORDS`, with `match='notice uses the word {word}$'`. A guard test pins the five-word tuple.
   - `test_absolute_path_is_rejected`: 3 params (backslash drive, slash drive, root). Each checks that the schema accepts the value, then asserts `'notice contains an absolute path'`.
   - `test_validate_fails_closed_without_history_git_show` and `test_git_show_error_names_full_sha_and_fetch_hint` now also assert `match='git show failed'`.
   - `test_dual_role_statement_must_match_published_statement` is unchanged (`'dual role'`).
2. **Reply tests** (`tests/test_archive_assessment_demo3_w1_req_001_reply.py`):
   - Removed `REJECTS`. Added the helper `assert_schema_rejects(reply, validator, path)`, which asserts `ValidationError`, the keyword and the instance path.
   - Schema-level cases now assert the keyword and path:
     - bad AA4 format: `pattern` at `controls[0].authority`
     - flipped state, both directions: `type` at `controls[i].rule`
     - UNKNOWN rule state: `enum`
     - popped control: `minItems`; extra control: `maxItems`
     - 39-char commit: `pattern`; `xyz` manifest digest: `pattern`
     - 7-char record commit: `pattern`
   - New `test_mutation_swapped_control_id_with_21_controls`: 2 params, schema-valid, asserts `'reply controls differ from the 21 requested controls'`.
   - `test_mutation_dual_role_text` asserts `'dual role statement differs from the published statement'`. `test_mutation_absolute_path` has 3 params and asserts `'reply contains an absolute path'`. Both first prove that the schema accepts the mutation.
   - Zeroed `authority_sha256` and `manifest_sha256`: new `test_mutation_zeroed_digest_reaches_the_fresh_build_comparison` asserts `'reply JSON differs from a fresh build'`.
   - `test_validate_rejects_tampered_constant`: each of the 6 params carries its own class and message.
   - `test_resolve_record_commit_fails_when_commit_missing_or_not_ancestor`: each param has its own message.
   - `test_validate_fails_closed_without_history_git_show`: `match='git show failed'`.
   - `test_real_reply_files_validate` (D-13) now calls `require_history`. It asserts stdout `PASS` and still uses no monkeypatching.
   - `test_no_rule_published_row_raises_authority_error` and `test_shape_names_validated_against_authority`: see Deviations.

## Confirmed match strings (A4: each from a run of the unmodified validator)

Notice:
| Case | Class | Message |
|------|-------|---------|
| pin authority_id / version / publication_commit (SUP, REC) | ValidationError | `const` at `pin.<key>` |
| pin authority_sha256 / manifest_sha256 = 0*64 | AuthorityError | `notice differs from the values derived from the frozen inputs` |
| lineage relative_path absolute | AuthorityError | `notice contains an absolute path` |
| forbidden word | AuthorityError | `notice uses the word <word>` (all five) |
| NOTICE_PUBLICATION/RECORD/SCHEMA_COMMIT = d*40 | AuthorityError | `the frozen commit d...d is not in the repository history; ...` |
| NOTICE_PUBLICATION_COMMIT = 31addfa / 4d9b7c1 / b3c0411; NOTICE_RECORD_COMMIT = ae15c74 | AuthorityError | `NOTICE_PUBLICATION_COMMIT differs from the publication_commit named by the frozen publication record` |
| NOTICE_SCHEMA_COMMIT = ae15c74 | GitHistoryError | `schemas/archive_assessment_demo3_w1_req_001_notice_2_0_2.schema.json@ae15c74...: git show failed: ...` |
| fake git cat-file rc 128 / merge-base rc 1 | AuthorityError | `the frozen commit <PUB> is not in the repository history` / `the frozen commit <PUB> is not an ancestor of HEAD` |
| publication not ancestor of record | AuthorityError | `the publication commit is not an ancestor of the record commit` |
| digest_normalisation RAW_BYTES (direct and build_notice) | AuthorityError | `the superseded version does not declare the global CRLF_TO_LF claim` |
| aa2_closure_sha256 changed | AuthorityError | `aa2_closure_sha256 in 2.0.1 differs from aa2_closure in 2.0.2` |
| aa1_manifest_sha256 popped | AuthorityError | `aa1_manifest_sha256 in 2.0.1 differs from aa1_manifest in 2.0.2` |
| superseded authority edited in git | AuthorityError | `the authority frozen at the superseded commit differs from the supersedes entry` |
| controls[0] state changed | AuthorityError | `1 of 80 control rows differ from the superseded version, so no-decision-changed cannot be stated` |
| control set / applicability_decision_ids changed | AuthorityError | `control set or cited decision ids differ from the superseded version` |

Reply:
| Case | Class | Message |
|------|-------|---------|
| swapped control id, 21 controls | AuthorityError | `reply controls differ from the 21 requested controls` |
| dual role text | AuthorityError | `dual role statement differs from the published statement` |
| absolute authority_path | AuthorityError | `reply contains an absolute path` |
| zeroed pin digest | AuthorityError | `reply JSON differs from a fresh build` (validate_reply_object accepts it) |
| REPLY_PUBLICATION_COMMIT = d*40 | GitHistoryError | `registry/archive_assessment_applicability_authority_v2.json@d...d: git show failed` |
| REPLY_RECORD_COMMIT = d*40 | GitHistoryError | `registry/archive_assessment_applicability_authority_v2_publication_record.json@d...d: git show failed` |
| REPLY_PUBLICATION_COMMIT = 54a7fd0 / 4d9b7c1 / b3c0411; REPLY_RECORD_COMMIT = 31addfa | AuthorityError | `REPLY_PUBLICATION_COMMIT differs from the publication_commit named by the frozen publication record` |
| all RULE_PUBLISHED rows and records turned to no-rule | AuthorityError | `no RULE_PUBLISHED row for the example` |
| one row changed, record not | AuthorityError | `EMS-CTRL-030: decision record disagrees with the authority row` |
| shape params | AuthorityError | `authority lacks the top_level_field applicability_decision_ids`, `authority lacks the semantics_block not_applicable_semantics`, `authority rows lack the field not_applicable_rule`, `authority rows lack the field not_applicable_authority`, `authority rows do not carry the eight AA1-GOV ids` |

Research strings that were directional and corrected (A4):
- Notice tampered constants. The research list was `'differs from a fresh build'`, `'not in the repository history'`, `'publication_commit'` and `'not an ancestor'`. With the real params, no case produces `'differs from a fresh build'` or `'not an ancestor'`:
  - the d*40 commits fail the history check;
  - the reachable commits fail the record binding;
  - the schema commit ae15c74 fails `git show` with `GitHistoryError`.
  - `'not an ancestor'` is reachable only through a fake `git`. It is asserted in the `resolve_record_commit` tests instead.
- Reply sha/digest. The reply has no "differs from the values derived" message. The guard that rejects a zeroed digest is the fresh-build file comparison.
- Reply tampered constants. `resolve_record_commit` is called via build_reply, after the pinned reads in load_inputs, so d*40 constants fail at the first pinned `git show` (`GitHistoryError`), before the history check is reached. This is recorded as a finding and the builder was not changed (FROZEN-04 is test-only).

## Non-vacuity (sabotage) runs

I ran each case against a scratch edit of a builder. The script swapped one guard for `if False:` (or removed the schema call), ran only the matching tests, then wrote the original bytes back. All 26 cases went red:

| Guard broken | Tests red |
|---|---|
| N notice schema validate in validate_notice_object | 4 failed (cited constant by schema) |
| N contains_absolute | 3 failed |
| N dual role | 1 failed |
| N forbidden words | 5 failed |
| N derived-values comparison | 2 failed |
| N digest_scope_error CRLF claim | 1 failed, 2 passed (the other two mutations target other checks) |
| N digest_scope_error per-digest values | 2 failed, 1 passed |
| N supersedes digest | 1 failed |
| N rows_differing set / ids | 3 failed |
| N `if differing:` | 1 failed |
| N record binding | 5 failed (4 constant params + record binding test) |
| N history (cat-file) | 4 failed |
| N ancestor of HEAD | 1 failed |
| N publication before record | 1 failed |
| N committed JSON comparison (inverted) | 1 failed (committed-files test) |
| R reply schema validate | 6 failed |
| R contains_absolute | 3 failed |
| R id-set check | 2 failed |
| R dual role | 1 failed |
| R fresh-build JSON comparison | 2 failed |
| R record binding | 4 failed |
| R no RULE_PUBLISHED example | 1 failed |
| R record agrees with row | 1 failed |
| R PER_CONTROL_FIELDS shape | 2 failed, 3 passed (other params target other guards) |
| R history (cat-file) | 1 failed |
| R ancestor of HEAD | 1 failed |

After the runs, `git diff --quiet -- scripts` succeeded (empty) and the reply builder's sha256 was unchanged. The script is `scratchpad/sabotage.py` (session scratchpad, not committed).

## Verification

All runs used `-p no:cacheprovider` and a fresh `--basetemp=.pytest-temp/p11-4*`:

- **Notice test file:** 130 passed, 0 skipped.
- **Reply test file:** 109 passed, 0 skipped.
- **Full `-k archive_assessment` suite, plain:** 910 passed, 7 deselected, 0 skipped, 0 failed (334 s). The baseline was 890; the change is +20 test items from the new and split parametrised tests.
- **Full suite with `EMS_FAIL_ON_SKIP=1`:** 910 passed, 7 deselected, 0 skipped, 0 failed (298 s).
- **Validators:** all six CI `--validate` commands print PASS: publisher v2, governance decisions, rule proposals `--validate` and `--validate-record`, reply, and notice.
- **`py_compile`** succeeds on both test files.
- **`grep -c REJECTS`** prints 0 for both test files.
- **SC4:** `git diff b97e805 HEAD -- <7 frozen paths>` is empty, and so is the working-tree diff on those paths.
- **`git status`:** only the two test files are newly modified. `.planning/config.json`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `registry/adjudication_rules.json` and `registry/policy_decisions.json` are still unstaged and were not touched. Nothing is staged.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_no_rule_published_row_raises_authority_error` tested a different guard**
- **Found during:** Task 2
- **Issue:** The test turned the three RULE_PUBLISHED rows into no-rule rows, but the decision records still said RULE_PUBLISHED. So `'EMS-CTRL-030: decision record disagrees with the authority row'` fired first, and the `'no RULE_PUBLISHED row for the example'` guard the test is named for was never reached.
- **Fix:** The test now also updates the matching latest decision records and asserts `match='no RULE_PUBLISHED row for the example'`. The old behaviour is kept as its own test, `test_decision_record_disagreeing_with_row_raises_authority_error`. Both were proven red by sabotage.
- **Files modified:** tests/test_archive_assessment_demo3_w1_req_001_reply.py

**2. [Rule 2 - Rigor] Tightened `pytest.raises` calls outside the REJECTS list**
- `test_shape_names_validated_against_authority` (5 params), both `resolve_record_commit` missing/not-ancestor tests and the `git_show` fail-closed tests had a bare `AuthorityError` or `GitHistoryError`. They now carry the confirmed message, so the notice file meets "every pytest.raises names a class and a match=".
- The one exception is `test_build_reply_takes_four_inputs`, which keeps `TypeError` with no match.

**3. The plan's step "commit by explicit path" was not run**
- The orchestrator instructions say not to commit. Nothing was staged or committed; the orchestrator will make the commit.

## Findings (not fixed: frozen builder code)

- `validate_reply()` reaches `resolve_record_commit()` via build_reply, after the pinned reads in load_inputs. The reply's shallow-clone, history and ancestor guards therefore run only after those reads. With an unknown commit, `validate_reply` fails at the first pinned `git show` (`GitHistoryError`, still with the fetch hint), before reaching the history check. The notice's `load_inputs()` calls it first.
- The notice builder working copy has mixed line endings (`git ls-files --eol`: `i/lf w/mixed`). It was like this before this plan and was left alone; `git diff -- scripts` is empty.

## Self-Check: PASSED

- FOUND: tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py (modified, uncommitted)
- FOUND: tests/test_archive_assessment_demo3_w1_req_001_reply.py (modified, uncommitted)
- There is no task commit to check: the orchestrator makes the commit.
