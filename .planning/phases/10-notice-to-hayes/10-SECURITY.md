---
phase: 10
slug: notice-to-hayes
status: verified
threats_open: 0
asvs_level: 1
created: 2026-11-12
---

# Phase 10 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| git history to builder | Frozen bytes read via `git_show`; history may be shallow or missing | Authority, record, sign-off, decisions, manifest, schema (public governance data) |
| builder to Hayes | The generated notice is the only thing Hayes trusts for the re-pin target | Pin (commit, id, version, sha256 values) |
| builder output to repository | Generated files are committed artifacts that Hayes reads | Notice Markdown, JSON, schema |
| local repo to remote | Pushed commits become what Hayes can pin and read | Branch `feature/ems-aa3-archive-applicability-authority` |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-10-01 | Tampering | Cited id, version and commit in the notice | mitigate | Byte-rebuild `validate_notice` (three "differs from a fresh build" checks) and schema `const` values for publication commit, id and version (builder line 277). Tests `test_validate_rejects_tampered_cited_value`, `..._tampered_notice_bytes` and `..._tampered_constant` pass (48/48). | closed |
| T-10-02 | Spoofing | `publication_commit` constant against the record | mitigate | `load_inputs` raises unless `record['publication_commit'] == NOTICE_PUBLICATION_COMMIT` (builder lines 106-107). The record is read at `NOTICE_RECORD_COMMIT` only. | closed |
| T-10-03 | Repudiation/Integrity | Drift in live code or the working tree changing the notice | mitigate | All inputs are read via `pinned_json`/`pinned_digest`/`pinned_raw_digest` through `V2.git_show` at fixed SHAs. The test sets `V2.VERSION` to 9.9.9 and `AUTHORITY_ID` to 9.9.9 (test lines 225-226). Residual: the builder imports helper logic from the live v2 publisher (review WR-02); see Accepted Risks. | closed |
| T-10-04 | Denial/Integrity | Shallow clone skipping checks | mitigate | `resolve_record_commit` checks `--is-shallow-repository`, `cat-file -e` and `merge-base --is-ancestor` for all three SHAs, and checks that publication is an ancestor of record (builder lines 70-80). The non-skipping `fake_shallow_git` tests pass. | closed |
| T-10-05 | Information disclosure | Absolute paths or CI ids in the notice | mitigate | `V2.contains_absolute` check (builder line 288) and `test_absolute_path_is_rejected`. A grep for CI run ids or `actions/runs` in the notice MD and JSON returns 0 matches. | closed |
| T-10-06 | Tampering | Hand edits to generated files | mitigate | Byte-rebuild `--validate` runs locally (PASS) and in CI (run 43350106147, archive-assessment job). | closed |
| T-10-07 | Tampering | Unrelated work swept into a commit | mitigate | Explicit-path staging. 47343a1 holds only the builder and tests. `.planning/config.json`, `registry/adjudication_rules.json` and `registry/policy_decisions.json` remain modified and unstaged. | closed |
| T-10-08 | Repudiation | Unreviewed wording published | mitigate | Blocking D-12 checkpoint: Oscar Mack approved the rendered notice on 2026-11-12, before the notice commit 052f0f1. | closed |
| T-10-09 | Tampering | Unrelated modified files pushed | mitigate | 052f0f1 contains exactly the three notice files and 49c7b08 contains exactly `ems-validate.yml`. `git status` confirms the unrelated files are uncommitted. | closed |
| T-10-10 | Tampering | Drift in the authority or the reply | mitigate | `git diff ae15c74 HEAD` is empty on the publication paths, and the record equals its a71257e content. The reply doc, JSON and schema are unchanged since e781f08. The reply builder changed only in Phase 9 commits 82cff90 and 6e47a4f. | closed |
| T-10-11 | Repudiation | Notice sent before it is on the remote | mitigate | The notice carries `send_condition` (builder line 203, rendered under "Sending"). The push completed (HEAD = origin = 49c7b08) and CI passed before any sending. | closed |
| T-10-12 | Elevation | Unapproved push, PR or tag | mitigate | Blocking D-13 checkpoint: Oscar Mack approved the push. `gh pr list --head` is empty and `git tag --points-at HEAD` is empty. | closed |
| T-10-SC | Tampering | Package installs | accept | No new packages were added. | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-10-01 | T-10-SC | No dependencies were added in this phase, so the package supply-chain surface is unchanged. | Plan-time disposition (10-01/02/03 PLAN) | 2026-11-12 |

Advisory note (not an open threat): code review 10-REVIEW.md, WR-01 to WR-05, records that the builder renders some facts it does not itself enforce, and that it uses helper logic from the live v2 publisher. The orchestrator checked the rendered facts against the frozen bytes at ae15c74: 29/29 mutations are `REJECTED_FAIL_CLOSED`, and the three AA1/AA2 files contain CRLF, so the 2.0.1 scope error is real. The published notice is accurate. Hardening is available via `/gsd-code-review 10 --fix`.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-11-12 | 13 | 13 | 0 | gsd-secure-phase orchestrator (plan-time register, evidence from code, tests, git and CI) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-11-12
