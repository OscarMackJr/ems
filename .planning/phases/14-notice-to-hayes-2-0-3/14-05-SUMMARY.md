---
phase: 14-notice-to-hayes-2-0-3
plan: 05
subsystem: notice
tags: [commit, ci, push, d-14]
requires:
  - phase: 14-04
    provides: approved notice files, code commit 8142341
provides:
  - notice commit e10b240
  - CI commit c04763d
  - pushed branch at c04763d97e6356fc0143b713e70e3ca680044115, ems-validate.yml green
affects: []
key-files:
  created:
    - docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md
    - registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json
  modified:
    - .github/workflows/ems-validate.yml
metrics:
  tasks: 3
  files: 4
  completed: 2026-11-17
---

# Phase 14 Plan 05: Notice commit, CI line, push and CI Summary

The approved 2.0.3 notice and the CI validator line are committed separately, the branch is pushed after Oscar Mack's "push", and ems-validate.yml is green at the pushed head.

## Task 1: Commits

- `--validate` re-run before staging: PASS.
- `e10b240 docs(14): add 2.0.3 notice to Hayes`: exactly the three notice files.
- `c04763d ci(14): validate the 2.0.3 notice`: exactly .github/workflows/ems-validate.yml, one added line (`python scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py --validate`), no removed line.
- Frozen-artifact diffs against 1544dc1 and 87a46d1: empty.
- .planning/config.json, registry/adjudication_rules.json, registry/policy_decisions.json: still modified and unstaged.

## Task 2: Push approval (D-14)

22 commits listed with `git log origin/...HEAD`; only 8142341, e10b240 and c04763d touch files outside .planning/. Oscar Mack replied "push" on 2026-11-17.

## Task 3: Push and CI

- Plain `git push` succeeded first time (5498002..c04763d); the token workaround was not needed.
- HEAD equals origin/feature/ems-aa3-archive-applicability-authority: c04763d97e6356fc0143b713e70e3ca680044115.
- Dispatched run 44160179245 (workflow_dispatch), headSha c04763d97e6356fc0143b713e70e3ca680044115: status completed, conclusion success; jobs validate and archive-assessment both success. No push-triggered run appeared for this head.
- No PR created; `git tag --points-at HEAD` empty.
- Secret-pattern grep over the phase directory: the only hit is the acceptance-criterion text in 14-05-PLAN.md; no token.

Sending the notice to Hayes stays the EMS authority's action.

## Addendum: review fixes, re-approval and second push (2026-11-17)

- `/gsd-code-review 14 --fix` fixed WR-01 (1b5f6c2), WR-02 (e15eeb9) and WR-03 (fcd9f7e); the orchestrator narrowed one over-broad WR-02 test assertion (12842fd). See 14-REVIEW-FIX.md.
- The notice was regenerated with --emit-schema/--build; --validate PASS; the 2.0.3 notice tests passed (89 + the corrected test). The Markdown diff changed only the step 2 sentence and the outcome table (5 rows; re-pin only after steps 1, 2 and 3 all pass).
- Oscar Mack re-approved the regenerated wording ("approved", D-14) and approved the second push ("push").
- Notice regeneration commit: b23a623. Plain `git push` c04763d..b23a623; HEAD equals origin at b23a623e24515b8be5892466df47ba397671a281.
- Dispatched run 44171475201 (workflow_dispatch) at headSha b23a623e24515b8be5892466df47ba397671a281: completed, success; validate and archive-assessment jobs success. This supersedes run 44160179245 as the final head check.
- Hayes verifies step 3 at or after b23a623; the pin stays 1544dc19ba235d732c832d1651895550ed5a265d. No PR, merge or tag.

## Deviations from Plan

None. Run inline by the orchestrator.

## Self-Check: PASSED
