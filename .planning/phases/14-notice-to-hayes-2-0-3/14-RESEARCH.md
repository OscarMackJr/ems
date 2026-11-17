# Phase 14: Notice to Hayes (2.0.3) - Research

**Researched:** 2026-11-17
**Domain:** Generated, self-validating governance notice (Python 3.12 + jsonschema + git plumbing) that re-executes pinned code from git history
**Confidence:** HIGH (the key mechanisms were run against the real repository in this session)

## Summary

Phase 14 adds one standalone builder, `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`. It is modelled on the original 2.0.2 builder at `47343a1`, which had `--build`, `--emit-schema` and `--validate`, combined with the frozen-helper style of the current 2.0.2 builder. It generates three files (notice JSON, Markdown, closed schema). It has three new claim enforcers: CLAIM-01 (it reruns the pinned negative mutations), CLAIM-02 (it recomputes all 7 lineage digests from git) and CLAIM-03 (it computes raw and LF hashes for the 3 RAW_BYTES files). It also adds the verify-at-pin guidance from PIN-03. Every fact the notice needs was checked against the repository during this research: the pin, the record, the lineage digests, the raw/LF pairs, the 29 mutations, the 16 closed schema levels and the deferred text.

The hard problem is D-01: run `run_mutations` from the **pinned** publisher without executing or reading any live file. **This was solved and verified in this session.** Write the needed pinned blobs (publisher, governance-decisions builder, 7 data/schema files) into a fresh `tempfile.TemporaryDirectory()` that mirrors the repo layout. Load the publisher with `importlib.util.spec_from_file_location` from that temp path, so all its path constants (and those of the builder it loads lazily, and of the builder's own nested publisher copy) resolve inside the temp dir. Then rebind exactly one attribute, `pub.ROOT = <real repo root>`, so the pinned `git_show`/`git_run` (`cwd=ROOT`) still reach the real object database for the `62a8955` catalog and `ae15c74` superseded-authority reads. With that setup the rerun produced 29 outcomes that are **byte-for-byte equal** to the frozen negative-invariant file at the pin. A Python audit hook showed that every `open()` during the run was inside the temp dir. The unmutated baseline is accepted by every gate, `pub.schema()` equals the pinned schema file, and the pinned publisher blob's LF sha256 equals the manifest's `publisher_script.sha256` (`cf694a06…`). Without the `ROOT` rebind the run fails closed with `GitHistoryError: not a git repository`.

One correction to a locked decision must reach the planner and user. **`requirements.txt` at the pin contains only `PyYAML==6.0.3` and `Jinja2==3.1.6`. It does not list `jsonschema`, and the pinned publisher imports `jsonschema`.** D-09's prerequisite "`pip install -r requirements.txt`" is therefore insufficient. A Hayes operator who follows it literally gets `ModuleNotFoundError` at step 1. CI installs `-r requirements.txt jsonschema pytest`. The notice command must be `python -m pip install -r requirements.txt jsonschema` (verified environment: jsonschema 4.26.0). `requirements-dev.txt` is untracked, so it cannot be cited either.

**Primary recommendation:** Build `pinned_mutation_run()` exactly as described: temp-dir materialisation, `spec_from_file_location`, a single `pub.ROOT` rebind, a baseline-accepts check, then `run_mutations`. Wrap all pinned-module exceptions into the builder's own `AuthorityError`/`GitHistoryError`. Compare `(id, rejected_by, result)` entry for entry with the manifest-bound frozen file. Pass the rerun result into a pure `build_notice(...)` so tests can exercise each claim guard directly without a 7-second rerun per test.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Running the mutations (CLAIM-01)
- **D-01:** The builder runs the mutations from the **pinned publisher blob**: it reads `scripts/publish_archive_assessment_applicability_authority_v2.py` with `git_show` at `1544dc1…`, loads it as a module, and runs its `run_mutations` (with `NEGATIVE_MUTATIONS` and `mutation_gates`) on the frozen inputs at the pin (authority, sign-off, governance decisions). The pinned publisher's `decisions_builder()` loads `scripts/build_archive_assessment_governance_decisions.py` from its live path; that builder (and its schema) must also come from the pin, not the working tree. The researcher must work out how to load both pinned modules so that no live file is executed and the pinned module's path constants do not redirect reads to live files. A later publisher edit must not change the result.
- **D-02:** **Rerun equals recorded.** The builder fails with a domain error unless: every mutation is rejected (non-empty `rejected_by`, result `REJECTED_FAIL_CLOSED`), the frozen negative-invariant output at the pin has `result == 'PASS'`, and the rerun's per-mutation list (`id`, `rejected_by`, `result`) equals the frozen file entry for entry, in order. This catches both a mutation that is not rejected and a recorded file that overstates.
- **D-03:** The notice JSON lists each mutation (`id`, `rejected_by`). The Markdown gives the count, says each mutation was run by the builder and rejected, and points to the JSON for the list.

#### What the notice says
- **D-04:** **Re-pin framing.** "Re-pin to `1544dc1…`. It replaces `ae15c74…` (2.0.2) and `31addfa…` (2.0.1); if Hayes pins either, move straight to `1544dc1…`." Full SHAs throughout. This works whether or not Hayes acted on the 2.0.2 notice. The other two Hayes-side steps from the reply and 2.0.2 notice are restated (eight classification facts on the target description; read the published v2 shape).
- **D-05:** **The 2.0.1 digest-scope error is repeated and computed** (CLAIM-03), because Hayes may jump from `31addfa` directly. For each of the three RAW_BYTES files (`aa1_manifest`, `aa2_approval`, `aa2_closure`) the builder computes the raw sha256 and the LF sha256 of the bytes at the pin, requires them to differ, and shows both in the notice. 2.0.1's global `CRLF_TO_LF` claim is read from the 2.0.1 authority at `31addfa`. `--validate` fails if any pair is equal or does not match git.
- **D-06:** **What changed in 2.0.3** is derived data plus one fixed line:
  - derived: `source_lineage.supersedes` moved from 2.0.1 at `31addfa` to 2.0.2 at `ae15c74`; 0 of 80 rows differ from 2.0.2 on the compared keys; the decisions digest `4e746d1f…` is unchanged; the mutation count (from the D-01 rerun) and the closed schema levels (from the frozen schema at the pin);
  - one fixed, plain line naming the verification changes: `--validate --at-pin`, plain-mode byte identity, GATE-06..GATE-10, frozen validators. No ranking or emphasis words.
- **D-07:** **All 7 lineage digests are recomputed** (CLAIM-02). Each entry lists key, path, normalisation, sha256 and the commit it was recomputed at: the pin for `aa1_manifest`, `aa2_approval`, `aa2_closure` and `governance_decisions`; the commit named in the lineage entry for `catalog_reference` (`62a8955…`), `v1_baseline` (`62a8955…`) and `supersedes` (`ae15c74…`). The hash uses the declared normaliser. The validator fails on any mismatch.
- **D-08:** Decision content as in 10 D-08: counts (21 decided: 3 rules, 18 no-rule; 59 `NOT_YET_DECIDED`), the 3 rules in machine form, the governance decisions LF sha256 unchanged, and a pointer to the reply and decisions file for the 18 no-rule reasons.

#### Verify-at-pin guidance (PIN-03)
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

#### Builder form and gates
- **D-12:** **New standalone builder** `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, in the 2.0.2 builder's compact style, with its own frozen constants (`NOTICE_PUBLICATION_COMMIT = 1544dc19ba235d732c832d1651895550ed5a265d`, `NOTICE_RECORD_COMMIT = 87a46d147413bd99e931c71a1ab165eb0903f014`, the 2.0.2 and 2.0.1 commits, ids and versions, request ids, `DUAL_ROLE_STATEMENT`, `NOTICE_DATE`). It copies helpers rather than importing the 2.0.2 builder or the live publisher. Files: `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md`, `registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json`, `schemas/archive_assessment_demo3_w1_req_001_notice_2_0_3.schema.json` (closed, `additionalProperties: false`). Inputs read via `git_show` at the frozen commits with record binding, existence and ancestry checks, and fail-closed shallow check (10 D-04, 12-03 uniform git-error handling).
- **D-13:** **Schema is validated from the live committed file**, byte-compared with the builder's schema function. No frozen-schema commit constant in this phase.
- **D-14:** **Gates as in Phase 10:** a blocking review of the rendered Markdown by Oscar Mack before the notice commit (any change by regenerating, never by hand edit); then a blocking push checkpoint. On go-ahead, push the branch (the notice commits plus the local `.planning` commits after `5498002`) with the STATE.md token workaround, dispatch `ems-validate.yml`, and confirm it is green at the pushed head. The notice states it must not be sent until its own commit is on the remote branch. No PR, merge or tag.
- **D-15:** **CI and tests:** add the 2.0.3 notice `--validate` to the `archive-assessment` job (separate code commit). New `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` validates the committed files, covers tamper of each cited id/version/commit, and has one test per claim that fails for its named reason with a specific `match=` (mutation not rejected; rerun differs from recorded; frozen negative result not PASS; wrong lineage digest for each of the 7; raw equals LF for a RAW_BYTES file; live publisher edit does not change the build or `--validate`). Keep at least one non-skipping fail-closed history test.

#### Carried forward (not re-asked)
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

### Deferred Ideas (OUT OF SCOPE)
- Freezing the 2.0.3 notice schema at a commit constant (D-13): later, if needed.
- Opening a PR, merging to main, tagging: left to the EMS authority.
- WR-02 ambient `GIT_*` scrubbing (12-SECURITY AR-03), 11-REVIEW and 12-REVIEW IN items, `.gitattributes eol=lf` (12 D-15): still deferred.
- V2-01 (other 59 controls) and V2-02 (Hayes re-run): still deferred.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| NOTICE-03 | Generated, `--validate`-checked notice citing 2.0.3 id/version/commit, what changed, no decision changed, PIN-03 guidance, re-pin request | Builder pattern (2.0.2 builder at `47343a1` for `--build`/`--emit-schema`/`schema()`; current 2.0.2 for frozen helpers); all cited facts verified (Pinned Facts table); D-13 schema byte-compare |
| PIN-03 | Exact commands to verify at pin and at record commit, and what each result means | Verified command behaviour of the pinned publisher (`validate_published`, `check_publication_record`, `AT_PIN_DEFERRED` L828); **jsonschema prerequisite gap** (Pitfall 1); self-reference of notice commit (Pitfall 6) |
| CLAIM-01 | Builder runs every negative mutation, records a domain rejection, validator fails if any not rejected | Pattern 1 (pinned mutation run), verified 29/29 equal to frozen; baseline-accept non-vacuity (Pitfall 3); exception-class wrapping (Pitfall 4) |
| CLAIM-02 | Validator recomputes all 7 lineage digests from git | Pattern 2; all 7 recomputed in session and matched |
| CLAIM-03 | Every "declared under wrong scope" statement computed: raw hash differs from LF hash | Pattern 3; all 3 RAW_BYTES files contain CRLF; raw==2.0.1-recorded, raw≠LF (verified) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- Python 3.12, `jsonschema`, PyYAML, pytest; match the existing code (compact `publish_*`/notice-builder style: single quotes, one-line helpers, `from __future__ import annotations`).
- New script naming: `snake_case.py`, verb-first (`build_…`). Do not add `Verb-PascalCase.py`.
- Deterministic JSON: `json.dumps(value, indent=2, sort_keys=True) + '\n'`; write with `newline='\n'`.
- SHA-256 via `hashlib`; registry JSON must not contain absolute paths (`contains_absolute`); repo-relative forward-slash paths.
- Fail closed: domain exception (`AuthorityError`) on any violated invariant; `UNKNOWN` never resolves to not-applicable.
- `build_*` (pure) / `validate_*` (raises) pairs, then `main()` with `argparse`.
- Hash-based certification breaks on uncoordinated hand edits, so regenerate and never hand-edit generated files.
- Working tree: unrelated uncommitted work stays untouched; stage by explicit path only.
- Authority: Oscar Mack approves; the dual-role statement must be explicit in the record.
- Boundary: nothing from Hayes is adopted into EMS.
- GSD workflow: edits go through `/gsd-execute-phase`.
- Rationale lives in docs/registry, not code comments (comments sparse).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Read frozen inputs at pin/record/2.0.2/2.0.1 | Git object DB (via `git show`) | — | Content-addressed history is the source of truth; working tree is never read for inputs |
| Rerun negative mutations (CLAIM-01) | Pinned publisher + pinned decisions builder, executed from a temp materialisation | Builder (orchestration, comparison) | D-01: the code that certified 2.0.3 is the code that reruns; the builder only compares |
| Lineage recomputation (CLAIM-02) and raw/LF scope proof (CLAIM-03) | Notice builder (own copied helpers) | Git object DB | Pure hashing over blobs; no pinned code needed |
| Notice content derivation (`build_notice`) | Notice builder (pure function) | — | Testable without git once inputs are loaded |
| Notice schema | Notice builder `schema()` → committed `schemas/…2_0_3.schema.json` | — | D-13: live committed file byte-compared to function |
| Verify-at-pin instructions | Notice text (generated) | Pinned publisher (`AT_PIN_DEFERRED` quoted) | Notice and tool cannot disagree |
| CI gate | `.github/workflows/ems-validate.yml` `archive-assessment` job | pytest glob | Separate commit (D-15) |

## Pinned Facts (all verified this session against git)

| Fact | Value | Source |
|------|-------|--------|
| PUB (pin) | `1544dc19ba235d732c832d1651895550ed5a265d` | `git rev-parse 87a46d1^` = PUB [VERIFIED: git] |
| REC | `87a46d147413bd99e931c71a1ab165eb0903f014`; only non-planning change PUB→REC is the publication record | `git diff --name-only PUB REC` [VERIFIED: git] |
| Record at REC | authority 2.0.3, `authority_sha256 696116e7…a0e0a6`, `manifest_sha256 3084dd94…3830e`, CRLF_TO_LF, publication_commit PUB | [VERIFIED: git] |
| Sign-off at PUB | Oscar Mack, EMS_GOVERNANCE_AUTHORITY, date 2026-11-17; manifest `published_on` 2026-11-17 | [VERIFIED: git] |
| 2.0.2 | `ae15c7458e49c8f55cc58c61bab04bc716aa9892`, authority LF sha `a44eea1f…`; its `supersedes.commit` = `31addfa…` | [VERIFIED: git] |
| 2.0.1 | `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb`; `source_lineage.digest_normalisation = CRLF_TO_LF`; keys `aa1_manifest_sha256`, `aa2_closure_sha256`, `aa2_approval_sha256` | [VERIFIED: git] |
| Lineage keys at PUB | `aa1_manifest, aa2_approval, aa2_closure, catalog_reference, governance_decisions, supersedes, v1_baseline` (7) | [VERIFIED: git] |
| Commit-bearing lineage | `catalog_reference` & `v1_baseline` → `62a8955dc28d9458cd1167fad314926e057c31fc`; `supersedes` → `ae15c74…`; the other 4 have no `commit` key (→ PUB) | [VERIFIED: git] |
| All 7 recomputed digests | match the recorded sha256 under declared normaliser | probe script [VERIFIED: git] |
| RAW_BYTES raw vs LF | aa1 raw `f0da8e2e…` / LF `06e39f7b…`; aa2_approval raw `de170ebc…` / LF `248b6e38…`; aa2_closure raw `ed589d76…` / LF `66662df3…` (all contain CRLF) | [VERIFIED: git] |
| 2.0.1 recorded values | equal the raw digests above (so 2.0.1's CRLF_TO_LF scope claim was wrong for each) | [VERIFIED: git] |
| AA1 manifest at 31addfa | **not present** (committed later in 07-01 `bb7c067`) → raw/LF must be computed at PUB, not 31addfa | [VERIFIED: git] |
| Negative mutations | 29; frozen file `result: PASS`; rerun equal in full | probe [VERIFIED: git + run] |
| Closed schema levels (authority schema at PUB) | 16; `pub.schema()` == committed schema at PUB | [VERIFIED: run] |
| Pinned publisher LF sha256 | `cf694a06…c908` == manifest `publisher_script.sha256` | [VERIFIED: git] |
| Decisions digest | `4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f` (raw == LF) | [VERIFIED: git] |
| `AT_PIN_DEFERRED` (PUB L828) | `PUBLICATION_RECORD_BINDING: the publication record naming this commit is written in the next commit; run plain --validate at the record commit or any later commit to check it` | [VERIFIED: git] |
| At-pin PASS output | `json.dumps({'status': 'PASS', 'mode': 'AT_PIN', 'deferred': [AT_PIN_DEFERRED]})` (L825) | [VERIFIED: git] |
| Plain `--validate` at PUB | raises `publication record still names the superseded 2.0.2 publication, so HEAD is the publication commit, not the record commit; run --validate --at-pin here, or plain --validate at the record commit or later` (L841) | [VERIFIED: git] |
| Shallow at-pin | `GitHistoryError: the clone is shallow; fetch full history (git fetch --unshallow)` (L400) | [VERIFIED: git] |
| Remote URL | `https://github.com/OscarMackJr/ems.git` (matches `git remote -v`; builder must hard-code) | [VERIFIED: git] |
| Remote branch tip | `5498002c…` = WR-03 commit | `git ls-remote` [VERIFIED] |
| requirements.txt at PUB | `PyYAML==6.0.3`, `Jinja2==3.1.6` only; **no jsonschema** | [VERIFIED: git] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12 (local 3.12.10; CI `3.12`) | runtime | CI-pinned [VERIFIED: local + workflow] |
| jsonschema | 4.26.0 locally (unpinned in CI) | Draft 2020-12 validation of notice + pinned publisher's gates | Already used by every authority script [VERIFIED: local] |
| PyYAML | 6.0.3 | Imported by the pinned publisher (`catalog_controls`) | requirements.txt [VERIFIED] |
| stdlib: `importlib.util`, `tempfile`, `hashlib`, `subprocess`, `json`, `argparse` | — | pinned-module loading, temp materialisation, hashing, git | No new dependency |

### Supporting
| Tool | Version | Purpose |
|------|---------|---------|
| git | 2.54.0.windows.1 | `git show <sha>:<path>`, `rev-parse --is-shallow-repository`, `cat-file -e`, `merge-base --is-ancestor` |
| pytest | 9.1.1 | tests (orchestrator runs them) |
| gh | 2.91.0 | workflow dispatch / run view at push gate |

**Installation:** none. No new package is installed in this phase.

## Package Legitimacy Audit

No external packages are installed or added in this phase, so the slopcheck gate does not apply. `jsonschema` and `PyYAML` are already in use. The only "dependency" change is wording in the notice: it tells Hayes to `pip install … jsonschema`, which matches the existing CI step.

| Package | Registry | Disposition |
|---------|----------|-------------|
| (none new) | — | — |

## Architecture Patterns

### System Architecture Diagram

```
                 frozen constants (PUB, REC, 2.0.2, 2.0.1, URL, NOTICE_DATE, ...)
                                   |
                                   v
   resolve_record_commit(): shallow? --yes--> GitHistoryError (fail closed)
        | commits exist? ancestors of HEAD? PUB ancestor of REC?
        v
   load_inputs(): git show @PUB  (authority, signoff, decisions, manifest, schema, negative, trace)
                  git show @REC  (publication record)  -> record binding (names PUB, digests)
                  git show @ae15c74 (2.0.2 authority) / @31addfa (2.0.1 authority)
                  check_inputs_bound(manifest)  (negative/trace/schema/signoff/authority digests)
        |
        +--> pinned_mutation_run(authority, signoff, decisions)        [CLAIM-01]
        |       tempdir <- git show @PUB of 9 files (2 scripts + 7 data/schema)
        |       pub = spec_from_file_location(tempdir/scripts/publish_..._v2.py)
        |       check: LF sha(pub blob) == manifest.publisher_script.sha256; pub.VERSION == '2.0.3'
        |       pub.ROOT = REAL_ROOT   (git cwd only; path constants stay in tempdir)
        |       baseline: unmutated authority/signoff/decisions accepted by every gate
        |       outcomes = pub.run_mutations(...)      (pinned exceptions -> builder AuthorityError)
        |       returns {outcomes, at_pin_deferred=pub.AT_PIN_DEFERRED}
        |
        v
   build_notice(inputs..., rerun)  (pure)
        |-- rerun vs frozen negative: all rejected, frozen PASS, (id,rejected_by,result) equal in order
        |-- lineage_entries(): 7 x sha256(normaliser(git show @commit-or-PUB))   [CLAIM-02]
        |-- digest_scope_error(): 3 x raw != LF, raw == recorded, 2.0.1 CRLF_TO_LF  [CLAIM-03]
        |-- rows 0/80 vs 2.0.2; decisions digest equal everywhere; counts 21/3/18/59
        |-- verify section: URL, prerequisites, 3 steps, outcome table, quoted AT_PIN_DEFERRED
        v
   notice dict --> render_markdown()  /  jtext()  /  schema()
        |
   --build: write JSON+MD (after building all payloads) then validate_notice()
   --emit-schema: write schema
   --validate: fresh rebuild == committed JSON/MD (LF-normalised); committed schema == schema();
               jsonschema(committed schema).validate(committed JSON); forbidden words; no abs paths; PASS
```

### Recommended file set
```
scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py   # builder (--build, --emit-schema, --validate)
schemas/archive_assessment_demo3_w1_req_001_notice_2_0_3.schema.json # generated by --emit-schema
registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json       # generated by --build
docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md                                # generated by --build
tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py       # picked up by CI glob
.github/workflows/ems-validate.yml                                   # +1 validator line (separate commit)
```

### Pattern 1: Run the pinned mutations with no live file executed (D-01, CLAIM-01). Verified.

**What:** Materialise the pinned blobs in a temp dir, load from there, and rebind `ROOT` so git still works.

**Files to materialise at PUB.** These are exactly the files opened during a full baseline-plus-29-mutation run, confirmed with `sys.addaudithook('open')`:
```
scripts/publish_archive_assessment_applicability_authority_v2.py
scripts/build_archive_assessment_governance_decisions.py
registry/archive_assessment_governance_decisions.json
registry/archive_assessment_applicability_authority.json            # V1_AUTHORITY (v1_baseline_entry, validate_publication)
registry/archive_assessment_not_applicable_rule_proposals.json      # builder PROPOSALS
registry/archive_assessment_rule_proposals_drafting_record.json     # builder DRAFTING_RECORD
registry/archive_assessment_governance_answers.json                 # builder ANSWERS (.exists() + lf_digest)
registry/archive_assessment_governance_wording_approval.json        # builder WORDING_APPROVAL
schemas/archive_assessment_governance_decisions.schema.json         # mutation_gates load(b.DECISIONS_SCHEMA)
```

**Why it works:**
- The pinned publisher's `ROOT = Path(__file__).resolve().parents[1]` resolves to the temp dir, so `GOVERNANCE_DECISIONS`, `V1_AUTHORITY`, `BUILDER_SCRIPT` and the rest are computed at exec time inside the temp dir.
- `decisions_builder()` then loads `tempdir/scripts/build_…py`. That builder's module-level `spec_from_file_location(ROOT/'scripts'/'publish_…v2.py')` loads a **second pinned publisher copy**, also from the temp dir.
- Path constants are evaluated once at exec time. Rebinding `pub.ROOT` afterwards therefore changes only call-time uses: `git_show`/`git_run` `cwd=ROOT`, and `rel()`/`check_tree_matches_head`, which are not on the mutation path.
- The builder's nested `V2` does no git calls on this path, so it is left untouched.

```python
# Verified in session (scratchpad probe): 29 outcomes == frozen file, full dict equality.
PINNED_CODE = ('scripts/publish_archive_assessment_applicability_authority_v2.py', 'scripts/build_archive_assessment_governance_decisions.py')
PINNED_DATA = ('registry/archive_assessment_governance_decisions.json', 'registry/archive_assessment_applicability_authority.json',
               'registry/archive_assessment_not_applicable_rule_proposals.json', 'registry/archive_assessment_rule_proposals_drafting_record.json',
               'registry/archive_assessment_governance_answers.json', 'registry/archive_assessment_governance_wording_approval.json',
               'schemas/archive_assessment_governance_decisions.schema.json')

def load_pinned_publisher(tmp: Path):
    for p in (*PINNED_CODE, *PINNED_DATA):
        dest = tmp / p; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(git_show(NOTICE_PUBLICATION_COMMIT, p))
    spec = importlib.util.spec_from_file_location('aa_pinned_publisher_2_0_3', tmp / PINNED_CODE[0])
    pub = importlib.util.module_from_spec(spec); spec.loader.exec_module(pub)
    pub.ROOT = ROOT   # git cwd only; every path constant already points into tmp
    return pub

def pinned_mutation_run(authority: dict, signoff: dict, decisions: dict, manifest: dict) -> dict:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        try:
            pub = load_pinned_publisher(tmp)
            if hashlib.sha256(lf_bytes((tmp / PINNED_CODE[0]).read_bytes())).hexdigest() != manifest['publisher_script']['sha256']: raise AuthorityError('pinned publisher differs from the certified publisher_script digest')
            if pub.VERSION != NOTICE_VERSION: raise AuthorityError('pinned publisher is not the 2.0.3 publisher')
            # non-vacuity: the unmutated inputs must pass every gate the mutations are judged by
            pub.validate_governance_decisions(); pub.validate_publication(authority)
            jsonschema.Draft202012Validator(pub.schema()).validate(authority)
            pub.validate_signoff(signoff, pub.sha_text(pub.jtext(authority)))
            outcomes = pub.run_mutations(authority, signoff, decisions)
            b = pub._BUILDER
            for path in (pub.GOVERNANCE_DECISIONS, pub.V1_AUTHORITY, pub.BUILDER_SCRIPT, Path(b.__file__), Path(b.V2.__file__), b.PROPOSALS, b.DRAFTING_RECORD, b.ANSWERS, b.WORDING_APPROVAL, b.DECISIONS_SCHEMA):
                if not Path(path).resolve().is_relative_to(tmp.resolve()): raise AuthorityError(f'pinned code resolved {path.name} outside the pinned materialisation')
            return {'outcomes': outcomes, 'at_pin_deferred': pub.AT_PIN_DEFERRED}
        except AuthorityError: raise
        except Exception as e:  # pinned classes are not the builder's classes (see Pitfall 4)
            cls = GitHistoryError if type(e).__name__ == 'GitHistoryError' else AuthorityError
            raise cls(f'pinned mutation run failed: {type(e).__name__}: {e}') from e
```
(Shape only. Tighten the broad `except` to `(ValueError, OSError, KeyError, TypeError, AttributeError, jsonschema.ValidationError, jsonschema.SchemaError)` if the planner prefers. Pinned `AuthorityError`/`GitHistoryError` subclass `ValueError`.)

**D-02 comparison (separate pure function, called from `build_notice`):**
```python
def check_rerun(rerun: list, negative: dict) -> list:
    for o in rerun:
        if not o.get('rejected_by') or o.get('result') != 'REJECTED_FAIL_CLOSED': raise AuthorityError(f"mutation {o.get('id')} was not rejected by the rerun")
    if negative.get('result') != 'PASS': raise AuthorityError('the frozen negative-invariant result at the pin is not PASS')
    proj = lambda xs: [(x['id'], x['rejected_by'], x['result']) for x in xs]
    if proj(rerun) != proj(negative['negative_invariant_tests']): raise AuthorityError('the mutation rerun differs from the frozen negative-invariant output')
    return [{'id': o['id'], 'rejected_by': list(o['rejected_by'])} for o in rerun]
```

### Pattern 2: Recompute all 7 lineage digests (CLAIM-02)
```python
LINEAGE_NORMALISATION = {'aa1_manifest': 'RAW_BYTES', 'aa2_approval': 'RAW_BYTES', 'aa2_closure': 'RAW_BYTES', 'catalog_reference': 'CRLF_TO_LF', 'governance_decisions': 'CRLF_TO_LF', 'supersedes': 'CRLF_TO_LF', 'v1_baseline': 'CRLF_TO_LF'}
NORMALISERS = {'RAW_BYTES': lambda b: b, 'CRLF_TO_LF': lf_bytes}
def lineage_entries(authority: dict) -> list:
    lin = authority['source_lineage']
    if sorted(lin) != sorted(LINEAGE_NORMALISATION): raise AuthorityError('source_lineage keys differ from the 7 declared inputs')
    out = []
    for key in sorted(lin):
        e = lin[key]; norm = e.get('normalisation')
        if norm != LINEAGE_NORMALISATION[key]: raise AuthorityError(f'source_lineage {key}: normalisation {norm!r} differs from {LINEAGE_NORMALISATION[key]}')
        at = e.get('commit', NOTICE_PUBLICATION_COMMIT)
        got = hashlib.sha256(NORMALISERS[norm](git_show(at, e['relative_path']))).hexdigest()
        if got != e['sha256']: raise AuthorityError(f'source_lineage {key}: recomputed sha256 at {at} differs from the recorded digest')
        out.append({'key': key, 'relative_path': e['relative_path'], 'normalisation': norm, 'sha256': got, 'recomputed_at': at})
    return out
```
The 8th digest inside `supersedes` (`governance_decisions_sha256`, path `governance_decisions_relative_path`, at `ae15c74`, CRLF_TO_LF) should also be recomputed. It is the "decisions digest unchanged" evidence; report it under `decisions`/`what_changed`, not as an 8th lineage row (D-07 says 7).

### Pattern 3: Computed digest-scope error (CLAIM-03)
For each of the three pairs (`aa1_manifest_sha256`→`aa1_manifest`, `aa2_approval_sha256`→`aa2_approval`, `aa2_closure_sha256`→`aa2_closure`):
1. `raw = sha256(git_show(PUB, path))`, `lf = sha256(lf_bytes(raw_bytes))`.
2. **First** require `raw != lf` (message names the key, e.g. `aa1_manifest: raw sha256 equals its LF sha256, so the wrong-scope statement cannot be made`). Put this check first so the named test fires for its own reason.
3. Then require `raw == 2.0.3 lineage sha256` and `raw == 2.0.1 <key>_sha256`; require the 2.0.1 `source_lineage.digest_normalisation == 'CRLF_TO_LF'` (read at `31addfa`); require 2.0.3 declares `RAW_BYTES`.
4. Emit `{key, previous_key, relative_path, raw_sha256, lf_sha256, previous_declared_scope: 'CRLF_TO_LF', declared_scope: 'RAW_BYTES'}`.

### Pattern 4: Builder modes (from original 2.0.2 builder `47343a1`, plus IN-02 fix)
- `--emit-schema`: `dump(NOTICE_SCHEMA, schema())`.
- `--build`: `inputs = load_inputs(); notice = build_notice(*inputs); validate_notice_object(notice, inputs)`. Then render **both** payloads, write JSON and MD (`newline='\n'`), then call `validate_notice()` (10-REVIEW IN-02).
- `--validate`: existence check → fresh build → `lf_bytes(committed JSON) == jtext(notice)` → `lf_bytes(committed MD) == render_markdown(notice)` → `lf_bytes(committed schema) == jtext(schema())` (D-13) → `validate_notice_object(load(NOTICE_JSON), inputs)` → `Draft202012Validator(load(NOTICE_SCHEMA)).validate(...)` → print `PASS`.
- `validate_notice` must run the mutation rerun **once** and reuse it (≈7 s per rerun on this machine). Make the rerun part of `load_inputs()`'s returned tuple so `validate_notice_object(notice, inputs)` does not rerun.

### Pattern 5: Verify section in the notice JSON (PIN-03)
Suggested closed shape:
`verify: {repository_url, prerequisites: [..], steps: [{step, checkout, commands: [..], pass_means}], outcomes: [{case, meaning, action}], at_pin_deferred}`. Note:
- `at_pin_deferred` comes from `pub.AT_PIN_DEFERRED` (returned by the pinned run). Use a schema `pattern: '^PUBLICATION_RECORD_BINDING: '`.
- Optionally assert that the pinned publisher source contains the substring `run --validate --at-pin here`, so the "plain at pin fails by design and points to --at-pin" row is tied to code.
- Schema constants: `repository_url` const, step commits const `PUB`/`REC`.

### Anti-Patterns to Avoid
- **`git worktree add` at the pin:** writes `.git/worktrees` admin state into the user's (and Hayes's) repository. It needs cleanup that a crash skips, and it checks out with `core.autocrlf` conversion (this machine: `core.autocrlf=true`). Use the temp materialisation from `git show` blobs instead.
- **Setting `GIT_DIR` / other `GIT_*` env vars** so git works from the temp dir: this leaks into every subprocess, and it runs against the deferred AR-03 direction (scrub ambient `GIT_*`).
- **Temp dir inside the repo** (so git discovery works with no rebind): this leaves debris when interrupted. Anything under `generated/archive-assessment/ems-aa3-v2/` breaks the publisher's at-pin `git_dirty` check (it lists ignored files in `OUT`).
- **Patching pinned source text before `exec`**, or replacing pinned functions such as `git_show`: this weakens "the pinned code ran". The single `ROOT` rebind is the only intervention.
- **Importing the 2.0.2 builder or the live publisher**: forbidden by D-12 and FROZEN-02.
- **Counting mutations from the frozen file** (the 2.0.2 WR-01 flaw): the count must come from the rerun.
- **Copying the 2.0.2 `publisher_refs` AST scanner test verbatim**: the 2.0.3 builder legitimately calls `spec_from_file_location` and holds the publisher's relative path as a git path string, so that scanner would always fail. Replace it with behavioural tests (Pitfall 7).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Re-implementing mutations / gates | A copy of `NEGATIVE_MUTATIONS` or `mutation_gates` in the builder | The pinned publisher's own `run_mutations` (Pattern 1) | D-01; a copy would prove the copy, not the certified code |
| Extracting `AT_PIN_DEFERRED` | Retyped string | `pub.AT_PIN_DEFERRED` from the loaded pinned module | D-11; notice and tool cannot disagree |
| Schema strictness | Hand-written JSON | `schema()` with `obj()` helper (`additionalProperties: False`, `required: list(props)`) from `47343a1` | Consistent closed levels; D-13 byte compare |
| Git error handling | Ad-hoc `subprocess` calls | Copied `git_show` (40-hex SHA + `bad_rel` checks, `GitHistoryError` with fetch hint) and `resolve_record_commit` from the current 2.0.2 builder | 12-03 uniform handling; tests already define expected messages |
| Sign-off check | New code | Copied `validate_signoff` (four-argument form) from the 2.0.2 builder with 2.0.3 id/version | FROZEN-02 pattern |

## Runtime State Inventory

Not a rename/refactor phase. For completeness, the runtime state the phase touches:

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None. No datastore; all state is git-tracked files | None |
| Live service config | GitHub remote branch `feature/ems-aa3-archive-applicability-authority`, tip `5498002` (verified `git ls-remote`); local `.planning` commits after it (`3fd54ac`, `144934b`, `f1212f9`, `4bc5401`, `ed222e3`, `72aed55`, `8c63687`, `e539c0e`) not yet pushed | Push at D-14 gate with token workaround (STATE.md) |
| OS-registered state | None | None |
| Secrets/env vars | GitHub CLI token used transiently as `http.extraheader` for push (STATE.md); the harness sets `GIT_EDITOR`/`GIT_ASKPASS`/`GIT_TERMINAL_PROMPT`, which Phase 13 removed in-process before git calls | Same push procedure as Phase 13 |
| Build artifacts | `__pycache__` written into the temp dir by `exec_module` (removed with it) | None |

## Common Pitfalls

### Pitfall 1: The D-09 install command omits jsonschema (blocks Hayes at step 1)
**What goes wrong:** `pip install -r requirements.txt` at `1544dc1` installs only PyYAML and Jinja2. `python scripts/publish_…_v2.py --validate --at-pin` then fails with `ModuleNotFoundError: No module named 'jsonschema'`.
**Why:** CI installs jsonschema separately (`pip install -r requirements.txt jsonschema pytest`). `requirements-dev.txt` is untracked.
**How to avoid:** The notice prerequisite and step text should say `python -m pip install -r requirements.txt jsonschema` (the CI form without pytest). Optionally name the verified version 4.26.0. Changing `requirements.txt` is out of scope: it would not exist at the pin. **Flag to the user at plan time**, because this adjusts locked D-09 wording.
**Warning signs:** An operator dry run of step 1 in a fresh venv fails on import.

### Pitfall 2: Pinned module path constants silently reading live files
**What goes wrong:** If the publisher is exec'd with `__file__` = the real path (as the 2.0.2 tests' `frozen_publisher` helper does), then `GOVERNANCE_DECISIONS`, `V1_AUTHORITY`, `BUILDER_SCRIPT` and the builder's `PROPOSALS`/`ANSWERS`/... point at the working tree. The live builder module also gets executed.
**How to avoid:** Use Pattern 1, and assert after the run that every path constant (and `b.__file__`, `b.V2.__file__`) resolves under the temp dir.
**Warning signs:** The "live publisher/builder edited" clone test changes outcome.

### Pitfall 3: Vacuous rejections (a missing pinned file makes everything "rejected")
**What goes wrong:** If, for example, `registry/archive_assessment_governance_answers.json` were not materialised, the pinned `validate_decisions` would append `answers_sha256 does not match the live answers file` for **every** document. Each DECISIONS mutation would then still show `PYTHON_VALIDATOR`, so a broken setup would look like a pass. The D-02 equality to the frozen file would likely still match for those entries.
**How to avoid:** Run the baseline-accepts check on the unmutated authority, sign-off and decisions with the same pinned gates before `run_mutations` (Pattern 1). Add a test that drops one materialised data file and expects the baseline check to fail with a specific message.

### Pitfall 4: Exception class identity across module copies
**What goes wrong:** The pinned `pub.AuthorityError`, the builder's `b.AuthorityError` (= its nested `b.V2.AuthorityError`) and the notice builder's `AuthorityError` are three different classes. `except AuthorityError` in the notice builder will not catch pinned errors, so tests with `pytest.raises(MODULE.AuthorityError)` fail confusingly.
**How to avoid:** Wrap everything raised inside `pinned_mutation_run` into the builder's own classes, mapping a pinned `GitHistoryError` (by class name or `isinstance(e, pub.GitHistoryError)`) to the builder's `GitHistoryError`.

### Pitfall 5: A test fails for a reason other than its name (10-REVIEW WR-03)
**What goes wrong:** `build_notice` binds the authority and record first, so a lineage tamper test that goes through `build_notice` fails at an earlier binding.
**How to avoid:** Call the target function directly (`lineage_entries`, `digest_scope_error`, `check_rerun`) with a specific `match=`. For git-level claims, serve edited bytes through a monkeypatched `MODULE.git_show` keyed on `(commit, path)` (the 2.0.2 `serve_edited` helper). Order the checks inside each function so the named check is the first one that can fire. For example, raw==LF comes before raw==recorded: serving LF-only bytes would otherwise trip the recorded-digest check first.

### Pitfall 6: The notice cannot name its own commit
**What goes wrong:** Step 3 says "at the notice commit or later", but the notice file cannot contain the SHA of the commit that adds it.
**How to avoid:** Phrase step 3 as `git checkout feature/ems-aa3-archive-applicability-authority` (the `REMOTE_BRANCH` constant already in the 2.0.2 builder) "at or after the commit that adds this notice". Do not invent a SHA.

### Pitfall 7: The "live publisher edit" test proving nothing
**What goes wrong:** The live publisher and decisions builder currently equal the pinned blobs (`git diff 1544dc1 HEAD` on both: empty). A test that does not actually change them is vacuous.
**How to avoid:** Use the Phase 12 D-10 clone pattern (`git -c core.longpaths=true clone --shared -q ROOT <tmp>/c`):
1. Copy the working-tree 2.0.3 builder and the three notice files into the clone, so the test also works before they are committed.
2. Assert the baseline `python scripts/build_…_2_0_3.py --validate` returns `(0, 'PASS')` (the 13-03 WR-03 lesson).
3. Overwrite `scripts/publish_archive_assessment_applicability_authority_v2.py` **and** `scripts/build_archive_assessment_governance_decisions.py` in the clone with `raise SystemExit('mutated live file executed')`.
4. Assert the outcome is unchanged. Optionally also run `--build` in the clone and assert byte-identical outputs.

Two runs take about 20 s. Acceptable for one test.

### Pitfall 8: Overclaiming test status
13-VERIFICATION advisory: do not claim "all tests green at the publication commit". It is accurate to say that `--validate --at-pin` passes at PUB and plain `--validate` passes at REC and later. CI run ids stay in planning docs (carried decision).

### Pitfall 9: Slow tests
Each full build reruns 29 mutations (≈6.7 s on this machine; the 2.0.2 `--validate` takes ≈3.3 s). Cache `load_inputs()` once per test module (the rerun result is part of the tuple). Pass tuples or edited copies into `build_notice`. Reserve full `validate_notice()` runs for the committed-files test, the CLI test, the clone test and a few tamper tests (monkeypatch `pinned_mutation_run` to return the cached result where the test is not about mutations).

### Pitfall 10: Forbidden words / emphasis
Keep the `FORBIDDEN_WORDS` check (`best, critical, important, recommended, highest`) over rendered Markdown and JSON. D-06 requires the fixed verification-changes line to be plain. Check that the quoted `AT_PIN_DEFERRED` and the pinned error texts contain none of these (verified: they do not).

## Code Examples

### Loading inputs and binding (copy from current 2.0.2 builder, extend)
Source: `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` L129-193 (in repo).
- `resolve_record_commit()` iterates frozen commits: PUB, REC, 2.0.2 `ae15c74`, 2.0.1 `31addfa`. Each must exist and be an ancestor of HEAD; also require PUB to be an ancestor of REC.
- `load_inputs()` returns the 2.0.3 authority @PUB, the 2.0.2 authority @ae15c74 and the 2.0.1 authority @31addfa (all at the same path `registry/archive_assessment_applicability_authority_v2.json`). It also returns the record @REC, the signoff, decisions, manifest, authority schema, negative and trace (all @PUB), and the pinned rerun.
- Record binding: `record['publication_commit'] == PUB`; the record's authority/manifest LF digests equal the blobs at PUB; `check_inputs_bound(manifest)` covers the signoff, schema, authority, negative and trace artifacts.
- Supersedes binding: `authority.source_lineage.supersedes == {2.0.2 id, '2.0.2', ae15c74, …}`, and `previous_2_0_2.source_lineage.supersedes.commit == 31addfa`. This gives the D-06 "moved from 2.0.1 at 31addfa to 2.0.2 at ae15c74" as derived data.

### Test skeleton for the claims (D-15)
```python
def test_rerun_rejects_unrejected_mutation():          # CLAIM-01
    rerun = copy.deepcopy(INPUTS_RERUN); rerun[0]['rejected_by'] = []
    with pytest.raises(AuthorityError, match='mutation swapped_authority was not rejected by the rerun'): MODULE.check_rerun(rerun, NEGATIVE)

def test_pinned_code_accepting_a_mutation_fails(monkeypatch):   # CLAIM-01 via the real pinned run
    real = MODULE.load_pinned_publisher
    def with_noop(tmp):
        pub = real(tmp); pub.NEGATIVE_MUTATIONS = [*pub.NEGATIVE_MUTATIONS, pub.Mutation('noop', 'No change.', 'AUTHORITY', lambda a: None)]; return pub
    monkeypatch.setattr(MODULE, 'load_pinned_publisher', with_noop)
    with pytest.raises(AuthorityError, match='pinned mutation run failed: AuthorityError: mutation noop was accepted'): MODULE.pinned_mutation_run(*ARGS)

def test_rerun_differs_from_recorded():                 # D-02
    neg = copy.deepcopy(NEGATIVE); neg['negative_invariant_tests'][2]['rejected_by'] = ['SCHEMA']
    with pytest.raises(AuthorityError, match='the mutation rerun differs from the frozen negative-invariant output'): MODULE.check_rerun(INPUTS_RERUN, neg)

def test_frozen_negative_not_pass():                    # D-02
    neg = dict(NEGATIVE, result='FAIL')
    with pytest.raises(AuthorityError, match='frozen negative-invariant result at the pin is not PASS'): MODULE.check_rerun(INPUTS_RERUN, neg)

@pytest.mark.parametrize('key', sorted(MODULE.LINEAGE_NORMALISATION))   # CLAIM-02, 7 cases
def test_wrong_lineage_digest(key):
    a = copy.deepcopy(AUTHORITY); a['source_lineage'][key]['sha256'] = '0' * 64
    with pytest.raises(AuthorityError, match=f'source_lineage {key}: recomputed sha256 at [0-9a-f]{{40}} differs'): MODULE.lineage_entries(a)

@pytest.mark.parametrize('key', ['aa1_manifest', 'aa2_approval', 'aa2_closure'])  # CLAIM-03
def test_raw_equals_lf_blocks_wrong_scope_statement(monkeypatch, key):
    path = AUTHORITY['source_lineage'][key]['relative_path']; real = MODULE.git_show
    monkeypatch.setattr(MODULE, 'git_show', lambda c, p: real(c, p).replace(b'\r\n', b'\n') if (c, p) == (MODULE.NOTICE_PUBLICATION_COMMIT, path) else real(c, p))
    with pytest.raises(AuthorityError, match=f'{key}: raw sha256 equals its LF sha256'): MODULE.digest_scope_error(AUTHORITY, PREV_2_0_1)
```
Also needed:
- tamper tests for each cited id/version/commit (schema `const` → `jsonschema.ValidationError` with `validator == 'const'`, and the committed-bytes path → `notice JSON differs from a fresh build`);
- a committed-files test with no monkeypatching that requires history (FROZEN-04);
- shallow/unknown-commit fake-git tests (copied from the 2.0.2 tests);
- **a non-skipping fail-closed history test**: monkeypatch `git_show` to raise `GitHistoryError`, which must raise, not skip;
- the baseline-file-missing test (Pitfall 3);
- the path-constants-in-tmp assertion;
- the clone test (Pitfall 7);
- a CLI test checking `--build`/`--emit-schema`/`--validate` mutual exclusion.

## State of the Art

| Old Approach (2.0.2 notice) | Current Approach (2.0.3 notice) | Impact |
|-----------------------------|---------------------------------|--------|
| Mutation count = `len(frozen tests)` (WR-01) | Pinned `run_mutations` rerun, compared to the frozen file | CLAIM-01 |
| 3 of 7 lineage digests re-hashed (raw only), 4 echoed (WR-04) | All 7 re-hashed with the declared normaliser at the entry's commit | CLAIM-02 |
| "Wrong scope" asserted from string equality (WR-05) | raw≠LF computed and both hashes shown | CLAIM-03 |
| No verify-at-pin instructions (PIN-03 gap) | 3-step command sequence and outcome table, deferred text quoted from the pinned code | PIN-03 |
| Schema frozen at `052f0f1` commit constant | Live committed schema byte-compared to `schema()` (D-13) | Simpler; freezing deferred |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `git show <sha>:<path>` emits the raw blob with no eol/textconv conversion (textconv applies to blobs only with explicit `--textconv`) | Patterns 2/3 | Low: every recomputed digest in this session matched the recorded raw values, and the pinned publisher relies on the same call [ASSUMED for the mechanism, empirically consistent] |
| A2 | The pinned-run timing (≈7 s on Windows) is similar or faster on ubuntu CI | Pitfall 9 | Low: only affects CI duration |
| A3 | Hayes will run the commands in a POSIX or PowerShell shell where `python` is 3.12 | Verify section | Low/medium: the notice may add "use the Python 3.12 interpreter (`py -3.12` on Windows)"; wording is discretionary |
| A4 | Users accept changing the D-09 install text to `pip install -r requirements.txt jsonschema` | Pitfall 1 | Medium: if refused, step 1 fails for Hayes. Requires user confirmation |

## Open Questions

1. **D-09 install command (Pitfall 1)**
   - Known: `requirements.txt` at the pin lacks jsonschema; CI adds it.
   - Unclear: whether the user wants the exact version named.
   - Recommendation: `python -m pip install -r requirements.txt jsonschema`, and state that jsonschema 4.26.0 was the version used for verification. Confirm at the D-14 Markdown review at the latest, preferably during planning.
2. **Should the 8th digest (`supersedes.governance_decisions_sha256`) be shown?**
   - Recommendation: recompute it at `ae15c74` and show it as the "decisions digest unchanged" evidence. Keep exactly 7 lineage rows (D-07).
3. **`.gitattributes` for the new notice files**
   - The 2.0.2 notice files have no entry, and `eol=lf` is deferred (12 D-15). Validation compares after LF normalisation, so a Windows `autocrlf=true` checkout passes. Recommendation: no `.gitattributes` change.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 (`.venv`) | builder, tests | ✓ | 3.12.10 | — |
| jsonschema | builder, pinned publisher | ✓ | 4.26.0 | — |
| PyYAML | pinned publisher | ✓ | 6.0.3 | — |
| pytest | tests (orchestrator only) | ✓ | 9.1.1 | — |
| git | all history reads | ✓ | 2.54.0.windows.1 (`core.autocrlf=true` in `.git/config`) | — |
| gh | dispatch/run view at the push gate | ✓ | 2.91.0 | — |
| Full history | resolve_record_commit, tests | ✓ (not shallow; all frozen commits present) | — | — |
| Bash tool | research only | worked this session (flaky per memory) | — | PowerShell from the orchestrator for pytest/validators |

**Missing dependencies with no fallback:** none.

## Validation Architecture

Skipped: `workflow.nyquist_validation` is `false` in `.planning/config.json` (committed value). The test map required by D-15 is in Code Examples and Pitfalls 3/5/7/9.

## Security Domain

`security_enforcement: true`, ASVS level 1.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | `git_show` validates a 40-hex SHA and a repo-relative path (`bad_rel`); lineage `relative_path` values from the authority pass through it before git and before temp-dir writes; closed JSON Schema (Draft 2020-12) on the notice |
| V6 Cryptography | yes (integrity only) | `hashlib.sha256`; never a custom digest |
| V10 Malicious Code / V14 Config | yes | Executed code is only the content-addressed blob at PUB whose LF sha256 equals the certified `publisher_script.sha256`. Repo URL is a constant (D-10) |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Executing a tampered live publisher/builder during notice validation | Tampering / EoP | Pattern 1 (temp materialisation from git blobs, publisher digest check against the manifest, path-constants-in-tmp assertion, clone test) |
| Path traversal when materialising files into the temp dir | Tampering | Fixed constant list of 9 paths (not data-driven); `bad_rel` on every path |
| Git option injection via SHA/path | Tampering | 40-hex regex; `commit:path` single argument; consider the `--` terminator as the pinned publisher uses |
| Shallow or partial clone producing false PASS | Spoofing | `rev-parse --is-shallow-repository` must print exactly `false`; `cat-file -e` and ancestry checks; non-skipping fail-closed test |
| Notice overstating checks (signed statement to an external assessor) | Repudiation | Every claim is computed and `--validate` byte-rebuilds; per-claim tests with specific `match=` |
| Ambient `GIT_*` environment redirecting git | Tampering | Deferred (AR-03); do not add `GIT_*` usage in the builder |
| Temp dir left behind | Info disclosure (low) | `tempfile.TemporaryDirectory()` context; contents are public repo blobs |

## Sources

### Primary (HIGH confidence)
- Repository at `1544dc1`/`87a46d1`/`ae15c74`/`31addfa`/`62a8955`, via `git show`, `git diff`, `git rev-parse`, `git ls-remote`: all facts in the Pinned Facts table.
- Executed probes (scratchpad): `pin_mutations_probe.py` (rerun == frozen, 29/29; failure without `ROOT` rebind), `audit_probe.py` (all opens inside the temp dir; baseline OK; `schema()` == pinned schema), `lineage_probe.py` (7 digests; raw/LF pairs; 2.0.1 values; 16 levels).
- `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` (current) and its version at `47343a1` (`--build`/`--emit-schema`/`schema()`).
- `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`, `tests/aa_history.py`, `tests/test_archive_assessment_lineage_validation.py` (D-10 clone test).
- `.planning/phases/10-notice-to-hayes/10-REVIEW.md` (WR-01..05, IN-01/02); `.planning/phases/13-…/13-VERIFICATION.md` (at-pin evidence, overclaim advisory).
- `.github/workflows/ems-validate.yml` (`archive-assessment` job: `fetch-depth: 0`, installs `jsonschema` separately).

### Secondary / Tertiary
- None. No web sources were needed; this phase is entirely repository-internal.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH (no new dependencies; versions read locally).
- Architecture (pinned run): HIGH (executed end to end against real history, with audit-hook evidence).
- Pitfalls: HIGH for 1-7 (each observed or derived from code read this session); MEDIUM for 9 (timing, Windows only).

**Research date:** 2026-11-17
**Valid until:** while PUB/REC are the cited pin; recheck if anything under `scripts/` that the pinned run materialises changes in the plan (it must not).
