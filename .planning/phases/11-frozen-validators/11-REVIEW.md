---
phase: 11-frozen-validators
reviewed: 2026-11-15T00:00:00Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
  - scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
  - tests/conftest.py
  - tests/aa_history.py
  - tests/test_archive_assessment_skip_guard.py
  - tests/test_archive_assessment_demo3_w1_req_001_reply.py
  - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py
  - tests/test_archive_assessment_applicability_authority_v2_publication.py
  - tests/test_archive_assessment_lineage_validation.py
  - tests/test_archive_assessment_governance_decisions.py
  - tests/test_archive_assessment_governance_answers.py
  - tests/test_archive_assessment_rule_proposals.py
  - tests/test_archive_assessment_rule_proposals_record.py
  - tests/test_archive_assessment_normalisation_claims.py
  - .github/workflows/ems-validate.yml
findings:
  critical: 0
  warning: 1
  info: 9
  total: 10
status: issues_found
---

# Phase 11: Code Review Report (re-review after 11-05 / 11-06)

**Reviewed:** 2026-11-15
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

Scope: `git diff 9947a48^ HEAD -- scripts tests .github`. Since the prior review (at 1145cc9) the source delta is limited to:

- `tests/conftest.py`: a new `pytest_make_collect_report` hookwrapper.
- `tests/aa_history.py`: `== 'true'` changed to `!= 'false'`.
- `tests/test_archive_assessment_skip_guard.py`: 4 module-skip cases and 4 shallow-output cases.
- `tests/test_archive_assessment_demo3_w1_req_001_reply.py`: one comment line (line 423).

Both frozen builders and `.github/workflows/ems-validate.yml` are byte-identical to the previously reviewed versions. So the prior freeze assessment (SC1) still holds: there is no runtime path to the live publisher, and every pinned read and history check fails closed.

Verification performed:
- `pytest tests/test_archive_assessment_skip_guard.py --basetemp=.pytest-temp/rr11-skipguard -p no:cacheprovider`: 22 passed.
- A scratch probe with copies of the real `conftest.py` / `aa_history.py` under `EMS_FAIL_ON_SKIP=1`:
  - A module with `pytest.skip(..., allow_module_level=True)` now gives `ERROR collecting ... Interrupted: 1 error during collection`, exit 2. This happens even when `-k` deselects that module.
  - An imperative `pytest.xfail('history missing')` still gives `1 xfailed`, exit 0. This was accepted in 11-05.

No Critical issues. Nothing found lets a frozen validator or the CI gate report PASS on missing or tampered history.

## Prior Findings Status

| ID | Title (short) | Status | Evidence |
|----|---------------|--------|----------|
| WR-01 | EMS_FAIL_ON_SKIP misses collection skips and imperative xfail | **Resolved** (collection skips) / **Accepted** (imperative xfail, `xfail(run=False)`) | `conftest.py:24-32` hookwrapper; `test_module_*` cases at skip_guard lines 93-118 pass. 11-05 decision keeps the xfail exemption as is; probe confirms `pytest.xfail()` still exits 0. See new WR-05 for a side effect of the fix. |
| WR-02 | EMS_ALLOW_NO_HISTORY opt-out reaches only a few history-dependent tests | **Accepted** | 11-05 decision: "accepted as the fail-closed D-08 convenience". Unchanged: `require_history` appears at reply lines 292/313/323/434/521 and notice lines 85/166/174/186 only. The hint text still advertises the opt-out (see IN-08). |
| WR-03 | Wrong "validate_reply never calls resolve_record_commit" claim | **Resolved** (wording) / **Accepted** (ordering deferred) | Reply test line 423 now reads "resolve_record_commit is called via build_reply, after the pinned reads in load_inputs". This is accurate: reply builder line 177 is still the only call, after `load_inputs()` at lines 306-315. 11-06 defers the builder reordering to the frozen-builder edits. |
| WR-04 | history_problem treats unrecognised shallow output as a full clone | **Resolved** | `aa_history.py:25` now uses `!= 'false'`, matching reply line 346 and notice line 155. Covered by the parametrised `b''`/`b'maybe'`/`b'true'` test at skip_guard lines 168-175. |
| IN-01 | Reply lacks the publication-before-record ancestry check | **Open** (deferred with frozen-builder edits) | Reply `resolve_record_commit` (lines 341-353) has no `merge-base --is-ancestor REPLY_PUBLICATION_COMMIT REPLY_RECORD_COMMIT`; the notice has it at line 162. |
| IN-02 | Reply ungenerated-file message can raise ValueError | **Open** | Reply lines 319-321 still call `rel(p)` without the `is_relative_to(ROOT)` guard the notice uses at line 362. |
| IN-03 | Independence proofs miss runpy and split-string publisher paths | **Open** | Test files unchanged apart from one comment. |
| IN-04 | D-11 mutation tests exec the live publisher file | **Open** | Unchanged. |
| IN-05 | require_git_history names no pinned commit; no SHA shape check | **Open** | `conftest.py:35-37` still calls `require_history(ROOT)` with no commits. `aa_history.py:27-29` still passes registry-sourced values to `git cat-file -e` without a `[0-9a-f]{40}` check. |
| IN-06 | No REPLY_SCHEMA_COMMIT tampered-constant case | **Open** | Reply parametrisation at lines 422-430 is unchanged. |
| IN-07 | conftest imports aa_history via sys.path insertion | **Open** | `conftest.py:8` unchanged. There is still no `pytest.ini` / `pyproject.toml` pinning `--import-mode=prepend`. |

## Narrative Findings (AI reviewer)

## Warnings

### WR-05: The collection-skip guard aborts the whole session for a skip in any module, including ones that `-k` deselects, so one unrelated skip hides every archive-assessment result

**File:** `tests/conftest.py:24-32`; `.github/workflows/ems-validate.yml` (step "Archive-assessment tests": `python -m pytest tests -k archive_assessment`)
**Issue:** The hookwrapper turns every skipped `CollectReport` into `failed`. pytest treats a failed collection report as a collection error, and by default it stops the session before running any test ("Interrupted: N errors during collection", exit 2). Two things make this broader than D-10 needs:
1. The CI step collects all of `tests/` and only then filters with `-k archive_assessment`. Collection runs before deselection, so a module-level skip in any non-archive test file fails the archive-assessment job. That includes any of the roughly 100 other test modules in this repository, or one added later by unrelated work. My scratch probe shows this: `pytest test_a.py test_b.py -k ok`, where `test_a.py` has a module-level skip and `test_ok` is the only selected test, gives `1 error`, `Interrupted`, exit 2, and `test_ok` never runs.
2. Because the session is interrupted, the converted skip hides every other result. The CI log shows one "ERROR collecting" line and no pass/fail data for the 900+ archive tests. The 11-05 summary records the outcome as "1 error" but does not say that nothing else runs.

This is fail-closed, so it is not a blocker. But the archive-assessment gate now depends on whether unrelated, deselected modules call `importorskip` at module level. That is a realistic pattern for optional dependencies such as `docx` and LibreOffice-backed tests. A developer who adds one somewhere else in `tests/` turns the Hayes-facing gate red with no archive-assessment cause.
**Fix:** Limit the conversion to collectors that will actually be selected, or defer the failure so collection finishes. Do either of these:
```python
@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    outcome = yield
    if os.environ.get('EMS_FAIL_ON_SKIP') != '1':
        return
    rep = outcome.get_result()
    if rep.skipped and 'archive_assessment' in collector.nodeid:
        rep.outcome = 'failed'
        rep.longrepr = f'skipped module treated as failure (EMS_FAIL_ON_SKIP=1): {collector.nodeid}: {rep.longrepr}'
```
or keep the reports as skipped and set `session.exitstatus = 1` in a `pytest_sessionfinish(session, exitstatus)` hook when `terminalreporter.stats.get('skipped')` is non-empty. That way the run completes and shows every result. Also narrow the CI step to `tests/test_archive_assessment_*.py` instead of `tests -k archive_assessment`, so CI does not collect unrelated modules. Add a skip-guard case that runs a skipped module together with `-k` deselection and asserts the intended behaviour.

## Info

### IN-08: The history-failure hint still tells operators to set EMS_ALLOW_NO_HISTORY=1, which skips only about 9 of the roughly 104 frozen-validator tests

**File:** `tests/aa_history.py:10`
**Issue:** WR-02 was accepted as a fail-closed convenience. But `HINT` still offers the opt-out as the fix for an offline run ("or set EMS_ALLOW_NO_HISTORY=1 for an offline local run"). An operator who follows it still sees about 200 red reply and notice items (see WR-02). With the gap accepted, the message now promises more than the code does.
**Fix:** Change the hint wording to match the accepted behaviour, for example: "set EMS_ALLOW_NO_HISTORY=1 to skip the history-guarded tests; tests that read pinned history still fail without it". Alternatively, record the limit in the requirement doc.

### IN-09: An unrecognised shallow-check output is reported as "is a shallow repository", without the actual output

**File:** `tests/aa_history.py:25-26`
**Issue:** After the WR-04 fix, empty output, a wrapper banner, or an old git echoing `--is-shallow-repository` all produce "`<root>` is a shallow repository, history is incomplete". Running `git fetch --unshallow`, as the hint suggests, does not fix those cases. The prior fix suggestion included the observed value; the implemented change kept the old text.
**Fix:**
```python
out = r.stdout.decode('utf-8', 'replace').strip()
if out != 'false':
    return f'{root} is a shallow or unreadable repository (is-shallow={out!r}), history is incomplete{pinned}; fetch full history'
```
The existing test asserts only `'shallow' in msg and 'fetch full history' in msg`, so it still passes with this text.

---

_Reviewed: 2026-11-15_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
