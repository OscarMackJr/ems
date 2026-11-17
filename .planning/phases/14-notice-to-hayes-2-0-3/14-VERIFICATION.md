---
phase: 14-notice-to-hayes-2-0-3
verified: 2026-11-17T20:00:00Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
---

# Phase 14: Notice to Hayes (2.0.3) Verification Report

**Phase Goal:** Hayes receives a generated, validated notice for 2.0.3 whose claims are enforced rather than asserted, and which tells Hayes how to verify at the pin and re-pin.
**Status:** passed. **Re-verification:** No.

## Observable Truths

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|---|---|---|
| 1 | Notice cites 2.0.3 id, version, commit; lists changes; states no decision changed; asks Hayes to re-pin | VERIFIED | `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md` contains id EMS-AA3-...-2.0.3, version 2.0.3, pin 1544dc19..., "What to do" re-pin item, "What changed in 2.0.3" section, "No decision changed" section (0 of 80 rows differ). I ran `--validate` myself: prints PASS in about 11s. |
| 2 | Exact commands to verify at the pin and at the record commit, with meaning of each result | VERIFIED | "How to verify": step 1 `--validate --at-pin` at the pin, step 2 `--validate` at record commit 87a46d1, step 3 notice validation. A results table gives meaning and action. Prerequisites include a full clone and the jsonschema pin. |
| 3 | Builder runs every negative mutation and records a domain rejection each; validator fails if any not rejected | VERIFIED | Builder has `pinned_mutation_run`, which loads the publisher from the pin, and `check_rerun`, which raises `AuthorityError("mutation ... was not rejected by the rerun")`. The registry JSON records 29 mutations with the rejecting gate. The notice states "29 negative mutations ... each was run and rejected". Orchestrator ran 89 tests, all passed. |
| 4 | Validator recomputes all 7 lineage digests from git; "wrong scope" statement computed from raw vs LF hashes | VERIFIED | `lineage_entries` hashes `git_show(at, path)` through the per-entry normaliser for all 7 entries (aa1_manifest, aa2_approval, aa2_closure, catalog_reference, governance_decisions, supersedes, v1_baseline). `digest_scope_error` computes raw and LF sha256 for the 3 RAW_BYTES files, and the notice prints values that differ for each. |

**Score:** 4/4

## Requirements Coverage

| Requirement | Status | Evidence |
|---|---|---|
| NOTICE-03 | SATISFIED | SC1 evidence. Notice generated and `--validate` PASS. Includes PIN-03 guidance and a re-pin request. |
| PIN-03 | SATISFIED | "How to verify" section with commands and a result-meaning table. |
| CLAIM-01 | SATISFIED | Mutation rerun and `check_rerun`. |
| CLAIM-02 | SATISFIED | 7 digests recomputed from git. |
| CLAIM-03 | SATISFIED | Raw vs LF hashes computed for each RAW_BYTES file. |

All 5 IDs are mapped to Phase 14 in REQUIREMENTS.md and appear in the ROADMAP. No orphans. The REQUIREMENTS.md checkboxes and traceability table still read "Pending" and need updating by the orchestrator.

## Behavioral and Delivery Checks

| Check | Result |
|---|---|
| `python scripts/build_..._notice_2_0_3.py --validate` (run by me) | PASS |
| Notice tests (orchestrator) | 89 passed, 0 skipped |
| 2.0.2 notice and reply tests (orchestrator) | 242 passed |
| CI | The `--validate` line is in `ems-validate.yml`. Run 44160179245 succeeded. HEAD matches origin. |
| Notice committed in e10b240 | The three generated files (notice markdown, registry JSON, schema) are committed. |
| Debt markers (TBD, FIXME, XXX) in the builder | None |
| D-14 human approval of the rendered notice | Recorded as given by Oscar Mack. |

## Review Warnings Assessment

- **WR-01** (pinned publisher ROOT points at the live repo): This is a convention-level weakness. It does not defeat SC3, because the mutations execute from blobs fetched at the pin and rejections are recorded. Not a blocker.
- **WR-02** (outcome table row 2 wording "Step 2 or step 3 ... at 87a46d1"): The wording is imprecise, because step 3 runs on the branch tip and not at 87a46d1. The meaning is still recoverable, since the row says "or any later commit". This is a clarity defect and does not affect SC2. A fix is advisable at the next regeneration.
- **WR-03** (CI installs unpinned jsonschema, the notice says 4.26.0): Hayes is told to use the pinned version. CI is a separate gate. No success criterion is affected. Not a blocker.

## Anti-Patterns

None blocking.

## Human Verification

None outstanding. D-14 approval was already given.

## Gaps Summary

No gaps. The phase goal is achieved. The only follow-up is bookkeeping: tick NOTICE-03, PIN-03 and CLAIM-01 to CLAIM-03 in REQUIREMENTS.md. The WR-02 wording can be tidied later.

_Verifier: Claude (gsd-verifier)_
