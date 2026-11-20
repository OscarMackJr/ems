---
gsd_state_version: 1.0
milestone: v1.3.0
milestone_name: Authority 2.0.4 Tech-Debt Closure
status: executing
last_updated: "2026-11-19T15:53:48.848Z"
last_activity: 2026-11-19 -- Phase 17 planning complete
progress:
  total_phases: 4
  completed_phases: 1
  total_plans: 14
  completed_plans: 5
  percent: 25
stopped_at: Phase 16 complete (5/5) — ready to discuss Phase 17
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-11-18)

**Core value:** For every one of the 21 requested controls, EMS publishes an explicit, machine-readable, authority-backed applicability decision that Hayes can cite — so that "EMS decided" is always distinguishable from "EMS has not decided yet".
**Current focus:** Phase 17 — security hardening and schema pinning

## Current Position

Phase: 17
Plan: Not started
Status: Ready to execute
Last activity: 2026-11-19 - Completed quick task 261119-szw: Branch cleanup for demo

Progress: [░░░░░░░░░░] 0% (0/4 phases)

## Performance Metrics

**Velocity:**

- Total plans completed: 77
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
| 14 | 5 | - | - |
| 15 | 1 | - | - |
| 16 | 5 | - | - |

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
- Phase 15 added: Address tech debt: notice long-path git_show and step 2 wording
- v1.3.0 roadmap created 2026-11-18: Phase 16 Test Robustness and Review Closure (BASE-01..04, GATE-13..15, BOOK-01..02), Phase 17 Security Hardening and Schema Pinning (SEC-01..04, GATE-11..12), Phase 18 Certified Republication 2.0.4 (PUB-13..15), Phase 19 Notice to Hayes 2.0.4 (NOTICE-04..05)

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v1.3.0 Roadmap]: All code, schema and test changes (Phases 16-17) precede one 2.0.4 republication (Phase 18); red window accepted from the first publisher edit until the publication commit; the notice (Phase 19) follows because it cites the publication commit
- [v1.3.0 Roadmap]: BOOK (planning-only) is placed in Phase 16; GATE-11/12 are schema changes and go with SEC in Phase 17
- [v1.3.0 Roadmap]: 2.0.4 publication requires sign-off by Oscar Mack as EMS governance authority with the dual-role statement (human gate in Phase 18)
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

- [All phases]: Working tree cleaned 2026-11-19 (quick 261119-shp). The unrelated August work (109 untracked files plus the `registry/adjudication_rules.json` and `registry/policy_decisions.json` changes) is parked on local branch `wip/aug-2026-domain-authorities` (`f6bb4a3`, not pushed). Still stage by explicit path only.
- [Next publication]: 13-REVIEW WR-01: the D-10 baseline assertion fails at the next publication commit (BASE-01 closes this in Phase 16). Any republication reopens a red window (hash certification).
- [CI]: The `archive-assessment` job (261015-ci1) runs on PRs, pushes to main and `workflow_dispatch`, with `EMS_FAIL_ON_SKIP=1`. The latest green run is 44325017719 at `91d8847`: 1121 passed and 7 validators printed PASS.
- [Notice 2.0.3]: Recorded. Notice sent to Hayes at 91d88473129a8996e97da23be58de33076ec5b51 (91d8847, 2026-11-18), confirmed by Oscar Mack; 2.0.3 half of NOTICE-05 recorded in .planning/quick/261119-sd5-record-ems-demo-pin-and-2-0-3-notice-sen/261119-sd5-DEMO-PIN.md. NOTICE-05 stays Pending until the 2.0.4 send commit is recorded (Phase 19).
- [Demo pin]: Demo uses EMS commit 755cb275564f44b0af15dcad86267d809fe23f79 (755cb27; remote tip, CI run 44423016638 green). v1.3.0 Phases 17-19 are parked until after the demo; plan 17-04 must not start before then. Known gap: Hayes demo3/run-service records still pin EMS 62a8955, not 1544dc1. See 261119-sd5-DEMO-PIN.md.
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
| 261118-cgq | Make the deep-root git_show test skip-free so the CI skip guard stays green (audit B-1) | 2026-11-18 | 72a5c06 | [261118-cgq-make-the-windows-only-deep-root-git-show](./quick/261118-cgq-make-the-windows-only-deep-root-git-show/) |
| 261119-sd5 | Record EMS demo pin (755cb27) and 2.0.3 notice send commit (91d8847) | 2026-11-19 | 428e00a | [261119-sd5-record-ems-demo-pin-and-2-0-3-notice-sen](./quick/261119-sd5-record-ems-demo-pin-and-2-0-3-notice-sen/) |
| 261119-shp | Working tree triage for demo: August work parked on wip/aug-2026-domain-authorities (f6bb4a3), 26 EOL-only files restored, .pytest-* removed and ignored | 2026-11-19 | 0b50a4f | [261119-shp-working-tree-triage-for-demo](./quick/261119-shp-working-tree-triage-for-demo/) |
| 261119-szw | Branch cleanup for demo: tags ems-aa3-authority-2.0.3 (1544dc1) and ems-demo-2026-12 (755cb27) pushed; 16 stale branches and 5 worktrees removed (archive/* tags kept); PR #8 closed; AA4 chain untouched | 2026-11-19 | (this commit) | [261119-szw-branch-cleanup-for-demo](./quick/261119-szw-branch-cleanup-for-demo/) |

## Deferred Items

Items acknowledged and deferred at the v1.2.0 milestone close on 2026-11-18:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| quick_task | 261014-vau-fix-reply-gate-wording | scanner reports `missing`; complete (`261014-vau-SUMMARY.md` present) | v1.2.0 close |
| quick_task | 261015-ci1-ci-archive-assessment-gates | scanner reports `missing`; complete (`261015-ci1-SUMMARY.md` present) | v1.2.0 close |
| quick_task | 261019-st1-ems-2-0-1-status-paragraph | scanner reports `missing`; complete (`261019-st1-SUMMARY.md` present) | v1.2.0 close |
| quick_task | 261118-cgq-make-the-windows-only-deep-root-git-show | scanner reports `missing`; complete (`261118-cgq-SUMMARY.md` present) | v1.2.0 close |

## Session Continuity

Last session: 2026-11-19T01:37:43.207Z
Stopped at: Phase 17 context gathered
Resume file: .planning/phases/17-security-hardening-and-schema-pinning/17-CONTEXT.md

## Operator Next Steps

- Run /gsd-plan-phase 16
