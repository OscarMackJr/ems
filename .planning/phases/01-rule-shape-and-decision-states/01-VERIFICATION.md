---
phase: 01-rule-shape-and-decision-states
verified: 2026-10-13T18:00:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 1: Rule Shape and Decision States Verification Report

**Phase Goal:** EMS has a chosen, machine-checkable shape for a not-applicable rule, its named authority and a three-valued decision state per control, with rule semantics written out in full, so a rule can be drafted and published without meaning left to convention.
**Status:** passed (initial verification)

## Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Schema passes a RULE_PUBLISHED control (rule + AA4-GOV id), a NO_RULE_WILL_BE_PUBLISHED control (with id) and a NOT_YET_DECIDED control | VERIFIED | Probe against `schema()` and `validate_authority()`: rule+authority accepted by both; no-rule+AA4-GOV-002 accepted; built authority has 80 controls all NOT_YET_DECIDED and validates |
| 2 | Inconsistent combinations rejected (rule w/o authority, undecided w/ rule, decided w/o id, state outside three values) | VERIFIED | Probe: all four rejected by BOTH schema and Python validator |
| 3 | Rejects field outside the allowed set, state UNKNOWN or other, and free-text such as `absence_of_evidence` | VERIFIED | Probe: `tier` field, UNKNOWN state and free-text rule rejected by both schema and validator. Rules are restricted to 4 of the 8 fields (CONTEXT D-07/D-08, noted in ROADMAP) |
| 4 | Semantics block states AND combination, satisfied rule -> NOT_APPLICABLE, UNKNOWN never -> not-applicable | VERIFIED | `semantics()` has a full `resolution` table (all-known+met -> NOT_APPLICABLE, any UNKNOWN -> APPLICABILITY_UNRESOLVED), `unknown_is_never_not_applicable: true`, `no_short_circuit`, statements and field definitions |
| 5 | Existing AA3 pytest invariants pass; v1.0.0 content unaltered | VERIFIED | `git diff 1ff6f2c~1..HEAD` shows no change to the v1 publisher, v1 schema or v1 registry JSON. 87 archive/applicability tests pass, including 71 new v2 tests. v2 is a new versioned publisher and schema (version 2.0.0, new authority_id). No v2 registry file was written (by design, D-19) |

**Score:** 5/5

## Requirements Coverage

| Requirement | Plans | Status | Evidence |
|-------------|-------|--------|----------|
| SCHEMA-01 structured rule | 01-02, 01-03 | SATISFIED | Rule object schema and validator |
| SCHEMA-02 authority names a decision id | 01-02, 01-03 | SATISFIED | `AA4-GOV-NNN` pattern |
| SCHEMA-03 three-valued decision state | 01-02, 01-03 | SATISFIED | Enum of three states, all 80 controls carry one |
| SCHEMA-04 inconsistent combinations rejected | 01-02, 01-03 | SATISFIED | Probe above |
| SCHEMA-05 declared fields and KNOWN_TRUE/KNOWN_FALSE only | 01-02, 01-03 | SATISFIED | Probe above |
| SCHEMA-06 semantics written out | 01-01, 01-02, 01-03 | SATISFIED | `semantics()`; field definitions approved by Oscar Mack (01-FIELD-DEFINITIONS.md) |

All six IDs appear in the plan frontmatter and in REQUIREMENTS.md. No orphans. The REQUIREMENTS.md checkboxes and traceability rows still read "Pending"; the orchestrator should tick them on phase completion.

## Behavioral Spot-Checks

- pytest (`-k "archive_assessment or aa3 or applicability_authority"`): 87 passed.
- `--emit-schema` exits 0. `--validate` fails closed with "v2 registry authority file is not published", as designed.
- No debt markers (TBD/FIXME/XXX) checked in the three source files beyond the review; the review reports none.

## Code Review Findings (weighed independently)

None is a goal-blocking gap for Phase 1. All are hardening items that should be scheduled before or inside Phase 4:

- **CR-01 (lineage sha256 computed over CRLF working-tree bytes):** real defect, but it affects publication and certification, not the rule shape or decision states. Phase 4 SC5 covers lineage and hash certification, so it must be fixed before Phase 4 publishes (normalise line endings in `digest()` and recompute and compare in the validator). Deferred to Phase 4. WARNING.
- **WR-01 (resolver returns NOT_APPLICABLE for controls the validator rejects):** the resolver is a test oracle and is not consumed by Hayes. The published semantics are correct. Worth fail-closing. WARNING.
- **WR-02 (authority existence check opt-in):** no decision records exist until Phase 3. Make it mandatory when Phase 4 wires `--validate`. WARNING, Phase 3/4.
- **WR-03 (trailing newline accepted by the id pattern):** minor. Use `fullmatch` and length bounds. WARNING.
- **WR-04 (schema weaker than validator: contradictory duplicate-field rules, unpinned statements):** the validator rejects them, and SC3 does not require the schema to catch duplicates. WARNING.
- **WR-05 to WR-07, WR-08, WR-09:** gaps in wording pinning, vocabulary checks, crash on malformed input, test specificity and coverage. Hardening; they do not falsify any success criterion. WARNING.
- **IN-01:** the CLAUDE.md constraint says "eight declared fields", but the implementation allows 4. This is a recorded decision (D-07/D-08), and the ROADMAP SC3 note acknowledges it. Update the CLAUDE.md wording.

Recommend a short hardening gap-closure (CR-01, WR-01, WR-02, WR-03) before Phase 4. It is optional for advancing to Phase 2.

## Human Verification

None outstanding. Field-definition approval (D-10) is recorded in the committed `01-FIELD-DEFINITIONS.md` (Approver: Oscar Mack, Status: APPROVED). Note that the draft was committed before approval; the wording is unchanged since.

## Anti-Patterns

No blocker stubs found. Registry-wide dirty tree files (adjudication_rules.json, policy_decisions.json, untracked files) were not touched by the phase commits.

---
_Verified: 2026-10-13_
_Verifier: Claude (gsd-verifier)_
