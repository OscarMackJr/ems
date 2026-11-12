---
phase: 09-certified-republication-2-0-2
plan: 04
subsystem: archive-assessment v2 publication
tags: [publication, sign-off, PUB-07, PUB-08, PUB-09]
requirements: [PUB-07, PUB-08, PUB-09]
publication_commit: ae15c7458e49c8f55cc58c61bab04bc716aa9892
key-files:
  modified:
    - schemas/archive_assessment_applicability_authority_v2.schema.json
    - registry/archive_assessment_applicability_authority_v2.json
    - registry/archive_assessment_applicability_authority_v2_signoff.json
    - generated/archive-assessment/ems-aa3-v2/ (7 publication files)
metrics:
  completed: 2026-11-12
---

# Phase 9 Plan 04: Publish authority 2.0.2 Summary

EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2 is published in publication commit **ae15c7458e49c8f55cc58c61bab04bc716aa9892**, the commit Hayes pins.
- **Decisions:** 21 controls decided. 3 have a published rule: CTRL-030 production=KNOWN_FALSE, CTRL-039 production=KNOWN_FALSE, CTRL-052 ai_enabled=KNOWN_FALSE. 18 are NO_RULE_WILL_BE_PUBLISHED. The other 59 are NOT_YET_DECIDED.
- **Authority LF sha256:** a44eea1f98ec361ab100c554eb3a8d3529cfeb1fec78ec6d38193a675f0b8beb. Manifest sha256: 9991228ab7ff0a0c52c61b77a4d4c0e58b56d68b0c382caa83496621f092bac2.
- **Supersedes:** 2.0.1 at 31addfa. The governance decisions digest 4e746d1f… is unchanged, and all 80 rows are identical to 2.0.1.

## Sign-off
Oscar Mack, EMS_GOVERNANCE_AUTHORITY, approved on 2026-11-12. He reviewed the full dry-run summary through a blocking checkpoint ("Approve, date 2026-11-12"). The sign-off carries the exact DUAL_ROLE_STATEMENT from the publisher and the dry-run digest. A second dry run just before publishing printed the same digest.

## Steps and checks
1. Preflight: publisher, reply script and tests committed, with no diff.
2. `--emit-schema` regenerated the schema; the dry run wrote nothing else.
3. Dry run and blocking sign-off.
4. Sign-off written; `--validate-signoff` PASS.
5. `--publish` PASS; `--validate-signoff` PASS again.
6. Commit with an explicit 10-path `git add`: `git diff --cached --name-only` showed exactly 10 paths and nothing else.
7. `git diff --name-only HEAD~1 HEAD -- scripts tests` is empty. The reply MD and JSON are unchanged.
8. `--validate --pre-publication` PASS. Reply `--validate` PASS.
9. Plain `--validate` is red at this commit by design (D-04): the record still names 2.0.1 until 09-05.

## Deviations from Plan
None. The orchestrator executed the plan inline, because it needs PowerShell and the blocking human sign-off.

## Self-Check: PASSED
