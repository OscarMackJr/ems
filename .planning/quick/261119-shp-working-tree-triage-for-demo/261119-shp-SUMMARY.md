---
quick_id: 261119-shp
status: complete
date: 2026-11-19
---

# Quick Task 261119-shp: Working tree triage for demo — Summary

The working tree on `feature/ems-aa3-archive-applicability-authority` went from 143 entries to clean (only this
task's files, committed here). No work was lost. Executed by the orchestrator (git cannot run in subagents on this
machine); rulings are in 261119-shp-PLAN.md.

## Results

1. **Parked (groups B + C): 111 files** on local branch `wip/aug-2026-domain-authorities`, commit
   `f6bb4a3` (parent `428e00a`). These are 109 previously untracked August files and the content changes to
   `registry/adjudication_rules.json` and `registry/policy_decisions.json`. Before the park, every file's
   `git hash-object` was recorded in a manifest. After the commit, `git rev-parse f6bb4a3:<path>` matched all 111
   (0 mismatches). The branch was not pushed (ruling "Keep local"). On switching back, both registry files returned
   to their HEAD content.
2. **Restored (group A): 26 files** with `git restore`, after a re-check showed that none of them had a content
   diff ignoring CR/EOL.
3. **Cleared (group D):** 8 `.pytest-*` folders were deleted, and so was
   `.planning/phases/06-address-tech-debt-publication-gate-hardening-2-0-1/.gitkeep`. `.pytest-*/` was added
   to `.gitignore`.

## Evidence

- After the steps, `git status --porcelain` showed only ` M .gitignore` and this task's directory.
- `python scripts/publish_archive_assessment_applicability_authority.py --validate` printed PASS (exit 0)
  before and after the triage.

## Notes

- **Demo pin:** it stays at 755cb27. This commit adds one non-`.planning` change (`.gitignore`) on top of the
  feature branch. The authority, publisher, registry and test files are untouched.
- **Retrieving the parked work:** use `git switch wip/aug-2026-domain-authorities`, or
  `git checkout f6bb4a3 -- <path>`. The work is unreviewed and not for merge as-is. 24 of the 109 files are
  byte-identical to files on `feature/external-review-*` branches.
- **Restore scope:** `git restore` on group A also restored the two 2.0.3 notice files. That removes the
  "line-ending only" caveat recorded in 261119-sd5-DEMO-PIN.md section 6.
