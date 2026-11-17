---
phase: 14-notice-to-hayes-2-0-3
plan: 01
subsystem: archive-assessment-notice
tags: [notice, pinned-rerun, lineage, digest-scope]
requires: []
provides:
  - "frozen constants, git helpers and history guard for the 2.0.3 notice builder"
  - "pinned_mutation_run, check_rerun, lineage_entries, digest_scope_error, rows_differing, load_inputs"
affects: [14-02, 14-03, 14-04]
key-files:
  created:
    - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
  modified: []
requirements-completed: [CLAIM-01, CLAIM-02, CLAIM-03, NOTICE-03]
duration: short
completed: 2026-11-17
---

# Phase 14 Plan 01: Notice builder core (2.0.3) Summary

Standalone 2.0.3 notice builder core that reruns the 29 negative mutations from pinned git blobs in a temp dir, recomputes all 7 lineage digests, and computes the raw/LF digest-scope proof.

## Tasks
1. Constants, copied helpers, history guard, pure claim checks - done.
2. Pinned mutation rerun (D-01) and load_inputs (10-tuple, rerun last) - done.

No code commit was made (per plan, Plan 04 commits the code after the orchestrator's pytest run). The new script is untracked.

## Smoke check (run via Bash)
- py_compile: OK
- load_inputs(): rerun outcomes 29; check_rerun entries 29; lineage_entries 7
- digest_scope_error pairs (raw/LF): aa1_manifest f0da8e2e/06e39f7b, aa2_approval de170ebc/248b6e38, aa2_closure ed589d76/66662df3
- rows_differing(2.0.3, 2.0.2) = (0, 80)
- Live publisher and decisions builder: no git status changes; no GIT_DIR/worktree strings in the builder.

## Deviations from Plan
None. All pinned names (VERSION, validate_governance_decisions, validate_publication, schema, sha_text, jtext, validate_signoff, run_mutations, AT_PIN_DEFERRED, _BUILDER, V1_AUTHORITY, BUILDER_SCRIPT) exist at 1544dc1 as used. Minor: rows_differing is called with the 2.0.2 authority as specified; `argparse` is imported for Plan 02's CLI and is currently unused.

## Known Stubs
None. build_notice, render, schema and CLI are intentionally deferred to Plan 02.

## Self-Check: PASSED
