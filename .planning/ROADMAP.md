# Roadmap: EMS Not-Applicable Rule Publication (DEMO3-W1-REQ-001)

## Milestones

- ✅ **v1.0.0 Not-Applicable Rule Publication** — Phases 1-6 (shipped 2026-10-15) — [archive](./milestones/v1.0.0-ROADMAP.md)
- ✅ **v1.1.0 Authority 2.0.2 Lineage Correction** — Phases 7-10 (shipped 2026-11-13) — [archive](./milestones/v1.1.0-ROADMAP.md)
- 🚧 **v1.2.0 Authority 2.0.3 Verification Hardening** — Phases 11-14 (in progress)

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

- [x] Phase 7: Lineage Source and Per-Digest Scope (4/4 plans) — completed 2026-10-21
- [x] Phase 8: Gate and Schema Hardening (5/5 plans) — completed 2026-11-12
- [x] Phase 9: Certified Republication 2.0.2 (5/5 plans) — completed 2026-11-13
- [x] Phase 10: Notice to Hayes (3/3 plans) — completed 2026-11-13

</details>

### v1.2.0 Authority 2.0.3 Verification Hardening (Phases 11-14)

- [x] **Phase 11: Frozen Validators** - Historical reply and 2.0.2 notice validators stop depending on live publisher code, and pinned-blob failures are loud (gap closure planned 2026-11-15) (completed 2026-11-16)
- [x] **Phase 12: Verify-at-Pin and Gate Hardening** - Publisher and validator changes: `--validate` works at the pin, the gates fail closed, and the review cleanup items are closed (completed 2026-11-16)
- [x] **Phase 13: Certified Republication 2.0.3** - One human-gated publication of 2.0.3 with no decision change (completed 2026-11-17)
- [x] **Phase 14: Notice to Hayes (2.0.3)** - A generated, claim-enforced notice that cites the 2.0.3 commit and tells Hayes how to verify at the pin (completed 2026-11-17)

## Phase Details

### Phase 11: Frozen Validators

**Goal**: The DEMO3 reply validator and the 2.0.2 notice validator are frozen, so later publisher edits cannot change their results and a missing pinned blob is never silently skipped.
**Depends on**: Phase 10 (v1.1.0 shipped)
**Requirements**: FROZEN-01, FROZEN-02, FROZEN-03, FROZEN-04
**Success Criteria** (what must be TRUE):

  1. The reply validator and the 2.0.2 notice validator import no live publisher constants or functions; a deliberate change to the publisher's `PREV_COMPARED_KEYS`, `DUAL_ROLE_STATEMENT`, `validate_signoff` or `rule_text` leaves both results unchanged.
  2. When the 2.0.1 blob or any other pinned blob cannot be reached, the tests and validators fail with an explicit error and do not skip.
  3. Pytest validates the committed notice files, and each notice test goes red when the specific check it is named for is broken.
  4. This phase is completed before any publisher edit, so the historical reply and 2.0.2 notice stay green throughout.

**Plans**: 6 plans (4 executed, 2 gap closure)

**Wave 1**

- [x] 11-01-PLAN.md — freeze the reply validator on 2.0.1

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 11-02-PLAN.md — freeze the 2.0.2 notice validator

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 11-03-PLAN.md — skip-to-fail and CI skip guard

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 11-04-PLAN.md — notice and reply test rigor

**Gap closure** *(from 11-VERIFICATION.md; 11-05 and 11-06 run in parallel)*

- [x] 11-05-PLAN.md — collection-level skips fail under EMS_FAIL_ON_SKIP (WR-01); fail-closed shallow check (WR-04)
- [x] 11-06-PLAN.md — correct the resolve_record_commit statements (WR-03)

### Phase 12: Verify-at-Pin and Gate Hardening

**Goal**: The publisher and validators are in their final 2.0.3 form: Hayes can verify at the pin, malformed input fails with domain errors, and the audit review items are closed, all before the single republication.
**Depends on**: Phase 11
**Requirements**: PIN-01, PIN-02, GATE-06, GATE-07, GATE-08, GATE-09, GATE-10
**Success Criteria** (what must be TRUE):

  1. On a clean checkout of the publication commit with no later commit, the documented `--validate` command returns PASS and its output names the one check it defers (binding the record to its commit).
  2. Plain `--validate` returns PASS at the record commit or any later commit, by checking that the record names the publication commit and that the publication files are byte-identical between the two commits.
  3. `--validate` fails when the publisher-script digest differs from the certification, not only pytest.
  4. Malformed authority shapes raise `AuthorityError` (never `TypeError`, `KeyError` or `AttributeError`); `validate_published` checks the schema first; `--validate` enforces cross-note uniqueness under `norm_templated`.
  5. The D-10 test shows a live catalog edit does not change the build or `--validate`; the D-13 test uses real changed answer bytes; the GATE-10 publisher and test cleanup items are done (conditional dry-run text, reachable DIFFER branch, restored 2.0.0 constant check, no dead `log`, uniform `resolve_record_commit` errors, D-08 tamper test covering rule and no-rule rows).

**Plans**: 8 plans (sequential waves; every plan updates 12-BASELINE-RED.md; 12-08 is gap closure)
**Wave 1**

- [x] 12-01-PLAN.md — baseline ledger; D-09/D-10/D-11 CI glob, scoped skip guard, history wording (green)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 12-02-PLAN.md — GATE-08/GATE-09 real-bytes and `--validate`-path tests (green)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 12-03-PLAN.md — GATE-10 IN-02, IN-03, IN-04 (reply builder only), IN-06 (green)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 12-04-PLAN.md — GATE-07 schema-first domain errors, GATE-10 IN-01 dry-run DIFFER (opens red window: 1 test)

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 12-05-PLAN.md — PIN-01 git seam, D-05 paths, `--validate --at-pin` (red set unchanged)

**Wave 6** *(blocked on Wave 5 completion)*

- [x] 12-06-PLAN.md — PIN-02 ancestry + blob identity; GATE-06 script digest (+1 test, + CI validator 1)

**Wave 7** *(blocked on Wave 6 completion)*

- [x] 12-07-PLAN.md — final 2.0.3 form: SUPERSEDED_V2_0_2, VERSION 2.0.3, truthful texts (+1 test; D-16 end state)

**Wave 8** *(gap closure; blocked on Wave 7 completion)*

- [x] 12-08-PLAN.md — CR-01 at-pin binds pinned tree to HEAD blobs and index, hardened git status; WR-01 plain working-tree binding; WR-04 real-layout tests (red set unchanged)

### Phase 13: Certified Republication 2.0.3

**Goal**: `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3` is published once, with certification, manifest and traceability, signed off by the EMS governance authority, and no decision changed.
**Depends on**: Phase 12
**Requirements**: PUB-10, PUB-11, PUB-12
**Success Criteria** (what must be TRUE):

  1. 2.0.3 is published with certification, manifest and traceability, supersedes 2.0.2 at `ae15c74`, and records Oscar Mack's sign-off as EMS governance authority with the dual-role statement (human gate).
  2. The decisions digest is still `4e746d1f…`, all 80 rows are identical to 2.0.2, and the counts are 21 decided and 59 undecided.
  3. The publication commit contains only this milestone's deliberate changes (staged by explicit path), and the CI `archive-assessment` job passes on it.
  4. The red window that opened at the first publisher edit in Phase 12 is closed: all real-file tests are green at the publication commit.

**Plans**: 4 plans

**Wave 1**

- [x] 13-01-PLAN.md — pre-flight, read-only dry run, blocking sign-off by Oscar Mack, write sign-off

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 13-02-PLAN.md — emit schema, publish, 10-path publication commit, at-pin in tree and fresh clone, red set at PUB, PUB-11 check

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 13-03-PLAN.md — record-only commit (red window closed), WR-03 test-only commit, all green

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 13-04-PLAN.md — blocking push go-ahead, push to WR-03 head, CI green, 13-VERIFICATION.md and STATE.md evidence

### Phase 14: Notice to Hayes (2.0.3)

**Goal**: Hayes receives a generated, validated notice for 2.0.3 whose claims are enforced rather than asserted, and which tells Hayes exactly how to verify at the pin and re-pin.
**Depends on**: Phase 13
**Requirements**: NOTICE-03, PIN-03, CLAIM-01, CLAIM-02, CLAIM-03
**Success Criteria** (what must be TRUE):

  1. The generated notice, checked by `--validate`, cites the 2.0.3 id, version and commit, lists what changed, states that no decision changed, and asks Hayes to re-pin.
  2. The notice gives the exact commands to verify at the pin and at the record commit, and says what each result means.
  3. The builder runs every negative mutation and records a domain rejection for each; the validator fails if any mutation was not rejected.
  4. The validator recomputes all 7 lineage digests from git, and every "declared under the wrong scope" statement is computed by showing that each RAW_BYTES file's raw hash differs from its LF hash.

**Plans**: 5 plans

**Wave 1**

- [x] 14-01-PLAN.md — builder core: frozen constants, history guard, pinned mutation rerun (CLAIM-01), lineage recomputation (CLAIM-02), raw/LF scope proof (CLAIM-03)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 14-02-PLAN.md — build_notice with verify-at-pin section (PIN-03), render, closed schema, --build/--emit-schema/--validate

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 14-03-PLAN.md — tests: per-claim, tamper, fail-closed, content, CLI, live-file clone

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 14-04-PLAN.md — orchestrator pytest gate, code commit, generate notice, Oscar Mack review (D-14)

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 14-05-PLAN.md — notice commit, CI line commit, push checkpoint, push and CI green

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 7. Lineage Source and Per-Digest Scope | v1.1.0 | 4/4 | Complete | 2026-10-21 |
| 8. Gate and Schema Hardening | v1.1.0 | 5/5 | Complete | 2026-11-12 |
| 9. Certified Republication 2.0.2 | v1.1.0 | 5/5 | Complete | 2026-11-13 |
| 10. Notice to Hayes | v1.1.0 | 3/3 | Complete | 2026-11-13 |
| 11. Frozen Validators | v1.2.0 | 6/6 | Complete    | 2026-11-16 |
| 12. Verify-at-Pin and Gate Hardening | v1.2.0 | 8/8 | Complete    | 2026-11-16 |
| 13. Certified Republication 2.0.3 | v1.2.0 | 4/4 | Complete    | 2026-11-17 |
| 14. Notice to Hayes (2.0.3) | v1.2.0 | 5/5 | Complete    | 2026-11-17 |
