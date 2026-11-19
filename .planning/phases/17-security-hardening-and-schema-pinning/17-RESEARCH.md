# Phase 17: Security Hardening and Schema Pinning - Research

**Researched:** 2026-11-18
**Domain:** Python governance publisher, git seam, JSON-schema pinning, CI (stdlib + jsonschema 4.26.0 + pytest; no new packages)
**Confidence:** HIGH (all findings come from reading the actual scripts and tests, plus two small experiments in a scratch repo)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
D-01 Final 2.0.4 form: `VERSION='2.0.4'`; `SUPERSEDED_V2_0_3` replaces `SUPERSEDED_V2_0_2` (authority id, version 2.0.3, commit `1544dc19ba235d732c832d1651895550ed5a265d`, 2.0.3 authority LF sha256 `696116e7...`, decisions LF sha256 `4e746d1f...`); values from files/git, never hand-typed; every dependent use moves with it (validators, schema, mutations, row comparison, dry-run summary, at-pin supersedes binding).
D-02 Red-window ledger `17-BASELINE-RED.md` (format of `12-BASELINE-RED.md`); each publisher-touching commit lists its red set; red set may only shrink or stay as listed; D-10 baseline test (`tests/test_archive_assessment_lineage_validation.py`) joins at first publisher edit, not weakened.
D-03 DEFERRED-17 publisher fixes, each with a test: IN-01 ("working tree" in place of "committed"); IN-02 ("the record still names the superseded X publication (HEAD is the publication commit or earlier)"); IN-03 (at-pin, record already names this publication: "the record already names this publication; run plain --validate here"); IN-04 (`git_not_shallow()` at top of `validate_published`, both modes); IN-06 (`lf_digest(SCRIPT)` check moves to just after the manifest load).
D-04 12 IN-05 and 12 IN-06 (decisions-builder scope) verified closed by SEC-04 / SEC-02; cross-check against `16-REVIEW-CLOSURE.md`.
D-05 SEC-01: `load_pinned_publisher` in the 2.0.3 notice builder compares pinned publisher blob LF sha256 to the pinned manifest `publisher_script.sha256` BEFORE `exec_module`/`decisions_builder()`; test proves publisher did not run; fail-closed `AuthorityError`; behaviour-only (byte-identical output); Phase 19 copies the order.
D-06 SEC-02 for 2.0.4: manifest gains `decisions_builder_script {relative_path, sha256, sha256_normalisation:'CRLF_TO_LF'}` sibling of `publisher_script` plus note; `--validate` checks live builder LF digest in both modes, plain mode also at the publication commit; check runs BEFORE `decisions_builder()` imports/executes; manifest schema/validation updated, missing/invalid entry fails closed.
D-07 SEC-02 for the 2.0.3 notice builder: frozen constant = LF sha256 of `scripts/build_archive_assessment_governance_decisions.py` at `1544dc1`, computed from git; checked before pinned builder executes; behaviour-only; closure notes it is not a manifest digest.
D-08 SEC-04 scope: publisher `git_show`/`git_run`; 2.0.3 notice builder own git calls + `live_git_subprocess`; `tests/aa_history.py`. Frozen reply (2.0.1) and 2.0.2 notice builders untouched (ledger: CLOSED (frozen)).
D-09 Isolation: `env=` from `os.environ` with EVERY `GIT_*` dropped, then `GIT_NO_REPLACE_OBJECTS=1`, `GIT_LITERAL_PATHSPECS=1`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL` = empty file / null device; needed settings passed explicitly (e.g. `core.longpaths=true`); hostile-env test (GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, refs/replace or GIT_REPLACE_REF_BASE).
D-10 One copy of the sanitized-env builder per script (no shared module); a test asserts the copies yield the same variable policy.
D-11 2.0.4 sign-off `scope` is free text with no digests: `validate_signoff` rejects any run of 7-64 hex chars; scope must contain `AUTHORITY_ID` and `VERSION`; digests live only in checked fields.
D-12 Rule applies from 2.0.4 forward only; 2.0.2/2.0.3 sign-offs immutable and validate under their own rules via pinned/frozen publishers.
D-13 Pin with `const`: `supersedes.sha256`, `supersedes.governance_decisions_sha256`, `v1_baseline.sha256`, `governance_decisions.sha256` (`4e746d1f...`); `aa1_manifest`, `aa2_closure`, `aa2_approval`, `catalog_reference` digests stay pattern-checked and validator-recomputed; a schema mutation per newly pinned field.
D-14 `schema()` emits const values from constants; a test recomputes each from the git blob at its commit and asserts equality.

### Claude's Discretion
SEC-03 mechanics (drop `--exclude='*.md'`; check no .md trips the pattern; any narrow exclusion justified and listed); whether `git_show` switches to `git cat-file blob` (keep Phase 15 `--` and long-path behaviour); hostile-env test mechanics and the empty-config-file approach on Windows vs Linux CI; test names; commit grouping/order (preferred: green-safe commits first - SEC-03, 2.0.3 builder behaviour-only fixes, `aa_history.py` - then the publisher edits that open the red window; each commit stages explicit paths and lists its red set).

### Deferred Ideas (OUT OF SCOPE)
Phase 18: 2.0.4 publication, sign-off, closing the red window. Phase 19: 2.0.4 notice builder (copies SEC-01 order and SEC-04 isolation; adds 15 IN-01). Frozen: SEC-04 for the reply (2.0.1) and 2.0.2 notice builders. No decision/row/sign-off/publication change in this phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SEC-01 | Pinned publisher digest checked before exec | Notice builder `load_pinned_publisher` L281-297 execs at L289 and checks at L322-324 (post-exec). Reorder; see Pattern 1 and test-signature impact. |
| SEC-02 | Decisions-builder blob has a manifest digest checked by `--validate` | Publisher `decisions_builder()` L701 execs the live builder; `validate_published` L798 calls it BEFORE the manifest is loaded (L810). Reorder plus new manifest entry (Pattern 2); 2.0.3 frozen constant 8ccd93c3... (verified from git). |
| SEC-03 | CI secret scan covers `*.md` | Remove `--exclude='*.md'` at ems-validate.yml L65. Verified zero `.md` hits in the working tree and in tracked files. |
| SEC-04 | Git seam isolated from caller env; literal pathspecs | Pattern 3; experiment-verified. |
| GATE-11 | Schema pins superseded digests | `pinned()` in `schema()` L468-472 exempts `sha_keys`; remove exemption (Pattern 4). |
| GATE-12 | Sign-off scope carries no unchecked digest | `validate_signoff` L607-627 (Pattern 5). |
</phase_requirements>

## Summary

All six requirements plus the DEFERRED-17 items are edits to three scripts (`scripts/publish_archive_assessment_applicability_authority_v2.py` "publisher", `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` "notice builder", `tests/aa_history.py`), one workflow, and tests. No new packages. The publisher currently is the 2.0.3 final form (VERSION L34). The only "scary" interaction is the unusually strong source-introspection tests in the publisher test file (see Pitfalls 1-3), which dictate where `subprocess` and `os` may appear and which argv shapes `git_show` must produce.

The two risks CONTEXT flagged were checked. (a) Git for Windows' system `core.autocrlf=true` disappearing under `GIT_CONFIG_NOSYSTEM` is NOT a problem here: this repo also sets `core.autocrlf=true` in `.git/config` (local scope survives the isolation), every publication file has `text eol=lf` in `.gitattributes`, and `git status --porcelain` on the publication paths returned empty under `GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=NUL`. The publisher script and decisions builder are `i/lf w/crlf attr/` (no eol attribute) but are compared via Python `lf_bytes`, and `git_dirty` includes the script path only under at-pin on a clean tree; the test is "at-pin on the real tree" (see Open Question 1). (b) `GIT_CONFIG_GLOBAL=os.devnull` works on this machine (git 2.54.0.windows.1) and drops the global `safe.directory` entries/credential helper; hostile `GIT_DIR`/`GIT_WORK_TREE` made `git rev-parse HEAD` fail unsanitised and succeed sanitised in a scratch repo.

**Primary recommendation:** Add one `git_env()` helper per script (no `subprocess` word inside it; pass `core.longpaths=true` through `GIT_CONFIG_COUNT/KEY_0/VALUE_0` in the env rather than `-c` in argv, so every existing argv-shape test stays valid), reorder digest-before-exec in both the notice builder and `validate_published`, and sequence commits so the red window opens only at the first publisher edit.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Hash-before-exec of pinned code | Notice builder script (Python) | pytest | Check lives where the exec is |
| Decisions-builder manifest digest | Publisher script + manifest JSON (registry/generated output) | Phase 18 republication writes it | Certification pattern: digest recorded at publication, checked by `--validate` |
| Git env isolation | Each script's own seam (publisher, notice builder, test helper) | `live_git_subprocess` shim for pinned code | One copy per script (D-10) keeps certified publisher self-contained |
| Schema pins | `schema()` in publisher -> `schemas/archive_assessment_applicability_authority_v2.schema.json` | pytest equality test | Schema is emitted from code, committed, certified by hash |
| Sign-off scope rule | `validate_signoff` in publisher | Phase 18 runbook | Validator enforces; human types the text |
| Secret scan | GitHub Actions workflow | - | CI only |

## Standard Stack

No additions. Existing: Python 3.12, `jsonschema==4.26.0` (CI pin), pytest, PyYAML; git (local 2.54.0.windows.1; ubuntu-latest CI git is recent enough for `GIT_CONFIG_GLOBAL` (>= 2.32) and `GIT_CONFIG_COUNT` (>= 2.31)) [VERIFIED: local `git --version`; CI git version ASSUMED current ubuntu-latest, see A1].

**Package Legitimacy Audit:** no external packages are installed by this phase. slopcheck not applicable.

## Architecture Patterns

### Data flow (what each change touches)

```
caller env (may hold GIT_DIR/GIT_INDEX_FILE/replace refs)
   -> git_env()  [drop all GIT_*, set NO_REPLACE/LITERAL/NOSYSTEM/CONFIG_GLOBAL=devnull + CONFIG_COUNT longpaths]
   -> git_show / git_run  (publisher)           -> every validator read of pinned blobs, ancestry, shallow, status
   -> live_git_subprocess shim (notice builder) -> git calls made by PINNED publisher code
notice builder: git_show(pinned publisher blob) -> LF sha256 == manifest.publisher_script.sha256 ? -> only then exec_module
                git_show(pinned builder blob)   -> LF sha256 == FROZEN_BUILDER_SHA256 ?          -> only then pub.decisions_builder()
publisher --validate: shallow check -> (at-pin tree checks) -> load manifest -> lf_digest(SCRIPT)==publisher_script.sha256
                      -> lf_digest(BUILDER_SCRIPT)==decisions_builder_script.sha256 -> decisions_builder() import/exec -> rest
```

### Pattern 1: SEC-01 in the notice builder (D-05)
Current order inside `load_pinned_publisher(tmp)`: write pinned code and data to tmp -> `exec_module` (L289) -> `pub.decisions_builder()` (L290, execs pinned builder) -> ROOT containment -> swap `subprocess`. The digest check is later in `pinned_mutation_run` (L322-324), after exec. Fix:
- Change signature to `load_pinned_publisher(tmp, manifest)` (or pass expected digests), and after the materialisation loop but before `spec_from_file_location`/`exec_module`, compute `hashlib.sha256(lf_bytes((tmp/PINNED_CODE[0]).read_bytes()))` and compare with `manifest['publisher_script']['sha256']`; raise `AuthorityError('pinned publisher differs from the certified publisher_script digest')` (keep this exact message; `test_pinned_run_rejects_publisher_digest_mismatch` L195-200 matches it). Remove (or keep as redundant) the post-exec check at L322-324. Validate `manifest.get('publisher_script')` shape defensively first (a missing key currently raises KeyError wrapped by `_WRAPPED`; should become AuthorityError).
- D-07: before `pub.decisions_builder()`, compare LF sha256 of the materialised `tmp/PINNED_CODE[1]` with a new frozen constant `PINNED_DECISIONS_BUILDER_SHA256`. Value verified from git: `git cat-file blob 1544dc19...:scripts/build_archive_assessment_governance_decisions.py` LF-normalised = `8ccd93c3036a706b6b39ee50ca81ff8a29778bf1b98765f3c44e36d90251a153` [VERIFIED: computed in this session]. Add a test (like `test_frozen_constants_match_git`) that recomputes it from git.
- Test signatures: existing tests wrap `MODULE.load_pinned_publisher` with `def wrapper(tmp): real(tmp)` at test lines 148, 161, 175, 819-828. Adding a `manifest` parameter breaks those wrappers. Either update all four wrappers to `(tmp, *a)` in the same commit, or keep `load_pinned_publisher(tmp)` and read the expected digest from a module global set by `pinned_mutation_run` (worse). Recommend the explicit parameter and updating the wrappers.
- Sentinel test: monkeypatch `MODULE.git_show` to return, for `PINNED_CODE[0]`, real bytes + `\nopen(SENTINEL,'w').write('ran')` (or return different bytes whose top level writes a sentinel), then call `pinned_mutation_run`; assert `AuthorityError` and `not SENTINEL.exists()`. Add an exec spy as a second assertion by monkeypatching `importlib.util.spec_from_file_location` to record calls (assert not called). Separate pair for the builder constant (tampered builder blob + sentinel; assert publisher module may have loaded but builder did not run).
- Byte-identical gate (16 D-02): rebuild the 2.0.3 notice then `git diff --exit-code` on its JSON/MD/schema.

### Pattern 2: SEC-02 in the publisher (D-06)
- `build_all_outputs` (L658) already takes `script_sha256`; add `builder_sha256: str | None = None` and emit `'decisions_builder_script': {'relative_path': rel(BUILDER_SCRIPT), 'sha256': builder_sha256 or lf_digest(BUILDER_SCRIPT), 'sha256_normalisation': 'CRLF_TO_LF'}` plus `'decisions_builder_script_note'` next to `publisher_script_note` (L694). `BUILDER_SCRIPT` is at L699 (defined after `build_all_outputs`; fine at call time but `rel(BUILDER_SCRIPT)` needs ROOT-relative: it is `Path(__file__).resolve().parent/...`, same shape as `SCRIPT`).
- `validate_published` (L792-825) today: shallow (at-pin only) -> tree checks -> `validate_governance_decisions()` (L798, which runs `decisions_builder()` = exec of live builder) -> authority/schema/lineage -> signoff -> manifest load (L810) -> `ps` check (L812-814) -> `lf_digest(SCRIPT)` (L814). The builder executes BEFORE the manifest exists in memory, so D-06 requires reordering: move `validate_governance_decisions()` after the manifest/digest checks. This also satisfies IN-06 (script digest check "just after the manifest load"). Safe order: `git_not_shallow()` (IN-04) -> at-pin tree/dirty checks -> verify OUT dir and manifest exist -> `load_checked(manifest)` -> validate `publisher_script` and `decisions_builder_script` entry shape -> `lf_digest(SCRIPT)` and `lf_digest(BUILDER_SCRIPT)` against them -> `validate_governance_decisions()` -> remainder. Note the existing error text `publisher script differs from the certified manifest digest (manifest publisher_script.sha256); ...` must stay (tests match it; `test_publisher_still_valid_and_digest_matches_manifest` L977).
- Plain mode also checks the builder at the publication commit (`git_show(pub, rel(BUILDER_SCRIPT))` LF digest == manifest digest), next to L856. At-pin mode: the builder path should join `check_tree_matches_head([... , rel(BUILDER_SCRIPT)])` and the `git_dirty` list alongside `rel(SCRIPT)` (L795-796).
- The `publish()` path (L780) calls `published_authority_checked()` -> `validate_governance_decisions()` -> executes the builder before any manifest exists; there the digest recorded is simply the live one, so no check is possible/needed (same as the publisher self-digest). Mutation gate `DECISIONS` (L730) also calls `decisions_builder()`; no change.
- Make `decisions_builder()` check-capable: `decisions_builder(expected_sha256=None)` that, when given, compares `lf_digest(BUILDER_SCRIPT)` before `spec.loader.exec_module`. Because `_BUILDER` is cached, a test should reset `MODULE._BUILDER = None` via monkeypatch before tampering. The builder itself loads the publisher via `importlib` at import (builder L18-19 `V2`), so the publisher file is re-executed under the name `aa_applicability_publisher_v2` - already covered by the publisher's own digest.
- Manifest "schema": there is no JSON schema file for the publication manifest (only `wave2c1a_generation_manifest.schema.json` is unrelated). The "manifest schema and validation" in D-06 is the inline shape check at L812-813 (relative_path equals, sha is 64 hex, normalisation CRLF_TO_LF). Replicate for the builder entry via a small shared helper `check_script_entry(entry, path, label)` to avoid copy drift. Add a negative test for missing/invalid/wrong-path builder entry.
- Rename impact: `build_all_outputs` callers include tests; grep before change.

### Pattern 3: SEC-04 git seam (D-08..D-10)
Publisher `git_show` L367 and `git_run` L375 are the only `subprocess` calls (a test enforces it). Implement:

```python
def git_env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('GIT_')}
    env.update({'GIT_NO_REPLACE_OBJECTS': '1', 'GIT_LITERAL_PATHSPECS': '1', 'GIT_CONFIG_NOSYSTEM': '1',
                'GIT_CONFIG_GLOBAL': os.devnull,
                'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'core.longpaths', 'GIT_CONFIG_VALUE_0': 'true'})
    return env
```
and `subprocess.run([...], cwd=ROOT, capture_output=True, env=git_env())`. Experiment result (git 2.54.0.windows.1, scratch repo): hostile `GIT_DIR`/`GIT_WORK_TREE` made `git rev-parse HEAD` return rc 128; with this env it returned the intended HEAD; `git config --show-origin --list` showed only the local `.git/config` plus `command line: core.longpaths=true` [VERIFIED: local experiment]. Notes:
- Prefer `GIT_CONFIG_COUNT` over `-c` argv: existing tests assert exact argv (`test_git_show_argv_ends_with_double_dash` L1679-1688 asserts `[['git','show',f'{SHA40}:registry/a.json','--']]`; many `fake_git_run` tests inspect args). `-c` in argv would break them. CONTEXT D-09 says "explicitly on the command line (-c)"; env-based `GIT_CONFIG_COUNT` is an equivalent explicit setting that keeps argv stable - flag to the user/planner as a minor deviation, or update tests if `-c` is mandated.
- `GIT_CONFIG_GLOBAL=os.devnull` is `nul` on Windows, `/dev/null` on Linux; both accepted by git. No need to create an empty file.
- Keep `os` out of the `source_without_git_show()` banned list: that test bans only the substring `subprocess` (and `os.system`, `Popen`, `Evaluate-`). So `git_env` must not contain the word "subprocess" in code, comments or docstrings; and the publisher needs `import os` (not currently imported).
- `GIT_LITERAL_PATHSPECS=1` makes `--literal-pathspecs` redundant but keep the flag in `git_dirty`/`git_index_flags` (cheap, and tests inspect it).
- `git_show` vs `git cat-file blob`: `git_commit_blob` already uses cat-file. Keep `git show ... --` (Phase 15 long-path error text, argv test). Under `GIT_NO_REPLACE_OBJECTS` both read real objects. Recommend: keep `git show`.
- autocrlf: `git_dirty` compares working tree to index through clean filters. Under isolation only local config plus `.gitattributes` apply. Publication files all have `text eol=lf`; the repo also sets local `core.autocrlf=true`. On a fresh Windows clone the system/global autocrlf no longer applies but `eol=lf` makes the publication files normalised regardless [VERIFIED: `.gitattributes` L1-15 and `git ls-files --eol`: i/lf w/lf attr/text eol=lf]. The publisher script and decisions builder have no eol attribute (`i/lf w/crlf attr/`): on a fresh Windows clone with system autocrlf=true they are CRLF in the tree (clean filter normalises), but with autocrlf now unset by isolation `git status` would call a CRLF working-tree script modified. In this repo local autocrlf=true saves it; on a fresh clone it would not. Decision needed: add `text eol=lf` for `scripts/publish_archive_assessment_applicability_authority_v2.py` and `scripts/build_archive_assessment_governance_decisions.py` to `.gitattributes` (this changes working-tree bytes only; index unchanged; must be a deliberate commit) OR pass `core.autocrlf=true` via the same GIT_CONFIG_* env (risky on Linux: LF files stay LF, harmless). Recommend the `.gitattributes` fix or env autocrlf (see Open Question 1).
- `safe.directory`: lived in the global config; dropped under isolation. Same-owner checkouts (CI runner, normal operator) are unaffected; a differently owned checkout now fails closed with "detected dubious ownership" as a `GitHistoryError` - acceptable fail-closed behaviour; document it [ASSUMED for CI: actions/checkout writes safe.directory only for container jobs; ubuntu-latest owner matches].
- `LANG`/message language: the Phase 15 hint depends on English `Filename too long`; optionally set `LC_ALL=C` in `git_env` (non-GIT_ var). Optional.
- Notice builder: it has its own `git_show` (L120) and `git()` (L187, `text=True`) and `live_git_subprocess` (L300). Give it its own `git_env()` and pass `env=` in all three; in the shim set `kwargs['env'] = git_env()` (overriding any pinned-code env, same as `cwd`). Pinned publisher code calls `subprocess.run(['git', ...], cwd=ROOT, capture_output=True)` through the shim; its argv is `git show <c>:<p> --`, `--literal-pathspecs ...` etc. Existing test L189-192 calls `module.git_run('rev-parse','--show-toplevel')` through the shim and still must resolve to the live ROOT: fine with sanitized env.
- `tests/aa_history.py` L14-15: add `env=` using its own `git_env()` copy (D-10). `tests/` other files call `subprocess.run(['git', ...])` directly (publication test L227, L523, L718..., lineage test); those are test fixtures, out of D-08 scope.
- D-10 "copies produce the same variable policy" test: load the three modules (publisher via importlib as other tests do, notice builder, `aa_history` via normal import) and compare `git_env()` results under a controlled `monkeypatch.setenv` set (including a hostile GIT_* and `GIT_CONFIG_PARAMETERS`). Equality of dicts is the simplest assertion.
- Hostile-env test: build a scratch repo in `tmp_path` (not a clone of the real repo - local clones are unreliable here), with a tagged blob and a `git replace` for it; set `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_REPLACE_REF_BASE`/`GIT_CONFIG_PARAMETERS` in `monkeypatch.setenv` pointing at a decoy repo; monkeypatch `MODULE.ROOT` to the scratch repo; assert `git_head()`, `git_show()`, `git_not_shallow()`, `git_dirty()` read the scratch repo and the unreplaced blob. Also run the same through the notice builder `git_show` and `live_git_subprocess` shim. Make `GIT_NO_REPLACE_OBJECTS` effective check: create replace ref via `git replace <orig> <other>` and show `git show` returns original bytes through the seam but replacement bytes through a plain unsanitised call (proves the test is non-vacuous).

### Pattern 4: GATE-11 schema pins (D-13, D-14)
`schema()` L463-: `pinned(entry, sha_keys)` builds `const` for every key except `sha_keys`, which get a 64-hex pattern. Current uses:
- `supersedes: pinned(SUPERSEDED_V2_0_2, {'sha256','governance_decisions_sha256'})` -> pass an empty set so both become const (`SUPERSEDED_V2_0_3` values).
- `v1_baseline: pinned({... 'sha256': None ...}, {'sha256'})` -> needs a constant `V1_BASELINE_SHA256` (CRLF_TO_LF sha256 of `V1_BASELINE_REL` at `V1_BASELINE_COMMIT`); entry then has the real value and an empty sha_keys.
- `governance_decisions.sha256` currently `sha` pattern -> `{'const': GOVERNANCE_DECISIONS_SHA256}` where the constant equals `SUPERSEDED_V2_0_3['governance_decisions_sha256']` (`4e746d1f...`); reuse that single value rather than adding a second literal.
- Leave `catalog_reference`, `aa1_manifest`, `aa2_*` as pattern.
- Mutations (list around L560-590): add `Mutation('v1_baseline_digest_differs', ..., 'AUTHORITY', lambda a: a['source_lineage']['v1_baseline'].__setitem__('sha256','0'*64), True)`, `supersedes_digest_differs` (sha256), `governance_decisions_digest_differs`; `supersedes_governance_digest_differs` (L587) already exists but currently only has the Python validator reject it unless `schema_must_reject` is True - set the fifth arg `True` for all four so `run_mutations` asserts the schema itself rejects. The negative-invariant count (currently 29, asserted in tests such as L1349 and the notice test `== 29`) rises; update expectations: the 2.0.3 notice builder runs the PINNED publisher (its mutations stay 29) but the publisher tests count `len(NEGATIVE_MUTATIONS)`; grep `== 29`.
- The committed schema file `schemas/archive_assessment_applicability_authority_v2.schema.json` must be regenerated with `--emit-schema` at Phase 18 (certification hashes it); in Phase 17 `test_committed_schema_equals_schema_function` (applicability_authority_v2.py L212) goes red - this is the known red-set entry (12-07 had it too).
- Constants test (D-14): recompute via `git_show(commit, rel)` LF sha for supersedes authority + decisions at `SUPERSEDED_V2_0_3['commit']`, v1_baseline at `V1_BASELINE_COMMIT`, and assert equality; also assert `schema()` output const values equal them. The 2.0.3 authority LF digest equals the 2.0.3 sign-off `authority_sha256` `696116e7...` [VERIFIED: signoff JSON].

### Pattern 5: GATE-12 sign-off scope (D-11, D-12)
In `validate_signoff` (L607-627) after the non-empty check at L620-621, when the target version >= (2,0,4) (parse `want_version` with a strict `^[0-9]+\.[0-9]+\.[0-9]+$` regex; unparsable -> error):
- reject `re.search(r'[0-9a-fA-F]{7,}', scope)` (D-11 says 7-64; use `{7,}` so a 70-char run also fails). Digits-only runs of 7+ (e.g. `20261118`) also match; that is intended-stricter and should be stated in the Phase 18 runbook ("no date without hyphens, no long numbers").
- require `want_id in scope` and `want_version in scope` (version substring is also inside id; check both literally).
- Publisher `VERSION` becomes 2.0.4 so the rule applies to its sign-off; the notice builder's own copy of `validate_signoff` (L149) is frozen for 2.0.3 and must not gain it. The 2.0.3 sign-off JSON file stays immutable; since the real sign-off file still holds the 2.0.3 record while the publisher is 2.0.4, every real-file sign-off validation is red until Phase 18 (accepted).
- Tests need fixtures: a 2.0.4-form sign-off (valid scope without digests) built in memory, plus negative cases: scope with a 7-char, 40-char and 64-char hex; scope missing id; missing version; and a positive case that a 2.0.3-version call still accepts the old scope text (D-12). The exact current `Mutation` entries for sign-off (L560-582) use the real sign-off; switch them to a constructed 2.0.4 record.

### Pattern 6: SEC-03 (Claude's discretion)
`.github/workflows/ems-validate.yml` L64-65: `grep -RInE "$secret_pattern" . --exclude-dir=.git --exclude-dir=.venv --exclude='*.md'`. Remove `--exclude='*.md'`. Verified: `grep -RInE` of the pattern over the whole working tree restricted to `*.md` (excluding .git/.venv) found 0 files, and over `git ls-files '*.md'` 0 hits [VERIFIED: ran both locally]. Note the CI checkout contains only tracked files and `.planning/` is tracked, so `.planning/**/*.md` (including this research and 17-CONTEXT) are scanned; do not write literal token examples (for example a GitHub token prefix followed by 20+ alphanumerics, a PEM private-key header line, or the AWS secret-key variable name followed by an equals sign) in any .md. This file avoids them (its own literal examples were reworded in plan revision 1 so the pattern no longer matches it). No narrow exclusion is needed. Add a lightweight pytest guard (`tests/test_ci_secret_scan_covers_markdown.py` or inside an existing archive test file; note CI runs only `tests/test_archive_assessment_*.py`, so name it `test_archive_assessment_ci_workflow.py`) that reads the workflow text and asserts the secret-scan step contains no `--exclude='*.md'` (regex over the step) and that the pattern string is unchanged.

### DEFERRED-17 fixes (D-03), exact current locations
| Item | Current text / location | Change | Test hook |
|------|-------------------------|--------|-----------|
| IN-01 | L845-846 `'publication record authority_sha256 does not match the committed authority'` / `'...the committed manifest'` | "the authority in the working tree" / "the manifest in the working tree" | Mutate working-tree digest, assert new wording; old test matches nothing on "committed authority" (grep found no test matching it) |
| IN-02 | L841 `publication record still names the superseded {v} publication, so HEAD is the publication commit, not the record commit; run --validate --at-pin here, ...` | Reword to "...still names the superseded {v} publication (HEAD is the publication commit or earlier); run --validate --at-pin here ..." | Existing test L714 matches `still names the superseded {v} publication.*run --validate --at-pin here` - keep both phrases in that order |
| IN-03 | L836-839 at-pin branch | If `record.get('authority_id') == a['authority_id'] and record.get('version') == a['version']` raise "the record already names this publication; run plain --validate here" before the superseded-commit check | New test in the at-pin group |
| IN-04 | L793-794 shallow check only in at-pin; plain mode at L851 | Call `git_not_shallow()` first in `validate_published`; the later plain-mode call at L851 can stay or go; tests monkeypatching `git_not_shallow` (L245, L619, L678, L704, L780, L817) keep working since it is looked up by module global | Test: monkeypatch `git_not_shallow` to raise and `git_show` to record calls; assert no `git_show` before the raise in both modes |
| IN-06 | L814 `lf_digest(SCRIPT)` after manifest load, but after `validate_governance_decisions()` and authority validation | Move to immediately after the manifest `ps` shape check (part of Pattern 2 reorder) | Test: with manifest tampered AND an otherwise-failing authority, error is the script-digest error |
| IN-05, IN-06(scope) | superseded by SEC-04, SEC-02 | verification only: cross-check `16-REVIEW-CLOSURE.md` rows | Phase verification |

### Dependent uses to move for D-01 (all `SUPERSEDED_V2_0_2` sites)
Publisher L36-44 (def), L184 (build), L251, L292, L323, L326, L334-335, L349, L476 (schema), L587 (mutation text), L636 (dry-run). Also: `EXPECTED_NORMALISATION` unchanged; dry-run text L655 ("Gates GATE-01 to GATE-10", "Verification changes in 2.0.3" style strings) - update to describe 2.0.4 hardening (SEC-01..04, GATE-11/12) since the notice for 2.0.4 reads them [ASSUMED - wording belongs to Phase 18/19]; the manifest note L694. Tests referencing it (must be renamed together): `tests/test_archive_assessment_applicability_authority_v2.py` L204; `..._v2_publication.py` L82, 85, 191, 226, 241, 409, 1065 (hard-codes `'ae15c74'`), 1069, 1178, 1428, 1485, 1490; `tests/test_archive_assessment_lineage_validation.py` L32, 83, 373; `tests/test_archive_assessment_normalisation_claims.py` L36. Search for literal `ae15c74`, `2.0.2`, `a44eea1f` in tests too (the 2.0.2 authority digest is now not the supersedes digest). Keep a historical `SUPERSEDED_V2_0_2` constant in tests only if a test needs it; it should not remain in the publisher (D-01: "replaces").

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Git config isolation | Custom git wrapper or temp HOME dir | `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_COUNT/KEY/VALUE` | Native git env, verified working |
| Hex-run detection | Manual loop | `re.search(r'[0-9a-fA-F]{7,}', scope)` | One line |
| Digest check helper | Repeated inline copies | One `check_script_entry` helper in the publisher | Publisher and builder entries must not diverge |
| Schema pin values | Hand-typed literals in `schema()` | Module constants plus a git-recompute test | D-14 |

## Common Pitfalls

### Pitfall 1: Source-introspection tests ban the word "subprocess"
**What goes wrong:** `source_without_git_show()` (publication tests L94-104, L1351-1355) removes `import subprocess`, `git_show` and `git_run` source and asserts `subprocess` is nowhere else. A `git_env()` docstring/comment/variable mentioning it, or a new git call outside the two functions, turns tests red for a non-substantive reason.
**Avoid:** Keep `subprocess` strictly in `git_show`/`git_run`; name the helper `git_env`; no comments with that word. Both functions must still contain the literal `subprocess.run`.

### Pitfall 2: Exact-argv tests
`test_git_show_argv_ends_with_double_dash` expects argv exactly `['git','show','<sha>:<path>','--']`. Use env, not `-c`, for longpaths/etc. Also fakes of `subprocess.run` accept `(argv, **kwargs)`; adding `env=` as kwarg is fine.

### Pitfall 3: `load_pinned_publisher` wrappers in 2.0.3 notice tests
Four wrappers call `real(tmp)`. Signature change requires updating them in the same commit (lines 146-180, 819-828).

### Pitfall 4: `_BUILDER` cache and validation order
`decisions_builder()` caches the module; a test (or `--validate` after `build_published_authority`) that already imported the builder will not re-check. The digest check must run on every `validate_published` call independently of the cache (compare `lf_digest(BUILDER_SCRIPT)` each time; only the exec is cached).

### Pitfall 5: Red-window accounting
Real-file tests turn red from the first publisher byte change because the certified manifest hashes the publisher (`test_publisher_still_valid_and_digest_matches_manifest`, `test_real_published_files_validate`, CI validator 1), the schema-equality test turns red once `schema()` changes, and the sign-off/version/supersedes changes turn red tests that read the real 2.0.3 files. Plus: the D-10 baseline test (`test_archive_assessment_lineage_validation.py`). Do NOT touch the publisher until the green-safe commits are done. Each publisher commit must record measured red node ids in `17-BASELINE-RED.md`; the main session runs pytest (`--basetemp`, `EMS_FAIL_ON_SKIP=1`) because Bash is flaky.

### Pitfall 6: autocrlf on isolated git
See Pattern 3; verify with the real repo `git status` for the 12-file set and the two scripts. If the scripts are added to `.gitattributes` with `eol=lf`, that file change is itself a deliberate commit in the green-safe group; CRLF-in-working-tree for these two scripts is currently normal on this machine.

### Pitfall 7: Hex-run rule vs ordinary text
`[0-9a-fA-F]{7,}` also matches digit-only runs and words like "defaced". The id text `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.4` contains no 7-char hex run (hyphens/dots break it) [VERIFIED by reasoning on the string]. Add a test that the id+version-only scope passes.

### Pitfall 8: Frozen builders
Reply (2.0.1) and 2.0.2 notice builders and `PINNED_*` frozen constants must stay byte-unchanged; verify with `git diff --exit-code` on both and on the 2.0.3 notice outputs after edits to the notice builder.

## Code Examples

Hash-before-exec in the notice builder (shape; names follow the existing file):

```python
def load_pinned_publisher(tmp: Path, manifest: dict):
    for p in (*PINNED_CODE, *PINNED_DATA):   # existing materialisation loop
        ...
    ps = manifest.get('publisher_script') if isinstance(manifest, dict) else None
    if not isinstance(ps, dict) or not isinstance(ps.get('sha256'), str):
        raise AuthorityError('manifest publisher_script entry missing or invalid')
    if hashlib.sha256(lf_bytes((tmp / PINNED_CODE[0]).read_bytes())).hexdigest() != ps['sha256']:
        raise AuthorityError('pinned publisher differs from the certified publisher_script digest')
    spec = importlib.util.spec_from_file_location('aa_pinned_publisher_2_0_3', tmp / PINNED_CODE[0])
    pub = importlib.util.module_from_spec(spec); spec.loader.exec_module(pub)
    if hashlib.sha256(lf_bytes((tmp / PINNED_CODE[1]).read_bytes())).hexdigest() != PINNED_DECISIONS_BUILDER_SHA256:
        raise AuthorityError('pinned decisions builder differs from the frozen digest')
    b = pub.decisions_builder()
```
Caveat: in this shape the builder digest check sits after publisher exec (publisher code runs, builder does not). Pinned publisher top level runs only after its own digest is checked, which is what SEC-01 requires. Since the digest of both blobs is known up front, do both checks BEFORE the first `exec_module` for the strictest ordering (recommended) and keep the test asserting neither ran.

Hostile env test skeleton:

```python
def test_git_seam_ignores_hostile_environment(tmp_path, monkeypatch):
    repo, decoy = make_repo(tmp_path/'r'), make_repo(tmp_path/'d')
    sha = commit_file(repo, 'registry/a.json', b'real\n'); replace_blob(repo, sha_of('registry/a.json'), b'fake\n')
    for k, v in {'GIT_DIR': str(decoy/'.git'), 'GIT_WORK_TREE': str(decoy), 'GIT_INDEX_FILE': str(decoy/'idx'),
                 'GIT_OBJECT_DIRECTORY': str(decoy/'.git'/'objects')}.items(): monkeypatch.setenv(k, v)
    monkeypatch.setattr(MODULE, 'ROOT', repo)
    assert MODULE.git_head() == sha and MODULE.git_show(sha, 'registry/a.json') == b'real\n'
```

## State of the Art

| Old | Current | Impact |
|-----|---------|--------|
| `git_show` using inherited env | sanitized env (this phase) | `refs/replace` and `GIT_DIR` can no longer redirect fail-closed checks |
| pin digest checked after exec | before exec | pinned code never runs unverified |
| schema pins superseded digests by pattern | `const` | schema alone rejects drifted lineage |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 (OPEN: stays open until the CI `workflow_dispatch` run confirms it) | ubuntu-latest git supports `GIT_CONFIG_GLOBAL` (>=2.32) and `GIT_CONFIG_COUNT` (>=2.31) | Pattern 3 | CI hostile-env test fails; CI `workflow_dispatch` is the authoritative run |
| A2 | Differently-owned checkouts failing with "dubious ownership" after dropping global `safe.directory` is acceptable fail-closed behaviour | Pattern 3 | Operator friction only |
| A3 (RESOLVED: D-09 amended to env config) | Env-based `GIT_CONFIG_COUNT` is acceptable in place of `-c` argv (CONTEXT D-09 wording says `-c`) | Pattern 3 | If `-c` is mandated, update argv-shape tests |
| A4 | Dry-run/manifest note wording changes are free text decided by the planner/Phase 18 | Pattern 5 | Notice wording mismatch later |

## Open Questions (RESOLVED)

1. **Scripts' working-tree EOL under isolation**
   - Known: repo-local autocrlf=true saves the real repo; publication files have `eol=lf`; the two scripts have no eol attribute and are CRLF in the working tree.
   - Unclear: behaviour of `git_dirty` (at-pin, includes `rel(SCRIPT)`, and builder if added) on a fresh Windows clone.
   - Recommendation: add `text eol=lf` for the publisher and decisions builder to `.gitattributes` in a green-safe commit (changes no index bytes), and have the hostile-env test cover `git_dirty` on a CRLF working file in a scratch repo configured with and without local autocrlf.
   - RESOLVED: `.gitattributes` `text eol=lf` for the publisher and decisions-builder scripts, committed in 17-01 before the first publisher edit (D-09a); the hostile-env test in 17-03 covers `git_dirty`.
2. **`-c` vs env for longpaths.** Recommendation: env (A3). Confirm with the user only if strictness on the wording matters.
   - RESOLVED: env `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0`, not `-c` (D-09 amended, git >= 2.32).
3. **Should `decisions_builder()` itself take the expected digest** (defence in depth for any other caller), or only `validate_published`? Recommendation: parameter on `decisions_builder`, passed from `validate_published`.
   - RESOLVED: `decisions_builder(expected_sha256=None)`, digest checked on every call outside the `_BUILDER` cache, forwarded from `validate_published` (17-05, D-06).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| git | all | yes | 2.54.0.windows.1 | - |
| Python 3.12 + jsonschema 4.26.0 + pytest | tests | yes (repo .venv; main session runs) | - | - |
| Bash tool | scripts | flaky (my probes worked this session) | - | PowerShell; main session runs full pytest with `--basetemp` |
| Local `git clone` of the repo | clone-based tests | unreliable | - | CI `workflow_dispatch` is authoritative |

## Validation Architecture

Nyquist validation is disabled; mapping is only for the planner.

| Req | Test (new unless noted) | File |
|-----|-------------------------|------|
| SEC-01 | tampered pinned publisher blob: AuthorityError, sentinel absent, `spec_from_file_location` not called; manifest digest mismatch; missing manifest entry | `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` (update 4 wrappers) |
| SEC-02 (2.0.3) | tampered pinned builder blob rejected before exec; constant recomputes from git | same |
| SEC-02 (2.0.4) | manifest missing/invalid builder entry; live builder differs; plain-mode builder-at-pin differs; check precedes `decisions_builder()` (spy on `spec_from_file_location`) | `tests/test_archive_assessment_applicability_authority_v2_publication.py` |
| SEC-03 | workflow text has no `*.md` exclude | new `tests/test_archive_assessment_ci_workflow.py` (must match `test_archive_assessment_*.py` glob) |
| SEC-04 | hostile env across publisher, notice builder + shim, `aa_history`; same-policy test across 3 copies; literal pathspec (a path containing `*`) | publication tests; notice tests; `test_archive_assessment_skip_guard.py` for aa_history |
| GATE-11 | one mutation per newly pinned field with `schema_must_reject=True`; `schema()` const equals git-recomputed digest | `..._v2.py`, `..._publication.py` |
| GATE-12 | scope rule cases (see Pattern 5) | publication tests |
| DEFERRED-17 | IN-01..IN-04, IN-06 tests per table | publication tests |

Quick command (main session): `EMS_FAIL_ON_SKIP=1 python -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q -rf --basetemp=<scratch>`. Baseline before any edit: record in `17-BASELINE-RED.md` (12-BASELINE-RED.md format; last known 16 state is all green).

## Security Domain

| ASVS Category | Applies | Control |
|---------------|---------|---------|
| V5 Input validation | yes | `bad_rel`, 40-hex commit check, sign-off scope regex, schema `const`/pattern |
| V6 Cryptography | yes | `hashlib.sha256` only; no custom crypto |
| V10 Malicious code / integrity | yes | verify digest before exec; frozen constants |
| V14 Config | yes | sanitized git env; CI secret scan includes md |
| V2/V3/V4 | no | no authn/session/access control |

| Threat | STRIDE | Mitigation |
|--------|--------|------------|
| Tampered pinned publisher/builder executed | Tampering/EoP | hash-before-exec (SEC-01/02) |
| Ambient `GIT_DIR`, replace refs redirect checks | Tampering/Spoofing | `git_env()` (SEC-04) |
| Secret committed in .md | Info disclosure | CI scan (SEC-03) |
| Digest hidden in free-text scope | Repudiation | scope rule (GATE-12) |
| Local `.git/config` hostile (e.g. `include.path`, `core.fsmonitor`) | Tampering/EoP | Out of scope: repo-local config is trusted; note in closure |

## Sources

### Primary (HIGH)
- Repo files read: `scripts/publish_archive_assessment_applicability_authority_v2.py`, `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `scripts/build_archive_assessment_governance_decisions.py` (imports), `tests/aa_history.py`, publication/lineage/notice tests (cited lines), `.github/workflows/ems-validate.yml`, `.gitattributes`, `registry/archive_assessment_applicability_authority_v2_signoff.json`, `16-REVIEW-CLOSURE.md`, `12-REVIEW.md` (IN-01..06, WR-02), `12-BASELINE-RED.md`, `17-CONTEXT.md`, `REQUIREMENTS.md`.
- Local experiments (git 2.54.0.windows.1): hostile env vs sanitized env in a scratch repo; `git config --show-origin` under isolation; `git status --porcelain` on publication paths under isolation; builder blob digest at `1544dc1`; secret-pattern grep over md files.

### Secondary / Tertiary
- Git env var semantics (`GIT_CONFIG_GLOBAL`, `GIT_CONFIG_COUNT`, `GIT_NO_REPLACE_OBJECTS`, `GIT_LITERAL_PATHSPECS`): from training knowledge, confirmed by the local experiment but not re-read from git docs this session (MEDIUM).

## Metadata

**Confidence:** Standard stack HIGH (no change); Architecture HIGH (read from code); Pitfalls HIGH (read from tests); CI git-version behaviour MEDIUM.
**Research date:** 2026-11-18. **Valid until:** until the publisher or notice builder changes outside this phase.

## Project Constraints (from CLAUDE.md)
- Python 3.12, `jsonschema`, PyYAML, pytest; match existing file style (the publisher uses single quotes and compact one-line helpers; deterministic JSON `json.dumps(..., indent=2, sort_keys=True) + '\n'`; `AuthorityError` fail-closed; repo-relative forward-slash paths).
- Unrelated uncommitted work in the tree stays untouched; each commit stages explicit paths only; the Hayes-pinned commit contains only deliberate changes.
- New scripts use snake_case; no new versioned `-v2` style scripts; edit existing files.
- Hash-based certification: do not hand-edit generated outputs; any publisher edit needs republication (Phase 18).
- Work must go through a GSD workflow before edits.
