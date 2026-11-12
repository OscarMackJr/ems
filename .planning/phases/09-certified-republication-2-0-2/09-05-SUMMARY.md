---
phase: 09-certified-republication-2-0-2
plan: 05
subsystem: archive-assessment v2 publication
tags: [record, red-window-close, CI, PUB-07, PUB-08, PUB-09]
requirements: [PUB-07, PUB-08, PUB-09]
key-files:
  modified:
    - registry/archive_assessment_applicability_authority_v2_publication_record.json
  created:
    - .planning/phases/09-certified-republication-2-0-2/09-VERIFICATION.md
metrics:
  completed: 2026-11-12
---

# Phase 9 Plan 05: Close the red window Summary

The publication record was written with `--record-publication ae15c74…` and committed alone in a71257e. It names 2.0.2, authority a44eea1f…, manifest 9991228a…, and publication commit ae15c74.

Checks at the record commit:
- Plain `--validate` and all five CI validators print PASS.
- The full `-k archive_assessment` suite gives 720 passed and 0 failed, so the red window is closed.
- Publication bytes are identical between ae15c74 and a71257e.

After Oscar Mack's "Push approved", the branch was pushed: 81 commits, now 5c1926d..a71257e on origin. ems-validate.yml was dispatched as run 43332405316. It finished green (validate and archive-assessment) at headSha a71257e, the record commit. No PR, merge or tag was created.

## Commits
- a71257e: feat — publication record (record-only commit)
- planning: 09-VERIFICATION.md, 09-05-SUMMARY.md, STATE.md (run id and SHAs, D-06)

## Deviations from Plan
- The plain `git push` through the credential helper worked, so the GIT_CONFIG extraheader workaround was not used.
- The orchestrator executed the plan inline, because it needs PowerShell and the blocking push approval.

## Self-Check: PASSED
