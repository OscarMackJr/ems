---
phase: 14-notice-to-hayes-2-0-3
plan: 04
subsystem: notice
tags: [pytest, notice, generation, d-14-review]
requires:
  - phase: 14-03
    provides: tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
provides:
  - code commit 8142341 (builder + tests)
  - generated, validated and approved notice files (uncommitted; Plan 05 commits them)
affects: [14-05]
key-files:
  created:
    - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
    - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
    - docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md
    - registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json
    - schemas/archive_assessment_demo3_w1_req_001_notice_2_0_3.schema.json
metrics:
  tasks: 3
  files: 5
  completed: 2026-11-17
---

# Phase 14 Plan 04: Test gate, code commit, generation and review Summary

The orchestrator ran the tests from PowerShell (fresh `--basetemp`, `-p no:cacheprovider`), committed the builder and tests, generated the three notice files with `--emit-schema` then `--build`, and Oscar Mack approved the rendered Markdown (D-14).

## Task 1: Orchestrator test gate

| Run | Result | pytest exit |
| --- | --- | --- |
| 2.0.3 notice tests, before generation | 84 passed, 5 failed, 0 skipped | 1 |
| 5 failures rerun with `--tb=line` | all missing-file errors (`not generated` / FileNotFoundError on registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json) | 1 |
| 2.0.2 notice + reply tests | 242 passed | 0 |

The 5 failures were exactly the allowed set: test_committed_notice_files_validate, test_cli_rejects_missing_and_combined_modes[argv0..2], test_live_publisher_and_decisions_builder_edit_does_not_change_notice.

## Task 2: Code commit and generation

- `8142341 feat(14-04): add 2.0.3 notice builder and tests`: lists exactly the builder and the test file.
- `--emit-schema` exit 0; `--build` PASS; `--validate` PASS.
- JSON: publication_commit 1544dc1…, publication_record_commit 87a46d1…, authority id …-2.0.3, version 2.0.3, negative_mutation_count 29, 29 mutations, 7 lineage, 3 digest_scope_error digests, 3 verify steps, 4 outcomes.
- Markdown contains every required string; forbidden-word count 0.
- Frozen-artifact diffs against 1544dc1 and 87a46d1: empty.
- The three generated files are untracked and unstaged; .planning/config.json, registry/adjudication_rules.json and registry/policy_decisions.json remain modified and unstaged.

## Task 3: D-14 review

- Pre-review rerun of the 2.0.3 test file against the generated files: 89 passed, 0 skipped, pytest exit 0.
- Oscar Mack replied "approved" on 2026-11-17. No wording changes.

## Deviations from Plan

None. Plan 04 was run inline by the orchestrator because pytest must run from the main session.

## Self-Check: PASSED
