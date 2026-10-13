# Requirements: EMS Not-Applicable Rule Publication (DEMO3-W1-REQ-001)

**Defined:** 2026-10-13
**Core Value:** For every one of the 21 requested controls, EMS publishes an explicit, machine-readable, authority-backed applicability decision that Hayes can cite — so that "EMS decided" is always distinguishable from "EMS has not decided yet".

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

The 21 controls: EMS-CTRL-009, 010, 011, 012, 013, 014, 015, 017, 018, 019, 020, 021, 022, 030, 033, 039, 042, 052, 062, 075, 079.

The eight classification fields: `production`, `internet_exposed`, `contains_customer_data`, `ai_enabled`, `owner`, `tier`, `service_criticality`, `data_classification`.

### Schema and States

- [x] **SCHEMA-01**: The applicability schema accepts a structured `not_applicable_rule` for a control instead of fixing it to `null`
- [x] **SCHEMA-02**: The schema accepts a `not_applicable_authority` that names a governance decision id
- [x] **SCHEMA-03**: Every control carries an explicit decision state with exactly three values: rule published, no rule will be published, not yet decided
- [x] **SCHEMA-04**: The schema rejects inconsistent combinations (a published rule with no authority, an undecided control with a rule, a decided control with no decision id)
- [x] **SCHEMA-05**: Rule conditions can reference only the eight declared classification fields and only `KNOWN_TRUE` or `KNOWN_FALSE`; anything else fails validation
  - Note (CONTEXT D-07/D-08): in 2.0.0, rule conditions may name only `production`, `internet_exposed`, `contains_customer_data`, `ai_enabled`; the other four fields (`owner`, `tier`, `service_criticality`, `data_classification`) stay declared but are not usable in rules.
- [x] **SCHEMA-06**: The authority states rule semantics in full: how conditions combine, what result a satisfied rule yields, and that an `UNKNOWN` field never yields not-applicable

### Blind Drafting

- [x] **DRAFT-01**: A rule-or-no-rule proposal with rationale exists for each of the 21 controls
- [x] **DRAFT-02**: Each proposal lists its EMS-source inputs, which are the control catalog definitions only. The drafter's reading of a control name is recorded separately as a labelled interpretation and is not an EMS source. The Phase 1 rule shape and the approved field definitions are declared once as the drafting frame. Nothing in the proposals refers to RiskMVP or Hayes evidence
  - Note (Phase 2 CONTEXT D-26): amended 2026-10-13; the catalog entries for the 21 controls carry no description.
- [x] **DRAFT-03**: All 21 proposals are committed before any comparison with a target, and that commit is recorded in the decision trail

### Governance Decisions

- [ ] **GOV-01**: The governance authority approves, changes or rejects each of the 21 proposals individually
- [x] **GOV-02**: Each outcome, rule or no-rule, is recorded as a governance decision with a unique id
- [x] **GOV-03**: Each decision record states that the approver holds both the EMS authority role and the Hayes developer role
- [ ] **GOV-04**: Decision records are machine-readable and schema-validated

### Publication

- [ ] **PUB-01**: A new authority version carries the 21 decisions, each citing its decision id as authority
- [ ] **PUB-02**: The other 59 controls are published as not yet decided, otherwise unchanged
- [ ] **PUB-03**: The publisher produces certification, manifest and decision-to-control traceability with SHA-256 digests
- [ ] **PUB-04**: Tests assert the invariants: 21 decided, 59 undecided, condition vocabulary respected, every decided control has an authority
- [ ] **PUB-05**: The new version records its lineage from AA3 v1.0.0 at commit `62a8955`
- [ ] **PUB-06**: The publication commit contains only this project's changes

### Reply to Hayes

- [ ] **REPLY-01**: A written reply to `DEMO3-W1-REQ-001` gives, for each of the 21, the rule and its authority or the no-rule decision and its id
- [ ] **REPLY-02**: The reply cites the authority id, version and commit to re-pin to, and describes the published shape
- [ ] **REPLY-03**: The reply states what publication does not do: the three Hayes-side changes still needed, and that the classification-prerequisites gap is untouched

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Coverage

- **V2-01**: Rule-or-no-rule decisions for the remaining 59 controls
- **V2-02**: Confirmation from a Hayes re-run that the 21 resolve at the new pin

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Hayes target description carrying the eight classification facts | Hayes-side gap, recorded separately by Hayes; next milestone in the Hayes repository |
| Changing Hayes to read the shape EMS publishes | Hayes-side; next milestone |
| Hayes re-pinning and updating its all-21-refuse test | Hayes-side; the test goes red by design |
| Moving the live resolved count off zero | Depends on the three Hayes-side changes; publication alone cannot do it |
| Adopting any Hayes-defined shape, profile, evaluator or evidence design | The shape and content are EMS's to choose; the 21 ids are EMS's own controls |
| Shaping rules to the known RiskMVP result | Rules are drafted blind, from the catalog alone |
| Sending the reply | The project writes the reply as a document in the repo; the authority sends it |
| Landing unrelated in-flight uncommitted work | Not part of the request; kept out of this project's commits |
| General codebase hardening (script sprawl, `.bak` files, dependency pinning) | Not needed to answer the request |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCHEMA-01 | Phase 1 | Complete |
| SCHEMA-02 | Phase 1 | Complete |
| SCHEMA-03 | Phase 1 | Complete |
| SCHEMA-04 | Phase 1 | Complete |
| SCHEMA-05 | Phase 1 | Complete |
| SCHEMA-06 | Phase 1 | Complete |
| DRAFT-01 | Phase 2 | Complete |
| DRAFT-02 | Phase 2 | Complete |
| DRAFT-03 | Phase 2 | Complete |
| GOV-01 | Phase 3 | Pending |
| GOV-02 | Phase 3 | Complete |
| GOV-03 | Phase 3 | Complete |
| GOV-04 | Phase 3 | Pending |
| PUB-01 | Phase 4 | Pending |
| PUB-02 | Phase 4 | Pending |
| PUB-03 | Phase 4 | Pending |
| PUB-04 | Phase 4 | Pending |
| PUB-05 | Phase 4 | Pending |
| PUB-06 | Phase 4 | Pending |
| REPLY-01 | Phase 5 | Pending |
| REPLY-02 | Phase 5 | Pending |
| REPLY-03 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0

---
*Requirements defined: 2026-10-13*
*Last updated: 2026-10-13 after roadmap creation (traceability)*
