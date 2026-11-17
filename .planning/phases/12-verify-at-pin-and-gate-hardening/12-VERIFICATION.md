---
phase: 12-verify-at-pin-and-gate-hardening
verified: 2026-11-17T03:45:00Z
status: gaps_found
score: 7/8 must-haves verified
overrides_applied: 0
gaps:
  - truth: "At-pin PASS means the bytes it validated are the pinned commit's bytes: --validate --at-pin fails closed when any D-05 publication file or the publisher script is modified, untracked, absent from HEAD or index-flagged (D-04, D-08, D-12), so the single named deferred check (PUBLICATION_RECORD_BINDING) really is the only check not performed at the pin (PIN-01)"
    status: failed
    reason: "The at-pin clean-tree guarantee rests only on `git status --porcelain -- <paths>` (git_dirty, publisher L403-408, called at L762-765). In this repository all 7 generated publication files sit under the gitignored `generated/` (.gitignore:6; check-ignore confirms every one). Reproduced in a scratch repo with the same ignore rule: (1) an untracked file under the ignored generated/ prints nothing; (2) a publication file dropped from the index by a committed `git rm --cached`, still on disk, prints nothing although HEAD no longer contains it; (3) `git update-index --skip-worktree` (or assume-unchanged) followed by an edit prints nothing, which also defeats D-08/D-12 for the publisher script; (4) with `status.showUntrackedFiles=no` an untracked file prints nothing. In each case at-pin goes on to validate the working tree and prints {status: PASS, mode: AT_PIN, deferred: [PUBLICATION_RECORD_BINDING]}, so the output's claim that only the record binding is deferred is false. Phase 13 uses this exact gate at the publication commit before writing the record, and the record permanently binds the commit Hayes re-pins to. A defective pin (for example a generated file missing from the publication commit) would be recorded and caught only afterwards by plain --validate or by Hayes. The D-04 error text 'modified or untracked' promises more than the check delivers. A fresh clean checkout (Hayes's case) is not misled, because a missing file then fails validation. The gap is in the operator gate that PIN-01's at-pin mode exists to provide. No test covers these cases (12-REVIEW WR-04): the only real-git at-pin test uses a temp repo with no .gitignore and no index flags, and the git_dirty unit tests fake git_run."
    artifacts:
      - path: "scripts/publish_archive_assessment_applicability_authority_v2.py"
        issue: "git_dirty (L403-408) uses plain `git status --porcelain`; validate_published at-pin branch (L762-765) relies on it alone; nothing checks that each publication path and the script exist in HEAD and equal the HEAD blob"
      - path: "tests/test_archive_assessment_applicability_authority_v2_publication.py"
        issue: "test_real_git_repo_at_pin_passes_and_dirty_fails (L758-786) builds a repo with no .gitignore and no index flags; it covers only working-tree byte edits"
    missing:
      - "In at-pin mode, after git_not_shallow(), compare every D-05 path plus rel(SCRIPT) against HEAD directly: git_show(git_head(), p) must succeed (path committed at HEAD) and lf_bytes(live file) must equal lf_bytes(HEAD blob); fail closed with an AuthorityError naming the path otherwise (12-REVIEW CR-01 fix)"
      - "Reject any of those paths whose `git ls-files -v` tag is lowercase (assume-unchanged) or 'S' (skip-worktree)"
      - "Harden git_dirty as a second line: `git --literal-pathspecs status --porcelain --untracked-files=all --ignored=matching -- <paths>` (also closes IN-05)"
      - "Make the error text match what is checked"
      - "Extend the real-git at-pin test: temp repo with `.gitignore` containing `generated/` and force-added generated files; assert at-pin fails for (a) a committed `git rm --cached` of a generated publication file, (b) skip-worktree plus edit of the authority and of the script, (c) assume-unchanged plus edit, (d) `git config status.showUntrackedFiles no` with a publication file untracked"
      - "List any test or validator this turns red in 12-BASELINE-RED.md. The D-16 red set may only stay as listed: a publisher edit keeps the same 3 tests and validator 1 red until the Phase 13 republication certifies the new script digest"
---

# Phase 12: Verify-at-Pin and Gate Hardening Verification Report

**Phase Goal:** The publisher and validators are in their final 2.0.3 form: Hayes can verify at the pin, malformed input fails with domain errors, and the audit review items are closed, all before the single republication.
**Verified:** 2026-11-17T03:45:00Z (HEAD 02699fb, branch feature/ems-aa3-archive-applicability-authority)
**Status:** gaps_found
**Re-verification:** No. This is the initial verification.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1 / PIN-01: on a clean checkout of the publication commit, `--validate --at-pin` returns PASS and names the one deferred check | VERIFIED | `validate_published(at_pin=True)` prints `{"status":"PASS","mode":"AT_PIN","deferred":[AT_PIN_DEFERRED]}`. AT_PIN_DEFERRED names PUBLICATION_RECORD_BINDING and points to plain `--validate` (L793, L796). The binding comes from `a['source_lineage']['supersedes']` (D-02, L803). `test_real_git_repo_at_pin_passes_and_dirty_fails` passes with real git. `--at-pin` without `--validate` is a parser error. `--pre-publication` is rejected as an unrecognised argument (verified on the CLI). |
| 2 | At-pin PASS means the validated bytes are the pinned commit's bytes (D-04/D-08/D-12 fail closed), so the single deferred check is truly the only one | FAILED (BLOCKER) | 12-REVIEW CR-01, reproduced. `git status --porcelain` is silent for ignored or untracked files under `generated/` (all 7 generated publication files), for publication files dropped from HEAD by a committed `rm --cached`, for skip-worktree and assume-unchanged edits (including the publisher script), and under `status.showUntrackedFiles=no`. See the gap in the frontmatter. |
| 3 | SC2 / PIN-02: plain `--validate` passes at the record commit or later, checking that the record names the publication commit, ancestry, and byte identity of the publication files | VERIFIED | `check_publication_record` non-at-pin branch (L816-825): `git_not_shallow`, `git_is_ancestor(pub, head)`, and `git_show(pub,p) == git_show(head,p)` for all 10 `publication_paths()`. When the record still names the superseded publication, the error points to `--at-pin` (L809). Tests `test_plain_validate_requires_ancestry`, `..._blob_identity_at_head[3]`, `..._shallow_fails_closed` and `test_real_git_repo_plain_passes_after_record_and_later_commits_and_catches_head_drift` all pass. |
| 4 | SC3 / GATE-06: `--validate` fails when the publisher-script digest differs from the certification | VERIFIED | L782 compares the live script's LF digest with `manifest.publisher_script.sha256`. L825 does the same for the script at the publication commit. `test_script_edit_after_publication_fails_validate` and `test_pinned_script_digest_mismatch_fails_plain_validate` pass. |
| 5 | SC4 / GATE-07, GATE-08: malformed shapes raise AuthorityError, `validate_published` checks the schema first, and `--validate` enforces cross-note uniqueness under `norm_templated` | VERIFIED | `load_checked` and `schema_check` wrap the OSError, ValueError, SchemaError and ValidationError cases. The schema check runs before `validate_publication` (L770-772). There are 9 `test_malformed_published_files_raise_domain_error` cases and 2 `validate_lineage` non-object cases. GATE-08: the decisions builder already enforces it (L321, `key = norm if certified else norm_templated`, from 08 WR-05 a9ff5d1). Phase 12 added `--validate`-path tests: `test_validate_cli_rejects_note_collision_for_real_changed_answers` and `test_publisher_validate_governance_decisions_rejects_note_collision_for_real_changed_answers`. Both pass. |
| 6 | SC5 / GATE-09, GATE-10: D-10 and D-13 tests and the cleanup items | VERIFIED (with advisory WR-03) | D-10: the in-process `test_d10_..._does_not_change_build_or_validation` and the subprocess `test_d10_..._does_not_change_validate_outcome`. D-13: real changed answer bytes. GATE-10: the dry-run lead and row text are conditional (L614-619), and `test_dry_run_summary_differ_branch_is_reachable` passes. The 2.0.0 anchor test is restored (`test_2_0_0_anchor_matches_frozen_2_0_1_publisher_and_chain`). The dead `log` fake is gone (a3a9c9b). `resolve_record_commit` errors are uniform in the reply builder (D-13). The D-08 tamper test covers 3 rows (undecided, no-rule, rule) x 4 tampers. |
| 7 | D-16: the only reds are the 3 named tests and CI validator 1, and nothing prevents them clearing at a correct 2.0.3 publication | VERIFIED | Own run, see Behavioral Spot-Checks: 986 passed, 3 failed, exactly the D-16 ids. Validator 1 exits 1 with the expected message, and validators 2-6 exit 0. Clearing path: `schema()` pins `SUPERSEDED_V2_0_2`, which an `--emit-schema` at publication refreshes. At the 2.0.3 publication commit, the committed record (2.0.2 at ae15c74, sha a44eea1f...) equals `supersedes`, which satisfies the at-pin branch. At the record commit, plain mode checks the 2.0.3 record, ancestry and blobs. The manifest will record the new script digest. CI uses `fetch-depth: 0`. |
| 8 | Boundaries: no change under registry/, schemas/, docs/ or generated/ since 87b5cd5; the frozen 2.0.2 notice builder is unchanged; the reply builder changed only as D-13 allows | VERIFIED | `git diff --stat 87b5cd5 HEAD -- registry schemas docs generated` is empty. `git diff 87b5cd5 HEAD -- scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` is empty. The reply builder diff touches only the `resolve_record_commit` loop body: an OSError wrap of `cat-file`/`merge-base`, and a split between `merge-base` exit 1 and other exit codes. No literals or other functions changed. Validator 5 (reply) and validator 6 (notice) PASS. |

**Score:** 7/8 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/publish_archive_assessment_applicability_authority_v2.py` | git seam, `publication_paths`, at-pin and plain modes, GATE-06, SUPERSEDED_V2_0_2, VERSION 2.0.3 | VERIFIED (except truth 2) | 843 lines. `SUPERSEDED_V2_0_1` is gone from scripts/ and tests/. The at-pin dirty check is the gap. |
| `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` | D-13 IN-04 only | VERIFIED | 16-line diff confined to `resolve_record_commit` |
| `tests/conftest.py` | D-10 skip guard scoped to `test_archive_assessment_*` modules | VERIFIED | `_archive_module` gate. `test_guard_ignores_skip_in_deselected_non_archive_module` passes. |
| `tests/aa_history.py` | D-11 IN-08/IN-09 wording | VERIFIED | Accurate HINT. Unrecognised shallow output is reported with the raw value. |
| `.github/workflows/ems-validate.yml` | D-09 narrowed glob | VERIFIED | `python -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q`, `EMS_FAIL_ON_SKIP: '1'`, fetch-depth 0 |
| `12-BASELINE-RED.md` | red set per commit | VERIFIED | The ledger matches the observed end state |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `main --validate --at-pin` | `validate_published(True)` | argparse | WIRED | L835-836 |
| at-pin branch | working tree == pinned tree | `git_dirty` (`git status --porcelain`) | PARTIAL | Blind to ignored, untracked, absent-from-HEAD and index-flagged paths (gap) |
| `check_publication_record` at-pin | `source_lineage.supersedes` | `a['source_lineage']['supersedes']` | WIRED | D-02 |
| plain mode | publication commit blobs | `git_is_ancestor` + `git_show` x 10 + script | WIRED | L818-825 |
| `validate_published` | manifest `publisher_script.sha256` | `lf_digest(SCRIPT)` | WIRED | L782 |
| CI step | archive tests and 6 validators | workflow | WIRED | L87-99 |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full archive suite, D-16 red set only | PowerShell, `EMS_FAIL_ON_SKIP=1`, `.venv\Scripts\python.exe -m pytest (Get-ChildItem tests/test_archive_assessment_*.py).FullName --basetemp=<fresh scratch> -p no:cacheprovider -q -rf` | 986 passed, 3 failed in 360.48s. pytest's own exit code is 1. FAILED: `test_archive_assessment_applicability_authority_v2.py::test_committed_schema_equals_schema_function`, `..._v2_publication.py::test_real_published_files_validate`, `..._v2_publication.py::test_publisher_still_valid_and_digest_matches_manifest` | PASS (exactly D-16) |
| CI validator 1 | `publish_..._v2.py --validate` | exit 1: `AuthorityError: authority identity/version/status invalid; source_lineage supersedes does not name the 2.0.2 publication` | PASS (accepted red, D-16) |
| CI validators 2-6 | decisions `--validate`; proposals `--validate` and `--validate-record`; reply `--validate`; notice 2.0.2 `--validate` | all PASS (exit 0) | PASS |
| `--at-pin` alone | `publish_..._v2.py --at-pin` | `error: --at-pin requires --validate` | PASS |
| removed flag | `--validate --pre-publication` | `unrecognized arguments: --pre-publication` | PASS |
| CR-01 reproduction | scratch repo with `.gitignore: generated/`; `git status --porcelain -- <path>` for ignored-untracked, committed `rm --cached`, skip-worktree edit, `showUntrackedFiles=no` | no output in all four cases (control case `?? reg/u.json` reported) | FAIL (confirms gap) |

### Probe Execution

No probes are declared or used in this phase. Step 7c does not apply.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| PIN-01 | 12-05 | documented `--validate` at a clean checkout of the publication commit returns PASS and names its deferred check | BLOCKED (partially) | The positive path works (truth 1). The at-pin fail-closed guarantee that makes "one deferred check" true does not hold (truth 2, CR-01). |
| PIN-02 | 12-06 | plain `--validate` passes at the record commit or later, with ancestry and byte identity | SATISFIED | truth 3 |
| GATE-06 | 12-06 | `--validate` checks the publisher-script digest | SATISFIED | truth 4 |
| GATE-07 | 12-04 | domain errors; schema first | SATISFIED | truth 5 |
| GATE-08 | 12-02 | `--validate` path enforces `norm_templated` uniqueness | SATISFIED | truth 5 |
| GATE-09 | 12-02 | D-10 catalog-edit test; D-13 real bytes | SATISFIED | truth 6 (WR-03 advisory) |
| GATE-10 | 12-03, 12-04 | cleanup items | SATISFIED | truth 6 |

No orphaned requirements: REQUIREMENTS.md maps exactly PIN-01, PIN-02 and GATE-06..10 to Phase 12. REQUIREMENTS.md still shows PIN-01, PIN-02 and GATE-06 as `[ ]`/Pending, which is consistent with completion only at the Phase 13 publication.

### Code Review Findings: Classification

| Finding | Classification | Rationale |
|---------|----------------|-----------|
| CR-01 at-pin clean-tree check rests on `git status --porcelain` | **GAP (BLOCKER), truth 2 / PIN-01** | Reproduced, and it applies to this repo's layout (all 7 generated files are under the ignored `generated/`). It defeats the D-04/D-08/D-12 fail-closed guarantee that PIN-01's at-pin mode depends on, and it sits in the exact gate Phase 13 uses before recording the pin. |
| WR-04 no real-layout at-pin test | **Part of the CR-01 gap** | This is why CR-01 went unseen. The gap's `missing` list includes the tests. |
| WR-01 plain mode binds the working tree to HEAD only for authority and manifest | Advisory | SC2/PIN-02 literally require record naming, ancestry and pub-vs-HEAD byte identity, and all three are implemented. CI and Hayes run on clean checkouts where the working tree equals HEAD. Same root cause as CR-01 (working tree not bound to committed blobs), so it is cheap to fix in the same gap plan. |
| WR-02 ambient `GIT_*` env and replace refs | Advisory | Hardening beyond the stated criteria |
| WR-03 D-10 subprocess test vacuous while `--validate` is red | Advisory | The in-process D-10 test genuinely covers build and `validate_publication`. The subprocess test becomes meaningful once validator 1 is green after Phase 13. Recommended: assert `before == (0, 'PASS')` at Phase 13. |
| IN-01..IN-07 | Advisory | Message accuracy, ordering of the shallow check, literal pathspecs (fold IN-05 into the CR-01 fix), GATE-06 self-attestation scope, brittle test assertions. None negates a success criterion. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| scripts/publish_archive_assessment_applicability_authority_v2.py | 765 | Error text promises "modified or untracked" but the check is blind to ignored-untracked paths | Blocker (same gap) | False fail-closed claim |

No unreferenced TBD, FIXME or XXX markers were introduced in the phase-modified code.

### Human Verification Required

None beyond the gap. The at-pin positive path at a real 2.0.3 pin can only be observed in Phase 13, and Phase 13 SC4 already covers it.

### Gaps Summary

Phase 12 delivers almost everything:
- the 2.0.3 final form (SUPERSEDED_V2_0_2, VERSION 2.0.3);
- PIN-02 ancestry and blob identity;
- GATE-06 script digest, live and pinned;
- GATE-07 schema-first domain errors;
- GATE-08/09 `--validate`-path tests;
- every GATE-10 cleanup item;
- the D-09/D-10/D-11 test and CI fixes.

The red window is exactly the D-16 ledger: 3 tests plus validator 1. I found nothing that would stop it from closing at a correct 2.0.3 publication and record commit. Nothing changed under registry/, schemas/, docs/ or generated/. The 2.0.2 notice builder is untouched, and the reply builder change stays within D-13.

One gap blocks the goal. `--validate --at-pin` can print PASS, naming only the record binding as deferred, when the tree it validated is not the pinned tree. Its only guard is `git status --porcelain`, which cannot see the ignored `generated/` publication files when they are untracked or dropped from HEAD, cannot see skip-worktree or assume-unchanged edits (including to the publisher script), and cannot see anything under `status.showUntrackedFiles=no`. This is the gate Phase 13 relies on before it writes the permanent publication record, so it must be fixed in the publisher before the single republication. The fix is a direct HEAD-blob comparison for the 10 publication paths plus the script, an index-flag rejection, and hardened status flags, with real-layout tests. The fix is a publisher edit, so it keeps the existing D-16 reds (same 3 tests plus validator 1) and must not add any new ones. WR-01 (plain-mode working tree vs committed blobs) shares the root cause and can be fixed in the same plan.

---

_Verified: 2026-11-17T03:45:00Z_
_Verifier: Claude (gsd-verifier)_
