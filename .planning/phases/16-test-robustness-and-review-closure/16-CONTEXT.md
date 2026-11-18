# Phase 16: Test Robustness and Review Closure - Context

**Gathered:** 2026-11-18
**Status:** Ready for planning

<domain>
## Phase Boundary

The tests and validators that guard the authority become honest about what they check. Every 12-, 14- and 15-REVIEW info item, and 11-REVIEW IN-08/IN-09, gets a recorded disposition: fixed with a test, closed with a reason, or moved to a named later phase. The v1.2.0 planning bookkeeping is corrected.

Phase 16 makes **no publisher edit**. Hash certification stays intact, the red window stays closed, and CI `archive-assessment` stays green with 0 skips through this phase. The red window opens in Phase 17.

Requirements: BASE-01..04, GATE-13, GATE-14, GATE-15, BOOK-01, BOOK-02. GATE-13 and GATE-15 are partly re-routed to Phases 17 and 19 (see D-05, D-03).

Invariants: decisions digest `4e746d1f…`; 21 decided and 59 `NOT_YET_DECIDED`; the frozen reply (2.0.1) and 2.0.2 notice builders are byte-unchanged; **the sent 2.0.3 notice output (JSON, Markdown, schema) is byte-unchanged**; CI green with 0 skips.

</domain>

<decisions>
## Implementation Decisions

### 2.0.3 notice builder (GATE-14, GATE-15)
- **D-01:** The 2.0.3 notice **was sent** to Hayes at `91d8847` (confirmed by the authority 2026-11-18). Its generated text is immutable. Phase 19 (NOTICE-05) records this send commit in a committed artifact; Phase 16 only captures the fact.
- **D-02:** **Behaviour-only fixes** in `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`. Every fix must leave `--build` output byte-identical to the committed `registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json`, `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md` and `schemas/archive_assessment_demo3_w1_req_001_notice_2_0_3.schema.json`. The plan must include an explicit gate for this: rebuild, then `git diff --exit-code` on those three files. In scope:
  - 14 IN-01: remove `pinned_raw_digest`. Add `EXPECTED_LINEAGE_COMMIT` (`catalog_reference`/`v1_baseline` → `CATALOG_COMMIT`, `supersedes` → `PREVIOUS_2_0_2_COMMIT`, everything else → the pin) and fail closed if a lineage entry's `commit` differs. Decide whether `CATALOG_COMMIT` stays, since it is now used.
  - 14 IN-02: wrap malformed-input paths (`JSONDecodeError`, `UnicodeDecodeError`, `KeyError`, `TypeError`, `ValueError`) in the domain `AuthorityError`. Match `pub.GitHistoryError` by class, not by name, and keep the "pinned baseline" context in the re-raised message.
  - 14 IN-03: make `--build` write the schema too, before validating. Write atomically (temp file plus replace) so that a failed validation leaves no partial files. Schema bytes are unchanged because the committed schema already equals `schema()`.
  - 14 IN-04: `copy.deepcopy` the rule dicts taken from the authority.
  - 14 IN-05: use `onexc=` in place of `onerror=`. Make `run()` parse `r.stdout` only and assert `returncode`. The containment test already has the WR-01 live-tamper case; confirm and close it, or strengthen the assertion that is always true.
  - 15 IN-02: remove the duplicated hint test and fold the `core.longpaths` check into `test_git_show_error_names_full_sha_and_fetch_hint`.
  - 15 IN-03: on `OSError` (git missing), the hint says "git unavailable: {e}; install git and ensure it is on PATH" and does not mention fetching history. This is an error path, so it never reaches the output.
- **D-03:** **15 IN-01 (`C:\ems` in the sent registry JSON) is closed for 2.0.3 with the reason "sent text is immutable"** and moved to Phase 19. The 2.0.4 notice builder must avoid absolute-path example text, and its `contains_absolute` must scan the whole string, not only the start. GATE-15's requirement text and traceability are amended to match (D-09).

### Publisher edits timing (GATE-13)
- **D-04:** **No publisher edits in Phase 16.** 12-REVIEW IN-01, IN-02, IN-03 and IN-04, plus IN-06's "move the `lf_digest(SCRIPT)` check to just after the manifest load", are recorded as **DEFERRED-17**. Phase 17 makes them, with tests, inside its single red window alongside SEC-01..04 and GATE-11/12.
- **D-05:** **12 IN-05 (literal pathspecs) is closed as superseded by SEC-04**, and **12 IN-06's decisions-builder scope as superseded by SEC-02**, with cross-references. Phase 17 verification confirms them.
- **D-06:** 12 IN-07 is split:
  - Test-only parts are fixed in Phase 16. The reply test's `cat_exc` case matches `'cannot check whether the frozen commit'`, and `test_at_pin_binding_reads_supersedes_from_authority` drops the source grep and keeps its behavioural assertion.
  - The reply-builder message (regex-failure branch says "not in the repository history") is CLOSED: the builder is frozen and byte-unchanged.

### D-10 baseline test (BASE-01, BASE-03)
- **D-07:** **Mode from the record state.** In the clone, read the publication record. If it names the superseded version (taken from the authority's `source_lineage.supersedes`, not a hard-coded 2.0.2/2.0.3 constant), run `--validate --at-pin`; otherwise run plain `--validate`. Accept `PASS` or a JSON object with `status == 'PASS'`. One test then holds at the publication commit Hayes pins, at the record commit and at later commits.
- **D-08:** **Overlay the working-tree publication paths.** After `git clone --shared`, copy the working-tree versions of the 10 D-05 publication paths and the publisher script into the clone, then commit them there so plain mode's byte-identity check (pub vs HEAD) sees them as committed. Unrelated working-tree changes are never copied.
  - `outcome()` uses `encoding='utf-8', errors='replace'`, takes the result from the last non-empty line of `stdout` only, and keeps `stderr` in the failure message.
- **D-08a:** **Red window:** from Phase 17's first publisher edit, this baseline goes red with the other real-file tests. It joins the Phase 17 accepted red-set inventory and closes at the 2.0.4 publication. Do not weaken it to equality-only.

### Closure record and requirement text
- **D-09:** **One closure ledger:** `.planning/phases/16-test-robustness-and-review-closure/16-REVIEW-CLOSURE.md`.
  - It has a table with one row per item: 11 IN-08 and IN-09; 12 IN-01..IN-07; 14 IN-01..IN-05; 15 IN-01..IN-03.
  - Columns are item, disposition (`FIXED` / `CLOSED` / `DEFERRED-17` / `DEFERRED-19` / `SUPERSEDED-BY-SEC-0x`), reason, and evidence (test name and commit).
  - The historical REVIEW files are not edited. The verifier checks the ledger against GATE-13/14/15.
- **D-10:** **Edit `.planning/REQUIREMENTS.md`:**
  - Reword GATE-13 (IN-01..04 and the IN-06 digest-check move go to Phase 17; IN-05/IN-06 scope are superseded by SEC-04/SEC-02).
  - Reword GATE-15 IN-01 (moves to Phase 19).
  - Add the matching traceability rows in Phase 17 and Phase 19.
  - Adjust the ROADMAP success criteria for Phases 16, 17 and 19 to match.
  - Do this in the same commit as BOOK-02 (V2-01/V2-02 deferred rows; they are already present, so confirm).

### Claude's Discretion
- BASE-02 deep-root `git_show` test mechanics:
  - On Windows with a deep root, assert that `Filename too long` reproduces without `--` (with `core.longpaths=false`) and fail loudly otherwise.
  - On other platforms, assert the `--` behaviour only and make no MAX_PATH claim.
  - There are no skips under `EMS_FAIL_ON_SKIP=1`.
  - The depth threshold, the fallback when the clone root would be ≥240 characters, and how the test forces a deep root are left to the planner and researcher. Start from quick-task 261118-cgq.
- BASE-04 wording in `tests/aa_history.py`: this is a test helper, not a frozen builder, so fix both items there.
  - IN-08: the hint says that `EMS_ALLOW_NO_HISTORY=1` skips only the history-guarded tests and that tests reading pinned history still fail.
  - IN-09: unrecognised `--is-shallow-repository` output is reported verbatim (`is-shallow={out!r}`).
  - Record whatever part, if any, lands only in a frozen builder as CLOSED.
- BOOK-01: the 11–13 SUMMARY files show as `M` only because of line endings (`git diff --ignore-cr-at-eol` is empty). Add `requirements-completed` frontmatter matching v1.2.0 traceability, and stage by explicit path so that only the frontmatter change is committed. Some files use `requirements:`; the planner decides whether to add or rename.
- Plan and commit grouping, and test names.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and scope
- `.planning/REQUIREMENTS.md`: BASE-01..04, GATE-13/14/15, BOOK-01/02, the Out of Scope table (frozen-builder items).
- `.planning/ROADMAP.md` §Phase 16 / 17 / 19: success criteria and invariants (amended per D-10).
- `.planning/milestones/v1.2.0-MILESTONE-AUDIT.md`: tech-debt source (W-2, B-1, N-1).

### Review findings being closed
- `.planning/phases/11-frozen-validators/11-REVIEW.md` §IN-08, §IN-09.
- `.planning/phases/12-verify-at-pin-and-gate-hardening/12-REVIEW.md` §Info IN-01..IN-07 (and WR-02, which feeds SEC-04).
- `.planning/phases/13-certified-republication-2-0-3/13-REVIEW.md` §WR-01 (BASE-01), §IN-02/IN-03 (BASE-03).
- `.planning/phases/14-notice-to-hayes-2-0-3/14-REVIEW.md` §Info IN-01..IN-05; `14-REVIEW-FIX.md` (WR-01 containment shim already applied).
- `.planning/phases/15-address-tech-debt-notice-long-path-git-show-and-step-2-wordi/15-REVIEW.md` §Info IN-01..IN-03.
- `.planning/quick/261118-cgq-make-the-windows-only-deep-root-git-show/261118-cgq-SUMMARY.md`: current deep-root test state (BASE-02 baseline).

### Prior decisions
- `.planning/phases/14-notice-to-hayes-2-0-3/14-CONTEXT.md`: D-01/D-02 pinned-run design, D-12 standalone builder and frozen constants, D-13 schema byte-compare, D-15 test expectations.
- `.planning/phases/13-certified-republication-2-0-3/13-CONTEXT.md`: red-window handling and the publication/record two-commit sequence.
- `.planning/phases/11-frozen-validators/11-CONTEXT.md`: freeze policy for the reply and 2.0.2 notice builders.

</canonical_refs>

<code_context>
## Existing Code Insights

### Files in play
- `tests/test_archive_assessment_lineage_validation.py` (~line 355-375): the D-10 test, `outcome()`, the `git clone --shared` of HEAD (BASE-01/03).
- `tests/aa_history.py` (lines 10, 25-26): `HINT` and the shallow-check message (BASE-04).
- `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`: GATE-14/15 fixes. Relevant lines: `contains_absolute` line 93, the git-missing hint line 102, `pinned_json` lines 152-153, `lineage_entries` lines 160-162 and 219, the rule reference line 399, `--build` lines 571-578.
- `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`:
  - `run()` lines 170-182, `rmtree` lines 619-641.
  - Duplicate hint test ~line 714 vs `test_git_show_error_names_full_sha_and_fetch_hint` ~line 346.
  - The deep-root test.
- `tests/test_archive_assessment_demo3_w1_req_001_reply.py:386` (`cat_exc`), `tests/test_archive_assessment_applicability_authority_v2_publication.py:550` (source grep): 12 IN-07 test parts.
- `tests/conftest.py`: the `EMS_FAIL_ON_SKIP=1` collect-skip guard. Any guard on record state must assert, never skip.

### Established patterns
- Publisher `MODULE.rel()`, `MODULE.PUBLICATION_RECORD`, and the authority `source_lineage.supersedes` give the superseded identity (12-05: at-pin reads supersedes from the authority).
- Domain exceptions: `AuthorityError`, `pub.GitHistoryError`. Tests use a specific `match=`.
- The builder's `validate_notice` byte-rebuild compare already exists. Reuse it as the output-unchanged gate for D-02.

### Integration points
- CI `.github/workflows/ems-validate.yml` `archive-assessment` job runs the 2.0.3 notice `--validate` and pytest with `EMS_FAIL_ON_SKIP=1`. It must stay green.
- Environment: Bash and local `git clone` (sh.exe crash) are unreliable on this machine. Run tests and validators from the orchestrator in PowerShell with `--basetemp`. Clone-based tests may need the CI run (`workflow_dispatch`) as their authoritative evidence.

</code_context>

<specifics>
## Specific Ideas

- The sent 2.0.3 notice must stay byte-identical. It is now treated as frozen output, though its builder still takes behaviour-only fixes.
- "EMS decided" vs "not yet decided" is unaffected: no registry, authority, sign-off or decision file changes in this phase.

</specifics>

<deferred>
## Deferred Ideas

- **Phase 17:** 12 IN-01..IN-04 publisher message, pointer and ordering fixes; IN-06 digest-check placement; IN-05/IN-06 scope through SEC-04/SEC-02; adding the D-10 baseline to the accepted red-set inventory.
- **Phase 19:** 15 IN-01 (no absolute-path example text in the 2.0.4 notice, with a whole-string `contains_absolute`); NOTICE-05 records the 2.0.3 send commit `91d8847`.
- **Out of scope (frozen):** the reply-builder regex-failure message (12 IN-07 builder part).

</deferred>

---

*Phase: 16-test-robustness-and-review-closure*
*Context gathered: 2026-11-18*
