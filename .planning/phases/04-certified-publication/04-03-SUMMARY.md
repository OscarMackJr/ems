---
phase: 04-certified-publication
plan: 03
subsystem: archive-assessment-line-endings
tags: [gitattributes, eol-lf]
requires: ["04-02"]
provides:
  - "narrow .gitattributes pinning project files to eol=lf"
key-files:
  created:
    - .gitattributes
requirements: [PUB-06]
metrics:
  commit: c4fd370
  completed: 2026-10-14
---

# Phase 4 Plan 03: Narrow .gitattributes Summary

A new `.gitattributes` lists 14 explicit project files plus `generated/archive-assessment/ems-aa3-v2/**` as `text eol=lf`; v1 files and `ems-aa3/` are not listed.

## Verification
- `git check-attr eol`: ems-aa3-v2 path = lf; ems-aa3 path and v1 authority registry = unspecified.
- Only one line contains an asterisk (the v2 folder).
- Commit c4fd370 contains only `.gitattributes`.
- No renormalisation was needed or performed.

## Working tree status after adding .gitattributes
- `schemas/archive_assessment_governance_answers.schema.json` still shows ` M` (no content diff; left untouched, not staged, as instructed).
- `registry/adjudication_rules.json` and `registry/policy_decisions.json` remain ` M` as before.
- No other tracked file became dirty because of .gitattributes.
- Git warned that `.gitattributes` itself would be converted to CRLF on next touch (global autocrlf); it has no effect on the committed blob.

## Deviations from Plan
None. Note that several listed v2 registry files do not exist yet (publisher output in a later plan); their entries are inert until then.

## Self-Check: PASSED
