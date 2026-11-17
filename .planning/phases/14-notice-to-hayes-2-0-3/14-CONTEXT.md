# Phase 14: Notice to Hayes (2.0.3) - Context

**Gathered:** 2026-11-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce a generated, `--validate`-checked notice to Hayes Verify about `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3`, published at `1544dc19ba235d732c832d1651895550ed5a265d` and recorded at `87a46d147413bd99e931c71a1ab165eb0903f014`. The notice:

- cites the 2.0.3 id, version and publication commit, and asks Hayes to re-pin;
- lists what changed and states that no decision changed;
- gives the exact commands to verify at the pin and at the record commit, and what each result means (PIN-03);
- enforces its claims instead of asserting them: the mutations are actually run (CLAIM-01), all 7 lineage digests are recomputed from git (CLAIM-02), and every "declared under the wrong scope" statement is computed (CLAIM-03).

Covers NOTICE-03, PIN-03, CLAIM-01, CLAIM-02, CLAIM-03.

Out of scope:
- The authority, publication files, publication record and publisher do not change. No republication.
- The frozen 2.0.1 reply and the frozen 2.0.2 notice (builders, files, tests) do not change.
- No other controls are decided.
- Sending the notice is the EMS authority's action, out of band.

</domain>

<decisions>
## Implementation Decisions

### Running the mutations (CLAIM-01)
- **D-01:** The builder runs the mutations from the **pinned publisher blob**: it reads `scripts/publish_archive_assessment_applicability_authority_v2.py` with `git_show` at `1544dc1…`, loads it as a module, and runs its `run_mutations` (with `NEGATIVE_MUTATIONS` and `mutation_gates`) on the frozen inputs at the pin (authority, sign-off, governance decisions). The pinned publisher's `decisions_builder()` loads `scripts/build_archive_assessment_governance_decisions.py` from its live path; that builder (and its schema) must also come from the pin, not the working tree. The researcher must work out how to load both pinned modules so that no live file is executed and the pinned module's path constants do not redirect reads to live files. A later publisher edit must not change the result.
- **D-02:** **Rerun equals recorded.** The builder fails with a domain error unless: every mutation is rejected (non-empty `rejected_by`, result `REJECTED_FAIL_CLOSED`), the frozen negative-invariant output at the pin has `result == 'PASS'`, and the rerun's per-mutation list (`id`, `rejected_by`, `result`) equals the frozen file entry for entry, in order. This catches both a mutation that is not rejected and a recorded file that overstates.
- **D-03:** The notice JSON lists each mutation (`id`, `rejected_by`). The Markdown gives the count, says each mutation was run by the builder and rejected, and points to the JSON for the list.

### What the notice says
- **D-04:** **Re-pin framing.** "Re-pin to `1544dc1…`. It replaces `ae15c74…` (2.0.2) and `31addfa…` (2.0.1); if Hayes pins either, move straight to `1544dc1…`." Full SHAs throughout. This works whether or not Hayes acted on the 2.0.2 notice. The other two Hayes-side steps from the reply and 2.0.2 notice are restated (eight classification facts on the target description; read the published v2 shape).
- **D-05:** **The 2.0.1 digest-scope error is repeated and computed** (CLAIM-03), because Hayes may jump from `31addfa` directly. For each of the three RAW_BYTES files (`aa1_manifest`, `aa2_approval`, `aa2_closure`) the builder computes the raw sha256 and the LF sha256 of the bytes at the pin, requires them to differ, and shows both in the notice. 2.0.1's global `CRLF_TO_LF` claim is read from the 2.0.1 authority at `31addfa`. `--validate` fails if any pair is equal or does not match git.
- **D-06:** **What changed in 2.0.3** is derived data plus one fixed line:
  - derived: `source_lineage.supersedes` moved from 2.0.1 at `31addfa` to 2.0.2 at `ae15c74`; 0 of 80 rows differ from 2.0.2 on the compared keys; the decisions digest `4e746d1f…` is unchanged; the mutation count (from the D-01 rerun) and the closed schema levels (from the frozen schema at the pin);
  - one fixed, plain line naming the verification changes: `--validate --at-pin`, plain-mode byte identity, GATE-06..GATE-10, frozen validators. No ranking or emphasis words.
- **D-07:** **All 7 lineage digests are recomputed** (CLAIM-02). Each entry lists key, path, normalisation, sha256 and the commit it was recomputed at: the pin for `aa1_manifest`, `aa2_approval`, `aa2_closure` and `governance_decisions`; the commit named in the lineage entry for `catalog_reference` (`62a8955…`), `v1_baseline` (`62a8955…`) and `supersedes` (`ae15c74…`). The hash uses the declared normaliser. The validator fails on any mismatch.
- **D-08:** Decision content as in 10 D-08: counts (21 decided: 3 rules, 18 no-rule; 59 `NOT_YET_DECIDED`), the 3 rules in machine form, the governance decisions LF sha256 unchanged, and a pointer to the reply and decisions file for the 18 no-rule reasons.

### Verify-at-pin guidance (PIN-03)
- **D-09:** **Full command sequence**, with prerequisites (Python 3.12, `pip install -r requirements.txt`, a full non-shallow clone, no local edits to the pinned paths):
  1. `git clone https://github.com/OscarMackJr/ems.git`, `git checkout 1544dc1…` (full SHA), install requirements, `python scripts/publish_archive_assessment_applicability_authority_v2.py --validate --at-pin`.
  2. `git checkout 87a46d1…` (the record commit, full SHA), then plain `python scripts/publish_archive_assessment_applicability_authority_v2.py --validate`. The notice says this also passes at any later commit on the branch.
  3. At the notice commit or later, `python scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py --validate`, which rebuilds the notice and reruns the mutations and digests.
- **D-10:** The repository URL `https://github.com/OscarMackJr/ems.git` is a fixed constant in the builder, never read from `git remote`, so output does not depend on operator config.
- **D-11:** **Per-outcome table** explaining results:
  - at-pin PASS: one JSON object, `status` PASS, `mode` `AT_PIN`, exactly one `deferred` item starting `PUBLICATION_RECORD_BINDING`. The deferred text is quoted from the pinned publisher blob (`AT_PIN_DEFERRED`), not retyped. Meaning: pinned bytes are certified; run step 2 next;
  - plain PASS at the record commit or later: the record names the pin and the publication files are byte-identical between the two commits;
  - plain `--validate` run at the pin fails by design and points to `--at-pin`;
  - any other failure, including a shallow clone: do not consume the authority; report to EMS.

### Builder form and gates
- **D-12:** **New standalone builder** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, in the 2.0.2 builder's compact style, with its own frozen constants (`NOTICE_PUBLICATION_COMMIT = 1544dc19ba235d732c832d1651895550ed5a265d`, `NOTICE_RECORD_COMMIT = 87a46d147413bd99e931c71a1ab165eb0903f014`, the 2.0.2 and 2.0.1 commits, ids and versions, request ids, `DUAL_ROLE_STATEMENT`, `NOTICE_DATE`). It copies helpers rather than importing the 2.0.2 builder or the live publisher. Files: `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md`, `registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json`, `schemas/archive_assessment_demo3_w1_req_001_notice_2_0_3.schema.json` (closed, `additionalProperties: false`). Inputs read via `git_show` at the frozen commits with record binding, existence and ancestry checks, and fail-closed shallow check (10 D-04, 12-03 uniform git-error handling).
- **D-13:** **Schema is validated from the live committed file**, byte-compared with the builder's schema function. No frozen-schema commit constant in this phase.
- **D-14:** **Gates as in Phase 10:** a blocking review of the rendered Markdown by Oscar Mack before the notice commit (any change by regenerating, never by hand edit); then a blocking push checkpoint. On go-ahead, push the branch (the notice commits plus the local `.planning` commits after `5498002`) with the STATE.md token workaround, dispatch `ems-validate.yml`, and confirm it is green at the pushed head. The notice states it must not be sent until its own commit is on the remote branch. No PR, merge or tag.
- **D-15:** **CI and tests:** add the 2.0.3 notice `--validate` to the `archive-assessment` job (separate code commit). New `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` validates the committed files, covers tamper of each cited id/version/commit, and has one test per claim that fails for its named reason with a specific `match=` (mutation not rejected; rerun differs from recorded; frozen negative result not PASS; wrong lineage digest for each of the 7; raw equals LF for a RAW_BYTES file; live publisher edit does not change the build or `--validate`). Keep at least one non-skipping fail-closed history test.

### Carried forward (not re-asked)
- Notice voice: from Oscar Mack as EMS governance authority, exact dual-role statement read from the frozen sign-off, unsigned in the repository until sent (10 D-10). `NOTICE_DATE` constant; the 2.0.3 `published_on` (2026-11-17) cited separately (10 D-11).
- The notice cites one pin (`1544dc1…`) with authority LF sha256 and manifest sha256; names `87a46d1…` only as the record commit; CI run ids stay in planning docs (10 D-07, 09 D-06).
- No dependency on live publisher constants or functions (FROZEN-02, 10-REVIEW WR-02).
- Generated header line ("generated, read-only, rebuild with the script").
- Stage only by explicit path. Never stage `.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json` or the unrelated untracked files.
- The orchestrator runs pytest and validators through PowerShell with a fresh `--basetemp` and `-p no:cacheprovider`, recording pytest's own exit code. Subagents do not run pytest.
- The plan checks with `git diff` that the publication files, record, publisher, the frozen reply and the frozen 2.0.2 notice files are unchanged.

### Claude's Discretion
- Constant, helper and section names; exact JSON shape of the notice and schema (closed).
- Exact wording of the fixed verification-changes line and the outcome table, provided it is plain and accurate.
- How code commits are split (each with explicit paths), and whether the CI line lands with the builder or separately (preferred: separate).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope
- `.planning/ROADMAP.md` § Phase 14: goal and success criteria 1-4.
- `.planning/REQUIREMENTS.md`: NOTICE-03, PIN-03, CLAIM-01, CLAIM-02, CLAIM-03.
- `.planning/PROJECT.md`: constraints (authority, dual role, working tree, boundary).
- `.planning/STATE.md`: 2.0.3 publication facts (PUB `1544dc1`, REC `87a46d1`, WR-03 `5498002`), push token workaround, environment notes.

### Prior decisions
- `.planning/phases/10-notice-to-hayes/10-CONTEXT.md`: D-01..D-13, the 2.0.2 notice pattern this phase follows.
- `.planning/phases/10-notice-to-hayes/10-REVIEW.md`: WR-01 (CLAIM-01), WR-04 (CLAIM-02), WR-05 (CLAIM-03), WR-02 (live-code dependency), WR-03 (tests that cannot fail for their named reason).
- `.planning/phases/11-frozen-validators/11-CONTEXT.md`: freeze decisions; frozen builders stay untouched.
- `.planning/phases/12-verify-at-pin-and-gate-hardening/12-CONTEXT.md`: D-01..D-08 at-pin and plain modes, the deferred item, D-05 publication paths.
- `.planning/phases/13-certified-republication-2-0-3/13-CONTEXT.md` and `13-VERIFICATION.md`: publication and record SHAs, at-pin evidence in tree and fresh clone, CI evidence.

### Code and artifacts
- `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`: pattern to follow (frozen constants, `pinned_*` helpers, `resolve_record_commit`, `lineage_entries`, `digest_scope_error`, `build_notice`, `render_markdown`, byte-rebuild `validate_notice`).
- `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`: test pattern (committed-file validation, tamper, fail-closed fakes).
- `docs/DEMO3_W1_REQ_001_NOTICE_2_0_2.md`: tone and section layout.
- `scripts/publish_archive_assessment_applicability_authority_v2.py` at `1544dc1`: `NEGATIVE_MUTATIONS`, `run_mutations` (L740), `mutation_gates` (L718), `decisions_builder` (L701), `NORMALISERS` (L73), `AT_PIN_DEFERRED` (L828), `validate_published` (L792).
- `scripts/build_archive_assessment_governance_decisions.py` at `1544dc1`: loaded by the pinned publisher's mutation gates.
- `registry/archive_assessment_applicability_authority_v2.json` at `1544dc1`: 2.0.3 `source_lineage` (7 entries).
- `generated/archive-assessment/ems-aa3-v2/` at `1544dc1`: manifest, negative-invariant validation.
- `registry/archive_assessment_applicability_authority_v2_publication_record.json` at `87a46d1`: record naming `1544dc1`.
- `.github/workflows/ems-validate.yml`: `archive-assessment` job validator list.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- 2.0.2 notice builder helpers (copy, don't import): `git_show`, `pinned_bytes`/`pinned_json`/`pinned_digest`/`pinned_raw_digest`, `resolve_record_commit`, `lineage_entries`, `rows_differing`, `digest_scope_error`, `closed_schema_levels`, `validate_signoff`, `rule_text`.
- Pinned publisher `run_mutations` returns `{mutation, id, description, rejected_by, result}` per mutation; the frozen negative output records the same.

### Established Patterns
- Validation = fresh rebuild compared byte-for-byte to committed files + schema check + binding checks on every cited value.
- Tests assert specific error messages so each fails for the check it names (11 D-12/D-13, 10-REVIEW WR-03).
- Line endings: generated notice files are compared after LF normalisation as the 2.0.2 builder does; `.gitattributes eol=lf` stays deferred (12 D-15).

### Integration Points
- CI `archive-assessment` job: add `python scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py --validate`.
- The pytest glob `tests/test_archive_assessment_*.py` picks up the new test file automatically.

</code_context>

<specifics>
## Specific Ideas

- Hayes may still be pinned at `31addfa` or earlier, so the notice must stand alone: re-pin target, the computed scope error and the verification steps.
- The notice's own `--validate` is offered to Hayes as a third verification step, so Hayes can check the notice's claims (mutations rerun, digests recomputed), not just the authority.
- The at-pin deferred text is quoted from the pinned publisher so the notice and the tool output cannot disagree.

</specifics>

<deferred>
## Deferred Ideas

- Freezing the 2.0.3 notice schema at a commit constant (D-13): later, if needed.
- Opening a PR, merging to main, tagging: left to the EMS authority.
- WR-02 ambient `GIT_*` scrubbing (12-SECURITY AR-03), 11-REVIEW and 12-REVIEW IN items, `.gitattributes eol=lf` (12 D-15): still deferred.
- V2-01 (other 59 controls) and V2-02 (Hayes re-run): still deferred.

</deferred>

---

*Phase: 14-notice-to-hayes-2-0-3*
*Context gathered: 2026-11-17*
