---
phase: 13-certified-republication-2-0-3
plan: 04
subsystem: archive-assessment v2 publication / CI
tags: [push, CI, D-01, D-04, D-08, PUB-12]
requirements: [PUB-10, PUB-11, PUB-12]
requirements-completed: [PUB-10, PUB-11, PUB-12]
key-files:
  created:
    - .planning/phases/13-certified-republication-2-0-3/13-VERIFICATION.md
  modified:
    - .planning/STATE.md
metrics:
  completed: 2026-11-17
---

# Phase 13 Plan 04: Push, CI and evidence Summary

After Oscar Mack's go-ahead, the branch was pushed with a **plain push** (the token fallback was not used), so its remote tip is WR03 = 5498002c5eea3a6d9e3bfbb6766119880bb36804. **CI run 44134035073** (workflow_dispatch) concluded success at headSha WR03, with jobs validate and archive-assessment both successful. No PR or tag was created, and the remote tag list is unchanged. The evidence is recorded in 13-VERIFICATION.md and STATE.md, in **evidence commit 144934b2415ddc78634782f794e833371e4900f3** (`docs(13-04): record 2.0.3 publication and CI evidence`).

## Checkpoint
- Captured before presenting the checkpoint:
  - pre-push `git ls-remote --tags origin`, verbatim:
```
88550ed7bfb827bc46a11355f0655867977a3b43	refs/tags/ems-v0.4.5-wave1
6c69f2230f4a26ebd4d795b9e480c210bcfeb1e8	refs/tags/ems-v0.4.5-wave1^{}
bd0b24bb2603e6fdbad0a9ad301f4aff339482a5	refs/tags/ems-v0.5.0-wave2b
d5c1a73208d716ad2ca33906a0b8ae53a82e8457	refs/tags/ems-v0.5.0-wave2b^{}
a2235e0725a39010340707f8e5ce6b6abb6d4e27	refs/tags/ems-v0.6.0-wave2c
98b0b75fe2c5eea4b61530ce98bdf29742e8f2d4	refs/tags/ems-v0.6.0-wave2c^{}
```
  - `git log --oneline WR03..HEAD`, before the push: `3fd54ac docs(13-02,13-03): publication and record summaries, tracking after waves 2-3`;
  - commits to push: 85 (`origin/...49c7b08..WR03`);
  - `merge-base --is-ancestor REC WR03` exits 0;
  - the scoped `git status` over the 10 paths, the record and the WR-03 test was empty.
- Resume signal, verbatim: `push approved`.
- The remote tip when the signal was received was 49c7b088cb2773222bd3d98532273c1aac5eadf7.

## Task 1: Push and CI
- Pre-push: REC is an ancestor of WR03 and the origin tip is an ancestor of WR03 (fast-forward). `Env:GIT_*` count was 0.
- `git push origin "5498002c5eea3a6d9e3bfbb6766119880bb36804:refs/heads/feature/ems-aa3-archive-applicability-authority"`: `49c7b08..5498002`, exit 0. **Plain push; the fallback was not used.** Afterwards `Env:GIT_*` count was 0, and `ls-remote` shows the tip = WR03.
- `gh workflow run ems-validate.yml --ref feature/ems-aa3-archive-applicability-authority` started run 44134035073 (created 2026-11-17T17:10:31Z, event workflow_dispatch, headSha WR03).
- `gh run watch --exit-status`: exit 0.
- `gh run view`: conclusion success; headSha 5498002c5eea3a6d9e3bfbb6766119880bb36804; jobs validate success and archive-assessment success.
- Post-run checks:
  - `git diff --quiet PUB WR03 -- <10 paths>` exits 0, and `git diff --quiet REC WR03 -- <record>` exits 0;
  - `gh pr list --head ...` is empty;
  - `git tag --points-at` returns nothing for PUB, REC and WR03;
  - the post-push `git ls-remote --tags origin` is byte-identical to the pre-push baseline above.

## Task 2: Evidence
- 13-VERIFICATION.md is written (status passed, D-01 SC3 and SC4 readings, Push scope). STATE.md has the [Publication 2.0.3] entry and the Current Position update.
- They are committed as 144934b2415ddc78634782f794e833371e4900f3, which contains only those two files.
- The secret grep (`x-access-token:…`, `gh[pousr]_…`) over .planning finds nothing. `git diff --name-only WR03 HEAD -- . ':(exclude).planning'` is empty.
- Local-only .planning commits after WR03: 3fd54ac, 144934b, and this SUMMARY's commit. The Phase 14 push publishes them.

## Deviations from Plan
- None beyond the in-process clearing of the `GIT_*` variables the harness sets (see 13-01).

## Self-Check: PASSED
