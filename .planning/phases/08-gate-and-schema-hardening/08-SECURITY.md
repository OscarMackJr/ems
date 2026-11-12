---
phase: 08
slug: gate-and-schema-hardening
status: verified
threats_open: 0
asvs_level: 1
created: 2026-11-12
---

# Phase 08 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Committed registry files → publisher/validators | Authority, sign-off, publication record and governance answers/decisions are read from the working tree and must fail closed when malformed or tampered | Controlled governance JSON (integrity-sensitive) |
| git history → publisher/reply builder | Pinned blobs (catalog at `62a8955`, 2.0.0 authority, publication commit) read via `git show`; commit strings come from constants or the publication record | Blob bytes, commit SHAs (integrity-sensitive) |
| Repository clone state → reply builder | Shallow clones can graft history and make a commit lookup lie | Commit identity |

---

## Threat Register

P = `scripts/publish_archive_assessment_applicability_authority_v2.py`, G = `scripts/build_archive_assessment_governance_decisions.py`, R = `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`.

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-08-01 | Tampering | grandfather exemption | mitigate | `CERTIFIED_ANSWERS_SHA256` exact match (G:64, G:153, G:321); digest computed from file read in both production callers (G:372, G:411); tests flip bytes and constant | closed |
| T-08-02 | Spoofing | caller passes certified digest with synthetic answers | accept | See AR-01 | closed |
| T-08-03 | Repudiation | copy-paste notes passing review | mitigate | `norm_templated` uniqueness for non-certified files in `strict_checks` and `validate_decisions` (G:72, G:153/164, G:321/326) | closed |
| T-08-04 | Tampering | record commit lookup in shallow clone | mitigate | `--is-shallow-repository` must return exactly `false`, else AuthorityError before `git log` (R:264-268) | closed |
| T-08-05 | Information disclosure | error text | accept | See AR-02 | closed |
| T-08-06 | Tampering | extra fields in authority | mitigate | `additionalProperties: false` at top level, rows, semantics (P:393, P:400, P:387); 3 schema-must-reject mutations (P:491-493) | closed |
| T-08-07 | Tampering | mutation gate counting non-domain errors as rejection | mitigate | Narrow excepts; `GitHistoryError` re-raised (P:610-630); propagation tests for AUTHORITY, SIGNOFF, DECISIONS | closed |
| T-08-08 | Denial of service | closed schema rejecting real authority | mitigate | All used properties declared (P:395-405, 16 top-level); built document validates in tests | closed |
| T-08-09 | Tampering | live catalog edit flips or masks the gate | mitigate | `catalog_bytes()` reads only via `git_show(CATALOG_COMMIT, …)` (P:93); live edit/delete tests | closed |
| T-08-10 | Tampering | catalog_reference forged | mitigate | digest/commit/path checked (P:323-325); in `COMMIT_PINNED` (P:336); schema consts (P:382) | closed |
| T-08-11 | DoS / silent bypass | shallow clone or missing history | mitigate | `GitHistoryError` on OSError or non-zero exit, no skip (P:342-343) | closed |
| T-08-12 | Elevation of privilege | git option injection via commit string | mitigate | 40-hex fullmatch and `bad_rel` before argv-list `subprocess.run` (P:339-341) | closed |
| T-08-13 | Tampering | absent or other-authority record passes | mitigate | Record required (P:714); exact identity per mode (P:718-723) | closed |
| T-08-14 | Spoofing | record commit not containing the bytes | mitigate | git_show digest equality for authority and manifest (P:727-728) | closed |
| T-08-15 | Elevation of privilege | option injection through publication_commit | mitigate | Shape check (P:716-717) then git_show regex/bad_rel; `write_publication_record` 40-hex check (P:731) | closed |
| T-08-16 | Denial of service | KeyError on malformed record | mitigate | Exact `RECORD_KEYS` set check raises AuthorityError (P:711, P:716) | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01 | T-08-02 | `validate_answers`/`strict_checks` trust a caller-supplied digest, but both production callers compute it from the file they read (G:372, G:411) and G:259 rejects a decisions `answers_sha256` that differs from the live answers file. Only tests pass synthetic digests. | Plan-time disposition (08-01-PLAN threat model) | 2026-11-12 |
| AR-02 | T-08-05 | Error messages use repo-relative names (P:339-343, R:266-268). P:343 passes git stderr through, which reports `commit:relpath` form — repo-relative in practice. | Plan-time disposition (08-02-PLAN threat model) | 2026-11-12 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-11-12 | 16 | 16 | 0 | gsd-security-auditor (verify mode, plan-time register); post-review-fix code (5107eb6) |

Note: T-08-08 plan text says "14 properties"; code declares 16 top-level properties (superset, test checks subset) — wording mismatch, not a gap.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-11-12
