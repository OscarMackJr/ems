# Roadmap: EMS Not-Applicable Rule Publication (DEMO3-W1-REQ-001)

**Milestone:** v1.1.0 Authority 2.0.2 Lineage Correction
**Status:** Planning
**Phases:** 7-10 (continues from v1.0.0, which ended at Phase 6; archived in `.planning/milestones/v1.0.0-ROADMAP.md`)
**Granularity:** coarse

## Overview

`EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1` (commit `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb`) declares a single global `digest_normalisation: CRLF_TO_LF` in `source_lineage`, but three of its digests (`aa1_manifest_sha256`, `aa2_closure_sha256`, `aa2_approval_sha256`) are raw-byte, and the AA1 manifest those digests point at is not in the repository. This milestone corrects the lineage scope, commits the AA1 manifest, closes the audit gate debt carried from v1.0.0, tightens the v2 schema, and republishes the authority as 2.0.2 with no applicability decision changed. A generated notice then tells Hayes what changed and asks it to re-pin.

**Ordering guarantees (not negotiable):**

- All code and schema changes (lineage, gates, schema) land before the single republication phase. There is exactly one publication producing 2.0.2.
- The AA1 manifest commit (LIN-03) lands before lineage recomputation (LIN-02) is verified, because the validator recomputes from the committed file.
- The notice to Hayes is written after the 2.0.2 publication commit, because it cites that commit.
- No applicability decision changes. The decisions digest stays equal to 2.0.0's (`4e746d1f…`).

**Accepted red window:** Every edit to the publisher, schema generator or validators makes the real-file tests (hash certification of 2.0.1 outputs) fail until the 2.0.2 publication commit regenerates the certified outputs. This window opens at the first code edit in Phase 7 and closes at the Phase 9 publication commit. It is expected and documented; it is not a regression. Tests that do not depend on the certified real files must stay green throughout, and each red test must be listed in the plan that opens or widens the window.

**Staging:** The working tree holds unrelated modified files (`registry/adjudication_rules.json`, `registry/policy_decisions.json`, and others) and about 60 untracked files from other work. Every commit in this milestone stages by explicit path only; never `git add -A` or `git add .`.

**Sign-off:** The 2.0.2 publication requires sign-off by Oscar Mack as EMS governance authority (exact role, as enforced by `validate_signoff`). Nothing is published on drafting judgment alone.

**AA1 manifest source:** The AA1 manifest file is supplied by the user from the authority's own copy. Its path is asked for during Phase 7; it is not reconstructed or fetched by Claude.

## Phases

**Phase Numbering:**

- Integer phases (7, 8, 9, 10): Planned milestone work
- Decimal phases (7.1, 7.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 7: Lineage Source and Per-Digest Scope** - The AA1 manifest is committed and every `source_lineage` digest declares and is recomputed under its own normalisation
- [ ] **Phase 8: Gate and Schema Hardening** - The remaining audit gates fail closed, `--validate` uses a frozen catalog reference, and the v2 schema rejects extra fields
- [ ] **Phase 9: Certified Republication 2.0.2** - `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2` is signed off, published and certified in a clean commit with no decision changed, and CI is green on it
- [ ] **Phase 10: Notice to Hayes** - A generated, validated notice cites 2.0.2 and its commit, names the 2.0.1 digest-scope error, and asks Hayes to re-pin

## Phase Details

### Phase 7: Lineage Source and Per-Digest Scope

**Goal**: Every digest in the AA3 `source_lineage` says how it was computed and can be recomputed from a committed file, including the AA1 manifest, so that a reader can verify each lineage hash from the repository alone.
**Depends on**: Nothing (first phase of v1.1.0; builds on 2.0.1 at `31addfa`)
**Requirements**: LIN-01, LIN-02, LIN-03
**Success Criteria** (what must be TRUE):

  1. The AA1 manifest, supplied by the user, is committed at a repo-relative path in a commit of its own (explicit-path staging), `.gitattributes` marks it `-text` like the AA2 outputs, and its raw-byte SHA-256 read back from the checked-out file equals `f0da8e2e45c306ccc42ae96f25a19922668f3eedecdb26006f13514e24ad9b4b`.
  2. The lineage the publisher builds gives each digest its own normalisation (`RAW_BYTES` or `CRLF_TO_LF`) alongside a repo-relative path (and commit where relevant); no single global normalisation field remains that could contradict any digest.
  3. A validator recomputes every lineage digest from its cited path (at its cited commit where relevant) under the declared normalisation and passes on the correct inputs; changing one byte of a cited file, the declared normalisation, or the recorded digest makes it fail.
  4. `aa1_manifest_sha256`, `aa2_closure_sha256` and `aa2_approval_sha256` are declared `RAW_BYTES`, and the digests that really are LF-normalised are declared `CRLF_TO_LF`; pytest covers both kinds.

**Plans**: TBD
**Notes**:

- The AA1 manifest commit (LIN-03) is plain data and does not open the red window; land it first so LIN-02 can be verified against a committed file.
- The first publisher or validator edit in this phase opens the accepted red window (see Overview).
- Ask the user for the AA1 manifest path at the start of the phase.

### Phase 8: Gate and Schema Hardening

**Goal**: The gates that guard publication and the reply fail closed on every path the v1.0.0 audit found open, `--validate` no longer depends on the live shared catalog, and the v2 schema itself rejects unexpected fields.
**Depends on**: Phase 7
**Requirements**: GATE-01, GATE-02, GATE-03, GATE-04, GATE-05, SCHEMA-07
**Success Criteria** (what must be TRUE):

  1. The publication-record cross-check fails when the record is absent or names a different authority, and passes only for the matching record or in an explicitly named pre-publication mode (GATE-01); a mutation in the gate harness that raises anything other than the validator's domain error (`AuthorityError`) fails the gate instead of being counted as a rejection (GATE-02).
  2. Editing the live `registry/control_catalog.yaml` in a scratch copy does not change the result of `--validate`, which checks the catalog against a frozen reference (pinned digest or commit); tampering with the frozen reference itself makes `--validate` fail (GATE-03).
  3. In a shallow clone, the reply's record-commit lookup either finds the commit or fails with an explicit message; it never passes silently (GATE-04). Two cross-notes that differ only in templated values are detected as duplicates because uniqueness compares `norm_templated` forms (GATE-05).
  4. The generated v2 schema sets `additionalProperties: false` at the top level, on control rows and on `not_applicable_semantics`; an authority document with an extra field at any of those three levels fails schema validation, and the negative-invariant output records each as rejected by the schema itself (SCHEMA-07).
  5. Every new fail-closed path has a pytest that drives it to failure; tests that do not depend on the certified real files pass.

**Plans**: TBD
**Notes**:

- The schema file is generated by the publisher (`schema()`); SCHEMA-07 is a publisher change, not a hand edit of `schemas/archive_assessment_applicability_authority.schema.json`.
- GATE-04 and GATE-05 touch the reply script and the governance-decisions builder; changes there must be output-neutral (no change to the committed decisions or reply content).
- 06-REVIEW WR-01 and WR-03 stay as designed (D-09, D-03) and are not reopened here.

### Phase 9: Certified Republication 2.0.2

**Goal**: A new authority version `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2` is published at a commit Hayes can re-pin to, carrying the corrected lineage, gates and schema, with every applicability decision identical to 2.0.0 and 2.0.1.
**Depends on**: Phase 8
**Requirements**: PUB-07, PUB-08, PUB-09
**Success Criteria** (what must be TRUE):

  1. After a dry run and sign-off by Oscar Mack as EMS governance authority, the publisher writes 2.0.2 with certification, manifest and traceability; its lineage records that it supersedes 2.0.1 at `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb`; `--validate` prints `PASS` and the full archive-assessment pytest suite passes, closing the red window.
  2. The decisions digest in 2.0.2 equals 2.0.0's (`4e746d1f…`); the authority shows 21 decided (3 rules, 18 no-rule) and 59 `NOT_YET_DECIDED`; a per-control comparison with 2.0.1 shows identical decision content for all 80 controls.
  3. `git show --stat` on the publication commit lists only this milestone's files and none of the unrelated modified or untracked files; the publication commit SHA is recorded in a later commit.
  4. The CI `archive-assessment` job passes on the publication commit (run id recorded).

**Plans**: TBD
**Notes**:

- Human gate: publication does not happen without Oscar Mack's sign-off as EMS governance authority.
- Bash is broken on this machine and GSD subagents cannot run tests or validators; the orchestrator runs them via PowerShell. `git push` may need the GitHub CLI token workaround recorded in STATE.md.
- The CI job runs on PRs, pushes to main and `workflow_dispatch`; a branch push alone may need a manual dispatch to satisfy PUB-09.

### Phase 10: Notice to Hayes

**Goal**: Hayes receives a written, generated notice that tells it exactly which authority, version and commit to re-pin to, what changed between 2.0.1 and 2.0.2, and that no applicability decision changed.
**Depends on**: Phase 9
**Requirements**: NOTICE-01, NOTICE-02
**Success Criteria** (what must be TRUE):

  1. A notice generated by a script from the published authority cites `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2`, version `2.0.2` and the full Phase 9 publication commit SHA, and the script's `--validate` run passes; changing the cited id, version or commit in the notice makes `--validate` fail.
  2. The notice lists what changed: per-digest lineage scope and the committed AA1 manifest, the gate fixes (WR-02, WR-04, catalog decoupling, WR-05, `norm_templated` uniqueness), and the stricter schema.
  3. The notice names the 2.0.1 error explicitly (global `CRLF_TO_LF` declared while `aa1_manifest_sha256`, `aa2_closure_sha256` and `aa2_approval_sha256` are raw-byte), states that no applicability decision changed (decisions digest unchanged, 21 decided and 59 undecided), and asks Hayes to re-pin.
  4. The notice is committed after the publication commit with explicit-path staging; sending it is left to the EMS authority.

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 7 → 8 → 9 → 10

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 7. Lineage Source and Per-Digest Scope | 0/TBD | Not started | - |
| 8. Gate and Schema Hardening | 0/TBD | Not started | - |
| 9. Certified Republication 2.0.2 | 0/TBD | Not started | - |
| 10. Notice to Hayes | 0/TBD | Not started | - |

## Coverage

| Category | Requirements | Phase |
|----------|--------------|-------|
| Lineage | LIN-01, LIN-02, LIN-03 | 7 |
| Gates and Schema | GATE-01, GATE-02, GATE-03, GATE-04, GATE-05, SCHEMA-07 | 8 |
| Publication | PUB-07, PUB-08, PUB-09 | 9 |
| Notice to Hayes | NOTICE-01, NOTICE-02 | 10 |

v1.1.0 requirements mapped: 14/14. No orphans, no duplicates.

## Notes for Planning

- **Hash certification.** The 2.0.1 manifest hashes the publisher, the generated schema and the authority. Any edit to these turns the real-file tests red until the 2.0.2 publication commit (accepted red window, see Overview).
- **The schema and authority files are generated.** Changes belong in `scripts/publish_archive_assessment_applicability_authority.py`, never in hand edits to `registry/archive_assessment_applicability_authority.json` or the schema.
- **Commit SHAs cannot be recorded in the commit they name.** The 2.0.2 publication SHA is recorded in a later commit, and the notice cites it from a commit after publication.
- **Working tree.** Stage by explicit path only; unrelated modified and untracked files stay out of every commit.
- **Environment.** Bash fails on this machine; tests and validators are run by the orchestrator via PowerShell.
- **No user-facing screens.** No phase carries a UI hint.

---
*Roadmap created: 2026-10-20 for milestone v1.1.0*
