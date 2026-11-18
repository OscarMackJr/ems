---
phase: quick-261118-cgq
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
autonomous: true
requirements: [B-1]
must_haves:
  truths:
    - "The deep-root git_show test never skips: no skipif, no pytest.skip"
    - "On any platform, MODULE.git_show(PUB, long_rel) is asserted equal to real `git show PUB:long_rel --` bytes from a real shared clone"
    - "The 'Filename too long' reproduction is asserted only on win32 with the deep root built and the failure reproducing; it is never a precondition"
    - "Archive suite has 0 skips under EMS_FAIL_ON_SKIP=1"
  artifacts:
    - path: "tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py"
      provides: "skip-free test_git_show_double_dash_survives_deep_checkout_root_with_real_git"
  key_links:
    - from: "the test"
      to: "MODULE.git_show"
      via: "monkeypatch MODULE.ROOT to clone"
      pattern: "setattr\\(MODULE, 'ROOT', clone\\)"
---

<objective>
Close audit blocker B-1: the Windows-only deep-root git_show test goes red on ubuntu CI because EMS_FAIL_ON_SKIP=1 turns skips into failures. Make it skip-free while keeping the real-git git_show check on every platform.
Output: edited test only (test-only change; no regeneration; do not touch conftest.py, the CI workflow, builders, notice JSON/MD/schema, or the frozen reply / 2.0.2 builders).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/v1.2.0-MILESTONE-AUDIT.md
@tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Rewrite the deep-root git_show test without skips</name>
  <files>tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py</files>
  <action>
Edit only the test at ~lines 714-739 (keep its name for traceability with 15-VERIFICATION and the audit). Remove the `@pytest.mark.skipif(...)` decorator. Keep `require_history(ROOT, commits=FROZEN_COMMITS)`, `long_rel`, and the `base = TMP / 'deep'` cleanup.
1. Build the deep clone root as today (loop appending 'd'*20 segments while len(str(clone)) + 1 + len(long_rel) <= 270, then `/ 'c'`). Track `deep = len(str(clone)) < 240`. If not deep, replace the pytest.skip with a fallback: `clone = base / 'c'` (shallow root under TMP). No skip.
2. `clone.parent.mkdir(parents=True)`, then real `git clone --shared --no-checkout -q ROOT clone`; keep the pytest.fail on non-zero return code. Keep `git('config','core.longpaths','false',cwd=clone)` assert.
3. Run `without = git('show', f'{PUB}:{long_rel}', cwd=clone)`. Compute `reproduces = without.returncode != 0 and 'Filename too long' in without.stderr`. Only `if sys.platform == 'win32' and deep and reproduces:` add an informative assertion (e.g. `assert without.returncode != 0 and 'Filename too long' in without.stderr`, which is trivially true there; the point is it is never a precondition and never skips). Do not assert reproduction otherwise and do not skip.
4. Always: `monkeypatch.setattr(MODULE, 'ROOT', clone)` then `assert MODULE.git_show(PUB, long_rel) == git('show', f'{PUB}:{long_rel}', '--').stdout`. Note `git(...)` helper must be run with `cwd=clone` for the `--` reference call if it was not already defaulting to it; check the helper's signature and keep the existing call semantics (existing line passes no cwd, so confirm it resolves to the monkeypatched ROOT; if it uses the module ROOT global of the test file instead, pass `cwd=clone` explicitly).
5. Keep the `finally: shutil.rmtree(base, onerror=_rm_readonly)`.
If `sys` becomes unused elsewhere in the file, leave the import (it is still used by the win32 check).
  </action>
  <verify>
    <automated>cd C:\temp\standars\ems; $env:EMS_FAIL_ON_SKIP='1'; .\.venv\Scripts\python.exe -m pytest tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py -k deep_checkout_root -q --basetemp C:\Users\OMack\AppData\Local\Temp\claude\1a7b91a18e8f3eda\ca3502dc-11b6-48c9-86c8-e5169dea0c8f\scratchpad\bt1</automated>
  </verify>
  <done>Test passes natively on Windows with EMS_FAIL_ON_SKIP=1, not skipped; file has no `pytest.skip` or `skipif` (grep -n "pytest.skip\|skipif" returns nothing).</done>
</task>

<task type="auto">
  <name>Task 2: Verify non-Windows path, full suite, validator; commit</name>
  <files>tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py</files>
  <action>
Executor may be in a worktree without .venv: use the main repo venv by absolute path `C:\temp\standars\ems\.venv\Scripts\python.exe`. Every pytest run needs `--basetemp` under C:\Users\OMack\AppData\Local\Temp\claude\1a7b91a18e8f3eda\ca3502dc-11b6-48c9-86c8-e5169dea0c8f\scratchpad (distinct subdir per run). Set EMS_FAIL_ON_SKIP=1 for all.
1. Simulate non-Windows: write a one-off plugin in the scratchpad (e.g. scratchpad\force_linux.py with `import sys; sys.platform = 'linux'` at import) and run the changed test with `-p force_linux` and PYTHONPATH including the scratchpad. It must pass (git_show equality asserted, reproduction branch not taken). If forcing sys.platform breaks unrelated machinery (subprocess/pathlib), instead monkeypatch only `sys.platform` as seen by the test module (e.g. plugin sets it in a `pytest_collection_modifyitems`/fixture-free hook after collection) so the test's `sys.platform` check sees 'linux'.
2. Run the full notice 2.0.3 test file plus tests/test_archive_assessment_skip_guard.py: all pass, 0 skipped.
3. Run `.venv python scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py --validate` and confirm it prints PASS.
4. Commit atomically, staging by explicit path only (working tree has unrelated uncommitted work, including a modified docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md and registry files, which must NOT be staged): `git add tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` then `git commit -m "fix(quick-261118-cgq): make deep-root git_show test skip-free off Windows" -m "<body>" ` ending with the line `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Confirm with `git show --stat HEAD` that only the one test file is in the commit.
  </action>
  <verify>
    <automated>cd C:\temp\standars\ems; $env:EMS_FAIL_ON_SKIP='1'; .\.venv\Scripts\python.exe -m pytest tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py tests/test_archive_assessment_skip_guard.py -q -rs --basetemp C:\Users\OMack\AppData\Local\Temp\claude\1a7b91a18e8f3eda\ca3502dc-11b6-48c9-86c8-e5169dea0c8f\scratchpad\bt2</automated>
  </verify>
  <done>Linux-simulated run passes; full file + skip guard pass with 0 skipped; validator prints PASS; single commit contains only the test file.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| none | Test-only change; no runtime, input, or published-authority surface touched |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-quick-01 | Tampering | unrelated uncommitted work | mitigate | stage by explicit path; verify `git show --stat HEAD` lists one file |
| T-quick-02 | Repudiation | weakened coverage | mitigate | git_show equality vs real `git show ... --` asserted on all platforms |
</threat_model>

<verification>
Native and simulated-linux runs pass under EMS_FAIL_ON_SKIP=1; grep for pytest.skip|skipif empty; validator PASS; one-file commit.
</verification>

<success_criteria>
Audit blocker B-1 resolved: archive-assessment CI job on ubuntu has zero skips from this test and still exercises real-git git_show.
</success_criteria>

<output>
Create `.planning/quick/261118-cgq-make-the-windows-only-deep-root-git-show/261118-cgq-SUMMARY.md` when done
</output>
