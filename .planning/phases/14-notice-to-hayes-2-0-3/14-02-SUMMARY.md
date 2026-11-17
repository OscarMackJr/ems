---
phase: 14-notice-to-hayes-2-0-3
plan: 02
subsystem: archive-assessment-notice
tags: [notice, schema, render, validate]
requires: [14-01]
provides:
  - "build_notice, render_markdown, schema, validate_notice_object, validate_notice, main (--build/--emit-schema/--validate)"
key-files:
  modified:
    - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
requirements-completed: [NOTICE-03, PIN-03, CLAIM-01, CLAIM-02, CLAIM-03]
completed: 2026-11-17
---

# Phase 14 Plan 02: Notice builder (2.0.3) Summary

Completed the 2.0.3 notice builder: derived `build_notice` (re-pin framing, 29 mutations, 7 lineage rows, digest-scope proof, verify-at-pin section), `render_markdown`, a closed `schema()`, the byte-rebuild validation pair and the CLI.

## Tasks
1. build_notice with what_changed, mutations, lineage, scope error, decisions, verify and Hayes steps - done.
2. render_markdown, closed schema(), validate pair, CLI - done.

No code commit (per plan; Plan 04 commits after pytest). The builder is still untracked. No generated notice, schema or doc was written.

## Smoke check (in memory, nothing written)
- py_compile OK.
- load_inputs, build_notice and validate_notice_object pass; 29 mutations, 7 lineage rows, 121 rendered lines.
- Schema accepts a 'd'*40 substitution at verify.steps[0].checkout and digest_scope_error.previous_commit (D-15 derivation paths).
- Schema rejects a tampered pin.version by 'const'.
- git status shows no generated notice files; frozen builders and publisher untouched.

## Deviations from Plan
None. Minor choices: step 3's "at or after the commit that adds this notice" text is in pass_means; step number is an integer field; notice_date is a schema const of NOTICE_DATE.

## Known Stubs
None.

## Self-Check: PASSED
