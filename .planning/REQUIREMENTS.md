# Requirements: EMS Not-Applicable Rule Publication — v1.1.0 Authority 2.0.2 Lineage Correction

**Defined:** 2026-10-20
**Core Value:** For every one of the 21 requested controls, EMS publishes an explicit, machine-readable, authority-backed applicability decision that Hayes can cite — so that "EMS decided" is always distinguishable from "EMS has not decided yet".

## v1.1.0 Requirements

### Lineage

- [x] **LIN-01**: Each digest in `source_lineage` declares its own normalisation (`RAW_BYTES` or `CRLF_TO_LF`); no single global field contradicts any digest
- [x] **LIN-02**: Each lineage digest can be recomputed from a file at a cited repo path (and commit where relevant) using the normalisation it declares; a validator does this recomputation and fails on any mismatch
- [x] **LIN-03**: The AA1 manifest is committed at a repo-relative path, protected with `-text` the same way as the AA2 outputs, and its raw-byte SHA-256 equals `f0da8e2e45c306ccc42ae96f25a19922668f3eedecdb26006f13514e24ad9b4b`

### Gates

- [x] **GATE-01**: (06-REVIEW WR-02) The publication-record cross-check fails when the record is absent or names a different authority; the only exception is an explicitly named pre-publication mode
- [x] **GATE-02**: (06-REVIEW WR-04) The mutation gate counts a mutation as rejected only when the validator raises its domain error; any other exception fails the gate
- [x] **GATE-03**: (catalog decoupling) `--validate` checks the catalog against a frozen reference (the pinned digest or commit), so edits to the live `registry/control_catalog.yaml` don't turn it red
- [x] **GATE-04**: (06-REVIEW WR-05) The reply's record-commit lookup either works in a shallow clone or fails with an explicit message there; it never passes silently
- [x] **GATE-05**: (03-REVIEW WR-01) Cross-note uniqueness compares notes using `norm_templated`

### Schema

- [x] **SCHEMA-07**: The v2 schema sets `additionalProperties: false` at the top level, on control rows and on `not_applicable_semantics`; the negative-invariant file records extra fields as rejected by the schema itself

### Publication

- [x] **PUB-07**: `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2` is published with certification, manifest and traceability, and its lineage records that it supersedes 2.0.1 at `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb`
- [x] **PUB-08**: No decision changes: the decisions digest equals 2.0.0's (`4e746d1f…`), the counts stay at 21 decided and 59 undecided, and the per-control decision content is identical
- [x] **PUB-09**: The publication commit contains only this milestone's changes, and the CI `archive-assessment` job passes on it

### Notice to Hayes

- [ ] **NOTICE-01**: A generated, `--validate`-checked notice cites the 2.0.2 authority id, its version and its commit, and lists what changed: the lineage scope, the gates and the schema
- [ ] **NOTICE-02**: The notice names the 2.0.1 digest-scope error explicitly, states that no applicability decision changed, and asks Hayes to re-pin

## Future Requirements

- **V2-01**: Rule-or-no-rule decisions for some or all of the other 59 controls
- **V2-02**: Confirmation from a Hayes re-run that the 21 resolve at the pinned commit (Hayes-side)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Decisions for the other 59 controls | Deferred to V2-01; this milestone is corrective |
| Any change to an applicability decision | 2.0.2 is a lineage and gate correction; PUB-08 pins the decisions digest |
| 06-REVIEW WR-01 (publisher script digest not checked live) | By design (D-09) |
| 06-REVIEW WR-03 (frozen-catalog check passes without git history) | By design (D-03) |
| Hayes-side re-run and test updates | Belongs in the Hayes repository |
| Landing unrelated in-flight work in the tree | Unrelated; kept out of this milestone's commits |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| LIN-01 | Phase 7 | Complete |
| LIN-02 | Phase 7 | Complete |
| LIN-03 | Phase 7 | Complete |
| GATE-01 | Phase 8 | Complete |
| GATE-02 | Phase 8 | Complete |
| GATE-03 | Phase 8 | Complete |
| GATE-04 | Phase 8 | Complete |
| GATE-05 | Phase 8 | Complete |
| SCHEMA-07 | Phase 8 | Complete |
| PUB-07 | Phase 9 | Complete |
| PUB-08 | Phase 9 | Complete |
| PUB-09 | Phase 9 | Complete |
| NOTICE-01 | Phase 10 | Pending |
| NOTICE-02 | Phase 10 | Pending |

**Coverage:**
- v1.1.0 requirements: 14 total
- Mapped to phases: 14
- Unmapped: 0

---
*Requirements defined: 2026-10-20*
*Traceability updated: 2026-10-20 — roadmap v1.1.0 (Phases 7-10)*
