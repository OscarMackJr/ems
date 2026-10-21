---
phase: 07-lineage-source-and-per-digest-scope
plan: 04
requirements: [LIN-01]
key-files:
  created: [tests/test_archive_assessment_normalisation_claims.py]
metrics:
  tasks: 2
  files: 1
---

# Phase 7 Plan 04: Normalisation claim audit tests Summary

Seven read-only pytest recompute tests (`*normalisation_claim`) prove every digest_normalisation claim outside source_lineage: publication record, certification, manifest artifacts, manifest publisher script (git blob at publication commit), traceability decision records, sign-off, and reply pin plus reply doc prose.

## Tasks
Tasks 1 and 2 were written together in one file and committed as one commit: cb8f6fb (test(07-04)). The plan separates them but both touch the same single file.

## Deviations
None. No script, schema, registry, generated or reply file was modified (D-14). Field names were read from the committed files before writing assertions. The reply prose string lives in docs/DEMO3_W1_REQ_001_REPLY.md (not the reply JSON), so the test checks it there.

## Test results: pending orchestrator run
Orchestrator must run in PowerShell (scratch = C:\Users\OMack\AppData\Local\Temp\claude\C--temp-standars-ems\79172311-e155-47bc-9abe-2867de1f66b8\scratchpad):
- `.\.venv\Scripts\python.exe -m pytest tests\test_archive_assessment_normalisation_claims.py -p no:cacheprovider -q --basetemp <scratch>\bt4`
- `.\.venv\Scripts\python.exe -m pytest tests -k normalisation_claim -p no:cacheprovider -q --basetemp <scratch>\bt4b` (expect 7 tests)
- `.\.venv\Scripts\python.exe -m pytest tests -k archive_assessment -p no:cacheprovider -q --basetemp <scratch>\bt4d` (expect only the 3 red tests from 07-02-PLAN)

If any claim test fails, stop and raise to the user (D-13); do not edit digests.

## Self-Check: PASSED (file exists, commit cb8f6fb exists; tests not run by executor)

## Orchestrator Test Run (2026-10-20)

- `pytest tests -k normalisation_claim`: 7 passed. Every D-13 claim holds; no claim is false.
- `pytest tests -k archive_assessment`: 499 passed, 0 failed. The red window is not open yet, because 07-02 has not run.

