---
phase: 11-frozen-validators
plan: 03
subsystem: archive-assessment
tags: [tests, history-guard, ci, skip-guard, hayes]
requires: [Plan 11-01 (fe5f5b2), Plan 11-02 (de6c678)]
provides: [shared history helper tests/aa_history.py, EMS_FAIL_ON_SKIP conftest hook, require_git_history fixture, skip-guard proof test, CI step env]
affects: [Plan 11-04 REJECTS replacement, Phase 12 publisher edits (publisher import-time git errors still lack the fetch hint)]
key-files:
  created:
    - tests/aa_history.py
    - tests/conftest.py
    - tests/test_archive_assessment_skip_guard.py
  modified:
    - .github/workflows/ems-validate.yml
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
    - tests/test_archive_assessment_lineage_validation.py
    - tests/test_archive_assessment_governance_decisions.py
    - tests/test_archive_assessment_governance_answers.py
    - tests/test_archive_assessment_rule_proposals.py
    - tests/test_archive_assessment_rule_proposals_record.py
    - tests/test_archive_assessment_normalisation_claims.py
    - tests/test_archive_assessment_demo3_w1_req_001_reply.py
    - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
requirements: [FROZEN-03]
requirements-completed: [FROZEN-03]
decisions:
  - "Opt-out env var is EMS_ALLOW_NO_HISTORY=1 (skip instead of fail); CI guard env var is EMS_FAIL_ON_SKIP=1, set only on the Archive-assessment tests step"
  - "D-10 mechanism: pytest_runtest_makereport hookwrapper in tests/conftest.py (not -rs summary grep); proven for pytest.skip and skipif-mark skips, leaves xfail alone"
  - "All seven git_ready copies de-duplicated into aa_history.history_problem/require_history; pinned commits passed via commits= and named in every message"
  - "Tool-availability checks (shutil.which('git'), temp-repo git init) also go through require_history(ROOT), so they follow the opt-out; a failed git init/commit in a temp repo is pytest.fail with stderr"
completed: 2026-11-14
---

# Phase 11 Plan 03: Fail instead of skip on missing pinned history Summary

No archive-assessment test skips silently any more. A missing pinned commit or blob, a shallow clone, a non-repository or a missing git now fails with a message naming the path, the pinned commit SHAs and "fetch full history". `EMS_ALLOW_NO_HISTORY=1` turns those into skips for offline local runs, and the CI step sets `EMS_FAIL_ON_SKIP=1`, which turns any skip (including one caused by the opt-out) into a failure.

## Tasks

1. **Helper, hook, fixture, guard test, workflow**
   - `tests/aa_history.py`: `history_problem(root, commits=())` (list-form `git rev-parse --is-shallow-repository` and `git cat-file -e <sha>^{commit}`; messages for git unavailable / not a repository / shallow / each missing commit, all naming `root`, the pinned commits and "fetch full history") and `require_history(root, commits=())` (`pytest.skip` under `EMS_ALLOW_NO_HISTORY=1`, otherwise `pytest.fail(..., pytrace=False)` with the `git fetch --unshallow` / `EMS_ALLOW_NO_HISTORY=1` hint).
   - `tests/conftest.py`: `pytest_runtest_makereport(hookwrapper=True)` converting any non-xfail skipped report to failed when `EMS_FAIL_ON_SKIP == '1'` (returns immediately otherwise), and a `require_git_history` fixture calling `require_history(ROOT)`.
   - `tests/test_archive_assessment_skip_guard.py` (14 tests): subprocess pytest runs on a one-test temp file (copies of the real `conftest.py` and `aa_history.py`, `-p no:cacheprovider`, `--basetemp`, `--rootdir`, inherited `EMS_*` vars stripped) for: `pytest.skip` with/without the guard; `skipif` mark with/without the guard (A1); passing test and strict xfail under the guard stay green; missing history fails by default, skips with the opt-out only, fails with both vars set (Pitfall 4). In-process tests cover each `history_problem` message (full clone None, missing commit, not a repository via `GIT_DIR`, git unavailable) and `require_history` fail/skip/opt-out-only-on-'1'. The module-level `from aa_history import ...` proves A2.
   - `.github/workflows/ems-validate.yml`: `env: EMS_FAIL_ON_SKIP: '1'` on the `Archive-assessment tests` step only. `EMS_ALLOW_NO_HISTORY` appears 0 times; `fetch-depth: 0` and the validator step unchanged.
2. **Publication and lineage**
   - Publication: local `git_ready` removed; `prev_201_authority_bytes()` now `pytest.fail`s naming the relative path, the full 31addfa SHA, ROOT and "fetch full history (git fetch --unshallow)"; temp-repo test: `require_history(ROOT)` for git availability, `git init`/`git commit` failure is `pytest.fail` with stderr; the four `skipif(not REAL_*.exists())` guards removed, with `assert ... must be committed` in their place; the 8 `git_ready` sites use `require_history` with the commits each test reads (54a7fd0 + V1 baseline, 31addfa, or the record's publication commit).
   - Lineage: `git_ready` replaced with `PINNED_COMMITS = (V1_BASELINE_COMMIT, 2.0.1 commit)`; 5 `shutil.which('git')` skips (incl. the `fx` temp-repo fixture) are `require_history(REAL_ROOT)`; the 3 `git_ready` sites pass `PINNED_COMMITS`; the 2.0.1 blob read `pytest.fail`s with path, full SHA and fetch hint; `import shutil` dropped.
3. **governance_decisions, governance_answers, rule_proposals, rule_proposals_record**
   - governance_decisions: `git_ready`/`needs_git` removed; 3 tests use `@pytest.mark.usefixtures('require_git_history')`; the eed4a5f test uses `RECORDS_COMMIT = 'eed4a5fcdaeba0338f9b482598bcc08c4b7ee619'` via `require_history(commits=)` and `pytest.fail` naming path, full SHA and fetch hint; both `skipif(not DECISIONS.exists())` replaced by existence asserts.
   - governance_answers: the six `'answers not yet filled'` skips are `assert all(e['disposition'] is not None ...), 'committed answers must be filled'`.
   - rule_proposals: `gated()` and its 9 uses removed (parametrize ids kept); `git_out` calls `require_history(ROOT)` instead of catching `FileNotFoundError`.
   - rule_proposals_record: `git_ready`/`needs_git` removed; 11 tests use `usefixtures('require_git_history')`.
4. **normalisation_claims, reply, notice**
   - normalisation_claims: `PINNED_COMMITS` (V1 baseline, 2.0.1) plus the commit each test reads; unused `import pytest` removed (ruff F401).
   - reply: `FROZEN_COMMITS = (REPLY_PUBLICATION_COMMIT, REPLY_RECORD_COMMIT, REPLY_SCHEMA_COMMIT)` at 4 sites. notice: `FROZEN_COMMITS = (PUB, REC, SUP, SCH)` at 3 sites.
   - D-07 builder check: both frozen builders' fail-closed errors already name the full SHA, path and "fetch full history" (11-01/11-02). No builder edited.

## Verification

- Task 1 `tests/test_archive_assessment_skip_guard.py` (basetemp `p11-3a-x2`, final code): **14 passed**. A1 (hook converts both `pytest.skip` and `skipif` setup skips) and A2 (`from aa_history import ...` in a test module and in conftest) confirmed.
- Task 2 publication + lineage (`p11-3b-x1`): **295 passed, 0 failed, 0 skipped**.
- Task 3 four files (`p11-3c-x1`): **251 passed, 0 failed, 0 skipped**.
- Task 4 three files (`p11-3d-t1`): **226 passed, 0 failed, 0 skipped**.
- Full `pytest tests -k archive_assessment -rs` (`p11-3d-full1`): **890 passed, 0 failed, 0 skipped, 7 deselected** (baseline 876 + 14 skip-guard tests). Started before the last two cosmetic edits (message wording in `aa_history.py`, unused `import pytest` in normalisation_claims).
- Same run with `EMS_FAIL_ON_SKIP=1` on the final code (`p11-3d-full-guard`): **890 passed, 0 failed, 0 skipped, 7 deselected**.
- Whole `tests/` collection: 897 collected, no collection errors; the 7 non-archive tests pass (`-k "not archive_assessment"`), so the conftest is inert for them. No skip pattern exists in any non-archive test file.
- Completeness grep `grep -rln "pytest.skip\|pytest.mark.skipif\|git_ready\|needs_git\|gated(" tests/ --include=*.py`: only `tests/aa_history.py` (opt-out skip) and `tests/test_archive_assessment_skip_guard.py` (temp-file strings, `pytest.skip.Exception`). Per-task greps (incl. `not yet` and `gated`) over the converted files: 0 hits.
- Workflow: `grep -n EMS_FAIL_ON_SKIP` shows the single step env (line 89); `grep -c EMS_ALLOW_NO_HISTORY` prints 0; `git diff` touches only that step; YAML parses.
- GIT_DIR probe (empty dir), one history-dependent test per converted file (governance_answers has none): reply, notice, normalisation_claims, lineage, governance_decisions (eed4a5f and a fixture-based test), publication (`test_superseded_v2_0_1_constants_match_git_history`) **fail** with `C:\temp\standars\ems is not a git repository, pinned history is unavailable (pinned commits: <full SHAs>); fetch full history; run git fetch --unshallow, or set EMS_ALLOW_NO_HISTORY=1 for an offline local run`. With `EMS_ALLOW_NO_HISTORY=1` they **skip**; with both vars set they **fail** (`skipped test treated as failure (EMS_FAIL_ON_SKIP=1)`). `prev_201_authority_bytes()` with an unreachable commit: `2.0.1 authority blob registry/archive_assessment_applicability_authority_v2.json at commit <40-char sha> is not reachable in C:\temp\standars\ems; fetch full history (git fetch --unshallow)`. rule_proposals, rule_proposals_record and the publication `env`-fixture tests are red in all three modes (see Findings).
- All six validator commands print PASS (publisher, governance decisions, rule proposals `--validate` and `--validate-record`, reply, notice). `git diff --stat` empty for `scripts/`, `schemas/`, `generated/`, `docs/DEMO3_*` and `registry/archive_assessment_*` (SC4). `git diff --cached` empty.
- `ruff check --select F` passes on all 12 test files plus the helper and conftest.
- Unrelated changes (`.planning/config.json`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `registry/adjudication_rules.json`, `registry/policy_decisions.json`) are still unstaged and untouched.

## Deviations from Plan

1. **Research said `normalisation_claims` `git_ready` checked V1_BASELINE and 2.0.1.** It did not (plain shallow check only). Per the plan text, those two commits are now passed via `commits=`, plus the publication commit each test actually reads. This is stricter, not looser.
2. **Non-temp-repo `shutil.which('git')` skips in lineage** (LIN-03 tests, D-09 catalog test) also go through `require_history(REAL_ROOT)`, so in a shallow clone they now fail (or skip under the opt-out) where they previously ran. In a full clone (CI, `fetch-depth: 0`) behaviour is identical. Chosen so there is one opt-out path, as the plan's "follows the opt-out via require_history" wording asks.
3. **Message text.** `history_problem` also lists the pinned commits in the shallow / not-a-repository / git-unavailable messages, so the probe's message names the full SHAs even when the repository itself is unreadable.
4. **Skip-guard subprocess uses copies** of `tests/conftest.py` and `tests/aa_history.py` in its temp dir (the temp test lives outside `tests/`, so the real conftest would not load). The copies are byte-for-byte the real files, read at test time.

## Findings (not fixed; out of scope / frozen)

- **Live publisher import-time git errors bypass the opt-out.** With `GIT_DIR` pointing at an empty dir, `tests/test_archive_assessment_rule_proposals.py` errors at collection and `rule_proposals_record` / the publication `env` fixture error at setup, because `scripts/validate_archive_assessment_rule_proposals.py` and the publication fixtures call the live publisher's `catalog_controls()`/`catalog_bytes()` first. The publisher raises `GitHistoryError('registry/control_catalog.yaml@62a8955: git show failed: ...')` with a short SHA and no fetch hint. These are red (never green, so FROZEN-03 holds), but `EMS_ALLOW_NO_HISTORY=1` does not make those tests skip, and the message lacks the full SHA / hint. The publisher is frozen until Phase 12 (SC4: no publisher diff), so this is left for Phase 12.
- `tests/test_archive_assessment_governance_answers.py` has no history-dependent test, so it is not part of the GIT_DIR probe.

No commits were made and nothing was staged. The orchestrator commits by explicit path (all 13 files in `files_modified`) with `test(11-03): fail instead of skip on missing pinned history; fail CI on any skip`.

## Self-Check: PASSED

- `tests/aa_history.py`, `tests/conftest.py`, `tests/test_archive_assessment_skip_guard.py` exist (untracked); the 9 converted test files and the workflow show as ` M`.
- Nothing staged; no commits made; no frozen script/schema/registry bytes changed.
