---
phase: 09-certified-republication-2-0-2
plan: 01
subsystem: archive-assessment v2 publisher
tags: [red-window, D-07, D-08, D-04, PUB-07, PUB-08]
requirements: [PUB-07, PUB-08]
key-files:
  created:
    - .planning/phases/09-certified-republication-2-0-2/09-BASELINE-RED.md
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - tests/test_archive_assessment_lineage_validation.py
metrics:
  completed: 2026-11-12
---

# Phase 9 Plan 01: Open the red window — 2.0.2 publisher logic Summary

The publisher now has VERSION 2.0.2. SUPERSEDED_V2_0_1 replaces SUPERSEDED_V2_0_0 throughout: commit 31addfa, authority LF sha 7be5eb88…, decisions LF sha 4e746d1f…. The values were derived from git and the 2.0.1 record, and a git-history test checks them. validate_publication compares all 80 rows on four decision fields, plus the control-id set and the top-level applicability_decision_ids, against the 2.0.1 authority read through git_show (D-08). A content mismatch raises AuthorityError; GitHistoryError propagates and mutation_gates re-raises it. validate_signoff takes an optional authority_id and version, with defaults bound to the live constants. A D-04 byte-identity test is in place and skips until the 2.0.2 record exists. The mutation count stays at 29.

## Commits
- 0f67df7: docs — baseline red set (orchestrator pytest, before any code change)
- 69ea357: feat — VERSION 2.0.2, SUPERSEDED_V2_0_1 everywhere, parameterised validate_signoff, retargeted tests, 3 behavior tests
- 4f8b609: docs — red set after Task 2a
- 23cfad6: feat — D-08 80-row comparison and tests: row tamper ×4, decision-id tamper, GitHistoryError through mutation_gates, D-04 byte identity
- 941e81c: fix — D-10 catalog fixture serves the 2.0.1 blob (orchestrator)
- 6784ce9: docs — red set after plan 01

## Verification
Orchestrator runs, from PowerShell with `--basetemp` in the session scratchpad:
- Baseline, `-k archive_assessment`: 694 passed, 3 failed (the 3 accepted reds).
- After 2a, three v2 modules: 376 passed, 2 failed.
- After 2b plus the fix: 384 passed, 2 failed. The remaining failures are test_committed_schema_equals_schema_function and test_real_published_files_validate, both accepted reds that stay red until 09-04.

Every commit was staged by explicit path. No protected path (registry/adjudication_rules.json, registry/policy_decisions.json, .planning/config.json) is in any commit.

## Deviations from Plan
- **[Rule 3 – blocking] Fixture support for D-08 (23cfad6).** The `env` and `fake_git_show` fixtures in the publication tests now serve the real 2.0.1 blob, because the new comparison reads git history under a temp ROOT.
- **[Rule 1 – bug] D-10 lineage test (941e81c).** test_d10_live_catalog_edit_or_delete_does_not_change_build_or_validation used a fixture repo with no 2.0.1 history and failed closed with GitHistoryError after D-08. The orchestrator fixed it the same way, and the red set is back to the accepted two.
- The 2.0.1 blob is not cached, so a mutation run makes about 30 extra `git show` calls. Runtime stayed acceptable (about 175 s for the three modules).

## Self-Check: PASSED
