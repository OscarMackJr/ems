# Phase 9: Certified Republication 2.0.2 - Context

**Gathered:** 2026-11-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Publish `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2`. It carries the Phase 7 lineage, the Phase 8 gates and the stricter schema. Every applicability decision stays identical to 2.0.0 and 2.0.1. The steps:

- a dry run;
- sign-off by Oscar Mack as EMS governance authority;
- the publication commit;
- the publication-record commit;
- a push and a green CI run.

Covers PUB-07, PUB-08 and PUB-09.

This phase closes the accepted red window. It does not write the notice to Hayes (Phase 10). It does not regenerate the DEMO3 reply. It does not decide any of the other 59 controls.

The phase includes a few code changes that must land before the publication commit:

- moving the supersession binding from 2.0.0 to 2.0.1;
- the row comparison with 2.0.1;
- the "what changed" section of the sign-off summary;
- freezing the reply validator.

</domain>

<decisions>
## Implementation Decisions

### Reply after 2.0.2
- **D-01:** The DEMO3 reply (`docs/DEMO3_W1_REQ_001_REPLY.md` and `registry/archive_assessment_demo3_w1_req_001_reply.json`) is a sent 2.0.1 artifact and is frozen. Its bytes do not change.
  - `build_archive_assessment_demo3_w1_req_001_reply.py --validate` stops reading the live authority, publication record and sign-off.
  - It rebuilds the reply from the 2.0.1 inputs, read with `git_show` at their commits, and requires byte equality with the committed reply.
  - Without git history it fails closed, consistent with 07 D-11 and 08 D-09.
  - The Phase 10 notice supersedes the reply for Hayes.
- **D-02:** The 2.0.1 anchors are named constants in the reply script, in the style of `CATALOG_COMMIT` from Phase 8:
  - publication commit `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb`;
  - publication-record commit `4d9b7c1` (use the full SHA).

  `resolve_record_commit` must no longer derive the record commit from `git log` on the live record path, because after 2.0.2 that would return the 2.0.2 record commit. The GATE-04 shallow-clone check (08 D-11) stays. Tests must prove three things:
  - the reply validator still passes after the record and authority change to 2.0.2;
  - tampering with the reply bytes or a constant fails it;
  - it fails closed without history.
- **D-03:** This change lands in a code commit before the publication commit, like every other code change in the milestone.

### CI evidence (PUB-09)
- **D-04:** Hayes pins the publication commit. The publication record still names 2.0.1 at that commit, so plain `--validate` (08 D-02) and the reply validator are red there by design. The green CI run is therefore taken on the **publication-record commit** that follows it. A check, either a test or a verification step, proves that every publication file is byte-identical between the publication commit and the record commit, using `git diff --stat <pub>..<record>` limited to the publication paths, or digest equality. The plan states this rewording of ROADMAP SC4 explicitly. No gate is weakened, and no CI auto-detect or pre-publication CI mode is added.
- **D-05:** After the record commit there is a blocking checkpoint. On Oscar Mack's go-ahead, Claude does the following:
  - pushes `feature/ems-aa3-archive-applicability-authority` with the GitHub CLI token workaround recorded in STATE.md (one-command `http.extraheader` via `GIT_CONFIG_*`, credential.helper cleared);
  - dispatches the `archive-assessment` workflow on the branch (`gh workflow run`);
  - waits for it to finish and confirms it passed at the record commit's SHA.

  Nothing is pushed without that go-ahead. No PR, merge or tag is made in this phase.
- **D-06:** The CI run id and the publication SHA are recorded in planning docs only (`09-VERIFICATION.md` and STATE.md), as run 38744767442 was. The publication record and the schemas do not change shape. The publication SHA is already recorded in the publication-record commit.

### Supersession lineage
- **D-07:** `source_lineage.supersedes` names 2.0.1 only. `SUPERSEDED_V2_0_0` is replaced by a `SUPERSEDED_V2_0_1` binding:
  - authority id, version `2.0.1` and commit `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb`;
  - the 2.0.1 authority LF sha256 (`7be5eb88…`, from the 2.0.1 publication record);
  - the 2.0.1 governance-decisions LF sha256 (still `4e746d1f…`).

  The values come from the files and git, never typed by hand. Every use of the superseded binding follows this change: validator checks, schema `pinned(...)`, the `supersedes_governance_digest_differs` mutation, the pre-publication branch at L719-721 (which must now check the 2.0.1 record: commit `31addfa`, authority sha `7be5eb88…`), and the dry-run summary. No separate 2.0.0 anchor entry is added. 2.0.0 stays reachable through 2.0.1's own lineage. "No decision changed since 2.0.0" holds because the decisions digest is unchanged along the chain.
- **D-08:** PUB-08 is enforced in the publisher validator and also in pytest. Validation reads the 2.0.1 authority with `git_show(31addfa, registry/archive_assessment_applicability_authority_v2.json)`. All 80 rows' decision content must be value-equal to it: `not_applicable_decision_state`, `not_applicable_rule`, `not_applicable_authority` and `decision_ids`. The top-level `applicability_decision_ids` must also be equal. Validation fails closed without history. Pytest drives a tampered row to failure. The existing decisions-digest binding (06 D-12) still holds against `4e746d1f…`.

### Sign-off summary
- **D-09:** The 2.0.2 dry-run and sign-off summary keeps everything in 06 D-21:
  - 21 decided and 59 undecided;
  - each control with its AA4 id and state;
  - the 3 rules in full;
  - the authority LF digest;
  - the supersedes and no-decision-changed line, now naming 2.0.1 @ `31addfa`.

  It adds a short, neutral "what changed in 2.0.2" section.
- **D-10:** The "what changed" section is derived from the built authority and the code wherever possible:
  - each lineage entry with its declared normalisation, including that the AA1 manifest is committed and `RAW_BYTES`;
  - the mutation count (29) and the schema levels that set `additionalProperties: false`;
  - the 2.0.1 → 2.0.2 row-comparison result (D-08).

  A short fixed line names the gate fixes (GATE-01..05: publication-record check and pre-publication mode, domain-error-only mutation gate, frozen catalog reference, shallow-clone record lookup, `norm_templated` uniqueness). The wording is plain and adds no ranking or emphasis.

### Carried forward (not re-asked)
- Sequence (08 specifics, 06 D-21): code commits, then a dry-run publish and the blocking sign-off checkpoint. Then the sign-off record (role `EMS_GOVERNANCE_AUTHORITY`, date, exact dual-role statement), then `--publish`, then the publication commit. Then `--validate --pre-publication` (the record still names 2.0.1), then `--record-publication <sha>`, then the record commit. Then plain `--validate` PASS and the full archive-assessment pytest suite, which closes the red window. Then the D-05 push and CI checkpoint.
- Overwrite the v2 files in place (06 D-07). No publication history file. `PUBLISHED_ON` comes from the sign-off date (06 D-10).
- The publication commit holds only the generated publication: the v2 registry authority, the `ems-aa3-v2/` outputs, the sign-off and the regenerated schema. `git show --stat` lists only those (04 D-20, 06 D-22).
- Stage only by explicit path. Unrelated modified and untracked files stay out of every commit.
- The red window closes at the publication and record commits. Every red test is listed in the plan that touches it.
- Tests and validators are run by the orchestrator through PowerShell, with `--basetemp`. GSD subagents cannot run them.

### Claude's Discretion
- Constant and helper names (`SUPERSEDED_V2_0_1`, reply anchor constants), in the compact single-quote publisher style.
- Whether the publication-file byte-identity check in D-04 is a pytest or a verification-step command.
- How the code commits before publication are split, provided each one stages explicit paths and the red set only shrinks or stays as listed.
- Whether the Phase 6 D-13 comparison test against 2.0.0 @ `54a7fd0` is kept alongside the new 2.0.1 comparison (keeping it is preferred).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope
- `.planning/ROADMAP.md` — Phase 9 goal, success criteria, ordering guarantees, red window, staging, sign-off
- `.planning/REQUIREMENTS.md` — PUB-07, PUB-08, PUB-09
- `.planning/PROJECT.md` — constraints (authority, dual role, working tree)
- `.planning/STATE.md` — push token workaround, CI run history, environment notes

### Prior decisions
- `.planning/phases/08-gate-and-schema-hardening/08-CONTEXT.md` — D-01/D-02 pre-publication vs plain `--validate`; D-03 commit-content check; D-07..D-09 frozen catalog; D-11 shallow check in the reply; Phase 9 sequence in specifics
- `.planning/phases/08-gate-and-schema-hardening/08-VERIFICATION.md` and `08-REVIEW-FIX.md` — final state of the gates and the current red set
- `.planning/phases/07-lineage-source-and-per-digest-scope/07-CONTEXT.md` — lineage shape; D-10/D-11 `git_show` fail closed; D-14 reply untouched
- `.planning/phases/06-address-tech-debt-publication-gate-hardening-2-0-1/06-CONTEXT.md` — D-07 overwrite in place; D-08 lineage; D-10 published-on; D-12/D-13 no-decision-change proof; D-17..D-20 mutations; D-21/D-22 process and hygiene
- `.planning/phases/04-certified-publication/04-CONTEXT.md` — D-17 byte-identical `--validate`; D-19 sign-off; D-20 publication commit contents; D-21 publication record

### Code
- `scripts/publish_archive_assessment_applicability_authority_v2.py`:
  - `VERSION` L34 and `SUPERSEDED_V2_0_0` L36
  - lineage and validator uses L242-L320; schema `pinned` L379; mutation L490
  - `validate_signoff` L509; `dry_run_summary` L533; `publish` L672
  - `validate_published` L684 (pre-publication branch L719-721); `write_publication_record` L730; `main` L737
- `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` — live reads L231/L253; `resolve_record_commit` L262-L280; `PIN_KEYS` L28
- `registry/archive_assessment_applicability_authority_v2_publication_record.json` — the 2.0.1 record (source of the `SUPERSEDED_V2_0_1` values)
- `.github/workflows/ems-validate.yml` — `archive-assessment` job (pytest `-k archive_assessment` plus five validators, `fetch-depth: 0`)
- `tests/test_archive_assessment_applicability_authority_v2_publication.py`, `tests/test_archive_assessment_lineage_validation.py` — `env` fixture and temp git repo fixture

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `git_show`, `lf_digest`, `COMMIT_PINNED` and `NORMALISERS` in the v2 publisher serve the 2.0.1 row comparison and the frozen reply inputs.
- `dry_run_summary` already prints the supersedes and no-decision-changed line. Extend it for D-09/D-10.
- `MUTATIONS` and the `schema()` generator supply the derived counts for the change list.

### Established Patterns
- The superseded binding is one constant that the validator, schema, mutation and pre-publication branch all read. Swapping the constant moves them together. Check every reference.
- The reply builder imports the publisher as `V2` and reuses its loaders and `validate_signoff`. The frozen path must reuse the same helpers on `git_show` bytes.
- Real-file tests are red until the publication commit, and some are red until the record commit. List both sets.

### Integration Points
- The reply validator and plain `--validate` both run in CI. After the record commit, all five validators and pytest must pass at the same SHA.
- 63 local commits are not on origin. The D-05 push publishes the whole milestone branch.

</code_context>

<specifics>
## Specific Ideas

- Hayes pins the publication commit, and CI evidence comes from the record commit. Because no publication file differs between the two (D-04), the green run certifies the pinned bytes.
- The "what changed" list in the sign-off summary previews the Phase 10 notice content.

</specifics>

<deferred>
## Deferred Ideas

- A CI mode that validates the publication commit itself in pre-publication mode (rejected for D-04; adds workflow code and a temporary ref).
- A tracked CI-evidence field in the publication record (rejected for D-06).
- An explicit 2.0.0 `decisions_origin` anchor in 2.0.2's lineage (rejected for D-07).
- Opening a PR or merging to main, and tagging: left to the EMS authority.
- Regenerating the DEMO3 reply for 2.0.2: not planned; the Phase 10 notice informs Hayes.

</deferred>

---

*Phase: 09-certified-republication-2-0-2*
*Context gathered: 2026-11-12*
