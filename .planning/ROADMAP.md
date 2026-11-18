# Roadmap: EMS Not-Applicable Rule Publication (DEMO3-W1-REQ-001)

## Milestones

- ✅ **v1.0.0 Not-Applicable Rule Publication** — Phases 1-6 (shipped 2026-10-15) — [archive](./milestones/v1.0.0-ROADMAP.md)
- ✅ **v1.1.0 Authority 2.0.2 Lineage Correction** — Phases 7-10 (shipped 2026-11-13) — [archive](./milestones/v1.1.0-ROADMAP.md)
- ✅ **v1.2.0 Authority 2.0.3 Verification Hardening** — Phases 11-15 (shipped 2026-11-18) — [archive](./milestones/v1.2.0-ROADMAP.md)
- 🚧 **v1.3.0 Authority 2.0.4 Tech-Debt Closure** — Phases 16-19 (in progress)

## Phases

<details>
<summary>✅ v1.0.0 Not-Applicable Rule Publication (Phases 1-6) — SHIPPED 2026-10-15</summary>

- [x] Phase 1: Rule Shape and Decision States
- [x] Phase 2: Blind Drafting
- [x] Phase 3: Governance Decisions
- [x] Phase 4: Certified Publication
- [x] Phase 5: Reply to Hayes
- [x] Phase 6: Address tech debt: publication gate hardening (2.0.1)

</details>

<details>
<summary>✅ v1.1.0 Authority 2.0.2 Lineage Correction (Phases 7-10) — SHIPPED 2026-11-13</summary>

- [x] Phase 7: Lineage Source and Per-Digest Scope (4/4 plans)
- [x] Phase 8: Gate and Schema Hardening (5/5 plans)
- [x] Phase 9: Certified Republication 2.0.2 (5/5 plans)
- [x] Phase 10: Notice to Hayes (3/3 plans)

</details>

<details>
<summary>✅ v1.2.0 Authority 2.0.3 Verification Hardening (Phases 11-15) — SHIPPED 2026-11-18</summary>

- [x] Phase 11: Frozen Validators (6/6 plans)
- [x] Phase 12: Verify-at-Pin and Gate Hardening (8/8 plans)
- [x] Phase 13: Certified Republication 2.0.3 (4/4 plans)
- [x] Phase 14: Notice to Hayes (2.0.3) (5/5 plans)
- [x] Phase 15: Address tech debt: notice long-path git_show and step 2 wording (1/1 plans)

</details>

### v1.3.0 Authority 2.0.4 Tech-Debt Closure (Phases 16-19)

- [ ] **Phase 16: Test Robustness and Review Closure** - Baseline and git_show tests become honest, the 12/14/15 review info items are fixed or closed with a reason, and the planning bookkeeping is corrected
- [ ] **Phase 17: Security Hardening and Schema Pinning** - Pinned-publisher and decisions-builder digests are checked before use, the git seam is isolated, the CI scan covers `*.md`, and the schema pins superseded digests
- [ ] **Phase 18: Certified Republication 2.0.4** - One publication of 2.0.4 with no decision change, after all code and schema changes
- [ ] **Phase 19: Notice to Hayes (2.0.4)** - A generated notice that cites the 2.0.4 commit and the three-step verify sequence, with the sent commit recorded

## Phase Details

### Phase 16: Test Robustness and Review Closure

**Goal**: The tests and validators that guard the authority are honest about what they check, and every selected review info item from phases 11-15 is fixed with a test or closed with a recorded reason, with the frozen builders untouched.
**Depends on**: Phase 15 (v1.2.0 shipped)
**Requirements**: BASE-01, BASE-02, BASE-03, BASE-04, GATE-13, GATE-14, GATE-15, BOOK-01, BOOK-02
**Success Criteria** (what must be TRUE):

  1. The D-10 baseline assertion passes at the next publication commit and at later commits, and it checks the working tree under test, not committed HEAD; `outcome()` decodes UTF-8 and keeps stderr separate.
  2. On Windows with a deep root the `git_show` test fails loudly unless `Filename too long` reproduces without `--`; on other platforms it asserts the `--` behaviour only; it runs no skips under `EMS_FAIL_ON_SKIP=1`.
  3. Every selected 11/12/14/15 REVIEW item has a recorded disposition in `16-REVIEW-CLOSURE.md`: 14-REVIEW IN-01..05 and 15-REVIEW IN-02/IN-03 are fixed with tests; 12-REVIEW IN-07 test parts are fixed and the reply-builder message closed as frozen; 12-REVIEW IN-01..04 and the IN-06 digest-check move are carried to Phase 17; 12-REVIEW IN-05 and the IN-06 decisions-builder scope are superseded by SEC-04 and SEC-02; 15-REVIEW IN-01 moves to Phase 19 (2.0.3 text is immutable).
  4. The history-failure hint describes what `EMS_ALLOW_NO_HISTORY=1` skips, and an unrecognised shallow-check output is reported verbatim, or each is recorded as out of scope because the code is in a frozen builder.
  5. The SUMMARY files for phases 11-13 carry `requirements-completed` frontmatter matching v1.2.0 traceability, V2-01 and V2-02 are listed as deferred, and unrelated working-tree changes stay out of the commits.

**Invariants**: decisions digest stays `4e746d1f…`; 21 decided and 59 `NOT_YET_DECIDED`; frozen reply (2.0.1) and 2.0.2 notice builders byte-unchanged; CI `archive-assessment` green with 0 skips.
**Plans**: 5 plans

**Wave 1**
- [x] 16-01-PLAN.md — D-10 baseline test (record-state mode, working-tree overlay, UTF-8 stdout), HINT assertion, 12 IN-07 test parts
- [x] 16-02-PLAN.md — Deep-root git_show test that can fail, 2.0.3 notice builder behaviour-only fixes, D-02 byte-identity gate
- [x] 16-04-PLAN.md — `requirements-completed` frontmatter for phase 11-13 SUMMARY files

**Wave 2** *(blocked on Wave 1 completion)*
- [ ] 16-03-PLAN.md — 16-REVIEW-CLOSURE.md ledger, GATE-13/15 rewording, ROADMAP criteria for 16/17/19

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 16-05-PLAN.md — Phase gate (frozen-file range diff from 9a10810, validators, pytest, CI workflow_dispatch checkpoint)

### Phase 17: Security Hardening and Schema Pinning

**Goal**: The publisher, validator and git seam are in their final 2.0.4 form: nothing pinned is executed unchecked, a hostile caller environment cannot redirect a fail-closed check, and the schema rejects drifted superseded digests, all before the single republication.
**Depends on**: Phase 16
**Requirements**: SEC-01, SEC-02, SEC-03, SEC-04, GATE-11, GATE-12
**Success Criteria** (what must be TRUE):

  1. A pinned publisher whose digest differs from the certification is rejected with a fail-closed error before it is executed (test shows the publisher did not run).
  2. The pinned decisions-builder blob has a manifest digest, and `--validate` fails when the blob does not match it.
  3. The CI secret-pattern scan covers `*.md` files.
  4. With hostile `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY` or replace refs in the environment, the git seam still reads the intended repository and a fail-closed check cannot be redirected; pathspecs are literal.
  5. A 2.0.4 authority naming different superseded 2.0.3/2.0.2 digests fails schema validation, and the sign-off `scope` no longer carries an unchecked digest in free text.
  6. The deferred 12-REVIEW items (IN-01..IN-04 and the IN-06 `lf_digest(SCRIPT)` check move) are made with tests inside the red window; 12-REVIEW IN-05 is confirmed superseded by SEC-04. The D-10 baseline test joins the accepted red-set inventory at the first publisher edit and closes at the 2.0.4 publication (not weakened).

**Invariants**: as Phase 16. A red window (real-file tests red from hash certification) opens at the first publisher edit in Phases 16-17 and is accepted until the Phase 18 publication commit.
**Plans**: TBD

### Phase 18: Certified Republication 2.0.4

**Goal**: `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.4` is published once, with certification, manifest and traceability, signed off by the EMS governance authority, and no decision changed.
**Depends on**: Phase 17
**Requirements**: PUB-13, PUB-14, PUB-15
**Success Criteria** (what must be TRUE):

  1. 2.0.4 is published with certification, manifest and traceability, supersedes 2.0.3 at `1544dc1`, and records Oscar Mack's sign-off as EMS governance authority with the dual-role statement (human gate).
  2. The decisions digest is still `4e746d1f…`, all 80 rows are identical to 2.0.3, and the counts are 21 decided and 59 undecided.
  3. The publication commit contains only this milestone's deliberate changes, staged by explicit path, and the red window is closed with all real-file tests green.
  4. `--validate --at-pin` gives PASS at the pin, plain `--validate` gives PASS at the record commit, and CI `archive-assessment` is green with 0 skips at the publication commit and the shipped head.

**Plans**: TBD

### Phase 19: Notice to Hayes (2.0.4)

**Goal**: Hayes receives a generated, validated 2.0.4 notice that gives the three-step verify sequence, and EMS records which commit was actually sent.
**Depends on**: Phase 18
**Requirements**: NOTICE-04, NOTICE-05
**Success Criteria** (what must be TRUE):

  1. The generated notice, checked by `--validate`, cites the 2.0.4 id, version and commit and gives the three-step verify sequence.
  2. The step 1 clone command includes `-c core.longpaths=true`, and the line on plain `--validate` states exactly what it binds.
  3. When the notice is sent, the sent commit is recorded in a committed planning or registry artifact, along with the 2.0.3 send commit (`91d8847` or later) if that notice was sent.
  4. The frozen reply and 2.0.2 notice builders remain byte-unchanged and CI stays green with 0 skips.
  5. The 2.0.4 notice builder has no absolute-path example text in the registry JSON, and its `contains_absolute` scans the whole string (15-REVIEW IN-01; the sent 2.0.3 text stays immutable).

**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 7. Lineage Source and Per-Digest Scope | v1.1.0 | 4/4 | Complete | 2026-10-21 |
| 8. Gate and Schema Hardening | v1.1.0 | 5/5 | Complete | 2026-11-12 |
| 9. Certified Republication 2.0.2 | v1.1.0 | 5/5 | Complete | 2026-11-13 |
| 10. Notice to Hayes | v1.1.0 | 3/3 | Complete | 2026-11-13 |
| 11. Frozen Validators | v1.2.0 | 6/6 | Complete | 2026-11-16 |
| 12. Verify-at-Pin and Gate Hardening | v1.2.0 | 8/8 | Complete | 2026-11-16 |
| 13. Certified Republication 2.0.3 | v1.2.0 | 4/4 | Complete | 2026-11-17 |
| 14. Notice to Hayes (2.0.3) | v1.2.0 | 5/5 | Complete | 2026-11-17 |
| 15. Address tech debt: notice long-path git_show and step 2 wording | v1.2.0 | 1/1 | Complete | 2026-11-18 |
| 16. Test Robustness and Review Closure | v1.3.0 | 3/5 | In Progress|  |
| 17. Security Hardening and Schema Pinning | v1.3.0 | 0/? | Not started | - |
| 18. Certified Republication 2.0.4 | v1.3.0 | 0/? | Not started | - |
| 19. Notice to Hayes (2.0.4) | v1.3.0 | 0/? | Not started | - |
