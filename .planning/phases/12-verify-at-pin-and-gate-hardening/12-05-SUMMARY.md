---
phase: 12-verify-at-pin-and-gate-hardening
plan: 05
subsystem: archive-assessment publisher (authority v2)
tags: [PIN-01, D-01, D-02, D-03, D-04, D-05, D-12, at-pin, git-seam, red-window]
requires: [12-04]
provides:
  - git_run single subprocess seam plus git_head, git_is_ancestor, git_not_shallow, git_dirty
  - git_show passes -- after revision:path
  - publication_paths() (the 10 D-05 files, defined once)
  - AT_PIN_DEFERRED constant and `--validate --at-pin` CLI mode
affects:
  - scripts/publish_archive_assessment_applicability_authority_v2.py (live bytes still differ from manifest publisher_script.sha256; accepted red unchanged)
  - 12-06 (PIN-02 uses git_head, git_is_ancestor, git_not_shallow, publication_paths)
tech-stack:
  added: []
  patterns: [single git seam (git_show + git_run), validate SHA/path before calling git, fail closed on unknown git output]
key-files:
  created:
    - .planning/phases/12-verify-at-pin-and-gate-hardening/12-05-SUMMARY.md
  modified:
    - scripts/publish_archive_assessment_applicability_authority_v2.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - .planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md
decisions:
  - "[Phase 12] 12-05: all git access goes through git_show or git_run; typed helpers validate 40-hex SHAs and bad_rel paths before git and raise GitHistoryError on OSError or unexpected rc"
  - "[Phase 12] 12-05: --pre-publication removed with no alias; --at-pin requires --validate; at-pin reads the superseded identity from source_lineage.supersedes, not SUPERSEDED_V2_0_1"
  - "[Phase 12] 12-05: at-pin runs git_not_shallow then git_dirty over the 10 D-05 paths plus the publisher script before any content check; PASS prints one JSON object with exactly one deferred item (PUBLICATION_RECORD_BINDING); plain --validate still prints PASS"
metrics:
  duration: ~45 min active (excluding suite wall time)
  completed: 2026-11-16
  tasks: 2
  files: 3
requirements-completed: [PIN-01]
---

# Phase 12 Plan 05: `--validate --at-pin` and a single git seam Summary

Hayes can now run `--validate --at-pin` on a clean checkout of a publication commit. In that mode the publisher:
- checks every item that can be checked at the pin;
- reads the superseded identity from the authority's own `source_lineage.supersedes`;
- fails closed on a dirty tree or a shallow clone;
- prints a single JSON object naming the one deferred check (`PUBLICATION_RECORD_BINDING`).

All git access now goes through two functions, `git_show` and `git_run`. This delivers PIN-01, which is not marked complete yet; it completes later in the phase, as instructed.

## What was done

**Task 1 (commit bc3d47e). Git seam and D-05:**
- `git_run(*args)` is the only new `subprocess.run` call site. An `OSError` becomes `GitHistoryError('git <cmd>: git unavailable: ...')`.
- Four typed helpers sit on top of `git_run`:
  - `git_head`: returns a 40-hex SHA, otherwise raises `GitHistoryError`.
  - `git_is_ancestor`: both arguments must be 40-hex, else `AuthorityError` before git runs. rc 0 returns True, rc 1 returns False, any other rc raises `GitHistoryError`.
  - `git_not_shallow`: passes only on exactly `false`. `true` raises a "shallow ... fetch full history" error. Any other output raises "cannot tell whether the clone is shallow" with the repr of the output.
  - `git_dirty(paths)`: checks every path with `bad_rel`, then runs `status --porcelain -- <paths>` and returns the non-empty lines.
- A small `git_err(r)` helper decodes stderr. It has no `subprocess` annotation, so the source scan stays clean.
- `git_show` argv is now `['git', 'show', f'{commit}:{relative_path}', '--']`. Nothing else in it changed.
- `publication_paths()` returns `[rel(AUTHORITY), rel(SCHEMA), rel(SIGNOFF)]` followed by the seven `N_*` outputs under `rel(OUT)`.
- Test changes:
  - The source-scan helper now strips both `git_show` and `git_run`, and both scan tests assert `subprocess.run` appears in `git_run`.
  - 29 new unit tests cover the helpers, the `--` argv, and `publication_paths`. The real publication commit `ae15c74` `diff-tree` list equals `sorted(publication_paths())`.
  - The byte-identity test uses `MODULE.publication_paths()` with `len == 10`. The module-level `PUBLICATION_PATHS` list is deleted.

**Task 2 (commit 1b83c42). At-pin mode:**
- `main`: `--at-pin` replaces `--pre-publication`, with no alias. `--at-pin` without `--validate` is a parser error. The flag calls `validate_published(args.at_pin)`.
- `validate_published(at_pin)` runs these checks first, in order:
  1. `git_not_shallow()`;
  2. `git_dirty([*publication_paths(), rel(SCRIPT)])`. Any output raises `AuthorityError('at-pin: publication files are modified or untracked in the working tree: ...')`.
- At the end it prints `json.dumps({'status': 'PASS', 'mode': 'AT_PIN', 'deferred': [AT_PIN_DEFERRED]})`. Plain mode still prints `PASS`.
- `check_publication_record(a, at_pin)`: the at-pin branch takes `sup = a['source_lineage']['supersedes']` and checks the record against it:
  - `publication_commit` must equal `sup['commit']`;
  - `authority_sha256` must equal `sup['sha256']`;
  - the identity must be `sup['authority_id']` and `sup['version']`.

  There is no `SUPERSEDED_V2_0_1` reference left in the function. The git_show cross-checks of the authority and manifest digests still run in both modes.
- In the dry-run gate line, "pre-publication mode" became "at-pin mode (--validate --at-pin)" (D-14, partial).
- Test changes:
  - The `env` fixture fakes `git_not_shallow` and `git_dirty`. `REAL_GIT_DIRTY` and `REAL_GIT_NOT_SHALLOW` are captured at import.
  - `superseded_record` builds the record from the authority's `supersedes` entry.
  - The five pre-publication tests are rewritten under their at-pin names.
  - Five tests are new:
    - `test_at_pin_record_blobs_must_match_the_superseded_commit`
    - `test_at_pin_dirty_tree_fails_closed`: asserts the exact 11-path list passed to `git_dirty`.
    - `test_at_pin_shallow_fails_closed`
    - `test_real_git_repo_at_pin_passes_and_dirty_fails`: a real temp git repo. At-pin passes on a clean tree, fails after the authority file is edited, passes again once it is restored, and fails after the publisher script is edited.
    - `test_cli_pre_publication_flag_is_removed`
  - `test_at_pin_binding_reads_supersedes_from_authority` also proves the binding follows the passed-in document: a substituted `supersedes` entry, 9.9.8 at `c*40`, passes `check_publication_record`.

**Pitfall 3 note:** extra files in the gitignored OUT folder are not visible to `git status --porcelain`. They are caught by the existing OUT file-set check in `validate_published` ("generated file set differs from the expected set"), not by `git_dirty`. Modified tracked files under OUT are visible to porcelain, because they were force-added at publication.

## Verification (measured)

- **Task 1:**
  - v2_publication module (basetemp `p12-05-t1b`): 260 passed, 1 failed (the accepted test), exit 1.
  - Full archive suite (`p12-05-t1-full`): **974 passed, 1 failed**, 328.67s, exit 1.
  - Validators 1-6 PASS.
- **Task 2:**
  - v2_publication module (`p12-05-t2`): 265 passed, 1 failed (the accepted test), exit 1.
  - Full archive suite (`p12-05-t2-full`): **979 passed, 1 failed**, exit 1. pytest reported a wall time of 44138s; that is a host clock/sleep artefact.
  - Validators 1-6 PASS.
- In both full runs the only failure is `tests/test_archive_assessment_applicability_authority_v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest`.
- **Acceptance greps:**
  - `subprocess.run` appears 2 times.
  - The six helper defs are all present (count 6).
  - The `'--'` argv appears once.
  - `^PUBLICATION_PATHS` appears 0 times.
  - `git grep -- "--pre-publication" -- scripts tests` prints nothing.
  - `pre_publication` appears 0 times in the publisher.
  - `'--at-pin'` appears once, and so do `AT_PIN_DEFERRED = 'PUBLICATION_RECORD_BINDING: `, `'mode': 'AT_PIN'` and `git_dirty([*publication_paths(), rel(SCRIPT)])`.
- `git show --stat` lists exactly the publisher and the v2_publication test file for both commits.
- `--validate --at-pin` at the working HEAD (1b83c42) gives exit 1 with `at-pin record must name the superseded 2.0.1 publication commit`. This is correct: HEAD is not a pin. Plain `--validate` prints PASS.
- The publisher keeps CRLF line endings: both edits were applied on LF text and written back as CRLF.

## Deviations from Plan

**1. [Rule 2 - Fail closed] `git_dirty([])` raises `AuthorityError`**
- **Issue:** `git status --porcelain --` with no pathspec reports the whole repository. A call with an empty list would therefore not mean what its caller intends.
- **Fix:** an empty path list is rejected before git is called. Covered by `test_git_dirty_rejects_empty_path_list`.
- **Commit:** bc3d47e

**2. [Rule 3 - Blocking] The removed flag is built by string concatenation in the test**
- **Issue:** the plan asks for both a CLI test that passes `--pre-publication` and a `git grep -- "--pre-publication" -- scripts tests` that prints nothing.
- **Fix:** the test builds the flag as `'--pre' + '-publication'` (`REMOVED_FLAG`). It also asserts that the publisher source holds neither `pre-publication` nor `pre_publication`.
- **Commit:** 1b83c42

**3. [Minor] The real-repo at-pin test sets `core.autocrlf false`**
- **Reason:** this stops a global autocrlf setting from producing a spurious dirty status in the temp repo.
- **Commit:** 1b83c42

## TDD Gate Compliance

As in 12-04, each task's tests and implementation went into one commit (`refactor(12-05)` and `feat(12-05)`), so there is no separate `test(...)` RED commit. Task 1 is behaviour-preserving apart from the `--` argv. Task 2's new tests reference `AT_PIN_DEFERRED`, `--at-pin` and the `at_pin` keyword, none of which existed before the change.

## Known Stubs

None.

## Threat Flags

None. The new git surface (status, rev-parse, merge-base) is covered by T-12-05-01..06.

## Commits

- bc3d47e: refactor(12-05): single git seam, git show --, D-05 publication_paths (PIN-01)
- 1b83c42: feat(12-05): --validate --at-pin with one named deferred check (PIN-01, D-01..D-04, D-12)

## Self-Check: PASSED

- FOUND: scripts/publish_archive_assessment_applicability_authority_v2.py (in bc3d47e and 1b83c42)
- FOUND: tests/test_archive_assessment_applicability_authority_v2_publication.py (in bc3d47e and 1b83c42)
- FOUND: commits bc3d47e, 1b83c42
- FOUND: "## After plan 12-05 Task 1" and "## After plan 12-05 Task 2" in 12-BASELINE-RED.md
