---
phase: 11-frozen-validators
plan: 01
subsystem: archive-assessment
tags: [reply, frozen-validator, tests, hayes]
requires: [AA3 2.0.1 publication 31addfa, record 4d9b7c1, reply schema 7debe4a]
provides: [reply builder with no live-publisher dependency, D-02 literal-vs-blob tests, D-11 AST and mutation tests]
affects: [Plan 11-02 notice freeze (same pattern), Phase 12 publisher edits (reply stays green)]
key-files:
  created: []
  modified:
    - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
    - tests/test_archive_assessment_demo3_w1_req_001_reply.py
    - tests/test_archive_assessment_applicability_authority_v2_publication.py
requirements: [FROZEN-01]
requirements-completed: [FROZEN-01]
decisions:
  - "Reply validate_signoff is the 2-arg form from 31addfa (frozen on 2.0.1 semantics), not the live 4-arg 2.0.2 form"
  - "D-06: --push-check removed from the reply (network-dependent, live remote state, unused by CI, a frozen validator must be hermetic)"
  - "REPLY_SCHEMA_COMMIT = 7debe4aa544b425f2b80306a8510bfe74e568bae; schema read via a fixed REPLY_SCHEMA_REL so tests that redirect REPLY_SCHEMA still work"
completed: 2026-11-14
---

# Phase 11 Plan 01: Freeze the DEMO3 reply validator on 2.0.1 Summary

The reply builder now holds every 2.0.1 publisher value and helper it needs as local code. It checks its schema against the frozen blob at 7debe4a and offers only `--validate`. Tests prove the local literals equal the 31addfa publisher blob. They also show that a mutated live publisher cannot change the result.

## Tasks

1. **Builder freeze** (`scripts/build_archive_assessment_demo3_w1_req_001_reply.py`):
   - Removed `importlib.util`, the `_spec`/`V2` loader and every `V2.` use.
   - Copied these from the 31addfa blob: `AUTHORITY`, `SCHEMA`, `GOVERNANCE_DECISIONS(_REL)`, `REQUEST_CONTROL_IDS`, `DECISIONS`, `DECISION_STATES`, `VERSION='2.0.1'`, `AUTHORITY_ID`, `OUT`, `SIGNOFF`, `PUBLICATION_RECORD`, `APPROVER`, `APPROVER_ROLES`, `SIGNOFF_ROLE`, `DUAL_ROLE_STATEMENT`, `N_TRACE`, `N_MANIFEST` (plus `REGISTRY`/`SCHEMAS`), and the helpers `AuthorityError`, `lf_bytes`, `load`, `contains_absolute`, `jtext`, `rel`, `latest_records`, `is_date`, `validate_signoff` (2-arg) and `rule_text`.
   - Copied `git_show`, `GitHistoryError` and `bad_rel` from ae15c74 as generic helpers (D-03). They are outside the D-02 scope. `git_show` errors keep `git show failed`, name the full SHA and append `; fetch full history (git fetch --unshallow)`.
   - Added `REPLY_SCHEMA_COMMIT` and `frozen_schema()`, and deleted `schema()`.
   - `validate_reply` requires the committed schema bytes to equal the blob.
   - `resolve_record_commit` now checks `cat-file` and ancestry for the record, publication and schema commits, and its errors name the full SHA.
   - The CLI keeps `--validate` only. Removed `--build`, `--emit-schema`, `--push-check`, `push_check()`, `PUSH_*` and `import sys`.
2. **Tests**:
   - Reply test file:
     - Removed the `V2` alias, so `AuthorityError` is now `MODULE.AuthorityError`.
     - Patches now target `MODULE.git_show`.
     - Added local `dump`/`write_text` for temp files.
     - Replaced `MODULE.schema()` with `frozen_schema()`.
   - Added a D-02 blob loader `frozen_publisher(commit)`, which fails with `pytest.fail` naming the commit, path and "fetch full history". It drives these equality tests against the 31addfa blob:
     - 20 constants;
     - `rule_text` on the 3 real rules plus a 2-condition synthetic rule;
     - `latest_records` on the real decisions, `supersedes` as str and as list, and an empty doc;
     - `validate_signoff` on the real signoff, 14 mutations, a wrong digest and non-dict inputs, comparing the exception class name and text;
     - `contains_absolute` on 11 values;
     - `jtext`, `lf_bytes` and `rel`.
   - D-11 tests:
     - Static: an AST scan of the builder.
     - Non-vacuity: a check that the scanner flags the old loader source.
     - Behavioural: the test execs the live publisher and mutates `PREV_COMPARED_KEYS`, `DUAL_ROLE_STATEMENT`, `rule_text`, `REQUEST_CONTROL_IDS`, and makes `validate_signoff`, `git_show` and `latest_records` raise. It installs the copy under both module names and patches `spec_from_file_location` for the publisher path. It asserts the old loader line now yields the mutated module, then fresh-loads the builder and gets PASS.
   - Removed `test_validate_independent_of_live_version`, the 7 push-check tests (`test_push_check_status` x5, `_binds_to_reply_publication_commit`, `_cli_exit_code`) and `fake_git`.
   - Rewrote the CLI test:
     - `--build`, `--emit-schema` and `--push-check` exit 2. With `--validate` added, each is reported as `unrecognized arguments`. Alone, each leaves the required group empty.
     - `--validate` prints PASS.
     - Bytes of the 5 frozen paths (reply JSON, MD, schema, sign-off, publication record) are unchanged.
   - `test_frozen_constants_match_git` now also checks that `REPLY_SCHEMA_COMMIT` exists and is an ancestor of HEAD, and that the blob equals the committed schema and `frozen_schema()`.
   - Moved `test_publisher_still_valid_and_digest_matches_manifest` to the publication test file, where it uses that file's own `MODULE` (Pitfall 1).

## Deliberate literal difference (D-02)

The reply's `validate_signoff` is the 31addfa 2-arg form `validate_signoff(record, authority_lf_digest)`, called as `validate_signoff(signoff, record['authority_sha256'])`. The pre-freeze builder called the live 4-arg 2.0.2 form with `authority_id`/`version` keywords. That meant the reply depended on 2.0.2 publisher semantics. Freezing on 2.0.1 is the intended meaning of "frozen on 2.0.1". The committed reply bytes are unchanged, because the validated sign-off and record are 2.0.1. The D-02 test proves the 2-arg form equals the blob.

## D-06: --push-check removed

`push_check()` ran `git ls-remote origin`, so its result depended on the network and on live remote state. It only reported whether the already-sent 2.0.1 publication commit was on the remote branch. CI and scripts do not use it, and a frozen validator should be hermetic. `REMOTE_BRANCH` stays, because `build_reply` writes it into `send_condition`.

## Verification

- `python -I scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate` printed PASS from a clean cwd (`%TEMP%`). `--build`, `--emit-schema` and `--push-check` each exit 2.
- `grep -c "V2\|importlib\|publish_archive_assessment_applicability_authority"` on the builder prints 0.
- Targeted run (`-k "archive_assessment and (reply or published or publisher)"`, basetemp `.pytest-temp/p11-1-exec-b`): 113 passed, 0 failed, 0 skipped (204 deselected).
- Full run (`pytest tests -k archive_assessment -rs`, basetemp `.pytest-temp/p11-1-exec-full`): **807 passed, 0 failed, 0 skipped** (7 deselected). The baseline was 770.
- All six workflow validator commands print PASS: the publisher `--validate`, governance decisions `--validate`, rule proposals `--validate` and `--validate-record`, reply `--validate` and notice `--validate`.
- `git diff --stat` over the publisher, `docs/DEMO3_W1_REQ_001_REPLY.md`, `registry/archive_assessment_demo3_w1_req_001_reply.json` and `schemas/archive_assessment_demo3_w1_req_001_reply.schema.json` is empty.
- Non-vacuity probe (temporary, removed): I loaded the HEAD (pre-freeze) builder under the same mutation test. It failed with `AuthorityError: mutated live publisher was called`, and the AST scanner flagged it (`import importlib.util`, `call spec_from_file_location`, `name V2`).
- A4: the new `match=`/err strings (`unrecognized arguments: --X`, `one of the arguments --validate is required`, `mutated live publisher`) were confirmed by running them.

## Deviations from Plan

1. **[Rule 1 - Bug] Fixed schema path for the frozen-schema read.** `REPLY_SCHEMA_REL` is a fixed repo-relative constant instead of `rel(REPLY_SCHEMA)`. Tests redirect `REPLY_SCHEMA` to a temp file outside ROOT, where `rel()` would raise `ValueError` instead of the intended `reply schema differs` error. A test asserts `REPLY_SCHEMA_REL == rel(REPLY_SCHEMA)`.
2. **CLI test assertion shape.** Argparse reports a removed flag on its own as "one of the arguments --validate is required", not as unrecognised, because the required-group check fires first. The test therefore adds `[flag, '--validate']` cases, which prove each removed flag is `unrecognized`. Every case still asserts exit code 2.
3. The plan mentioned "8 push-check tests". The file held 7 test items (5 parametrised `test_push_check_status`, plus `_binds_...` and `_cli_exit_code`), and all were removed.
4. `resolve_record_commit` now checks all three frozen commits (record, publication, schema). The plan asked for the schema and publication commits to be added, and this also covers Pitfall 8. The error text changed from "the frozen publication record commit ..." to "the frozen commit <full sha> ...". No test matched the old text.

No commits were made, and nothing was staged. The orchestrator commits by explicit path with `feat(11-01): freeze the DEMO3 reply validator on 2.0.1`.

## Self-Check: PASSED

- The three modified files exist and show in `git status` as ` M`.
- The frozen reply/schema/publisher bytes show no diff.
