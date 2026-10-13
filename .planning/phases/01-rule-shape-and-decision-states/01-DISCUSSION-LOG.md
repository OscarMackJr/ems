# Phase 1: Rule Shape and Decision States - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-13
**Phase:** 1-Rule Shape and Decision States
**Areas discussed:** How conditions combine, Non-yes/no fields, States and outcomes, In place or new files

---

## How conditions combine

| Question | Options presented | Selected |
|----------|-------------------|----------|
| How should the conditions inside one rule combine? | Flat list, all must hold (recommended) / Nested ALL-ANY groups / Adopt the AA2 proposal (ALL, ANY, NOT, EQ, IN, KNOWN, UNKNOWN) | Flat list, all must hold |
| How should a control express "not applicable when A, or when B"? | Not supported in this version (recommended) / List of alternative condition lists / You decide | Not supported in this version |
| Should a rule be allowed to have zero conditions? | No, at least one condition (recommended) / Yes, allow unconditional rules | No, at least one condition |
| May the same field appear more than once in one rule? | No, each field at most once (recommended) / You decide | No, each field at most once |

**Notes:** The AA2 operator proposal was presented as never approved and wider than the vocabulary constraint.

---

## Non-yes/no fields

| Question | Options presented | Selected |
|----------|-------------------|----------|
| How should rules treat owner, tier, service_criticality, data_classification? | Rules use the four yes/no fields only (recommended) / All eight with a published meaning each / All eight, meaning left to the target description | Rules use the four yes/no fields only |
| How should the authority state which fields a rule may use? | Explicit published list (recommended) / Schema enum only | Explicit published list |
| Publish a one-line meaning for each of the four yes/no fields? | Yes, short definition per field (recommended) / No, field names stand as is / You decide | Yes, short definition per field |

**Notes:** Definition wording is governance content; recorded as needing Oscar Mack's approval before commit.

---

## States and outcomes

| Question | Options presented | Selected |
|----------|-------------------|----------|
| What applicability does "no rule will be published" resolve to? | APPLICABLE (recommended) / Still APPLICABILITY_UNRESOLVED / State only, no result claimed | APPLICABLE |
| Rule published, all fields known, conditions not all met? | APPLICABLE (recommended) / APPLICABILITY_UNRESOLVED | APPLICABLE |
| One named field known and failing, another UNKNOWN? | APPLICABILITY_UNRESOLVED (recommended) / APPLICABLE | APPLICABILITY_UNRESOLVED |
| State value names? | RULE_PUBLISHED / NO_RULE_WILL_BE_PUBLISHED / NOT_YET_DECIDED (recommended) / RULE_PUBLISHED / NO_RULE_DECIDED / UNDECIDED / You decide | RULE_PUBLISHED / NO_RULE_WILL_BE_PUBLISHED / NOT_YET_DECIDED |
| Where does the decision id for a no-rule control go? | One decision-authority field for both outcomes (recommended) / Separate field for no-rule / You decide | One decision-authority field for both outcomes |
| Pattern for new governance decision ids? | AA4-GOV-NNN (recommended) / Id embeds the control number / Id embeds the request | AA4-GOV-NNN |
| Should default_applicability_result change for a decided control? | Keep it; state semantics once at top level (recommended) / Set it per control | Keep it; state semantics once at top level |

---

## In place or new files

| Question | Options presented | Selected |
|----------|-------------------|----------|
| Where should the new shape live? | New versioned files beside v1.0.0 (recommended) / Change v1.0.0 files in place / Shared module plus thin publishers | New versioned files beside v1.0.0 |
| What version does the new authority carry? | 2.0.0 (recommended) / 1.1.0 / You decide | 2.0.0 |
| What does Phase 1 commit as the authority document? | Schema, semantics and tests only (recommended) / An all-NOT_YET_DECIDED authority file | Schema, semantics and tests only |

---

## Claude's Discretion

- JSON key names inside a condition and for the decision-state field
- File names for the v2 publisher, schema and test
- Whether a `docs/` page accompanies the semantics block
- Split of consistency enforcement between JSON Schema and validator code
- Validation error wording

## Deferred Ideas

- Alternative condition lists ("or") per control
- Rule conditions over the four non-yes/no fields with approved meanings
- Shared helper module for v1 and v2 publishers
