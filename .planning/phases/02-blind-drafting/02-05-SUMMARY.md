---
phase: 02-blind-drafting
plan: 05
subsystem: governance
tags: [drafting-record, history-tests, blind-drafting]
requires:
  - phase: 02-blind-drafting
    provides: drafting commit and approved brief (plans 03-04)
provides:
  - Drafting record naming the drafting commit, built from committed blob bytes
  - Unconditional history, hash and ordering tests (13 cases)
key-files:
  created:
    - registry/archive_assessment_rule_proposals_drafting_record.json
    - tests/test_archive_assessment_rule_proposals_record.py
key-decisions:
  - Published-authority-unchanged test covers the two existing published v1 files (authority, schema); no certification, history or traceability files exist for v1
requirements-completed: [DRAFT-02, DRAFT-03]
duration: n/a
completed: 2026-10-13
---

# Phase 2 Plan 05: Drafting Record and History Tests Summary

A drafting record in a later commit names the drafting commit, and tests prove from git alone that drafting preceded everything else and the proposals are unchanged since.

## Record

- Commits in order: tooling c8b27121cc37e065d7f0f10ea47b83f5854ad8c9, brief 6969f520162984d79276744805432d1c8dd14c89, drafting dc3b41c9fbb3571a191d2da5164fb73439a0637b, record commit be915e3664ef3d2f6b8b5a887cccfe706807ad9b.
- Record commit contains exactly `registry/archive_assessment_rule_proposals_drafting_record.json` and `tests/test_archive_assessment_rule_proposals_record.py`.
- Hashes computed over `git show` bytes; record is LF only; validator `--validate` PASS, `--validate-record` PASS.
- Isolation recorded as by instruction and brief design, project instructions not loaded, residual exposure stated (prompt hash covers prompt bytes only; CLI default system prompt in effect).
- Pytest (authority, v2, proposals, record modules): 171 passed, 0 skipped.

## Final phase audit

- Order of commits as above: confirmed.
- Registry diff from before the tooling commit to HEAD: only the proposals file and the drafting record.
- Proposals blob at HEAD equals the blob at the drafting commit (fb55535b6f17e2c4c3a2cd23dddbd39cd0355458).
- `registry/adjudication_rules.json` and `registry/policy_decisions.json` remain modified and unstaged; index empty after commit.
- No v2 authority file tracked; REQUIREMENTS.md DRAFT-02 and ROADMAP Phase 2 wording already carry D-26 (not edited).

## Deviations from Plan

**1. [Rule 1 - Bug] Test expected four published v1 files** The plan assumed certification, history and traceability files exist; only the authority and its schema exist at baseline. Assertion lowered to at least 2 (authority JSON required). Fixed in the same commit.

## Self-Check: PASSED
