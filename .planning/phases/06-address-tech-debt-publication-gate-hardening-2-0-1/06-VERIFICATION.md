---
phase: 06-address-tech-debt-publication-gate-hardening-2-0-1
verified: 2026-10-14T00:00:00Z
status: passed
score: 22/22 decisions verified (D-01..D-22)
overrides_applied: 0
gaps: []
---

# Phase 6 Verification

**Goal:** Harden the AA3 v2 publication gates, republish as 2.0.1 with fresh sign-off and a new publication commit, and regenerate the reply to cite 2.0.1.

## Independent evidence
- `pytest tests -k archive_assessment`: 492 passed, 0 failed (run by verifier).
- `--validate` for the v2 publisher, the governance-decisions builder and the proposals validator: PASS, PASS, PASS.
- Frozen inputs (decisions, answers, proposals, drafting record, v1 authority, control_catalog.yaml): `git diff 54a7fd0 HEAD` is empty, so no decision input changed (D-12 and phase boundary).
- 2.0.0 binding: `supersedes` in the committed authority records commit 54a7fd09..., authority sha256 de36e227..., and decisions sha256 4e746d1f.... The 2.0.0 authority digest equals both `sha256(git show 54a7fd0:...)` and the 0ce89f2 publication record. `v1_baseline` is a separate field (D-08).
- Authority diff in 31addfa touches only `authority_id`, `version` and lineage (D-06, D-13).
- Sign-off: role `EMS_GOVERNANCE_AUTHORITY`, approver Oscar Mack, date 2026-10-14, exact dual-role statement, scope text bound to the authority digest 7be5eb88... (D-21, D-10).
- Publication record: publication_commit 31addfa..., authority and manifest digests present (D-21). `PUBLISHED_ON` is no longer a constant (D-10).
- Publisher contains `SIGNOFF_ROLE`, `Mutation` list with ids, descriptions and gates, `mutation_gates`, a manifest `publisher_script` digest, and `v1_baseline`/`supersedes` handling (D-01, D-09, D-17..D-20). A new negative-invariant validation output has 177 lines of recorded results.
- CLAUDE.md and `.planning/PROJECT.md` Vocabulary lines both say "first four of the eight" (D-04).
- Commit order: 06-01 (docs), 06-02, 06-03, 06-04 (fixes), 730f51e (publisher code), 31addfa (publication), 4d9b7c1 (record), 7debe4a/fe9d50d (reply). This matches D-21 ordering.
- Hygiene: the unrelated `adjudication_rules.json`, `policy_decisions.json` and `archive_assessment_governance_answers.schema.json` changes remain unstaged and out of the phase commits (D-22). The push has not happened, per D-16 (ls-remote returned nothing).
- The reply cites 2.0.1, the record commit and 31addfa, and has the history note and a send_condition naming 31addfa on the remote branch (D-14..D-16).

## Decision coverage
D-01..D-22 are all accounted for in the evidence above and in the 492 passing tests. D-02 (only IN-01 and IN-07 fixed), D-05 (reply IN-01..06 fixed in 7debe4a) and D-11 (builder refusal, 06-03) are covered by the tests. D-03 is covered by 1da27db and the proposals validator PASS.

## Deviations evaluated
1. **Red-test window (06-04, grown to 18 tests at 06-05):** accepted by the user and recorded in 06-05-PLAN.md. It contradicts the CONTEXT "never red between commits" wording (Claude's Discretion). It is a process deviation only. The final state is green and the amendment is documented. Not a gap.
2. **Publication commit has 8 files (decision_traceability byte-identical):** D-21 and D-22 require only publication files, so this is consistent. The two tests adjusted in 06-08 pass and still assert the intended behaviour. Not a gap.
3. **06-09 run inline, with Oscar Mack's sign-off and read-through:** the human gate was satisfied by the approver himself. The push is intentionally left to the user (D-16). Not a gap.
4. **06-REVIEW.md (5 warnings, 4 info):** none contradicts a must-have.
   - WR-01 (script digest not checked live) is the explicit D-09 design.
   - WR-03 (the frozen-catalog skip on a shallow clone) is the D-03 "skip cleanly" requirement.
   - The rest are advisory hardening (mutation catch breadth, shallow-clone handling in the reply, dead FAIL branches).

## Warnings (non-blocking, advisory)
- Review WR-02 (publication-record check skipped when the record is absent or its id differs) and WR-04 (broad exception catch in `mutation_gates`) are real residual weaknesses beyond D-01 and D-02 scope. They are candidates for a follow-up phase.

## Remaining human step (not a gap)
Oscar Mack pushes the branch and sends the reply. Verify with `git ls-remote origin feature/ems-aa3-archive-applicability-authority` that it contains 31addfa.

**Result:** Phase goal achieved. Status: passed.
