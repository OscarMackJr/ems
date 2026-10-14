---
phase: 06-address-tech-debt-publication-gate-hardening-2-0-1
plan: 05
subsystem: archive-assessment v2 publisher
tags: [d-06, d-08, d-09, d-10, d-12, d-13, d-17, d-18, d-19, d-20, d-21, wr-02, wr-03, wr-06]
requires: ["06-04"]
provides:
  - publisher 2.0.1 code (version, lineage, D-12 binding, executed mutation harness, script-digest manifest field)
key-files:
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - schemas/archive_assessment_applicability_authority_v2.schema.json
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - tests/test_archive_assessment_applicability_authority_v2.py
decisions:
  - "Mutation records are a NamedTuple (a dataclass crashes when the module is loaded by spec with postponed annotations)"
  - "Prohibitions (evaluator_executions, hayes_modifications, target_comparisons) stay documented zero constants, backed by a source test with no subprocess or evaluator call"
  - "Constants for 2.0.0 live in code, so any later decision amendment turns the 2.0.1 validator red until a new version updates them (intended)"
metrics:
  tasks: 6
  files: 4
  completed: 2026-10-14
requirements: [D-01, D-06, D-08, D-09, D-10, D-12, D-13, D-17, D-18, D-19, D-20, D-21, D-22]
---

# Phase 6 Plan 05: Publisher 2.0.1 Code Summary

The publisher now builds 2.0.1 with lineage to 2.0.0 and v1, and its certification is computed from 26 executed negative mutations and a semantic check over all 80 rows.

## What changed

- VERSION 2.0.1 and AUTHORITY_ID derived from it; SUPERSEDED_V2_0_0 and the full 40-hex V1 baseline commit are code constants.
- validate_publication binds the decisions-file LF digest to the 2.0.0 constant and re-derives every row's decision fields and applicability_decision_ids from the decision records.
- Schema: closed lineage with required keys and const/sha pins, rule field may appear once (maxContains), record_count const 21. Emitted with `--emit-schema` only.
- PUBLISHED_ON removed; the date comes from the sign-off. Manifest has top-level `publisher_script`; validate rebuilds with the recorded digest. Honest limit: a later edit that changes what the publisher builds still turns the rebuild-compare red (intended).
- 26 `Mutation` records (17 old + 9 new); `run_mutations`, `mutation_gates`, `semantic_conflicts`. An accepted mutation or a conflict raises before any write. Negative file entries carry id, description, rejected_by, result and the `mutation` key.
- Dry-run summary lists 21 decided and 59 undecided controls, the rules, the authority LF sha256 and the supersession line.

## Derivation values (from git show)

- 2.0.0 publication commit 54a7fd09114704a97a7a48fce5f89aebeb48c90a
- authority LF sha256 de36e227be4ccc95f4a8a8a08247cf6e49f7682908c7f425f8cc02bbaa1da353
- decisions LF sha256 4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f
- v1 commit 62a8955dc28d9458cd1167fad314926e057c31fc
- Dry run: exit 0; 2.0.1 authority LF sha256 7be5eb8869a8897ee6d55051f9d872fee9a8a35bdbd2ad5093d40e8a1d489e4f; line "Version 2.0.1 supersedes ...2.0.0 version 2.0.0 (commit 54a7fd0). No decision changed ... equals the 2.0.0 value."

## Deviations from Plan

**1. [Rule 3 - plan assumption wrong] Red set is 18, not 5.** The reply builder validates the committed 2.0.0 sign-off against the now-2.0.1 constants, so 15 more reply-module tests fail until plans 06-06 and 06-08. The user accepted this (RED-LIST AMENDMENT in the plan). No shims or skips.

Exact failing set at commit 730f51e (`pytest -k archive_assessment`: 18 failed, 458 passed):
- v2_publication: test_real_published_files_validate
- reply module: test_real_reply_files_validate, test_publisher_still_valid_and_digest_matches_manifest, test_validate_reply_accepts_unmutated_reply_from_temp_file, test_validate_reply_rejects_loosened_schema_file, test_built_reply_counts, test_each_entry_matches_authority_and_decision_record, test_the_three_rules, test_first_sentence_for_all_records, test_mutation_swapped_aa4_id, test_mutation_bad_aa4_format, test_mutation_flipped_state, test_mutation_altered_rule, test_mutation_removed_and_extra_control, test_mutation_sha_and_digest, test_mutation_dual_role_text, test_mutation_absolute_path, test_markdown_content
- CLIs: publisher `--validate`, reply `--validate` (decisions builder `--validate` passes)

## Known Stubs

None.

## Commits

- 730f51e: feat(06-05): publisher 2.0.1 code - executed certification, lineage, schema, script-digest manifest

## Self-Check: PASSED
