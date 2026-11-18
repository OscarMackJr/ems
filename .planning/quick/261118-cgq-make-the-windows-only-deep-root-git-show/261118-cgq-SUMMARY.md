---
quick_id: 261118-cgq
status: complete
date: 2026-11-18
closes: v1.2.0 audit B-1 (CI archive-assessment would fail on the Windows-only skipif test)
commits: [66248f4, 72a5c06]
key-files:
  modified:
    - tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py
---

# Quick Task 261118-cgq: CI-safe deep-root git_show test

`test_git_show_double_dash_survives_deep_checkout_root_with_real_git` now has no skips, so it can run under `EMS_FAIL_ON_SKIP=1` on any platform.

## Changes

- Removed `@pytest.mark.skipif(sys.platform != 'win32')` and both in-test `pytest.skip` calls.
- When the deep clone root would be 240 characters or more, the test falls back to a shallow clone root under TMP. Before, it skipped.
- The test always asserts, with real git, that `MODULE.git_show(PUB, long_rel)` equals `git show PUB:long_rel --`. It runs in a `--shared` clone with `core.longpaths=false`. The reference call now passes `cwd=clone` explicitly, because the `git()` helper defaults to the repository root.
- The executor's commit (66248f4) still asserted that the "Filename too long" failure reproduces without `--`, but only after checking that condition, so the assertion could never fail. The orchestrator removed it in 72a5c06. On Windows with a deep root, the equality assertion under `core.longpaths=false` still shows that `--` works.
- No changes to conftest.py, the CI workflow, any builder, or the notice JSON, Markdown or schema.

## Verification (EMS_FAIL_ON_SKIP=1)

- **Executor worktree:** natively, 1 passed and 0 skipped. With `sys.platform` forced to `linux` through a scratchpad plugin, 1 passed. The reproduction branch was exercised: the clone root was 157 characters and git exited 128 with "Filename too long".
- **Main checkout after 72a5c06:**
  - Before Git's `sh.exe` began crashing, the targeted selection (deep root, double dash, error hint) passed 5 times, and the deep-root test passed with the platform forced to `linux`.
  - The skip guard test file gave 23 passed.
  - The builder's `--validate` printed PASS.
  - `grep "pytest.skip|skipif"` on the test file finds nothing.
  - ruff reports the same 6 findings as the base, so there is no regression.
- **Full notice file:** 95 passed and 3 failed. All 3 failures come from local `git clone` calls, which now crash on this machine. Git's bundled `sh.exe` reports `fatal error - add_item ... errno 1` (see STATE.md Environment), and a plain `git clone --shared` outside pytest fails the same way 4 out of 4 times. Two of the failing tests (`test_live_*`) existed before this change. This is an environment problem, not a test regression. In the executor's worktree run, the only full-file failure was a CRLF checkout artefact in the worktree.
- **Not yet run:** the CI run on ubuntu. It needs a push and a `workflow_dispatch` run.
