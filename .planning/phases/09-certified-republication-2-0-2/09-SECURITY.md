---
phase: 09
slug: certified-republication-2-0-2
status: verified
threats_open: 0
asvs_level: 1
created: 2026-11-13
---

# Phase 09 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| git history to validator | 2.0.1 bytes are read via git_show; they are untrusted if the repo is shallow or tampered | authority, decisions, sign-off and record blobs (integrity-critical) |
| working tree to commit | dirty unrelated files sit next to deliberate changes | registry, schema and generated files (integrity-critical) |
| approver to repository | human authority approval becomes signed data | sign-off record (authority-critical) |
| generator to commit | generated hashed files are committed to git | 10 publication artifacts (hash-certified) |
| local repo to origin | the milestone branch is pushed | 81 commits |
| gh token to git process | a credential could pass through the environment | GitHub token (secret) |
| CI to evidence | a claim that CI is green must match the SHA | CI run id and headSha |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-09-01 | Tampering | SUPERSEDED_V2_0_1 digests | mitigate | Constant at publisher L36-45. `test_superseded_v2_0_1_constants_match_git_history` recomputes both digests from `git show 31addfa` and cross-checks them with the 4d9b7c1 record. | closed |
| T-09-02 | Tampering | decision drift 2.0.1 → 2.0.2 | mitigate | `rows_differing_from_previous` compares 80 rows on 4 fields, the id set and applicability_decision_ids. Digest binding to 4e746d1f. Tests: row tamper ×4, id-list tamper, decisions-digest tamper. | closed |
| T-09-03 | Spoofing | shallow clone false pass (publisher) | mitigate | `git_show` raises GitHistoryError and mutation_gates re-raises it. Tests show it propagating through validate_publication and mutation_gates. | closed |
| T-09-04 | Info disclosure / Tampering | commit scope (09-01) | mitigate | Explicit-path staging. The 09-01 commits touch only the publisher, the tests and .planning phase, STATE and ROADMAP files. | closed |
| T-09-05 | Elevation | parameterised validate_signoff | mitigate | Defaults stay bound to the live AUTHORITY_ID and VERSION. Only the reply builder passes explicit 2.0.1 values. Both forms tested. | closed |
| T-09-06 | Tampering | reply re-pointed to another commit | mitigate | Byte-equality rebuild from pinned 2.0.1 inputs. Review WR-01 found that a valid-but-wrong REPLY_PUBLICATION_COMMIT was accepted. Fixed in 6e47a4f: it must equal the frozen record's publication_commit. Tamper tests add 4d9b7c1 and b3c0411, and the auditor confirmed both are rejected. | closed |
| T-09-07 | Spoofing | shallow clone false pass (reply) | mitigate | `resolve_record_commit` fails closed on a shallow clone, rc≠0, unknown output or OSError. Shallow-clone and GitHistoryError tests. | closed |
| T-09-08 | Tampering | wrong anchor SHA | mitigate | `test_frozen_constants_match_git` checks the constants. Runtime runs `cat-file -e` and `merge-base --is-ancestor`. | closed |
| T-09-09 | Tampering | commit scope (09-02) | mitigate | 82cff90 and 02a4ea3 each touch one intended file. Reply artifacts show an empty diff 766062f..HEAD. | closed |
| T-09-10 | Repudiation / Spoofing | misleading sign-off summary | mitigate | Every figure in dry_run_summary is derived from the authority, git and code, and tests assert them. Residuals WR-03 (omission) and IN-01 (unreachable DIFFER text) produce no false statement. See notes. | closed |
| T-09-11 | Tampering | dry run writing files | mitigate | `publish(True)` returns before any write. A test asserts no output exists after a dry run. | closed |
| T-09-12 | Tampering | commit scope (09-03) | mitigate | 251cb30 touches only the publisher and the publication test. | closed |
| T-09-13 | Spoofing / Repudiation | sign-off gate bypass | mitigate | Blocking human checkpoint (approved 2026-11-12). validate_signoff pins the key set, approver, role, date, dual-role text and digest. The sign-off was first committed in ae15c74, after approval. | closed |
| T-09-14 | Tampering | stale or hand-edited hashes | mitigate | validate_published checks rebuild equality of every output. Scripts and tests are unchanged from 251cb30 to ae15c74, and the publisher is unchanged to HEAD. | closed |
| T-09-15 | Tampering | publication commit scope | mitigate | ae15c74 holds exactly 10 paths: schema, authority, sign-off and 7 generated. | closed |
| T-09-16 | Tampering | manifest script digest | mitigate | The live publisher LF sha equals the manifest `publisher_script.sha256` f6b51cca. Tests check it. | closed |
| T-09-17 | Tampering | decision drift (publication) | mitigate | validate_published → validate_publication runs the D-08 comparison and the 4e746d1f binding. | closed |
| T-09-18 | Info disclosure | token exposure during push | mitigate | The plain push worked and the token workaround was not used. No credentials in the remote URL, no extraheader in config, and a token grep over the phase diff found 0 hits. The CI secret-pattern grep is in place. | closed |
| T-09-19 | Elevation / Repudiation | push without consent | mitigate | The push followed an explicit "Push approved". No PR, merge or tag. | closed |
| T-09-20 | Tampering | integrity of pinned bytes | mitigate | check_publication_record re-hashes via git_show. Byte identity holds for ae15c74..a71257e, and ae15c74 is an ancestor of a71257e. | closed |
| T-09-21 | Repudiation | unverifiable CI claim | mitigate | CI run 43332405316: success, headSha a71257e (= the remote tip), both jobs green. Recorded in 09-VERIFICATION. | closed |
| T-09-22 | Tampering | record and planning commit scope | mitigate | a71257e holds only the record. Planning commits use explicit .planning paths, and .planning/config.json was never committed. | closed |
| T-09-SC | Tampering | package installs | accept | No package installs. requirements*.txt and .github are unchanged from 766062f to HEAD. | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-09-01 | T-09-SC | The phase installs no packages. The auditor confirmed requirements*.txt and .github are unchanged from 766062f to HEAD, so there is no supply-chain surface. | Plan-time disposition (09-01..05 threat models) | 2026-11-13 |

*Accepted risks do not resurface in future audit runs.*

### Non-blocking notes (not open threats)

- **WR-01 fix not yet in CI:** 6e47a4f is local and not pushed. CI run 43332405316 covers a71257e, before the fix. The fix does not touch certified bytes, because the reply builder and tests are not in the manifest.
- **WR-02:** the frozen reply validator still depends on live publisher constants and code. This is hardening, not a mitigation gap.
- **WR-03 and IN-01:** the dry-run summary leaves out AA1 committed/RAW_BYTES, the commit pins and the second supersedes normalisation. Its "No decision changed" lead-in is unconditional, but the DIFFER path cannot be reached. Carry the missing statements into the Phase 10 notice; a fix would require republication.
- **WR-04:** the PUB-08 tests skip when the 2.0.1 blob is unreachable, so in such a clone the test evidence fails open. The runtime fails closed, and the orchestrator run had 0 skips.
- **IN-05:** plain `--validate` does not check the publisher script digest; only pytest does.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-11-13 | 23 | 23 | 0 | gsd-security-auditor (read-only git/gh/`python -I`) + orchestrator PowerShell test evidence |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-11-13
