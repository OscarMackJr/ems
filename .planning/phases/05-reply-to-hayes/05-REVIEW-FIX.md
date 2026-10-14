---
phase: 05-reply-to-hayes
fixed_at: 2026-10-14T20:10:00Z
review_path: .planning/phases/05-reply-to-hayes/05-REVIEW.md
iteration: 1
findings_in_scope: 7
fixed: 7
skipped: 0
status: all_fixed
---

# Phase 5: Code Review Fix Report

**Fixed at:** 2026-10-14T20:10:00Z
**Source review:** .planning/phases/05-reply-to-hayes/05-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 7 (WR-01..WR-07; fix_scope critical_warning, so IN-01..IN-06 were not attempted)
- Fixed: 7
- Skipped: 0

The publisher script, the v2 schema and every published registry and generated file are unchanged (D-17). Only the reply generator, its test, and the regenerated `docs/DEMO3_W1_REQ_001_REPLY.md` (WR-04) were modified. The reply JSON and the reply schema did not change. Nothing was pushed.

## Fixed Issues

### WR-01: Mutation tests are tautological and never exercise the real validator

**Files modified:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py`
**Commit:** ad46d43
**Applied fix:** Removed `rejected()` and its `reply != build()` fallback. Added `assert_validate_rejects()`. It writes the mutated reply into a module-level `TemporaryDirectory`, points `MODULE.REPLY_JSON` at that file and requires `validate_reply()` to raise `reply JSON differs from a fresh build`. The swapped-AA4-id, `KNOWN_TRUE` rule-flip and zeroed `authority_sha256` tests now use it. A positive control test checks that an unmutated reply passes the same temp-file path.

### WR-02: `--validate` does not anchor the sign-off or the decision records

**Files modified:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, `tests/test_archive_assessment_demo3_w1_req_001_reply.py`
**Commit:** 3f3586e
**Applied fix:** `build_reply` now calls `V2.validate_signoff(signoff, record['authority_sha256'])`. A new `load_inputs()`, used by both `--build` and `--validate`, does three checks:
- the publication record's manifest digest matches the manifest;
- the sign-off LF digest matches its manifest entry;
- the decision-traceability file matches its manifest entry, and the governance decision records' LF digest equals every `decision_record_sha256` in that traceability.

New tests: an edited rationale is rejected with `decision records differ`, and a sign-off with a swapped role is rejected with `sign-off differs`. Both use temp copies, so no real file is touched.

### WR-03: The committed reply schema is never compared with `schema()`

**Files modified:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, `tests/test_archive_assessment_demo3_w1_req_001_reply.py`
**Commit:** a589550
**Applied fix:** `validate_reply()` now requires the LF bytes of `schemas/archive_assessment_demo3_w1_req_001_reply.schema.json` to equal `jtext(schema())`. A new test checks that a loosened temp copy of the schema is rejected.

### WR-04: The prose claim "No control resolves until..." contradicts the published resolution table

**Files modified:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, `tests/test_archive_assessment_demo3_w1_req_001_reply.py`, `docs/DEMO3_W1_REQ_001_REPLY.md` (regenerated)
**Commit:** feb8e19
**Applied fix:** The sentence was reworded as the authority decided. It now reads: "Hayes's resolver resolves no control until the target description carries the eight classification facts; under the EMS resolution table alone, a control with NO_RULE_WILL_BE_PUBLISHED is applicable whatever the facts."
- The reply was regenerated with `--build`. Only line 68 of the Markdown changed, and the reply JSON is unchanged.
- The test now asserts that the old sentence is gone and the new one is present. The forbidden-word check still passes, and the reply stays unsigned.
- **Status:** fixed. The wording is the authority's chosen text. It still needs the authority's read-through before sending, as already tracked in 05-HUMAN-UAT.

### WR-05: Generated-file validation test skips silently when the reply is missing

**Files modified:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py`
**Commit:** d4b17b7
**Applied fix:** Removed the `skipif` decorator from `test_real_reply_files_validate`. If the committed reply is missing, the test now fails through `validate_reply()`'s "not generated" error.

### WR-06: `--push-check` always exits 0

**Files modified:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, `tests/test_archive_assessment_demo3_w1_req_001_reply.py`
**Commit:** f8655d3
**Applied fix:** `push_check()` now returns a status, and `main()` calls `sys.exit` with it:
- 0: the commit is on the remote;
- 1: the commit is NOT on the remote;
- 2: UNKNOWN. This covers an `ls-remote` failure or no remote tip, a remote tip that is not present locally, and any `merge-base` exit other than 0 or 1, including 128.

The check still never pushes or fetches. New tests use a fake `git` and cover all five paths plus the CLI exit code. A live run on this machine prints UNKNOWN (the branch is not on the remote) and exits 2, which is correct.

### WR-07: `first_sentence` breaks on abbreviations and ignores newline sentence breaks

**Files modified:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, `tests/test_archive_assessment_demo3_w1_req_001_reply.py`
**Commit:** c3dad63
**Applied fix:** The split is now `(?<=\.)\s+(?=[A-Z])`, so a newline counts as a sentence break. The function raises `AuthorityError` in four cases:
- the result is empty;
- the result contains a newline or a carriage return;
- the result does not end with a period;
- the result ends with e.g., i.e., etc. or vs.

New tests:
- positive cases for a normal split, a newline split and a single sentence;
- fail-closed cases for an abbreviation, a mid-sentence newline, text with no period, and empty text.

All 21 current rationales still cut to the same sentence, so `--build` produced no change.
- **Status:** fixed: requires human verification. This is a logic change to how sentences are cut. Please confirm that the fail-closed conditions match the intended D-12 behaviour.

## Final verification (run in the main working tree after the fast-forward to c3dad63)

- `python scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate`: PASS
- `python scripts/publish_archive_assessment_applicability_authority_v2.py --validate`: PASS
- `python -m pytest tests/test_archive_assessment_demo3_w1_req_001_reply.py tests/test_archive_assessment_applicability_authority_v2_publication.py -q --basetemp=C:/temp/pytest-fix-tmp`: 86 passed, 0 skipped. The real-file test and the git-gated SHA tests all ran.
- These three files are still modified-and-unstaged, untouched and outside every commit:
  - `registry/adjudication_rules.json`
  - `registry/policy_decisions.json`
  - `schemas/archive_assessment_governance_answers.schema.json`

  The untracked files were not touched either.

---

_Fixed: 2026-10-14T20:10:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
