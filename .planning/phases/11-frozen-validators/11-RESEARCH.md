# Phase 11: Frozen Validators - Research

**Researched:** 2026-11-14
**Domain:** Python governance scripts and pytest; freezing two historical validators against a live publisher
**Confidence:** HIGH (all findings come from reading the repo, git history and an executed probe of the pinned blobs)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Each frozen builder holds the publisher semantics it needs as **local literals and local code**. This covers `DUAL_ROLE_STATEMENT`, `PREV_COMPARED_KEYS` (notice), `REQUEST_CONTROL_IDS`, `RULE_FIELDS`, `CONDITION_STATES`, `COMBINATION`, `APPROVER_ROLES`, `DECISION_STATES`, `AUTHORITY_ID_RE`, `rule_text`, `validate_signoff`, `closed_schema_levels` (notice), `latest_records` (reply), and the repo-relative path constants (`AUTHORITY`, `SIGNOFF`, `OUT`, `N_TRACE`, `N_MANIFEST`, `N_NEGATIVE`, `PUBLICATION_RECORD`, `GOVERNANCE_DECISIONS`, `SCHEMA`, ...). The runtime path never execs code read from git.
- **D-02:** A pytest proves each literal is correct. It loads the publisher blob at the frozen **publication commit** (reply: `31addfa...`, the existing `REPLY_PUBLICATION_COMMIT`; notice: `ae15c74...`, `NOTICE_PUBLICATION_COMMIT`) with `git show` plus `exec` into a throwaway module, **in the test only**. It then asserts that every frozen constant equals the frozen publisher's value. For the frozen functions (`rule_text`, `validate_signoff`, `closed_schema_levels`, ...), it asserts equal output on representative inputs, including the real frozen inputs. If a literal must differ from that publisher and still rebuilds the committed bytes, the plan records the difference and justifies it.
- **D-03:** Generic helpers are **copied into each builder**: `git_show`, `lf_bytes`, `jtext`, `rel`, `load`, `dump`/`write_text` (if still needed), `contains_absolute`, `AuthorityError`, `GitHistoryError`, and any `NORMALISERS`/`lf_digest` use. Each builder ends with **zero imports** of `publish_archive_assessment_applicability_authority_v2` (no `V2`). Keep the compact single-quote style already used in each builder.
- **D-04:** The frozen schema check stops regenerating the schema. `--validate` requires the committed schema bytes to equal `git_show(<artifact's commit>, <schema path>)`, then validates the committed JSON against that schema. `schema()` is removed from the validate path; the planner decides whether to delete it. The planner also picks the commit constant for each schema: the reply schema's commit (e.g. `e781f08`, full SHA) and the 2.0.2 notice commit. These are full SHAs, and `cat-file -e` and ancestor checks apply, as with the other anchors.
- **D-05:** Remove `--build` and `--emit-schema` from both builders. The argparse group offers `--validate`, plus `--push-check` on the reply if kept (D-06). The CLI can no longer write the frozen files. Tests rebuild in memory with `build_*()` and never write repo files. The CI step (`--validate`) is unchanged.
- **D-07:** The scope is **every `tests/test_archive_assessment_*.py`**. Every `pytest.skip` that fires because a pinned commit or blob is unreachable becomes `pytest.fail`, with an explicit message naming the commit and path and saying to fetch full history. This includes `prev_201_authority_bytes()` (31addfa) in the publication tests, the lineage-validation 2.0.1 skip, the governance_decisions `eed4a5f` skip, the rule_proposals git skip, and the reply and notice tests. The validators themselves already fail closed; check that their errors name the missing commit and path, and fix any that don't.
- **D-08:** `git_ready()` failures (shallow clone, not a repository, no git) **fail by default**. A local opt-out env var (for example `EMS_ALLOW_NO_HISTORY=1`; planner picks the name) restores the skip for offline local runs. CI never sets it. Put this in one shared place, such as `tests/conftest.py` or a small helper, rather than in the 6+ copies of `git_ready`. Whether to de-duplicate those copies is Claude's discretion.
- **D-09:** Existence guards left over from the red-window era also become failures, because the artifacts are committed: `skipif(not REAL_AUTHORITY.exists())`, `skipif(not REAL_RECORD.exists())`, `'answers not yet filled'`, `'decisions not yet built'`, `'not yet written'` (`gated()`), `git commit unavailable` and `git unavailable` in temp-repo fixtures. Temp-repo `git unavailable` cases follow D-08's opt-out.
- **D-10:** CI guard: the `archive-assessment` job in `.github/workflows/ems-validate.yml` fails if the pytest run reports **any skipped test**. Use a conftest hook active under `CI`, or `-rs` plus a summary check; planner's choice. This is a workflow/test change, not a publisher change, so it is allowed before Phase 12.
- **D-11:** SC1 is proven two ways: (1) **Static:** a test parses both builders with `ast` and asserts that neither imports the v2 publisher module, whether by `import`, `from ... import` or `importlib`/`spec_from_file_location` with its path. (2) **Behavioural:** a test installs a deliberately **mutated** copy of the live publisher in `sys.modules` under its import name (and at the path the old loader used). The copy has changed `PREV_COMPARED_KEYS`, a changed `DUAL_ROLE_STATEMENT`, a `validate_signoff` that raises and a different `rule_text`. The test asserts that `validate_reply()` and `validate_notice()` still PASS on the committed files. This replaces the narrow `test_validate_independent_of_live_version`, or extends it.
- **D-12:** Notice test rigor (10-REVIEW WR-03, IN-01): each negative test asserts a **specific** error (`match='absolute path'`, `jsonschema.ValidationError` or `match='schema'`, and so on) rather than the broad `REJECTS` tuple; the guarded function is called directly where needed, so the named guard is the one that fires (example: `digest_scope_error` with an edited `previous`, and `build_notice` with an edited `previous` argument); `test_changed_row_blocks_no_decision_changed` either asserts that `build_notice` raises, or is renamed to what it really tests; one test runs `validate_notice()` against the **committed** repo files with no monkeypatching. It is subject to D-08 only.
- **D-13:** The reply tests get the same treatment as the notice tests: specific matches on negative tests, and a committed-files `validate_reply()` test (add it if missing).

Carried forward: stage only by explicit path; never stage `.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json` or unrelated untracked files. Reply and notice bytes stay frozen (check with `git diff` against their commits). The publisher file shows **no diff** at the end of Phase 11 (SC4). Validators stay green after every commit; no red window. Fail closed without history; keep the WR-01 record-to-publication-commit binding.

### Claude's Discretion
- Constant and helper names, and how much of `schema()` / `render_markdown` to keep (the validate path still needs `render_markdown` for the byte rebuild).
- D-06 `--push-check` keep or remove.
- Whether to de-duplicate the `git_ready` copies (D-08).
- The D-10 mechanism.
- How the commits are split. Preferred: (1) freeze the reply, (2) freeze the notice, (3) skip-to-fail plus the CI guard, (4) test rigor. Each commit stages explicit paths and stays green.

### Deferred Ideas (OUT OF SCOPE)
- Notice claim enforcement for the 2.0.2 notice (WR-01/WR-04/WR-05). CLAIM-01..03 apply to the 2.0.3 notice builder in Phase 14.
- A mutation-sweep meta-test that disables each guard and asserts its test goes red.
- Executing the historical publisher from git at runtime.
- Any edit to the publisher, its schema, the authority or publication files (Phase 12). Regenerating the reply or the notice.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FROZEN-01 | Reply validator uses no live publisher constants/functions | Inventory of every `V2.*` use in the reply builder (below); local-literal list; `validate_signoff` signature trap; D-02/D-11 test design |
| FROZEN-02 | Notice validator uses no live publisher constants/functions (`PREV_COMPARED_KEYS`, `DUAL_ROLE_STATEMENT`, `validate_signoff`, `rule_text`) | Inventory of the notice builder's `V2.*` uses; frozen blob at ae15c74 verified to hold them |
| FROZEN-03 | Unreachable pinned blob fails, never skips | Skip-site inventory per file; `needs_git`/`skipif` collection-time trap; shared helper and CI skip guard design |
| FROZEN-04 | Pytest validates committed notice files; each notice test goes red for its named check | Test-by-test weakness list for the notice and reply tests; committed-files test; specific-match guidance |
</phase_requirements>

## Summary

Both builders load the live publisher with `importlib.util.spec_from_file_location(...)` and execute it at import time as `V2`. About 30 symbols are borrowed from it. Today live and frozen values are identical (the live file differs from the ae15c74 blob only by line endings), so nothing is red. The first Phase 12 edit would change them. Freezing means giving each builder its own literals and helper copies, proving them equal to the frozen publisher blob in a test, and proving by mutation that a changed live publisher cannot move either result.

I probed the pinned blobs by executing them in a throwaway module (with `__file__` set to the real script path and the module registered in `sys.modules`). Both exec cleanly. 31addfa gives `VERSION='2.0.1'` and has no `PREV_COMPARED_KEYS`. ae15c74 gives `VERSION='2.0.2'` and has `PREV_COMPARED_KEYS`. **The two frozen publishers differ in `validate_signoff`.** 31addfa has `validate_signoff(record, authority_lf_digest)` and compares to the 2.0.1 `AUTHORITY_ID` and `VERSION`. ae15c74 has `validate_signoff(record, authority_lf_digest, authority_id=None, version=None)`. The reply builder today calls the live 4-arg form with keyword arguments, so it is actually depending on the 2.0.2 publisher. Freeze the reply on the 31addfa 2-arg form (hard-wired to 2.0.1) and freeze the notice on the ae15c74 4-arg form. That is what "frozen on 2.0.1" and "frozen on 2.0.2" mean.

The skip work is mostly mechanical, but there is one design trap. `needs_git` (governance_decisions, rule_proposals_record) and every `skipif(not X.exists())` is evaluated at collection time, where a test cannot fail. They must become runtime checks (fixture or an in-test call). Pytest has no built-in "skips are failures" switch, so D-10 needs a small `conftest.py` hook.

**Primary recommendation:** Do the four commits in the CONTEXT order. Within each, write the new in-memory-only validator first and keep the old tests green by switching them from `MODULE.V2.x` to `MODULE.x` in the same commit. Put the D-02 literal-vs-blob test and the D-11 mutation test into the same commit that freezes each builder, so there is never a window where the freeze is unproven.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Frozen reply and notice validation | `scripts/build_archive_assessment_demo3_*` (single-process Python CLI) | `tests/` | Validators are the authority for the historical documents; tests prove them |
| Frozen-literal correctness proof | `tests/` (exec of the git blob, test only) | -- | D-02 forbids exec of git code at runtime |
| Pinned-history availability policy (fail vs skip) | shared test helper / `tests/conftest.py` | each test module | One place for the opt-out env var |
| No-skip CI guard | `tests/conftest.py` hook plus `.github/workflows/ems-validate.yml` | -- | CI sets the env var; the hook converts skip to fail |
| Committed bytes (reply, notice, schemas) | Git (unchanged) | -- | Frozen; validators only read |

## Standard Stack

No new packages. Everything is already in the repo's stack. [VERIFIED: CLAUDE.md, imports of the two builders and tests]

| Library | Version | Purpose |
|---------|---------|---------|
| Python | 3.12 (`.venv/Scripts/python.exe`; CI pins 3.12) | runtime |
| `jsonschema` | unpinned in `requirements.txt` path | `Draft202012Validator` for the committed frozen schema |
| `pytest` | per `requirements-dev.txt` | tests, `conftest.py` hooks |
| stdlib `ast`, `types`, `subprocess`, `hashlib`, `re` | stdlib | static import test, blob exec in test, git |

**Package legitimacy audit:** No external packages are installed or recommended in this phase, so slopcheck does not apply. [VERIFIED: scope reading]

## Architecture Patterns

### Data flow after the freeze

```
frozen git objects (31addfa / 4d9b7c1 for reply; ae15c74 / a71257e / 31addfa for notice)
        |  git show  (local git_show copy, fail closed, names full SHA + path)
        v
 builder.load_inputs() -> build_x(inputs)  -- local literals + local helpers only
        |                         |
        |                 render_markdown(x)   json: jtext(x)
        v                         v
 validate_x():  committed JSON/MD bytes == fresh build (LF-normalised)
                committed schema bytes == git_show(SCHEMA_COMMIT, schema path)
                jsonschema(committed schema).validate(committed JSON)
                binding checks (record commit, manifest, trace)  -> PASS

tests/ (never in the runtime path):
   exec(git show PUBLICATION_COMMIT:publisher) into a throwaway module
        -> assert builder constants == blob constants; builder funcs == blob funcs
   mutated live-publisher copy in sys.modules -> fresh-import builder -> validate still PASS
   ast scan of builder source -> no import or path literal naming the v2 publisher
```

### Exact V2 inventory (what must become local)

**Reply builder** (`V2.` uses):
- Constants: `REQUEST_CONTROL_IDS`, `DECISIONS`, `APPROVER_ROLES`, `DECISION_STATES`, `DUAL_ROLE_STATEMENT`, `GOVERNANCE_DECISIONS_REL`, and paths `AUTHORITY`, `SCHEMA`, `OUT`, `SIGNOFF`, `GOVERNANCE_DECISIONS`, `PUBLICATION_RECORD`, `N_MANIFEST`, `N_TRACE`.
- Used only by `schema()`: `RULE_FIELDS`, `CONDITION_STATES`, `COMBINATION`, `AUTHORITY_ID_RE`. If `schema()` is deleted (recommended, D-04), these four literals are not needed. Fewer literals mean fewer drift points.
- Functions: `git_show`, `lf_bytes`, `jtext`, `rel`, `load`, `contains_absolute`, `latest_records`, `validate_signoff`, `rule_text`, `AuthorityError`, `GitHistoryError` (only via tests). `dump` and `write_text` are used only by `--build` and `--emit-schema`, so they go away with D-05.

**Notice builder** (`V2.` uses):
- Constants: `REQUEST_CONTROL_IDS`, `APPROVER_ROLES`, `DUAL_ROLE_STATEMENT`, `PREV_COMPARED_KEYS`, and paths `AUTHORITY`, `SIGNOFF`, `SCHEMA`, `OUT`, `N_MANIFEST`, `N_TRACE`, `N_NEGATIVE`, `GOVERNANCE_DECISIONS`, `PUBLICATION_RECORD`.
- `schema()` only: `RULE_FIELDS`, `CONDITION_STATES`, `COMBINATION`, `AUTHORITY_ID_RE` (again unnecessary if `schema()` is deleted).
- Functions: `git_show`, `lf_bytes`, `jtext`, `rel`, `load`, `contains_absolute`, `closed_schema_levels`, `validate_signoff`, `rule_text`, `AuthorityError`, `GitHistoryError`. `dump`/`write_text` go with `--build`.
- `V2.ROOT` is used once, in the `validate_notice` "not generated" message: use the local `ROOT`.
- `validate_signoff` pulls in `is_date`, `APPROVER`, `SIGNOFF_ROLE` and `datetime.date`. Copy them as well (`APPROVER='Oscar Mack'`, `SIGNOFF_ROLE='EMS_GOVERNANCE_AUTHORITY'`).
- `NORMALISERS` and `lf_digest` are **not** used by either builder, so there is nothing to copy. (D-03 lists them "if used".)

### Pattern 1: Frozen validate_signoff per publisher version
- Reply: copy the 31addfa form `validate_signoff(record, authority_lf_digest)` with literal `AUTHORITY_ID='EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1'` and `VERSION='2.0.1'`. Change the call site from `validate_signoff(signoff, d, authority_id=..., version=...)` to the 2-arg call. The committed reply bytes do not change, because the record being validated is 2.0.1. Record this in the plan as the one deliberate difference (D-02 asks for it). The signoff blob at 31addfa carries `authority_id` 2.0.1, so the check still passes. [VERIFIED: diff of 31addfa vs ae15c74 publisher blobs]
- Notice: copy the ae15c74 form byte-for-byte, including the `authority_id=None, version=None` defaults. Defaults refer to `AUTHORITY_ID`/`VERSION`, so define those two as the 2.0.2 literals too. The builder always passes both. [VERIFIED: blob read]

### Pattern 2: D-02 literal-vs-blob test (test only)
```python
# tests: load a frozen publisher blob without importing the live one
import subprocess, sys, types
def frozen_publisher(commit):
    src = subprocess.run(['git', 'show', f'{commit}:scripts/publish_archive_assessment_applicability_authority_v2.py'],
                         cwd=ROOT, capture_output=True, check=True).stdout.decode('utf-8')
    m = types.ModuleType('aa_frozen_publisher')
    m.__file__ = str(ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')  # so ROOT resolves
    sys.modules['aa_frozen_publisher'] = m        # NamedTuple in the blob needs this
    try: exec(compile(src, f'publisher@{commit[:7]}', 'exec'), m.__dict__)
    finally: sys.modules.pop('aa_frozen_publisher', None)
    return m
```
Verified by probe: both blobs exec cleanly under `python -I` with the repo `.venv`; `ROOT` resolves to the repo; the reply blob has no `PREV_COMPARED_KEYS`. Use `check=True` plus a wrapper that calls `pytest.fail` with the commit, path and "fetch full history" text (D-07). Parametrise the constant comparison over a list of names per builder. Assert `m.AUTHORITY.relative_to(m.ROOT)` strings equal the builder's repo-relative constants. If the builders keep paths as `Path` under their own `ROOT`, compare `rel()` output.

Function equivalence cases to include: `rule_text` on each of the 3 real rules and a 2-condition synthetic rule; `latest_records` (reply) on the real decisions doc and a doc with `supersedes` as str and as list; `closed_schema_levels` (notice) on the real frozen schema and a nested synthetic one; `validate_signoff` on the real frozen signoff plus at least one mutation per error branch (wrong approver, wrong role, bad date, empty scope, altered dual-role text, wrong id, wrong version, wrong digest, wrong normalisation, extra key, non-dict). Compare **exception text** equal or both pass. For the reply, the blob is 2-arg and the builder is 2-arg, so the call shape is the same. `contains_absolute` and `jtext`/`lf_bytes`/`rel` get a few direct cases (`jtext` equality on a nested dict; `contains_absolute` on `/x`, `\\\\x`, `C:\\x`, `C:/x`, nested list/dict).

### Pattern 3: D-11 behavioural mutation test
The current loader never registers the publisher in `sys.modules`, so the mutation must be applied in a way that would have affected the old loader. The old loader read the **file at the path**. A genuinely meaningful test therefore patches whatever the old code would have reached:
1. Build a mutated copy of the live publisher (read the live file text, `exec` into a throwaway module, then overwrite `PREV_COMPARED_KEYS`, `DUAL_ROLE_STATEMENT`, `rule_text`, and set `validate_signoff` to a function that raises).
2. Register it in `sys.modules` under `'aa_applicability_publisher_v2'` and `'publish_archive_assessment_applicability_authority_v2'` (the import name), and also patch `importlib.util.spec_from_file_location` for that path to return a spec that loads the mutated module (this is what the old code used).
3. **Fresh-load** the builder file (new `spec_from_file_location` + `exec_module`, as the test files already do). Do not reuse the module the test file loaded at import time, because it was loaded before the mutation.
4. Assert `validate_reply()` and `validate_notice()` print PASS (use `capsys`) on the committed files.
If the builder still imported the publisher, step 3 would load the mutation and the validate would fail. Also run the same test against a builder snapshot to show it is not vacuous: simplest is a unit check in the same test that a throwaway builder source with the old import line (`git show HEAD:...` of the pre-freeze builder is not available after the commit, so instead assert the static AST test would flag a string containing the old loader line).

### Pattern 4: Static independence test (AST)
Parse each builder and walk the tree. Fail if any of these appear: `ast.Import`/`ast.ImportFrom` naming a module whose dotted path contains `publish_archive_assessment_applicability_authority`; any `ast.Constant` string containing `publish_archive_assessment_applicability_authority_v2`; any `ast.Name` or `ast.Attribute` equal to `V2`; any call to `importlib.import_module`, `__import__`, `spec_from_file_location`, `SourceFileLoader`, `exec`, or `eval` in the builder. Scanning all string constants catches the path form. Comments are not in the AST, so SCRIPT_REL text and the markdown never trip this (the markdown strings do not contain the publisher name; confirmed by reading both render functions).

### Recommended commit structure (matches CONTEXT)
1. **Reply freeze** (`scripts/...reply.py`, `tests/...reply.py`): local literals and helpers, 2-arg `validate_signoff`, `REPLY_SCHEMA_COMMIT`, no `--build`/`--emit-schema`, D-02 + D-11 + AST tests, committed-files test (D-13), move or relocate the `V2.validate_published()` test (see Pitfall 1).
2. **Notice freeze** (`scripts/...notice_2_0_2.py`, `tests/...notice_2_0_2.py`): same for the notice.
3. **Skip-to-fail + CI guard**: shared helper, conftest hook, edits to ~9 test files, `.github/workflows/ems-validate.yml`.
4. **Notice/reply test rigor (D-12/D-13)**: specific matches, direct guard calls, rename or strengthen `test_changed_row_blocks_no_decision_changed`.
Commit 4 may fold into 1 and 2 if the plan prefers. Each commit stages explicit paths only.

### Schema commit constants (D-04)
Both committed schema files are byte-equal to HEAD at these commits. [VERIFIED: `git show <sha>:<path> | cmp`]
- Reply schema: last changed in `7debe4aa544b425f2b80306a8510bfe74e568bae` (`feat(06-08)`). `e781f08eaaf45b227c4cb2c96d110ecec85d584c` (the commit CONTEXT suggested) also holds identical bytes, and both are ancestors of HEAD. Prefer `7debe4aa...` because it is the last commit that changed the file, so the constant says what it means. If the reply MD/JSON commit is preferred for symmetry, that is `258875de55dddc1ce0fc588612336f5aa6b53832`, but the schema did not change there.
- Notice schema: `052f0f13f4c882a7b80667d4835bc802002e0f80` (`docs(10): add 2.0.2 notice to Hayes`). Note this is a commit made **after** the notice publication commit; it is not the same as `NOTICE_PUBLICATION_COMMIT`. It must pass the `cat-file -e` and ancestor checks.
- The schema files carry `eol=lf` in `.gitattributes`, so raw bytes already equal LF bytes on Windows. Compare with `lf_bytes()` on both sides anyway, as the existing code does.
- The embedded `const` values in the notice schema (`NOTICE_PUBLICATION_COMMIT`, ids, 29 mutations, 16 levels) come from the committed bytes now, not from builder constants, which removes a second source of truth.

### Where the validation logic needs the schema
`validate_reply_object` and `validate_notice_object` call `schema()` today, and many tests call them directly on mutated objects. After D-04 replace `schema()` with `frozen_schema()` = `json.loads(git_show(SCHEMA_COMMIT, SCHEMA_REL))` (cache not needed). Tests such as `test_mutation_bad_aa4_format` then still raise `jsonschema.ValidationError` from the same schema bytes. Existing tests that call `MODULE.schema()` (`test_history_note_binds...`, `test_schema_closes_every_object_level`, `write_set`, `test_validate_notice_rejects_loosened_schema_file`) need a `frozen_schema()` or git-read replacement.

### D-06 recommendation: remove `--push-check` from the reply
Reasons: it shells out `git ls-remote origin`, so it depends on network and live remote state; it only reports whether the already-sent 2.0.1 publication commit is on the remote branch; it is not used by CI, the workflow or any script (grep: only 05-phase planning docs mention it); a frozen validator should be hermetic. Removing it also deletes `sys`, `PUSH_*`, `push_check()`, `REMOTE_BRANCH` use outside the markdown text, and 8 tests (`test_push_check_*`, the `fake_git` helper). `REMOTE_BRANCH` stays because `build_reply` writes it into `send_condition`. Rewrite `test_cli_flags_mutually_exclusive` to assert that `--build`, `--emit-schema` and `--push-check` all exit non-zero with argparse errors and that `--validate` is the only accepted flag. Alternative (keep) is defensible but adds a read-only network call to a frozen module; record whichever choice in the plan.

### Anti-patterns to avoid
- **Importing a shared "frozen_common" module for both builders.** D-03 says copy; a shared module is a new live dependency that could drift (and `scripts/` builders are run as scripts, not packages).
- **Reading the publisher text via `git show` at runtime** (rejected in D-01).
- **Keeping `MODULE.V2` as an alias** in the test file. Tests that still need the live publisher (for example `V2.validate_published`) must load it themselves under a different name so a stray `MODULE.V2` use fails loudly.
- **Patching `V2.git_show` in tests.** After the freeze, tests must patch `MODULE.git_show`. This works only if `pinned_bytes` and friends call `git_show` as a module global at call time (they do today via `V2.git_show`; the copy must keep global-name lookup, not bind it as a default argument).

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| Failing on skips in CI | a custom runner or log scraper | a `pytest_runtest_makereport` hook in `tests/conftest.py` gated by an env var | The skip outcome is visible only inside pytest; output scraping misses `-q` mode and xdist |
| Comparing frozen vs live code | text diff of the files | exec the blob in the test and compare values and outputs (D-02) | A file diff is noisy (line endings) and says nothing about behaviour |
| Detecting imports in the builders | regex on source | `ast` walk | Regex misses aliasing and string-path loaders |
| JSON schema validation | custom checker | `jsonschema.Draft202012Validator` (already used) | Existing |

## Common Pitfalls

### Pitfall 1: The reply test file couples to the live publisher in a non-frozen way
`test_publisher_still_valid_and_digest_matches_manifest` (reply tests, around line 258) calls `V2.validate_published()` and compares `V2.lf_digest(V2.SCRIPT)` to the committed manifest's `publisher_script` digest. That test is about the **publisher**, not the reply. Phase 12 edits the publisher, which makes it fail until Phase 13 republishes. That would be red inside the "reply stays green" test file. Move it to the publication tests (`tests/test_archive_assessment_applicability_authority_v2_publication.py`, which already has `test_real_published_files_validate` and will take the red window in Phase 12 anyway) or delete it if redundant there. Do this in commit 1 while the publisher is still unchanged, so it stays green.

### Pitfall 2: `validate_signoff` signature drift (see Summary)
Copying the live 4-arg form into the reply would silently freeze the reply on 2.0.2 semantics. Copy the 31addfa form. The D-02 test must call both with the same shape.

### Pitfall 3: Collection-time skips cannot fail
`needs_git` (`pytest.mark.skipif(reason is not None, ...)` evaluated at import), `gated(path)`, and `skipif(not REAL_RECORD.exists())` run when the test module is imported. Converting them to `pytest.fail` means moving the check into the test run: a fixture (`require_history`) or a `pytest.mark.usefixtures`. Replace the decorator form with `@pytest.mark.usefixtures('require_git_history')`. For `gated(path)` and the `exists()` skips, just delete the guard; the test fails naturally on a missing file (add an explicit `assert path.exists(), '<message>'` where the natural error is unclear).

### Pitfall 4: Opt-out and the CI guard interact
If the opt-out env var is set the helper calls `pytest.skip`, and the CI guard then turns that into a failure when `EMS_FAIL_ON_SKIP` (or `CI`) is set. That is the intended outcome, but test it: with both set, a missing-history case must end red. Document that CI must never set the opt-out.

### Pitfall 5: The mutation test can pass vacuously
If the test loads the builder module that the test file already imported at collection time, the mutation arrives too late and the test proves nothing. Always fresh-load the builder after installing the mutation (Pattern 3).

### Pitfall 6: Windows paths and `tmp_path`
Reply and notice tests use a module-level `tempfile.TemporaryDirectory()` because `tmp_path` was unusable on this machine. Other test files use `tmp_path`. The environment notes say pytest needs `--basetemp` pointing at a fresh directory (for example `.pytest-temp/p11`). Run through the orchestrator's PowerShell wrapper as the carried-forward note says. [CITED: STATE.md/CONTEXT carried-forward]

### Pitfall 7: Message wording and `match=` patterns
Existing tests match on strings such as `'shallow'`, `'differs from a fresh build'`, `'git show failed'`, `'reply schema differs'`. When copying `git_show`, keep `git show failed` in the `GitHistoryError` text. Improve it by using the full SHA and appending a hint such as `; fetch full history (git fetch --unshallow)` so D-07's "name the commit and path and say to fetch full history" is met by the validator itself. The publisher's copy uses `commit[:7]`; the frozen copy is allowed to differ.

### Pitfall 8: Frozen reply `resolve_record_commit` does not check the publication commit is an ancestor
It checks the record commit only. The test `test_publication_sha_is_ancestor_and_holds_authority` does check the publication commit. Under D-07, with `pytest.fail` replacing skip, this test is fine. Optionally add the publication-commit ancestor check to the validator (cheap and in the spirit of the notice's loop over all three commits); not required by the requirements. If added, the bytes of the reply do not change.

### Pitfall 9: Shared helper must be importable
There is no `tests/__init__.py`, no `conftest.py`, no `pytest.ini` or `pyproject.toml`. Under pytest's default `prepend` import mode the `tests/` directory is on `sys.path`, so a helper module there can be imported by name. Name it so it is not collected as a test file and does not match `-k archive_assessment` accidentally (for example `tests/aa_history.py`; it is not named `test_*`). Fixtures and hooks go in a new `tests/conftest.py`. A `conftest.py` is auto-loaded for every test in `tests/`, including non-archive tests, so any hook must be inert unless its env var is set.

## Skip inventory (D-07..D-09) and treatment

| File | Sites | Kind | Treatment |
|------|-------|------|-----------|
| `..._v2_publication.py` | L217 `prev_201_authority_bytes()` | pinned blob (31addfa) | `pytest.fail` with commit, path, fetch-history hint (this is FROZEN-03's headline case) |
| | L598, L602 (temp repo `git init`, `git commit`) | tool availability | `git unavailable` follows opt-out; failed `git commit` in a temp repo is a real failure, not a skip |
| | L636 `skipif(not REAL_AUTHORITY.exists())`, L662/L686/L1057 `skipif(not REAL_RECORD.exists())` | red-window guards | delete the guards (D-09) |
| | L665, 689, 705, 719, 732, 745, 1060 `if reason: pytest.skip(reason)` | `git_ready()` | shared helper (D-08) |
| `..._lineage_validation.py` | L53 (fixture `git unavailable`), L267, 293, 300, 313, 336-361, 380 | `git_ready()` / tool / 2.0.1 blob | shared helper; L361 is a pinned blob so `pytest.fail` |
| `..._governance_decisions.py` | L242-251 `needs_git`, L285/290 `skipif(not DECISIONS.exists())`, L352 (`eed4a5f`) | collection-time guard, red-window guard, pinned commit | fixture-based; delete the `exists()` guards; L352 `pytest.fail`. Note the `eed4a5f` check uses a short SHA; make the message name it |
| `..._governance_answers.py` | L63, 117, 123, 136, 145, 154 `'answers not yet filled'` | red-window guard | the committed answers are filled, so remove the skip; assert filled instead |
| `..._rule_proposals.py` | L161 `gated()`, L175 `git_out` `FileNotFoundError` | red-window guard, tool availability | remove `gated`; `git_out` follows opt-out |
| `..._rule_proposals_record.py` | L34-43 `git_ready`/`needs_git` | collection-time | fixture-based |
| `..._normalisation_claims.py` | L36-47 `git_ready` (checks V1_BASELINE and 2.0.1 commits), L72, L102 | history | shared helper |
| `..._demo3_..._reply.py` | L337, 349, 455, 532 | history | shared helper |
| `..._demo3_..._notice_2_0_2.py` | L131, 141 | history | shared helper |

Total: 48 `skip` hits in the grep, plus 7 `git_ready` definitions (publication L653, notice L61, reply L319, governance_decisions L242, lineage L28, normalisation_claims L36, rule_proposals_record L34). The lineage and normalisation_claims versions also check that specific commits exist; keep that logic by letting the shared helper take an optional commit list, or leave those two as thin wrappers that call the shared helper. De-duplicating is discretionary; a single `history_problem(commits=())` function plus `require_history(commits=())` (calls `pytest.fail` or, with the opt-out set, `pytest.skip`) is the lowest-risk shape.

`tests/test_archive_assessment_rule_proposals_record.py` `git_ready` compares `r.stdout == 'true'` after `git()` decodes and strips, so it works; there is no latent bug there.

### D-10 mechanism (recommendation)
Add `tests/conftest.py`:
```python
import os, pytest

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if os.environ.get('EMS_FAIL_ON_SKIP') == '1' and rep.skipped and not hasattr(rep, 'wasxfail'):
        rep.outcome = 'failed'
        rep.longrepr = f'skipped test treated as failure (EMS_FAIL_ON_SKIP=1): {item.nodeid}: {rep.longrepr}'
```
and in the workflow set `env: EMS_FAIL_ON_SKIP: '1'` on the `Archive-assessment tests` step (the explicit variable is clearer than keying on `CI`, which GitHub also sets for every job). A skip via `skipif` mark is reported at setup with `rep.skipped`, so this catches it. A cheaper alternative: add `-rs` and a shell step that greps the pytest summary for `skipped`. The hook is more reliable. Add a test that runs a one-test pytest subprocess (`pytest.main` via `subprocess` with a temp test file that skips) with the env var set and asserts a non-zero exit, and with it unset asserts exit 0. Name the test file `tests/test_archive_assessment_skip_guard.py` so `-k archive_assessment` picks it up. Use `--basetemp` and `-p no:cacheprovider` in that subprocess.

## Test rigor findings (D-12, D-13)

Weaknesses I confirmed by reading the tests, each with the fix.

Notice tests (`tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`):
- `REJECTS = (AuthorityError, jsonschema.ValidationError)` is used by `test_validate_rejects_tampered_cited_value`, `test_validate_rejects_tampered_constant`, `test_absolute_path_is_rejected`. Replace with specific expectations. For tampered cited values, the object-level call should raise `jsonschema.ValidationError` (pin consts are in the schema); `authority_sha256`/`manifest_sha256` zeros are valid to the schema, so those must reach the "differs from the values derived" `AuthorityError` message. Assert each one separately.
- `test_absolute_path_is_rejected` sets `lineage[0]['relative_path'] = 'C:\\temp\\x.json'`. The schema accepts any non-empty string there, so the guard that should fire is `contains_absolute` (`match='absolute path'`). Assert that message, so it fails if the guard is deleted (today the later derived-values mismatch would raise `AuthorityError` anyway and mask it).
- `test_validate_rejects_tampered_constant` calls `validate_notice()` and accepts any error; split by constant and assert the message each should produce (`'differs from a fresh build'`, `'not in the repository history'`, `'publication_commit'`, `'not an ancestor'`). Check what each really produces by running it once; do not guess.
- `test_digest_scope_error_fails_when_previous_authority_edited` already calls `digest_scope_error` directly, but accepts any `AuthorityError`. Add `match=` per mutation: `'global CRLF_TO_LF claim'` (mutation 1), `'differs from'` (mutation 2: `aa2_closure_sha256` changed), and for the popped key `old.get(old_key)` is `None` so the message is `'aa1_manifest_sha256 in 2.0.1 differs from aa1_manifest in 2.0.2'`. The `build_notice` half passes because `serve_edited` also trips `pinned_digest(SUPERSEDED_COMMIT...) != sup['sha256']` first, so it proves a different guard (the supersedes digest check). To make `build_notice` reach `digest_scope_error`, pass an edited `previous` directly (`build_notice(authority, edited, *rest)`) and note that `previous['authority_id']`/`version`/digest checks run first; use a mutation that leaves the digest check intact only when passing `previous` as an argument and recomputing is not applied. Simplest and honest: call `digest_scope_error` for the guard, call `build_notice` with the edited `previous` argument for the integration path, and assert on the message for each.
- `test_changed_row_blocks_no_decision_changed` tests `rows_differing` only (asserts `== 1`), so its name overstates what it checks. Add a `build_notice(authority, edited, ...)` call asserting `match='differ from the superseded version'`, or rename. Note that changing `controls[0]` state also changes the digest check path; pass `previous` as an argument so `pinned_digest(SUPERSEDED_COMMIT)` equals `sup['sha256']` still holds (it reads from git, not from the argument) and the row guard fires. Also add the other `rows_differing` guard (control set or `applicability_decision_ids` differ).
- `test_dual_role_statement_must_match_published_statement` already matches `'dual role'`. Keep.
- `test_forbidden_word_is_rejected` matches `'best'`. Keep; consider covering all five words by parametrising.
- Add the **committed-files test** (D-12, FROZEN-04): `def test_committed_notice_files_validate(capsys): require_history(); MODULE.validate_notice(); assert capsys.readouterr().out.strip() == 'PASS'` with no monkeypatching. `test_validate_notice_accepts_unmutated_notice_from_temp_files` uses temp copies written from the builder, so it does not prove the committed bytes pass. Also assert no `\r` in the committed files and that the committed JSON contains no absolute path, mirroring `test_real_reply_files_validate`.
- `test_mutation_count_and_closed_levels_come_from_frozen_bytes` asserts `'differs from the published manifest'` for the edited negative blob; fine. Its `V2.closed_schema_levels` and `V2.PREV_COMPARED_KEYS` use must become the builder's local ones, plus a D-02 equality check.
- `test_cli_flags_mutually_exclusive` parametrises `['--build','--validate']` and `['--emit-schema','--validate']` as expected-failure; after D-05 both are argparse errors for an unknown flag, which is still non-zero but for a different reason. Rewrite so that it asserts `--build` and `--emit-schema` are unrecognised (exit code 2) and that nothing was written.

Reply tests (`tests/test_archive_assessment_demo3_w1_req_001_reply.py`):
- `REJECTS` is used by 8 tests (`test_mutation_bad_aa4_format`, `_flipped_state`, `_altered_rule`, `_removed_and_extra_control`, `_sha_and_digest`, `_dual_role_text`, `_absolute_path`, `test_record_commit_format_checked_by_schema_only`). Same fix: specific exception class, plus `match=` for `AuthorityError` branches.
- `test_mutation_dual_role_text` and `test_mutation_absolute_path` suffer the same masking: `dual_role_statement` is only `minLength 1` in the schema, so the `'dual role statement differs'` guard is the one that must fire; `published_shape.authority_path` is any string in the schema so `'absolute path'` must fire. Assert those messages.
- `test_mutation_removed_and_extra_control` is mostly the schema (`minItems`/`maxItems` 21) and the id check; assert each exception class, since popping one control trips the schema first and the id-set check second only if the schema allowed it. Add one case for the id-set guard (21 controls but a swapped id) to reach `'reply controls differ from the 21 requested controls'`.
- `test_real_reply_files_validate` already runs `MODULE.validate_reply()` on the committed files; it is the D-13 committed-files test. Keep it; add `require_history()`.
- `test_validate_independent_of_live_version` is replaced or extended by Pattern 3. Delete the narrow version, or keep it as one case in the new test.
- `test_validate_rejects_tampered_constant` (6 params) should assert the specific `AuthorityError` text per parameter.

For FROZEN-04 "each test goes red when the check it is named for is broken": the planner should include, for each notice and reply negative test, a one-line plan step to confirm the expected message by running it once against the unmodified validator (the plan's verification step), and optionally a local manual sabotage run of the three highest-value guards (record binding, `digest_scope_error`, `contains_absolute`). The mutation-sweep meta-test is deferred, so do not automate this.

## State of the Art

| Old approach | Current approach | Impact |
|--------------|------------------|--------|
| Builders exec the live publisher file and read `V2.*` | Local literals and copies, proven equal to the frozen publisher by a test-only blob exec | Publisher edits in Phase 12 cannot change the historical results |
| Builders regenerate the schema and compare bytes | Compare committed schema to the git blob at a pinned commit | One fewer live-derived value |
| Skips for missing history | `pytest.fail` with the commit and path; opt-out env var for local use; CI converts any skip to a failure | A shallow clone cannot make the suite look green |

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | The pytest hook form `pytest_runtest_makereport(hookwrapper=True)` converting `rep.outcome` works for `skipif`-mark skips on the repo's installed pytest | D-10 | Hook would not fire; fall back to `-rs` plus summary grep. Verify by running the skip-guard test once. [ASSUMED, from pytest conventions; not tested this session] |
| A2 | Default pytest `prepend` import mode puts `tests/` on `sys.path` so a helper module in `tests/` is importable by name | Pitfall 9 | Helper import fails; fall back to putting helpers in `conftest.py` fixtures only. [ASSUMED] |
| A3 | Removing `--push-check` is acceptable to the user (D-06 is discretionary) | D-06 | Low; the plan records it and keeping it is a small diff |
| A4 | The expected exception messages listed in the rigor section are directional; the plan must confirm each by running | Test rigor | Wrong `match=` strings; caught by the first test run |

## Open Questions

1. **Baseline (resolved).** `pytest tests -k archive_assessment -p no:cacheprovider -q -rs --basetemp=.pytest-temp/p11-research` gave `770 passed, 7 deselected` in about 237 s, with **zero skips** at HEAD b97e805. So the D-10 guard can be switched on without first fixing any skip that fires in a full clone. The suite takes about 4 minutes, so use `-k` on the two demo3 files for per-task checks and the full run per commit.

2. **Should `validate_reply`/`validate_notice` also check the schema commit is an ancestor of HEAD?** CONTEXT D-04 says yes (`cat-file -e` and ancestor checks "as with the other anchors"). Plan it in `resolve_record_commit` (notice already loops over its three commits; add the schema commit to that loop; the reply needs the same loop for the publication and schema commits).
3. **The notice schema commit (`052f0f1`) is the same commit that added the notice files.** Because the notice builder's own commit also is the schema commit, there is no circularity problem (the schema is read from git, not from the working tree), but the constant must be written into the builder before that history can be checked: it is already in history, so no issue. Just do not try to use the commit of the change that introduces the constant.

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python `.venv` | all | yes | `.venv/Scripts/python.exe` (3.12 per CLAUDE.md) | -- |
| git, full history (not shallow) | all pinned-blob reads | yes | `git rev-parse --is-shallow-repository` returned `false`; 31addfa, ae15c74, 7debe4a, e781f08, 052f0f1 resolve and are ancestors of HEAD | -- |
| Bash tool | research probes | worked this session | -- | PowerShell per STATE.md |
| pytest, jsonschema, PyYAML | tests and publisher blob exec | yes (probe imported them via the blobs) | -- | -- |

Missing dependencies: none.

## Security Domain

`security_enforcement` is on (ASVS level 1). The phase has no network, auth, session or crypto code. Applicable items:

| ASVS category | Applies | Control |
|---------------|---------|---------|
| V5 Input validation | yes | `jsonschema` on committed JSON; `git_show` validates the 40-hex commit and repo-relative path (copy verbatim, including `bad_rel`, which rejects `..`, absolute and drive paths) |
| V6 Cryptography | no new use | SHA-256 via `hashlib` only |
| V12 Files and resources | yes | Builders must not write repo files after D-05; test exec of a git blob is test-only and confined to the repo's own history |

Threat patterns:
| Pattern | STRIDE | Mitigation |
|---------|--------|------------|
| Command injection through commit or path into `git show` | Tampering | `subprocess.run([...])` list form (no shell), commit regex, `bad_rel` check; keep both when copying `git_show` |
| Silent trust of a missing history (shallow clone) | Repudiation / Spoofing | Fail by default (D-08); CI never sets the opt-out; CI skip guard |
| Executing code from git at runtime | Tampering | Not done; exec only in tests (D-01/D-02) |

## Don't forget (checks the planner should add to every plan)

- After each commit: `git diff <commit-or-HEAD~> -- scripts/publish_archive_assessment_applicability_authority_v2.py docs/DEMO3_W1_REQ_001_REPLY.md registry/archive_assessment_demo3_w1_req_001_reply.json docs/DEMO3_W1_REQ_001_NOTICE_2_0_2.md registry/archive_assessment_demo3_w1_req_001_notice_2_0_2.json schemas/archive_assessment_demo3_w1_req_001_reply.schema.json schemas/archive_assessment_demo3_w1_req_001_notice_2_0_2.schema.json` is empty (SC4, frozen bytes).
- Run `python scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate` and the notice `--validate`, plus the other three CI validators, and `python -m pytest tests -k archive_assessment -p no:cacheprovider -q --basetemp=.pytest-temp/p11-N` after each commit.
- `git status` must still show `.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json` and the untracked files untouched; stage by explicit path.
- The reply and notice test files contain the only importers of `MODULE.V2`; grep for `V2` after the edit and expect zero hits in the builders and only the deliberately separate live-publisher loads in tests.
- Both builders are standalone scripts run as `python scripts/<file> --validate`; after removing `importlib.util` and `V2`, confirm they run from a clean working directory and with `python -I`.

## Sources

### Primary (HIGH confidence)
- Repo files read this session: `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`, `scripts/publish_archive_assessment_applicability_authority_v2.py` (live, plus blobs at 31addfa and ae15c74), both demo3 test files, skip sites in the other seven `test_archive_assessment_*.py` files, `.github/workflows/ems-validate.yml`.
- Executed probe (scratchpad script) exec-ing both pinned publisher blobs: confirmed `VERSION`, presence of `PREV_COMPARED_KEYS`, `validate_signoff` arity (2 vs 4).
- `git show <sha>:<path> | cmp` for schema bytes at 7debe4a, e781f08, 052f0f1; `git merge-base --is-ancestor` checks; `git ls-files --eol`.
- `.planning/phases/11-frozen-validators/11-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `CLAUDE.md`.

### Secondary / Tertiary
- pytest hook and import-mode behaviour: from general knowledge, tagged `[ASSUMED]` (A1, A2); verify when the skip-guard test is first run.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH (nothing new)
- Architecture (what to copy, what the blobs contain, commit constants): HIGH (read and probed)
- Skip inventory: HIGH from grep; line numbers are as of HEAD b97e805 and may shift by a few lines
- Test-rigor message expectations: MEDIUM (reasoned from source; confirm each `match=` by running)
- D-10 hook: MEDIUM (A1)

**Research date:** 2026-11-14
**Valid until:** until the first publisher edit (Phase 12) or any change to the two builders; the repo is the only moving part.
