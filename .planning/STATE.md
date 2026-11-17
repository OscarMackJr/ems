---
gsd_state_version: 1.0
milestone: v1.2.0
milestone_name: Authority 2.0.3 Verification Hardening
status: planning
last_updated: "2026-11-17T17:50:54.377Z"
last_activity: 2026-11-17
progress:
  total_phases: 4
  completed_phases: 3
  total_plans: 18
  completed_plans: 18
  percent: 75
stopped_at: Phase 13 complete (4/4) — ready to discuss Phase 14
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-11-13)

**Core value:** For every one of the 21 requested controls, EMS publishes an explicit, machine-readable, authority-backed applicability decision that Hayes can cite — so that "EMS decided" is always distinguishable from "EMS has not decided yet".
**Current focus:** Phase 14 — notice to hayes (2.0.3)

## Current Position

Phase: 14 of 14 (notice to hayes (2.0.3))
Plan: Not started
Status: Ready to plan
Last activity: 2026-11-17

Progress: [█████░░░░░] 50%

## Performance Metrics

**Velocity:**

- Total plans completed: 66
- Average duration: - min
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 02 | 5 | - | - |
| 03 | 4 | - | - |
| 04 | 7 | - | - |
| 05 | 3 | - | - |
| 06 | 9 | - | - |
| 7 | 4 | - | - |
| 08 | 5 | - | - |
| 09 | 5 | - | - |
| 10 | 3 | - | - |
| 11 | 6 | - | - |
| 12 | 8 | - | - |
| 13 | 4 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
| Phase 06 P05 | 90min | 6 tasks | 4 files |
| Phase 11 P05 | 15min | 2 tasks | 3 files |
| Phase 11 P06 | 5min | 1 tasks | 2 files |
| Phase 12 P01 | 13min | 3 tasks | 5 files |
| Phase 12 P02 | 25min | 2 tasks | 4 files |
| Phase 12 P04 | 25min | 2 tasks | 4 files |
| Phase 12 P05 | 45min | 2 tasks | 3 files |
| Phase 12 P07 | 35min | 2 tasks | 6 files |
| Phase 12 P08 | 60min | 3 tasks | 3 files |

## Accumulated Context

### Roadmap Evolution

- Phase 6 added: Address tech debt: publication gate hardening (2.0.1)
- v1.1.0 roadmap created 2026-10-20: Phase 7 Lineage Source and Per-Digest Scope (LIN-01..03), Phase 8 Gate and Schema Hardening (GATE-01..05, SCHEMA-07), Phase 9 Certified Republication 2.0.2 (PUB-07..09), Phase 10 Notice to Hayes (NOTICE-01..02)
- v1.2.0 roadmap created 2026-11-13: Phase 11 Frozen Validators (FROZEN-01..04), Phase 12 Verify-at-Pin and Gate Hardening (PIN-01..02, GATE-06..10), Phase 13 Certified Republication 2.0.3 (PUB-10..12), Phase 14 Notice to Hayes 2.0.3 (NOTICE-03, PIN-03, CLAIM-01..03)

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Phase order is fixed by the EMS authority: shape, blind drafting, governance decisions, publication, reply
- [Roadmap]: Blind drafting (Phase 2) is committed before any governance decision (Phase 3); no phase compares a rule with a target repository
- [Roadmap]: Phase 3 is a human gate; the user gives an individual disposition for each of the 21 proposals and nothing is published before it
- [Roadmap]: Rule shape (Phase 1) precedes drafting so that proposals are written in a shape with defined semantics; Phase 1 uses no target information
- [Roadmap]: No phase carries a UI hint; the project is registry JSON, schema, publisher script, pytest and generated outputs
- [Phase 3]: 21 governance answers typed by authority, committed unchanged (cc74445); records AA4-GOV-001..021 published (eed4a5f)
- [Phase 06]: 06-05: accepted 18-item red window until plans 06-06 and 06-08; 2.0.0 constants held in code
- [v1.1.0 Roadmap]: All code and schema changes (Phases 7-8) precede one republication (Phase 9); the notice (Phase 10) follows because it cites the publication commit
- [v1.1.0 Roadmap]: Accepted red window opens at the first publisher/validator edit in Phase 7 and closes at the 2.0.2 publication commit
- [v1.1.0 Roadmap]: AA1 manifest commit (LIN-03) lands first in Phase 7, before LIN-02 recomputation is verified; the file is supplied by the user (path asked at Phase 7 start)
- [v1.1.0 Roadmap]: 2.0.2 publication requires sign-off by Oscar Mack as EMS governance authority (human gate in Phase 9)
- [v1.2.0 Roadmap]: Frozen validators (Phase 11) land before any publisher edit so the historical reply and 2.0.2 notice stay green
- [v1.2.0 Roadmap]: Accepted red window opens at the first publisher edit in Phase 12 and closes at the 2.0.3 publication commit (Phase 13)
- [v1.2.0 Roadmap]: Verify-at-pin mechanics (PIN-01/02) are publisher/validator changes, so they land in Phase 12; PIN-03 guidance and CLAIM-01..03 belong to the notice in Phase 14, which cites the publication commit
- [v1.2.0 Roadmap]: 2.0.3 publication requires sign-off by Oscar Mack as EMS governance authority with the dual-role statement (human gate in Phase 13)
- [Phase 11]: 11-05: Collection-level skips under EMS_FAIL_ON_SKIP=1 become collection errors via pytest_make_collect_report hookwrapper
- [Phase 11]: 11-05: history_problem requires exactly 'false' from --is-shallow-repository (WR-04); WR-02 opt-out reach accepted
- [Phase 11]: 11-06: WR-03 closed as wording fix only; reply guard ordering deferred with frozen-builder edits
- [Phase 12]: 12-01: collect skip guard scoped by collector.path name test_archive_assessment_*.py, not nodeid
- [Phase 12]: 12-02: D-10 --validate clone test asserts outcome equality only (not PASS); all 'f'*64 stand-ins replaced by real digests
- [Phase 12]: 12-03: 2.0.0 anchor literal gains relative_path to equal the frozen SUPERSEDED_V2_0_0 at 31addfa by full equality
- [Phase 12]: 12-03: reply resolve_record_commit: merge-base rc 1 = not an ancestor; other rc or OSError = cannot check ancestry (notice builder deferred, D-13)
- [Phase 12]: 12-04: validate_published runs schema_check (check_schema + validate, wrapped as AuthorityError) before validate_publication; load() unchanged
- [Phase 12]: 12-04: dry-run lead says 'DECISIONS DIFFER from <version>' unless decisions digest equals superseded value and no row/set differs
- [Phase 12]: 12-04: red window open; accepted red set exactly test_publisher_still_valid_and_digest_matches_manifest until 2.0.3 publication
- [Phase 12]: 12-05: all git access goes through git_show or git_run; helpers validate SHAs/paths before git and fail closed (GitHistoryError)
- [Phase 12]: 12-05: --pre-publication removed (no alias); --validate --at-pin reads superseded identity from source_lineage.supersedes
- [Phase 12]: 12-05: at-pin checks shallow state and git_dirty over the 10 D-05 paths + publisher script first; PASS prints one JSON object with one deferred item (PUBLICATION_RECORD_BINDING); plain --validate still prints PASS
- [Phase 12]: 12-06: plain --validate requires a full clone, publication commit ancestor of HEAD and identical raw blobs for the 10 D-05 paths at pub and HEAD; at the pin it points to --validate --at-pin
- [Phase 12]: 12-06: GATE-06 --validate checks the live publisher LF digest against manifest publisher_script.sha256 in both modes, and the script at the publication commit in plain mode; CI validator 1 red by design until the 2.0.3 publication

### Pending Todos

- None

### Blockers/Concerns

- [All phases]: The working tree holds unrelated modified files (`registry/adjudication_rules.json`, `registry/policy_decisions.json`, `.planning/config.json`) and about 60 untracked files from other work. Stage by explicit path only.
- [Phase 12]: Any publisher, schema or authority edit turns the real-file tests red until the 2.0.3 publication commit (hash certification). The red window is accepted and planned.
- [Phase 12]: 12-07: SUPERSEDED_V2_0_1 replaced by SUPERSEDED_V2_0_2 (ae15c74, a44eea1f..., decisions 4e746d1f...); VERSION '2.0.3'; superseded-version messages derive from the constant
- [Phase 12]: 12-07: frozen 2.0.1 sign-off test reads the 2.0.1 identity from the 2.0.2 authority's source_lineage.supersedes at ae15c74
- [Phase 12]: 12-07: end-of-phase accepted red set is 3 tests (committed schema, real published files, publisher digest) + CI validator 1; closed by Phase 13 publication and record commits
- [Phase 12]: 12-08: at-pin runs check_tree_matches_head over the 10 D-05 paths + publisher script (HEAD blob under CRLF_TO_LF, present on disk, index tag 'H' only), then hardened git status (--literal-pathspecs, --untracked-files=all, --ignored=matching) over those paths and the output folder
- [Phase 12]: 12-08: plain --validate ends with check_tree_matches_head(publication_paths()) (WR-01)
- [Phase 12]: 12-08: WR-02 stays advisory; WR-03 (assert before == (0, 'PASS') in the D-10 subprocess test) is a Phase 13 follow-up
- [v1.2.0]: Scope is the v1.1.0 audit tech debt (`.planning/milestones/v1.1.0-MILESTONE-AUDIT.md`); no decision content changes (decisions digest `4e746d1f…` is pinned).
- [CI]: `archive-assessment` job (261015-ci1) green on ubuntu-latest, run 38744767442: 492 passed, 5 validators PASS; runs on PRs, pushes to main, and `workflow_dispatch`
- [Publication 2.0.2]: EMS-AA3 authority 2.0.2 published at ae15c7458e49c8f55cc58c61bab04bc716aa9892 (Hayes pins this), record commit a71257ed267410138a3c4daba412b00c116663d8; CI run 43332405316 green (validate + archive-assessment) at headSha a71257e (workflow_dispatch, 2026-11-12); publication bytes identical pub..record
- [Publication 2.0.3]: EMS-AA3 authority 2.0.3 published at 1544dc19ba235d732c832d1651895550ed5a265d (Hayes pins this; signed off by Oscar Mack 2026-11-17), record commit 87a46d147413bd99e931c71a1ab165eb0903f014 (direct child of PUB), WR-03 commit 5498002c5eea3a6d9e3bfbb6766119880bb36804; CI run 44134035073 green (validate + archive-assessment) at headSha 5498002 (workflow_dispatch, 2026-11-17); publication bytes identical PUB..WR03; --validate --at-pin PASS in tree and in a fresh --no-local clone. Push scope: remote tip is 5498002; the .planning-only commits after WR03 (3fd54ac, and the docs(13-04) evidence commit) are local and are published by the Phase 14 push.
- [Environment]: `git push` via the credential manager fails in this session (sh.exe crash); pushing with the GitHub CLI token as a one-command `http.extraheader` (env `GIT_CONFIG_*`, credential.helper cleared) works
- [Environment]: Bash fails on this machine (cygwin `add_item` fatal error); GSD subagents have no PowerShell tool, so they cannot run tests or validators — run those from the orchestrator

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 261014-vau | Fix reply gate wording (audit AUDIT-W1, AUDIT-W2) | 2026-10-15 | 258875d | [261014-vau-fix-reply-gate-wording](./quick/261014-vau-fix-reply-gate-wording/) |
| 261015-ci1 | Run archive-assessment tests and validators in CI | 2026-10-15 | f767c64 | [261015-ci1-ci-archive-assessment-gates](./quick/261015-ci1-ci-archive-assessment-gates/) |
| 261019-st1 | Record EMS 2.0.1 status paragraph | 2026-10-19 | 3131e6e | [261019-st1-ems-2-0-1-status-paragraph](./quick/261019-st1-ems-2-0-1-status-paragraph/) |

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-11-17T17:50:54.362Z
Stopped at: Phase 14 context gathered
Resume file: .planning/phases/14-notice-to-hayes-2-0-3/14-CONTEXT.md

## Operator Next Steps

- Plan the first phase with /gsd-plan-phase 11
