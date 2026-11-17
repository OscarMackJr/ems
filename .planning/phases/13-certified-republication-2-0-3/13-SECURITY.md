---
phase: 13
slug: certified-republication-2-0-3
status: verified
threats_open: 0
asvs_level: 1
created: 2026-11-17
---

# Phase 13 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> The register was authored at plan time in the `<threat_model>` blocks of 13-01..13-04-PLAN.md. No SUMMARY raised a Threat Flags entry. Evidence is cited from 13-0x-SUMMARY.md and 13-VERIFICATION.md.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| approver to repository | Oscar Mack's approval becomes signed registry data | sign-off record (governance decision, integrity-critical) |
| drafting agent to authority | the agent prepares the proposal; only the human decides | proposed sign-off JSON, dry-run text |
| operator environment to git | ambient GIT_* / GIT_CONFIG_* variables could change what git returns | process environment |
| generator to commit | generated, hash-certified files cross into git | authority, schema, 7 generated outputs (integrity-critical) |
| working tree to commit | about 60 unrelated modified or untracked files sit beside the publication files | unrelated operator work (must stay out) |
| publisher to record | the record self-references PUB and is checked by plain --validate | publication record (SHA + digests) |
| test code to gate | a weak test could pass while the gate is red (WR-03) | test assertions |
| local repo to origin | push of 85 commits including the 2.0.3 publication | repository history (public to collaborators) |
| gh token to git process | the credential passes through process environment variables (fallback only) | GitHub token (secret) |
| CI to evidence / EMS to Hayes | the claim of green must match the exact pushed SHA; Hayes pins PUB | CI run metadata, pinned commit |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-13-01 | Spoofing/Repudiation | sign-off gate bypass or forged approval | mitigate | Blocking checkpoint. The record was written only after the verbatim signal `approve, date 2026-11-17`. `--validate-signoff` PASS (13-01 Task 3), and again before and after `--publish` (13-02) | closed |
| T-13-02 | Repudiation | dual role left implicit | mitigate | A `python -I` comparison shows dual_role_statement byte-equal to the publisher DUAL_ROLE_STATEMENT (dual_equal True, 13-01); the verifier re-confirmed it | closed |
| T-13-03 | Tampering | stale or mismatched digest in the sign-off | mitigate | The second dry run after the write printed the same Authority LF sha256 696116e7…; a re-confirm dry run before `--publish` matched as well; no script or input edit was made after the dry run | closed |
| T-13-04 | Tampering | wrong or reused sign-off date | mitigate | Mechanical check: ParseExact OK, and `($d -ge '2026-11-17') -and ($d -le '2026-11-17') -and ($d -ne '2026-11-12')` was True (13-01) | closed |
| T-13-05 | Tampering | ambient GIT_* environment during validation | mitigate | The pre-flight found GIT_EDITOR, GIT_ASKPASS and GIT_TERMINAL_PROMPT, all set by the harness. They were removed in-process (count 0) before every validator, dry run and sign-off call. The pre-flight pytest ran with them set; its result equalled the expected D-16 set. These variables control prompts only, not repository, index or object reads. Disclosed as a deviation in 13-01-SUMMARY | closed |
| T-13-06 | Tampering | commit scope contamination | mitigate | Explicit `git add --` (3 paths) and `git add -f --` (7 paths). The cached list had exactly 10 entries. The diff-tree of PUB equals sorted publication_paths(). No protected or untracked path is in any phase commit (13-02, verifier) | closed |
| T-13-07 | Tampering | stale schema or sign-off digest in the manifest | mitigate | `--emit-schema` ran before `--publish`. test_committed_schema_equals_schema_function is green at PUB. The verifier recomputed all 9 manifest entries with 0 mismatches | closed |
| T-13-08 | Tampering | hand edits to hashed files | mitigate | Only the publisher wrote the authority, outputs and schema. At-pin PASS checks the HEAD blobs and the hardened status over the 11 paths and the output folder | closed |
| T-13-09 | Spoofing | pinned commit not reproducible for Hayes | mitigate | Fresh `--no-local`, non-shallow clone detached at PUB with the system core.autocrlf=true; `--validate --at-pin` PASS (13-02 Task 2) | closed |
| T-13-10 | Tampering | decision drift | mitigate | Independent recompute: decisions LF sha 4e746d1f…, 0 of 80 rows differ against ae15c74, counts 3/18/59 (13-02 Task 3); the verifier re-confirmed | closed |
| T-13-11 | Tampering | ambient GIT_* during at-pin | mitigate | `Env:GIT_*` count was 0 before both at-pin runs (13-02 Task 2) | closed |
| T-13-12 | Tampering | wrong or short SHA in the record | mitigate | `--record-publication` was given the full 40-hex PUB from `git rev-parse HEAD`. Record publication_commit == PUB. Plain `--validate` PASS at REC | closed |
| T-13-13 | Tampering | record or WR-03 commit scope contamination | mitigate | Single explicit-path staging. The diff-tree of REC is the record only, and of WR03 the test file only (13-03) | closed |
| T-13-14 | Tampering | publication bytes drift after PUB | mitigate | `git diff --quiet` exits 0 for PUB..REC and PUB..WR03 over the 10 paths, and for REC..WR03 over the record | closed |
| T-13-15 | Repudiation | red result hidden by an unstable-moment suite run | mitigate | The suite ran only at committed states (pre-flight, PUB, REC, WR03) with EMS_FAIL_ON_SKIP=1 and a fresh basetemp each time. No suite ran between the sign-off write and publish, or between the record write and its commit | closed |
| T-13-16 | Tampering | D-10 test passes while --validate is red | mitigate | `assert before == (0, 'PASS')` landed in 5498002. The single test and the full suite pass at WR03. A forward note is in 13-REVIEW WR-01 (the assertion is expected red at a future publication commit) | closed |
| T-13-17 | Elevation/Repudiation | push without authority consent | mitigate | Blocking checkpoint. The push ran only after the verbatim `push approved`. The remote tip at signal time was 49c7b08. No PR, merge or tag (13-04) | closed |
| T-13-18 | Information disclosure | token exposure during the fallback push | mitigate | The plain push succeeded, so the fallback and token were never used. The secret grep (`x-access-token:…`, `gh[pousr]_…`) over .planning is clean | closed |
| T-13-19 | Repudiation | unverifiable CI claim | mitigate | `gh run view 44134035073`: success, headSha == WR03 == `git ls-remote` tip, both jobs success. Ancestry and byte identity are recorded in 13-VERIFICATION.md | closed |
| T-13-20 | Tampering | ambient GIT_CONFIG_* left in the session | mitigate | No GIT_CONFIG_* was ever set (plain push). `Env:GIT_*` count was 0 after the push | closed |
| T-13-21 | Tampering | evidence written into hashed registry files | mitigate | Evidence is only in 13-VERIFICATION.md and STATE.md. The evidence commit 144934b lists only those two paths. `git diff --name-only WR03 HEAD -- . ':(exclude).planning'` is empty | closed |
| T-13-SC | Tampering | package installs | accept | No package installs happened in this phase (see the Accepted Risks Log) | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-13-SC | T-13-SC | No dependency was installed or upgraded in Phase 13. The existing `.venv` was used unchanged, so there was no supply-chain exposure to mitigate | plan-time disposition (13-01..13-04 PLAN threat models) | 2026-11-17 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-11-17 | 22 | 22 | 0 | gsd-secure-phase orchestrator (State B, plan-time register; short-circuit, no auditor spawn) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-11-17
