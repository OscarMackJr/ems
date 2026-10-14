---
phase: 05
slug: reply-to-hayes
status: verified
threats_open: 0
asvs_level: 1
created: 2026-10-14
---

# Phase 05 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| published files to generator | Read-only inputs (v2 authority, publication record, sign-off, decision records, manifest, traceability); a stale or altered input must fail closed | Authority values, digests, decision rationales |
| reply to Hayes | The reply content is what an external assessor will cite | Per-control decisions, rules, pin SHA, digests |
| test to git history | Tests read local git; a shallow clone gives incomplete history | Commit ancestry, file contents at the pinned SHA |
| working tree to commit | Unrelated modified and untracked files sit beside project files | File selection for phase commits |
| repo to Hayes | Reply is not usable until the pin is on the remote | Publication commit 54a7fd0 |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-05-01 | Tampering | reply values vs authority | mitigate | `build_reply` cross-checks each of 21 rows against latest decision record (state, authority id, rule) and raises `AuthorityError` (scripts/build_archive_assessment_demo3_w1_req_001_reply.py:47-63); `load_inputs`/`check_inputs_bound` bind manifest, sign-off, traceability and decision records to the published manifest (:201-219); `validate_reply` byte-compares JSON, Markdown and schema to a fresh build (:228-233). `--validate` run: PASS | closed |
| T-05-02 | Tampering | publisher script digest in manifest | mitigate | Script loads the publisher only via `importlib` (:13-15) and never writes publisher files; publisher `--validate` run: PASS; `test_publisher_still_valid_and_digest_matches_manifest` asserts publisher LF digest equals manifest entry (tests/...reply.py:248-253) — passed | closed |
| T-05-03 | Information disclosure | absolute paths in reply JSON | mitigate | `V2.contains_absolute(reply)` in `validate_reply_object` (:192-193), called from both `--build` (:281) and `--validate` (:234); `test_mutation_absolute_path` (tests:218) and `test_real_reply_files_validate` (tests:245) — passed; grep of reply JSON/MD for drive-letter or home paths: no matches | closed |
| T-05-04 | Repudiation | wrong pin SHA | mitigate | Pin SHA taken from `record['publication_commit']` (:72); publication SHA literal not typed in script; `test_publication_sha_is_ancestor_and_holds_authority` (tests:311-319) checks ancestry and authority digest at SHA — passed (not skipped) | closed |
| T-05-05 | Spoofing | accidental push or send | mitigate | Only git calls in script: `ls-remote`, `cat-file -e`, `merge-base --is-ancestor` (:251, :256, :260); no push/commit/add/fetch; `fake_git` in tests raises on any other git command (tests:266) — passed | closed |
| T-05-06 | Tampering | reply drift from authority | mitigate | `test_each_entry_matches_authority_and_decision_record` (tests:106) plus mutation tests (tests:147-218) that run through real `validate_reply()` via `assert_validate_rejects` (WR-01 fix ad46d43) — 32 passed | closed |
| T-05-07 | Repudiation | wrong pinned commit | mitigate | Ancestor and digest-at-SHA test (tests:311-319); record-commit test (tests:322-331) checks 0ce89f2 added the record and 54a7fd0 is its ancestor — both ran, passed | closed |
| T-05-08 | Tampering | CRLF changing digests | mitigate | .gitattributes lines 16-18 set `text eol=lf` for reply MD, JSON, schema; `git check-attr eol` prints `lf` for all three; `validate_reply` compares `V2.lf_bytes` (:228-232); `test_real_reply_files_validate` asserts no `\r` (tests:243-244); CR count in all three committed files: 0 | closed |
| T-05-09 | Denial of service | false green on shallow clone | accept | See Accepted Risks Log AR-05-01; skip is explicit via `git_ready()` (tests:296-305, :313-314, :324-325) | closed |
| T-05-10 | Tampering | unrelated files in commit | mitigate | `git show --stat`: 7623f73 (4 files: .gitattributes, reply schema, script, test), 5f2e36c (2 files: reply MD, JSON), ad46d43/3f3586e/a589550/feb8e19/d4b17b7/f8655d3/c3dad63 touch only reply script, test and reply MD. `git diff --name-only 986dbe5..HEAD` lists only .planning files and the six phase-5 files. registry/adjudication_rules.json, registry/policy_decisions.json, schemas/archive_assessment_governance_answers.schema.json remain ` M` (unstaged, uncommitted) | closed |
| T-05-11 | Spoofing | reply sent without authority | mitigate | No push/send code (see T-05-05); reply states "It stays unsigned in the repository until it is sent" (docs/DEMO3_W1_REQ_001_REPLY.md:9); send condition present (MD:170, JSON:291); `--push-check` returns non-zero unless pin is on remote (:245-271, WR-06 f8655d3) | closed |
| T-05-12 | Tampering | published files edited | mitigate | Publisher `--validate`: PASS; `git diff --name-only 986dbe5..HEAD` contains no v2 publisher, v2 schema, published registry or generated/archive-assessment/ems-aa3-v2 file | closed |
| T-05-13 | Information disclosure | secrets or local paths in reply | mitigate | `contains_absolute` enforced in `validate_reply_object` on `--validate` path (:234 -> :192); reply contains only repo-relative paths, SHAs and governance text (grep for local paths: no matches) | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-05-01 | T-05-09 | The two git-history tests (`test_publication_sha_is_ancestor_and_holds_authority`, `test_record_commit_added_the_publication_record`) skip with an explicit reason on a shallow clone, missing git or non-repository. A shallow CI checkout therefore reports skipped, not failed, for the pin-ancestry checks. Local operator runs use full history; in this audit both tests ran and passed (0 skipped). Residual: CI (ubuntu-latest, default shallow checkout) may not exercise these two checks. | Plan 05-02 threat model (disposition accept); EMS governance authority Oscar Mack | 2026-10-14 |

---

## Unregistered Flags

None. No SUMMARY.md `## Threat Flags` were raised in 05-01, 05-02 or 05-03.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-14 | 13 | 13 | 0 | gsd-security-auditor (Claude) |

Evidence runs on 2026-10-14 at HEAD 7bdbd6d:
- `python scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate`: PASS (exit 0)
- `python scripts/publish_archive_assessment_applicability_authority_v2.py --validate`: PASS (exit 0)
- `python -m pytest tests/test_archive_assessment_demo3_w1_req_001_reply.py -q -rs --basetemp=C:/temp/pytest-sec-tmp`: 32 passed, 0 skipped
- No push or fetch performed; push state of 54a7fd0 on the remote not re-checked by this audit (05-03-SUMMARY reports UNKNOWN; send condition remains in force).

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-14
