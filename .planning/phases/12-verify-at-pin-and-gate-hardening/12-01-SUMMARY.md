---
phase: 12-verify-at-pin-and-gate-hardening
plan: 01
subsystem: test-gate
tags: [ci, pytest, skip-guard, git-history, red-window]
requires: []
provides:
  - "12-BASELINE-RED.md red-window ledger (D-16)"
  - "archive-scoped collect-report skip guard (D-10)"
  - "CI archive step selected by unquoted glob tests/test_archive_assessment_*.py (D-09)"
  - "accurate aa_history HINT and shallow-unknown message (D-11)"
affects: [12-02, 12-03, 12-04, 12-05, 12-06, 12-07]
tech-stack:
  added: []
  patterns: ["collector scoping by path name, not nodeid"]
key-files:
  created:
    - .planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md
  modified:
    - .github/workflows/ems-validate.yml
    - tests/conftest.py
    - tests/aa_history.py
    - tests/test_archive_assessment_skip_guard.py
decisions:
  - "Collect-report skip guard is scoped by collector.path name (test_archive_assessment_*.py), not nodeid, because --rootdir changes nodeid prefixes"
  - "A skip raised inside conftest.py itself is no longer converted by the collect guard; CI still fails in that case because nothing is collected (pytest exit 5)"
metrics:
  duration: "~13 min"
  completed: 2026-11-16
  tasks: 3
  files: 5
requirements-completed: [GATE-09]
---

# Phase 12 Plan 01: Baseline ledger and test-gate hardening (D-09..D-11) Summary

This plan records a green baseline ledger, then lands the three gate fixes in one green commit. The fixes scope the collect-time skip-to-failure guard to `test_archive_assessment_*` modules, select the CI archive modules with an unquoted glob, and make the `aa_history` messages accurate about `EMS_ALLOW_NO_HISTORY` and about unknown shallow-check output.

## Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Measure baseline, create 12-BASELINE-RED.md | (docs commit with this SUMMARY) | 12-BASELINE-RED.md |
| 2 | Scope collect skip guard, narrow CI glob (D-09, D-10) | 8dd3778 | conftest.py, test_archive_assessment_skip_guard.py, ems-validate.yml |
| 3 | aa_history wording (D-11); one combined commit; ledger update | 8dd3778 | aa_history.py, test_archive_assessment_skip_guard.py, 12-BASELINE-RED.md |

As the plan requires, Tasks 2 and 3 share the single code commit `8dd3778` (D-11 requires one commit).

## Measured results

- Baseline at HEAD 87b5cd59c0564c8877eccb184038057bce107a72: `EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=.pytest-temp/p12-01-baseline`. Result: **918 passed**, exit 0, 310.51s. All 6 CI validators printed PASS.
- RED check (tests edited, implementation not yet changed): `tests/test_archive_assessment_skip_guard.py` gave 3 failed, 20 passed, exit 1. The failures were the new deselected-module case and the `''` and `'maybe'` parameters of the shallow-output test.
- GREEN: skip-guard module **23 passed**, exit 0 (`--basetemp=.pytest-temp/p12-01-t3`).
- Full suite after the change (`--basetemp=.pytest-temp/p12-01-full`): **919 passed**, 0 failed, 0 skipped, exit 0, 317.43s. All 6 CI validators printed PASS.
- Accepted red set now: none.

## TDD Gate Compliance

The RED state was verified by running the tests, but no separate `test(...)` RED commit exists. The plan explicitly requires D-09, D-10 and D-11 to land as ONE commit (`8dd3778`, type `test`). This is intentional and follows the plan.

## Deviations from Plan

None. The plan was executed as written.

## Notes

- **T-12-01-04 (accepted):** a skip raised inside `conftest.py` itself is no longer converted to a failure by the collect guard, because conftest is not a `test_archive_assessment_*` module. CI still fails in that case: nothing is collected, so pytest exits 5.
- The working copy uses CRLF line endings (`core.autocrlf=true`). The committed blobs are LF, as before, and the diff contains only the intended lines.
- GATE-09 was NOT marked complete in REQUIREMENTS.md. This plan only supports the gate GATE-09's tests run under; the D-10/D-13 test content GATE-09 names is delivered by 12-02. An automatic mark-complete was reverted.
- The unrelated uncommitted files (`.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json`, untracked files) were not staged.

## Self-Check: PASSED

- FOUND: .planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md
- FOUND: tests/conftest.py (`_archive_module`), tests/aa_history.py, tests/test_archive_assessment_skip_guard.py, .github/workflows/ems-validate.yml
- FOUND: commit 8dd3778 (4 files exactly; message ends with Co-Authored-By line)
