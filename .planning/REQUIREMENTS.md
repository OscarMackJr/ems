# Requirements: v1.2.0 Authority 2.0.3 Verification Hardening

**Defined:** 2026-11-12
**Core Value:** For every one of the 21 requested controls, EMS publishes an explicit, machine-readable, authority-backed applicability decision that Hayes can cite — so that "EMS decided" is always distinguishable from "EMS has not decided yet".

**Source:** v1.1.0 audit tech debt (`.planning/milestones/v1.1.0-MILESTONE-AUDIT.md`). Each requirement cites the review finding it closes.

## v1.2.0 Requirements

### Verify-at-pin

- [ ] **PIN-01**: Hayes can run a documented `--validate` command on a clean checkout of the 2.0.3 publication commit, with no later commit, and get PASS. The output names the one check it defers: binding the record to its commit.
- [ ] **PIN-02**: Plain `--validate` returns PASS at the record commit or any later commit. It verifies that the record names the publication commit and that the publication files are byte-identical between the two commits.
- [ ] **PIN-03**: The 2.0.3 notice tells Hayes the exact commands to verify at the pin and at the record commit, and what each result means. This closes the v1.1.0 gap where the notice gave no instructions for the pin (09 tech debt, PUB-09/NOTICE-01).

### Frozen validators

- [x] **FROZEN-01**: The DEMO3 reply validator, which is frozen on 2.0.1, uses no live publisher constants or functions. A publisher change does not change its result. (09-REVIEW WR-02)
- [x] **FROZEN-02**: The 2.0.2 notice validator uses no live publisher constants or functions: `PREV_COMPARED_KEYS`, `DUAL_ROLE_STATEMENT`, `validate_signoff` and `rule_text`. It still passes on the unchanged 2.0.2 notice files once the 2.0.3 publisher lands. (10-REVIEW WR-02)
- [x] **FROZEN-03**: If the 2.0.1 blob or any other pinned blob cannot be reached, tests and validators fail with an explicit error instead of skipping. (09-REVIEW WR-04)
- [x] **FROZEN-04**: Pytest validates the committed notice files. Each notice test fails when the check it is named for is broken. (10-REVIEW IN-01, WR-03)

### Notice claim enforcement

These apply to the notice builder and validator used for 2.0.3.

- [ ] **CLAIM-01**: The builder runs every negative mutation and records a domain rejection for each one. The validator fails if any mutation was not rejected. Today the builder only counts the mutations. (10-REVIEW WR-01)
- [ ] **CLAIM-02**: The validator recomputes all 7 lineage digests from git instead of echoing 4 of them. (10-REVIEW WR-04)
- [ ] **CLAIM-03**: Any "declared under the wrong scope" statement is computed: for each RAW_BYTES file, the validator shows that its raw hash differs from its LF hash. (10-REVIEW WR-05)

### Gate and validator hardening

- [ ] **GATE-06**: `--validate` checks the publisher-script digest against the certification. Today only pytest checks it. (09-REVIEW IN-05)
- [x] **GATE-07**: Malformed authority shapes raise `AuthorityError`, never a raw `TypeError`, `KeyError` or `AttributeError`. `validate_published` validates the schema before running its Python checks. (08-REVIEW WR-03)
- [x] **GATE-08**: The `--validate` path of `validate_decisions` enforces cross-note uniqueness under `norm_templated`. (08-REVIEW WR-05)
- [x] **GATE-09**: The D-10 test shows that a live catalog edit does not change the build or `--validate` result. The D-13 test uses real changed answer bytes instead of a fabricated digest. (08-REVIEW WR-06, WR-07)
- [x] **GATE-10**: Publisher and test cleanup (09-REVIEW IN-01..04, IN-06):
  - the dry-run's "no decision changed" text is conditional, and the DIFFER branch can be reached;
  - the check of the 2.0.0 constant against git history is restored;
  - the dead `log` handling is removed;
  - `resolve_record_commit` handles git errors the same way everywhere;
  - the D-08 tamper test covers rule rows and no-rule rows.

### Republication

- [ ] **PUB-10**: `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3` is published with certification, manifest and traceability.
  - Oscar Mack signs it off as EMS governance authority, with the dual-role statement.
  - It supersedes 2.0.2 at `ae15c74`.
- [ ] **PUB-11**: No decision changes. The decisions digest stays `4e746d1f…`, all 80 rows are identical to 2.0.2, and the counts stay at 21 decided and 59 undecided.
- [ ] **PUB-12**: The publication commit contains only this milestone's deliberate changes, and the CI `archive-assessment` job passes on it.

### Notice

- [ ] **NOTICE-03**: A generated notice, checked by `--validate`, cites the 2.0.3 id, version and commit. It lists what changed, states that no decision changed, includes the PIN-03 verification guidance, and asks Hayes to re-pin.

## Future Requirements

- **V2-01**: Rule-or-no-rule decisions for the other 59 controls
- **V2-02**: Hayes re-run confirmation (done on the Hayes side)

## Out of Scope

| Item | Reason |
|------|--------|
| Regenerating the 2.0.1 reply or the 2.0.2 notice | Both are historical documents that were already sent or generated. Only their validators change. |
| Sending the 2.0.3 notice | The authority sends it, out of band. |
| Bookkeeping debt (`requirements:` vs `requirements-completed:` in SUMMARY frontmatter) | Affects planning tooling only, not the authority. |
| Review items from the 01–07 reviews that the v1.1.0 audit does not list | Already closed or superseded. The scope is the v1.1.0 audit. |
| Any change to decision content | This milestone is verification hardening only. The decisions digest is pinned. |
| Landing unrelated in-flight work in the tree | Stays untouched and out of this milestone's commits. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PIN-01 | Phase 12 | Pending |
| PIN-02 | Phase 12 | Pending |
| PIN-03 | Phase 14 | Pending |
| FROZEN-01 | Phase 11 | Complete |
| FROZEN-02 | Phase 11 | Complete |
| FROZEN-03 | Phase 11 | Complete |
| FROZEN-04 | Phase 11 | Complete |
| CLAIM-01 | Phase 14 | Pending |
| CLAIM-02 | Phase 14 | Pending |
| CLAIM-03 | Phase 14 | Pending |
| GATE-06 | Phase 12 | Pending |
| GATE-07 | Phase 12 | Complete |
| GATE-08 | Phase 12 | Complete |
| GATE-09 | Phase 12 | Complete |
| GATE-10 | Phase 12 | Complete |
| PUB-10 | Phase 13 | Pending |
| PUB-11 | Phase 13 | Pending |
| PUB-12 | Phase 13 | Pending |
| NOTICE-03 | Phase 14 | Pending |

**Coverage:** 19 requirements, 19 mapped (Phase 11: 4, Phase 12: 7, Phase 13: 3, Phase 14: 5)

---
*Requirements defined: 2026-11-12*
