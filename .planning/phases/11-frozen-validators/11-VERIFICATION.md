---
phase: 11-frozen-validators
verified: 2026-11-14T00:00:00Z
status: gaps_found
score: 13/15 must-haves verified
overrides_applied: 0
gaps:
  - truth: "The CI archive-assessment job fails if any test is skipped (11-03 must-have; 11-CONTEXT D-10: fails if the pytest run reports any skipped test)"
    status: partial
    reason: "The EMS_FAIL_ON_SKIP hook is pytest_runtest_makereport only. A module-level skip (pytest.importorskip or pytest.skip(allow_module_level=True)) produces a CollectReport the hook never sees. Reproduced with copies of the real tests/conftest.py and tests/aa_history.py and the exact CI command: pytest reports '1 passed, 2 skipped' and exits 0."
    artifacts:
      - path: "tests/conftest.py"
        issue: "Hook covers runtest-phase reports only; no pytest_collectreport or session-end check, so collection-level skips pass CI"
      - path: "tests/test_archive_assessment_skip_guard.py"
        issue: "No case for importorskip or allow_module_level skip, so the gap is not detected"
    missing:
      - "Treat a skipped CollectReport as failed under EMS_FAIL_ON_SKIP=1 (pytest_collectreport hook), or fail the session at sessionfinish when the terminal reporter's 'skipped' stats are non-empty"
      - "Add skip-guard subprocess cases for module-level pytest.importorskip and pytest.skip(allow_module_level=True)"
      - "Optional (outside the literal 'skipped' wording): treat imperative pytest.xfail() / xfail(run=False) as a failure under the guard"
---

# Phase 11: Frozen Validators Verification Report

**Phase Goal:** The DEMO3 reply validator and the 2.0.2 notice validator are frozen, so later publisher edits cannot change their results and a missing pinned blob is never silently skipped.
**Verified:** 2026-11-14
**Status:** gaps_found
**Re-verification:** No, initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC1 | Reply and 2.0.2 notice validators import no live publisher constants or functions; mutating `PREV_COMPARED_KEYS`, `DUAL_ROLE_STATEMENT`, `validate_signoff`, `rule_text` leaves both results unchanged | VERIFIED | Both builders import only stdlib and `jsonschema`. No `publish_archive...` path, importlib, exec or runpy. Constants and functions are local (reply L33, 94, 115; notice L24, 31, 103, 125). Every publisher-era input goes through `git_show(<40-hex>, path)`. `mutated_live_publisher()` mutates all four names (notice test L727-730), and `test_validate_*_passes_with_a_mutated_live_publisher` passes in the orchestrator's full run |
| SC2 | Unreachable 2.0.1 or other pinned blob: tests and validators fail with an explicit error, never skip | VERIFIED | `git_show` raises `GitHistoryError('<path>@<sha>: git show failed ...; fetch full history')`. `resolve_record_commit` raises `AuthorityError` naming the full SHA. `aa_history.require_history` calls `pytest.fail` by default. `frozen_publisher` calls `pytest.fail` naming the path and commit. No `skipif`, `needs_git` or `gated` remains in `tests/test_archive_assessment_*.py` (grep). Full suite: 0 skipped |
| SC3 | Pytest validates the committed notice files; each notice test goes red when its named check breaks | VERIFIED | `test_committed_notice_files_validate` (notice L83) runs `validate_notice()` on the repo files with no monkeypatch and asserts `PASS`. Every `pytest.raises` in both files carries `match=`, except schema helpers that assert `validator` and `absolute_path`, the CLI `SystemExit` test (asserts code 2 and the stderr text), and one arity `TypeError` |
| SC4 | Completed before any publisher edit; historical reply and 2.0.2 notice stay green | VERIFIED | `git diff --stat 5f807d4 HEAD -- scripts/publish_archive_assessment_applicability_authority_v2.py registry schemas docs` is empty. Reply and notice `--validate` return PASS (orchestrator) |
| 01-T1 | Reply builder has zero references to the live v2 publisher | VERIFIED | grep shows no publisher name, path or V2 alias. AST and string scanner test at L740, plus a scanner self-test at L744 |
| 01-T3 | Local literals and functions equal the 31addfa publisher blob (D-02); generic helpers are out of scope (D-03) | VERIFIED | `frozen_publisher('31addfa…')` execs the blob in a throwaway module (test-only). Equality tests cover constants, `rule_text`, `latest_records`, `validate_signoff`, `contains_absolute`, `jtext`/`lf_bytes`/`rel` (L596-697) |
| 01-T4 | Reply CLI can no longer write frozen files | VERIFIED | `main()` offers only `--validate` (L359). `test_cli_rejects_removed_and_missing_modes` asserts exit 2 for `--build`, `--emit-schema` and `--push-check`, and that the bytes are unchanged |
| 02-T1 | Notice builder has zero references to the live v2 publisher | VERIFIED | grep is clean. `test_builder_has_no_publisher_reference` is at L704 |
| 02-T3 | Notice literals and functions equal the ae15c74 publisher blob | VERIFIED | Equality tests at L523-649 (constants, identity constants, `rule_text`, `closed_schema_levels`, `validate_signoff`, `contains_absolute`, `bad_rel`, `is_date`, `jtext`/`lf_bytes`/`load`/`rel`) |
| 02-T4 | Notice CLI offers `--validate` only | VERIFIED | L379. The CLI test at L467 asserts exit 2 |
| 03-T2 | `git_ready` failures fail by default; `EMS_ALLOW_NO_HISTORY=1` restores a skip for offline local runs | UNCERTAIN (WARNING) | Fail-by-default holds. The opt-out reaches only tests that call `require_history`: 5 of 53 reply tests and 4 of 51 notice tests. Most reply and notice tests still fail under the opt-out (review WR-02). This is fail-closed, and no FROZEN requirement asks for the opt-out. It is a D-08 convenience |
| 03-T3 | The CI archive-assessment job fails if any test is skipped | FAILED (partial) | Gap: collection-level skips escape. Reproduced; see below |
| 03-T4 | No collection-time skipif/needs_git/gated guard remains | VERIFIED | grep finds matches only inside the skip-guard fixture strings |
| 04-T3 | `test_changed_row_blocks_no_decision_changed` asserts that `build_notice` raises | VERIFIED | Notice L374-381: `pytest.raises(AuthorityError, match='1 of 80 control rows differ…')` around `MODULE.build_notice` |
| 04-T4 | No REJECTS tuple remains | VERIFIED | grep returns nothing in either file |

Merged (restated by roadmap SCs): 01-T2 and 02-T2 into SC1; 01-T5 and 02-T5 into SC4; 03-T1 into SC2; 04-T1 and 04-T2 into SC3.

**Score:** 13/15 verified, 1 failed, 1 uncertain

### Key Link Verification

| From | To | Via | Status |
|------|----|-----|--------|
| reply tests | `31addfa:scripts/publish_..._v2.py` | `frozen_publisher` git show and exec (test-only) | WIRED |
| notice tests | `ae15c74:scripts/publish_..._v2.py` | `frozen_publisher` | WIRED |
| `.github/workflows/ems-validate.yml` | `tests/conftest.py` | `EMS_FAIL_ON_SKIP: '1'` on the Archive-assessment tests step (L87-90) | WIRED (the hook itself is partial; see gap) |
| notice tests | `MODULE.digest_scope_error` / `MODULE.build_notice` | direct calls with an edited `previous` (L332, L374) | WIRED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Collection-level skip under the CI guard | Scratch copy of `conftest.py` + `aa_history.py`, modules with `pytest.importorskip("no_such_mod_xyz")` and `pytest.skip(..., allow_module_level=True)`, `EMS_FAIL_ON_SKIP=1 python -m pytest t -k archive_assessment -p no:cacheprovider -q` | `1 passed, 2 skipped`, exit 0 | FAIL |
| Full suite, reply/notice `--validate`, removed flags | orchestrator evidence | 917 passed / 0 skipped; PASS; exit 2 | PASS |

### Requirements Coverage

| Requirement | Plan | Status | Evidence |
|-------------|------|--------|----------|
| FROZEN-01 | 11-01 | SATISFIED | SC1, 01-T1, 01-T3, reply mutation test |
| FROZEN-02 | 11-02 | SATISFIED | SC1, 02-T1, 02-T3, notice mutation test (all four named items mutated) |
| FROZEN-03 | 11-03 | SATISFIED (literal wording) | Pinned-blob unreachability fails with explicit errors in tests and validators. The broader "CI fails on any skip" plan must-have is the open gap |
| FROZEN-04 | 11-04 | SATISFIED | SC3 |

No orphaned requirements. REQUIREMENTS.md maps exactly FROZEN-01 to FROZEN-04 to Phase 11. The traceability table still reads "Pending", which the orchestrator should update.

### Judgments Requested

1. **WR-01: GAP.** FROZEN-03's literal text covers only unreachable pinned blobs, and that part is met: no archive test currently skips at module level. The phase must-have (11-03 T3) and D-10, however, say the CI job fails if the pytest run *reports any skipped test*. Pytest reports module-level skips as "skipped", and the guard exits 0 on them (reproduced). This truth is therefore literally false, and it is the net meant to protect the Phase 12 red window. The fix is small, test-only, and allowed before Phase 12. Imperative `pytest.xfail()` is reported as "xfailed", not "skipped", so it falls outside the literal wording: WARNING only.
2. **WR-03: the reviewer is correct.** `validate_reply()` → `build_reply()` → `resolve_record_commit()` at `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:177`. The call runs after `load_inputs()`'s pinned `git show` reads (L307-314), which is why d*40 constants surface as `GitHistoryError`. `test_validate_fails_closed_without_history_shallow` (reply test L392) relies on this call: it patches only `git` and gets `shallow` from `validate_reply()`. Documentation to correct:
   - `.planning/phases/11-frozen-validators/11-04-SUMMARY.md` L105 and L175 ("validate_reply does not / never calls resolve_record_commit")
   - `tests/test_archive_assessment_demo3_w1_req_001_reply.py` L423 comment
   - Correct wording: "called via build_reply, after the pinned reads in load_inputs"

   Not a must-have failure (the asserted behaviour is right), but the record is false. WARNING.
3. **WR-02: no requirement demands it.** FROZEN-01 to FROZEN-04 and roadmap SC2 require failing rather than skipping. The opt-out is D-08 operator convenience, and its partial reach is fail-closed. WARNING (UNCERTAIN on 03-T2). It could be closed by an autouse `require_history` fixture in the two files, or accepted.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| tests/conftest.py | 13-21 | Skip guard misses CollectReport and imperative xfail | Blocker (for 03-T3) | CI can pass with unexecuted modules |
| tests/aa_history.py | 49-52 | Unrecognised `--is-shallow-repository` output treated as a full clone (fail-open), unlike builders' `!= 'false'` | Warning | Violates the CLAUDE.md fail-closed rule in a test helper (WR-04) |
| tests/test_archive_assessment_demo3_w1_req_001_reply.py | 423 | False comment about `resolve_record_commit` | Warning | Misleads Phase 12 planning (WR-03) |
| tests/test_archive_assessment_demo3_w1_req_001_reply.py | 472 | `pytest.raises(TypeError)` with no match | Info | Arity check, not a named-guard test |

No TBD, FIXME or XXX markers were found in the phase-modified files.

### Human Verification Required

None.

### Gaps Summary

One gap, test-infrastructure only: the `EMS_FAIL_ON_SKIP` guard does not fail collection-level skips. The phase must-have "CI fails if any test is skipped" is therefore not fully met. The freeze itself (FROZEN-01/02), the skip-to-fail conversion (FROZEN-03 literal) and the test rigor (FROZEN-04) are achieved in code. If the developer decides D-10 meant only runtest-phase skips, accept with an override on 11-03 T3; otherwise close it with a `pytest_collectreport` hook and two skip-guard cases. Independently, correct the WR-03 statements in the 11-04 SUMMARY and the reply test comment.

---

_Verified: 2026-11-14_
_Verifier: Claude (gsd-verifier)_
