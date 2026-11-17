---
phase: 12
slug: verify-at-pin-and-gate-hardening
status: verified
threats_open: 0
asvs_level: 1
created: 2026-11-17
---

# Phase 12 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Audited at HEAD `7a49e84` (branch `feature/ems-aa3-archive-applicability-authority`). The register was authored at plan time (`register_authored_at_plan_time: true`) in the `<threat_model>` blocks of 12-01..12-08-PLAN. Line numbers refer to the files at `7a49e84`. "Publisher" means `scripts/publish_archive_assessment_applicability_authority_v2.py`, "pub tests" means `tests/test_archive_assessment_applicability_authority_v2_publication.py`, and "reply builder" means `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| CI shell → pytest | Bash glob expansion decides which test modules the archive gate runs | Test module paths (integrity-critical) |
| environment → test harness | `EMS_FAIL_ON_SKIP` and `EMS_ALLOW_NO_HISTORY` change the gating | Booleans set by the operator or CI |
| git subprocess output → publisher, reply builder, `aa_history` | rc and stdout of `rev-parse`, `merge-base`, `status`, `ls-files`, `cat-file` and `show` decide clone completeness, ancestry and tree state | Short status strings and pinned blobs (integrity-critical, public) |
| live working tree → publisher `--validate` | The live catalog must not influence pinned validation. At the pin, the working-tree bytes must be the bytes at HEAD | Registry, schema, sign-off, generated outputs, publisher script |
| committed files → publisher `--validate` | The authority, schema, sign-off, manifest and record bytes are untrusted input to the validator | JSON documents (integrity-critical) |
| git index or config → publisher | Index flags (skip-worktree, assume-unchanged) and status config can hide working-tree state from `git status` | Index tags, porcelain lines |
| answers file bytes → decisions validator | Changed answer bytes must remove the D-13 grandfathered-note exemption | Answers digest |
| git history → pinned constants | `SUPERSEDED_V2_0_2` must reflect the real 2.0.2 publication | Commit SHA and digests |
| publisher texts → Hayes | The dry-run text, manifest note and at-pin output are read by the verifier and quoted by the Phase 14 notice | Human-readable claims |
| publication commit → Hayes | The record written in Phase 13 permanently binds the commit Hayes re-pins to | Publication record |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-12-01-01 | Repudiation | archive test silently skipped in CI | mitigate | The `pytest_make_collect_report` hookwrapper (`tests/conftest.py` L29-39) turns a collection-level skip into a failure for any `test_archive_assessment_*` module (`_archive_module`, L24-26) when `EMS_FAIL_ON_SKIP=1`. Subprocess cases: `test_module_importorskip_with_guard_fails` (skip-guard L96) and `test_module_skip_with_guard_fails` (L104), with controls at L121 and L128. CI sets `EMS_FAIL_ON_SKIP: '1'` (`ems-validate.yml` L89). | closed |
| T-12-01-02 | Tampering | CI glob matches nothing or is quoted | mitigate | The run line is unquoted: `python -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q` (`ems-validate.yml` L90). The job runs on `ubuntu-latest` with the default bash (no `nullglob`), so an unmatched pattern reaches pytest as a literal path and fails (exit 4). | closed |
| T-12-01-03 | Spoofing | unrecognised shallow output read as a full clone | mitigate | `history_problem` passes only on exactly `'false'` and reports any other output raw with `!r` (`tests/aa_history.py` L26-31). Tests: `test_history_problem_unrecognised_shallow_output_is_problem[b'', b'maybe', b'true']` (skip-guard L182-197) and the positive control at L199. | closed |
| T-12-01-04 | Repudiation | a skip raised in `conftest.py` is no longer converted | accept | See AR-01. | closed |
| T-12-01-SC | Tampering | package installs (12-01) | accept | See AR-04. | closed |
| T-12-02-01 | Tampering | a live catalog edit changes `--validate` | mitigate | The publisher reads the catalog only from the pinned commit (`catalog_bytes` → `git_show(CATALOG_COMMIT, CATALOG_REL)`, publisher L101). The clone-based outcome-equality test over overwrite and delete is `test_d10_live_catalog_edit_or_delete_does_not_change_validate_outcome` (`tests/test_archive_assessment_lineage_validation.py` L357-377). Because that test is vacuous while validator 1 is red (12-REVIEW WR-03), the in-process `test_d10_live_catalog_edit_or_delete_does_not_change_build_or_validation` (L334-355) supplies the non-vacuous evidence. It runs `validate_publication` before and after the overwrite and the delete. | closed |
| T-12-02-02 | Tampering | changed answers keep the grandfathered-note exemption | mitigate | Real-bytes tests: `test_changed_answers_bytes_remove_exemption` (`tests/test_archive_assessment_governance_answers.py` L121), `test_validate_cli_rejects_note_collision_for_real_changed_answers` (`tests/test_archive_assessment_governance_decisions.py` L215, builder `main()` CLI) and `test_publisher_validate_governance_decisions_rejects_note_collision_for_real_changed_answers` (L231, publisher wrapper). Each asserts `'repeats the note of'`. | closed |
| T-12-02-03 | Repudiation | a fabricated digest test passes without real I/O | mitigate | Acceptance greps re-run at `7a49e84`: `read_text(encoding='utf-8') + ' '` in the answers tests gives 0, and `'f' * 64` in the decisions tests gives 0. `test_validate_decisions_rejects_templated_note_collision_for_uncertified_answers` (decisions test L210) now uses a real changed copy. The one remaining `'f' * 64` (pub tests L375) is a sign-off digest-mismatch negative case, outside the D-13 scope. | closed |
| T-12-02-SC | Tampering | package installs (12-02) | accept | See AR-04. | closed |
| T-12-03-01 | Repudiation | a git error reported as "not an ancestor" | mitigate | `resolve_record_commit` (reply builder L341-364): `merge-base` rc 1 gives "not an ancestor of HEAD" (L361-362), any other non-zero rc gives "cannot check ancestry ... git merge-base exit N" (L363-364), and an OSError from each git call is wrapped as AuthorityError (L344-345, L353-354, L359-360). Parametrised cases (reply test L382-392) include `mb_rc=128`, `cat_exc` and `mb_exc`. | closed |
| T-12-03-02 | Elevation of privilege | exec of a git blob | accept | See AR-02. | closed |
| T-12-03-03 | Tampering | frozen reply builder output drifts | mitigate | `test_real_reply_files_validate` (reply test L290) runs the committed reply through the unmodified validator. `test_frozen_constants_match_git` (L322) and `test_frozen_constant_equals_publisher_blob` (L607) keep the freeze binding. CI runs `build_..._reply.py --validate` (`ems-validate.yml` L98). All pass in this audit run. | closed |
| T-12-03-SC | Tampering | package installs (12-03) | accept | See AR-04. | closed |
| T-12-04-01 | Denial of service | a malformed file crashes the validator with a non-domain exception | mitigate | `load_checked` (publisher L87-89) wraps OSError and ValueError (including JSONDecodeError). `schema_check` (L90-94) wraps SchemaError and ValidationError. `validate_published` uses `load_checked` for the authority, schema, sign-off and manifest (L800-809), the manifest guard is `isinstance(manifest, dict)` (L811), and the record guard is in `check_publication_record` (L832-833). Lineage guards: `validate_lineage` checks `isinstance` for `lin`, each entry and `supersedes` (L442-448). Tests: `test_malformed_published_files_raise_domain_error` covers 9 cases (pub tests L1466-1484) and `test_validate_lineage_rejects_non_object[list, string]` (lineage test L408-411). | closed |
| T-12-04-02 | Tampering | Python checks evaluate a schema-valid-looking authority before the schema does | mitigate | In `validate_published`, `schema_check(a, load_checked(SCHEMA), ...)` (publisher L801) runs before `validate_publication(a)` (L802). The case `authority_missing_required_key` raises `fails the schema` (pub tests L1473). | closed |
| T-12-04-03 | Repudiation | the dry run claims "No decision changed" when rows differ | mitigate | `dry_run_summary` sets `unchanged = same == 'equals' and not diff_ids and not set_differs`. `lead` is `'No decision changed'` only in that case, and otherwise `DECISIONS DIFFER from 2.0.2` (publisher L645-648). Test: `test_dry_run_summary_differ_branch_is_reachable` (pub tests L1486-1492). | closed |
| T-12-04-04 | Tampering | negative-mutation outcomes drift and silently change the certified N_NEGATIVE | mitigate | The fixed outcome set is enforced by `test_each_mutation_is_rejected_by_its_gates` (pub tests L1208-1209), `test_published_negative_file_equals_observed_outcomes` (L1359) and `test_certification_and_semantic_files_are_derived`, which asserts 29 invariants and `result == 'PASS'` (L1345-1351). `validate_published` rebuilds every output, including N_NEGATIVE, and compares bytes (publisher L815-819). | closed |
| T-12-04-SC | Tampering | package installs (12-04) | accept | See AR-04. | closed |
| T-12-05-01 | Tampering | a dirty tree at the pin certifies the wrong bytes | mitigate | At-pin runs `git_not_shallow()`, then `check_tree_matches_head([*publication_paths(), rel(SCRIPT)])`, then `git_dirty([..., rel(SCRIPT), rel(OUT)])`, before any other check (publisher L793-797). `publication_paths()` lists the 10 D-05 paths (L596). Real-repo test: `test_real_git_repo_at_pin_passes_and_dirty_fails` (pub tests L767) edits the authority and the script. Seam test: `test_at_pin_dirty_tree_fails_closed` (L603). | closed |
| T-12-05-02 | Tampering | option or argument injection into git via a commit or path | mitigate | 40-hex `re.fullmatch` checks on SHAs in `git_show` (L368), `git_is_ancestor` (L389-390), `git_commit_blob` (L412) and `write_publication_record` (L860). `bad_rel` (L363) is applied before git in `git_show` (L369), `git_dirty` (L405-406), `git_commit_blob` (L413) and `git_index_flags` (L420-421). `--` separators: `git_show` argv `['git','show',f'{commit}:{path}','--']` (L370), `git_dirty` (L407) and `git_index_flags` (L422). All calls are list-form with no shell. Tests: `test_git_show_argv_ends_with_double_dash` (pub tests L1682), `test_git_dirty_rejects_bad_path_before_git` (L1567), `test_git_is_ancestor_rejects_non_sha_before_git` (L1530), `test_git_commit_blob_argv_and_failures` (L1600) and `test_git_index_flags_rejects_bad_input_before_git` (L1627). | closed |
| T-12-05-03 | Repudiation | a shallow or unknown clone state yields a false PASS | mitigate | `git_not_shallow` (publisher L395-401) returns only on exactly `'false'`, raises on `'true'`, and raises GitHistoryError showing unknown output with `!r`. A non-zero rc also raises. Tests: `test_git_not_shallow_*` (pub tests L1536-1557), `test_at_pin_shallow_fails_closed` (L618) and `test_plain_validate_shallow_fails_closed` (L702). | closed |
| T-12-05-04 | Spoofing | the at-pin record names an arbitrary earlier publication | mitigate | At pin, `record['publication_commit']` must equal `source_lineage.supersedes.commit` and `authority_sha256` must equal `supersedes.sha256` (publisher L836-839). `supersedes` itself must equal the `SUPERSEDED_V2_0_2` constant (`validate_authority` L251, `validate_publication` L349, schema `pinned(...)` L476). The record digests are recomputed from the blobs at that commit (L847-848). Tests: `test_at_pin_mode_accepts_only_superseded_record` (L536), `test_at_pin_wrong_commit_or_digest_fails` (L581) and `test_at_pin_record_blobs_must_match_the_superseded_commit` (L591). | closed |
| T-12-05-05 | Repudiation | an at-pin PASS read as full verification | mitigate | At-pin prints `{"status":"PASS","mode":"AT_PIN","deferred":[AT_PIN_DEFERRED]}` (publisher L825). `AT_PIN_DEFERRED` names `PUBLICATION_RECORD_BINDING` and says to run plain `--validate` at the record commit or later (L828). Tests: `test_at_pin_mode_accepts_only_superseded_record` (pub tests L536) and `test_cli_validate_at_pin_passes_true` (L942). | closed |
| T-12-05-06 | Elevation of privilege | new subprocess call sites outside the seam | mitigate | `source_without_git_show()` (pub tests L95-99) removes only the import line, `git_show` and `git_run`. `test_module_does_not_call_git` (L101-103) and `test_publisher_source_runs_no_subprocess_or_evaluator` (L1353-1357) then assert that no `subprocess`, `os.system` or `Popen` remains. All new helpers (`git_head`, `git_is_ancestor`, `git_not_shallow`, `git_dirty`, `git_commit_blob`, `git_index_flags`) call `git_run` (publisher L381-429). | closed |
| T-12-05-SC | Tampering | package installs (12-05) | accept | See AR-04. | closed |
| T-12-06-01 | Tampering | a published file changed in a later commit | mitigate | Plain mode compares `git_show(pub, p)` with `git_show(head, p)` for every path in `publication_paths()` (the 10 D-05 paths) (publisher L854-855). Tests: `test_plain_validate_requires_blob_identity_at_head` (pub tests L693) and `test_real_git_repo_plain_passes_after_record_and_later_commits_and_catches_head_drift` (L734). | closed |
| T-12-06-02 | Spoofing | the record names a commit outside HEAD's history | mitigate | `if not git_is_ancestor(pub, head): raise AuthorityError(...)` (publisher L853). `git_is_ancestor` maps rc 0/1 and fails closed on any other rc (L388-393). Tests: `test_plain_validate_requires_ancestry` (pub tests L683), `test_git_is_ancestor_maps_rc` (L1519) and `test_git_is_ancestor_other_rc_fails_closed` (L1524). | closed |
| T-12-06-03 | Tampering | an uncertified publisher edit passes CI | mitigate | The live digest check `lf_digest(SCRIPT) != ps['sha256']` (publisher L814) runs in both modes. The pinned digest check `git_show(pub, rel(SCRIPT))` (L856) runs in plain mode. Tests: `test_script_edit_after_publication_fails_validate` (pub tests L1136), `test_pinned_script_digest_mismatch_fails_plain_validate` (L1154) and `test_validate_rejects_missing_publisher_script_entry` (L1164). CI validator 1 (`ems-validate.yml` L94) is red by design in the D-16 window. | closed |
| T-12-06-04 | Repudiation | plain `--validate` at the pin gives a confusing failure | mitigate | When the record still names the superseded publication, the error is "... run --validate --at-pin here, or plain --validate at the record commit or later" (publisher L841). Test: `test_plain_validate_at_pin_record_points_to_at_pin` (pub tests L712). | closed |
| T-12-06-05 | Repudiation | a shallow clone hides history | mitigate | `git_not_shallow()` (publisher L851) runs before `git_head()` and `git_is_ancestor` (L852-853) in plain mode. Test: `test_plain_validate_shallow_fails_closed` (pub tests L702). Caveat (12-REVIEW IN-04, advisory): earlier pinned reads in `validate_publication` and `validate_lineage` run first, but in a shallow clone they also fail closed (GitHistoryError), only with a less specific message. | closed |
| T-12-06-SC | Tampering | package installs (12-06) | accept | See AR-04. | closed |
| T-12-07-01 | Tampering | a hand-typed supersedes digest | mitigate | `test_superseded_v2_0_2_constants_match_git_history` (pub tests L1069-1081) recomputes the authority and decisions LF digests from the blobs at `ae15c74`, and checks the commit and `authority_sha256` against the record at `a71257e`. It passes in this audit run. The constant is at publisher L36-44. | closed |
| T-12-07-02 | Repudiation | the manifest note or dry run claims something untrue | mitigate | `git grep "pre-publication\|not recomputed on validation" -- scripts tests` at `7a49e84` finds only the negative assertion `assert 'pre-publication' not in out` (pub tests L1193). The rewritten `publisher_script_note` (publisher L694) describes both the live and the pinned digest checks, and the gate text in the dry run (L655) describes the at-pin and plain modes. | closed |
| T-12-07-03 | Tampering | 2.0.3 changes a decision | mitigate | The PUB-08 comparison reads the 2.0.2 rows at `SUPERSEDED_V2_0_2['commit']` (`rows_differing_from_previous`, publisher L291-296), and `validate_publication` raises on any differing row or set (L333-335). The decisions digest is pinned to `4e746d1f…` (L40, L323, L326). The dry-run test asserts `'row comparison 2.0.2 -> 2.0.3: 80 controls identical to 2.0.2'` (pub tests L1191). Tamper tests are at L1415 and L1427. | closed |
| T-12-07-04 | Denial of service | a missed constant reference breaks module collection | mitigate | `git grep SUPERSEDED_V2_0_1` at `7a49e84` matches only `.planning/` documents, with none in `scripts/` or `tests/`. All archive modules collect with no errors in this audit run. | closed |
| T-12-07-SC | Tampering | package installs (12-07) | accept | See AR-04. | closed |
| T-12-08-01 | Tampering | `validate_published` at pin | mitigate | `check_tree_matches_head` (publisher L431-440) checks each path against `git_commit_blob(head, p)` (`git cat-file blob <head>:<p>`, L411-416). It raises "not committed at HEAD" if the path is missing from HEAD, "absent from the working tree" if the file is missing on disk, and "working tree differs from HEAD" if the LF-normalised bytes differ. At pin it runs over the 10 D-05 paths plus the script, 11 in total (L795). Tests: `test_check_tree_matches_head_cases[pass_crlf, not_committed, absent, differs, flagged]` (pub tests L1639-1664), the blind-spot case `test_real_layout_at_pin_fails_closed_where_git_status_is_blind[rm_cached_generated]` (L857-895), and the positive controls at L838 and L845. | closed |
| T-12-08-02 | Spoofing | git index flags | mitigate | `git_index_flags` (publisher L418-429) accepts only the tag `'H'`. Any other tag (lowercase = assume-unchanged, `S`, `M`) and "not in the index" are reported, and `check_tree_matches_head` raises "index flags hide working-tree state" (L439-440). Tests: `test_git_index_flags_reports_flagged_and_missing_paths` (pub tests L1613) and the real-git blind-spot cases `skip_worktree_*` and `assume_unchanged_*` for both the authority and the script, including the flag-only cases (L857). | closed |
| T-12-08-03 | Information disclosure / Tampering | `git_dirty` | mitigate | The argv is `git --literal-pathspecs status --porcelain --untracked-files=all --ignored=matching -- <paths>` (publisher L407). At pin, the pathspec includes `rel(OUT)` (L796). Tests: the real-git blind-spot cases `untracked_with_show_untracked_no` and `ignored_extra_in_out` (pub tests L857-895), and `test_git_dirty_returns_porcelain_lines` (L1559). | closed |
| T-12-08-04 | Repudiation | at-pin output text | mitigate | The errors describe the comparison actually made: "git status (untracked and ignored files shown) reports changes ..." (publisher L797), and "not committed at HEAD", "absent from the working tree", "working tree differs from HEAD ... (CRLF_TO_LF normalised)" and "index flags hide working-tree state" (L434-440). `grep "modified or untracked"` on the publisher gives 0. | closed |
| T-12-08-05 | Tampering | plain `--validate` in the operator's tree | mitigate | `check_publication_record` ends plain mode with `check_tree_matches_head(publication_paths())` (publisher L857). Tests: `test_real_layout_plain_validate_binds_working_tree_to_head` (pub tests L897) and `test_plain_validate_binds_working_tree_to_head` (L1666). | closed |
| T-12-08-06 | Tampering | ambient `GIT_*` environment and replace refs (WR-02) | accept | See AR-03. | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01 | T-12-01-04 | The collect guard is now scoped to `test_archive_assessment_*` modules (D-10), so a skip raised in `conftest.py` itself is not converted. This still fails closed in CI: if `conftest.py` skips, nothing is collected and pytest exits 5, which fails the step. Recorded in 12-01-SUMMARY (Notes). | Plan-time disposition (12-01-PLAN), approved by Oscar Mack (EMS governance authority) | 2026-11-17 |
| AR-02 | T-12-03-02 | The tests exec the historical publisher blob, which is read with `git show` at a pinned 40-hex commit from this repository's own history. The exec runs in tests only. The builders contain no exec, eval or loaders, enforced by the AST scanner `FORBIDDEN_CALLS` (reply test L708) with `test_builder_has_no_publisher_reference` (L743) and the scanner self-test `test_publisher_ref_scanner_flags_the_old_loader` (L747). | Plan-time disposition (12-03-PLAN), approved by Oscar Mack (EMS governance authority) | 2026-11-17 |
| AR-03 | T-12-08-06 | 12-REVIEW WR-02: the git seam (`git_show`, `git_run`, publisher L367-377) inherits `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY` and related variables, and follows `refs/replace/*`. It is deferred as advisory. Scrubbing the environment and config would change Git for Windows system-config behaviour (`core.autocrlf`) in the operator's tree and could break the CRLF working copy that the certified LF digests rely on. CI (`fetch-depth: 0`, fresh `actions/checkout`) and Hayes run clean checkouts with no ambient `GIT_*` state or replace refs. Revisit after 2.0.3. | Plan-time disposition (12-08-PLAN), approved by Oscar Mack (EMS governance authority) | 2026-11-17 |
| AR-04 | T-12-01-SC, T-12-02-SC, T-12-03-SC, T-12-04-SC, T-12-05-SC, T-12-06-SC, T-12-07-SC | No packages were installed. `git diff --stat 87b5cd5 7a49e84 -- requirements.txt requirements-dev.txt` is empty, and the CI install line (`ems-validate.yml` L85) is unchanged. | Plan-time disposition (12-01..12-07-PLAN), approved by Oscar Mack (EMS governance authority) | 2026-11-17 |

Carried forward from Phase 11: the 11-SECURITY AR-01 caveat (11-REVIEW WR-05: a module-level skip in a deselected non-archive module stopped the whole run) is now fixed by D-10 in 12-01. The fix is the `_archive_module` scoping (`tests/conftest.py` L24-26, L34-35) and is tested by `test_guard_ignores_skip_in_deselected_non_archive_module` (skip-guard L112). The 11-SECURITY AR-02 HINT overstatement is fixed by D-11 (`tests/aa_history.py` L10-11). 11-SECURITY AR-03 and AR-04 are unchanged.

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-11-17 | 42 (32 mitigate, 10 accept) | 42 | 0 | gsd-security-auditor (code evidence at `7a49e84`; `EMS_FAIL_ON_SKIP=1` targeted pytest: skip-guard, reply, governance decisions and answers, lineage validation and v2 authority modules gave 469 passed and 1 failed; the v2 publication module gave 307 passed and 2 failed. That is 776 passed and 3 failed in total, and the 3 failures are exactly the D-16 red set) |

Red window (accepted by design, not a security gap): the D-16 set is `test_committed_schema_equals_schema_function`, `test_real_published_files_validate`, `test_publisher_still_valid_and_digest_matches_manifest` and CI validator 1. It stays red until the 2.0.3 republication in Phase 13. The orchestrator's independent full-suite run at `866c07a` gave 1020 passed and 3 failed (exactly the D-16 set) with `EMS_FAIL_ON_SKIP=1`.

Unregistered flags: none. 12-05-SUMMARY maps the new git surface (status, rev-parse, merge-base) to T-12-05-01..06. 12-06-SUMMARY maps its checks to T-12-06-01..05. The 12-08 additions (`cat-file blob`, `ls-files -v`) are registered as T-12-08-01..03.

Informational, not blockers (12-REVIEW, deferred or advisory):
- WR-02 is covered by T-12-08-06 and AR-03.
- WR-03: the subprocess D-10 test is vacuous while validator 1 is red. The in-process D-10 test carries the evidence for T-12-02-01. Assert `before == (0, 'PASS')` after Phase 13.
- IN-01..IN-04, IN-06 and IN-07 are wording, ordering and test-strength items. IN-06 notes that the GATE-06 self-attestation scope does not cover `scripts/build_archive_assessment_governance_decisions.py`. The decisions file itself is digest-pinned.
- CR-01, WR-01, WR-04 and IN-05 are closed by 12-08 (T-12-08-01..05).
- The reply builder's `git_show` (L72) has no trailing `--`. It is frozen (D-13) and has the 40-hex and `bad_rel` guards from Phase 11 (T-11-01).

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-11-17
