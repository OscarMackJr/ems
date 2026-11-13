---
phase: 09-certified-republication-2-0-2
verified: 2026-11-12T00:00:00Z
status: passed
score: 9/9 must-haves verified (WR-01 gap closed in 6e47a4f)
overrides_applied: 0
requirements: [PUB-07, PUB-08, PUB-09]
publication_commit: ae15c7458e49c8f55cc58c61bab04bc716aa9892
record_commit: a71257ed267410138a3c4daba412b00c116663d8
ci_run_id: 43332405316
ci_head_sha: a71257ed267410138a3c4daba412b00c116663d8
re_verification: true
gaps:
  - truth: "09-02 must-have / D-02: reply validator fails when a constant (REPLY_PUBLICATION_COMMIT) is tampered, including re-pointing to a different valid commit"
    status: closed
    closed_by: "6e47a4f — load_inputs requires REPLY_PUBLICATION_COMMIT == record['publication_commit']; tamper test adds 4d9b7c1 and b3c0411; orchestrator run: reply --validate PASS, reply module 66 passed"
    reason: "REPLY_PUBLICATION_COMMIT is never bound to record['publication_commit']. validate_reply() passes if the constant is set to any commit where the 2.0.1 files are byte-identical (reviewer reproduced with 4d9b7c1 and b3c0411). test_validate_rejects_tampered_constant only tries 'd'*40 and 54a7fd0, which fail for unrelated reasons. Reply bytes stay correct (pin comes from the record), so no roadmap success criterion is affected."
    artifacts:
      - path: "scripts/build_archive_assessment_demo3_w1_req_001_reply.py"
        issue: "load_inputs (L248-255) lacks a record['publication_commit'] == REPLY_PUBLICATION_COMMIT check"
      - path: "tests/test_archive_assessment_demo3_w1_req_001_reply.py"
        issue: "tampered-constant test lacks a valid-but-wrong commit case"
    missing:
      - "Add the binding check in load_inputs (fix text in 09-REVIEW.md WR-01) and add REPLY_PUBLICATION_COMMIT=4d9b7c1... to the tamper parametrization"
      - "No republication needed: the reply builder and tests are not in the publication manifest"
human_verification: []
---

# Phase 9 Verification: Certified republication 2.0.2

**Phase goal:** Publish `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2` at a commit Hayes can re-pin to, with the corrected lineage, gates and schema, and every applicability decision identical to 2.0.0 and 2.0.1.
**Re-verification:** No. This is the initial authoritative verification. The orchestrator's draft was independently re-checked.
**Status:** passed. All four ROADMAP success criteria and all three requirements hold. The verifier found one 09-02 must-have only partly met (WR-01). It was closed in 6e47a4f without republication: the reply builder and its tests are not in the publication manifest.

## Key identifiers

| Item | Value |
|------|-------|
| Publication commit (Hayes pins) | ae15c7458e49c8f55cc58c61bab04bc716aa9892 |
| Record commit | a71257ed267410138a3c4daba412b00c116663d8 |
| Authority | EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2 |
| Authority LF sha256 | a44eea1f98ec361ab100c554eb3a8d3529cfeb1fec78ec6d38193a675f0b8beb |
| Manifest sha256 | 9991228ab7ff0a0c52c61b77a4d4c0e58b56d68b0c382caa83496621f092bac2 |
| Governance decisions LF sha256 | 4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f |
| Supersedes | 2.0.1 @ 31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb |
| Sign-off | Oscar Mack, EMS_GOVERNANCE_AUTHORITY, 2026-11-12, dual-role statement present |
| CI run | 43332405316 (workflow_dispatch), success; jobs validate and archive-assessment both success |

## Independent checks run by the verifier (read-only git and `python -I`)

- Both commits exist. Remote branch tip is `a71257e` (`git ls-remote`).
- `gh run view 43332405316`: conclusion success, headSha is `a71257e...`, jobs `validate` and `archive-assessment` both success.
- `git show --stat ae15c74`: exactly 10 files (schema, authority, sign-off, publication doc, certification, manifest, and 5 generated outputs: traceability, matrix, negative-invariant, semantic validation). No unrelated or untracked files.
- `git show --stat a71257e`: only `registry/archive_assessment_applicability_authority_v2_publication_record.json`.
- `git diff --name-only ae15c74 a71257e -- . ':(exclude).planning'` lists only the record file. The commit in between (06eb7aa) touches only `.planning`.
- `git diff --name-only ae15c74~1 ae15c74 -- scripts tests` is empty, so no code changed in the publication commit.
- No tag points at HEAD.
- The authority at ae15c74 recomputes (CRLF_TO_LF) to `a44eea1f...`, which matches the record. The governance decisions file recomputes to `4e746d1f...`, which matches.
- Authority content at ae15c74:
  - id and version are 2.0.2.
  - 80 controls: 3 RULE_PUBLISHED, 18 NO_RULE_WILL_BE_PUBLISHED, 59 NOT_YET_DECIDED.
  - Rules: CTRL-030 production=KNOWN_FALSE, CTRL-039 production=KNOWN_FALSE, CTRL-052 ai_enabled=KNOWN_FALSE.
  - `source_lineage.supersedes` names 2.0.1 at 31addfa with sha `7be5eb88...` and decisions sha `4e746d1f...`.
  - `applicability_decision_ids` equal 2.0.1's.
- All 80 control rows are fully identical to the 2.0.1 authority at 31addfa (0 rows differ on any field), so decision content is identical.
- The reply artifacts (reply doc, JSON and schema) show an empty diff between e781f08 and HEAD (D-01).

Orchestrator-run evidence, not re-run here:

- `-k archive_assessment` gives 720 passed, 0 failed, 0 skipped at the record commit.
- All 5 CI validators PASS.
- `--validate --pre-publication` passes at the publication commit.

## Observable truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC1 | After a dry run and Oscar Mack's sign-off, 2.0.2 is written with certification, manifest and traceability. Lineage supersedes 2.0.1 at 31addfa. `--validate` prints PASS and the full suite is green (red window closed). | VERIFIED | Sign-off file (approver, role, date, dual-role). Lineage `supersedes` is bound to 31addfa. The manifest, certification and traceability are in the ae15c74 stat. The orchestrator ran 720 passed, 0 failed, and validators PASS at a71257e. Baseline reds are listed in 09-BASELINE-RED.md and now green. |
| SC2 | The decisions digest equals 2.0.0's (4e746d1f). 21 decided (3 rules, 18 no-rule) and 59 undecided. Per-control comparison with 2.0.1 is identical for all 80. | VERIFIED | Recomputed digest matches. Counters 3/18/59. 0 differing rows against 31addfa. |
| SC3 | `git show --stat` on the publication commit lists only this milestone's files. The publication SHA is recorded in a later commit. | VERIFIED | The ae15c74 stat lists 10 intended paths. The record at a71257e names ae15c74. |
| SC4 | The CI `archive-assessment` job passes on the publication commit (run id recorded). | VERIFIED (by D-04 reading) | The run is green on a71257e. The record file is the only non-.planning difference from ae15c74, so every publication file is byte-identical. Plain `--validate` is red at ae15c74 by design (the record still names 2.0.1). The literal CI-on-ae15c74 reading is not met, and no pre-publication CI mode was added. See Judgment calls. |
| PUB-07 | 2.0.2 published with certification, manifest and traceability, superseding 2.0.1 at 31addfa. | VERIFIED | As SC1. |
| PUB-08 | No decision change: digest equals 2.0.0's, counts 21/59, per-control content identical. | VERIFIED | As SC2. The comparison also runs in `validate_publication` and fails closed on missing history (GitHistoryError). |
| PUB-09 | The publication commit contains only this milestone's changes, and CI `archive-assessment` passes on it. | VERIFIED (by D-04 reading) | As SC3 and SC4. |
| 09-03 | The dry-run sign-off summary is complete per D-10. | VERIFIED with a WARNING | See WR-03 below. |
| 09-02 | The frozen reply validator fails on a tampered reply or a tampered constant (D-02). | VERIFIED (gap closed in 6e47a4f) | See WR-01 below and the closure note in Gaps summary. |

**Score:** 8/9 must-haves fully verified. The partial item is the 09-02 constant-tamper must-have only.

## Requirements coverage

Every ID in the PLAN frontmatter was cross-referenced against REQUIREMENTS.md. No requirement is orphaned. Phase 9 maps to PUB-07, PUB-08 and PUB-09 only, and all three are accounted for.

| ID | Status | Evidence |
|----|--------|----------|
| PUB-07 | SATISFIED | See truths above. |
| PUB-08 | SATISFIED | See truths above. |
| PUB-09 | SATISFIED | See truths above. |

Housekeeping: REQUIREMENTS.md still shows PUB-07, PUB-08 and PUB-09 as `[ ]` and "Pending" (L28-30, L66-68). The orchestrator should tick them in the phase-completion step. The ROADMAP row is already marked complete.

## Judgment calls on the code review

**WR-01 (reply validator accepts a tampered REPLY_PUBLICATION_COMMIT): a must-have gap.**
- It is a real shortfall against the 09-02 plan must-have and D-02. The plan explicitly requires a "different valid commit" tamper to raise, and the reviewer reproduced it passing.
- It is not a ROADMAP success-criterion gap and not a PUB-07/08/09 gap. The reply is a frozen 2.0.1 artifact, the reply bytes are unaffected (the pin comes from the record), and the reply builder is outside the publication manifest.
- It needs no republication. It is a small fix: a one-line binding check plus one test parameter.
- I recorded it as a `partial` gap because the decision tree makes any failed plan truth gaps_found. Severity is WARNING. It does not block Phase 10 or the pinned commit. The orchestrator may either run a short `--gaps` plan to close it, or accept it with an override. Override suggestion:

```yaml
overrides:
  - must_have: "tampering with a reply constant fails (REPLY_PUBLICATION_COMMIT re-pointed to a different valid commit)"
    reason: "Frozen 2.0.1 reply artifact; bytes unaffected; fix deferred, no republication needed"
    accepted_by: "Oscar Mack"
    accepted_at: "<ISO timestamp when accepted>"
```

**WR-03 (dry-run summary incomplete per D-10): not a gap that blocks. WARNING, accept.**
- The summary omits the statement that the AA1 manifest is committed under RAW_BYTES and the commit pins, and it lists only one of the two supersedes normalisations.
- The sign-off covered the authority bytes and the no-decision-change statement. The facts omitted are all verifiable in the authority's `source_lineage`, which I read.
- Fixing the publisher would change its digest (`f6b51cca...` is in the manifest) and force a republication. That cost is not justified.
- Carry the "AA1 manifest committed, RAW_BYTES" statement into the Phase 10 notice, as the reviewer recommends.

**Other review items.**
- WR-02 (frozen reply validator depends on live publisher code) and WR-04 (silent skips when the 2.0.1 blob is unreachable): non-blocking hardening. This clone has the blob, and the orchestrator run showed 0 skipped.
- IN-05 is worth a follow-up: nothing in plain `--validate` guards the publisher script digest. Only the pytest in the reply test file does.

## Judgment calls on the SC4 / PUB-09 reading (D-04)

- Hayes pins ae15c74. At that commit the record file still names 2.0.1, so plain `--validate` and CI are red there. This is by design, because the commit that records the SHA cannot be the commit it names.
- The green `archive-assessment` run covers a71257e. The 10 publication files are byte-identical between the two commits (the `git diff` above is empty apart from the record file). CI therefore certifies exactly the bytes Hayes pins. I accept this as satisfying SC4 and PUB-09 in substance.
- A reader who requires CI to be green on the literal pinned SHA would see this as unmet. I judge that reading unsatisfiable under the self-referential record, and the documented trade-off is explicit and honest.

## Anti-patterns

No TBD, FIXME or XXX markers or stubs were found in the reviewed files. The review lists no critical findings. IN-01 notes a dead DIFFER branch in the publisher, which is deferred because it would need a republication.

## Behavioral spot-checks and probes

The verifier did not re-run pytest or validators, per instruction. The orchestrator's PowerShell results are cited above. Independent recomputation of the authority and decisions digests, the stat scopes, and the row-for-row comparison all passed. No phase probe scripts were declared.

## Human verification

None required. The sign-off by Oscar Mack is recorded in the committed sign-off file, and the push approval was given in-session per the 09-05 summary.

## Gaps summary

The phase goal is achieved. 2.0.2 is published at ae15c74 with every decision identical to 2.0.1 and 2.0.0. The record commit a71257e is pushed, and CI is green on a bytes-identical tree. The only open item is WR-01, a missing binding check in the frozen reply validator, which is fixable with no republication.

**WR-01 closure (orchestrator, 6e47a4f):** `load_inputs` now raises AuthorityError unless REPLY_PUBLICATION_COMMIT equals the frozen record's `publication_commit`. `test_validate_rejects_tampered_constant` adds 4d9b7c1 and b3c0411, the two valid-but-wrong commits the reviewer reproduced. Orchestrator PowerShell run: reply `--validate` PASS; `tests/test_archive_assessment_demo3_w1_req_001_reply.py` 66 passed, 0 failed. The reply artifacts and the certified publisher are unchanged. CI run 43332405316 predates this fix and covers HEAD a71257e; the fix is local and not pushed.

**Carried forward (not gaps):**
- WR-03: put the AA1-manifest "committed, RAW_BYTES" statement and the commit pins in the Phase 10 notice. Fixing the dry-run text would force a republication.
- WR-02, WR-04 and IN-01..06: hardening notes, see 09-REVIEW.md.

---

_Verified: 2026-11-12_
_Verifier: Claude (gsd-verifier)_
