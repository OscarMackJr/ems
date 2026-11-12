---
phase: 09-certified-republication-2-0-2
status: passed
verified: 2026-11-12
requirements: [PUB-07, PUB-08, PUB-09]
publication_commit: ae15c7458e49c8f55cc58c61bab04bc716aa9892
record_commit: a71257ed267410138a3c4daba412b00c116663d8
ci_run_id: 43332405316
ci_head_sha: a71257ed267410138a3c4daba412b00c116663d8
---

# Phase 9 Verification — Certified republication 2.0.2

## Key identifiers

| Item | Value |
|------|-------|
| Publication commit (Hayes pins) | ae15c7458e49c8f55cc58c61bab04bc716aa9892 |
| Record commit | a71257ed267410138a3c4daba412b00c116663d8 |
| Authority | EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2 |
| Authority LF sha256 | a44eea1f98ec361ab100c554eb3a8d3529cfeb1fec78ec6d38193a675f0b8beb |
| Manifest sha256 | 9991228ab7ff0a0c52c61b77a4d4c0e58b56d68b0c382caa83496621f092bac2 |
| Governance decisions LF sha256 | 4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f (unchanged from 2.0.0/2.0.1) |
| Supersedes | 2.0.1 @ 31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb |
| Sign-off | Oscar Mack, EMS_GOVERNANCE_AUTHORITY, 2026-11-12, dual-role statement included |
| CI run | 43332405316 (workflow_dispatch), conclusion success; jobs validate ✓, archive-assessment ✓ |
| CI headSha | a71257ed267410138a3c4daba412b00c116663d8 (= pushed branch HEAD = record commit) |

## Red window accounting

See 09-BASELINE-RED.md.
- **Baseline:** 3 accepted reds; `-k archive_assessment` gave 694 passed, 3 failed.
- **Plans 01-04:** the same 3 reds throughout, with no new ids once the plan-01 fixture fix landed.
- **At the record commit:** `-k archive_assessment` gives **720 passed, 0 failed, 0 skipped**. All three baseline reds are green, and the D-04 byte-identity test runs instead of skipping.

## Local validators at the record commit (all PASS, exit 0)

- `publish_archive_assessment_applicability_authority_v2.py --validate`
- `build_archive_assessment_governance_decisions.py --validate`
- `validate_archive_assessment_rule_proposals.py --validate`
- `validate_archive_assessment_rule_proposals.py --validate-record`
- `build_archive_assessment_demo3_w1_req_001_reply.py --validate`

At the publication commit, `--validate --pre-publication` and the reply `--validate` passed. Plain `--validate` is red there by design (D-04).

## Byte identity and scope (D-04, PUB-09)

- `git diff --quiet ae15c74 a71257e --` over the 10 publication paths exits **0**. Those paths are the schema, authority, sign-off, and the 7 files under generated/archive-assessment/ems-aa3-v2/.
- `git diff --name-only ae15c74 a71257e -- . ':(exclude).planning'` lists only `registry/archive_assessment_applicability_authority_v2_publication_record.json`. The one commit in between, 06eb7aa, touches only .planning/.
- `git show --stat ae15c74`: exactly the 10 publication paths.
- `git show --stat a71257e`: exactly the record file.
- Neither commit includes `registry/adjudication_rules.json`, `registry/policy_decisions.json`, `.planning/config.json` or any untracked file.
- `git diff --name-only ae15c74~1 ae15c74 -- scripts tests` is empty: no code changed in the publication commit.
- Reply artifacts (`docs/DEMO3_W1_REQ_001_REPLY.md`, `registry/archive_assessment_demo3_w1_req_001_reply.json`, `schemas/archive_assessment_demo3_w1_req_001_reply.schema.json`): `git diff --stat e781f08 HEAD` is empty (D-01).
- CI: `git merge-base --is-ancestor a71257e <headSha>` exits 0, because headSha is the record commit itself. So the record-to-headSha byte check holds trivially.

## Requirement evidence

- **PUB-07** (republish 2.0.2 with no decision change): 21 controls decided. 3 have a rule: CTRL-030 production=KNOWN_FALSE, CTRL-039 production=KNOWN_FALSE, CTRL-052 ai_enabled=KNOWN_FALSE. 18 are NO_RULE_WILL_BE_PUBLISHED, and 59 are NOT_YET_DECIDED. The decisions digest is unchanged. Plain validate and CI are green at the record commit.
- **PUB-08** (lineage and comparison with 2.0.1): SUPERSEDED_V2_0_1 is bound to 31addfa, 7be5eb88… and 4e746d1f…, and a git-history test checks the values. validate_publication compares all 80 rows on four decision fields, plus the control set and the top-level decision ids, against `git_show(31addfa)`; the result is "80 controls identical to 2.0.1". Tamper tests and a GitHistoryError fail-closed test pass.
- **PUB-09** (clean, pinned publication commit): the scope checks are above. The branch was pushed only after Oscar Mack approved ("Push approved"). The remote ref is at a71257e. No PR, merge or tag was created: `gh pr list --head` is empty and no tag points at HEAD.

## ROADMAP SC4: reading under D-04

Hayes pins the publication commit ae15c74. At that commit the record still names 2.0.1, so plain `--validate` and CI are red there by design. The green `archive-assessment` run, 43332405316, ran on the record commit a71257e. Every publication file is byte-identical between the two commits, so the green run certifies exactly the bytes Hayes pins. No gate was weakened, and no pre-publication CI mode was added.

## Secrets

The push used the normal credential helper; the token workaround was not needed. No token was written to any file.
