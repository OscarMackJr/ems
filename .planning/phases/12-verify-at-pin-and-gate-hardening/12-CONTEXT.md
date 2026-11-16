# Phase 12: Verify-at-Pin and Gate Hardening - Context

**Gathered:** 2026-11-16
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase puts the v2 publisher and its validators into their final 2.0.3 form before the single republication, which happens in Phase 13. Requirements: PIN-01, PIN-02, GATE-06, GATE-07, GATE-08, GATE-09, GATE-10.

**What it delivers:**
- Hayes can run a documented `--validate` mode on a clean checkout of the publication commit and get PASS. The output names the one check it defers.
- Plain `--validate` passes at the record commit and at any later commit.
- `--validate` checks the publisher-script digest.
- Malformed shapes fail with `AuthorityError`.
- `--validate` enforces cross-note uniqueness under `norm_templated`.
- The 08/09 review test and cleanup items are closed.

**Also in scope:** the folded-in 11-REVIEW WR-05, IN-08 and IN-09 test/CI fixes.

**Not in this phase:**
- Publishing 2.0.3 (Phase 13).
- The notice and its verification guidance, PIN-03 and NOTICE-03 (Phase 14).
- Any decision change.

</domain>

<decisions>
## Implementation Decisions

### Verify-at-pin mode (PIN-01)
- **D-01:** Rename `--pre-publication` to `--at-pin`. The command is `--validate --at-pin`, and `--pre-publication` is removed, with no alias. The publish sequence uses `--at-pin` in the step where it used `--validate --pre-publication` before (the 09 carried-forward sequence). `--at-pin` without `--validate` is a parser error, as today.
- **D-02:** In at-pin mode the identity of the superseded authority comes from the authority's own `source_lineage.supersedes` entry: authority id, version, commit and authority sha256. That entry is already checked against the pinned constant by `validate_publication` and `validate_lineage`. `check_publication_record` no longer hard-codes `SUPERSEDED_V2_0_1[...]`. The record must name exactly that superseded publication, and its digests must match the blobs at the superseded commit, so the existing `git_show` cross-checks still apply.
- **D-03:** At-pin mode prints a single JSON object when it passes, for example `{"status":"PASS","mode":"AT_PIN","deferred":["PUBLICATION_RECORD_BINDING: the record naming this commit is written in the next commit; run plain --validate at the record commit"]}`. The exact deferred wording is up to the planner, but it must name the record-to-commit binding as the only deferred check. Plain `--validate` still prints `PASS`, so CI and existing output are unchanged.
- **D-04:** At-pin mode fails closed if any of the publication paths (the D-05 set) is modified or untracked in the working tree, using `git status --porcelain -- <paths>`. The script cannot tell whether HEAD is the pin, so a clean tree is what it can enforce. If git is unavailable or the clone is shallow, it fails closed, as 07 D-11 and 08 D-09 require.

### Byte identity at the record commit or later (PIN-02)
- **D-05:** The "publication files" are the 10 files the publication commit contains: `AUTHORITY`, `SCHEMA`, `SIGNOFF`, and every file in `OUT` (the 7 generated files, manifest included). The list is derived from the publisher's path constants and is defined once, so at-pin's dirty check (D-04) and the Phase 13 PUB-12 commit check can reuse it. The publication record is not in the list, because it is written in the next commit.
- **D-06:** Plain `--validate` requires `record['publication_commit']` to be an ancestor of HEAD, checked with `git merge-base --is-ancestor`. For each D-05 file it then requires `git show <publication_commit>:<path>` to be byte-identical to `git show HEAD:<path>`. The existing LF-digest checks still cover the working-tree bytes. It fails closed without history or in a shallow clone. When run at the publication commit itself, plain `--validate` fails because the record names the previous authority. Its error message should point to `--validate --at-pin`.

### Publisher-script digest (GATE-06)
- **D-07:** Plain `--validate` requires `lf_digest(live publisher script)` to equal `manifest.publisher_script.sha256`. It also requires the LF digest of `git show <publication_commit>:<script path>` to equal the same value. The consequence is accepted: any later edit to the publisher, even a comment, turns `--validate` red until the next certified republication. This is the existing red-window model, and it matches the project rule that hash-based certification breaks on uncoordinated hand edits.
- **D-08:** In at-pin mode, the live publisher script must equal the manifest digest. At the pin, the live script is the pinned one, and D-04 guarantees it is unmodified. The script check is not deferred.

### WR-05, IN-08, IN-09 (folded in from 11-REVIEW)
- **D-09:** Narrow the CI `archive-assessment` step in `.github/workflows/ems-validate.yml` from `pytest tests -k archive_assessment` to `pytest tests/test_archive_assessment_*.py`. The planner should check how the glob expands on ubuntu bash; quoting may be needed. The step keeps `-p no:cacheprovider -q` and `EMS_FAIL_ON_SKIP=1`.
- **D-10:** Scope the `pytest_make_collect_report` hook in `tests/conftest.py` to collectors whose node id or path is an archive-assessment test module (`test_archive_assessment_*`). Skips in other modules are left alone. Add a subprocess case to `tests/test_archive_assessment_skip_guard.py` with a deselected, non-archive skipping module next to an archive module. With the guard on, the archive tests must still run and pass. A module-level skip in an archive-assessment module must still fail.
- **D-11:** Fix the wording in `tests/aa_history.py`. IN-08: the HINT must state accurately how far `EMS_ALLOW_NO_HISTORY=1` reaches. IN-09: when the shallow-check output is unrecognised (neither `true` nor `false`), the message must say so and show the raw output, not claim the repository is shallow. Fail-closed behaviour is unchanged. D-09, D-10 and D-11 go in one small test/CI commit. It should land first, while everything is still green.

### Carried forward (not re-asked)
- **Red window:** it opens at the first publisher edit in this phase and closes at the 2.0.3 publication commit and record commit (Phase 13). Each plan that touches the publisher lists every test or CI step it turns red. The red set may only shrink or stay as listed.
- **Final form:** "Final 2.0.3 form" means the publisher's supersedes binding moves to 2.0.2, following the 09 D-07 pattern. A `SUPERSEDED_V2_0_2` constant names authority id, version 2.0.2, commit `ae15c7458e49c8f55cc58c61bab04bc716aa9892`, the 2.0.2 authority LF sha256 (`a44eea1f…`) and the decisions LF sha256 (`4e746d1f…`). Values come from files and git, never typed by hand. All dependent uses move with it: validators, schema `pinned(...)`, mutations, the PUB-08 row comparison (2.0.3 against 2.0.2) and the dry-run summary. Version and id constants for 2.0.3 follow the existing pattern.
- **Grandfathering (08 D-13):** the certified answers digest still falls back to `norm`. Any other digest gets the strict check. GATE-08 applies that same rule on the `--validate` path of `validate_decisions`.
- **Domain errors only (08 D-04/D-05):** mutation gates count only domain errors. GATE-07 hardens shapes so no `TypeError`, `KeyError` or `AttributeError` escapes. `validate_published` runs the schema check before the Python checks.
- **Frozen builders (Phase 11):** the reply and 2.0.2 notice builders are frozen and must stay green, along with their freeze tests. The GATE-10 item "`resolve_record_commit` handles git errors the same way everywhere" touches `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:341`. Any change there must leave the reply validator result, the frozen literals and the Phase 11 independence tests unchanged.
- **Staging:** stage only by explicit path. Never stage `.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json` or the unrelated untracked files.
- **Who runs tests:** the orchestrator runs pytest and validators through PowerShell with a fresh `--basetemp`. Report pytest's own exit code, not one from a pipe.
- **No CI weakening:** no CI auto-detect mode is added (09 D-04). CI keeps running plain `--validate`.

### Resolutions of the research open questions (orchestrator, 2026-11-16, unattended run; conservative defaults)
- **D-12:** The at-pin dirty check (D-04) covers the 10 D-05 publication paths **plus the publisher script**. This makes D-08's guarantee true: at the pin the live script is unmodified, and its digest equals the manifest. The D-05 byte-identity set for plain `--validate` stays at the 10 files, because D-07 covers the script separately.
- **D-13:** GATE-10 IN-04 ("`resolve_record_commit` handles git errors the same way everywhere") is fixed only in the reply builder. The 2.0.2 notice builder stays frozen and untouched, as Phase 11 requires. The same pattern in the notice builder is recorded as deferred.
- **D-14:** The dry-run gate line and the manifest `publisher_script_note` must be true after GATE-06 and the `--at-pin` rename. They must not mention `--pre-publication` or claim the script digest is checked only by pytest. Wording is the planner's choice. Any change to manifest text is output that the 2.0.3 publication certifies; it is not a hand edit.
- **D-15:** Marking the notice files `eol=lf` in `.gitattributes` (a fresh Windows clone fails `test_committed_notice_files_validate`; CI is unaffected) is **out of scope**. It is deferred.
- **D-16:** Record every commit's red set in `12-BASELINE-RED.md`, following `09-BASELINE-RED.md`. The research measured the accepted end state as 3 tests plus CI validator 1 (`publish_..._v2.py --validate`). Any red beyond that ledger blocks the commit.

### Claude's Discretion
- Helper names, such as the D-05 path-list function and the at-pin result builder, in the publisher's compact single-quote style.
- Exact deferred-check wording and error messages, including the D-06 pointer to `--at-pin`.
- How GATE-07..10 are split into commits. Preferred order: (1) the D-09/D-10/D-11 test/CI commit while green; (2) the GATE-09 and GATE-10 test-only items where possible; (3) the publisher changes, which open the red window; (4) the supersedes move to 2.0.2. Each commit stages explicit paths and lists its red set.
- Whether at-pin mode and plain mode share one function with a mode argument, or are separate functions.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap
- `.planning/REQUIREMENTS.md`: PIN-01, PIN-02, GATE-06..GATE-10 wording, including the GATE-10 sub-items.
- `.planning/ROADMAP.md` § Phase 12: success criteria 1-5.
- `.planning/PROJECT.md` § Current Milestone: red-window context and what is still deferred.

### Prior decisions this phase builds on
- `.planning/phases/08-gate-and-schema-hardening/08-CONTEXT.md`: D-01/D-02 (pre-publication and plain modes, renamed here), D-03 (record `git_show` cross-check), D-04/D-05 (domain-error gates), D-07..D-10 (catalog pinning; the GATE-09 D-10 test), D-11 (shallow check), D-13 (answers grandfathering).
- `.planning/phases/09-certified-republication-2-0-2/09-CONTEXT.md`: D-04 (CI evidence at the record commit, publication-file identity), D-07 (supersedes binding pattern), D-08 (PUB-08 row comparison), D-09/D-10 (dry-run summary; GATE-10's DIFFER branch).
- `.planning/phases/11-frozen-validators/11-CONTEXT.md`: the freeze decisions that limit edits to the reply builder.

### Review findings being closed
- `.planning/phases/08-gate-and-schema-hardening/08-REVIEW.md`: WR-03 (GATE-07), WR-05 (GATE-08), WR-06 and WR-07 (GATE-09).
- `.planning/phases/09-certified-republication-2-0-2/09-REVIEW.md`: IN-01..IN-04 and IN-06 (GATE-10), IN-05 (GATE-06).
- `.planning/phases/11-frozen-validators/11-REVIEW.md`: WR-05, IN-08, IN-09 (D-09..D-11).

### Code
- `scripts/publish_archive_assessment_applicability_authority_v2.py`: `validate_published` (L713), `check_publication_record` (L742), `main` (L766), `SUPERSEDED_V2_0_1` (L36), `dry_run_summary` (L555), `build_all_outputs` publisher_script (L614), `validate_lineage` (L367).
- `scripts/build_archive_assessment_governance_decisions.py`: `validate_decisions` cross-note check (GATE-08).
- `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`: `resolve_record_commit` (L341), frozen.
- `tests/test_archive_assessment_applicability_authority_v2_publication.py`: the existing publisher-script digest tests (L652-655, L686-694), the D-08/D-10/D-13 tests.
- `tests/conftest.py`, `tests/aa_history.py`, `tests/test_archive_assessment_skip_guard.py`: the skip guard and history helper.
- `.github/workflows/ems-validate.yml` L90-99: the archive-assessment pytest step and the six CI validators.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `git_show(commit, rel)` in the publisher: the pinned-blob reader, which already fails closed. Use it for the D-06 blob comparison and the D-07 pinned-script digest.
- `lf_digest`, `lf_bytes`, `rel(SCRIPT)`: the digest helpers already used for `publisher_script`.
- `check_publication_record`: already does the record-to-publication-commit blob cross-checks (08 D-03). Extend it rather than duplicating it.
- `aa_history.require_history` / `history_problem`: the shared fail-closed history check for tests.

### Established Patterns
- **Compact single-quote publisher style:** one-line guards that raise `AuthorityError(...)`.
- **Build/validate separation:** tests mutate a built object and assert a specific `AuthorityError` match (11 D-12/D-13 rigor).
- **Output:** plain `--validate` prints `PASS`, and other CLI modes print JSON with `status`, as `publish()` does.

### Integration Points
- CI runs plain `--validate` at the pushed head, which after publication is the record commit (09 D-04).
- Phase 13's publish sequence uses `--validate --at-pin` at the publication commit. Phase 14's notice (PIN-03) documents both commands for Hayes.

</code_context>

<specifics>
## Specific Ideas

- The at-pin JSON's `deferred` list should contain exactly one item, the publication-record binding. Hayes should be able to read it and know what remains to be checked, and where.
- Byte identity is checked at the git-blob level, comparing the publication commit with HEAD, so CRLF in the working tree on Windows does not cause false differences.

</specifics>

<deferred>
## Deferred Ideas

- 11-REVIEW IN-01..IN-07 (frozen-builder and test polish). Not in Phase 12's requirements, and touching the frozen builders has its own risk. Revisit after 2.0.3.
- V2-01 (decisions for the other 59 controls) and V2-02 (Hayes re-run) stay deferred, per PROJECT.md.
- The IN-04 git-error handling pattern in the frozen 2.0.2 notice builder (D-13).
- `.gitattributes` `eol=lf` for the notice files, which fixes the fresh-Windows-clone failure (D-15).

</deferred>

---

*Phase: 12-verify-at-pin-and-gate-hardening*
*Context gathered: 2026-11-16*
