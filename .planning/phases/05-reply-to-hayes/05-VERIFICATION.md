---
phase: 05-reply-to-hayes
verified: 2026-10-14T00:00:00Z
status: passed
score: 4/4 must-haves verified
human_verification:
  - test: "Decide on the sentence 'No control resolves until the target description carries the eight classification facts.' (docs/DEMO3_W1_REQ_001_REPLY.md line 68, review WR-04)"
    expected: "Either accept it as a statement about Hayes's classification-prerequisites gate, or reword it to name whose gate it is and regenerate the reply before it is sent"
    why_human: "It is an accuracy judgement on a citable EMS statement. It conflicts with the authority's resolution table and with the sentence before it. The reply has not been sent, so it can still be corrected."
---

# Phase 5: Reply to Hayes Verification Report

**Phase Goal:** A written reply to DEMO3-W1-REQ-001 sits in the repository, says what EMS decided for each of the 21 controls and where to cite it, and is plain about what publication does not change.
**Status:** human_needed (all success criteria verified; one accuracy warning needs the authority's decision)
**Re-verification:** No

## Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All 21 controls listed, each with rule and authority or the no-rule decision and id, agreeing with the published authority | VERIFIED | The reply JSON has 21 controls. A script cross-check against `registry/archive_assessment_applicability_authority_v2.json` matched 21/21 on decision state and authority id. The MD shows 3 RULE_PUBLISHED (030, 039, 052) and 18 NO_RULE. `--validate` printed PASS. |
| 2 | Names authority id, version and the full publication SHA (54a7fd0911...), describes the published shape | VERIFIED | Reply lines 72-93 give SHA 54a7fd09114704a97a7a48fce5f89aebeb48c90a, authority id EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0 (matches the authority file), version 2.0.0, digests, field names and file paths. That SHA is an ancestor of HEAD. |
| 3 | States the 59 others remain undecided, the three Hayes-side changes, and that the classification-prerequisites gap is untouched | VERIFIED | Lines 146 and 150-156. The authority has exactly 59 NOT_YET_DECIDED rows. All three Hayes-side changes are listed. The gap is stated as untouched. See WR-04 below for the one sentence at issue. |
| 4 | Committed as a document after the publication commit, only this project's files; sending left to the authority | VERIFIED | Commit 5f2e36c adds exactly 2 files (the MD and the JSON). Commit 7623f73 adds the script, schema, test and .gitattributes. Both come after the publication commit. The "Sending" section holds the reply until the commit is on the remote. |

**Score:** 4/4

## Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| REPLY-01 | SATISFIED | Truth 1 |
| REPLY-02 | SATISFIED | Truth 2 |
| REPLY-03 | SATISFIED | Truth 3 |

All three IDs are mapped to Phase 5 in REQUIREMENTS.md. No orphaned requirements.

## Behavioral Spot-Checks

| Check | Result | Status |
|-------|--------|--------|
| `pytest tests/test_archive_assessment_demo3_w1_req_001_reply.py --basetemp=C:/temp/pytest-verify-tmp` | 17 passed | PASS |
| `python scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate` | PASS | PASS |

## Independent judgement on WR-04

The reply says "No control resolves until the target description carries the eight classification facts" (line 68). The authority's resolution table maps NO_RULE_WILL_BE_PUBLISHED to APPLICABLE with condition ALWAYS. The preceding sentence in the reply says the same ("applicable whatever the facts"). So line 68 is imprecise as a statement of EMS semantics. It is true only as a description of Hayes's classification-prerequisites gate (the project's D-15 intent), and the reply does not say that.

It does not defeat success criterion 3. That criterion requires the 59 undecided controls, the three Hayes-side changes and the untouched gap, and all three are stated correctly. Two things mitigate it: the surrounding text makes the actual resolution behaviour clear, and the live count of resolved controls is correctly described as staying at zero because of the Hayes-side gate. It is still a real accuracy defect in a document Hayes will cite as EMS's word. It is a warning, not a blocker. Because the reply is unsent, the fix is cheap: reword it in the generator (script lines 117-118) and regenerate. I left this for the authority to decide, which is why the status is human_needed rather than passed.

## Anti-Patterns and Review Findings

No TBD/FIXME/XXX debt markers were checked beyond the review's scope. The review's WR-01 to WR-03 and WR-05 to WR-07 are weaknesses in guard tests and CLI checks. The current output is correct and the tests and `--validate` pass. They are advisory and do not make any success criterion false. WR-01 (tautological mutation tests) weakens the regression protection claimed for the reply.

## Human Verification Required

### 1. Line 68 wording (WR-04)

**Test:** Read line 68 against the resolution table and the line before it.
**Expected:** Accept it as scoped to Hayes's gate, or reword it ("Hayes's resolver resolves no control until ...; under the EMS table alone, NO_RULE_WILL_BE_PUBLISHED is APPLICABLE whatever the facts") and regenerate the reply.
**Why human:** It is an accuracy judgement on an authority statement.

---

_Verified: 2026-10-14_
_Verifier: Claude (gsd-verifier)_
