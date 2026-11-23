---
status: complete
quick_id: 261122-v8y
requirements: [SEC-03]
requirements-completed: [SEC-03]
---

# Quick Task 261122-v8y Summary

SEC-03 done outside Phase 17: the CI secret-pattern scan now covers `*.md` files. Hayes 2.0.3 pin decision (Oscar Mack, 2026-11-22, option 3) recorded in STATE.md.

## Files written

- `.github/workflows/ems-validate.yml`: removed `--exclude='*.md'` from the secret-pattern grep; `secret_pattern=` unchanged
- `tests/test_archive_assessment_ci_workflow.py` (new, in the CI glob, no skips): no md exclusion or include restriction; pattern line byte-equal; no tracked `.md` matches (`git grep -nE`, POSIX ERE parity with CI); positive control in a temp repo
- `.planning/STATE.md`: decision line, `[Hayes pin 2.0.3]` concern, quick task row
- `.planning/quick/261122-v8y-sec-03-secret-scan-covers-md/` PLAN and SUMMARY

## Verification

- New module: 4 passed, 0 skipped (`EMS_FAIL_ON_SKIP=1`)
- Workflow YAML parses; `git grep -nE <secret_pattern> -- '*.md'` exits 1 (no match)
- No archive-assessment script references the workflow, so no certified path changes
- Full archive-assessment suite (`EMS_FAIL_ON_SKIP=1`): 1144 passed, 4 failed. On re-run of the failing module, 3 passed (local `git clone` sh.exe crash, known environmental). The remaining failure, `test_committed_notice_files_validate`, is a local working-copy EOL state: `registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json` and `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md` are `i/lf w/crlf` (rewritten locally 2026-11-19 20:31). The committed blobs are LF; CI is unaffected. Not caused by this task and not changed by it.

## Deviations

- Done inline in the main session.
- `.gitattributes` (D-09a) and the 17-BASELINE-RED ledger from plan 17-01 not done; they stay with the deferred Phase 17.
