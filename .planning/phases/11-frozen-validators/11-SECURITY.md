---
phase: 11
slug: frozen-validators
status: verified
threats_open: 0
asvs_level: 1
created: 2026-11-16
---

# Phase 11 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| git history → frozen builders | The reply and 2.0.2 notice builders read pinned blobs with `git show` at fixed commits | Committed registry, schema and publisher bytes (integrity-critical, public) |
| git subprocess output → history checks | `--is-shallow-repository`, `cat-file -e` and `merge-base` output decide whether the history is complete | Short status strings (integrity-critical) |
| environment → test harness | `EMS_FAIL_ON_SKIP` and `EMS_ALLOW_NO_HISTORY` control the gating | Booleans set by the operator or CI |
| CLI → working tree | The frozen builders' CLI surface could otherwise rewrite frozen files | Frozen reply and notice bytes |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-11-01 | Tampering | reply `git_show` command injection | mitigate | `git_show` (reply builder L69-75) is a list-form subprocess with no shell, enforces a 40-hex SHA, and applies `bad_rel` (L68: rejects absolute paths, drive prefixes, a leading `\` and `..`). All callers go through it. | closed |
| T-11-02 | Tampering | exec of git-sourced code (reply) | mitigate | The builder has no exec, eval or loader calls. The AST ban is `FORBIDDEN_CALLS` with `test_builder_has_no_publisher_reference` (reply test L705-747), plus a test that the scanner itself works. | closed |
| T-11-03 | Repudiation | frozen literals drifting from the 31addfa publisher | mitigate | Literal-vs-blob equality tests against the publisher at 31addfa (reply test L559-701) cover 20 constants and the functions. | closed |
| T-11-04 | Spoofing | shallow clone accepted as history (reply) | mitigate | `resolve_record_commit` (L341-353) requires the output to be exactly `'false'`, checks `cat-file -e` with the full SHA in the error, and checks ancestry. Tests are at reply test L361-396. | closed |
| T-11-05 | Tampering | CLI overwriting frozen reply files | mitigate | Only `--validate` remains (L356-364). For each removed flag, a test checks exit code 2, that the 5 frozen paths are byte-identical, and that the removed attributes are gone (reply test L536-556). | closed |
| T-11-06 | Tampering | notice `git_show` injection | mitigate | `bad_rel` and `git_show` are identical to the reply's (notice builder L77-85). There are behaviour tests for both. | closed |
| T-11-07 | Tampering | runtime exec of git code (notice) | mitigate | No exec or loaders in the builder. The same AST ban applies. | closed |
| T-11-08 | Repudiation | literal drift from ae15c74 | mitigate | Equality tests at ae15c74 (notice test L486-655). They include the `validate_signoff` exception class and text across 4 sets of arguments. | closed |
| T-11-09 | Spoofing | shallow clone (notice) | mitigate | The cat-file and ancestor loop covers all four anchors, including the schema commit, plus a publication-before-record check (notice builder L150-164). Tests are at L219-278. | closed |
| T-11-10 | Tampering | CLI rewriting the frozen notice | mitigate | Only `--validate` remains (L376-384). Tests check exit code 2, unchanged bytes and that the removed attributes are gone (notice test L463-483). | closed |
| T-11-11 | Spoofing | shallow clone passing as green | mitigate | `require_history` fails by default (`aa_history.py` L70-76). CI keeps `fetch-depth: 0` and sets `EMS_FAIL_ON_SKIP=1`, and never sets the opt-out. | closed |
| T-11-12 | Repudiation | opt-out used silently in CI | mitigate | `test_missing_history_with_opt_out_and_guard_fails` (skip-guard L136-140): with both env vars set, the run ends red. | closed |
| T-11-13 | Tampering | git command injection in the test helper | mitigate | `_git` is list-form with no shell (`aa_history.py` L50-51). Note: "SHAs from constants" is only partly true, because some callers pass `publication_commit` read from a committed registry file (11-REVIEW IN-05). Without a shell, a bad value cannot inject a command and fails closed. | closed |
| T-11-14 | Denial of service | conftest hook affecting unrelated tests | accept | See AR-01. | closed |
| T-11-15 | Repudiation | a deleted guard hidden by a broad error | mitigate | No `REJECTS` tuple remains. Every negative test names a specific class and `match=`, and the guards are called directly. | closed |
| T-11-16 | Tampering | committed notice files drifting | mitigate | `test_committed_notice_files_validate` (notice test L83-90) has no monkeypatching. The reply equivalent is `test_real_reply_files_validate`. | closed |
| T-11-17 | Tampering | wrong `match=` strings | mitigate | All 22 `match=` strings occur in the builders' error text, and 261 tests pass against the unmodified validators. | closed |
| T-11-05-01 | Tampering | collection-level skip bypasses the guard | mitigate | `pytest_make_collect_report` hookwrapper (conftest L24-32), with two failing-under-guard cases and two controls (skip-guard L93-118). | closed |
| T-11-05-02 | Spoofing | unrecognised git output read as a full clone | mitigate | `history_problem` requires exactly `'false'` (`aa_history.py` L62), with a parametrised test and a positive control (skip-guard L168-183). | closed |
| T-11-05-03 | Elevation of privilege | reach of the `EMS_ALLOW_NO_HISTORY` opt-out (WR-02) | accept | See AR-02. | closed |
| T-11-05-04 | Tampering | an imperative xfail hides a skip | accept | See AR-03. | closed |
| T-11-05-SC | Tampering | package installs (11-05) | accept | See AR-04. | closed |
| T-11-06-01 | Repudiation | inaccurate evidence record in 11-04-SUMMARY | mitigate | Both statements are corrected ("called via build_reply, after the pinned reads in load_inputs", L105 and L175). The false wording no longer appears. | closed |
| T-11-06-SC | Tampering | package installs (11-06) | accept | See AR-04. | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01 | T-11-14 | The hook does nothing unless `EMS_FAIL_ON_SKIP=1`, and only the CI archive-assessment step sets that. Caveat (11-REVIEW WR-05): in that step, a module-level skip in any `tests/` module, even one deselected by `-k`, stops the whole run. This fails closed and nothing triggers it today. It is fixed in Phase 12 D-10 (`.planning/phases/12-verify-at-pin-and-gate-hardening/12-CONTEXT.md`). | Plan-time disposition (11-03-PLAN), approved by Oscar Mack (EMS governance authority) | 2026-11-16 |
| AR-02 | T-11-05-03 | This is the fail-closed D-08 convenience for offline local runs. With the guard on, a skip from the opt-out still fails, and CI never sets the opt-out. Note (11-REVIEW IN-08): the HINT text overstates how far the opt-out reaches. The wording fix is in Phase 12 D-11. | Plan-time disposition (11-05-PLAN), approved by Oscar Mack | 2026-11-16 |
| AR-03 | T-11-05-04 | An imperative `pytest.xfail()` cannot be told apart from a marker xfail (both set `wasxfail`). The exemption is tested (`test_guard_leaves_xfail_alone`), and no xfail is used in the suite outside the skip-guard fixtures. | Plan-time disposition (11-05-PLAN), approved by Oscar Mack | 2026-11-16 |
| AR-04 | T-11-05-SC, T-11-06-SC | No packages were installed. `requirements*.txt` has not changed since the baseline `6c69f22`. | Plan-time disposition (11-05/11-06-PLAN), approved by Oscar Mack | 2026-11-16 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-11-16 | 24 | 24 | 0 | gsd-security-auditor (code evidence; `EMS_FAIL_ON_SKIP=1` pytest over the reply, notice and skip-guard tests: 261 passed, exit 0) |

Informational, not blockers: 11-REVIEW IN-01 (the reply has no publication-before-record ancestry check) and the WR-03 ordering (the reply runs `resolve_record_commit` after the pinned reads) are still open as review items. Neither is new attack surface. Both are deferred until after 2.0.3, per `12-CONTEXT.md`.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-11-16
