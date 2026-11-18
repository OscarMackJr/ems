---
phase: 16-test-robustness-and-review-closure
status: complete
requirements: [GATE-13, GATE-14, GATE-15, BASE-04]
counts:
  fixed: 11
  closed: 1
  deferred_17: 5
  deferred_19: 1
  superseded: 2
---

# Phase 16 Review Closure Ledger

Recorded: 2026-11-18, HEAD 5d76958

One row per selected review info item from the phase 11, 12, 14 and 15 REVIEW files (decision D-09). Dispositions:

- FIXED: changed in Phase 16 and covered by a named test.
- CLOSED: not changed, with a recorded reason.
- DEFERRED-17 / DEFERRED-19: carried to Phase 17 / Phase 19 as tracked work; not done in Phase 16.
- SUPERSEDED-BY-SEC-0x: made unnecessary or covered by a Phase 17 security requirement.

Historical REVIEW files are not edited. The frozen reply (2.0.1) and 2.0.2 notice builders and the publisher are byte-unchanged by Phase 16.

| Item | Disposition | Reason | Evidence |
|------|-------------|--------|----------|
| 11 IN-08 | FIXED | The history-failure HINT now says what `EMS_ALLOW_NO_HISTORY=1` actually skips. The code is `tests/aa_history.py`, a test helper, so nothing lands only in a frozen builder. | 8dd3778 (HINT text); c1cec3a (regression test `test_hint_says_opt_out_only_skips_guarded_tests` in `tests/test_archive_assessment_skip_guard.py`) |
| 11 IN-09 | FIXED | An unrecognised shallow-check output is reported verbatim as a problem. | 8dd3778; c1cec3a (`test_history_problem_unrecognised_shallow_output_is_problem`) |
| 12 IN-01 | DEFERRED-17 | Plain-mode error message is publisher text. No publisher edit in Phase 16 (D-04); Phase 17 makes it with a test inside its red window. | Phase 17 criterion (ROADMAP); 16-CONTEXT D-04 |
| 12 IN-02 | DEFERRED-17 | "HEAD is the publication commit" diagnosis is publisher text (D-04). | Phase 17 criterion (ROADMAP); D-04 |
| 12 IN-03 | DEFERRED-17 | At-pin wrong-record error pointing to plain mode is publisher text (D-04). | Phase 17 criterion (ROADMAP); D-04 |
| 12 IN-04 | DEFERRED-17 | Shallow check before history reads is publisher ordering (D-04). | Phase 17 criterion (ROADMAP); D-04 |
| 12 IN-05 | SUPERSEDED-BY-SEC-04 | Literal pathspecs are required by SEC-04 (git seam isolation). Phase 17 verification confirms (D-05). | REQUIREMENTS SEC-04; D-05 |
| 12 IN-06 (digest-check placement) | DEFERRED-17 | Moving the `lf_digest(SCRIPT)` check is a publisher edit (D-04). | Phase 17 criterion (ROADMAP); D-04 |
| 12 IN-06 (decisions-builder scope) | SUPERSEDED-BY-SEC-02 | The pinned decisions-builder blob gets a manifest digest checked by `--validate` under SEC-02 (D-05). | REQUIREMENTS SEC-02; D-05 |
| 12 IN-07 (test parts) | FIXED | Reply test `cat_exc` match fixed; the source-grep in `test_at_pin_binding_reads_supersedes_from_authority` removed (behavioural test remains). | c1cec3a (`tests/test_archive_assessment_demo3_w1_req_001_reply.py`, `tests/test_archive_assessment_applicability_authority_v2_publication.py`) |
| 12 IN-07 (reply-builder message) | CLOSED | The weak message is in the frozen reply builder, which must stay byte-unchanged (D-06). | Reply builder byte-unchanged (range diff in 16-05) |
| 14 IN-01 | FIXED | Unused `pinned_raw_digest` removed; `EXPECTED_LINEAGE_COMMIT` added and a differing lineage commit raises `AuthorityError`; `CATALOG_COMMIT` now used. | e7d60ff; 66c2b23; `test_lineage_entries_fails_when_commit_differs_from_expected`, `test_expected_lineage_commit_covers_the_pinned_exceptions`, `test_frozen_constants_match_git` |
| 14 IN-02 | FIXED | Malformed or missing pinned input and decode errors raise `AuthorityError`; history errors keep their type with baseline context. | e7d60ff; `test_malformed_pinned_input_raises_authority_error`, `test_missing_key_in_pinned_input_raises_authority_error`, `test_pinned_history_error_is_reraised_as_history_error_with_baseline_context` |
| 14 IN-03 | FIXED | `--build` validates in memory, stages temp files, replaces all three outputs atomically (schema included) and validates. Output byte-identical to the sent notice (D-02 gate in 16-02). | e7d60ff; `test_failed_build_validation_leaves_no_partial_files`, `test_build_writes_all_three_files_atomically_and_matches_fresh_build` |
| 14 IN-04 | FIXED | The notice rule dict is a deep copy of the authority rule. | e7d60ff; `test_built_rule_is_a_copy_of_the_authority_rule` |
| 14 IN-05 | FIXED | The always-true containment assertion in `test_pinned_run_paths_stay_in_temp_materialisation` was deleted (not strengthened). The always-true containment half is covered by the live-tamper tests. | e7d60ff; 66c2b23; `test_live_data_file_edit_does_not_change_notice`, `test_live_publisher_and_decisions_builder_edit_does_not_change_notice` |
| 15 IN-01 | DEFERRED-19 | Closed for 2.0.3: the sent text is immutable (D-03), so the absolute Windows example text in the registry JSON stays. The 2.0.4 notice builder must avoid absolute-path example text and scan the whole string in `contains_absolute`. | Phase 19 criterion (ROADMAP); D-03 |
| 15 IN-02 | FIXED | Duplicated hint test removed; folded into one test. | 66c2b23 (`test_git_show_error_names_full_sha_and_fetch_hint`) |
| 15 IN-03 | FIXED | Missing git binary hint says to install git and put it on PATH, not to fetch history. | e7d60ff (`test_git_show_missing_git_hint_says_install_not_fetch`) |

## Related records

- D-01: the 2.0.3 notice was sent at 91d8847 (confirmed by the EMS governance authority on 2026-11-18). It is captured here only. The committed artifact that records the sent commit is Phase 19 NOTICE-05.
- D-08a: the D-10 baseline test (rewritten in 04e5ff6) joins Phase 17's accepted red-set inventory at the first publisher edit and closes at the 2.0.4 publication. It is not weakened. The same red window is recorded in the ROADMAP Phase 17 criteria.
- 16-04 (850f0da) closed BOOK-01 and 16-01 (04e5ff6, c1cec3a) closed BASE-01, BASE-03 and BASE-04; they are not ledger items.
