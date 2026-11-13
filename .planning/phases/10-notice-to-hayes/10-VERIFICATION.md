---
phase: 10-notice-to-hayes
verified: 2026-11-12T00:00:00Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
---

# Phase 10: Notice to Hayes Verification Report

**Phase Goal:** Hayes receives a written, generated notice that tells it which authority, version and commit to re-pin to, what changed between 2.0.1 and 2.0.2, and that no applicability decision changed.
**Status:** passed. **Re-verification:** No.

| # | Success criterion | Status | Evidence |
|---|---|---|---|
| 1 | Generated notice cites id, version, full publication SHA; `--validate` passes and fails on tampering | VERIFIED | Notice cites `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2`, `2.0.2` and `ae15c7458e49c8f55cc58c61bab04bc716aa9892`. That commit exists as "feat(09-04): publish ... 2.0.2". Its v2 authority JSON carries that id and version. `--validate` printed PASS in my own run. Tests cover tampered cited values, tampered constants, tampered notice bytes and a loosened schema. The orchestrator reports 48 passed. I did not run pytest. |
| 2 | Lists lineage scope and AA1 manifest, gate fixes (WR-02, WR-04, catalog decoupling, WR-05, norm_templated), and stricter schema | VERIFIED | "What changed" section lists the per-digest lineage entries with the AA1 manifest as RAW_BYTES. It names WR-02, WR-04, catalog decoupling, WR-05 and the norm_templated uniqueness check. It also states the schema closes 16 levels with additionalProperties false. |
| 3 | Names 2.0.1 error, states no decision changed, asks Hayes to re-pin | VERIFIED | The notice has a dedicated section naming the global CRLF_TO_LF scope and the three raw-byte digests (aa1_manifest_sha256, aa2_closure_sha256, aa2_approval_sha256). "No decision changed" states 21 decided (3 rules, 18 no-rule), 59 undecided, 0 of 80 rows differ, and the same decisions digest. "What to do" asks Hayes to re-pin. |
| 4 | Committed after publication with explicit-path staging; sending left to the authority | VERIFIED | Commit 052f0f1 comes after ae15c74 and contains exactly 3 files (notice md, json, schema). The notice says "Do not send ... until on remote". The orchestrator reports it is pushed, with CI green at 49c7b08 and the `--validate` step wired in `.github/workflows/ems-validate.yml` (line 97). No PR or tag exists. |

**Score:** 4/4

## Requirements Coverage

| Requirement | Status | Evidence |
|---|---|---|
| NOTICE-01 | SATISFIED | Criteria 1 and 2. The REQUIREMENTS.md checkbox and traceability table still show Pending, so the orchestrator should tick them. |
| NOTICE-02 | SATISFIED | Criterion 3. Same bookkeeping note. |

No orphaned requirements. REQUIREMENTS.md maps only NOTICE-01 and NOTICE-02 to Phase 10.

## Anti-Patterns

None blocking. The 10-REVIEW.md warnings (5) are advisory hardening. The builder does not itself enforce some facts it renders. The orchestrator checked those facts against frozen bytes at ae15c74 and they are true.

## Human Verification

None required. The "dual role" statement and the unsigned/unsent status are present in the notice.

## Gaps

None.

_Verifier: Claude (gsd-verifier)_
