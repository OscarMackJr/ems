---
phase: 07-lineage-source-and-per-digest-scope
plan: 03
subsystem: testing
tags: [pytest, lineage, validate_lineage, git, sha256]
requires: [07-01, 07-02]
provides:
  - Standalone pytest coverage for validate_lineage (D-10, D-11, D-12) and the AA1 manifest (LIN-03)
affects: [tests]
key-files:
  created: [tests/test_archive_assessment_lineage_validation.py]
  modified: []
requirements: [LIN-02, LIN-03]
metrics:
  completed: 2026-10-20
---

# Phase 7 Plan 03: Lineage validation tests Summary

One new test file covers `validate_lineage` hermetically (temp git repo, CRLF fixtures, monkeypatched `MODULE.ROOT`) and the committed AA1 manifest.

## What was built

- Hermetic fixture builds a complete 8-label lineage from CRLF files plus a temp git repo with `* -text`.
- D-12 tamper tests: changed byte, changed declared normalisation, changed recorded digest, parametrised over RAW_BYTES (aa1_manifest) and CRLF_TO_LF (catalog_reference): 6 cases. Commit-pinned (v1_baseline, supersedes, supersedes governance digest) digest and normalisation negatives, plus a test proving the blob, not the working file, is used.
- D-10/D-11: nonexistent 40-hex commit, short commit, option-like commit rejected before any subprocess call, missing path, missing working file, unknown normalisation, absolute and `..` paths, missing label, git unavailable.
- Real-repo (read-only): validate_lineage positive (skips if shallow), expected normalisations, tampered aa1 digest raises.
- LIN-03 (`aa1` in names): tracked, HEAD blob raw sha256 equals hard-coded literal f0da8e2e...9b4b, `.gitattributes` line, `git check-attr` reports `text: unset`.

## Deviations from Plan

Tasks 1 and 2 both modify the same new file and were written together; committed as a single commit rather than two. Nothing else deviated. Publisher and all other files untouched.

## Verify commands (pending orchestrator run)

- `.\.venv\Scripts\python.exe -m pytest tests\test_archive_assessment_lineage_validation.py -p no:cacheprovider -q --basetemp <scratch>\bt3` - pending orchestrator run
- `... -k aa1` (at least 3 tests) - pending orchestrator run
- `pytest tests -k archive_assessment -p no:cacheprovider -q` expecting exactly the 3 accepted red tests - pending orchestrator run

Executor did not run python/pytest per instructions.

## Self-Check: PASSED (file exists; commit recorded below by orchestrator log)
