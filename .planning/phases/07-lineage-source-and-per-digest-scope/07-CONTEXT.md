# Phase 7: Lineage Source and Per-Digest Scope - Context

**Gathered:** 2026-10-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Every digest in the AA3 v2 `source_lineage` declares its own normalisation and can be recomputed from a committed file, and the AA1 manifest is committed and verified. Covers LIN-01, LIN-02, LIN-03. This phase changes the publisher's lineage builder, the schema it generates and its `--validate` path. It does not publish 2.0.2 (Phase 9), and it does not touch the gates or schema strictness of Phase 8.

</domain>

<decisions>
## Implementation Decisions

### Lineage shape (LIN-01)
- **D-01:** Each lineage digest becomes an object: `{relative_path, sha256, normalisation}`, plus `commit` where the digest is pinned to a commit. The flat `aa1_manifest_sha256` / `aa2_closure_sha256` / `aa2_approval_sha256` keys are replaced by objects (for example `aa1_manifest`, `aa2_closure`, `aa2_approval`; the planner picks the exact key names). This is a deliberate breaking shape change in a new version, 2.0.2. The Phase 10 notice must describe it.
- **D-02:** The global `source_lineage.digest_normalisation` field is removed. Nothing in the lineage may state a scope that contradicts a digest.
- **D-03:** Every digest in the lineage carries an explicit `normalisation`. This includes the nested `governance_decisions`, `supersedes`, `v1_baseline` and `catalog_reference` entries. The validator treats all of them uniformly.
- **D-04:** The normalisation vocabulary is a closed enum, `RAW_BYTES | CRLF_TO_LF`, enforced by the generated schema (fail closed).

### AA1 manifest (LIN-03)
- **D-05:** The file is `generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json`, which already exists at this path and is gitignored. Verified 2026-10-20: raw-byte SHA-256 = `f0da8e2e45c306ccc42ae96f25a19922668f3eedecdb26006f13514e24ad9b4b` (exact match). It has 87 CRLF line endings, and its LF-normalised digest would be `06e39f7b…`. It is committed in place with `git add -f`, in a commit of its own that stages only that file and `.gitattributes`.
- **D-06:** Add `.gitattributes` rule `generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json -text` (file-specific, like `ems-aa2/approval/** -text`) so git never converts its CRLF bytes.
- **D-07:** If the committed file's raw-byte hash read back from a fresh checkout does not equal `f0da8e2e…`, stop and do not commit. Never change the recorded digest to fit the file.
- **D-08:** Commit the manifest only. The 13 AA1 artifacts the manifest lists stay untracked. Lineage cites only the manifest's hash.

### Validator (LIN-02)
- **D-09:** Lineage recomputation is a new `validate_lineage(...)` inside `scripts/publish_archive_assessment_applicability_authority_v2.py`, called from the existing `--validate` path. CI already runs that path. No separate script.
- **D-10:** Digests that carry a `commit` (`supersedes`, `v1_baseline`) are recomputed from `git show <commit>:<relative_path>`. All other digests are recomputed from the checked-out file. The declared normalisation is applied in both cases.
- **D-11:** If git history is unavailable for a commit-pinned digest, validation fails closed. Unlike the frozen-catalog behaviour of 06 D-03, it never passes silently. The CI `archive-assessment` job already checks out with `fetch-depth: 0`.
- **D-12:** Negative tests: a changed byte in a cited file, a changed declared normalisation, and a changed recorded digest each make `validate_lineage` fail. Tests cover both `RAW_BYTES` and `CRLF_TO_LF` entries.

### Normalisation sweep
- **D-13:** Audit every other `digest_normalisation` claim. These are the publication record, the certification, the publication manifest, `decision_record_digest_normalisation` in the traceability, and the record and pin fields the reply builder reads. For each claim, add a pytest that recomputes the digest and proves the claim. Change the shape only where a claim is false. Expected result: these claims are genuinely LF and stay as they are.
- **D-14:** Do not touch the DEMO3 reply, its builder or its schema in Phase 7. Its two digests really are LF, and it is a sent 2.0.1 artifact. Hayes learns of 2.0.2 through the Phase 10 notice.

### Claude's Discretion
- Exact object key names in `source_lineage` and the structure of the `validate_lineage` helper, matching the publisher's compact style.
- How the `lf_digest` / raw `digest` helpers are selected by normalisation, for example a small mapping `{'RAW_BYTES': raw, 'CRLF_TO_LF': lf}`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope
- `.planning/ROADMAP.md` — Phase 7 goal, success criteria, red-window and staging rules
- `.planning/REQUIREMENTS.md` — LIN-01, LIN-02, LIN-03
- `.planning/PROJECT.md` — constraints (publication pattern, working tree, authority)

### Prior decisions
- `.planning/phases/06-address-tech-debt-publication-gate-hardening-2-0-1/06-CONTEXT.md` — LF-normalised hashing, D-03 frozen catalog, D-09 script digest, D-12 decisions-digest pin
- `.planning/milestones/v1.0.0-MILESTONE-AUDIT.md` — origin of the lineage digest-scope debt

### Code
- `scripts/publish_archive_assessment_applicability_authority_v2.py` — `build_authority` lineage (lines ~151-157), schema `source_lineage` (~302-308), `lf_digest`, publication record (~632)
- `tests/test_archive_assessment_applicability_authority_v2.py` (line ~144, lineage keys) and `tests/test_archive_assessment_applicability_authority_v2_publication.py` (lines ~78, 227-228, 416-417, which assert `CRLF_TO_LF`). These need updating.
- `scripts/publish_archive_assessment_applicability_authority.py:78` — v1 origin of the `aa1_manifest_sha256` constant and raw `digest()` for AA2 files
- `.gitattributes` — existing `-text` rule for `generated/archive-assessment/ems-aa2/approval/**`
- `.github/workflows/ems-validate.yml` — `archive-assessment` job, `fetch-depth: 0`

### Data
- `generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json` — the AA1 manifest to commit
- `generated/archive-assessment/ems-aa2/approval/` — AA2 closure and approval files (raw-byte digests, committed in `35bfc08`)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `digest(p)` (raw bytes) in the v1 publisher and `lf_digest(p)` in the v2 publisher. These are the two normalisations, and `validate_lineage` can dispatch on them.
- The existing v2 `--validate` path and its negative-mutation harness, where new lineage mutations can be added.

### Established Patterns
- The schema is generated by the publisher (`schema()`), so the enum and object shape are publisher changes, never hand edits.
- `build_*` / `validate_*` pairs, `AuthorityError` on violation, compact single-quote style in `publish_*` scripts.
- Explicit-path staging only. `generated/` is gitignored, so certified outputs are force-added.

### Integration Points
- Lineage objects flow into the authority JSON, the generated schema, certification and traceability. The real-file tests go red here (accepted red window, which closes at Phase 9 publication).

</code_context>

<specifics>
## Specific Ideas

- The AA1 manifest's CRLF bytes are the reason a raw-byte digest is correct for it. The notice should say this plainly.

</specifics>

<deferred>
## Deferred Ideas

- Committing the 13 AA1 analysis artifacts the manifest lists. This is out of LIN-03 scope and could be a future lineage-completeness item.
- Re-pointing the DEMO3 reply to 2.0.2. Not planned; the Phase 10 notice supersedes it for Hayes.

</deferred>

---

*Phase: 07-lineage-source-and-per-digest-scope*
*Context gathered: 2026-10-20*
