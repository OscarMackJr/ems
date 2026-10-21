---
phase: 07-lineage-source-and-per-digest-scope
plan: 01
subsystem: archive-assessment lineage
tags: [aa1, manifest, gitattributes, lineage]
requires: []
provides:
  - "Committed AA1 manifest with CRLF bytes preserved (raw sha256 f0da8e2e…9b4b)"
affects: [07-02, 07-03]
key-files:
  created:
    - generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json
  modified:
    - .gitattributes
key-decisions:
  - "File-specific -text rule (no ems-aa1/** wildcard); the 13 listed AA1 artifacts stay untracked (D-08)"
requirements-completed: [LIN-03]
duration: 5min
completed: 2026-10-20
---

# Phase 7 Plan 01: AA1 Manifest Commit Summary

**The AA1 analysis-artifact manifest is committed on its own under a `-text` rule. Its raw-byte SHA-256 is `f0da8e2e45c306ccc42ae96f25a19922668f3eedecdb26006f13514e24ad9b4b`, and it reads back unchanged both from the git blob and from a fresh checkout.**

## Accomplishments
- Added `generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json -text` to `.gitattributes`, after the AA2 rule (D-06). This was the only change to that file (1 insertion).
- Force-added the manifest by explicit path. It is gitignored under `generated/`. Commit `bb7c067` contains exactly two paths (D-05).
- `git ls-files --eol` shows `i/crlf w/crlf attr/-text`, the same as the AA2 approval files: the CRLF bytes are stored without conversion.

## Verification
| Check | Result |
|-------|--------|
| Working-tree raw sha256, before staging | f0da8e2e…9b4b |
| Index empty before staging | yes |
| `git show HEAD:<manifest>` raw sha256 (bytes, Python) | f0da8e2e…9b4b |
| Fresh `git worktree` checkout raw sha256 | f0da8e2e…9b4b |
| `git show --name-only HEAD` | `.gitattributes`, manifest only |
| `git ls-files generated/archive-assessment/ems-aa1` | manifest only (D-08) |
| Unrelated `registry/adjudication_rules.json`, `registry/policy_decisions.json` | still unstaged ` M` |

## Task Commits
1. **Tasks 1 and 2, `.gitattributes` rule and manifest commit:** `bb7c067` (chore). The plan requires one commit, so both tasks share it.

## Deviations from Plan
- The fresh-checkout worktree was created in the session scratchpad instead of `$env:TEMP`, because of permission problems with the default temp directory on this machine. The check itself is the same.

## Issues Encountered
None. The red window is not opened, because this plan changes data only.

## Self-Check: PASSED
