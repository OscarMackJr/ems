# Phase 10: Notice to Hayes - Context

**Gathered:** 2026-11-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce a generated, `--validate`-checked notice to Hayes Verify about `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2`. The notice:

- tells Hayes which authority, version and commit to re-pin to (publication commit `ae15c7458e49c8f55cc58c61bab04bc716aa9892`);
- says what changed between 2.0.1 and 2.0.2;
- names the 2.0.1 digest-scope error;
- states that no applicability decision changed;
- asks Hayes to re-pin.

Covers NOTICE-01 and NOTICE-02.

Out of scope:

- The authority, the publication, the publisher and the DEMO3 reply do not change. The reply is a frozen 2.0.1 artifact (09 D-01), and this notice supersedes it for Hayes.
- No other controls are decided.
- No republication.
- Sending the notice is the EMS authority's action; it is not part of this phase.

</domain>

<decisions>
## Implementation Decisions

### Notice form and files
- **D-01:** The notice is three files, like the DEMO3 reply:
  - Markdown for people: `docs/DEMO3_W1_REQ_001_NOTICE_2_0_2.md`.
  - JSON for Hayes to parse: `registry/archive_assessment_demo3_w1_req_001_notice_2_0_2.json`.
  - A schema for the JSON: `schemas/archive_assessment_demo3_w1_req_001_notice_2_0_2.schema.json`.

  `--validate` requires a byte-for-byte rebuild of all three and validates the JSON against the schema.
- **D-02:** A new builder script generates it, e.g. `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`. It imports the v2 publisher as `V2`, as the reply builder does. The frozen reply builder `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` is not modified.
- **D-03:** File names are tied to the request (`DEMO3_W1_REQ_001_NOTICE_2_0_2`), so Hayes reads the notice as a follow-up to the request that the reply answered.

### Where the content comes from
- **D-04:** Inputs are frozen from day one.
  - Named constants: `NOTICE_PUBLICATION_COMMIT` = `ae15c7458e49c8f55cc58c61bab04bc716aa9892` and `NOTICE_RECORD_COMMIT` = `a71257ed267410138a3c4daba412b00c116663d8`. Use full SHAs.
  - Every input is read with `git_show` at these commits (the 2.0.2 authority, manifest, sign-off, negative-invariant validation output, schema and record), and at `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb` for the 2.0.1 authority. Never read the live working-tree files.
  - Apply the reply lessons:
    - The record read at `NOTICE_RECORD_COMMIT` must name `NOTICE_PUBLICATION_COMMIT` as its `publication_commit`. This is the WR-01 binding.
    - Check the commit exists and is an ancestor.
    - Fail closed without history (shallow-clone check as in GATE-04).

  A later 2.0.3 must not break or silently re-point the notice.
- **D-05:** The "what changed" list is derived, not hand-written. Derive it from the frozen 2.0.2 artifacts rather than from live publisher code, so a later publisher edit cannot change the notice (review WR-02 lesson). It includes:
  - each `source_lineage` entry with its declared normalisation, stating that the AA1 manifest is committed and hashed `RAW_BYTES`, which closes review WR-03;
  - the negative-mutation count and the closed schema levels (`additionalProperties: false`), read from the frozen outputs and schema;
  - the 2.0.1 → 2.0.2 row-comparison result (80 controls identical).

  One fixed line names the gate fixes: GATE-01..05 and the roadmap WR labels (WR-02, WR-04, catalog decoupling, WR-05, `norm_templated` uniqueness). The wording is plain, with no ranking or emphasis.
- **D-06:** The 2.0.1 digest-scope error is derived from the two authorities. 2.0.1 at `31addfa` declared one global `CRLF_TO_LF` normalisation; 2.0.2 declares the normalisation per digest. The notice names the digests whose declared scope was wrong: `aa1_manifest_sha256`, `aa2_closure_sha256`, `aa2_approval_sha256`. `--validate` fails if the stated digests do not match what git shows.

### What the notice cites
- **D-07:** The notice cites one commit to pin: `ae15c74…`, given as the full SHA, together with the authority id `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2`, version `2.0.2`, authority LF sha256 `a44eea1f…` and manifest sha256 `9991228a…`. It names `a71257e…` only as the commit that records the publication and changes no authority bytes, as the reply did with `4d9b7c1`. CI run ids are not cited; they stay in planning docs (09 D-06).
- **D-08:** Decision content:
  - counts: 21 decided (3 rules, 18 no-rule) and 59 `NOT_YET_DECIDED`;
  - the 3 rules in machine form (CTRL-030, CTRL-039 `production = KNOWN_FALSE`; CTRL-052 `ai_enabled = KNOWN_FALSE`);
  - the governance decisions LF sha256 `4e746d1f…`, unchanged.

  For the 18 no-rule reasons, the notice points to the reply and the decisions file instead of repeating them.
- **D-09:** The notice stands alone on what Hayes still has to do. It says plainly that `ae15c74` replaces `31addfa` as the re-pin target. It restates the other two Hayes-side steps from the reply: the target description must carry the eight classification facts, and Hayes must read the v2 shape. ROADMAP SC3 requires it to ask Hayes to re-pin.

### Voice, date and send condition
- **D-10:** The notice is written as from Oscar Mack acting as EMS governance authority. It includes the exact `DUAL_ROLE_STATEMENT` (read from the frozen sign-off or publisher, not retyped) and stays unsigned in the repository until it is sent.
- **D-11:** A `NOTICE_DATE` constant holds the day the notice is generated, so `--validate` rebuilds identical bytes. The 2.0.2 publication date (2026-11-12, `published_on` from the sign-off) is cited separately.
- **D-12:** Oscar Mack reviews the rendered Markdown at a **blocking checkpoint** before the notice commit, as he reviewed the reply wording in Phase 5. Any change is made by regenerating, never by hand-editing the generated files.
- **D-13:** The phase ends with a **blocking push checkpoint**. On Oscar Mack's go-ahead, Claude pushes the branch: the notice commit plus the 7 local commits from the Phase 9 close-out, including the WR-01 fix `6e47a4f`. Claude then dispatches `ems-validate.yml` and confirms it is green at the pushed HEAD. The notice states it must not be sent until its own commit is on the remote branch. No PR, merge or tag.

### Carried forward (not re-asked)
- Stage only by explicit path. Unrelated modified and untracked files stay out of every commit. Never stage `.planning/config.json`, `registry/adjudication_rules.json` or `registry/policy_decisions.json`.
- The orchestrator runs tests and validators through PowerShell with `--basetemp`. Subagents do not run pytest.
- The authority, publication files, publisher and reply artifacts must not change in this phase. The plan checks this with `git diff` against `ae15c74`/`a71257e` for the publication paths and against `e781f08` for the reply.
- ROADMAP SC1: changing the cited id, version or commit in the notice must make `--validate` fail. Tamper tests cover each.

### Claude's Discretion
- Constant, helper and section names in the new builder, matching the reply builder's style.
- Whether the new `--validate` is added to the CI `archive-assessment` job's validator list. Preferred: add it, as a separate code commit, since the job already runs the reply validator.
- The exact JSON shape of the notice and its schema (closed with `additionalProperties: false`, following the Phase 8 schema strictness).
- How the code commits are split, provided each stages explicit paths.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope
- `.planning/ROADMAP.md`: Phase 10 goal and success criteria SC1-SC4
- `.planning/REQUIREMENTS.md`: NOTICE-01, NOTICE-02
- `.planning/PROJECT.md`: constraints (authority, dual role, working tree, boundary)
- `.planning/STATE.md`: publication and CI facts, environment notes (push, PowerShell, `--basetemp`)

### Prior decisions
- `.planning/phases/09-certified-republication-2-0-2/09-CONTEXT.md`: D-01/D-02, the frozen reply (pattern for D-04 here); D-04, pinned vs CI commit; D-06, CI ids in planning docs only; D-10, "what changed" content
- `.planning/phases/09-certified-republication-2-0-2/09-VERIFICATION.md`: publication and record SHAs, digests, SC4 reading
- `.planning/phases/09-certified-republication-2-0-2/09-REVIEW.md`: WR-01 (constant binding), WR-02 (live-code dependency), WR-03 (AA1 RAW_BYTES statement owed to the notice)
- `.planning/phases/09-certified-republication-2-0-2/09-SECURITY.md`: non-blocking notes carried forward
- `.planning/phases/07-lineage-source-and-per-digest-scope/07-CONTEXT.md`: per-digest normalisation and the AA1 manifest commit (`bb7c067`)
- `.planning/phases/08-gate-and-schema-hardening/08-CONTEXT.md`: GATE-01..05 and SCHEMA-07 meanings

### Code and artifacts
- `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`: pattern to follow (`pinned_bytes`/`pinned_json`/`pinned_digest`, `resolve_record_commit`, `REPLY_*_COMMIT` binding, byte-rebuild `validate_reply`, `render_markdown`, schema)
- `tests/test_archive_assessment_demo3_w1_req_001_reply.py`: test pattern (frozen constants vs git, tamper, shallow/fail-closed fakes)
- `docs/DEMO3_W1_REQ_001_REPLY.md`: tone, section layout and the Hayes-side steps to restate
- `scripts/publish_archive_assessment_applicability_authority_v2.py`: `git_show`, `lf_bytes`, `jtext`, `DUAL_ROLE_STATEMENT`, `SUPERSEDED_V2_0_1`, `dry_run_summary` (the "what changed" precedent)
- `registry/archive_assessment_applicability_authority_v2.json` at `ae15c74`: 2.0.2 `source_lineage`
- `registry/archive_assessment_applicability_authority_v2.json` at `31addfa`: 2.0.1 lineage with the global normalisation claim
- `generated/archive-assessment/ems-aa3-v2/` at `ae15c74`: manifest, negative-invariant validation (mutation count)
- `.github/workflows/ems-validate.yml`: `archive-assessment` job validator list

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `V2.git_show`, `V2.lf_bytes`, `V2.jtext`, `V2.rel` and `V2.AuthorityError`/`GitHistoryError` for frozen reads and deterministic output.
- From the reply builder: `pinned_*` helpers, `resolve_record_commit` (shallow check, `cat-file -e`, `merge-base --is-ancestor`), and the byte-rebuild validation structure.
- `rows_differing_from_previous` and `closed_schema_levels` in the publisher. These are live code; per D-05, prefer recomputing from frozen bytes or reading the frozen outputs.

### Established Patterns
- Generated documents carry a "generated, read-only, rebuild with the script" header line.
- Validation is a fresh rebuild compared to committed bytes, plus a schema check, plus binding checks on every cited value.
- Tests use `git_ready()` skips for real-history cases and fakes for shallow or no-history cases. Review WR-04 warns that skips make evidence fail open, so keep at least one non-skipping fail-closed test.

### Integration Points
- CI `archive-assessment` job: add `python scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py --validate` (Claude's discretion, preferred).
- The `pytest -k archive_assessment` selection picks up new tests named `test_archive_assessment_*`.

</code_context>

<specifics>
## Specific Ideas

- The notice is the place to say that the AA1 manifest is now committed and hashed as RAW_BYTES. The signed-off dry-run summary left this out (review WR-03), so the notice has to carry it.
- "Re-pin to ae15c74 instead of 31addfa" should be stated plainly, because the reply Hayes already holds names 31addfa.
- Hayes deferred its re-pin to `31addfa` to a later Hayes phase (quick 261019-st1 note), so it may go straight from its current pin to `ae15c74`.

</specifics>

<deferred>
## Deferred Ideas

- Citing the CI run id in the notice (rejected for D-07; kept in planning docs).
- Regenerating the DEMO3 reply for 2.0.2 (rejected in 09 D-01; the notice supersedes it).
- Opening a PR, merging to main, tagging: left to the EMS authority.
- Review hardening items WR-02/WR-04/IN-05 on the existing reply and publisher tests: separate follow-up, not this phase.

</deferred>

---

*Phase: 10-notice-to-hayes*
*Context gathered: 2026-11-13*
