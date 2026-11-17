---
phase: 12-verify-at-pin-and-gate-hardening
plan: 06
subsystem: archive-assessment publisher (authority v2)
tags: [PIN-02, GATE-06, D-06, D-07, D-08, ancestry, blob-identity, script-digest, red-window]
requires: [12-05]
provides:
  - plain --validate D-06 check (not shallow, publication commit is an ancestor of HEAD, 10 D-05 blobs identical at pub and HEAD)
  - plain --validate at the pin points to --validate --at-pin
  - GATE-06 live publisher digest check in both modes and pinned publisher digest check in plain mode
affects:
  - CI validator 1 is red by design until the 2.0.3 publication (Phase 13)
  - 12-07 (red set grows by test_committed_schema_equals_schema_function)
tech-stack:
  added: []
  patterns: [compare raw git blobs at two resolved SHAs, never git_show('HEAD')]
key-files:
  created:
    - .planning/phases/12-verify-at-pin-and-gate-hardening/12-06-SUMMARY.md
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - .planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md
decisions:
  - "[Phase 12] 12-06: plain --validate runs git_not_shallow, git_is_ancestor(pub, git_head()) and a raw-blob identity loop over publication_paths() after the existing record cross-checks; the --at-pin pointer runs after the shape and normalisation checks and before the identity check"
  - "[Phase 12] 12-06: GATE-06 checks lf_digest(SCRIPT) against manifest publisher_script.sha256 in both modes; plain mode also checks the script blob at the publication commit; check_publication_record(a, at_pin, script_sha256) has no defaults"
metrics:
  duration: ~40 min active (excluding suite wall time)
  completed: 2026-11-16
  tasks: 2
  files: 3
---

# Phase 12 Plan 06: D-06 ancestry and blob identity, GATE-06 script digest Summary

Plain `--validate` now holds at the record commit or any later commit only if the publication commit is in HEAD's history and all 10 published files are byte-identical (raw git blobs) at the publication commit and at HEAD. It fails closed on a shallow clone. At the pin itself, it tells the operator to run `--validate --at-pin`. `--validate` in both modes also binds the live publisher script to the certified manifest digest, and plain mode binds the script at the publication commit as well. This turns CI validator 1 red by design until the 2.0.3 publication.

## What was done

**Task 1 (commit 0054f2c), PIN-02 / D-06:**
- `check_publication_record` reads `sup = a['source_lineage']['supersedes']` once. In plain mode, a record naming the superseded identity raises `publication record still names the superseded 2.0.1 publication, so HEAD is the publication commit, not the record commit; run --validate --at-pin here, or plain --validate at the record commit or later`. It runs after the `RECORD_KEYS` shape check and the `digest_normalisation` check, and before the `must name` check.
- After the existing git_show record cross-checks, plain mode runs `git_not_shallow()`, `head = git_head()`, `git_is_ancestor(pub, head)` (`publication commit <7> is not an ancestor of HEAD; ...`) and, for every `publication_paths()` entry, `git_show(pub, p) != git_show(head, p)` (`<path>: differs between the publication commit and HEAD`).
- Tests: `HEAD_COMMIT = 'b'*40`; env fakes `git_head` and `git_is_ancestor`; `REAL_GIT_HEAD` / `REAL_GIT_IS_ANCESTOR` captured at import; `register_blobs` registers every D-05 path plus the script at the record commit and at HEAD. New: `test_plain_validate_requires_ancestry`, `test_plain_validate_requires_blob_identity_at_head` (authority, schema, manifest), `test_plain_validate_shallow_fails_closed`, `test_plain_validate_at_pin_record_points_to_at_pin`, MALFORMED_FILES `record_is_a_list`, and `test_real_git_repo_plain_passes_after_record_and_later_commits_and_catches_head_drift` (C1 publish, C2 record, C3 unrelated: PASS; C4 changes the schema, `git checkout HEAD~1 -- schema` restores the working tree: fails with the drift message). `test_real_git_repo_record_passes_plain_mode` now uses the real git helpers. In `test_at_pin_mode_accepts_only_superseded_record`, the plain-mode match changed from `must name` to `--validate --at-pin`.

**Task 2 (commit c24f1d3), GATE-06 / D-07 / D-08:**
- `validate_published`, directly after the manifest `publisher_script` shape check: `lf_digest(SCRIPT) != ps['sha256']` raises `publisher script differs from the certified manifest digest (manifest publisher_script.sha256); a publisher edit needs a certified republication` (both modes).
- `check_publication_record(a, at_pin, script_sha256)`; plain mode after the blob loop checks the LF digest of `git_show(pub, rel(SCRIPT))` (`publisher script at the publication commit differs from the certified manifest digest`). Not run at the pin (D-12 dirty check covers it).
- Tests: `test_script_edit_after_publication_does_not_break_validate` rewritten as `test_script_edit_after_publication_fails_validate` (plain fails, at-pin with superseded record fails, at-pin passes again once restored); new `test_pinned_script_digest_mismatch_fails_plain_validate` (a CRLF pinned blob passes; different bytes fail). `test_at_pin_binding_reads_supersedes_from_authority` passes the manifest digest as the new third argument.

The publisher keeps CRLF line endings (843/843 lines); the test file stays LF as committed.

## Verification (measured)

- **Task 1:** v2_publication module (`p12-06-t1`): 273 passed, 1 failed. Full archive suite (`p12-06-t1-full`): **987 passed, 1 failed**, 405.51s, exit 1. Only failure: `test_publisher_still_valid_and_digest_matches_manifest`. Validators 1-6 PASS (validator 1 passes against real history: ae15c74 is an ancestor of HEAD and the 10 blobs are identical).
- **Task 2:** v2_publication module (`p12-06-t2`): 273 passed, 2 failed. Full archive suite (`p12-06-t2-full`): **987 passed, 2 failed**, 368.31s, exit 1. Failures: exactly `test_publisher_still_valid_and_digest_matches_manifest` and `test_real_published_files_validate`, both with the GATE-06 message. Validator 1 exit 1: `AuthorityError: publisher script differs from the certified manifest digest (manifest publisher_script.sha256); a publisher edit needs a certified republication`. Validators 2-6 PASS. Reply and 2.0.2 notice modules: 242 passed, exit 0.
- **Acceptance greps:** `differs between the publication commit and HEAD` 1, `is not an ancestor of HEAD` 1, `run --validate --at-pin here` 1, `git_show(head, p)` 1, `git_show('HEAD'` 0; RECORD_KEYS (l.800) and digest_normalisation (l.801) precede the pointer (l.808), which precedes the plain `must name` check (l.810). The at-pin branch's own `must name the superseded ... commit` message (l.804) is in the at-pin path and unaffected. GATE-06 messages each count 1; the old test def counts 0, the new one 1. `git show --stat` lists exactly the publisher and the v2_publication test file for both commits.

## Deviations from Plan

**1. [Minor] `check_publication_record` has no parameter defaults**
- **Reason:** adding a required `script_sha256` after `at_pin: bool = False` is a Python syntax error; giving the digest a default would let a caller skip the check silently. Both `at_pin` and `script_sha256` are now required; the only callers (the publisher and one test) pass both.
- **Commit:** c24f1d3

**2. [Minor] Ledger has two 12-06 sections**
- A `## After plan 12-06 Task 1` section was appended after commit 1 (per the orchestrator's after-each-commit instruction), and the plan's `## After plan 12-06 (commits ..., ...)` section after commit 2.

## TDD Gate Compliance

As in 12-04 and 12-05, each task's tests and implementation went into one `feat(12-06)` commit; there is no separate `test(...)` RED commit.

## Known Stubs

None.

## Threat Flags

None. No new git subcommands; the checks mitigate T-12-06-01..05 as planned.

## Commits

- 0054f2c: feat(12-06): plain --validate checks ancestry and publication-file identity at HEAD (PIN-02, D-06)
- c24f1d3: feat(12-06): --validate checks the publisher-script digest, live and at the publication commit (GATE-06, D-07, D-08)

## Self-Check: PASSED

- FOUND: scripts/publish_archive_assessment_applicability_authority_v2.py and tests/test_archive_assessment_applicability_authority_v2_publication.py in 0054f2c and c24f1d3
- FOUND: commits 0054f2c, c24f1d3
- FOUND: "## After plan 12-06" in 12-BASELINE-RED.md
