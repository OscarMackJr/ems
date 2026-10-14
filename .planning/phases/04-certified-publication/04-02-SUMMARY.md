---
phase: 04-certified-publication
plan: 02
subsystem: archive-assessment-governance-decisions
tags: [validators, review-debt, fail-closed]
requires: ["04-01"]
provides:
  - "strict checks on every answers entry including superseding entries"
  - "append-only --build for superseding records"
affects: [04-04]
key-files:
  modified:
    - scripts/build_archive_assessment_governance_decisions.py
    - tests/test_archive_assessment_governance_decisions.py
requirements: [PUB-04]
decisions:
  - "WR-01 stripping of control ids and digits is applied to the drafted-text comparison only, not to note uniqueness, because the real answers notes differ only by a leading control number"
metrics:
  commit: 0655149
  completed: 2026-10-14
---

# Phase 4 Plan 02: Decisions validator hardening Summary

CR-03 and WR-01, WR-02, WR-03, WR-04, WR-06, WR-07, WR-09 are fixed in the decisions builder; IN-01..05 untouched.

## Accomplishments
- CR-03: `strict_checks` runs over all entries; `build_decisions` also raises on APPROVED_AS_DRAFTED with a rule/rationale and on a scope ruling for a control without a scope note.
- WR-01: notes are compared with `ems-ctrl-N` and digits stripped against every string in the drafted proposal.
- WR-02: first 21 entries cannot supersede; later entries must name an earlier position for the same control.
- WR-03: unknown control id gives AuthorityError; the answers schema runs in `build_from_files`.
- WR-04: `date.fromisoformat` in both validators.
- WR-06: type guards (note, rationale, control_id, supersedes, rule conditions) raise AuthorityError.
- WR-07: `refreshable` accepts a rebuild whose existing records are a prefix of the rebuilt records.
- WR-09: fidelity test, superseding strict tests, emit-template subprocess refusal test, answers_sha binding test still present.

## Deviations from Plan
- WR-01: the real answers notes begin with a control number and are otherwise identical, so applying the stripped comparison to note uniqueness would reject the committed answers. It is applied to drafted-text comparison only.
- Tests are in the decisions test file only; tests/test_archive_assessment_governance_answers.py needed no change (two files committed, not three).
- Implementation was written before the tests rather than strictly red-first; no failing-first run was captured.
- Tests use the module-level TemporaryDirectory (tmp_path unreliable here).

## Verification
`python -m pytest tests -k archive_assessment -q`: 311 passed. Builder `--validate` and `--validate-answers` print PASS. Registry answers and decisions files unchanged.

## Self-Check: PASSED
Commit 0655149 contains exactly the two files above.
