# Phase 4: Certified Publication - Research

**Researched:** 2026-10-14
**Domain:** Spec-driven authority publication (Python 3.12, jsonschema, pytest) plus git hygiene on a dirty Windows working tree
**Confidence:** HIGH (all findings come from reading this repo's code, files and git state in this session; no external libraries are new)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** All three critical findings (CR-01 line-ending hashing, CR-02 answers binding, CR-03 strict checks on superseding entries) and all nine warnings (WR-01..09) in `03-REVIEW.md` are fixed before anything is published, with tests for each. Info items IN-01..05 are not in scope.
- **D-02:** A new, narrow `.gitattributes` lists only this project's files as `text eol=lf`: the `archive_assessment_*` registry and schema JSON this project created, `docs/ARCHIVE_ASSESSMENT_RULE_PROPOSALS_VIEW.md`, the v2 registry authority and the `generated/archive-assessment/ems-aa3-v2/` outputs. No broad globs.
- **D-03:** v1.0.0 files are NOT listed in `.gitattributes` and are not touched. Their raw-byte manifest is a recorded v1 limitation.
- **D-04:** Every SHA-256 that this phase writes or checks (manifest, certification, lineage, frozen-input digests) is taken over LF-normalised bytes (CRLF->LF), and the document states this in a normalisation field, following the existing `answers_sha256_normalisation` precedent.
- **D-05:** All generated files are written with `newline='\n'` (fixes WR-08).
- **D-06:** The review fixes land in their own commits, before the `.gitattributes` commit, the publisher-code commit and the publication commit.
- **D-07:** If the fixes require rewriting `registry/archive_assessment_governance_decisions.json`, only header digest/normalisation fields and newline bytes may change. Every record must be value-equal to the version at commit `eed4a5f`. A test proves this against `git show eed4a5f:<path>`. The answers file is not rewritten.
- **D-08:** Per control, the AA4-GOV id goes in `not_applicable_authority` only. `decision_ids` keeps exactly the eight AA1-GOV-001..008 ids on all 80 rows.
- **D-09:** A new top-level list (working name `applicability_decision_ids`) holds the 21 AA4-GOV ids. `approved_governance_decision_ids` stays the eight AA1 ids. Every `not_applicable_authority` must appear in the new list, and every id in the list must be cited by exactly one control. Needs a schema change in the v2 publisher (`schema()`), regenerated, not hand-edited.
- **D-10:** `source_lineage` gains a `governance_decisions` entry with `relative_path`, LF `sha256`, `record_count` and `drafting_commit`. The validator checks the digest against the live decisions file, that each cited id is the latest unsuperseded record for that control, and that decided state and rule match that record.
- **D-11:** Control rows stay lean: decision state, rule and authority id only. Traceability output joins control -> AA4 id -> record.
- **D-12:** The v2 validator pins the decided set to exactly the 21 request ids (EMS-CTRL-009, 010, 011, 012, 013, 014, 015, 017, 018, 019, 020, 021, 022, 030, 033, 039, 042, 052, 062, 075, 079) and requires every other control to be `NOT_YET_DECIDED`.
- **D-13:** The validator and a test compare all 80 rows field by field with the v1.0.0 registry file. Only added fields: `not_applicable_decision_state` on all rows and non-null rule/authority on the 21. Any other difference fails.
- **D-14:** Registry authority is `registry/archive_assessment_applicability_authority_v2.json`. Generated outputs go in `generated/archive-assessment/ems-aa3-v2/`, force-added as v1's were. v1 `ems-aa3/` untouched.
- **D-15:** Output set mirrors v1's (authority matrix, semantic validation, negative-invariant validation, publication certification JSON, publication report `.md`, publication manifest) plus an AA4 decision-to-control traceability file (21 records plus the 59 undecided controls). Names follow v1 with a v2 marker.
- **D-16:** No `now()`. A fixed `published_on` constant in the publisher stamps the outputs; re-running publish is byte-identical.
- **D-17:** `--validate` rebuilds the authority and every output in memory and requires equality with the committed files and with every LF digest in the manifest before printing `PASS`. A pytest runs the same check. A consistent hand edit plus a re-hash must fail.
- **D-18:** The publisher reads tracked inputs only: catalog, v1 authority, governance decisions, proposals, drafting record. AA2 lineage digests are copied from the v1 registry file. Must work on a fresh clone and ubuntu CI.
- **D-19:** Human gate: after a dry-run publish, execution stops at a blocking checkpoint with a summary (21 decided / 59 undecided; per control the AA4 id and state; the three rules in full; authority LF digest). Oscar Mack approves. Approval recorded in a tracked file (approver, role, date, authority LF digest, scope) and cited by the certification.
- **D-20:** The publication commit holds only the v2 registry authority, the `ems-aa3-v2/` outputs and the sign-off record. Publisher code, schema change and tests land earlier. `git show --stat` on it lists only those files.
- **D-21:** A small follow-up commit adds a publication record (publication commit SHA, authority id and version, manifest and authority LF digests). A test checks the SHA is an ancestor containing the authority with that digest (Phase 2 pattern, same shallow-clone handling). Phase 5 cites this SHA.
- **D-22:** No push, tag or merge. The last step reports the publication SHA and the push command.

### Claude's Discretion
- Exact names for the new top-level id list, lineage entry, normalisation field, v2 output files, sign-off record and publication record (snake_case, `archive_assessment_*` / v1 naming with a v2 marker).
- Whether v2 build/publish code extends `scripts/publish_archive_assessment_applicability_authority_v2.py` (preferred) or a sibling script; CLI flag names (`--publish`, `--validate`, `--emit-schema`).
- How the LF digest helper is shared (import from one place; do not duplicate the normalisation rule).
- How tests behave before the publication commit exists (real-file tests skip when the v2 registry file or publication record is absent, then go active).
- How many commits the review fixes take and in what order; each stages explicit paths only.
- The exact `published_on` date value.
- Wording of the sign-off summary (neutral, complete, no ranking or emphasis).

### Deferred Ideas (OUT OF SCOPE)
- IN-01..05 from the Phase 3 review.
- Extending `.gitattributes` to v1 files or repo-wide globs.
- Annotated tag, pushing, merging to main.
- Copying rationale or scope-note rulings into authority rows.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PUB-01 | New authority version carries 21 decisions, each citing its decision id | Overlay from `registry/archive_assessment_governance_decisions.json` onto `build_authority()` (Pattern 1); `applicability_decision_ids` list; D-10 binding |
| PUB-02 | Other 59 controls undecided, otherwise unchanged | D-13 field-by-field diff against v1 rows (Pattern 3); v1 row fields confirmed present in v2 rows |
| PUB-03 | Certification, manifest, decision-to-control traceability with SHA-256 | v1 `publish()` output set to mirror (Pattern 2); LF digest; fixed `published_on` |
| PUB-04 | Tests for 21/59/vocabulary/authority invariants | Test plan with skip-gating (Validation section); existing v2 tests keep passing if validators are split |
| PUB-05 | Lineage from AA3 v1.0.0 at `62a8955` | `supersedes` block already in `build_authority()`; fix its CRLF-sensitive sha256 |
| PUB-06 | Publication commit contains only this project's changes | Explicit-path staging protocol (Git section); `git show --stat` test |
</phase_requirements>

## Summary

Phase 4 is an extension of existing, working code, not new technology. No new packages are needed (stdlib, `jsonschema` 4.26.0, `PyYAML`, `pytest` are already installed and used). The hard parts are (a) fixing the Phase 3 review debt so the validators can be trusted as a gate, (b) making every digest independent of line endings on this `core.autocrlf=true` machine, and (c) keeping the publication commit pure while the working tree holds two modified registry files and about 60 untracked files.

Current state, verified this session: 270 archive-assessment tests pass on this machine. The v2 publisher (`scripts/publish_archive_assessment_applicability_authority_v2.py`) has `build_authority()` (all 80 rows `NOT_YET_DECIDED`), `validate_authority(a, known_decision_ids=None)`, `schema()`, `resolve_applicability()` and a CLI with only `--validate`/`--emit-schema`. There is no publish step and no `.gitattributes`. The v2 registry file does not exist yet. The decisions file holds 21 records AA4-GOV-001..021: 3 `RULE_PUBLISHED` (GOV-014 CTRL-030, GOV-016 CTRL-039 both `production KNOWN_FALSE`; GOV-018 CTRL-052 `ai_enabled KNOWN_FALSE`) and 18 `NO_RULE_WILL_BE_PUBLISHED`, no superseding records, so id n maps to the n-th control in the request list.

**Primary recommendation:** Plan five commit groups in this order: (1) Phase 3 review fixes with tests (incl. shared `lf_digest`, decisions header rewrite); (2) narrow `.gitattributes`; (3) v2 publisher/schema/tests; (4) blocking human sign-off then the publication commit (authority + `ems-aa3-v2/` + sign-off record only); (5) publication-record follow-up. Keep `validate_authority` as the generic structural validator (existing tests keep passing) and add a separate `validate_publication` for the 21/59 pin, v1 diff, decisions binding and id-list checks.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Authority build and overlay | Publisher script (`scripts/`) | registry JSON | Pure `build_*` reads tracked registry inputs, returns dict |
| Validation gate | Publisher script (`validate_*`) | JSON Schema in `schemas/` | Fail-closed `AuthorityError`; schema emitted from code |
| Certification, manifest, traceability | Publisher script writing `generated/...-v2/` | registry sign-off record | Hash-certified outputs, deterministic |
| Human approval | Tracked sign-off record in `registry/` | -- | Authority (Oscar Mack) approval must be a repo artifact |
| Publication integrity | git (commit contents, ancestry) | pytest | `git show --stat`, ancestor test of recorded SHA |
| Line-ending determinism | `.gitattributes` + LF-normalised digest helper | writers using `newline='\n'` | Two layers: git checkout bytes and digest rule |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.10 local; 3.12 CI-pinned | scripts and tests | CI pin per CLAUDE.md [VERIFIED: `python --version`] |
| jsonschema | 4.26.0 | `Draft202012Validator` on the emitted schema | Already used by v1/v2 publishers and builder [VERIFIED: local import] |
| PyYAML | 6.0.3 | read `registry/control_catalog.yaml` | Existing `catalog_controls()` [CITED: CLAUDE.md] |
| pytest | installed (`requirements-dev.txt`) | invariants | 270 existing archive tests pass [VERIFIED: pytest run] |
| hashlib / json / subprocess (stdlib) | -- | digests, deterministic JSON, git calls in tests | Matches repo style |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `.gitattributes` + LF digest | LF digest only | D-02 and D-04 lock both; the attribute fixes working-tree bytes, the digest rule fixes verification on any checkout |
| Extending the v2 script | New sibling script | CONTEXT prefers extending; it already owns `build_authority/validate_authority/schema` |

**Installation:** none. No external packages are added, so the Package Legitimacy Gate does not apply (no `slopcheck` run needed).

## Architecture Patterns

### System Architecture Diagram

```
tracked inputs (LF digests)                 publisher v2 (build_*, pure)
 control_catalog.yaml ----------+
 v1 authority json -------------+--> build_authority() [80 rows, all NOT_YET_DECIDED]
 governance_decisions.json -----+        |
 proposals / drafting record ---+        v
                                  overlay 21 decisions (state, rule, AA4 id)
                                  + applicability_decision_ids + lineage.governance_decisions
                                         |
                                         v
                       validate_authority (generic)  +  validate_publication (21/59 pin,
                       jsonschema(schema())           v1 diff, decisions binding, id list)
                                         |
              --publish --dry-run: print sign-off summary, write nothing tracked
                                         |
                              [BLOCKING: Oscar Mack approves]
                                         |
                       sign-off record (authority LF digest) written to registry/
                                         |
              --publish: write authority, schema(already committed), outputs in ems-aa3-v2/
                 matrix, semantic, negative, traceability(AA4), certification, report, manifest
                                         |
          --validate: rebuild all in memory, require byte equality with disk + manifest digests -> PASS
                                         |
          git add <explicit paths> (-f for generated/) -> publication commit
                                         |
          publication record (SHA, id, version, digests) -> follow-up commit
```

### Recommended file layout
```
.gitattributes                                              # new, narrow (D-02)
scripts/publish_archive_assessment_applicability_authority_v2.py   # extend: lf_digest, overlay, validate_publication, publish
scripts/build_archive_assessment_governance_decisions.py    # review fixes; imports V2.lf_digest
schemas/archive_assessment_applicability_authority_v2.schema.json  # regenerated via --emit-schema
registry/archive_assessment_applicability_authority_v2.json        # publication commit
registry/archive_assessment_applicability_authority_v2_signoff.json # publication commit (name is discretion)
registry/archive_assessment_applicability_authority_v2_publication_record.json # follow-up commit
generated/archive-assessment/ems-aa3-v2/*                  # publication commit, git add -f
tests/test_archive_assessment_applicability_authority_v2_publication.py  # new
```

### Pattern 1: Overlay on the existing builder
Keep `build_authority()` returning the all-undecided base (existing 156-line test file calls it and mutates `controls[0]` = EMS-CTRL-001). Add `build_published_authority()` that loads the decisions file, picks the latest unsuperseded record per control (a record is superseded if another record's `supersedes` names it), and for each of the 21 controls sets `not_applicable_decision_state = decided_outcome`, `not_applicable_rule = decided.rule`, `not_applicable_authority = decision_id`; adds `applicability_decision_ids` (sorted AA4 ids) and `source_lineage.governance_decisions`. [VERIFIED: decisions record fields `decision_id, control_id, decided_outcome, decided.rule, supersedes` read from the file]

### Pattern 2: Validator split (important for keeping existing tests green)
Existing v2 tests (`ok`, `both_reject`, `decide(a['controls'][0], ...)`) mutate EMS-CTRL-001 and expect generic validation to pass or fail. If the D-12 "exactly these 21" pin lives inside `validate_authority`, tests like `test_rule_published_state_passes` break. Put D-09/D-10/D-12/D-13 in a new `validate_publication(a)` that calls `validate_authority` first. The CLI `--validate` and the publication tests call `validate_publication`. The schema may require `applicability_decision_ids` (array of AA4 pattern, unique) with the base builder emitting `[]`; cross-consistency checks (list matches authorities) stay in `validate_publication`. [ASSUMED: this split is the least disruptive design; the planner may choose another as long as the existing 80+ v2 tests stay green]

### Pattern 3: D-13 field-by-field v1 diff
Load v1 rows by `control_id`. For each of 80 rows: `set(v2_row) - set(v1_row) == {'not_applicable_decision_state'}`; every v1 key has equal value except `not_applicable_rule`/`not_applicable_authority` on the 21 decided controls. Compare against the file in the repo, and ideally also against `git show 62a8955:registry/archive_assessment_applicability_authority.json` in a git-gated test (v1 working copy is CRLF here but byte-identical in git; `git diff --stat 62a8955 HEAD -- <v1 file>` is empty, so the file is unchanged since `62a8955`). [VERIFIED: git]

### Pattern 4: Deterministic writes and digests
```python
# Shared helper (put in the v2 publisher; builder imports V2.lf_digest)
def lf_bytes(b: bytes) -> bytes: return b.replace(b'\r\n', b'\n')
def lf_digest(p: Path) -> str: return hashlib.sha256(lf_bytes(p.read_bytes())).hexdigest()
def dump(p: Path, value: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(json.dumps(value, indent=2, sort_keys=True) + '\n')
```
Replace `digest()` in `build_authority` for catalog and v1 lineage sha256 as well: today `digest(CATALOG)` and `digest(V1_AUTHORITY)` are raw-byte hashes, and both files are `w/crlf` on this machine but `i/lf` in the index [VERIFIED: `git ls-files --eol`]. Left alone, a fresh Windows clone, this machine and ubuntu would produce different lineage hashes, which is exactly CR-01. `dump` in the v2 module (shared by the builder via `V2.dump`) fixes WR-08 in one place; also fix the report `.md` write.

### Pattern 5: Publish flow with a human gate
Provide `--publish --dry-run` (builds and validates in memory, prints the D-19 summary and authority LF digest, writes nothing under tracked paths) and `--publish` (requires the sign-off file and checks its authority LF digest equals the rebuilt authority's digest; fails closed otherwise). Keep `published_on` out of the authority document itself and only in cert/manifest/trace outputs, so the authority digest the human approves is identical in the dry run and the final run. The certification cites the sign-off record path and LF sha256; the sign-off record must not contain anything that depends on the certification (avoids a hash cycle). Order: dry-run -> approval -> write sign-off -> publish -> validate.

### Pattern 6: Manifest self-consistency
v1 manifest lists scripts/schemas/registry/generated artifacts plus `self_entry_exclusion_reason`. For v2 list: publisher script, builder is not needed, schema v2, v2 authority, sign-off record, the generated outputs. All hashes are LF digests and the manifest carries a `digest_normalisation: CRLF_TO_LF` field. `--validate` rebuilds the manifest and compares text, and recomputes every listed artifact digest from disk.

### Anti-Patterns to Avoid
- **`git add -A` / `git add .` / `git commit -a`:** the tree has 2 modified and ~60 untracked unrelated files. Never use.
- **Raw `digest()` for anything this phase writes:** CRLF-dependent (CR-01).
- **`datetime.now()` in outputs:** breaks byte-identical regeneration (D-16). v1 `publish()` uses it; do not copy.
- **Putting the 21 pin in the generic validator:** breaks the existing mutation tests.
- **Hand-editing the schema:** it is regenerated from `schema()`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Rule validation | New rule checker | `V2.validate_rule`, `V2.resolve_applicability` | Already tested against the eight-field vocabulary |
| Schema | Hand-written JSON | `schema()` + `--emit-schema` | Hand edits are overwritten and break hash certification |
| Deterministic JSON | Custom serialiser | `json.dumps(indent=2, sort_keys=True)+'\n'` | Repo convention |
| LF digest | A second copy of the rule | One `lf_digest` in the v2 module, imported by the builder | CONTEXT discretion item; `answers_digest` in the builder should delegate to it |
| Ancestor-commit test | New git logic | Copy `git_ready()`/`needs_git` pattern from `tests/test_archive_assessment_rule_proposals_record.py` | Handles missing git / shallow clone by skipping |

## Phase 3 Review Fix Map (D-01)

All fixes are in `scripts/build_archive_assessment_governance_decisions.py` unless noted; each needs a test (WR-09).

| Finding | Fix (from review, verified against current code) |
|---------|---------------------------------------------------|
| CR-01 (lines 204, 223-225) | Use `V2.lf_digest` for proposals, drafting record and the builder's recorded `drafting_record_sha256`; add header field e.g. `frozen_input_sha256_normalisation: 'CRLF_TO_LF'` (adds a key to `HEADER_KEYS` and the schema); view test compares LF bytes |
| CR-02 (226-227, 335-338) | `validate_decisions` compares `answers_sha256` with `answers_digest(ANSWERS)`; `--validate` also requires `decisions_text(doc) == decisions_text(build_from_files())` |
| CR-03 (111, 124, 127-160, 188-200) | Run `strict_checks` on all entries, keep the order/uniqueness check on first 21; make `build_decisions` raise on conflicting fields (APPROVED_AS_DRAFTED with rule/rationale, ruling on a control without scope note) |
| WR-01 | Strip `ems-ctrl-NNN` and digits before note comparison; compare against all drafted strings |
| WR-02 | First 21 entries must have `supersedes is None`; later ones must name an earlier position for the same control |
| WR-03 | Unknown `control_id` in extra entries -> `AuthorityError`; run the answers schema inside `build_from_files`. Note `answers_schema()` currently has `control_id` enum of the 21, so schema also rejects |
| WR-04 | Real date check with `date.fromisoformat` in both validators |
| WR-05 | Load wording approval in `validate_decisions`; require full `wording_approval` equality with what `build_decisions` writes |
| WR-06 | Type guards before `norm()`, hashable guards in `pairs()` |
| WR-07 | `--build` allows append-only (existing records equal prefix of rebuilt records) |
| WR-08 | `newline='\n'` writes (Pattern 4) |
| WR-09 | Fidelity test (zip answers entries and records, compare note, decided_on, supersedes, scope ruling, decided rule/rationale); superseding-entry strict tests; `answers_sha256` mismatch test; `--emit-template` refusal subprocess test |

**D-07 and the decisions file.** Adding the normalisation header key means the decisions file is rewritten. Records must not change: add a test comparing `records` (and every unchanged header field) to `git show eed4a5f:registry/archive_assessment_governance_decisions.json`. Current header values (`proposals_sha256` 31684001..., `drafting_record_sha256` b2d3f0e1..., `answers_sha256` 8efccce9...) already equal LF digests because the proposals and drafting record are `w/lf` here; they should not change. The git blob is already LF (`i/lf`), so "newline bytes" only differ in the CRLF working copy. Rebuild with `--build` is refused by the current code when content differs (WR-07), so the rewrite needs either the append-only rule extended to "header-only differences in the listed fields", or a one-off documented rewrite via `V2.dump`. [ASSUMED: the planner decides which; the test against `eed4a5f` is the safety net]

## Line endings: facts that drive the plan

| File | index | working tree here |
|------|-------|-------------------|
| `registry/control_catalog.yaml` | lf | **crlf** |
| v1 authority json + all `schemas/archive_assessment_*` | lf | **crlf** |
| `registry/archive_assessment_governance_answers.json`, `..._decisions.json` | lf | **crlf** |
| proposals, drafting record, wording approval, view `.md` | lf | lf |
| v1 `generated/archive-assessment/ems-aa3/*` | lf | crlf |

[VERIFIED: `git ls-files --eol`; `core.autocrlf=true`; no `.gitattributes`]

Consequences:
1. Index blobs are LF already, so adding `.gitattributes` (`text eol=lf`) does not change committed content; it makes future checkouts and writes LF. Listed files that are CRLF in the working tree should not show as modified (git normalises on compare). Verify with `git status --short -- <listed paths>` after adding it; if any shows modified, renormalise by explicit path (`git add --renormalize -- <path>`), not repo-wide.
2. A new `.gitattributes` also affects files only if listed; leave v1 files and everything unrelated out (D-02/D-03). Note the attribute for the v2 outputs and `ems-aa3-v2/` must be a directory pattern that does not match `ems-aa3/`.
3. The v1 outputs under `ems-aa3/` have raw-byte hashes calculated on one machine; leave them (D-03).
4. Existing frozen-file tests (view byte-identical test, `answers_digest`) must compare on LF bytes.

## Git staging protocol (PUB-06)

Facts: `git status` shows ` M registry/adjudication_rules.json`, ` M registry/policy_decisions.json` and ~60 untracked files (`.pytest-*`, `docs/*_REQUIREMENTS.md`, `registry/new_repository_onboarding_*` ...). `generated/` is gitignored (`.gitignore:6`), so v2 outputs need `git add -f`. Nothing is currently staged. [VERIFIED: git status, git check-ignore]

Recipe for every commit in this phase:
```bash
git add -f -- <explicit file list>           # -f only needed for generated/
git diff --cached --name-only                # must equal the intended list exactly
git commit -m "..."                          # no -a, no pathless add
git show --stat --format=%H HEAD             # confirm list
```
Safer variant: `git commit --only -- <paths>` would also ignore other staged paths, but the `--cached --name-only` check above is the explicit guard. Include a pytest (git-gated) that, once the publication record exists, asserts `git diff-tree --no-commit-id --name-only -r <sha>` equals the expected set: the v2 authority, `generated/archive-assessment/ems-aa3-v2/*` outputs and the sign-off record, and that `registry/adjudication_rules.json` and `policy_decisions.json` are absent from it. The `.planning/` docs commits (config `commit_docs: true`) are separate commits and must not be in the publication commit.

Pitfall: the commit-message hook or GSD tooling must not run `git add -A`. Pass explicit paths to `gsd-sdk query commit ... --files`.

## Common Pitfalls

### Pitfall 1: Digest of a CRLF working copy differs from the committed LF blob
**What goes wrong:** manifest hashes validate here but fail on a fresh Windows clone or ubuntu.
**How to avoid:** LF digest everywhere; add a test that computes the digest of the CRLF-converted bytes and equals the digest of `git show HEAD:<path>` for each manifest artifact (git-gated).
**Warning signs:** `--validate` passes locally, fails in a clone (CR-01 reproduction).

### Pitfall 2: Circularity between sign-off, certification and authority
**What goes wrong:** the approved digest changes after approval.
**How to avoid:** Pattern 5 ordering; the authority contains no date or sign-off reference; sign-off holds the authority digest; certification cites sign-off.

### Pitfall 3: Existing tests turn red between commits
**What goes wrong:** tests asserting the real v2 file exist before it is published.
**How to avoid:** real-file tests `skipif(not AUTHORITY.exists())` and the publication-record tests `skipif(not RECORD.exists())`. `main --validate` currently raises `AuthorityError('v2 registry authority file is not published')` when the file is missing; keep that CLI behaviour but gate pytest.

### Pitfall 4: Wrong "latest unsuperseded" mapping
**What goes wrong:** the overlay cites a superseded id once Phase 3 later adds superseding records.
**How to avoid:** compute the superseded set as in `validate_decisions`; exactly one unsuperseded record per control. Today there are none, but the test should include a synthetic supersession case.

### Pitfall 5: Shallow clone / CI
`.github/workflows/ems-validate.yml` uses `actions/checkout@v4` with default depth 1 and runs only py_compile/YAML/JSON/secret checks, not pytest [VERIFIED: file]. Git-history tests must skip when `git cat-file -t <sha>` fails or the repo is shallow (copy `git_ready()`). The publisher and `--validate` must not call git. The ancestor test for the publication record needs the publication SHA, which exists only after commit 4; the record is committed in commit 5, so no chicken-and-egg.

### Pitfall 6: Publication record digest vs. publication SHA
Record the authority LF digest and manifest LF digest; the test checks `git show <sha>:<authority path>` normalised equals the recorded digest, and that `<sha>` is an ancestor of HEAD. Do not put the SHA inside any file in the publication commit (impossible).

### Pitfall 7: v1 `source_lineage` carries over fields that must stay equal
`aa1_manifest_sha256`, `aa2_closure_sha256`, `aa2_approval_sha256` are copied from the v1 registry file (already done); keep that and do not read `generated/archive-assessment/ems-aa2/` (gitignored? untracked on a fresh clone). `catalog_reference.sha256` and `supersedes.sha256` must switch to LF digests.

## Code Examples

### Resolve latest unsuperseded decision per control
```python
# Source: derived from validate_decisions() in scripts/build_archive_assessment_governance_decisions.py
def latest_records(doc: dict) -> dict:
    superseded = {r['supersedes'] for r in doc['records'] if r['supersedes']}
    out = {}
    for r in doc['records']:
        if r['decision_id'] not in superseded: out[r['control_id']] = r
    return out
```

### Overlay
```python
for row in authority['controls']:
    rec = latest.get(row['control_id'])
    if rec:
        row['not_applicable_decision_state'] = rec['decided_outcome']
        row['not_applicable_rule'] = rec['decided']['rule']
        row['not_applicable_authority'] = rec['decision_id']
authority['applicability_decision_ids'] = sorted(r['decision_id'] for r in latest.values())
```

### Byte-identical re-run check (D-17)
```python
def validate_published() -> None:
    a = load(AUTHORITY); validate_publication(a)
    jsonschema.Draft202012Validator(load(SCHEMA)).validate(a)
    expected = build_all_outputs()               # dict: relative_path -> text (LF)
    for rel, text in expected.items():
        if lf_bytes((ROOT / rel).read_bytes()) != text.encode('utf-8'): raise AuthorityError(f'{rel} differs from a fresh build')
    man = load(OUT / MANIFEST)
    for art in man['artifacts']:
        if lf_digest(ROOT / art['relative_path']) != art['sha256']: raise AuthorityError(...)
    print('PASS')
```
Compare the committed authority to `build_published_authority()` too (a consistent hand edit plus re-hash fails because the rebuild comes from the decisions file).

## State of the Art

| Old | Current | Impact |
|-----|---------|--------|
| v1 `publish()` with `datetime.now()` and raw `digest()` | Fixed `published_on`, LF digests, `--validate` rebuild-and-compare | Byte-identical regeneration; cross-platform verification |
| v1 manifest of raw bytes (CRLF-dependent) | LF-normalised with a normalisation field | v1 limitation recorded, not fixed (D-03) |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Split into generic `validate_authority` + new `validate_publication` is the best fit for existing tests | Pattern 2 | Planner may instead rework tests; low risk |
| A2 | Decisions file rewrite path (header-only change) can be done by a one-off `V2.dump` or extended `--build` | D-07 section | Needs a planner choice; test against `eed4a5f` guards either way |
| A3 | `git add --renormalize` is only needed if listed files appear modified after adding `.gitattributes` | Line endings | If status shows churn, add an explicit-path renormalise commit |
| A4 | Placement of `published_on` outside the authority document is acceptable | Pattern 5 | If the authority must carry a date, the sign-off digest must be taken after the date is fixed; still fine since the date is a constant |

## Open Questions (RESOLVED)

1. **Exact `published_on` date and the name of new constants.** Discretion; set to the date of the publication run (planner can leave a placeholder constant changed in the publisher commit just before the dry run). Because the constant lives in code that is committed in commit 3 (before the gate), the date must be fixed before commit 3, or commit 3 must be amended before the run. Recommend deciding the date when commit 3 is made and, if the run slips a day, making a tiny code commit before the dry run.
   RESOLVED: plan 04-05 fixes the `PUBLISHED_ON` constant; plan 04-06 Task 1 handles a date slip with a small publisher-only code commit before the dry run.
2. **Is `.gitattributes` cleanly neutral for the CRLF working copies?** Verify empirically at execution (`git status` after adding). Not verifiable without making the change.
   RESOLVED: verified at execution in plan 04-03 Task 1 (`git status` after adding `.gitattributes`; renormalize explicit paths only if churn appears).
3. **Whether `generated/archive-assessment/ems-aa3-v2/` outputs should be listed in `.gitattributes` with a trailing-slash directory pattern:** use `generated/archive-assessment/ems-aa3-v2/** text eol=lf`; check it does not match `ems-aa3/`.
   RESOLVED: plan 04-01 rewrites the decisions-file header via `--build` (`HEADER_REFRESH_KEYS`); plan 04-03 adds the `ems-aa3-v2/**` pattern and checks it with `git check-attr`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | all | yes | 3.12.10 | -- |
| jsonschema | schema validation | yes | 4.26.0 | -- |
| PyYAML, pytest | catalog, tests | yes | installed (270 tests ran) | -- |
| git | commits, git-gated tests | yes | repo, not shallow, `62a8955` and `eed4a5f` present (`git cat-file -t 62a8955` -> commit) | tests skip when absent |

No missing dependencies.

## Validation Architecture

`workflow.nyquist_validation` is `false` in `.planning/config.json`, so the formal section is omitted. Practical test plan:

- Existing: `python -m pytest tests -k archive_assessment -q` (270 pass, about 23 s) is the quick command; full `python -m pytest` is the phase gate.
- New tests (names illustrative) in a new file, gated with `skipif` on the v2 file/record existing: decided count == 21, undecided == 59, decided set equals the 21 request ids, only the three expected rules (030/039 `production KNOWN_FALSE`, 052 `ai_enabled KNOWN_FALSE`), rule fields within the four usable fields and states within `KNOWN_TRUE/KNOWN_FALSE`, every decided control has an AA4 authority present in `applicability_decision_ids` and in the decisions file, every list id cited by exactly one control, `decision_ids` equals the eight AA1 ids on all 80, 59 rows equal v1 apart from the added state, lineage names `62a8955` and `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-1.0.0`, regeneration is byte-identical, manifest digests match LF bytes, a consistent hand edit plus re-hash fails `--validate`, `resolve_applicability` for 030/039/052 with KNOWN_TRUE/KNOWN_FALSE/UNKNOWN facts, unrelated files not in the publication commit (git-gated), publication record SHA is an ancestor and contains the authority with that digest (git-gated).
- Mutation tests use the existing `invalid(mutator)` style against `validate_publication`.
- Wave 0: the review-fix tests (WR-09) are written before or with each fix.

## Security Domain

`security_enforcement` is enabled. This is an offline file-publication phase with no network, auth or user input beyond JSON files.

| ASVS Category | Applies | Control |
|---------------|---------|---------|
| V2/V3 Auth/Session | no | -- |
| V4 Access Control | partial | Human sign-off record by the named authority; publish refuses without it |
| V5 Input Validation | yes | jsonschema + fail-closed `AuthorityError`; type guards (WR-06) |
| V6 Cryptography | yes | SHA-256 via `hashlib` (never hand-rolled) |
| V12 Files | yes | No absolute paths in registry JSON (`contains_absolute`); repo-relative forward-slash paths |

| Threat | STRIDE | Mitigation |
|--------|--------|-----------|
| Hand-edited authority with re-hashed manifest | Tampering | `--validate` rebuilds from tracked inputs and compares (D-17), decisions binding (D-10) |
| UNKNOWN resolving to not-applicable | Elevation / Spoofing | Vocabulary pin, `resolve_applicability` tests |
| Unrelated work leaking into the commit | Information disclosure / Tampering | Explicit-path staging and `--cached --name-only` check, stat test |
| Checkout-dependent digests | Repudiation | LF digests + `.gitattributes` |

## Sources

### Primary (HIGH confidence, read in this session)
- `scripts/publish_archive_assessment_applicability_authority_v2.py`, `scripts/publish_archive_assessment_applicability_authority.py`, `scripts/build_archive_assessment_governance_decisions.py`
- `registry/archive_assessment_governance_decisions.json` (21 records inspected), `registry/archive_assessment_governance_wording_approval.json`
- `tests/test_archive_assessment_applicability_authority_v2.py`, `tests/test_archive_assessment_rule_proposals_record.py`
- `.planning/phases/04-certified-publication/04-CONTEXT.md`, `.planning/phases/03-governance-decisions/03-REVIEW.md`, `.planning/REQUIREMENTS.md`, `.planning/config.json`, `CLAUDE.md`
- Local git state: `git ls-files --eol`, `git status`, `git check-ignore`, `git cat-file`, `.github/workflows/ems-validate.yml`

### Secondary / Tertiary
- None. No external documentation was needed.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, nothing new
- Architecture and validator split: HIGH on facts, MEDIUM on the recommended design (A1, A2)
- Pitfalls: HIGH, each traced to code or git state

**Research date:** 2026-10-14
**Valid until:** 2026-11-13 (stable internal code; re-verify if the working tree or `.gitattributes` situation changes)
