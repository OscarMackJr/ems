---
phase: 11-frozen-validators
plan: 05
subsystem: test-harness
tags: [pytest, skip-guard, gap-closure, FROZEN-03]
requires: []
provides:
  - collection-level skip guard (pytest_make_collect_report hookwrapper)
  - fail-closed shallow-repository detection in aa_history.history_problem
affects:
  - tests/conftest.py
  - tests/aa_history.py
  - tests/test_archive_assessment_skip_guard.py
tech-stack:
  added: []
  patterns: [hookwrapper on pytest_make_collect_report, mirroring the runtest makereport guard]
key-files:
  created: []
  modified:
    - tests/conftest.py
    - tests/aa_history.py
    - tests/test_archive_assessment_skip_guard.py
decisions:
  - "11-05: Collection-level skips under EMS_FAIL_ON_SKIP=1 become collection errors via a pytest_make_collect_report hookwrapper; no sessionfinish fallback needed (verified on pytest 9.1.1)"
  - "11-05: history_problem requires exactly 'false' from --is-shallow-repository; anything else is a shallow-history problem (WR-04)"
  - "11-05: WR-02 (EMS_ALLOW_NO_HISTORY opt-out reach) accepted as the fail-closed D-08 convenience; xfail exemption kept as is"
metrics:
  duration: ~15min
  completed: 2026-11-15
requirements: [FROZEN-03]
requirements-completed: [FROZEN-03]
---

# Phase 11 Plan 05: Collection-Level Skip Guard and Fail-Closed Shallow Check Summary

The `EMS_FAIL_ON_SKIP=1` guard now also catches module-level `pytest.importorskip` and `pytest.skip(allow_module_level=True)`. A `pytest_make_collect_report` hookwrapper turns them into collection errors ("1 error", non-zero exit). `aa_history.history_problem` now fails closed on any shallow-check output other than exactly `false`.

## Tasks

| Task | Name | Commits | Files |
|------|------|---------|-------|
| 1 | Fail collection-level skips under EMS_FAIL_ON_SKIP=1 | 8d3b935 (RED), 97c630f (GREEN) | tests/test_archive_assessment_skip_guard.py, tests/conftest.py |
| 2 | Make shallow-repository detection fail-closed (WR-04) | 60615d2 (RED), 348517f (GREEN) | tests/test_archive_assessment_skip_guard.py, tests/aa_history.py |

## What Changed

- `tests/conftest.py`: added a `pytest_make_collect_report(collector)` hookwrapper. When the guard is on and `rep.skipped`, it sets `outcome='failed'` and a longrepr that starts with `skipped test treated as failure (EMS_FAIL_ON_SKIP=1): <nodeid>: ...`. The runtest hook is unchanged.
- `tests/test_archive_assessment_skip_guard.py`: added `module_importorskip` and `module_skip` bodies. `run_case` gained an optional `extra_module` argument (default `None`). When set, it writes `test_ok.py` and passes it as a second pytest target, so the unguarded run reports `1 passed, 1 skipped` with exit 0 instead of exit 5. Added four `test_module_*` cases, the parametrised `test_history_problem_unrecognised_shallow_output_is_problem` (`''`, `'maybe'`, `'true'`), and `test_history_problem_false_output_passes_shallow_check`.
- `tests/aa_history.py`: `== 'true'` changed to `!= 'false'`; message text unchanged.

## TDD Gate Compliance

- Task 1 RED: 2 failed (the two guard-on module cases), 16 passed. GREEN: 18 passed.
- Task 2 RED: 2 failed (`''` and `maybe` params), 20 passed. GREEN: 22 passed.
- test(...) commits precede fix(...) commits for both tasks.

## Verification

- `.venv/Scripts/python.exe -m pytest tests/test_archive_assessment_skip_guard.py --basetemp=.pytest-temp/skipguard-green2 -p no:cacheprovider -q`: 22 passed
- `grep -c "pytest_make_collect_report" tests/conftest.py`: 1; `grep -c "def test_module_"`: 4; `grep -c "!= 'false'" tests/aa_history.py`: 1; `grep -c "== 'true'"`: 0
- `grep -n xfail tests/test_archive_assessment_*.py`: matches only in the skip_guard file
- Full run `EMS_FAIL_ON_SKIP=1 pytest tests -k archive_assessment`: 918 passed, 7 deselected, 0 skipped, 0 failed (322s; note: the recorded exit=0 is the exit of `tail` in the pipe, but the summary line shows no failures or errors)
- No builder, registry, schema or docs file touched (SC4).

## Deviations from Plan

None. The plan was executed as written. Local pytest is 9.1.1, not 8.4.2; the hookwrapper alone was enough, so no contingency fallback was added.

## Known Stubs

None.

## Self-Check: PASSED

All three modified files exist; commits 8d3b935, 97c630f, 60615d2, 348517f found.
