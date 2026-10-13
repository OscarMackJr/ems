# Roadmap: EMS Not-Applicable Rule Publication (DEMO3-W1-REQ-001)

## Overview

EMS answers Hayes Verify request `DEMO3-W1-REQ-001` by extending the AA3 archive-assessment applicability authority. The work runs in a fixed order that the EMS authority set: first EMS chooses the rule shape and the three decision states; then a rule-or-no-rule proposal is drafted for each of the 21 requested controls from the control catalog alone and committed; then the EMS authority personally decides each proposal; then a new authority version is published and certified with those 21 decisions and 59 controls left as not yet decided; and last a written reply cites the published commit. Each step is committed separately so an external reader can confirm the order from git history.

**Ordering guarantees (not negotiable):**

- Blind drafting is complete and committed before any governance decision is recorded.
- No phase in this roadmap compares a rule with a target repository. The RiskMVP assessment result is never an input.
- Nothing is published before the EMS authority has decided all 21 proposals.
- The reply is written after publication because it cites the publication commit.
- Every commit in this project contains only this project's files. The unrelated modified and untracked files in the working tree are never staged.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Rule Shape and Decision States** - The applicability schema can express a rule, a named authority, and three decision states, and rejects everything else (completed 2026-10-13)
- [ ] **Phase 2: Blind Drafting** - 21 rule-or-no-rule proposals drafted from the control catalog alone and committed before any decision
- [ ] **Phase 3: Governance Decisions** - The EMS authority decides each of the 21 proposals; each outcome becomes a schema-validated decision record (human gate)
- [ ] **Phase 4: Certified Publication** - A new authority version carries the 21 decisions and 59 undecided controls, certified, traceable and tested, in a clean commit
- [ ] **Phase 5: Reply to Hayes** - A written reply to `DEMO3-W1-REQ-001` cites the published authority, version and commit

## Phase Details

### Phase 1: Rule Shape and Decision States
**Goal**: EMS has a chosen, machine-checkable shape for a not-applicable rule, its named authority and a three-valued decision state per control, with rule semantics written out in full, so that a rule can be drafted and later published without any meaning left to convention.
**Depends on**: Nothing (first phase)
**Requirements**: SCHEMA-01, SCHEMA-02, SCHEMA-03, SCHEMA-04, SCHEMA-05, SCHEMA-06
**Success Criteria** (what must be TRUE):
  1. Validating an authority document against the new schema passes when a control carries a structured `not_applicable_rule`, a `not_applicable_authority` naming a governance decision id, and a decision state of "rule published"; it also passes for a "no rule will be published" control and for a "not yet decided" control.
  2. Validation fails for each inconsistent combination: a rule with no authority, a "not yet decided" control that carries a rule, a decided control with no decision id, and a decision state outside the three allowed values.
  3. Validation fails for a rule condition that names a field outside the eight declared classification fields, or that uses any state other than `KNOWN_TRUE` or `KNOWN_FALSE` (including `UNKNOWN`), or that is a free-text string such as `absence_of_evidence`.
     Note (CONTEXT D-07/D-08): in 2.0.0, rule conditions may name only `production`, `internet_exposed`, `contains_customer_data`, `ai_enabled`; the other four fields (`owner`, `tier`, `service_criticality`, `data_classification`) stay declared but are not usable in rules.
  4. A reader of the schema and semantics block can state, without consulting any other source, how conditions in a rule combine, what applicability result a satisfied rule yields, and that an `UNKNOWN` classification field never yields not-applicable.
  5. The existing AA3 pytest invariants still pass, and the published v1.0.0 authority content at `62a8955` is not altered in meaning by this phase.
**Plans**: TBD

### Phase 2: Blind Drafting
**Goal**: A rule-or-no-rule proposal with rationale exists for each of the 21 requested controls, drafted from the control catalog definitions alone, and is fixed in git history before any governance decision or any contact with a target.
**Depends on**: Phase 1
**Requirements**: DRAFT-01, DRAFT-02, DRAFT-03
**Success Criteria** (what must be TRUE):
  1. A committed proposals file lists exactly the 21 requested control ids (EMS-CTRL-009, 010, 011, 012, 013, 014, 015, 017, 018, 019, 020, 021, 022, 030, 033, 039, 042, 052, 062, 075, 079), and each entry is either a proposed rule in the Phase 1 shape or a proposed "no rule" outcome, with a written rationale.
  2. Each proposal lists its EMS-source inputs, and every one is a control catalog definition in this repository; interpretation is labelled as such; the drafting frame is declared once; a text search of the proposals for RiskMVP, the RiskMVP commit, Hayes evidence or the 2026-10-01 assessment result finds nothing.
     Note (Phase 2 CONTEXT D-26): amended 2026-10-13.
  3. `git log` shows a single drafting commit that contains all 21 proposals and predates every governance decision record; no decision record or new authority version exists at that commit.
  4. The drafting commit SHA is recorded in the decision trail in a later commit, so a reader can confirm from the repository alone that drafting came first.
  5. Proposals are marked as drafts with no authority; nothing in the published authority file changes in this phase.
**Plans**: TBD

### Phase 3: Governance Decisions
**Goal**: The EMS governance authority has personally approved, changed or rejected each of the 21 proposals, and each outcome is a machine-readable, schema-validated governance decision with its own id that names the approver's dual role.
**Depends on**: Phase 2
**Requirements**: GOV-01, GOV-02, GOV-03, GOV-04
**Success Criteria** (what must be TRUE):
  1. The decision records show 21 individual dispositions, one per requested control, each one of approved as drafted, changed, or rejected, each given by Oscar Mack for that control specifically; a single blanket approval of all 21 is not present.
  2. Each of the 21 outcomes, rule or no-rule, has a unique governance decision id that does not collide with `AA1-GOV-001`..`008`, and each record cites the drafting commit SHA from Phase 2.
  3. Every decision record states in its own text that the approver holds both the EMS authority role and the Hayes developer role.
  4. Validating the decision records against their schema passes; removing the dual-role statement, the decision id, the disposition or the control id from a record makes validation fail.
  5. Where the authority changed a proposal, the record shows both the drafted text and the decided text; the Phase 2 drafting commit is left unamended.
**Plans**: TBD

**Human gate:** This phase cannot be completed by drafting judgment. It finishes only when the user has given a disposition for each of the 21 proposals. No authority file, certification or reply is produced before it.

### Phase 4: Certified Publication
**Goal**: A new controlled version of the archive-assessment applicability authority is published at a commit Hayes can re-pin to, in which each of the 21 requested controls shows an explicit decision citing its governance decision id, and the other 59 controls show "not yet decided".
**Depends on**: Phase 3
**Requirements**: PUB-01, PUB-02, PUB-03, PUB-04, PUB-05, PUB-06
**Success Criteria** (what must be TRUE):
  1. The authority file shows 21 decided and 59 not-yet-decided controls; each of the 21 is either "rule published" with a rule and a `not_applicable_authority`, or "no rule will be published" with a decision id, and every cited id resolves to a Phase 3 decision record.
  2. For each of the 59 controls outside the request, the entry is the same as in v1.0.0 apart from the explicit "not yet decided" state: still `APPLICABILITY_UNRESOLVED`, no rule, no rule authority.
  3. Running the publisher regenerates the certification, the publication manifest and a decision-to-control traceability file, and the SHA-256 digests in the manifest match the files in the commit; the publisher's `--validate` run prints `PASS`.
  4. `python -m pytest` on the authority tests passes, including tests that fail if the decided count is not 21, the undecided count is not 59, a rule condition leaves the declared vocabulary, or a decided control lacks an authority.
  5. The new version has a new authority id and version, records its lineage from `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-1.0.0` at commit `62a8955`, and `git show --stat` on the publication commit lists only this project's files (none of the unrelated modified or untracked files).
**Plans**: TBD

### Phase 5: Reply to Hayes
**Goal**: A written reply to request `DEMO3-W1-REQ-001` sits in the repository, tells Hayes exactly what EMS decided for each of the 21 controls and where to cite it, and is plain about what publication does not change.
**Depends on**: Phase 4
**Requirements**: REPLY-01, REPLY-02, REPLY-03
**Success Criteria** (what must be TRUE):
  1. The reply lists all 21 requested controls, and for each gives either the rule and its authority or the no-rule decision and its id; every entry agrees with the published authority file.
  2. The reply names the authority id, the version and the full publication commit SHA to re-pin to, and that SHA is the Phase 4 publication commit; it describes the published shape well enough for Hayes to locate the rule, the authority and the decision state for a control.
  3. The reply states that the 59 other controls remain not yet decided, that three Hayes-side changes are still needed before any control resolves (target description carrying the eight classification facts, reading the published shape, re-pinning), and that the classification-prerequisites gap is untouched.
  4. The reply is committed as a document in this repository in a commit after the publication commit, containing only this project's files; sending it is left to the EMS authority.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Rule Shape and Decision States | 3/3 | Complete    | 2026-10-13 |
| 2. Blind Drafting | 1/5 | In Progress|  |
| 3. Governance Decisions | 0/TBD | Not started | - |
| 4. Certified Publication | 0/TBD | Not started | - |
| 5. Reply to Hayes | 0/TBD | Not started | - |

## Coverage

| Category | Requirements | Phase |
|----------|--------------|-------|
| Schema and States | SCHEMA-01, SCHEMA-02, SCHEMA-03, SCHEMA-04, SCHEMA-05, SCHEMA-06 | 1 |
| Blind Drafting | DRAFT-01, DRAFT-02, DRAFT-03 | 2 |
| Governance Decisions | GOV-01, GOV-02, GOV-03, GOV-04 | 3 |
| Publication | PUB-01, PUB-02, PUB-03, PUB-04, PUB-05, PUB-06 | 4 |
| Reply to Hayes | REPLY-01, REPLY-02, REPLY-03 | 5 |

v1 requirements mapped: 22/22. No orphans, no duplicates.

## Notes for Planning

Facts read from the repository on 2026-10-13 that the phase plans must account for:

- **The schema file is generated.** `scripts/publish_archive_assessment_applicability_authority.py` writes both `registry/archive_assessment_applicability_authority.json` and `schemas/archive_assessment_applicability_authority.schema.json` from code (`build_authority()` and `schema()`). A hand edit to either file is overwritten on the next publish. Phase 1 changes belong in the publisher, or in a new versioned publisher.
- **The v1.0.0 manifest hashes the publisher, the schema and the authority.** Editing any of the three in place makes the committed v1.0.0 manifest digests stale until Phase 4 republishes. Phase 1 planning must choose between in-place change and new versioned files, and say which. Hayes is pinned to `62a8955`, so it is not affected either way.
- **v1.0.0 constants block the new states.** The schema fixes `version` to `1.0.0`, `not_applicable_rule` and `not_applicable_authority` to `null`, `approved_governance_decision_ids` to exactly eight ids matching `AA1-GOV-00[1-8]`, and each control's `decision_ids` to exactly eight. New decision ids need room in all of these.
- **An existing test guards free-text rules.** `test_implicit_not_applicable_fails_closed` sets `not_applicable_rule` to the string `absence_of_evidence` and expects rejection. That must keep failing closed once structured rules are allowed.
- **Governance precedent is a blanket approval.** `generated/archive-assessment/ems-aa2/approval/archive_assessment_applicability_governance_approval.json` records `APPROVE_ALL_AS_PREPARED` with per-decision `approval_disposition`, `prepared_text` and `approved_text`. The per-decision record layout is reusable for Phase 3; the blanket instruction is not, because GOV-01 requires an individual disposition per control.
- **Commit SHAs cannot be recorded in the commit they name.** The drafting SHA (DRAFT-03) is recorded in a later commit; the publication SHA (REPLY-02) is cited from the Phase 5 commit.
- **Working tree.** `registry/adjudication_rules.json` and `registry/policy_decisions.json` are modified, and about 60 untracked files from other work are present. Stage this project's files by explicit path; never `git add -A` or `git add .`.
- **No user-facing screens.** This project is registry JSON, a schema, a publisher script, pytest and generated certification outputs.

---
*Roadmap created: 2026-10-13*
