---
phase: 16
slug: test-robustness-and-review-closure
status: verified
threats_open: 0
asvs_level: 1
created: 2026-11-18
register_authored_at_plan_time: true
---

# Phase 16 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| working tree -> commit | Unrelated uncommitted work must not enter phase commits | `.planning/` files, `registry/` edits from 2026-10-19 (unrelated) |
| test clone (tmp_path) -> real repo | Clone-based tests overlay publication paths into a temp clone | publication artifacts (public governance data) |
| pinned git history -> builder | The 2.0.3 notice builder reads git-pinned inputs | authority / record / manifest JSON |
| local repo -> remote | Pushing the branch is outward-facing | phase commits only |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-16-01 | Tampering | overlay commit in clone | mitigate | `overlay()` in `tests/test_archive_assessment_lineage_validation.py` uses per-command `-c user.name/-c user.email/-c commit.gpgsign=false` and makes no config writes and no push. The clone is under `tmp_path`, and only `publication_paths()` plus the publisher are copied | closed |
| T-16-02 | Information disclosure | unrelated working-tree files leaking into clone | mitigate | `overlay()` copies an explicit `rels` list with `--literal-pathspecs add -f -- *rels`. `-f` (b47a93f) only overrides gitignore for those explicit tracked publication paths | closed |
| T-16-03 | Repudiation | skipped guard hiding a missing history | mitigate | `pytest.fail`/assert only. With `EMS_FAIL_ON_SKIP=1`: local 1133 passed, 0 skipped; CI run 44408700761: 1133 passed, 0 skipped | closed |
| T-16-04 | Tampering | lineage commit in pinned authority | mitigate | `EXPECTED_LINEAGE_COMMIT` cross-check raises `AuthorityError` (e7d60ff), with commit-mismatch tests | closed |
| T-16-05 | Tampering | partial/stale outputs after failed --build | mitigate | Validation runs in memory first. Outputs are written to `.tmp` files and moved into place with `os.replace` (e7d60ff). If a replace or the post-check `validate_notice()` fails, the originals are restored (08f7301, review WR-02). Tests monkeypatch `os.replace` and check for no `.tmp` leftovers and byte-identical originals | closed |
| T-16-06 | Denial of service / integrity | malformed pinned input escaping as raw exceptions | mitigate | `load_inputs`/`build_notice` wrap ValueError, KeyError, TypeError and AttributeError (added in 08f7301, review WR-01) as `AuthorityError`, with wrong-type input tests | closed |
| T-16-07 | Tampering | accidental change of the sent notice text | mitigate | D-02 gate: after `--build`, `git diff --ignore-cr-at-eol --exit-code` exits 0 on the three 2.0.3 outputs. Checked after 16-02 and again after 08f7301 | closed |
| T-16-08 | Repudiation | closure dispositions without evidence | mitigate | The 16-03 plan's scripted ledger check passed (all 17 ids, no placeholders, every FIXED row has a hash). The cited hashes were confirmed with `git cat-file` | closed |
| T-16-09 | Tampering | unrelated working-tree changes entering commits | mitigate | Every phase commit was staged by explicit path and checked with `git diff --cached --name-only`. `git diff --name-only 9a10810..HEAD` contains no `registry/`, `schemas/`, `generated/` or sign-off path | closed |
| T-16-10 | Repudiation | wrong requirement attribution | mitigate | The insertion script compared each SUMMARY value with its PLAN's `requirements:` list and found no mismatches (850f0da) | closed |
| T-16-11 | Information disclosure | pushing unrelated working-tree work | mitigate | The scope check passed before the push, and the human checkpoint was approved before the first push. Only committed history is pushed; uncommitted `registry/` and `.planning/config.json` edits stay local | closed |
| T-16-12 | Tampering | frozen publisher/builders modified | mitigate | Frozen-file `git diff --ignore-cr-at-eol --exit-code` exits 0 for both 9a10810..HEAD and the working tree, and again after 08f7301 | closed |
| T-16-SC | Tampering | package installs | accept | No packages installed in this phase | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-16-01 | T-16-SC | No dependency was added or upgraded in phase 16 | plan-time disposition | 2026-11-18 |
| AR-16-02 | T-16-05 (residual) | `--build` rollback across three files is best-effort. A process crash between `os.replace` calls can leave a mixed set. A rerun of `--build`/`--validate` detects and repairs this, and the sent outputs are also pinned in git | review WR-02 fix note | 2026-11-18 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-11-18 | 13 | 13 | 0 | orchestrator (gsd-secure-phase, plan-time register, evidence from execution gates) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-11-18
