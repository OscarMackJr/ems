---
phase: 11-frozen-validators
verified: 2026-11-16T04:46:55Z
status: passed
score: 15/15 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 13/15
  gaps_closed:
    - "The CI archive-assessment job fails if any test is skipped (11-03 T3; D-10). Collection-level skips now become collection errors under EMS_FAIL_ON_SKIP=1"
    - "03-T2 opt-out reach (WR-02). Was UNCERTAIN; recorded as accepted in the 11-05 decisions (fail-closed D-08 convenience)"
  gaps_remaining: []
  regressions: []
---

# Phase 11: Frozen Validators Verification Report

**Phase Goal:** The DEMO3 reply validator and the 2.0.2 notice validator are frozen, so later publisher edits cannot change their results and a missing pinned blob is never silently skipped.
**Verified:** 2026-11-16T04:46:55Z
**Status:** passed
**Re-verification:** Yes, after gap closure plans 11-05 and 11-06

## Goal Achievement

### Re-check of the previous BLOCKER (11-03 T3 / FROZEN-03 net)

`tests/conftest.py:24-32` now has a `pytest_make_collect_report` hookwrapper. When `EMS_FAIL_ON_SKIP=1` and the collect report is skipped, the hook sets `outcome='failed'` and the guard message.

I reproduced the previous failing probe independently: scratch copies of the real `tests/conftest.py` and `tests/aa_history.py`, the exact CI form `pytest t -k archive_assessment`, one module calling `pytest.importorskip("no_such_mod_xyz")` and one calling `pytest.skip(..., allow_module_level=True)`.

| Run | Result | Exit |
|-----|--------|------|
| Guard on (`EMS_FAIL_ON_SKIP=1`) | `ERROR ... skipped test treated as failure (EMS...` x2, `Interrupted: 2 errors during collection` | 2 |
| Guard unset | `1 passed, 2 skipped` | 0 |

Previously the guarded run gave `1 passed, 2 skipped`, exit 0. **The gap is closed.** Imperative `pytest.xfail()` is still reported as `xfailed`, not `skipped`. The 11-05 decision accepts this, and it falls outside the literal "any skipped test" wording.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC1 | Reply and 2.0.2 notice validators import no live publisher constants or functions. Mutating `PREV_COMPARED_KEYS`, `DUAL_ROLE_STATEMENT`, `validate_signoff` and `rule_text` leaves both results unchanged | VERIFIED (regression) | Both builders import only stdlib and `jsonschema`. grep for `publish_archive`, `importlib`, `runpy` and `exec(` in either builder finds nothing. The builders are byte-identical since 1145cc9 (`git diff --stat 1145cc9 HEAD -- scripts` is empty). The `test_validate_*_passes_with_a_mutated_live_publisher` tests (reply L782, notice L747) are present and inside the orchestrator's 918-pass run |
| SC2 | When a pinned blob is unreachable, tests and validators fail with an explicit error and do not skip | VERIFIED | `aa_history.require_history` calls `pytest.fail` by default. `history_problem` is now fail-closed on any shallow output other than `false` (L25, WR-04). No `skipif`, `needs_git`, `gated`, `pytest.skip`, `importorskip` or `allow_module_level` appears in `tests/test_archive_assessment_*.py` outside the skip_guard fixtures. Skip-guard cases for missing history pass |
| SC3 | Pytest validates the committed notice files, and each notice test goes red when its named check breaks | VERIFIED (regression) | `test_committed_notice_files_validate` at notice L83. The test files changed by only one comment line since 1145cc9 |
| SC4 | Completed before any publisher edit; historical reply and 2.0.2 notice stay green | VERIFIED | `git diff --stat 5f807d4 HEAD -- scripts/publish_archive_assessment_applicability_authority_v2.py registry schemas docs` is empty. The only diffs are the two frozen builders, which are this phase's own work. I ran `reply --validate` (PASS, exit 0) and `notice --validate` (PASS, exit 0). The uncommitted `registry/adjudication_rules.json` and `registry/policy_decisions.json` edits are pre-existing unrelated work, not committed |
| 01-T1 | Reply builder has zero live-publisher references | VERIFIED (regression) | grep is clean; scanner test at reply L740 |
| 01-T3 | Local literals and functions equal the 31addfa blob | VERIFIED (regression) | Builder unchanged; equality tests unchanged |
| 01-T4 | Reply CLI can no longer write frozen files | VERIFIED (regression) | Builder unchanged |
| 02-T1 | Notice builder has zero live-publisher references | VERIFIED (regression) | Test at notice L704 |
| 02-T3 | Notice literals and functions equal the ae15c74 blob | VERIFIED (regression) | Builder unchanged |
| 02-T4 | Notice CLI offers `--validate` only | VERIFIED (regression) | Builder unchanged |
| 03-T2 | `git_ready` failures fail by default; `EMS_ALLOW_NO_HISTORY=1` restores a skip for offline local runs | VERIFIED (limited reach, accepted) | Fail-by-default holds. The opt-out skips the `require_history` callers, and `test_missing_history_skips_with_opt_out_only` passes. Its limited reach (WR-02) is fail-closed and is recorded as an accepted decision in 11-05. No FROZEN requirement depends on it |
| 03-T3 | The CI archive-assessment job fails if any test is skipped | VERIFIED (gap closed) | See the re-check above. The CI step `.github/workflows/ems-validate.yml:87-90` still sets `EMS_FAIL_ON_SKIP: '1'` |
| 03-T4 | No collection-time skipif/needs_git/gated guard remains | VERIFIED | grep is clean |
| 04-T3 | `test_changed_row_blocks_no_decision_changed` asserts that `build_notice` raises | VERIFIED (regression) | Test file unchanged |
| 04-T4 | No REJECTS tuple remains | VERIFIED (regression) | Unchanged |

Gap-closure must-haves (11-05) are all VERIFIED. Module `importorskip` and module skip under the guard exit non-zero with `1 error` and the guard message. Without the guard they exit 0 and report skipped. The shallow check requires exactly `false`. The full run shows 0 skipped (orchestrator: 918 passed, 7 deselected, exit 0).

Gap-closure must-haves (11-06, WR-03 wording) are VERIFIED. Reply test L423 and 11-04-SUMMARY L105/L175 now say "called via build_reply, after the pinned reads in load_inputs", which matches the builder at L177.

**Score:** 15/15 verified

### Key Link Verification

| From | To | Via | Status |
|------|----|-----|--------|
| `.github/workflows/ems-validate.yml` | `tests/conftest.py` | `EMS_FAIL_ON_SKIP: '1'` on the Archive-assessment tests step | WIRED (both hooks are now effective) |
| `tests/conftest.py` | `EMS_FAIL_ON_SKIP` | `os.environ` check in the runtest and collect hooks | WIRED |
| reply/notice tests | 31addfa / ae15c74 publisher blobs | `frozen_publisher` (test-only) | WIRED (unchanged) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Collection skips fail under the guard | scratch probe (above), guard on | 2 errors, exit 2 | PASS |
| Opt-out preserved without the guard | same probe, guard unset | 1 passed, 2 skipped, exit 0 | PASS |
| Skip-guard suite | `EMS_FAIL_ON_SKIP=1 .venv/Scripts/python.exe -m pytest tests/test_archive_assessment_skip_guard.py --basetemp=.pytest-temp/verify11-rr-skipguard -p no:cacheprovider -q` | 22 passed, pytest exit 0 | PASS |
| Reply validator | `python scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate` | PASS, exit 0 | PASS |
| Notice validator | `python scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py --validate` | PASS, exit 0 | PASS |
| Full archive suite under the guard | orchestrator: `EMS_FAIL_ON_SKIP=1 pytest tests -k archive_assessment` | 918 passed, 7 deselected, 0 skipped, exit 0 | PASS |
| WR-05 side effect | scratch probe: a non-archive module with module-level `importorskip`, `-k archive_assessment` | 1 error, Interrupted, exit 2 | Confirmed (fail-closed, advisory) |

### Probe Execution

Step 7c: no `scripts/*/tests/probe-*.sh` is declared for this phase. Not applicable.

### Requirements Coverage

| Requirement | Plan | Status | Evidence |
|-------------|------|--------|----------|
| FROZEN-01 | 11-01 | SATISFIED | SC1, 01-T1, 01-T3, reply mutation test |
| FROZEN-02 | 11-02 | SATISFIED | SC1, 02-T1, 02-T3, notice mutation test covering all four named items |
| FROZEN-03 | 11-03, 11-05 | SATISFIED | SC2, 03-T3 now closed, WR-04 fail-closed shallow check |
| FROZEN-04 | 11-04, 11-06 | SATISFIED | SC3 |

No requirements are orphaned. REQUIREMENTS.md maps exactly FROZEN-01 to FROZEN-04 to Phase 11. The traceability table still shows FROZEN-01, -02 and -04 as "Pending" (L79-82) and the checkboxes at L18, 19 and 21 as unticked. The orchestrator should update both when it closes the phase.

### WR-05 Assessment: advisory, does not block

WR-05 is confirmed. The collect hook converts a skipped `CollectReport` in **any** collected module. The CI step collects all of `tests/` before `-k` deselection, so a module-level skip in an unrelated module interrupts the archive job (exit 2) and hides every archive result.

It does not block the phase goal, for three reasons:

1. It is fail-closed. It can produce a false red but never a false green. The goal ("never silently skipped") and FROZEN-03 are about false greens.
2. No module in `tests/` uses `importorskip` or `allow_module_level` today (grep is clean), and the orchestrator's guarded run is green. The gate is not red now.
3. The risk is operational, not correctness: unrelated future work could turn the Hayes-facing gate red with no archive cause.

Recommended follow-up, for example before Phase 12 opens its red window: either narrow the CI step to `tests/test_archive_assessment_*.py`, or limit the conversion to `archive_assessment` node IDs. Add a skip-guard case for a deselected skipping module. Treat IN-08 (the opt-out hint over-promises) and IN-09 (the shallow message omits the observed output) as polish.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| tests/conftest.py | 24-32 | Collect hook is not scoped to archive modules (WR-05) | Warning | Fail-closed false-red risk from unrelated modules |
| tests/aa_history.py | 10 | HINT advertises an opt-out with limited reach (IN-08) | Info | Operator confusion |
| tests/aa_history.py | 25-26 | Message omits the observed shallow output (IN-09) | Info | Diagnostics only |

No TBD, FIXME or XXX markers are in the files modified by 11-05 or 11-06.

### Human Verification Required

None.

### Gaps Summary

There are no gaps. The previous BLOCKER is closed: collection-level skips under `EMS_FAIL_ON_SKIP=1` now fail the run, which I reproduced independently. Both validators remain frozen and pass, the publisher, registry, schemas and docs are untouched since 5f807d4, and the full guarded archive suite reports 918 passed with 0 skipped. WR-05 is an advisory, fail-closed warning and is recommended for follow-up before Phase 12.

---

_Verified: 2026-11-16T04:46:55Z_
_Verifier: Claude (gsd-verifier)_
