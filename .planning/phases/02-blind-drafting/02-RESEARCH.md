# Phase 2: Blind Drafting - Research

**Researched:** 2026-10-13
**Domain:** Tooling and git mechanics for a frozen, isolated-drafter proposals file (no domain library research needed)
**Confidence:** HIGH (all findings come from files in this repo, checked in this session)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
D-01..D-28 in `.planning/phases/02-blind-drafting/02-CONTEXT.md` are locked and are copied by reference, not restated. The ones that drive planning most:
- D-01: only EMS-source input is the control's entry in `registry/control_catalog.yaml`.
- D-04: embed exact catalog values per proposal; record catalog SHA-256 + git blob id once; a test re-reads the catalog and fails on any mismatch.
- D-11/D-12: one JSON file under `registry/`, status `DRAFT_NO_AUTHORITY`; per-proposal fields `control_id, proposed_outcome, proposed_rule, catalog_inputs, interpretation, rationale, confidence, alternative_considered, shape_limitation`. No authority id, no decision id.
- D-13: validator script (`build`/`validate` split, accumulate-then-raise `AuthorityError`), emits its own schema, reuses `validate_rule()` from the v2 publisher; pytest module.
- D-14: no digest certification/manifest. D-15: file frozen after drafting commit.
- D-16..D-23: one isolated AI drafter, fixed approved brief (committed first), orchestrator writes output unchanged, correction rounds = validator error messages only.
- D-24: drafting-record JSON committed in a LATER commit, with a test that the recorded SHA is an ancestor containing the proposals file.
- D-25: term-scan pytest over proposals file, brief and drafting record; the term list lives only in the test.

### Claude's Discretion
File names (snake_case, v2-style), where brief and drafting record live (tracked, not `generated/`), exact JSON keys/enum values, ordering of tooling commits vs brief commit (brief approved+committed before drafter runs; one drafting commit with all 21; record in a later commit; no red tests in between), ancestor-test behaviour in shallow clones.

### Deferred Ideas (OUT OF SCOPE)
Other EMS files as drafting inputs; writing catalog descriptions; a second drafter; Markdown view of proposals.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DRAFT-01 | Rule-or-no-rule proposal with rationale for each of 21 controls | Proposals schema + validator (below); `validate_rule()` reuse; exact-21 check |
| DRAFT-02 | EMS-source inputs = catalog definitions only; interpretation labelled; frame declared once; no forbidden terms | `catalog_inputs` embed + catalog-drift test; header drafting frame built from `semantics()`; term-scan test |
| DRAFT-03 | One drafting commit precedes any decision; SHA recorded later | Staging recipe, drafting-record file, ancestor test (below) |
</phase_requirements>

## Summary

Phase 2 is almost entirely process and tooling. Everything needed already exists in `scripts/publish_archive_assessment_applicability_authority_v2.py`: `validate_rule()`, `RULE_FIELDS`, `CONDITION_STATES`, `COMBINATION`, `semantics()`, `FIELD_DEFINITIONS`, `RESOLUTION`, `catalog_controls()`, `digest()`, `dump()`, `load()`, `contains_absolute()`, `AuthorityError`. The module is committed (tracked), has no import-time side effects (argparse is inside `main()`), and tests load it via `importlib.util.spec_from_file_location` - copy that pattern rather than importing from `scripts` as a package.

The published v2 authority registry file does NOT exist yet (`registry/archive_assessment_applicability_authority_v2.json` is untracked/absent); only the v2 script and schema are tracked. This phase must not create it. The v1 authority file and its certification are untouched by anything recommended here.

Key practical facts: the 21 catalog entries all carry exactly the same 8 keys (`control_id, control_name, scope, scope_owner, inheritance_allowed, evidence_authority, rationale, classification_status`), no `description` [VERIFIED: python yaml read of registry/control_catalog.yaml]. The catalog is tracked, clean in the working tree, CRLF-encoded; working-file git blob id equals HEAD blob id (`03c9faa4...`) [VERIFIED: git hash-object / rev-parse]. CI (`.github/workflows/ems-validate.yml`) does not run pytest, so the ancestor-commit test only matters locally, but should still skip cleanly in a shallow clone.

**Primary recommendation:** Build tooling in 2-3 small commits (validator+schema+tests, brief), commit the brief, run the isolated drafter, write its JSON unchanged, validate, `git add <explicit path>` + `git commit` for the proposals file alone, then a later commit for the drafting record. Never `git add -A`/`-a`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary | Rationale |
|------------|-------------|-----------|-----------|
| Proposal content | Isolated drafter (AI, no file tools) | - | D-16/D-17 |
| Shape validation of proposals | `scripts/` validator reusing v2 `validate_rule` | tests | D-13 |
| Catalog drift check | tests (re-read catalog) | validator | D-04 |
| Ordering proof | git history + drafting record + ancestor test | - | D-24 |
| Blindness proof (terms) | pytest term-scan | - | D-25 |

## Standard Stack

Python 3.12.10, pytest 8.4.2, `jsonschema`, `PyYAML` - all already in use [VERIFIED: `python --version`, `pytest --version`]. No new packages; no Package Legitimacy Audit needed (none installed).

## Phase 1 Frame (what the brief inlines)

Source of truth is code: `semantics()` / `FIELD_DEFINITIONS` / `RESOLUTION` in the v2 publisher [VERIFIED: file read].
- Rule shape: `{"combination": "ALL_CONDITIONS_MUST_MATCH", "conditions": [{"field": <one of 4>, "state": "KNOWN_TRUE"|"KNOWN_FALSE"}]}`; 1..4 conditions; each field at most once; exactly those keys.
- Usable fields: `production, internet_exposed, contains_customer_data, ai_enabled`. The other four (`owner, tier, service_criticality, data_classification`) are declared but not usable in rules.
- Resolution: no rule -> `APPLICABLE` always; rule, all named fields known and all met -> `NOT_APPLICABLE`; all known and not all met -> `APPLICABLE`; any named field `UNKNOWN` -> `APPLICABILITY_UNRESOLVED`. UNKNOWN never yields not-applicable.
- Approved field definitions (status APPROVED, Oscar Mack, 2026-10-13): `.planning/phases/01-rule-shape-and-decision-states/01-FIELD-DEFINITIONS.md`, and identical text in `FIELD_DEFINITIONS`. NOTE: that .md file contains `Source:` lines naming other EMS files (`registry/wave2d/applicability_rules.json`, `config/repository_overrides.example.yaml`). The brief must inline only the four definition sentences from `FIELD_DEFINITIONS`, not those Source lines or the file, so the drafter gets the frame without extra inputs (D-01/D-05). Also do not point the drafter at `.planning/` at all (D-16).
- Brief wording hazard: the v2 `semantics()` statements are clean of the D-25 terms [VERIFIED by reading], but the brief must be generated/checked by the term-scan test; do not copy text from `.planning/` files (CONTEXT/REQUIREMENTS contain the forbidden terms and the request id).

## Architecture Patterns

### Recommended layout (names are discretionary)
```
registry/archive_assessment_not_applicable_rule_proposals.json    # drafter output, frozen
schemas/archive_assessment_not_applicable_rule_proposals.schema.json  # emitted by validator --emit-schema
scripts/validate_archive_assessment_rule_proposals.py              # build_schema/validate_proposals/main
tests/test_archive_assessment_rule_proposals.py
docs/ or registry/ ...  drafter brief (tracked; e.g. docs/ARCHIVE_ASSESSMENT_RULE_DRAFTER_BRIEF.md)
registry/archive_assessment_rule_proposals_drafting_record.json    # later commit
```
Do not name anything with a D-25 term (including the request id). Do not put files under `generated/` (gitignored).

### Validator design
- Pure `validate_proposals(p, catalog=None)` raising `AuthorityError` with `'; '.join(errors)`; `schema()` function and `--validate` / `--emit-schema` CLI like v2 `main()`.
- Checks: top-level `status == 'DRAFT_NO_AUTHORITY'`; non-authority statement present; header drafting frame equals `semantics()` pieces (rule fields, states, combination, resolution, field definitions) so frame drift is caught; exactly 21 proposals, ids equal the fixed list, no duplicates; each `proposed_outcome` in two enum values (suggest `PROPOSE_RULE` / `PROPOSE_NO_RULE`); rule present iff PROPOSE_RULE, validated via imported `validate_rule(cid, rule, errors)`; `confidence` enum; `alternative_considered` string or null; `shape_limitation` object/null (define a structured form); `interpretation` non-empty and labelled; rationale 2-4 sentences (D-27) - check sentence count loosely; reject keys `not_applicable_authority`, `decision_id`, any `AA4-GOV-` pattern; `contains_absolute`; each `catalog_inputs` has at least `control_name, scope, scope_owner, evidence_authority`.
- Test style to copy: `invalid(mutator)` with deepcopy + `pytest.raises(AuthorityError)`, `ok(mutator)`, `schema_rejects(mutator)`.
- Since the real file does not exist while tooling is built, tests need a fixture proposals object (built in-test, neutral placeholder text, NOT using plausible per-control outcomes beyond what is needed). Important: the tests that read the real file must not be committed red before the drafting commit. Plan: tooling-phase tests run only against an in-test fixture; a separate real-file test class is added in the SAME commit as the proposals file (or skips when file absent - but skip-if-absent weakens the guarantee; prefer adding the real-file tests in the drafting commit... however that commit must contain only the 21 proposals per criterion 3). Resolution: let the real-file tests live in the tooling test module from the start with `pytest.mark.skipif(not PROPOSALS.exists())`, plus a final assertion in the drafting-record commit's tests that the file exists (no skip once the record exists). Flag for planner (see Open Questions).
- Term-scan (D-25): list of terms in the test only. Use `re.IGNORECASE`, scan raw file text. Terms: the RiskMVP name, the RiskMVP commit SHA and its short form, the consumer name, `2026-10-01`, the absent-rule reason code, and the request id. The test file itself contains the terms - fine, it is not scanned. Executor note: obtain the SHA/short form from the user/`STATE.md` when writing the test; this research deliberately does not reproduce them.
- Catalog drift (D-04): test loads `registry/control_catalog.yaml`, compares each embedded value to the catalog entry, and compares recorded `sha256` of the file bytes and the git blob id. Because the catalog is CRLF with no `.gitattributes`, compute sha256 on raw bytes (`Path.read_bytes()`, as `digest()` does) and blob id with `git hash-object`; both match HEAD today [VERIFIED]. If the catalog legitimately changes later the test goes red by design; that is acceptable but the record should state it (consider comparing against the blob at the drafting commit via `git show <sha>:registry/control_catalog.yaml` instead for robustness - recommended).

## Single drafting commit without the dirty tree

Tree state [VERIFIED: git status]: tracked-modified `registry/adjudication_rules.json`, `registry/policy_decisions.json`; many untracked docs/registry files and `.pytest-*` dirs. Nothing is staged now.

Recipe:
1. `git diff --cached --name-only` must be empty before starting (check, do not assume).
2. `git add -- registry/archive_assessment_not_applicable_rule_proposals.json` (explicit path only).
3. `git diff --cached --name-only` must list exactly that one path.
4. `git commit -m "..."` (no `-a`). Alternative: `git commit -m ... -- <path>` (commits only that path, ignores other index contents). Commit message must not contain D-25 terms (commit messages are not scanned, but keep clean anyway).
5. Capture SHA: `git rev-parse HEAD`.
6. Verify: `git show --stat --name-only HEAD` shows one file; `git status --short` still shows the unrelated files unchanged.
Same recipe for the brief commit and tooling commits. Never `git add .`/`-A`/`-u`.

Constraints satisfied: criterion 3 "no decision record or new authority version exists at that commit" - true because none exist anywhere yet; the drafting commit should be a pure one-file commit. Planning-doc commits (`docs(...)`) may interleave elsewhere, but not within the drafting commit.

Line endings: git `core.autocrlf=true` here and no `.gitattributes` [VERIFIED]. Write the proposals file with LF (`dump()` style: `json.dumps(indent=2, sort_keys=True)+'\n'`; or, because D-17 says write returned content unchanged, write bytes as produced and only normalise through the same function every time). `git add` may warn "LF will be replaced by CRLF" and store LF in the blob. The file hash in the drafting record must therefore be taken from the committed blob (`git show <sha>:path` bytes, or `git rev-parse <sha>:path`) rather than from a possibly CRLF-checked-out working file; the record test should compute SHA-256 over `git show` bytes. Same for the brief hash. This is the main hidden pitfall. Note D-17 "unchanged" vs deterministic `sort_keys` re-dump: sorting keys would alter the drafter's output ordering; decide whether the file is written verbatim (recommended: write verbatim, validator parses it, no re-serialisation) - planner should state this explicitly.

## Recording the SHA later (DRAFT-03)

- Drafting record JSON (D-24) in its own later commit, containing the SHA from step 5. A commit cannot contain its own SHA, hence "later".
- Ancestor test: `git merge-base --is-ancestor <sha> HEAD` (exit 0 = ancestor); `git cat-file -e <sha>:registry/<proposals>.json`; blob content at that sha SHA-256 equals recorded `proposals_sha256` and equals current file (frozen, D-15); and `git rev-list --max-parents=0`-style checks are unnecessary. Additionally assert the drafting commit changed exactly one path: `git diff-tree --no-commit-id --name-only -r <sha>` == [proposals path]. Assert commit date order is not reliable; ancestry is the proof. Optionally assert that no decision-record file or v2 registry file exists in the tree at `<sha>` (`git ls-tree -r --name-only <sha>` has no `archive_assessment_applicability_authority_v2.json` and no decision-record path).
- Shallow clone handling: `git rev-parse --is-shallow-repository` returns `true` -> `pytest.skip`; also skip if `git` is unavailable or `cat-file -e <sha>` fails with "bad object" in a shallow context. Locally the repo is not shallow [VERIFIED: false]. CI does not currently run pytest [VERIFIED: workflow greps], so this is defensive.
- Use `subprocess.run([...], cwd=ROOT, capture_output=True, text=True)`; no shell strings (Windows-safe).

## Isolation mechanics (practical notes)

- The drafter is a separate sub-agent started with the brief text inline and no file tools (D-17). The orchestrating session already has planning files in context, so the orchestrator must only pass the brief verbatim plus validator error text - nothing else. Record the model id of the drafter for the drafting record.
- Extracting the 21 catalog entries verbatim for the brief: generate programmatically from the YAML (e.g. `yaml.safe_load` then dump only those 21), so no hand editing; embed in the brief. Do not run per-control checks of "what the answer is".
- Brief must contain no worked example using any of the 21 controls (specifics note). Use only a placeholder/abstract JSON skeleton (`"control_id": "<ID>"`).
- Terms: brief cannot mention the assessment, a target, a consumer; refer only to "an archived repository snapshot target" (D-18, matches `target_type` in the authority).
- Brief approval (D-19): Oscar Mack approves the instructions (not proposals); record approval in the commit message or a small approval line in the brief header (without forbidden terms). The brief's SHA-256 (from committed blob) goes in the drafting record.
- Correction rounds (D-21): keep a plain counter in the orchestrator; the record stores the number.

## Don't Hand-Roll

| Problem | Use Instead |
|---------|-------------|
| Rule-shape validation | import `validate_rule` from the v2 publisher (load via importlib like the v2 tests) |
| Frame text | `semantics()`, `FIELD_DEFINITIONS`, `RESOLUTION` |
| Catalog load | `catalog_controls()` (asserts 80 unique ids) |
| Hashing | `digest()` / `hashlib.sha256` over bytes; `git hash-object` for blob id |

## Common Pitfalls

1. **Staging too much.** `git commit -a` or `git add .` would sweep `registry/adjudication_rules.json` / `policy_decisions.json`. Mitigation: explicit paths plus a pre-commit `git diff --cached --name-only` assertion in the plan task.
2. **CRLF hashing mismatch** (above). Hash committed blob bytes.
3. **Red tests between commits.** Real-file tests must skip (or be added with the file) until the proposals file exists; the drafting-record tests must not run before the record exists. Gate each on file existence, and add a final "exists" assertion when the record lands.
4. **Forbidden terms leaking via copy.** Planning docs contain them; scan brief/proposals/record only after writing, and generate the brief from code/inline text, not by copy from `.planning/`.
5. **Rewriting drafter output.** D-20/D-15 forbid review/edits; even `sort_keys` re-dump is a transformation. Decide up front and document.
6. **Importing v2 publisher fails on its missing registry file?** It does not: module-level code only defines constants/functions; `AUTHORITY` is just a path [VERIFIED]. `build_authority()` reads the v1 file and catalog, both tracked.
7. **Touching the v1/v2 authority or its certification.** Do not run `--validate` flows that write; this phase writes no file under those names. The existing `tests/test_archive_assessment_applicability_authority*.py` should still pass unchanged - run them as a regression check.
8. **Proposals schema accidentally defining `not_applicable_authority`/decision ids.** Schema should forbid them (additionalProperties false).
9. **Over-claiming blindness.** The record states isolation "by instruction and brief design" only (D-24); do not claim technical isolation.

## Code Examples

Load the v2 module (pattern from `tests/test_archive_assessment_applicability_authority_v2.py`):
```python
SCRIPT = Path(__file__).parents[1] / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py'
SPEC = importlib.util.spec_from_file_location('aa3_authority_v2', SCRIPT)
V2 = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(V2)
# V2.validate_rule(cid, rule, errors) appends to errors; V2.AuthorityError
```
Ancestor check:
```python
def git(*a): return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True)
if git('rev-parse', '--is-shallow-repository').stdout.strip() == 'true': pytest.skip('shallow clone')
assert git('merge-base', '--is-ancestor', sha, 'HEAD').returncode == 0
blob = subprocess.run(['git', 'show', f'{sha}:{PATH}'], cwd=ROOT, capture_output=True).stdout
assert hashlib.sha256(blob).hexdigest() == record['proposals_sha256']
```

## Environment Availability

| Dependency | Available | Version |
|------------|-----------|---------|
| Python | yes | 3.12.10 |
| pytest | yes | 8.4.2 |
| git | yes | repo non-shallow; autocrlf=true |

## Validation Architecture

Skipped: `workflow.nyquist_validation` is false in `.planning/config.json`. (Validation approach is covered by the validator/pytest design above.)

## Security Domain

Not applicable beyond input hygiene: the validator rejects absolute paths and unknown keys; no secrets or network involved. The main integrity control is process (git ordering + term scan).

## Assumptions Log

| # | Claim | Risk if Wrong |
|---|-------|---------------|
| A1 | `git commit -- <path>` semantics and `add` then `commit` both yield a single-file commit given an empty index | Low; plan includes a `--name-only` assertion |
| A2 | Hashing committed blob bytes avoids autocrlf drift | Low; verify once with `git show` vs `Path.read_bytes()` after commit |
| A3 | Sentence-count check for rationales (2-4) can be done heuristically | Low; may be loosened to non-empty |

## Open Questions

1. **Real-file tests before the drafting commit.** Skip-if-absent vs. adding them in the drafting-record commit. Recommendation: tooling test module holds fixture-only tests plus real-file tests gated on existence; record commit adds an unconditional existence check. Planner to confirm with user, since criterion 3 forbids anything but the 21 proposals in the drafting commit.
2. **Verbatim write vs deterministic re-dump** of the drafter's JSON (D-17 "unchanged" vs repo `sort_keys` convention). Recommendation: verbatim; validator does not require sorted keys.
3. **Catalog drift comparison target:** working-tree catalog vs the blob at the drafting commit. Recommendation: compare embedded values to the working catalog and also record/verify against the blob at the drafting commit.
4. **Where the D-25 SHA values come from** (user/STATE.md); the executor must fetch them when writing the term-scan test, without echoing them into scanned files.
5. **Brief location** (docs/ vs registry/): discretionary; recommend `docs/` with a name free of forbidden terms.

## Sources

### Primary (HIGH)
- `scripts/publish_archive_assessment_applicability_authority_v2.py`, `schemas/archive_assessment_applicability_authority_v2.schema.json`, `tests/test_archive_assessment_applicability_authority_v2.py` (read in this session)
- `.planning/phases/01-rule-shape-and-decision-states/01-FIELD-DEFINITIONS.md`, `02-CONTEXT.md`, `REQUIREMENTS.md`, `.planning/config.json`
- `registry/control_catalog.yaml` (field structure only), `.github/workflows/ems-validate.yml`, git state commands run locally

## Metadata

**Confidence:** stack HIGH, architecture HIGH, pitfalls HIGH (git/CRLF behaviour verified in config; blob-hash behaviour post-commit is A2).
**Research date:** 2026-10-13. **Valid until:** until the catalog or v2 publisher changes.
