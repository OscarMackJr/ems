---
phase: 06-address-tech-debt-publication-gate-hardening-2-0-1
plan: 04
subsystem: archive-assessment v2 publisher
tags: [cr-01, wr-04, cr-02, in-01, in-07, wr-09, hardening]
requires: ["06-03"]
provides:
  - SIGNOFF_ROLE and exact sign-off validation
  - governance decisions gate on publish and --validate paths
  - publication record digest check and manifest path guard
key-files:
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - tests/test_archive_assessment_applicability_authority_v2.py
decisions:
  - "Decisions-builder path is anchored to the publisher module file (BUILDER_SCRIPT), not the patchable ROOT, so env-fixture tests that patch ROOT still load it"
metrics:
  tasks: 3
  files: 3
  completed: 2026-10-14
requirements: [D-01, D-02, D-22]
---

# Phase 6 Plan 04: Publisher Gate Hardening Summary

The v2 publisher now rejects a Hayes-role sign-off, runs the governance-decisions validator and schema before any build or `--validate`, and checks the publication record digests against the committed files.

## What changed

- CR-01 and WR-04: new `SIGNOFF_ROLE = 'EMS_GOVERNANCE_AUTHORITY'`; `validate_signoff` requires role equality, exact dual-role statement, exact key sets for record and approval, a real ISO date (`is_date`), and a non-empty string scope. `APPROVER_ROLES` unchanged.
- CR-02 and IN-01: cached lazy `decisions_builder()` and `validate_governance_decisions()`; builder `ValueError`, schema, `KeyError`, `TypeError` become the publisher's `AuthorityError`. Called first in `published_authority_checked` and `validate_published`, not in `validate_publication`. Tamper tests cover approver, empty dual-role statement, bogus disposition and a record missing `decided`.
- IN-07: when the record names the same authority id, `authority_sha256` and `manifest_sha256` must match the committed files; a record naming another id is treated as pending.
- Pitfall 9: manifest `relative_path` values that are absolute or contain `..` are rejected.
- WR-09: the generated-dir guard uses `inspect.getsource` on the two build functions.

## Deviations from Plan

**1. [Rule 3 - Blocking, plan assumption wrong] Two real-file tests are red on every commit of this plan.**
The manifest lists the live publisher script's LF digest in `artifacts`, so any edit to the publisher makes `--validate` on the committed 2.0.0 files fail ("manifest ... differs from a fresh build"). The plan's claim that the suite stays green after every commit cannot hold until D-09 (manifest `publisher_script` recorded digest) lands in plan 06-05. The failing tests are exactly `test_real_published_files_validate` and `test_publisher_still_valid_and_digest_matches_manifest`; the other 425 pass. The research (06-RESEARCH, overview and Pitfall 1) anticipated this window. I did not regenerate the 2.0.0 outputs, since that would alter published artifacts outside this plan.

**2. [Rule 1 - Bug] Loader path.** The first version of the lazy loader used `ROOT`, which the `env` fixture patches, so env tests failed when run in isolation (the cached loader hid it in the full run). Fixed in commit 3 with `BUILDER_SCRIPT` anchored on `__file__`.

**3. Traversal guard is defence in depth.** The manifest fresh-build comparison rejects an edited manifest first, so the new path check is not the first line that fires in `validate_published`; the traversal tests pass either way.

Residual risk (A4): someone who edits the publication record can rename its authority id and skip the IN-07 check. Covered by the git-gated tests and the reply pin.

## Known Stubs

None.

## Commits

- c4ccf03: fix(06-04): sign-off must be EMS_GOVERNANCE_AUTHORITY with exact checks (CR-01, WR-04)
- 9792bd3: fix(06-04): run the governance decisions validator before any build (CR-02, IN-01)
- 2adcb09: fix(06-04): check publication record digests in --validate; scope generated-dir guard (IN-07, WR-09)

## Self-Check: PASSED
