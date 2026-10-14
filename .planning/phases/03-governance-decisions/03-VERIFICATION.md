---
phase: 03-governance-decisions
verified: 2026-10-14T00:00:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
gaps: []
deferred: []
warnings:
  - id: CR-01
    classification: non-goal-blocking debt (fix before Phase 4 certification)
  - id: CR-02
    classification: non-goal-blocking debt (fix before Phase 4 relies on the validator)
  - id: CR-03
    classification: non-goal-blocking debt (latent, affects only future supersession)
---

# Phase 3: Governance Decisions Verification Report

**Phase Goal:** The EMS governance authority has personally approved, changed or rejected each of the 21 proposals, and each outcome is a machine-readable, schema-validated governance decision with its own id that names the approver's dual role.
**Status:** passed (with three carried-forward code-review debts, below)
**Re-verification:** No, initial verification

Scope note: I checked structure, provenance and consistency only. I did not assess whether any disposition, note or rationale is correct.

## Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | 21 individual dispositions, one per requested control, no blanket approval | VERIFIED | `registry/archive_assessment_governance_decisions.json` has 21 records, one per control in the requested set (009,010,011,012,013,014,015,017,018,019,020,021,022,030,033,039,042,052,062,075,079). Each has its own `disposition` (all 21 are `APPROVED_AS_DRAFTED`) and its own `note`. There are 21 distinct notes. The answers file has no approve-all value. `--validate-answers` (strict) prints PASS. Answers commit cc74445 touches only the answers file. The "given by Oscar Mack" claim is established by commit provenance and the `approver` field, not independently provable by a verifier. See Provenance caveat. |
| 2 | Unique decision ids, no collision with AA1-GOV-001..008, each cites the Phase 2 drafting commit | VERIFIED | Ids are exactly AA4-GOV-001..021, in control order and unique. All 21 cite `dc3b41c9fbb3571a191d2da5164fb73439a0637b`. `git cat-file -t` on that SHA returns `commit`. It is "docs(02): commit blind-drafted rule proposals". |
| 3 | Every record states the dual role in its own text | VERIFIED | All 21 records carry `approver_roles` [EMS_GOVERNANCE_AUTHORITY, HAYES_VERIFY_DEVELOPER] and `dual_role_statement` ("...EMS governance authority and is also the developer of Hayes Verify..."). The wording is bound to `registry/archive_assessment_governance_wording_approval.json`. |
| 4 | Schema validation passes; removing dual-role statement, decision id, disposition or control id fails | VERIFIED | The decisions file validates against `schemas/archive_assessment_governance_decisions.schema.json`. I deleted each of the four fields from record 0 in memory, and in every case the schema reported errors. `--validate` prints PASS. The orchestrator reports the full suite at 277 passed. |
| 5 | Where changed, both drafted and decided text shown; Phase 2 drafting commit unamended | VERIFIED | Every record has `drafted` and `decided` side by side. Because every disposition is `APPROVED_AS_DRAFTED`, no change exists and `amendment_present` is false. The proposals file has no diff between dc3b41c and HEAD. The drafting record was added after dc3b41c. It is a new file, so dc3b41c itself is not amended. |

**Score:** 5/5

## Requirements Coverage

| Requirement | Source plans | Status | Evidence |
|-------------|-------------|--------|----------|
| GOV-01 | 03-02, 03-03, 03-04 | SATISFIED | 21 individual dispositions typed in the answers file (cc74445) and carried into the records. |
| GOV-02 | 03-01, 03-03, 03-04 | SATISFIED | Unique ids AA4-GOV-001..021. |
| GOV-03 | 03-01, 03-03, 03-04 | SATISFIED | Dual-role statement and roles in all 21 records. |
| GOV-04 | 03-02, 03-03, 03-04 | SATISFIED | Records are JSON, schema-validated, and negative-tested. |

All four IDs appear in the plan frontmatter and in REQUIREMENTS.md. No orphaned Phase 3 requirements. The REQUIREMENTS.md checkboxes are still pending by design, so they are not a gap.

## Artifacts and Wiring

| Artifact | Status |
|----------|--------|
| `registry/archive_assessment_governance_decisions.json` | Exists, substantive (21 full records), validated by script and schema. |
| `registry/archive_assessment_governance_answers.json` | Exists, filled, strict-valid. |
| `registry/archive_assessment_governance_wording_approval.json` | Exists, and the decisions header references and hashes it. |
| `schemas/archive_assessment_governance_{answers,decisions}.schema.json` | Exist and are used. |
| `scripts/build_archive_assessment_governance_decisions.py` | `--validate-answers` and `--validate` both print PASS. |
| `tests/test_archive_assessment_governance_*.py` | Run green (orchestrator: 277 passed). |

The decisions commit eed4a5f contains exactly one file. No v2 authority, certification or reply was produced, which matches the plan.

## Code Review Findings Weighed Against the Goal

The goal is: personally decided, machine-readable, schema-validated, own id, dual role named.

- **CR-01 (raw-byte input hashes fail on a CRLF clone): non-goal-blocking debt.** It does not touch the goal's properties. The records are machine-readable. They pass the JSON schema on any checkout, and the schema negative tests do not depend on line endings. What fails on a fresh Windows clone is the semantic `--validate` script's provenance cross-check (`proposals_sha256` and `drafting_record_sha256`) and 6 hash-dependent tests. The record contents are unaffected. The risk is real for the consumer, though. Hayes pins a commit and may re-validate on Windows. It must be fixed before Phase 4, which certifies hashes and publishes the commit Hayes re-pins to. It should be tracked as a Phase 4 prerequisite, not left as an unscheduled follow-up. It is an open risk to criterion 4 for fresh Windows checkouts, but it does not invalidate the 21 decisions.
- **CR-02 (validator does not tie records to the answers file): non-goal-blocking debt.** Today the committed records equal the answers. The orchestrator established that the pytest reproducibility test passes, and the answers hash is set. The weakness is that `--validate` alone cannot catch tampering after the fact. This matters for the Phase 4 traceability claim, so it should be fixed before Phase 4 relies on `--validate` as its gate.
- **CR-03 (superseding entries skip strict checks): non-goal-blocking debt.** No superseding entries exist. All 21 records have `supersedes: null`, so no current record is affected. It is a latent defect in the change-of-mind path only.

None of these makes any of the 5 success criteria false in the committed repository state.

## Anti-Patterns

I made no TBD/FIXME/XXX debt-marker scan of the modified files. The review documents WR-01..WR-09 (warnings: templated-note guard, date realism, partial wording-approval check, and similar) and IN-01..05, none goal-blocking.

## Human Verification

The human gate (authority personally gives each disposition) was executed in plan 04. A verifier cannot prove that Oscar Mack typed the answers beyond commit provenance: the answers commit cc74445 touches only the answers file, and its content differs from the blank template. The orchestrator is the party that observed the interaction. No further human item is raised.

## Gaps Summary

No goal gaps. Recommended carry-forward into Phase 4 planning: CR-01 (LF-normalise the proposals and drafting-record hashes, and add `.gitattributes`), CR-02 (bind `answers_sha256` and a fresh rebuild into `--validate`), CR-03 (strict-check all entries).

---

_Verified: 2026-10-14_
_Verifier: Claude (gsd-verifier)_
