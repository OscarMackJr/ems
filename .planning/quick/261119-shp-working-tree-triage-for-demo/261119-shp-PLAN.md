---
quick_id: 261119-shp
type: quick
mode: quick
autonomous: false
---

# Quick Task 261119-shp: Working tree triage for demo

Day 1-3 item of the 10-day demo plan (see 261119-sd5-DEMO-PIN.md). Clear the 143-entry working tree on
`feature/ems-aa3-archive-applicability-authority` without losing any work.

## Developer rulings (2026-11-19, AskUserQuestion in the main session)

- August work: "Park on a wip branch (Recommended)"
- EOL-only files: "Restore to HEAD (Recommended)"
- Temp dirs: "Delete + gitignore (Recommended)"
- Push wip: "Keep local"

## Inventory (orchestrator, 2026-11-19, at HEAD 428e00a)

| Group | Count | Finding |
|-------|-------|---------|
| A. Tracked, line-ending-only diff | 26 | `git diff --ignore-cr-at-eol --ignore-space-at-eol` empty: 24 `.planning` files (phase 07-10 and 14 SUMMARYs, 261019-st1 SUMMARY, config.json) plus `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md` and `registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json` |
| B. Tracked, real content change | 2 | `registry/adjudication_rules.json` (version 4.5-release-integrity-adjudication-v1), `registry/policy_decisions.json`; blobs on no branch |
| C. Untracked August work (2026-08-13..16) | 110 files | docs/, registry/, registry/wave2d/, schemas/, schemas/contracts/, scripts/, tests/, requirements-dev.txt; 24 identical on feature/external-review-*, 86 on no branch |
| D. Temp/stray | 8 dirs + 1 | `.pytest-*` folders; `.planning/phases/06-.../.gitkeep` |

## Tasks (orchestrator executes; git cannot run in subagents on this machine)

1. **Park B + C.** `git switch -c wip/aug-2026-domain-authorities`; stage group B and C by explicit path only; commit;
   switch back to `feature/ems-aa3-archive-applicability-authority`. Verify: every parked file's blob on the wip
   commit equals the pre-park `git hash-object`; groups B and C no longer appear in `git status`. Branch stays local.
2. **Restore A.** `git restore --` the 26 paths. Verify: none shows in `git status`.
3. **Clear D.** Delete the 8 `.pytest-*` folders and the `.gitkeep`; append `.pytest-*/` to `.gitignore`.
   Verify: `git status --porcelain` is empty except this task's files; validator `--validate` still PASS.

Commit on the feature branch: `.gitignore`, this PLAN, SUMMARY, STATE.md — by explicit path. Demo pin 755cb27 is unaffected.
