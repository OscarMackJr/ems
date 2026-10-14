---
phase: 04-certified-publication
verified: 2026-10-14T00:00:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
warnings:
  - "CR-01: validate_signoff accepts role HAYES_VERIFY_DEVELOPER (gate fail-open; shipped sign-off uses EMS_GOVERNANCE_AUTHORITY)"
  - "CR-02: publisher does not run the decisions validator on the cited decisions file (gate gap; shipped decisions file independently passes the builder validator)"
  - "WR-01..WR-10 from 04-REVIEW.md: gate-hardening and test-quality issues, none falsify the published data"
---

# Phase 4: Certified Publication Verification Report

**Phase Goal:** A new controlled version of the archive-assessment applicability authority is published at a commit Hayes can re-pin to, with 21 explicit decisions citing governance decision ids and 59 "not yet decided".
**Status:** passed (with recorded gate-hardening warnings)
**Re-verification:** No, initial verification

## Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | 21 decided / 59 undecided; each decided control has rule+authority or no-rule+decision id; ids resolve to Phase 3 records | VERIFIED | `registry/archive_assessment_applicability_authority_v2.json`: 80 controls; states NOT_YET_DECIDED=59, NO_RULE_WILL_BE_PUBLISHED=18, RULE_PUBLISHED=3. Every decided control carries `not_applicable_authority` (e.g. AA4-GOV-001, AA4-GOV-014); a script check found 0 unresolved ids against the 21 `decision_id`s in `registry/archive_assessment_governance_decisions.json`. All 21 records: approver Oscar Mack, disposition APPROVED_AS_DRAFTED. |
| 2 | 59 others equal v1.0.0 apart from explicit state | VERIFIED | Compared against `git show 62a8955:registry/archive_assessment_applicability_authority.json` after removing `not_applicable_decision_state`: 0 differences across 59 controls. They keep `APPLICABILITY_UNRESOLVED`, rule None, authority None. |
| 3 | Publisher regenerates certification, manifest and traceability; digests match; `--validate` prints PASS | VERIFIED | Publication commit 54a7fd0 contains certification, manifest, decision traceability, matrix, semantic and negative validation outputs. `.venv/Scripts/python.exe scripts/publish_archive_assessment_applicability_authority_v2.py --validate` printed PASS (run by me). |
| 4 | pytest passes incl. decided=21, undecided=59, vocabulary, authority-present tests | VERIFIED | The 3 phase test modules ran: 214 passed. Orchestrator reports the full suite at 372 passed. |
| 5 | New id/version, lineage from 1.0.0 @ 62a8955, publication commit lists only project files | VERIFIED | `authority_id` EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0, version 2.0.0; `source_lineage.supersedes` = v1.0.0, commit 62a8955, sha256 f084607c...; `git show --stat 54a7fd0` lists exactly 9 files, all archive-assessment v2 artifacts (none of the unrelated modified/untracked files). Publication record commit 0ce89f2 adds only the publication record JSON naming 54a7fd09114704a97a7a48fce5f89aebeb48c90a. Signed off by Oscar Mack with role EMS_GOVERNANCE_AUTHORITY and the dual-role statement. |

## Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| PUB-01 (21 decisions citing ids) | SATISFIED | Truth 1 |
| PUB-02 (59 undecided, otherwise unchanged) | SATISFIED | Truth 2 |
| PUB-03 (certification, manifest, traceability, SHA-256) | SATISFIED | Truth 3 |
| PUB-04 (invariant tests) | SATISFIED | Truth 4 |
| PUB-05 (lineage from v1.0.0 @ 62a8955) | SATISFIED | Truth 5 |
| PUB-06 (commit only project changes) | SATISFIED | Truth 5 (9-file commit) |

All six IDs are marked complete in REQUIREMENTS.md; no orphaned Phase 4 requirements.

## Code Review Findings (04-REVIEW.md) Assessment

The review's defects are in publication gates, not in the published data. I confirmed the shipped data independently: sign-off role is `EMS_GOVERNANCE_AUTHORITY`; all 21 decision records have approver Oscar Mack and a valid disposition; `--validate` passes. The goal and the five success criteria are therefore met as published.

- **CR-01 (sign-off accepts HAYES_VERIFY_DEVELOPER):** Real fail-open gate defect. It does not affect the shipped sign-off. It weakens the "approved by EMS authority" guarantee for future publications. WARNING.
- **CR-02 (publisher never runs decisions validator):** Real gap; the publication gate can't catch a tampered decisions file. The shipped file was checked here (approver, disposition, id resolution) and is sound, and the builder's `--validate` passes. WARNING for the current publication; should be fixed before any republish.
- **WR-01** certification artifacts hard-code PASS/REJECTED_FAIL_CLOSED results (negative mutations are only exercised in pytest). This weakens the evidentiary value of the certification JSON. Success criterion 3 asks only that digests match and `--validate` passes, so it is not a goal failure.
- **WR-02/WR-03** the v2 schema does not require governance lineage and does not enforce one-use-per-field in a rule. A schema-only consumer is less protected than the Python validator. The published data does not exhibit either defect.
- **WR-04..WR-10** loose sign-off validation, `--build` able to rewrite the decisions file under a certified authority, `--validate` coupled to the live script digest (any fix to the publisher script turns `--validate` red against 54a7fd0 until a republish), weak or tautological tests, duplicated constants.

Recommendation: do not alter the publisher or schema now. Phase 5 should cite 54a7fd0 as is. Any hardening of the gates (CR-01, CR-02, WR-01..04, WR-06) changes the script digest and schema, so it requires a coordinated republish (for example 2.0.1) with fresh sign-off. Track as follow-up work.

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Published authority validates | publisher `--validate` | PASS | PASS |
| Phase tests | pytest on the 3 phase modules | 214 passed | PASS |

## Anti-Patterns

None blocking in the published data. No TBD/FIXME checks were run beyond the review. The review's findings are recorded above.

## Human Verification Required

None. The blocking human gate (Oscar Mack sign-off) was completed and is recorded in the committed sign-off file.

## Gaps Summary

No gaps against the phase goal. Residual risk is limited to the unhardened gates listed above.

---
_Verified: 2026-10-14_
_Verifier: Claude (gsd-verifier)_
