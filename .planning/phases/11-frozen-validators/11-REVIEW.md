---
phase: 11-frozen-validators
reviewed: 2026-11-14T00:00:00Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
  - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
  - tests/conftest.py
  - tests/aa_history.py
  - tests/test_archive_assessment_skip_guard.py
  - tests/test_archive_assessment_applicability_authority_v2_publication.py
  - tests/test_archive_assessment_lineage_validation.py
  - tests/test_archive_assessment_governance_decisions.py
  - tests/test_archive_assessment_governance_answers.py
  - tests/test_archive_assessment_rule_proposals.py
  - tests/test_archive_assessment_rule_proposals_record.py
  - tests/test_archive_assessment_normalisation_claims.py
  - tests/test_archive_assessment_demo3_w1_req_001_reply.py
  - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
  - .github/workflows/ems-validate.yml
findings:
  critical: 0
  warning: 4
  info: 7
  total: 11
status: issues_found
---

# Phase 11: Code Review Report

**Reviewed:** 2026-11-14
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

Scope: `git diff 5f807d4 HEAD -- scripts tests .github` (commits fe5f5b2, de6c678, 2e11045, 7b97bc5).

**Freeze (SC1).** Neither frozen builder has a runtime path to the live publisher. Both import only stdlib and `jsonschema`. Every publisher input is read through `git_show(<40-hex SHA>, <repo-relative path>)`, which uses list-form `subprocess`, a SHA regex and a `bad_rel` path guard. The only working-tree reads are the committed reply or notice JSON/MD/schema. I found no `importlib`, `exec` or `runpy` use and no publisher path string. The fail-closed paths hold: shallow detection uses `!= 'false'`, and every unknown or unreachable commit raises `AuthorityError` or `GitHistoryError`. I found no path where unknown state becomes PASS. I checked one possible concern: `git show <sha>:<path>` does not apply textconv drivers to blobs (probed in a scratch repo), so a local git config cannot change the frozen bytes.

**Problems found.** They are in the skip-to-fail machinery and in a mis-stated known finding:

- The `EMS_FAIL_ON_SKIP` hook only sees runtest-phase reports. A collection-level skip or an imperative `pytest.xfail()` still exits 0. Both were proven with a scratch run.
- The `EMS_ALLOW_NO_HISTORY` opt-out reaches only 9 of the 104 test functions in the two frozen-validator test files. This is a second opt-out gap, separate from the known publisher-import one.
- The known finding "validate_reply() never calls resolve_record_commit()" is wrong. It does call it, through `build_reply` line 177, but only after about 10 pinned git reads. A test comment repeats the wrong claim.
- `aa_history.history_problem` treats an unrecognised shallow-check answer as a full clone. That is the opposite of the builders' fail-closed rule.

No Critical issues: nothing here lets a frozen validator or the CI gate report PASS on missing or tampered history.

## Warnings

### WR-01: The EMS_FAIL_ON_SKIP hook misses collection-level skips and imperative xfail, so the CI step can pass with skipped work

**File:** `tests/conftest.py:13-21`
**Issue:** `pytest_runtest_makereport` runs only for item setup/call/teardown reports. A module-level skip (`pytest.importorskip(...)` or `pytest.skip(..., allow_module_level=True)`) produces a `CollectReport`, which this hook never sees. The module is reported as "skipped" and pytest exits 0. Separately, `rep.skipped and hasattr(rep, 'wasxfail')` also exempts an imperative `pytest.xfail('...')` and `@pytest.mark.xfail(run=False)`. Both are "skip with another label".

Proven in a scratch directory using copies of the real `conftest.py` and `aa_history.py`, with `EMS_FAIL_ON_SKIP=1`:
```
SKIPPED [1] test_mod.py:2: could not import 'no_such_mod_xyz' ...
1 skipped, 1 xfailed in 0.05s
exit=0
```
**Failure scenario:** In Phase 12 someone adds `pytest.importorskip('yaml')` at the top of an archive-assessment test file, or turns a history guard into `pytest.xfail('history missing')`. CI would then report green with the whole module or test unexecuted. D-10 ("fails if the pytest run reports any skipped test") is not met. `test_archive_assessment_skip_guard.py` does not cover either case.
**Fix:** Also catch collection skips and enforce at session end:
```python
def pytest_collectreport(report):
    if os.environ.get('EMS_FAIL_ON_SKIP') == '1' and report.skipped:
        report.outcome = 'failed'
        report.longrepr = f'collection skipped (EMS_FAIL_ON_SKIP=1): {report.nodeid}: {report.longrepr}'

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    if os.environ.get('EMS_FAIL_ON_SKIP') != '1':
        return
    tr = session.config.pluginmanager.get_plugin('terminalreporter')
    if tr and (tr.stats.get('skipped') or any(getattr(r, 'when', 'call') != 'call' or 'xfail(' in str(getattr(r, 'wasxfail', '')) for r in tr.stats.get('xfailed', []))):
        session.exitstatus = 1
```
At minimum, treat a skipped `CollectReport` as failed. Add skip-guard cases for `importorskip` and `pytest.xfail()`. Under the guard, treat imperative xfail (no `xfail` mark on the item) as a failure.

### WR-02: The EMS_ALLOW_NO_HISTORY opt-out does not reach most history-dependent tests in the reply and notice files

**File:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py:52-63,566-571` and `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py:43-48,493-498`
**Issue:** `require_history` is called in only 5 of the 53 reply test functions and 4 of the 51 notice test functions. Nearly every other test calls `inputs()` / `build()`, which run `load_inputs()` (pinned git reads plus `resolve_record_commit`), or `blob()`. `frozen_publisher()` calls `pytest.fail` directly and bypasses `require_history`. The 11-03 summary lists only the live-publisher import-time case as an opt-out gap. This is a second, larger gap in the two files this phase was about.
**Failure scenario:** A developer in a shallow clone sets `EMS_ALLOW_NO_HISTORY=1`, as the hint text tells them to. About 200 reply and notice test items still go red with `GitHistoryError` / `AuthorityError`. A handful skip. D-08 ("a local opt-out restores the skip for offline local runs") is not met. This is fail-closed, so not a blocker, but the documented operator path does not work.
**Fix:** Gate each history-dependent module once with an autouse fixture, and route the blob loader through the helper:
```python
@pytest.fixture(autouse=True)
def _pinned_history():
    require_history(ROOT, commits=FROZEN_COMMITS)
```
(Define `FROZEN_COMMITS` before use.) In `frozen_publisher`, call `require_history(ROOT, commits=(commit,))` before the `git show`.

### WR-03: The "validate_reply never calls resolve_record_commit" finding is wrong, and a test comment asserts the wrong claim

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:177,306-315,322-323`; `tests/test_archive_assessment_demo3_w1_req_001_reply.py:423`
**Issue:** `validate_reply()` → `build_reply()` → `resolve_record_commit()` at line 177. `test_validate_fails_closed_without_history_shallow` (reply test line 392) proves this: it patches only `MODULE.git` and gets the `shallow` error from `validate_reply()`. The real defect is ordering. `load_inputs()` (lines 307-314) does about 10 `git show` reads, and `build_reply` does one more `pinned_digest` (line 174), before the shallow/cat-file/ancestor guard runs. The notice calls `resolve_record_commit()` first in `load_inputs()` (notice line 179). The test comment at line 423 ("validate_reply does not call resolve_record_commit") and the 11-04 SUMMARY "Findings" are both wrong.
**Failure scenario:** Phase 12 or a later phase plans a "fix" that adds a second `resolve_record_commit()` call to `validate_reply`, or reasons about the reply's guards from the summary, on a false premise. In a shallow clone, the reply reports a `git show failed` error instead of the shallow-clone diagnosis the guard was written to give. Only the notice does this correctly, so the two frozen validators diverge.
**Fix:** Move the call to the top of the reply's `load_inputs()` and keep `build_reply`'s use of its return value:
```python
def load_inputs() -> tuple:
    resolve_record_commit()
    authority, signoff = pinned_json(REPLY_PUBLICATION_COMMIT, AUTHORITY), ...
```
This is a frozen-builder edit, so it needs the same byte-for-byte reply check. If the builder must stay untouched, correct the comment at test line 423 and the 11-04 summary finding to: "called via build_reply after the pinned reads".

### WR-04: history_problem treats an unrecognised shallow-check answer as a full clone, the opposite of the builders' fail-closed check

**File:** `tests/aa_history.py:49-52`
**Issue:** The helper returns "shallow" only when stdout is exactly `'true'`. Any other rc-0 output counts as a full clone: empty output, a wrapper's banner, or an old git that echoes `--is-shallow-repository` back. Both frozen builders do the opposite: `s.stdout.strip() != 'false'` → fail (reply line 346, notice line 155). This is "unknown resolves to OK", which CLAUDE.md's error-handling rule forbids.
**Failure scenario:** With `require_git_history` (no `commits=`, used by about 14 tests in `governance_decisions` and `rule_proposals_record`) and a git that does not answer `true`/`false`, the guard passes. The tests then run against missing history. Most fail loudly. But a comparison of two empty outputs, such as `rule_proposals_record.test_proposals_frozen_since_drafting_commit` comparing two `rev-parse` stdouts, can pass vacuously when both reads fail.
**Fix:**
```python
out = r.stdout.decode('utf-8', 'replace').strip()
if out != 'false':
    return f'{root} is a shallow or unreadable repository (is-shallow={out!r}), history is incomplete{pinned}; fetch full history'
```

## Info

### IN-01: The reply's resolve_record_commit lacks the publication-before-record ancestry check the notice has

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:341-353` (compare the notice at line 162)
**Issue:** Only `test_frozen_constants_match_git` asserts that `REPLY_PUBLICATION_COMMIT` is an ancestor of `REPLY_RECORD_COMMIT`. `--validate` in CI does not enforce it. The record-binding check (line 310) covers most tamper cases, but the two frozen validators are asymmetric.
**Fix:** Add `if git('merge-base', '--is-ancestor', REPLY_PUBLICATION_COMMIT, REPLY_RECORD_COMMIT).returncode != 0: raise AuthorityError(...)`. This is a frozen-builder edit, so defer it with WR-03.

### IN-02: The reply's ungenerated-file message can raise ValueError instead of AuthorityError

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:319-321`
**Issue:** `rel(p)` raises `ValueError` when `REPLY_*` points outside ROOT, as the tests' temp redirects do. The notice guards this with `p.is_relative_to(ROOT)` (notice line 362), and the reply has no `test_validate_reports_ungenerated_files` counterpart.
**Fix:** Mirror the notice: `rel(p) if p.is_relative_to(ROOT) else p.name`, and add the matching test.

### IN-03: Both independence proofs miss runpy and split-string publisher paths

**File:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py:705-737` (`FORBIDDEN_CALLS`, `publisher_refs`); same in the notice tests at lines 677-701
**Issue:** `FORBIDDEN_CALLS` lacks `run_path`/`run_module`/`compile`. The string check needs the full `publish_archive_assessment_applicability_authority_v2` literal. A regression such as `runpy.run_path(str(ROOT / 'scripts' / ('publish_archive_assessment_applicability_authority' + '_v2.py')))` passes the AST scan. It also passes the behavioural test, because runpy reads the unmutated file from disk, not `sys.modules`.
**Fix:** Add `run_path`, `run_module`, `compile` and `import runpy` to the scanner. Also flag any string containing `publish_archive_assessment_applicability_authority`, with no `_v2` suffix required.

### IN-04: The D-11 mutation tests exec the live publisher file, coupling frozen-builder tests to Phase 12 edits

**File:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py:753-771`; `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py:715-736`
**Issue:** `mutated_live_publisher()` compiles and runs `PUBLISHER_PATH` from disk. If a Phase 12 edit makes the publisher raise at import time (for example, the import-time catalog git reads noted in 11-03), these "frozen builder is independent" tests go red for a reason unrelated to the builders.
**Fix:** Build the mutated module as a plain `types.ModuleType` carrying only the mutated attributes plus an `AuthorityError` class. The proof does not need the real publisher body.

### IN-05: The require_git_history fixture names no pinned commit, and history_problem does not validate SHA shape

**File:** `tests/conftest.py:24-26`, `tests/aa_history.py:53-55`; used in `tests/test_archive_assessment_governance_decisions.py:248-261` and `tests/test_archive_assessment_rule_proposals_record.py:54-134`
**Issue:** D-07 asks failure messages to name the commit. These tests read `MODULE.DRAFTING_COMMIT` / `record()['drafting_commit']` / `brief_commit`, but the fixture passes no `commits=`, so a missing drafting commit is reported only as a generic git failure. `commits` taken from registry JSON (publication test lines 667/688/1054) are passed to `git cat-file -e` without a 40-hex check. A value starting with `-` would be read as an option.
**Fix:** Pass the drafting/brief commits explicitly. In `history_problem`, reject any commit not matching `[0-9a-f]{40}` with a clear message.

### IN-06: The reply tampered-constant test has no REPLY_SCHEMA_COMMIT case

**File:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py:421-436`
**Issue:** The notice parametrises `NOTICE_SCHEMA_COMMIT` (`d*40` and a pre-schema commit). The reply covers only the publication and record commits, so nothing proves that a wrong `REPLY_SCHEMA_COMMIT` is rejected through `validate_reply()`.
**Fix:** Add `('REPLY_SCHEMA_COMMIT', 'd'*40, AuthorityError, 'the frozen commit d{40} is not in the repository history')` and a reachable pre-schema commit expecting `GitHistoryError`.

### IN-07: conftest.py imports aa_history through sys.path insertion

**File:** `tests/conftest.py:8`
**Issue:** `from aa_history import require_history` relies on pytest's default `prepend` import mode adding `tests/` to `sys.path`. Under `--import-mode=importlib` (or a future `pytest.ini` that sets it), the conftest fails to import, and the whole `tests/` collection errors, including the non-archive tests.
**Fix:** Import lazily inside the fixture, or document and pin the import mode (for example, `pytest.ini` with `addopts = -p no:cacheprovider` and the import mode set to `prepend`).

---

_Reviewed: 2026-11-14_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
