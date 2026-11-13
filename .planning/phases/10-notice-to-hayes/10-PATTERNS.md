# Phase 10: Notice to Hayes - Pattern Map

**Mapped:** 2026-11-12
**Files analyzed:** 7 (4 new generated or code files, 1 new test, 1 modified CI file; the schema, JSON and Markdown are produced by the builder)
**Analogs found:** 7 / 7 (all exact or role-match; the reply set is a one-to-one template)

No RESEARCH.md. Source: 10-CONTEXT.md, CLAUDE.md, the reply builder and test, the v2 publisher, and read-only `git show` / `git ls-tree` at the three frozen commits.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` | builder + validator script | transform, file-I/O (frozen git reads, byte-rebuild) | `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` | exact |
| `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` | test | request-response (tamper, fail-closed fakes) | `tests/test_archive_assessment_demo3_w1_req_001_reply.py` | exact |
| `docs/DEMO3_W1_REQ_001_NOTICE_2_0_2.md` (generated) | document | transform output | `docs/DEMO3_W1_REQ_001_REPLY.md` | exact |
| `registry/archive_assessment_demo3_w1_req_001_notice_2_0_2.json` (generated) | registry JSON | transform output | `registry/archive_assessment_demo3_w1_req_001_reply.json` | exact |
| `schemas/archive_assessment_demo3_w1_req_001_notice_2_0_2.schema.json` (generated via `--emit-schema`) | schema | transform output | `schemas/archive_assessment_demo3_w1_req_001_reply.schema.json` | exact |
| `.github/workflows/ems-validate.yml` (modify, `archive-assessment` job) | config | CI | lines 90-96 of the same file | exact |
| "What changed" derivation (inside the builder) | utility | transform from frozen bytes | `dry_run_summary` / `closed_schema_levels` / `rows_differing_from_previous` in `scripts/publish_archive_assessment_applicability_authority_v2.py` | role-match (those use live code; D-05 says recompute from frozen bytes) |

## Frozen inputs: what actually exists (verified with git)

All three SHAs resolve to the full SHAs in CONTEXT D-04: `ae15c7458e49c8f55cc58c61bab04bc716aa9892` (publication), `a71257ed267410138a3c4daba412b00c116663d8` (record), `31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb` (2.0.1).

### Exact paths (same at `ae15c74` and `a71257e`)
All of these exist at both `ae15c74` and `a71257e`. Use the V2 constants, as the reply builder does: `V2.AUTHORITY`, `V2.SIGNOFF`, `V2.PUBLICATION_RECORD`, `V2.SCHEMA`, `V2.OUT`, `V2.N_MANIFEST`, `V2.GOVERNANCE_DECISIONS`.

| Input | Path |
|---|---|
| 2.0.2 authority | `registry/archive_assessment_applicability_authority_v2.json` (at `ae15c74`) |
| 2.0.1 authority | the same path at `31addfa` |
| manifest | `generated/archive-assessment/ems-aa3-v2/ems_aa3_v2_archive_applicability_authority_publication_manifest.json` (9 artifacts; it does not list itself) |
| sign-off | `registry/archive_assessment_applicability_authority_v2_signoff.json` |
| negative-invariant validation | `generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_negative_invariant_validation.json` |
| authority schema | `schemas/archive_assessment_applicability_authority_v2.schema.json` |
| publication record | `registry/archive_assessment_applicability_authority_v2_publication_record.json` |
| decision traceability | `generated/archive-assessment/ems-aa3-v2/archive_assessment_applicability_authority_v2_decision_traceability.json` |
| certification | `generated/archive-assessment/ems-aa3-v2/EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION.json` |
| governance decisions | `registry/archive_assessment_governance_decisions.json` |

### The publication record: read it at `a71257e`, not `ae15c74`
- At `ae15c74` the record file still holds the old 2.0.1 values (`authority_id ...-2.0.1`, `publication_commit` `31addfa...`, `manifest_sha256` `c8a3ca0c...`). It was written in `ae15c74` before the new publication commit existed.
- At `a71257e` (commit "feat(09-05): record 2.0.2 publication commit") only that one file changed against `ae15c74`, apart from `.planning` files. It now reads:
```json
{ "authority_id": "EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2",
  "authority_sha256": "a44eea1f98ec361ab100c554eb3a8d3529cfeb1fec78ec6d38193a675f0b8beb",
  "digest_normalisation": "CRLF_TO_LF",
  "manifest_sha256": "9991228ab7ff0a0c52c61b77a4d4c0e58b56d68b0c382caa83496621f092bac2",
  "publication_commit": "ae15c7458e49c8f55cc58c61bab04bc716aa9892",
  "version": "2.0.2" }
```
- `publication_commit` lives in the publication record only. It is not in the sign-off or the manifest. This is the WR-01 binding: assert `record['publication_commit'] == NOTICE_PUBLICATION_COMMIT` after reading the record at `NOTICE_RECORD_COMMIT`.
- Test hook for the "record commit changes no authority bytes" claim: `git diff --name-status ae15c74 a71257e` shows only `.planning/*` and the record file.

### `source_lineage` shape, 2.0.1 versus 2.0.2
2.0.1 at `31addfa` has a global claim and bare digests:
```
source_lineage = {
  aa1_manifest_sha256, aa2_closure_sha256, aa2_approval_sha256   # bare strings
  digest_normalisation: "CRLF_TO_LF"                             # one global claim
  catalog_reference{relative_path, required_for_deterministic_compilation, sha256}
  governance_decisions{drafting_commit, record_count, relative_path, sha256}
  supersedes{authority_id 2.0.0, commit 54a7fd0..., governance_decisions_sha256, relative_path, sha256, version}
  v1_baseline{authority_id, commit, relative_path, sha256, version} }
```
2.0.2 at `ae15c74` uses one object per input, each carrying its own `normalisation` (and `commit` where pinned):

| Key | normalisation | Other fields |
|---|---|---|
| `aa1_manifest` | `RAW_BYTES` | `relative_path` `generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json`, `sha256` `f0da8e2e...` |
| `aa2_approval` | `RAW_BYTES` | `generated/archive-assessment/ems-aa2/approval/archive_assessment_applicability_governance_approval.json`, `de170ebc...` |
| `aa2_closure` | `RAW_BYTES` | `generated/archive-assessment/ems-aa2/approval/archive_assessment_applicability_governance_closure.json`, `ed589d76...` |
| `catalog_reference` | `CRLF_TO_LF` | `commit` `62a8955d...`, `required_for_deterministic_compilation: false`, `sha256` `12bb1a9d...` |
| `governance_decisions` | `CRLF_TO_LF` | `drafting_commit` `dc3b41c9...`, `record_count` 21, `sha256` `4e746d1f...` |
| `supersedes` | `CRLF_TO_LF` | `authority_id ...-2.0.1`, `commit` `31addfa...`, `governance_decisions_*` (path, sha, normalisation), `sha256` `7be5eb88...`, `version` 2.0.1 |
| `v1_baseline` | `CRLF_TO_LF` | `commit` `62a8955d...`, `sha256` `f084607c...` |

- The 2.0.1 authority's old global claim is `source_lineage.digest_normalisation == "CRLF_TO_LF"`; 2.0.2 has no such key.
- D-06 digests: `aa1_manifest_sha256`, `aa2_closure_sha256`, `aa2_approval_sha256` in 2.0.1 map to `aa1_manifest`, `aa2_closure`, `aa2_approval` in 2.0.2. The digest values are identical in both versions (`f0da8e2e...`, `ed589d76...`, `de170ebc...`). Only the declared scope changed, from `CRLF_TO_LF` to `RAW_BYTES`. The notice should say "declared scope" and should not claim any digest value changed.
- The derivation for `--validate` is: load both authorities with `pinned_json`, then compare `old['source_lineage']['digest_normalisation']` and the three bare `*_sha256` keys with the three new objects. The value of `new[k]['normalisation'] == 'RAW_BYTES'` identifies the wrongly scoped digests.
- The 2.0.2 `supersedes.normalisation` and `governance_decisions_normalisation` are `CRLF_TO_LF` (the reply builder uses `sup['governance_decisions_sha256']`; the 2.0.2 `supersedes` also has `governance_decisions_relative_path`).

### Mutation count and closed schema levels
- Mutation count: `negative_invariant_tests` list in the negative-invariant validation file at `ae15c74`. Length is **29**. The file's other keys are `published_on` (`2026-11-12`) and `result` (`PASS`). Each entry has `description`, `id`, `mutation`, `rejected_by`, `result` (`REJECTED_FAIL_CLOSED`). `NEGATIVE_MUTATIONS` in the publisher is the live source, so do not import it for the notice.
- The certification file only holds `negative_invariants: "PASS"`; it has no count.
- Closed schema levels: recompute from the frozen schema at `ae15c74` with the same traversal as `V2.closed_schema_levels` (copy the algorithm; the publisher function is live code but is pure on its argument, so calling `V2.closed_schema_levels(frozen_schema)` is also safe as it does not read the file). **16 levels** at `ae15c74`: `$`; `controls.items`; the `allOf[0].then` rule and its `conditions.items`; the `anyOf[0]` rule and its `conditions.items`; `not_applicable_semantics` and its `field_definitions`; `source_lineage`; and the 7 lineage children (`aa1_manifest`, `aa2_approval`, `aa2_closure`, `catalog_reference`, `governance_decisions`, `supersedes`, `v1_baseline`). Take the count and the path list from the code run, not from this prose.
- Row comparison 2.0.1 to 2.0.2: all 80 rows identical on `not_applicable_decision_state`, `not_applicable_rule`, `not_applicable_authority`, `decision_ids`, and `applicability_decision_ids` equal (verified: 0 differing of 80). Compute from the two frozen authorities with the keys in `V2.PREV_COMPARED_KEYS` (publisher line 281). The live `rows_differing_from_previous` calls `git_show` on `SUPERSEDED_V2_0_1`, which is a constant, so only the 2.0.2 side must be passed as the frozen object; the cleaner choice is a local function over two frozen dicts.
- Sign-off: `approval` {`approver` Oscar Mack, `date` 2026-11-12, `role` EMS_GOVERNANCE_AUTHORITY, `scope`}, `dual_role_statement`, `authority_sha256`, `status` `PUBLICATION_SIGNOFF`, `version`. Manifest holds `published_on` `2026-11-12`.
- Counts from certification: `control_population` 80, `decided_control_count` 21, `undecided_control_count` 59, `semantic_conflicts` 0.

## Pattern Assignments

### `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` (builder, transform + file-I/O)

**Analog:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` (341 lines).

**Imports and V2 load** (lines 1-17). Copy verbatim, changing the module name only:
```python
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re, subprocess, sys
from pathlib import Path
import jsonschema
ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V2)
```
Style: single quotes, compact helpers, `from __future__` header, one `import` per group as in the analog.

**Constants** (lines 19-35). Replace `REPLY_*` with `NOTICE_JSON`, `NOTICE_MD`, `NOTICE_SCHEMA`, `NOTICE_PUBLICATION_COMMIT`, `NOTICE_RECORD_COMMIT`, plus a `SUPERSEDED_COMMIT = '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb'`, `DOCUMENT_ID`, `SCRIPT_REL`, `REMOTE_BRANCH`, `NOTICE_DATE`, a `NOTICE_KEYS` list (the required keys), `PIN_KEYS`, `DIGEST_RE`, and `FORBIDDEN_WORDS = ('best', 'critical', 'important', 'recommended', 'highest')` (D-05: plain wording; the reply declares this tuple at line 35, and it is worth enforcing in the notice).

**Frozen reads** (lines 38-47). Copy as is:
```python
def pinned_bytes(commit: str, path: Path) -> bytes: return V2.git_show(commit, V2.rel(path))
def pinned_json(commit, path): return json.loads(pinned_bytes(commit, path).decode('utf-8'))
def pinned_digest(commit, path): return hashlib.sha256(V2.lf_bytes(pinned_bytes(commit, path))).hexdigest()
```
Note: `V2.git_show` validates a 40-hex SHA and a repo-relative path and raises `GitHistoryError` (subclass of `AuthorityError`) on failure. For RAW_BYTES digests of AA1 inputs the notice must not use `pinned_digest` (it LF-normalises); use `hashlib.sha256(pinned_bytes(...))`. The notice itself only needs the declared values from the authority, but if it verifies that `aa1_manifest.sha256` matches git bytes it must use raw bytes.

**Record binding (WR-01)** (lines 248-257), adapted:
```python
def load_inputs() -> tuple:
    authority = pinned_json(NOTICE_PUBLICATION_COMMIT, V2.AUTHORITY)
    previous  = pinned_json(SUPERSEDED_COMMIT, V2.AUTHORITY)
    signoff, decisions = pinned_json(NOTICE_PUBLICATION_COMMIT, V2.SIGNOFF), pinned_json(NOTICE_PUBLICATION_COMMIT, V2.GOVERNANCE_DECISIONS)
    manifest = pinned_json(NOTICE_PUBLICATION_COMMIT, V2.OUT / V2.N_MANIFEST)
    record = pinned_json(NOTICE_RECORD_COMMIT, V2.PUBLICATION_RECORD)
    if record.get('publication_commit') != NOTICE_PUBLICATION_COMMIT:
        raise V2.AuthorityError('NOTICE_PUBLICATION_COMMIT differs from the publication_commit named by the frozen publication record')
    ...
```
Also add the schema read (`pinned_json(NOTICE_PUBLICATION_COMMIT, V2.SCHEMA)`) and the negative-invariant read (`V2.OUT / 'archive_assessment_applicability_authority_v2_negative_invariant_validation.json'`; no `V2.N_*` constant for this file was verified, so check with `grep -n "N_NEG\|negative_invariant" scripts/publish_archive_assessment_applicability_authority_v2.py` before choosing between a V2 constant and a local string).

**Binding of inputs to the manifest** (lines 235-245, `check_inputs_bound`). Copy the structure. The manifest's `artifacts` is a list of `{relative_path, sha256}`; every frozen input the notice reads (sign-off, schema, authority, negative-invariant output, traceability) should be checked against it with `pinned_digest`. The sign-off and traceability checks are already in the analog; the additional ones are one extra `man.get(rel) != pinned_digest(...)` line each.

**Sign-off and authority checks** (lines 88-91):
```python
V2.validate_signoff(signoff, record['authority_sha256'], authority_id=record['authority_id'], version=record['version'])
if record['authority_id'] != authority['authority_id'] or record['version'] != authority['version']:
    raise V2.AuthorityError('publication record does not match the authority')
```
`validate_signoff(record, authority_lf_digest, authority_id=None, version=None)` is in the publisher at line 530.

**Record-commit resolution** (lines 279-295). Copy `git()` and `resolve_record_commit()` unchanged apart from the constant name. It does, in order: `rev-parse --is-shallow-repository` (fail closed unless the output is `false`), a 40-hex check plus `cat-file -e <sha>^{commit}`, then `merge-base --is-ancestor <sha> HEAD`. The notice should also run the cat-file and ancestor checks for `NOTICE_PUBLICATION_COMMIT` and `SUPERSEDED_COMMIT` (the reply checks only the record commit). Also assert `NOTICE_PUBLICATION_COMMIT` is an ancestor of `NOTICE_RECORD_COMMIT`, as the reply test does at test lines 346-357.

**Decision content** (reply lines 57-87 for decided/undecided split). Reuse: decided rows are those with `not_applicable_decision_state != 'NOT_YET_DECIDED'`; check `sorted(ids) == sorted(V2.REQUEST_CONTROL_IDS)`; counts 21 / 3 / 18 / 59; rules in machine form through `V2.rule_text(rule)` (publisher line 552). The notice does not repeat the 18 reasons (D-08), so `first_sentence` is not needed.

**Decisions unchanged check** (reply lines 93-95):
```python
decisions_sha = pinned_digest(NOTICE_PUBLICATION_COMMIT, V2.GOVERNANCE_DECISIONS)
if decisions_sha != sup['governance_decisions_sha256']:
    raise V2.AuthorityError('governance decisions differ from the superseded version, so no-decision-changed cannot be stated')
```
Expected value `4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f`. Also compare it with the same digest taken at `SUPERSEDED_COMMIT` and with the 2.0.1 authority's `source_lineage.governance_decisions.sha256`.

**Dual role** (reply line 103 and line 231-232): the reply copies `signoff['dual_role_statement']` and `validate_reply_object` checks it equals `V2.DUAL_ROLE_STATEMENT` (publisher line 451). Do the same. The date: the reply used `appr['date']`; the notice uses the `NOTICE_DATE` constant (D-11) and cites `appr['date']` separately as the publication date.

**Markdown render** (lines 129-195). Copy the structure: a `L: list[str]` accumulator, `'\n'.join(L)`, the check `if '\r' in text: raise`, and the first line as `# ...` followed by the generated, read-only line:
```python
L += [f"# Reply to {...}", '', f"This file is generated by {SCRIPT_REL} from the published authority and is read-only. Rebuild it with that script; do not edit it by hand.", '']
```
Section names to reuse from the reply (`## Opening`, `## The pin`, `## What publication does not change`, `## History`, `## Sending`), and the Opening paragraph "It is written as from {approver}, acting as the EMS governance authority, and dated {date}. It stays unsigned in the repository until it is sent." followed by `Dual role: {statement}`. Suggested new sections: `## What to do` (re-pin to `ae15c74` instead of `31addfa`, plus the two other Hayes-side steps; D-09), `## What changed`, `## The 2.0.1 digest-scope error`, `## No decision changed`, `## Sending`. Hayes-side items to restate are the two from reply lines 117-121: "The target description must carry the eight classification facts." and "Hayes must read the published v2 shape.", plus a re-pin item.

**Schema** (lines 198-221). Same pattern: nested dict, `additionalProperties: False` at every object, `required: list(KEYS)`, `{'const': ...}` for the cited id, version, publication commit (ROADMAP SC1) and `pattern '^[0-9a-f]{40}$'` for SHAs. Use the same `s`, `sha` shorthand variables.

**Byte-rebuild validation** (lines 260-276). Copy the shape:
```python
def validate_notice() -> None:
    for p in (NOTICE_JSON, NOTICE_MD, NOTICE_SCHEMA):
        if not p.exists(): raise V2.AuthorityError(f'{V2.rel(p)}: not generated')
    ...
    if V2.lf_bytes(NOTICE_JSON.read_bytes()) != V2.jtext(notice).encode('utf-8'): raise V2.AuthorityError('notice JSON differs from a fresh build')
    if V2.lf_bytes(NOTICE_MD.read_bytes()) != render_markdown(notice).encode('utf-8'): raise V2.AuthorityError('notice Markdown differs from a fresh build')
    if V2.lf_bytes(NOTICE_SCHEMA.read_bytes()) != V2.jtext(schema()).encode('utf-8'): raise V2.AuthorityError('notice schema differs from a fresh build')
    validate_notice_object(V2.load(NOTICE_JSON))
    jsonschema.Draft202012Validator(V2.load(NOTICE_SCHEMA)).validate(V2.load(NOTICE_JSON))
    print('PASS')
```
Error-message strings are matched by tests (`match='reply JSON differs from a fresh build'`), so keep the `... differs from a fresh build` suffix pattern.

**CLI** (lines 327-341). Keep the mutually exclusive group `--build`, `--validate`, `--emit-schema`. Do not copy `--push-check` unless wanted: the D-13 push checkpoint is manual. If it is added, `push_check()` (lines 298-324) is a drop-in with `NOTICE_PUBLICATION_COMMIT` replaced by the notice's own commit, which cannot be known at build time, so omission is simpler. Final lines: `if __name__ == '__main__': main()`; `V2.dump` and `V2.write_text` do the output (publisher lines 83 and 520).

**Anti-patterns to avoid (from review lessons):**
- Do not call `V2.lf_digest(...)`, `V2.dry_run_summary(...)`, `V2.NEGATIVE_MUTATIONS`, `V2.VERSION` or any other live-file or live-constant reader in the notice build. The reply test `test_validate_independent_of_live_version` (test line 423) monkeypatches `V2.lf_digest` to raise and `V2.VERSION` to `9.9.9`, then expects `validate_reply()` to pass. Mirror it for the notice. Use `V2.git_show`, `V2.lf_bytes`, `V2.jtext`, `V2.rel`, `V2.rule_text`, `V2.AuthorityError` only (pure helpers). Note `V2.REQUEST_CONTROL_IDS`, `V2.DUAL_ROLE_STATEMENT` and `V2.APPROVER_ROLES` are constants and are permitted (the reply uses them).
- Do not hand-write the "what changed" bullets. Derive each line from the frozen objects (D-05).

### `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py` (test)

**Analog:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py` (545 lines).

**Module load and helpers** (lines 1-64). Copy: importlib load of the builder script as a module named e.g. `aa_notice_demo3`, `V2 = MODULE.V2`, `REJECTS = (AuthorityError, jsonschema.ValidationError)`, a module-level `tempfile.TemporaryDirectory()` named `_TMP` (comment says `tmp_path` is unusable on this Windows machine; keep that), plus these helpers:
```python
def serve_edited(monkeypatch, path, obj):
    rel_path, real = V2.rel(path), V2.git_show
    data = V2.jtext(obj).encode('utf-8')
    monkeypatch.setattr(V2, 'git_show', lambda commit, relative_path: data if relative_path == rel_path else real(commit, relative_path))
```
Also `run_validate_notice(notice, monkeypatch)` (write temp JSON and MD, monkeypatch `NOTICE_JSON` and `NOTICE_MD`, call `validate_notice()`) and `assert_validate_rejects`.

**Tests to port** (names from the reply test), adapted for the notice:
- `test_validate_*_accepts_unmutated...` (line 66), `rejects_loosened_schema_file` (line 70, sets `additionalProperties = True`, expects `match='... schema differs'`), `rejects_edited_signoff` (line 95), `rejects_tampered_*_bytes` parametrised over json and md (lines 432-440).
- Tamper constants (lines 443-458): parametrise `NOTICE_PUBLICATION_COMMIT` with `'d' * 40`, `31addfa...`, `4d9b7c1...`, `b3c04114...`, and `NOTICE_RECORD_COMMIT` with `'d' * 40` and `ae15c74...`. Also tamper the cited id, version, authority sha and manifest sha in the written notice JSON (ROADMAP SC1: changing the id, version or commit must make `--validate` fail). These tamper cases run the real `validate_*` and rely on `git_ready()` skips (lines 319-328); the analog's skip-if-shallow pattern is acceptable for those only.
- Fail-closed without skipping (WR-04 lesson, CONTEXT "Established Patterns"): port `fake_shallow_git` (line 360) and `test_resolve_record_commit_fails_when_shallow_or_unknown` (385), `..._full_clone_passes_through` (393), `..._missing_or_not_ancestor` (400), `test_validate_fails_closed_without_history_shallow` (407) and `..._git_show` (413). These use monkeypatching of `MODULE.git` and `V2.git_show` and do not skip.
- `test_validate_independent_of_live_version` (423): monkeypatch `V2.lf_digest` to raise and `V2.VERSION` to `9.9.9`; `MODULE.validate_notice()` must pass.
- `test_frozen_constants_match_git` (346-357): `git rev-parse ae15c74`, `a71257e`, `31addfa` equal the three constants; `diff-tree --no-commit-id --name-only -r NOTICE_RECORD_COMMIT` for the record commit lists the record file among its changes (at `a71257e` it also lists `.planning/*` files, unlike `4d9b7c1`, so filter to non-`.planning` paths and assert the result is `[V2.rel(V2.PUBLICATION_RECORD)]`); `merge-base --is-ancestor` publication vs record.
- `test_built_*_counts`, `test_the_three_rules` (125-128, expects CTRL-030 and CTRL-039 `production = KNOWN_FALSE` and CTRL-052 `ai_enabled = KNOWN_FALSE`), `test_markdown_content` (232), `test_cli_flags_mutually_exclusive` (540).
- New derived-content tests: digests named in the digest-scope section equal exactly `{aa1_manifest, aa2_closure, aa2_approval}` and are computed from the two frozen authorities; fail when `31addfa` is served with an edited `digest_normalisation` or a changed bare digest (use `serve_edited` on the previous authority, keyed by path, but note both authorities share the same relative path, so the `serve_edited` lambda must also branch on `commit`); mutation count 29 equals `len(negative_invariant_tests)` of the served frozen file; 80 identical rows.
- Forbidden words: assert no word of `FORBIDDEN_WORDS` appears in the rendered text.

### `docs/DEMO3_W1_REQ_001_NOTICE_2_0_2.md` (generated)

**Analog:** `docs/DEMO3_W1_REQ_001_REPLY.md`, rendered by the builder, never hand-edited (D-12). Section outline in the reply: `## Opening` (line 5), `## Decisions per control` (13), `## What the rules mean` (60), `## The pin` (70), `## The published shape` (82), `## The other controls` (144), `## What publication does not change` (148), `## History` (160), `## Sending` (171). Tone: first-person-free third-person plain statements, "Cite this commit: <sha>", bullet lines `- Authority id: ...`, `- Authority sha256: ...`, `- Publication manifest sha256: ...`. The pin sentence about the record commit (reply `render_markdown` line 163) becomes: "The commit a71257e records the publication commit in a publication record and changes no authority bytes." The send condition (reply line 125) becomes a statement that the notice must not be sent until its own commit is on `feature/ems-aa3-archive-applicability-authority` on the remote (D-13).

### Generated JSON and schema

**Analogs:** `registry/archive_assessment_demo3_w1_req_001_reply.json` and its schema. Key set style: `REPLY_KEYS` list with `document_id`, `request_id`, `request_label`, `reply_date`, `from_authority`, `dual_role_statement`, `pin`, ... `send_condition`. Notice keys suggested: `document_id`, `request_id`, `request_label`, `notice_date`, `from_authority`, `dual_role_statement`, `pin` (same `PIN_KEYS` including `publication_commit`, `authority_id`, `version`, `authority_sha256`, `manifest_sha256`, `digest_normalisation`, `publication_record_commit`; plus `published_on`), `supersedes`, `what_changed` (lineage list, `negative_mutation_count`, `closed_schema_levels`, `row_comparison`, `gate_fix_line`), `digest_scope_error`, `decisions` (counts, `rules`, `governance_decisions_sha256`), `hayes_side_changes_needed`, `send_condition`. The `digest_normalisation` const `CRLF_TO_LF` in the reply's pin schema (line 214) still applies for the two published digests. Output uses `V2.jtext` (`json.dumps(value, indent=2, sort_keys=True) + '\n'`).

### `.github/workflows/ems-validate.yml` (modify)

**Analog:** the existing validators block, lines 90-96. Append one line after line 96, same indentation (10 spaces), as a separate code commit:
```yaml
      - name: Archive-assessment validators
        run: |
          python scripts/publish_archive_assessment_applicability_authority_v2.py --validate
          ...
          python scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate
          python scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py --validate
```
The job already uses `fetch-depth: 0` (line 75), which the shallow check needs. Tests are picked up by `pytest tests -k archive_assessment` (line 88), so the test file name must contain `archive_assessment`, which it does.

## Shared Patterns

### Frozen input discipline
**Source:** reply builder lines 38-47 and 248-257. **Apply to:** the notice builder and its tests. Every cited value is read through `V2.git_show(<40-hex commit>, <repo-relative path>)`. Never read the live working tree (live `registry/`, `generated/`, `schemas/` files are untouched by this phase).

### Fail closed
**Source:** `V2.AuthorityError`, `V2.GitHistoryError` (publisher lines 66-67), reply `resolve_record_commit` lines 283-295. **Apply to:** every check. Raise rather than return a status; a CLI failure is an uncaught exception, success prints `PASS`.

### Deterministic output
**Source:** `V2.jtext` (line 517), `V2.lf_bytes` (line 70), `V2.rel` (line 519), `V2.dump` (83), `V2.write_text` (520). **Apply to:** JSON, Markdown and schema writers and the byte comparison. Paths in registry JSON are repo-relative with forward slashes; `V2.contains_absolute` must be false on the notice object (reply line 226).

### Digest scope
**Source:** `V2.lf_bytes`, `hashlib.sha256`. **Apply to:** anything the notice recomputes. `CRLF_TO_LF` digests use `pinned_digest`; the three AA1/AA2 inputs are `RAW_BYTES` (hash the raw `git show` bytes). The two published pin digests (authority `a44eea1f...`, manifest `9991228a...`) are LF digests.

### Working-tree and scope guardrails (from CONTEXT carried-forward and CLAUDE.md)
Stage by explicit path only. Never stage `.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json`, `.pytest-*` directories or the untracked `docs/*` and `registry/*` files shown in git status. No edits to the publisher, authority, publication files or reply artifacts; verify with `git diff` against `ae15c74`/`a71257e` for the publication paths and `e781f08` for the reply. Subagents do not run pytest; the orchestrator runs it from PowerShell with `--basetemp`.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| (none) | | | Every new file has a one-to-one reply counterpart. The only new logic with no ready function is the derivation from frozen bytes: the digest-scope diff of the 2.0.1 and 2.0.2 `source_lineage`, the count of `negative_invariant_tests` in the frozen output, and the closed-levels count over the frozen schema. Use `V2.closed_schema_levels` (pure over its argument) and a local two-dict row comparison. |

## Metadata

**Analog search scope:** `scripts/`, `tests/`, `docs/`, `registry/`, `schemas/`, `.github/workflows/`, and git trees at `ae15c74`, `a71257e`, `31addfa`.
**Files read:** reply builder (full), reply test (lines 1-150, 314-460 and a function index), reply doc (head and section index), publisher (lines 30-69, 280-297, 355-374, 550-580), CI workflow (lines 68-96), seven frozen JSON files via `git show`.
**Pattern extraction date:** 2026-11-12
