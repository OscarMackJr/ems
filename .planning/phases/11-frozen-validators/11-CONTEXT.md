# Phase 11: Frozen Validators - Context

**Gathered:** 2026-11-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Freeze the two historical validators so that later publisher edits cannot change their results, and make missing pinned history fail loudly instead of skipping:

- the DEMO3 reply builder/validator `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, frozen on 2.0.1 @ `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb`;
- the 2.0.2 notice builder/validator `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`, frozen on 2.0.2 @ `ae15c7458e49c8f55cc58c61bab04bc716aa9892`.

Covers FROZEN-01, FROZEN-02, FROZEN-03 and FROZEN-04 (closes 09-REVIEW WR-02, WR-04 and 10-REVIEW WR-02, WR-03, IN-01).

Out of scope:

- Any edit to `scripts/publish_archive_assessment_applicability_authority_v2.py`, its schema, the authority or the publication files. This phase finishes **before** the first publisher edit (SC4); the red window opens in Phase 12.
- Regenerating the reply or the notice. Their committed bytes (`docs/DEMO3_W1_REQ_001_REPLY.md`, `registry/archive_assessment_demo3_w1_req_001_reply.json`, `docs/DEMO3_W1_REQ_001_NOTICE_2_0_2.md`, `registry/archive_assessment_demo3_w1_req_001_notice_2_0_2.json` and both schemas) must not change.
- Notice claim enforcement (CLAIM-01..03, including 10-REVIEW WR-01/WR-04/WR-05). That is Phase 14 and applies to the 2.0.3 notice builder.
- Publisher review items (GATE-06..10). That is Phase 12.

</domain>

<decisions>
## Implementation Decisions

### Freeze mechanism
- **D-01:** Each frozen builder holds the publisher semantics it needs as **local literals and local code**. This covers `DUAL_ROLE_STATEMENT`, `PREV_COMPARED_KEYS` (notice), `REQUEST_CONTROL_IDS`, `RULE_FIELDS`, `CONDITION_STATES`, `COMBINATION`, `APPROVER_ROLES`, `DECISION_STATES`, `AUTHORITY_ID_RE`, `rule_text`, `validate_signoff`, `closed_schema_levels` (notice), `latest_records` (reply), and the repo-relative path constants (`AUTHORITY`, `SIGNOFF`, `OUT`, `N_TRACE`, `N_MANIFEST`, `N_NEGATIVE`, `PUBLICATION_RECORD`, `GOVERNANCE_DECISIONS`, `SCHEMA`, ...). The runtime path never execs code read from git.
- **D-02:** A pytest proves each literal is correct. It loads the publisher blob at the frozen **publication commit** (reply: `31addfa…`, the existing `REPLY_PUBLICATION_COMMIT`; notice: `ae15c74…`, `NOTICE_PUBLICATION_COMMIT`) with `git show` plus `exec` into a throwaway module, **in the test only**. It then asserts that every frozen constant equals the frozen publisher's value. For the frozen functions (`rule_text`, `validate_signoff`, `closed_schema_levels`, ...), it asserts equal output on representative inputs, including the real frozen inputs. If a literal must differ from that publisher and still rebuilds the committed bytes, the plan records the difference and justifies it.
- **D-03:** Generic helpers are **copied into each builder**: `git_show`, `lf_bytes`, `jtext`, `rel`, `load`, `dump`/`write_text` (if still needed), `contains_absolute`, `AuthorityError`, `GitHistoryError`, and any `NORMALISERS`/`lf_digest` use. Each builder ends with **zero imports** of `publish_archive_assessment_applicability_authority_v2` (no `V2`). Keep the compact single-quote style already used in each builder.
- **D-04:** The frozen schema check stops regenerating the schema. `--validate` requires the committed schema bytes to equal `git_show(<artifact's commit>, <schema path>)`, then validates the committed JSON against that schema. `schema()` is removed from the validate path; the planner decides whether to delete it. The planner also picks the commit constant for each schema: the reply schema's commit (e.g. `e781f08`, full SHA) and the 2.0.2 notice commit. These are full SHAs, and `cat-file -e` and ancestor checks apply, as with the other anchors.

### Frozen CLI modes
- **D-05:** Remove `--build` and `--emit-schema` from both builders. The argparse group offers `--validate`, plus `--push-check` on the reply if kept (D-06). The CLI can no longer write the frozen files. Tests rebuild in memory with `build_*()` and never write repo files. The CI step (`--validate`) is unchanged.
- **D-06 (Claude's discretion):** Keep the reply's `--push-check` if it is read-only and still meaningful against frozen inputs. Remove it if it depends on live state that no longer makes sense. Record the choice and its reason in the plan.

### Skip-to-fail (FROZEN-03)
- **D-07:** The scope is **every `tests/test_archive_assessment_*.py`**. Every `pytest.skip` that fires because a pinned commit or blob is unreachable becomes `pytest.fail`, with an explicit message naming the commit and path and saying to fetch full history. This includes `prev_201_authority_bytes()` (31addfa) in the publication tests, the lineage-validation 2.0.1 skip, the governance_decisions `eed4a5f` skip, the rule_proposals git skip, and the reply and notice tests. The validators themselves already fail closed; check that their errors name the missing commit and path, and fix any that don't.
- **D-08:** `git_ready()` failures (shallow clone, not a repository, no git) **fail by default**. A local opt-out env var (for example `EMS_ALLOW_NO_HISTORY=1`; planner picks the name) restores the skip for offline local runs. CI never sets it. Put this in one shared place, such as `tests/conftest.py` or a small helper, rather than in the 6+ copies of `git_ready`. Whether to de-duplicate those copies is Claude's discretion.
- **D-09:** Existence guards left over from the red-window era also become failures, because the artifacts are committed: `skipif(not REAL_AUTHORITY.exists())`, `skipif(not REAL_RECORD.exists())`, `'answers not yet filled'`, `'decisions not yet built'`, `'not yet written'` (`gated()`), `git commit unavailable` and `git unavailable` in temp-repo fixtures. Temp-repo `git unavailable` cases follow D-08's opt-out.
- **D-10:** CI guard: the `archive-assessment` job in `.github/workflows/ems-validate.yml` fails if the pytest run reports **any skipped test**. Use a conftest hook active under `CI`, or `-rs` plus a summary check; planner's choice. This is a workflow/test change, not a publisher change, so it is allowed before Phase 12.

### Proof of independence (SC1) and test rigor (FROZEN-04)
- **D-11:** SC1 is proven two ways:
  1. **Static:** a test parses both builders with `ast` and asserts that neither imports the v2 publisher module, whether by `import`, `from ... import` or `importlib`/`spec_from_file_location` with its path.
  2. **Behavioural:** a test installs a deliberately **mutated** copy of the live publisher in `sys.modules` under its import name (and at the path the old loader used). The copy has changed `PREV_COMPARED_KEYS`, a changed `DUAL_ROLE_STATEMENT`, a `validate_signoff` that raises and a different `rule_text`. The test asserts that `validate_reply()` and `validate_notice()` still PASS on the committed files. This replaces the narrow `test_validate_independent_of_live_version`, or extends it.
- **D-12:** Notice test rigor (10-REVIEW WR-03, IN-01):
  - each negative test asserts a **specific** error (`match='absolute path'`, `jsonschema.ValidationError` or `match='schema'`, and so on) rather than the broad `REJECTS` tuple;
  - the guarded function is called directly where needed, so the named guard is the one that fires. Example: `digest_scope_error` with an edited `previous`, and `build_notice` with an edited `previous` argument;
  - `test_changed_row_blocks_no_decision_changed` either asserts that `build_notice` raises, or is renamed to what it really tests;
  - one test runs `validate_notice()` against the **committed** repo files with no monkeypatching. It is subject to D-08 only.
- **D-13:** The reply tests get the same treatment as the notice tests: specific matches on negative tests, and a committed-files `validate_reply()` test (add it if missing).

### Carried forward (not re-asked)
- Stage only by explicit path. Never stage `.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json` or the unrelated untracked files.
- The orchestrator runs pytest and validators through PowerShell with `--basetemp`. GSD subagents cannot run them, because Bash is broken and they have no PowerShell.
- Reply and notice bytes stay frozen. Each plan checks this with `git diff` against their commits. The publisher file shows **no diff** at the end of Phase 11 (SC4).
- The reply and notice validators must stay green after every commit in this phase, and the full `-k archive_assessment` suite and the five CI validators stay green. No red window in Phase 11.
- Fail closed without history (07 D-11, 08 D-09/D-11, 09 D-01/D-02); keep the WR-01 record→publication-commit binding.

### Claude's Discretion
- Constant and helper names, and how much of `schema()` / `render_markdown` to keep (the validate path still needs `render_markdown` for the byte rebuild).
- D-06 `--push-check` keep or remove.
- Whether to de-duplicate the `git_ready` copies (D-08).
- The D-10 mechanism.
- How the commits are split. Preferred: (1) freeze the reply, (2) freeze the notice, (3) skip-to-fail plus the CI guard, (4) test rigor. Each commit stages explicit paths and stays green.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope
- `.planning/ROADMAP.md`: Phase 11 goal and SC1-SC4; v1.2.0 ordering (Phase 11 before any publisher edit)
- `.planning/REQUIREMENTS.md`: FROZEN-01..04, plus the out-of-scope table (no regeneration of the reply or notice)
- `.planning/milestones/v1.1.0-MILESTONE-AUDIT.md`: source of the tech debt
- `.planning/PROJECT.md`: constraints
- `.planning/STATE.md`: environment notes (PowerShell, `--basetemp`, push workaround)

### Review findings closed here
- `.planning/phases/09-certified-republication-2-0-2/09-REVIEW.md`: WR-02 (reply depends on live V2; suggested fixes), WR-04 (PUB-08 tests skip silently)
- `.planning/phases/10-notice-to-hayes/10-REVIEW.md`: WR-02 (notice depends on live V2), WR-03 (tests can't fail for their named check), IN-01 (no committed-files test)

### Prior decisions
- `.planning/phases/09-certified-republication-2-0-2/09-CONTEXT.md`: D-01/D-02, frozen reply and anchor constants
- `.planning/phases/10-notice-to-hayes/10-CONTEXT.md`: D-01..D-07, notice files, frozen inputs, `NOTICE_*_COMMIT`
- `.planning/phases/08-gate-and-schema-hardening/08-CONTEXT.md`: D-07..D-11, frozen catalog `CATALOG_COMMIT` pattern, shallow-clone check

### Code
- `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` (341 lines): every `V2.*` use, `schema()`, `render_markdown`, `validate_reply`, `resolve_record_commit`, `main` L327
- `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` (331 lines): every `V2.*` use, `schema()`, `build_notice`, `digest_scope_error`, `validate_notice_object`, `main` L317
- `scripts/publish_archive_assessment_applicability_authority_v2.py`: the source of the literals. **Read-only in this phase**; frozen values come from its blob at 31addfa / ae15c74
- `tests/test_archive_assessment_demo3_w1_req_001_reply.py`, `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`: `git_ready`, `test_validate_independent_of_live_version`, the `REJECTS` tuple
- `tests/test_archive_assessment_*.py`: every `pytest.skip`/`skipif` (inventory from scouting: publication L217/598/602/636/662/686/1057, lineage L53/267/293/300/313/336-361/380, governance_decisions L242-251/285/290/352, governance_answers L63-154, rule_proposals L161/175, rule_proposals_record L34-43, normalisation_claims L36-102, plus the reply and notice tests)
- `.github/workflows/ems-validate.yml`: `archive-assessment` job (L75 fetch-depth 0, L88 pytest, L92-97 validators)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The publisher's `git_show`, `lf_bytes`, `jtext`, `rel`, `contains_absolute` and `AuthorityError` are the bodies to copy (D-03).
- The existing `pinned_bytes`/`pinned_json`/`pinned_digest` and `resolve_record_commit` in both builders already read frozen inputs from git. Only their helper calls change.
- The existing "frozen constants vs git" tests in the reply tests are the pattern for D-02.

### Established Patterns
- Validation = fresh in-memory rebuild compared with committed bytes, plus schema validation, plus binding checks.
- Tests import builders via `importlib` as `MODULE`. They monkeypatch paths for tamper tests and use fakes for shallow or no-history cases.
- Tests that catch `V2.AuthorityError` need to catch the builder's own `MODULE.AuthorityError` after D-03.

### Integration Points
- CI runs `python -m pytest tests -k archive_assessment -p no:cacheprovider -q`, then the five validators. The D-10 guard attaches here.
- Phase 12 will edit the publisher. After this phase, that edit must not touch the reply or notice validator results (the D-11 tests guard this).

</code_context>

<specifics>
## Specific Ideas

- The behavioural proof (D-11) uses a mutated copy of the **live** publisher, which rehearses exactly what Phase 12 will do.
- The literal-vs-git test (D-02) is what keeps local literals honest. Without it, copying constants would just move the drift risk.

</specifics>

<deferred>
## Deferred Ideas

- Notice claim enforcement for the 2.0.2 notice (WR-01/WR-04/WR-05). Not retrofitted. CLAIM-01..03 apply to the 2.0.3 notice builder in Phase 14.
- A mutation-sweep meta-test that disables each guard and asserts its test goes red. Rejected for D-12 as heavier and brittle.
- Executing the historical publisher from git at runtime. Rejected for D-01.

</deferred>

---

*Phase: 11-frozen-validators*
*Context gathered: 2026-11-14*
