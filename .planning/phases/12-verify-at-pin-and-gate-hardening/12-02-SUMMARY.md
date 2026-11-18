---
phase: 12-verify-at-pin-and-gate-hardening
plan: 02
subsystem: test-gate
tags: [pytest, d-10, d-13, norm_templated, real-bytes, cli-validate]
requires: [12-01]
provides:
  - "D-10 clone test: live catalog overwrite/delete leaves publisher --validate outcome unchanged (GATE-09, WR-06)"
  - "D-13 exemption-removal test on real changed answers bytes (GATE-09, WR-07)"
  - "builder main --validate and publisher validate_governance_decisions reject real changed answers with 'repeats the note of' (GATE-08, WR-05)"
affects: [12-03, 12-04, 12-05, 12-06, 12-07]
tech-stack:
  added: []
  patterns: ["git clone --shared + subprocess outcome-equality for live-file independence", "real changed file copy instead of fabricated digest"]
key-files:
  created: []
  modified:
    - tests/test_archive_assessment_lineage_validation.py
    - tests/test_archive_assessment_governance_answers.py
    - tests/test_archive_assessment_governance_decisions.py
    - .planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md
decisions:
  - "D-10 --validate test asserts outcome equality only (returncode, last output line), never PASS, so it stays green through the planned red window"
  - "All 'f'*64 stand-ins in the decisions tests replaced by real digests, including two the plan did not name, to satisfy the plan's zero-count grep"
metrics:
  duration: "~25 min"
  completed: 2026-11-16
  tasks: 2
  files: 4
requirements-completed: [GATE-08, GATE-09]
---

# Phase 12 Plan 02: GATE-08/GATE-09 real-bytes and --validate-path tests Summary

The `--validate` paths are now covered by tests that run the real CLI on real bytes. The D-10 test runs the publisher `--validate` in a `git clone --shared` and shows that overwriting or deleting the live catalog does not change the outcome. The D-13 test and the norm_templated tests now use a real answers copy with one changed byte. The builder `main --validate` and the publisher `validate_governance_decisions` both reject that copy with "repeats the note of", and both accept the certified answers. This is a test-only change: no file under scripts/, registry/, schemas/, docs/ or generated/ was edited.

## Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | D-10 live catalog edit or delete leaves `--validate` outcome unchanged | 1e846ff | tests/test_archive_assessment_lineage_validation.py |
| 2 | D-13 real bytes, GATE-08 `--validate` path tests, commit, ledger | 1e846ff (code), docs commit (ledger) | tests/test_archive_assessment_governance_answers.py, tests/test_archive_assessment_governance_decisions.py, 12-BASELINE-RED.md |

The plan specifies a single code commit for both tasks, made after the full suite was green.

## What changed

- `test_d10_live_catalog_edit_or_delete_does_not_change_validate_outcome`: clones with `git -c core.longpaths=true clone --shared -q`, sets `core.longpaths true` in the clone, and runs `publish_archive_assessment_applicability_authority_v2.py --validate` three times (before any change, after writing `controls: []`, after deleting the file). It asserts `(returncode, last non-empty line)` equality. The clone's baseline outcome is `(0, 'PASS')` today, measured by hand. Each run takes about 3.5 s, so the test takes about 11 s.
- `test_changed_answers_bytes_remove_exemption`: uses `answers_copy(..., extra=b'\n')` and checks the copy's real digest (and `None`). The fabricated `sha_text(... + ' ')` digest is gone.
- Decisions module: new helpers `changed_answers` and `changed_decisions`, plus `publisher()`. New tests:
  - `test_validate_cli_rejects_note_collision_for_real_changed_answers`
  - `test_publisher_validate_governance_decisions_rejects_note_collision_for_real_changed_answers`
  - two controls on the certified answers (`test_validate_cli_passes_for_certified_answers`, `test_publisher_validate_governance_decisions_passes_for_certified_answers`), which show that D-13 grandfathering still holds
- `test_validate_decisions_rejects_templated_note_collision_for_uncertified_answers` now uses the real changed copy and its real digest instead of patching `CERTIFIED_ANSWERS_SHA256`.

## Verification (measured)

- Task 1: `.venv/Scripts/python.exe -m pytest tests/test_archive_assessment_lineage_validation.py -p no:cacheprovider -q -k d10 --basetemp=.pytest-temp/p12-02-t1` gave exit 0 with **10 passed**, 71 deselected. The `-k d10` filter selects every existing d10 test, not just the two the plan counted.
- Task 2: `.venv/Scripts/python.exe -m pytest tests/test_archive_assessment_governance_answers.py tests/test_archive_assessment_governance_decisions.py -p no:cacheprovider -q --basetemp=.pytest-temp/p12-02-t2` gave exit 0 with 160 passed.
- Full suite: `EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-02-full` gave **924 passed**, 0 failed, 0 skipped, in 321.75s, **pytest exit 0**. That is 919 + 5 new tests.
- Six CI validators: all returned rc=0 and PASS (publisher --validate; decisions builder --validate; rule proposals --validate and --validate-record; reply --validate; 2.0.2 notice --validate).
- Acceptance greps all held: fabricated `+ ' '` count 0; `'f' * 64` count 0; each new def count 1; `core.longpaths` 2; `'core.longpaths=true', 'clone'` 1; `'--shared'` 1.
- `git show --name-only HEAD` (1e846ff) lists exactly the three test files. `git diff HEAD~1 HEAD -- scripts registry schemas docs generated` is empty. The plan's form `git diff HEAD~1 --stat -- ...` compares against the working tree, so it also shows the unrelated uncommitted edits to `registry/adjudication_rules.json` and `registry/policy_decisions.json`. Those edits were never staged.

## Deviations from Plan

1. **[Rule 3 - Blocking acceptance] Replaced two more `'f' * 64` uses.** The acceptance grep requires zero occurrences, but the plan named only one of three.
   - `test_validate_decisions_ignores_superseded_note_repeat`, which also patched `CERTIFIED_ANSWERS_SHA256`, now uses the real changed answers copy and its digest.
   - `build_cli_setup`'s "unpublished" authority digest now uses the real digest of the tmp answers file (`MODULE.V2.lf_digest(ans)`). That is a real digest that differs from the decisions digest, so the test's meaning is unchanged.
2. **[Count note] Task 1 verify reports 10 passed, not 2.** `-k d10` matches eight existing d10 tests besides the two D-10 catalog tests. All passed.
3. **[Rule 2 - Coverage] Added two control tests** for the certified-answers pass case on both paths. The plan's behavior section asks for them ("Control: ... both paths pass") but its action text did not name them.

## TDD Gate Compliance

The plan is test-only: the production logic already existed (a9ff5d1, b72c3e9, 6893164). The new tests therefore passed at first run, and no RED/GREEN split was possible. The tests can still tell the cases apart: each rejecting test is paired with a control on the certified bytes that passes, and the only difference is one appended byte.

## Known Stubs

None.

## Self-Check: PASSED

- FOUND: tests/test_archive_assessment_lineage_validation.py, tests/test_archive_assessment_governance_answers.py, tests/test_archive_assessment_governance_decisions.py
- FOUND: commit 1e846ff
- FOUND: "## After plan 12-02" in 12-BASELINE-RED.md
