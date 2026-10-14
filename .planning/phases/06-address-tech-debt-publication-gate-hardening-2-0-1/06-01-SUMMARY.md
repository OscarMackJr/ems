---
phase: 06-address-tech-debt-publication-gate-hardening-2-0-1
plan: 01
subsystem: docs
tags: [vocabulary, rule-fields, D-04, D-22]
requirements: [D-04, D-22]
key-files:
  modified: [.planning/PROJECT.md, CLAUDE.md]
metrics:
  tasks: 1
  files: 2
---

# Phase 6 Plan 01: Rule-field vocabulary wording Summary

Corrected PROJECT.md (Validated line and Constraints Vocabulary line) and CLAUDE.md (Vocabulary line) to say rule conditions use only the first four classification fields (production, internet_exposed, contains_customer_data, ai_enabled); the other four remain classification prerequisites. Wording matches `RULE_FIELDS = CLASSIFICATION_FIELDS[:4]` in the v2 publisher.

## Commits
- Task 1: see git log "docs(06-01): correct rule-field vocabulary wording to the first four fields" (two files, explicit-path staging)

## Deviations from Plan
None. Both files had no prior uncommitted changes. Unrelated working-tree changes were left untouched.

## Self-Check: PASSED
