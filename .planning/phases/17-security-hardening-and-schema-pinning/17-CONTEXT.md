# Phase 17: Security Hardening and Schema Pinning - Context

**Gathered:** 2026-11-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Before the single 2.0.4 republication (Phase 18), the publisher, the validator and the git seam reach their final 2.0.4 form:

- Pinned code is never executed before its digest is checked.
- A hostile caller environment cannot redirect a fail-closed check.
- The schema rejects drifted lineage digests.
- The sign-off scope carries no unchecked digest.

Requirements: SEC-01, SEC-02, SEC-03, SEC-04, GATE-11, GATE-12, and the DEFERRED-17 items from `16-REVIEW-CLOSURE.md`:
- 12-REVIEW IN-01..IN-04;
- 12-REVIEW IN-06, the `lf_digest(SCRIPT)` check move;
- 12-REVIEW IN-05, confirmed superseded by SEC-04;
- 12-REVIEW IN-06, decisions-builder scope, confirmed superseded by SEC-02.

This phase **opens the red window** at its first publisher edit. The window closes at the Phase 18 publication commit. No publication, sign-off or decision change happens here.

Invariants:
- The decisions digest stays `4e746d1f…`, with 21 decided and 59 `NOT_YET_DECIDED`.
- The frozen reply (2.0.1) and 2.0.2 notice builders stay byte-unchanged.
- The sent 2.0.3 notice output (JSON, MD and schema) stays byte-identical. Its builder takes behaviour-only fixes, with a gate of rebuild followed by `git diff --exit-code`, as in 16 D-02.
- CI `archive-assessment` stays at 0 skips. Red appears only as listed in the red-set ledger.

</domain>

<decisions>
## Implementation Decisions

### Carried forward (not re-asked)
- **D-01: Final 2.0.4 form**, following the 12 "final form" pattern:
  - `VERSION = '2.0.4'` and the id constant for 2.0.4.
  - A `SUPERSEDED_V2_0_3` constant replaces `SUPERSEDED_V2_0_2`: authority id, version 2.0.3, commit `1544dc19ba235d732c832d1651895550ed5a265d`, the 2.0.3 authority LF sha256 (`696116e7…`) and the decisions LF sha256 (`4e746d1f…`).
  - Values come from files and git and are never typed by hand.
  - Every dependent use moves with it: validators, the schema, mutations, the row comparison against 2.0.3, the dry-run summary and the at-pin supersedes binding.
- **D-02: Red-window ledger** `17-BASELINE-RED.md`, following `12-BASELINE-RED.md`.
  - Each commit that touches the publisher lists the red set it produces, and the red set may only shrink or stay as listed.
  - The D-10 baseline test (`tests/test_archive_assessment_lineage_validation.py`) joins the ledger at the first publisher edit and is not weakened (16 D-08a).
- **D-03: DEFERRED-17 publisher fixes, each with a test**, using the 12-REVIEW fix text:
  - IN-01: the plain-mode messages say "working tree" in place of "committed".
  - IN-02: the message says "the record still names the superseded X publication (HEAD is the publication commit or earlier)".
  - IN-03: at-pin, when the record already names this publication, the error says "the record already names this publication; run plain --validate here".
  - IN-04: `git_not_shallow()` runs at the top of `validate_published` in both modes, before any history read.
  - IN-06: the live `lf_digest(SCRIPT)` check moves to just after the manifest load.
- **D-04:** 12 IN-05 (literal pathspecs) and 12 IN-06 (decisions-builder scope) are verified as closed by SEC-04 and SEC-02. Phase verification cross-checks them against `16-REVIEW-CLOSURE.md`.

### Pinned-code checks (SEC-01, SEC-02)
- **D-05: SEC-01, hash before exec, in the 2.0.3 notice builder now.**
  - `load_pinned_publisher` in `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` reads the pinned publisher blob and compares its LF sha256 with the pinned manifest's `publisher_script.sha256`.
  - Only after that comparison passes does it run `exec_module` or `decisions_builder()`. The current post-exec check (around line 322) moves ahead of exec.
  - This is a behaviour-only change, and the output stays byte-identical.
  - A test tampers with the pinned blob or the digest and proves the publisher **did not run**, for example through a sentinel side effect or an exec spy. The error is a fail-closed `AuthorityError`.
  - Phase 19's 2.0.4 notice builder must copy this order.
- **D-06: SEC-02 for 2.0.4 mirrors GATE-06.**
  - The publication manifest gains a `decisions_builder_script` entry `{relative_path, sha256, sha256_normalisation: 'CRLF_TO_LF'}`, a sibling of `publisher_script`, with a matching note.
  - `--validate` checks the live `scripts/build_archive_assessment_governance_decisions.py` LF digest against it in both modes. In plain mode it also checks the builder at the publication commit.
  - The check runs **before** `decisions_builder()` imports or executes the builder.
  - Manifest schema and validation are updated to match: a missing or invalid entry fails closed.
- **D-07: SEC-02 for the 2.0.3 notice builder uses a frozen constant.**
  - The 2.0.3 manifest at `1544dc1` has no builder digest. The builder therefore gets a frozen constant: the LF sha256 of `scripts/build_archive_assessment_governance_decisions.py` at `1544dc1`, computed from git and never typed.
  - The constant is checked before the pinned decisions builder executes.
  - This is a behaviour-only change and the output is unchanged.
  - The closure record notes that this is not a manifest digest. The full SEC-02 manifest binding starts at 2.0.4.

### Git seam isolation (SEC-04)
- **D-08: Scope.** Three callers get the sanitized environment:
  - the publisher's `git_show` and `git_run` (every git call goes through them);
  - the 2.0.3 notice builder's own git calls and its `live_git_subprocess` shim, which pinned code runs git through, as a behaviour-only change;
  - `tests/aa_history.py`.

  The frozen reply and 2.0.2 notice builders are not touched, and the ledger records them as CLOSED (frozen).
- **D-09: Isolation depth.**
  - Build `env=` from `os.environ` with **every** `GIT_*` variable dropped.
  - Then set `GIT_NO_REPLACE_OBJECTS=1`, `GIT_LITERAL_PATHSPECS=1`, `GIT_CONFIG_NOSYSTEM=1`, and `GIT_CONFIG_GLOBAL` pointing to an empty file or the null device.
  - Pass any setting the seam needs explicitly on the command line (`-c key=value`), for example `core.longpaths=true` on Windows.
  - Pathspecs are literal. `git_dirty` already passes `--literal-pathspecs`; the env makes this the default.
  - A test sets a hostile `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` and `GIT_OBJECT_DIRECTORY`, plus a `refs/replace` substitution (or `GIT_REPLACE_REF_BASE`), and shows that each fail-closed check still reads the intended repository and blob.
- **D-10: One copy per script, not a shared module.**
  - Each script defines its own sanitized-env builder, which keeps the certified publisher self-contained inside its digest (14 D-12 standalone pattern).
  - A test asserts that the copies produce the same variable policy.

### Sign-off scope (GATE-12)
- **D-11: 2.0.4 scope is free text with no digests.**
  - The authority's own words.
  - `validate_signoff` rejects any run of 7 to 64 hex characters in `scope`.
  - The scope must contain `AUTHORITY_ID` and `VERSION`, and both are checked.
  - Digests and commits live only in checked fields: `authority_sha256`, and the authority's `source_lineage.supersedes`.
- **D-12: The rule applies from 2.0.4 forward only.**
  - The historical 2.0.2 and 2.0.3 sign-offs are immutable and still validate under their own rules, through the pinned and frozen publishers at their commits.
  - The new rule binds sign-offs with version >= 2.0.4.
  - The Phase 18 runbook gives the authority the scope constraint before they type it.

### Schema pin breadth (GATE-11)
- **D-13: Pin every fixed lineage digest with `const`.**
  - The four pinned digests: `supersedes.sha256`, `supersedes.governance_decisions_sha256`, `v1_baseline.sha256` and `governance_decisions.sha256` (`4e746d1f…`).
  - With these pinned, the schema alone enforces "no decision changed" and the historical lineage.
  - The `aa1_manifest`, `aa2_closure`, `aa2_approval` and `catalog_reference` digests stay pattern-checked and are recomputed by the validator.
  - Schema mutations are added for each newly pinned field, so a different 64-hex value fails schema validation.
- **D-14: The const values come from constants and are cross-checked by a test.**
  - `schema()` emits the const values from `SUPERSEDED_V2_0_3` and the related constants.
  - A test recomputes each value from the git blob at its commit and asserts equality.
  - Nothing is hand-typed.

### Claude's Discretion
- The CI secret scan (SEC-03) mechanics: drop `--exclude='*.md'` from `.github/workflows/ems-validate.yml`. The planner checks that no existing `.md` file trips the pattern, for example docs that quote token formats. Any narrow exclusion must be justified and listed.
- Whether `git_show` switches to `git cat-file blob` (the WR-02 suggestion). Keep the Phase 15 `--` and long-path behaviour.
- Hostile-env test mechanics, the empty-config-file approach on Windows vs Linux CI, and test names.
- Commit grouping and order. Preferred order: green-safe test, CI and builder commits first (SEC-03, the 2.0.3 builder behaviour-only fixes, `aa_history.py`), then the publisher edits that open the red window. Each commit stages explicit paths and lists its red set.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and scope
- `.planning/REQUIREMENTS.md`: SEC-01..04, GATE-11, GATE-12, GATE-13 (DEFERRED-17 wording), and the Out of Scope table (frozen builders).
- `.planning/ROADMAP.md` §Phase 17 and §Phase 18: success criteria and the red-window invariant.
- `.planning/phases/16-test-robustness-and-review-closure/16-REVIEW-CLOSURE.md`: the DEFERRED-17 and SUPERSEDED-BY-SEC rows this phase closes.
- `.planning/phases/16-test-robustness-and-review-closure/16-CONTEXT.md`: D-02 (behaviour-only builder fixes and the byte-identical gate), D-04/D-05, and D-08a (the D-10 baseline joins the red set).

### Review and security findings
- `.planning/phases/12-verify-at-pin-and-gate-hardening/12-REVIEW.md`: §WR-02 (git seam env, the source of SEC-04) and §IN-01..IN-06.
- `.planning/phases/13-certified-republication-2-0-3/13-REVIEW.md`: §WR-02 (schema pins, GATE-11) and §IN-01 (sign-off scope, GATE-12).
- `.planning/phases/14-notice-to-hayes-2-0-3/14-SECURITY.md`: §Observations 1-3 (the sources of SEC-01, SEC-02 and SEC-03).

### Prior patterns
- `.planning/phases/12-verify-at-pin-and-gate-hardening/12-CONTEXT.md`: the final-form constant move, the red-window rules and D-16 red-set ledger.
- `.planning/phases/12-verify-at-pin-and-gate-hardening/12-BASELINE-RED.md`: the ledger format.
- `.planning/phases/14-notice-to-hayes-2-0-3/14-CONTEXT.md`: D-01/D-02 (pinned-run design) and D-12 (standalone builder, frozen constants).
- `.planning/phases/15-address-tech-debt-notice-long-path-git-show-and-step-2-wordi/15-REVIEW.md`: the long-path `git_show` behaviour to preserve.

</canonical_refs>

<code_context>
## Existing Code Insights

### Files in play
- `scripts/publish_archive_assessment_applicability_authority_v2.py`. Line numbers are as of 2026-11-18:
  - `VERSION` L34, `SUPERSEDED_V2_0_2` L36-44, lineage build L184;
  - validator uses L251, L292, L323, L326, L349;
  - `git_show` and `git_run` L367-377, `git_not_shallow` L395, `git_dirty` L403 (already uses `--literal-pathspecs`), `git_commit_blob` L411;
  - `schema()` L463 with `pinned()` L470-472. The `sha_keys` exemption is what GATE-11 removes;
  - mutations around L587, `validate_signoff` L607-621 (scope non-empty check at L620-621);
  - manifest `publisher_script` L693-694, `decisions_builder()` L701;
  - `validate_published` L792, with the manifest `publisher_script` check at L812-814.
- `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`:
  - `PINNED_CODE` L75;
  - git calls at L123, L188 and L305;
  - `load_pinned_publisher` L281-297 (exec at L289, `decisions_builder()` at L290);
  - `live_git_subprocess` L300-306;
  - the post-exec digest check at L322-324.
- `registry/archive_assessment_applicability_authority_v2_signoff.json`: the 2.0.3 scope that carries the digest, which is the GATE-12 example. It is immutable.
- `.github/workflows/ems-validate.yml` L60-66: the secret-pattern step with `--exclude='*.md'`.
- `tests/aa_history.py` L15: the test-side git call.

### Research risks to verify
- With `GIT_CONFIG_NOSYSTEM`/`GIT_CONFIG_GLOBAL` isolation on Windows, Git for Windows' system `core.autocrlf` no longer applies. Confirm that `git status --porcelain` in `git_dirty` and `git_index_flags` does not then report CRLF working files as modified. Pass `-c core.autocrlf=...` explicitly if needed.
- Confirm the same isolation for `safe.directory` (CI runner ownership) and `core.longpaths`.
- `cat-file` and `show` blob bytes are unaffected by autocrlf.

### Established patterns
- Domain exceptions are `AuthorityError` and `GitHistoryError`. Tests use a specific `match=`.
- Mutations are a list of `Mutation(...)` entries. Every new schema pin gets one.
- The scratchpad `check.ps1` pattern (the full suite plus the validators) is used at each red-set checkpoint.
- Environment: Bash and local `git clone` are unreliable on this machine. Run tests and validators from the orchestrator in PowerShell with `--basetemp`. CI `workflow_dispatch` is the authoritative evidence for clone-based tests.

</code_context>

<specifics>
## Specific Ideas

- "EMS decided" vs "not yet decided" is unaffected. No decision file or row changes, and the decisions digest is now pinned in the schema itself.
- The authority (Oscar Mack) types the 2.0.4 sign-off scope in Phase 18. It must contain the id and version and no hex digests.

</specifics>

<deferred>
## Deferred Ideas

- **Phase 18:** the 2.0.4 publication, the sign-off (scope under D-11) and closing the red window.
- **Phase 19:** the 2.0.4 notice builder copies the SEC-01 hash-before-exec order and SEC-04 seam isolation, and adds 15 IN-01 (whole-string `contains_absolute`).
- **Out of scope (frozen):** SEC-04 for the reply (2.0.1) and 2.0.2 notice builders.

</deferred>

---

*Phase: 17-security-hardening-and-schema-pinning*
*Context gathered: 2026-11-18*
