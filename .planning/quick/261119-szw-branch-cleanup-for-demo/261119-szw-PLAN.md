---
quick_id: 261119-szw
type: quick
mode: quick
autonomous: false
---

# Quick Task 261119-szw: Branch cleanup for demo

Day 3-5 item of the 10-day demo plan. The repo `OscarMackJr/ems` is PUBLIC.

## Developer rulings (2026-11-19, AskUserQuestion in the main session)

- Demo pin: "Tags, no PR (Recommended)"
- Merged branches: "Delete local + remote (Recommended)"
- Old Wave 2: "Archive tags, then delete (Recommended)"
- AA4 work: "Leave as is (Recommended)"

## Inventory (orchestrator, 2026-11-19, after `git fetch --prune`)

- `origin/main` = de57bdf (2026-08-16). Local `main` is 12 behind it.
- **Merged into origin/main (9):** feature/external-review-{cross-repo-traceability, ems-authority-publication,
  remediation-closure, retention-authority-reconciliation} (each checked out in a clean worktree),
  feature/wave2d-{batch-20260814-baseline, ctrl018-remediation-transition, evaluation-contract, pilot-baseline,
  pilot-ctrl010-baseline}.
- **No unique patches; remote gone (3):** chore/wave2c-baseline-registration, feature/wave2d-initialization,
  feature/wave2d-scope-population. `git cherry` shows 0 `+`, but these are not ancestors of main.
- **Unmerged old Wave 2 (4):** feature/wave2-closeout (5, remote gone), feature/wave2c-remediation (6, remote gone),
  feature/wave2-control-scope (1, contained in wave2-closeout), feature/wave2d-pilot-ctrl018-baseline (1, PR #8 open).
- **Untouched:** the AA3p/AA4 chain of 7 branches (local only, each in a clean worktree), `wip/aug-2026-domain-authorities`,
  and `feature/ems-aa3-archive-applicability-authority`.
- **Detached worktree:** C:/temp/standars/ems-post-merge-baseline-verify at de57bdf (= origin/main), clean.

## Tasks (orchestrator executes; git push uses the gh-token extraheader method)

1. **Tags.** Create two annotated tags and push them to origin:
   - `ems-aa3-authority-2.0.3` -> 1544dc19ba235d732c832d1651895550ed5a265d
   - `ems-demo-2026-12` -> 755cb275564f44b0af15dcad86267d809fe23f79
   No PR.
2. **Merged and patch-equivalent cleanup.**
   - Remove the 4 clean external-review worktrees and the detached post-merge worktree.
   - For the 3 patch-equivalent branches, create local `archive/<branch>` tags. They are not ancestors of main, so
     this is a safety net.
   - Delete the 12 local branches.
   - Delete the 8 remote branches that still exist: the 4 external-review and 4 wave2d merged branches.
   - Fast-forward local `main` to `origin/main`.
3. **Old Wave 2.**
   - Create local `archive/<branch>` tags on the 4 tips.
   - Close PR #8 with a comment.
   - Delete the 4 local branches and the 2 remote branches (wave2-control-scope, wave2d-pilot-ctrl018-baseline).

**Verify:**
- Every deleted tip is reachable from origin/main or an archive tag.
- The two tags resolve to the intended commits on origin.
- The AA4 branches and worktrees are unchanged.
- The working tree is clean.
