---
phase: 13-certified-republication-2-0-3
plan: 01
subsystem: archive-assessment v2 publisher
tags: [sign-off, D-05, D-06, PUB-10, PUB-11]
requirements: [PUB-10, PUB-11]
requirements-completed: [PUB-10, PUB-11]
key-files:
  created: []
  modified:
    - registry/archive_assessment_applicability_authority_v2_signoff.json (written, validated, left uncommitted for 13-02)
metrics:
  completed: 2026-11-17
---

# Phase 13 Plan 01: Pre-flight, dry run and 2.0.3 sign-off Summary

The tree was publish-ready and the baseline red set was exactly the D-16 set. `--publish --dry-run` ran read-only: the whole-tree status was byte-identical before and after, and the hardened status was empty. It printed Authority LF sha256 `696116e765111c6f15237d876a9aca27f830c756707ee9c4b5e251d03aa0e0a6`. Oscar Mack approved at the blocking checkpoint with the date 2026-11-17. The sign-off record is written in the 2.0.2 wording and passes `--validate-signoff`. A second dry run printed the same digest. Nothing was published or committed apart from this summary.

## Task 1: Pre-flight and baseline red set
- Branch: feature/ems-aa3-archive-applicability-authority. `git merge-base --is-ancestor 509371d HEAD` exits 0.
- Index is empty. `git diff --name-only HEAD` over scripts, tests, schemas and the publication paths is empty, and the hardened `git status --porcelain --untracked-files=all --ignored=matching` over the pinned paths, the publisher, the OUT folder and the record is empty.
- Pytest (`EMS_FAIL_ON_SKIP=1`, all `tests/test_archive_assessment_*.py`, fresh basetemp in the session scratchpad): **3 failed, 1020 passed, 0 skipped, 0 errors, exit 1** (593 s). The failures are exactly D-16:
  - tests/test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function
  - tests/test_archive_assessment_applicability_authority_v2_publication.py::test_real_published_files_validate
  - tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest
- CI validators:
  - V1 `--validate`: exit 1, `AuthorityError: authority identity/version/status invalid; source_lineage supersedes does not name the 2.0.2 publication` (expected red)
  - V2 governance decisions `--validate`: exit 0, PASS
  - V3 rule proposals `--validate`: exit 0, PASS
  - V4 rule proposals `--validate-record`: exit 0, PASS
  - V5 reply `--validate`: exit 0, PASS
  - V6 notice 2.0.2 `--validate`: exit 0, PASS
- The whole-tree `git status --porcelain` was identical before and after the check run.

## Task 2: Dry run
- DRY_RUN_DATE (local) = **2026-11-17** (UTC was also 2026-11-17). Dry run exited 0.
- First line: `Publication sign-off summary for EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3`
- Decided controls: 21 (3 RULE_PUBLISHED, 18 NO_RULE_WILL_BE_PUBLISHED). Undecided controls: 59.
- Rules: EMS-CTRL-030 `production = KNOWN_FALSE`; EMS-CTRL-039 `production = KNOWN_FALSE`; EMS-CTRL-052 `ai_enabled = KNOWN_FALSE` (all ALL_CONDITIONS_MUST_MATCH).
- **Authority LF sha256: 696116e765111c6f15237d876a9aca27f830c756707ee9c4b5e251d03aa0e0a6** (CRLF_TO_LF). This matches the value research saw.
- "Version 2.0.3 supersedes EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2 version 2.0.2 (commit ae15c74). No decision changed: the governance decisions LF sha256 4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f equals the 2.0.2 value."
- What changed in 2.0.3 (used as printed, per D-05):
  - 7 derived lineage lines;
  - negative mutations: 29;
  - 16 schema levels with additionalProperties false;
  - "row comparison 2.0.2 -> 2.0.3: 80 controls identical to 2.0.2";
  - the Gates GATE-01 to GATE-10 line.
- Read-only proof: the whole-tree status was byte-identical before and after, and the hardened status was empty before and after.

## Checkpoint: sign-off
- Presented: the full dry-run output (the long lists of undecided IDs and schema paths were collapsed in the chat view; the full capture was referenced) and the proposed sign-off JSON.
- Resume signal, verbatim: `approve, date 2026-11-17`
- Approved date: 2026-11-17. $dry = 2026-11-17. $today at receipt = 2026-11-17.
- Mechanical check: ParseExact succeeded, and `($d -ge $dry) -and ($d -le $today) -and ($d -ne '2026-11-12')` returned **True**.
- `git status --porcelain` at approval was identical to the Task 2 capture.

## Task 3: Sign-off record
- registry/archive_assessment_applicability_authority_v2_signoff.json now holds:
  - authority_id EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3, version 2.0.3;
  - authority_sha256 696116e7…e0a6, CRLF_TO_LF;
  - approval: Oscar Mack, EMS_GOVERNANCE_AUTHORITY, date 2026-11-17, the 2.0.3 scope sentence;
  - status PUBLICATION_SIGNOFF.
- Keys are exactly {approval, authority_id, authority_sha256, authority_sha256_normalisation, dual_role_statement, status, version} and {approver, date, role, scope}. The file uses LF with one trailing newline (`i/lf w/lf`).
- `--validate-signoff`: PASS, exit 0.
- A `python -I` comparison shows dual_role_statement byte-equal to the publisher DUAL_ROLE_STATEMENT.
- Second dry run: exit 0, with the same Authority LF sha256.
- `git status --porcelain` differs from the pre-plan state only by ` M registry/archive_assessment_applicability_authority_v2_signoff.json`. The index is empty.
- No emit-schema, publish or pytest was run after the write (Pitfall 7).
- Local and UTC dates are the same (2026-11-17).

## Deviations from Plan
- **Ambient GIT_* variables (pre-flight step 4).** `Get-ChildItem Env:GIT_*` listed `GIT_EDITOR=true`, `GIT_ASKPASS=` (empty) and `GIT_TERMINAL_PROMPT=0`. The Claude Code harness sets these. They control editor and credential prompts only, not repository location, index or object reads. The orchestrator did not stop; it removed them in-process (`Remove-Item Env:GIT_*`, then checked the count was 0) before every validator, dry run and `--validate-signoff` call, so T-13-05 is mitigated in substance. The baseline pytest run happened before the removal and ran with them set; its result equals the expected D-16 set. 13-02 and 13-03 must clear them the same way before `--publish` and the validators.

## Self-Check: PASSED
