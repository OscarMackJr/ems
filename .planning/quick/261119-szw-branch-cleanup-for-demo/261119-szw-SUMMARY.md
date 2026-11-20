---
quick_id: 261119-szw
status: complete
date: 2026-11-19
---

# Quick Task 261119-szw: Branch cleanup for demo — Summary

Executed by the orchestrator. The rulings are recorded in 261119-szw-PLAN.md. The repository is public: the tags,
the remote deletions and the closing of PR #8 are visible.

## Results

1. **Tags pushed to origin.** Both are annotated, and `ls-remote` peeled each to the commit shown:

   | Tag | Commit | Marks |
   |---|---|---|
   | `ems-aa3-authority-2.0.3` | `1544dc19ba235d732c832d1651895550ed5a265d` | Authority 2.0.3 publication |
   | `ems-demo-2026-12` | `755cb275564f44b0af15dcad86267d809fe23f79` | Demo commit |

   No PR was opened.

2. **Merged and patch-equivalent cleanup.**
   - Five clean worktrees were removed: ems-external-review-closure, -p2, -p3, -publish, and the detached
     ems-post-merge-baseline-verify.
   - 12 local branches were deleted: 9 merged into origin/main and 3 patch-equivalent.
   - The 3 patch-equivalent tips were first tagged `archive/<branch>`:
     - `chore/wave2c-baseline-registration` 2e7993b
     - `feature/wave2d-initialization` 98a4883
     - `feature/wave2d-scope-population` fa8bea1
   - Local `main` was fast-forwarded to origin/main de57bdf.

3. **Old Wave 2.** Local archive tags were created on 4 tips, then the 4 branches were deleted:

   | Branch | Archived tip |
   |---|---|
   | `feature/wave2-closeout` | 76563d1 |
   | `feature/wave2c-remediation` | 2547ea2 |
   | `feature/wave2-control-scope` | 5b9309e |
   | `feature/wave2d-pilot-ctrl018-baseline` | 33f48a6 |

   PR #8 was closed with a comment.

4. **Remote.** 10 branches were deleted, using the gh-token extraheader push. After `git fetch --prune`, origin has
   only `main` and `feature/ems-aa3-archive-applicability-authority`.

## Verification

- All 16 deleted branch tips are reachable, either from origin/main or from an `archive/*` tag. 0 are
  unreachable.
- The 7 AA3p/AA4 branches and their worktrees are unchanged, under the ruling "Leave as is". They are still
  local-only, with about 150 unique commits.
- `wip/aug-2026-domain-authorities` (f6bb4a3) and the feature branch are unchanged.
- The working tree contains only this task's files.

## Notes

- The `archive/*` tags are local only, not pushed. To restore a branch, run `git branch <name> archive/<name>`.
- After the demo:
  - Decide on merging the feature branch into main: 422 commits and 387 files.
  - Decide what happens to the local-only AA4 chain.
