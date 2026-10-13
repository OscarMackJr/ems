---
phase: 02-blind-drafting
plan: 04
subsystem: governance
tags: [blind-drafting, proposals, drafting-commit]
requires:
  - phase: 02-blind-drafting
    provides: approved drafter brief (plan 03)
provides:
  - Single drafting commit holding the 21 draft proposals, frozen from this commit (D-15)
key-files:
  created:
    - registry/archive_assessment_not_applicable_rule_proposals.json
key-decisions:
  - Proposals file committed as produced after mechanical validation only; no content read or edited
requirements-completed: []
duration: n/a
completed: 2026-10-13
---

# Phase 2 Plan 04: Blind Drafting Run and Drafting Commit Summary

One isolated drafter run on the committed brief produced the proposals file, which passed the validator and tests unchanged and was committed alone.

## Record

- Drafting commit SHA: dc3b41c9fbb3571a191d2da5164fb73439a0637b (contains exactly `registry/archive_assessment_not_applicable_rule_proposals.json`)
- Committed proposals blob id: fb55535b6f17e2c4c3a2cd23dddbd39cd0355458 (content SHA-256 31684001ba3550fc98c1c86e487ff2c81fb106620f820dd0313311c8aea9886d, identical to the raw drafter output)
- Brief commit SHA: 6969f520162984d79276744805432d1c8dd14c89 (ancestor of the drafting commit)
- Drafter model id: claude-opus-5-5
- Prompt SHA-256 as reported: 8da9cbc462d3ae8b3c1a8ddf1a084bbb89529629520121449aad1fff84c7115d (executor recomputed the committed brief blob hash; equal)
- Correction rounds: 0
- Discard reasons: none (no attempts discarded)
- Date: 2026-10-13
- Validator: PASS. pytest proposals tests: 73 passed, 2 skipped (decision-record cases, delivered in plan 05). Combined authority, v2 and proposals tests: 156 passed, 2 skipped.
- Ordering checks at HEAD: no v2 authority file, no AA4-GOV reference in registry, only the proposals path changed in registry/scripts/schemas/tests/docs since the brief commit.

## Isolation statement (drafter)

Project instructions: NOT LOADED. One drafter attempt, run 2026-10-13 by the orchestrator as a headless CLI call (`claude -p --restricted --tools "" --strict-mcp-config --disable-slash-commands --no-session-persistence --model claude-opus-5-5 --output-format json`), working directory an otherwise empty scratch directory outside the repository; no tools available (0 tool permission denials, 1 turn, stop reason end_turn); no CLAUDE.md at user level or in any ancestor of that directory; user, project and local settings (hooks) ignored by restricted mode; no MCP servers; no skills. Residual exposure the prompt hash cannot exclude: the CLI's built-in default system prompt was in effect (it carries no project content), and `--bare` mode could not be used because it requires an API key that is not configured, so `--restricted` was used. Method chosen by the user (Oscar Mack).

## Deviations from Plan

None. DRAFT-01..03 left open (plan 05 delivers them).

## Self-Check: PASSED
