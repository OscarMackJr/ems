# EMS Not-Applicable Rule Publication (DEMO3-W1-REQ-001)

## What This Is

EMS is a spec-driven governance repository: 80 controls (EMS-CTRL-001..080), declarative JSON/YAML registries, and Python/PowerShell scripts that collect evidence, adjudicate applicability, and publish hash-certified authorities. This project updates the EMS archive-assessment applicability authority so that it can answer a formal request from Hayes Verify: for each of 21 named controls, EMS either publishes a machine-readable `not_applicable_rule` with a named authority, or publishes an explicit decision that no rule will be published.

The consumer is Hayes Verify, an external assessor that reads EMS at a pinned commit, treats it as read-only, and will not make applicability decisions itself.

## Core Value

For every one of the 21 requested controls, EMS publishes an explicit, machine-readable, authority-backed applicability decision that Hayes can cite — so that "EMS decided" is always distinguishable from "EMS has not decided yet".

## Requirements

### Validated

<!-- Inferred from the existing codebase (see .planning/codebase/). -->

- ✓ Control catalog of 80 controls with scope registry (`registry/control_catalog.yaml`, `registry/control_scope_registry.yaml`) — existing
- ✓ AA3 archive-assessment applicability authority v1.0.0, published and certified at commit `62a8955` (`registry/archive_assessment_applicability_authority.json`, schema, publisher script, test) — existing
- ✓ Classification vocabulary of eight fields (`production`, `internet_exposed`, `contains_customer_data`, `ai_enabled`, `owner`, `tier`, `service_criticality`, `data_classification`) with states `KNOWN_TRUE` / `KNOWN_FALSE` / `UNKNOWN` — existing
- ✓ Not-applicable semantics declared: requires an explicit controlled rule; unknown is not not-applicable; absence of evidence is not not-applicable — existing
- ✓ Authority publication pattern: schema-validated registry JSON, publisher script computing SHA-256 digests, publication certification, decision traceability, pytest invariants — existing
- ✓ Governance decision ids (`AA1-GOV-001`..`008`) cited per control as what makes the authority binding — existing
- ✓ The v2 applicability schema permits a structured `not_applicable_rule` and a `not_applicable_authority` per control (v1 files unchanged) — Validated in Phase 1: Rule Shape and Decision States
- ✓ The v2 authority shape expresses three distinguishable states per control: rule published, "no rule will be published" decided, and not yet decided — Validated in Phase 1: Rule Shape and Decision States
- ✓ A rule-or-no-rule proposal is drafted for each of the 21 controls from the control catalog definitions alone (`registry/archive_assessment_not_applicable_rule_proposals.json`, status `DRAFT_NO_AUTHORITY`) — Validated in Phase 2: Blind Drafting
- ✓ Drafts are committed before any comparison with a target repository or with the RiskMVP assessment result (drafting commit `dc3b41c`, recorded in `registry/archive_assessment_rule_proposals_drafting_record.json`) — Validated in Phase 2: Blind Drafting
- ✓ The governance authority reviewed and gave an individual disposition for each of the 21 proposals, typed by the authority in `registry/archive_assessment_governance_answers.json` (commit `cc74445`) after the wording sign-off (`bcba0f1`); nothing is published yet — Validated in Phase 3: Governance Decisions
- ✓ Each disposition is recorded as a schema-validated governance decision record `AA4-GOV-001`..`021` in `registry/archive_assessment_governance_decisions.json` (commit `eed4a5f`), each stating the approver holds both the EMS authority role and the Hayes developer role — Validated in Phase 3: Governance Decisions

- ✓ A "no rule will be published" outcome is itself a published decision with its own decision id (18 controls, `NO_RULE_WILL_BE_PUBLISHED`) — Validated in Phase 4: Certified Publication
- ✓ Rule conditions are expressed only over the first four of the eight declared classification fields (`production`, `internet_exposed`, `contains_customer_data`, `ai_enabled`), each as a `KNOWN_TRUE` / `KNOWN_FALSE` fact (CTRL-030, CTRL-039 `production = KNOWN_FALSE`; CTRL-052 `ai_enabled = KNOWN_FALSE`) — Validated in Phase 4: Certified Publication
- ✓ Each rule is explicit and machine-readable, with no meaning left to convention — Validated in Phase 4: Certified Publication
- ✓ Each rule or no-rule decision names its authority (`AA4-GOV-001`..`021`) so Hayes can cite what makes it binding — Validated in Phase 4: Certified Publication
- ✓ The 59 controls outside the request remain "not yet decided", identical to v1.0.0 apart from the explicit state — Validated in Phase 4: Certified Publication
- ✓ `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0` published with certification, traceability and passing tests at commit `54a7fd0` (signed off by Oscar Mack as EMS governance authority; SHA recorded in `0ce89f2`) — Validated in Phase 4: Certified Publication
- ✓ A written reply to request `DEMO3-W1-REQ-001` (`docs/DEMO3_W1_REQ_001_REPLY.md`, `registry/archive_assessment_demo3_w1_req_001_reply.json`, generated and `--validate`-checked by `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`) cites authority `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0`, version 2.0.0 and commit `54a7fd0`, and states what EMS did and did not publish; unsigned and not sent until the pin is on the remote — Validated in Phase 5: Reply to Hayes

### Active

<!-- Hypotheses until shipped and validated. -->

(none — all v1 requirements validated)

### Out of Scope

- Deciding rule-or-no-rule for the other 59 controls — the request names 21; the schema will allow rules for any control but only the 21 get a decision now
- Hayes's target description carrying the eight classification facts — a Hayes-side gap, recorded separately by Hayes, next milestone in the Hayes repository
- Changing Hayes to read the shape EMS publishes — Hayes-side, next milestone
- Hayes re-pinning to the new EMS commit, and updating the Hayes test that asserts all 21 refuse (it goes red by design) — Hayes-side, next milestone
- Moving the live count of resolved controls off zero — publication alone cannot do this; it depends on the three Hayes changes above
- Adopting anything defined in Hayes into EMS (the approved 21-control profile, collectors, evaluators, evidence designs, or the placeholder rule shape) — the shape and content are EMS's to choose; the 21 ids are EMS's own controls
- Shaping rules to produce a wanted outcome against RiskMVP — rules are drafted blind to the 10/1 result
- Landing the in-flight uncommitted work in this tree (onboarding, dependency supply chain, release integrity, test quality, real-repository pilot, and the modified `registry/adjudication_rules.json` and `registry/policy_decisions.json`) — unrelated to the request; left untouched and kept out of this project's commits
- General codebase hardening (script sprawl, `.bak` files, unpinned dev dependencies) — not needed to answer the request

## Context

**The request.** Hayes Verify, request id `DEMO3-W1-REQ-001`, register entry `EMSREQ-APPLIC-RULES`. Before checking a control against an outside repository, Hayes must decide whether the control applies; that decision belongs to EMS. At the pinned EMS commit `62a8955dc28d9458cd1167fad314926e057c31fc`, no control has a published `not_applicable_rule`, so Hayes stops at applicability.

**What was observed.** In one authorized read-only assessment on 2026-10-01 of `https://github.com/oscarmackjr-twg/RiskMVP` at commit `42aa362c76980a934fbaa470e603b48c7ef4b0b7`, all 21 controls refused with `EMS_NOT_APPLICABLE_RULE_ABSENT`. Hayes had predicted this in writing beforehand. In the meantime Hayes reports the controls as "applicability unresolved" and supplies no value of its own.

**The 21 controls.** EMS-CTRL-009, 010, 011, 012, 013, 014, 015, 017, 018, 019, 020, 021, 022, 030, 033, 039, 042, 052, 062, 075, 079.

**What Hayes's resolver needs from any shape EMS picks.**
- A rule per control that is explicit and machine-readable, with no meaning left to convention
- Conditions expressed only over the classification fields EMS's own document declares, each as a known-true or known-false fact about the target
- A named authority for each rule

**Any of these is a complete answer to Hayes:** the rules with the authority for each; a statement that no rule will be published for some or all controls; a date by which EMS expects to decide.

**State of the repository at the pinned commit (verified 2026-10-13).**
- `schemas/archive_assessment_applicability_authority.schema.json` fixes `not_applicable_rule` and `not_applicable_authority` to `type: null`
- All 80 controls in `registry/archive_assessment_applicability_authority.json` have `default_applicability_result: APPLICABILITY_UNRESOLVED`, `unresolved_reason: CONTROLLED_TARGET_CLASSIFICATION_AND_AUTHORITY_INPUTS_REQUIRED`, the same eight classification prerequisites, and decision ids `AA1-GOV-001`..`008`
- Among the 21, `required_non_repository_authority` is `REPOSITORY_CONTENT_ONLY` for 15, `PLATFORM` for 2, and `SERVICE`, `ORGANIZATION`, `APPLICATION`, `EMS` for 1 each
- Of the 21, only EMS-CTRL-039 appears in `registry/policy_applicability.yaml`; there is little prior rule material to reuse
- Authority id is `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-1.0.0`, target type `ARCHIVED_REPOSITORY_SNAPSHOT`, assessment semantics `CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT`
- Existing files for this authority: `scripts/publish_archive_assessment_applicability_authority.py`, `tests/test_archive_assessment_applicability_authority.py`, and tracked outputs in `generated/archive-assessment/ems-aa3/` (matrix, semantic and negative-invariant validation, publication manifest, AA2-to-AA3 decision traceability)

**The ambiguity this project removes.** Today a control with no rule and a control EMS has decided will never have a rule look identical to Hayes: both are `null`, both report "unresolved".

**Codebase map.** `.planning/codebase/` (mapped 2026-10-13). The architecture and structure documents classified most of `scripts/` by file name only; treat them as orientation.

**Working tree.** Branch `feature/ems-aa3-archive-applicability-authority`. Two modified registry files and about 60 untracked files from other in-flight work are present and are not part of this project.

## Constraints

- **Authority**: Oscar Mack is the approving EMS governance authority — no rule or no-rule decision is published on drafting judgment alone
- **Dual role**: The same person is the EMS approver and the Hayes developer — this must be written into each decision record, not left implicit
- **Drafting independence**: Drafts come from the control catalog definitions alone and are committed before any comparison with a target — prevents rules being shaped to a known result
- **Vocabulary**: Rule conditions use only the first four of the eight declared classification fields (`production`, `internet_exposed`, `contains_customer_data`, `ai_enabled`; the other four remain classification prerequisites, not rule fields) and the `KNOWN_TRUE` / `KNOWN_FALSE` states — Hayes's resolver requires this, and `UNKNOWN` must never resolve to not-applicable
- **Semantics**: Existing not-applicable semantics hold — explicit controlled rule required; unknown is not false; absence of evidence is not not-applicable
- **Boundary**: Nothing defined in Hayes is adopted into EMS — EMS chooses the shape
- **Publication pattern**: Follow the existing authority pattern (schema, publisher script, certification, traceability, pytest) — hash-based certification breaks on uncoordinated hand edits
- **Scope**: The 21 requested controls only — the other 59 stay undecided
- **Timeline**: Within days — keep the scope tight
- **Working tree**: Unrelated uncommitted work stays untouched and out of this project's commits — the commit Hayes re-pins to must contain only deliberate changes
- **Tech stack**: Python 3.12, `jsonschema`, PyYAML, pytest; Windows-primary with PowerShell wrappers — match the existing code

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Scope limited to the 21 controls in the request | Request names 21; deadline is days | — Pending |
| "No rule will be published" is an explicit published outcome with its own decision id | Lets Hayes tell "decided" from "not yet decided"; today both are `null` | — Pending |
| Drafts written from the catalog alone and committed before comparison with any target | The RiskMVP result for all 21 is already known; a rule written with it in view could be shaped to an outcome | ✓ Done in Phase 2: approved brief `6969f52`, drafting commit `dc3b41c`, record `be915e3` |
| Each rule or no-rule decision is backed by a new governance decision id | That id is the named authority Hayes cites; mirrors `AA1-GOV-001`..`008` | ✓ Done in Phase 3: `AA4-GOV-001`..`021`, one per control (`eed4a5f`); cited from the authority in Phase 4 |
| Dual role (EMS approver and Hayes developer) recorded in every decision record | Same person rules on both sides; workable only if explicit | ✓ Done in Phase 3: authority-approved sentence (`bcba0f1`) in all 21 records |
| Success is defined on the EMS side only | Three Hayes-side changes are needed before the live count moves; they belong to the next milestone in the Hayes repository | — Pending |
| Complete answer means a published, certified authority plus a written reply | Chosen over replying with a decision date alone | — Pending |
| EMS chooses the rule shape; Hayes's placeholder shape is not adopted | Hayes stated the shape is EMS's to choose and its placeholder is a stand-in | — Pending |
| Unrelated in-flight work left out of this project's commits | Assumed default, stated to the user before the PROJECT.md gate and not objected to | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-10-14 after Phase 5 (reply to Hayes) — reply committed (`7623f73`, `5f2e36c`; review fixes `ad46d43`..`c3dad63`, line-68 reword approved), `--validate` PASS. Open: push `feature/ems-aa3-archive-applicability-authority` so `54a7fd0` is on the remote before sending; 04-REVIEW.md hardening may lead to a v2.0.1 republish with fresh sign-off*
