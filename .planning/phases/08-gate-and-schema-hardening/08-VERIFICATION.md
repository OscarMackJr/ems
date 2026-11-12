---
phase: 08-gate-and-schema-hardening
verified: 2026-11-12T00:00:00Z
status: passed
score: 5/5 roadmap success criteria verified
overrides_applied: 0
gaps: []
advisory:
  - id: CR-01
    classification: hardening, carry into Phase 9 first edit (not a Phase 8 requirement gap)
  - id: WR-01..WR-07
    classification: see table below
---

# Phase 8: Gate and Schema Hardening Verification Report

**Phase Goal:** Gates guarding publication and the reply fail closed on every path the v1.0.0 audit found open, `--validate` no longer depends on the live shared catalog, and the v2 schema rejects unexpected fields.
**Status:** passed (with advisory warnings)
**Re-verification:** No, initial verification

Test evidence is from the orchestrator (663 passed, 3 failed; the 3 failures are the documented accepted red set). I did not run pytest. I read the code and git history to confirm each claim.

## Observable Truths

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|---|---|---|
| 1 | GATE-01: record check fails on absent or other-authority record, passes only for the matching record or in `--pre-publication` mode. GATE-02: non-domain exceptions fail the gate. | VERIFIED | `check_publication_record` (publisher L691+), `--pre-publication` flag (L715-717), skip branch removed, `validate_published(pre_publication)` calls it at L686. `mutation_gates` (L591-607) catches only `AuthorityError` (AUTHORITY, SIGNOFF), `ValueError` (DECISIONS) and `jsonschema.ValidationError`. KeyError, TypeError and AttributeError propagate. Propagation tests exist (08-03). |
| 2 | GATE-03: live catalog edits do not change `--validate`; the frozen reference is pinned and tampering fails. | VERIFIED | `CATALOG_COMMIT` (L46), `catalog_bytes()` = `git_show(CATALOG_COMMIT, CATALOG_REL)` (L90), no live `CATALOG` constant, `catalog_reference` carries the commit (L172), lineage check on commit (L309), schema `commit` const (L367). Tests include D-10 and D-09 fail-closed cases. |
| 3 | GATE-04: shallow clone finds the commit or fails explicitly. GATE-05: uniqueness uses `norm_templated`. | VERIFIED | Reply builder L264 `rev-parse --is-shallow-repository`, fail closed. Decisions builder L153 uses `norm_templated` unless `answers_sha256 == CERTIFIED_ANSWERS_SHA256` (grandfathering the certified answers, output-neutral). New tests cover both. |
| 4 | SCHEMA-07: `additionalProperties:false` at the top level, on control rows and on `not_applicable_semantics`; negative invariants record SCHEMA rejection. | VERIFIED | Publisher L372 (semantics), L374 (top level), L381 (control rows). Three new mutations (26 to 29) with `schema_must_reject`, and tests assert the SCHEMA gate. The committed schema file is intentionally not regenerated (Phase 9). |
| 5 | Every new fail-closed path has a pytest; tests independent of the certified real files pass. | VERIFIED | 663 passed. The only 3 failures are the accepted red set (committed schema vs `schema()`, real published files, reply digest vs manifest). All three are expected until Phase 9 republication. |

**Score:** 5/5

## Requirements Coverage

| Req | Plan | Status | Evidence |
|---|---|---|---|
| GATE-01 | 08-05 | SATISFIED | See truth 1 |
| GATE-02 | 08-03 | SATISFIED | See truth 1 |
| GATE-03 | 08-04 | SATISFIED | See truth 2 |
| GATE-04 | 08-02 | SATISFIED | See truth 3 |
| GATE-05 | 08-01 | SATISFIED | See truth 3 |
| SCHEMA-07 | 08-03 | SATISFIED | See truth 4 |

All six IDs are claimed by plan frontmatter. There are no orphaned requirements.

**Bookkeeping defect (non-blocking):** `.planning/REQUIREMENTS.md` still shows GATE-02 and SCHEMA-07 as unchecked `[ ]`, with "Pending" in the traceability table. Both are implemented. The orchestrator should tick them and mark them Complete.

## Review Findings Classification

| Finding | Classification | Rationale |
|---|---|---|
| CR-01 (`digest_normalisation` value not validated in the publication record) | Not a Phase 8 goal gap. Recommended hardening before Phase 9. | GATE-01 and its SC require only presence and identity. But it is the same class of error the milestone corrects, and Hayes reads this record. Add the check in the first Phase 9 edit, or as a small Phase 8 follow-up. |
| WR-01 (anchor hard-wired to the 2.0.0 constant and messages) | Phase 9 | The constant must be updated to 2.0.1 when 2.0.2 is published. Add this to the Phase 9 checklist. |
| WR-02 (git environment failures counted as rejections in the narrowed gate) | Real but minor residual of GATE-02 | The domain-error narrowing is in place. `git_show` failures raise `AuthorityError`, so they can be miscounted. Harden with a distinct subclass. |
| WR-03 (validators crash on malformed shapes) | Out of scope | D-05 was probed for the 29 mutations. Broader shape hardening is not required by the Phase 8 SC. |
| WR-04 (open nested objects in the schema) | Out of scope | SC4 names exactly three levels, which are closed. Tightening further is a future improvement. |
| WR-05 (`norm_templated` uniqueness only in the build path, not in `validate_decisions`) | Out of scope | GATE-05 text is "cross-note uniqueness compares notes using `norm_templated`", satisfied at the builder. Optional follow-up. |
| WR-06, WR-07 (test-strength gaps for D-10 and D-13) | Warning | The behaviours are implemented; the tests could be stronger. |

## Anti-Patterns

I did not run a full marker scan. The review reports only formatting slips (IN-05). No stubs found in the inspected code.

## Process Notes

- Intermediate commits 9a66899 and 0f29b8f have a non-compiling test file. It is fixed in b47cbbb. The final state is correct.
- The orchestrator's fix 0d95274 corrected one 08-05 test.
- Protected committed registry, schema and generated files are unchanged (per orchestrator).

## Human Verification Required

None. The accepted red set resolves in Phase 9.

## Gaps Summary

No goal-blocking gaps. Carry forward to Phase 9: CR-01, WR-01 and WR-02. Tick GATE-02 and SCHEMA-07 in REQUIREMENTS.md.

_Verified: 2026-11-12_
_Verifier: Claude (gsd-verifier)_
