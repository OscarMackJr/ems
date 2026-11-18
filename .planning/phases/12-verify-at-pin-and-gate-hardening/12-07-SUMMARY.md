---
phase: 12-verify-at-pin-and-gate-hardening
plan: 07
subsystem: archive-assessment publisher (authority v2)
tags: [PIN-01, PIN-02, GATE-06, D-14, D-16, supersedes, 2.0.3, red-window]
requires: [12-06]
provides:
  - publisher in final 2.0.3 form (VERSION '2.0.3', SUPERSEDED_V2_0_2 bound to ae15c74)
  - version-agnostic superseded messages derived from the constant (09 D-07)
  - truthful dry-run gate line and manifest publisher_script_note (D-14)
  - test_superseded_v2_0_2_constants_match_git_history
affects:
  - Phase 13 (publish 2.0.3 with --publish, --validate --at-pin, --record-publication; re-emit the schema)
  - Phase 14 notice (PIN-03 quotes the dry-run gate line and manifest note)
tech-stack:
  added: []
  patterns: [constants derived from git by a printed command and asserted against git by a test]
key-files:
  created:
    - .planning/phases/12-verify-at-pin-and-gate-hardening/12-07-SUMMARY.md
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - tests/test_archive_assessment_lineage_validation.py
    - tests/test_archive_assessment_normalisation_claims.py
    - .planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md
decisions:
  - "[Phase 12] 12-07: SUPERSEDED_V2_0_1 replaced by SUPERSEDED_V2_0_2 (ae15c74, a44eea1f..., decisions 4e746d1f...); VERSION '2.0.3'; every superseded-version message derives from SUPERSEDED_V2_0_2['version']"
  - "[Phase 12] 12-07: the frozen 2.0.1 sign-off test reads the 2.0.1 identity from source_lineage.supersedes of the 2.0.2 authority at ae15c74 (superseded_2_0_1_identity()), not from a constant"
  - "[Phase 12] 12-07: end-of-phase accepted red set is 3 tests + CI validator 1; closed by the Phase 13 publication and record commits"
metrics:
  duration: ~35 min active (excluding suite wall time)
  completed: 2026-11-16
  tasks: 2
  files: 6
requirements-completed: [PIN-01, PIN-02, GATE-06]
---

# Phase 12 Plan 07: 2.0.3 supersedes 2.0.2, truthful texts Summary

The publisher is now in the final 2.0.3 form: `VERSION = '2.0.3'`, and a git-derived `SUPERSEDED_V2_0_2` binding (commit ae15c74, authority LF sha256 a44eea1f…, decisions 4e746d1f…) replaces `SUPERSEDED_V2_0_1` everywhere. The dry-run gate line and the manifest `publisher_script_note` now describe GATE-06 and `--at-pin` truthfully. The red set equals the D-16 accepted end state.

## What was done

**Task 1 (publisher, no separate commit):**

Derivation command output (from 12-07-PLAN `<verification_commands>`):

```
ae15c7458e49c8f55cc58c61bab04bc716aa9892 EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2 2.0.2 a44eea1f98ec361ab100c554eb3a8d3529cfeb1fec78ec6d38193a675f0b8beb 4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f
record ae15c7458e49c8f55cc58c61bab04bc716aa9892 a44eea1f98ec361ab100c554eb3a8d3529cfeb1fec78ec6d38193a675f0b8beb 2.0.2
```

All checks held: the commit is ae15c74…, id/version are 2.0.2, the authority sha equals the record's `authority_sha256`, the decisions sha is 4e746d1f…, and the record names the same commit.

- `SUPERSEDED_V2_0_2` has the same key set as before, with values pasted from the output above. `VERSION = '2.0.3'`, and `AUTHORITY_ID` still derives from it.
- Every use moved to `SUPERSEDED_V2_0_2`: the build lineage, the `validate_publication` supersedes check, the PUB-08 `git_show(SUPERSEDED_V2_0_2['commit'], ...)`, the governance-decisions digest checks, `validate_lineage`, `pinned(SUPERSEDED_V2_0_2, ...)` in `schema()`, and `sup` in `dry_run_summary`.
- Messages now derive the version from the constant:
  - `source_lineage supersedes does not name the {v} publication`
  - `{cid}: decision content differs from {v}`
  - `decision set differs from {v}`
  - `governance_decisions sha256 does not equal the {v} decisions digest`
  - `decisions file differs from the {v} decisions; {VERSION} may not change any decision`
  - `lineage must record the {v} publication it supersedes`
  - the mutation description for `supersedes_governance_digest_differs`
- Edits were made at byte level, so CRLF is preserved.

**Task 2 (commit 8a519ba):**
- The lineage_validation and normalisation_claims modules use `MODULE.SUPERSEDED_V2_0_2` (PINNED_COMMITS, the `fx` fixture, the D-10 test). Their failure messages derive the version from the constant.
- v2 test module: `'2.0.3'` in `test_version_and_authority_id_come_from_constants`, and `SUPERSEDED_V2_0_2` in `test_supersedes_and_v1_baseline_follow_constants`. `test_committed_schema_equals_schema_function` is unchanged and red by design.
- v2_publication test module:
  - Renamed `prev_201_*` to `prev_superseded_*`.
  - `match=re.escape(SUPERSEDED_V2_0_2['version'])`.
  - Renamed `test_built_rows_equal_superseded_rows_on_the_four_decision_fields`, `test_applicability_decision_ids_tamper_against_superseded_raises_authority_error` and `test_missing_superseded_history_raises_git_history_error_through_mutation_gates`.
  - `test_version_constants_and_published_on_removed` asserts 2.0.3.
  - New `test_superseded_v2_0_2_constants_match_git_history` checks against ae15c74 and record commit a71257e.
  - The 12-03 anchor/chain test now asserts that the 2.0.2 authority supersedes 31addfa with the LF sha of the 2.0.1 blob, and that `git rev-parse ae15c74` equals `SUPERSEDED_V2_0_2['commit']`.
  - The frozen 2.0.1 sign-off test uses `superseded_2_0_1_identity()`.
  - The dry-run test asserts the 2.0.3/2.0.2 texts and `GATE-01 to GATE-10`, and checks that `pre-publication` is absent.
  - The at-pin source check asserts `'SUPERSEDED_V2_0_' not in src`, the same intent without naming the removed constant.
- `git grep SUPERSEDED_V2_0_1 -- scripts tests` prints nothing.

## D-14 texts (flag for the Phase 14 notice, PIN-03)

- Dry-run gate line: `  Gates GATE-01 to GATE-10: publication-record check; --validate --at-pin at the publication commit with one deferred check (publication record binding); plain --validate at the record commit or later with ancestry and publication-file byte identity; publisher-script digest checked by --validate; schema-first domain-error-only validation; frozen catalog reference; fail-closed shallow-clone and git checks; norm_templated uniqueness.`
- Manifest `publisher_script_note`: `The publisher script digest is recorded at publication. --validate requires the live publisher script to match it, and plain --validate also requires the script at the publication commit to match it; validation rebuilds every output with the recorded value.`

## Verification

- Full archive suite (`--basetemp=.pytest-temp/p12-07-full`): **986 passed, 3 failed**, exit 1. Failing:
  - `v2::test_committed_schema_equals_schema_function`
  - `v2_publication::test_real_published_files_validate`
  - `v2_publication::test_publisher_still_valid_and_digest_matches_manifest`
- Four-module run: 454 passed, 3 failed (same ids), no collection errors.
- CI validator 1 FAIL: `AuthorityError: authority identity/version/status invalid; source_lineage supersedes does not name the 2.0.2 publication`. Validators 2-6 PASS.
- Acceptance greps: the forbidden-pattern count is 0. The `VERSION = '2.0.3'`, `SUPERSEDED_V2_0_2 = {`, ae15c74…, 4e746d1f… and `pinned(SUPERSEDED_V2_0_2` counts are each 1. py_compile is OK.
- `git diff HEAD~1 HEAD -- registry schemas docs generated` is empty, and the commit lists exactly the publisher and the four test modules.

## Deviations from Plan

- **CI validator 1 message changed.** It now fails earlier, on the identity/supersedes check, because the committed authority is still 2.0.2. Before, it failed on the GATE-06 script-digest message. It is still FAIL by design and closes at the Phase 13 publication. Recorded in the ledger.
- **Additional wording changes.** The source-inspection assertion `'SUPERSEDED_V2_0_1' not in src` became `'SUPERSEDED_V2_0_' not in src`, so the git grep acceptance holds. Some pytest.fail messages and comments that said "2.0.1" now derive from or name the superseded publication.

No other deviations. `--emit-schema`, `--publish` and `--record-publication` were not run.

## Self-Check: PASSED

- 8a519ba exists in git log; the ledger has the "## After plan 12-07" section and "Accepted red set at end of Phase 12".
