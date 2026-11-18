# Phase 16: Test Robustness and Review Closure - Research

**Researched:** 2026-11-18
**Domain:** pytest test hardening, a standalone Python builder (behaviour-only fixes), planning bookkeeping (git/CRLF staging)
**Confidence:** HIGH (all findings read from the actual code at HEAD 9a10810). Two items cannot be run locally (see Environment) and are MEDIUM until CI runs them.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** The 2.0.3 notice was sent to Hayes at `91d8847`. Its generated text is immutable. Phase 19 (NOTICE-05) records the send commit; Phase 16 only captures the fact.
- **D-02:** Behaviour-only fixes in `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`. Every fix leaves `--build` output byte-identical to the committed `registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json`, `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md`, `schemas/archive_assessment_demo3_w1_req_001_notice_2_0_3.schema.json`. The plan includes an explicit gate (rebuild, then `git diff --exit-code` on those three files). In scope: 14 IN-01 (remove `pinned_raw_digest`; add `EXPECTED_LINEAGE_COMMIT`, fail closed on mismatch; decide whether `CATALOG_COMMIT` stays), 14 IN-02 (wrap malformed-input paths in `AuthorityError`; match `pub.GitHistoryError` by class; keep "pinned baseline" context), 14 IN-03 (`--build` writes the schema too, atomically, before validating), 14 IN-04 (`copy.deepcopy` the rule dicts), 14 IN-05 (`onexc=`; `run()` parses `r.stdout` only and asserts `returncode`; confirm/close or strengthen the always-true containment assertion), 15 IN-02 (remove duplicated hint test, fold the `core.longpaths` check into `test_git_show_error_names_full_sha_and_fetch_hint`), 15 IN-03 (OSError hint: "git unavailable: {e}; install git and ensure it is on PATH", no fetch advice).
- **D-03:** 15 IN-01 (`C:\ems` in the sent registry JSON) is closed for 2.0.3 with the reason "sent text is immutable" and moved to Phase 19. The 2.0.4 notice builder must avoid absolute-path example text, and its `contains_absolute` must scan the whole string. GATE-15 requirement text and traceability are amended (D-10).
- **D-04:** No publisher edits in Phase 16. 12-REVIEW IN-01, IN-02, IN-03, IN-04, plus IN-06's "move the `lf_digest(SCRIPT)` check to just after the manifest load", are recorded as DEFERRED-17.
- **D-05:** 12 IN-05 (literal pathspecs) is closed as superseded by SEC-04; 12 IN-06's decisions-builder scope as superseded by SEC-02, with cross-references.
- **D-06:** 12 IN-07 is split. Test-only parts are fixed in Phase 16: the reply test's `cat_exc` case matches `'cannot check whether the frozen commit'`; `test_at_pin_binding_reads_supersedes_from_authority` drops the source grep and keeps its behavioural assertion. The reply-builder message (regex-failure branch) is CLOSED (frozen, byte-unchanged).
- **D-07:** D-10 baseline test: mode from the record state. In the clone read the publication record; if it names the superseded version (from the authority's `source_lineage.supersedes`, not a hard-coded constant) run `--validate --at-pin`, otherwise plain `--validate`. Accept `PASS` or a JSON object with `status == 'PASS'`.
- **D-08:** Overlay the working-tree publication paths: after `git clone --shared`, copy the working-tree versions of the 10 D-05 publication paths and the publisher script into the clone and commit them there. Unrelated working-tree changes are never copied. `outcome()` uses `encoding='utf-8', errors='replace'`, takes the result from the last non-empty line of `stdout` only, keeps `stderr` in the failure message.
- **D-08a:** From Phase 17's first publisher edit this baseline goes red with the other real-file tests; it joins the Phase 17 accepted red-set inventory and closes at the 2.0.4 publication. Do not weaken it to equality-only.
- **D-09:** One closure ledger `.planning/phases/16-test-robustness-and-review-closure/16-REVIEW-CLOSURE.md`: one row per item (11 IN-08, IN-09; 12 IN-01..IN-07; 14 IN-01..IN-05; 15 IN-01..IN-03); columns item, disposition (`FIXED` / `CLOSED` / `DEFERRED-17` / `DEFERRED-19` / `SUPERSEDED-BY-SEC-0x`), reason, evidence (test name and commit). Historical REVIEW files are not edited.
- **D-10:** Edit `.planning/REQUIREMENTS.md`: reword GATE-13 and GATE-15 IN-01, add traceability rows in Phase 17 and Phase 19, adjust ROADMAP success criteria for Phases 16/17/19, in the same commit as BOOK-02 (V2-01/V2-02 rows already present; confirm).

### Claude's Discretion
- BASE-02 deep-root `git_show` test mechanics: on Windows with a deep root assert that `Filename too long` reproduces without `--` (with `core.longpaths=false`) and fail loudly otherwise; on other platforms assert the `--` behaviour only, no MAX_PATH claim; no skips under `EMS_FAIL_ON_SKIP=1`; depth threshold, the fallback for a clone root >= 240 chars, and how the test forces a deep root are left to the planner/researcher.
- BASE-04 wording in `tests/aa_history.py` (test helper, not a frozen builder): fix both items there; record whatever lands only in a frozen builder as CLOSED.
- BOOK-01: 11-13 SUMMARY files show `M` only because of line endings. Add `requirements-completed` frontmatter matching v1.2.0 traceability; stage by explicit path so only the frontmatter change is committed. Planner decides add vs rename for files that use `requirements:`.
- Plan and commit grouping, test names.

### Deferred Ideas (OUT OF SCOPE)
- Phase 17: 12 IN-01..IN-04 publisher fixes; IN-06 digest-check placement; IN-05/IN-06 scope via SEC-04/SEC-02; adding the D-10 baseline to the accepted red-set inventory.
- Phase 19: 15 IN-01 (no absolute-path example text in the 2.0.4 notice, whole-string `contains_absolute`); NOTICE-05 records the 2.0.3 send commit `91d8847`.
- Out of scope (frozen): the reply-builder regex-failure message (12 IN-07 builder part).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BASE-01 | D-10 baseline passes at the pin commit and later commits | Section "D-10 baseline test": mode chosen from the record vs `source_lineage.supersedes`; at current HEAD the record names 2.0.3 so plain mode is chosen |
| BASE-02 | Deep-root `git_show` test is not tautological | Section "BASE-02": real-git no-`--` reproduction assertion on win32, equality-only elsewhere |
| BASE-03 | D-10 test checks the working tree; UTF-8, stderr separate | Overlay of 10 `publication_paths()` + publisher; `outcome()` rewrite |
| BASE-04 | History hint and shallow-check wording | Already fixed in commit 8dd3778 (12-01). Phase 16 = verify, add a wording test, ledger FIXED |
| GATE-13 | 12-REVIEW IN-01..07 dispositions | Ledger rows: IN-01..04 DEFERRED-17, IN-05 SUPERSEDED-BY-SEC-04, IN-06 split, IN-07 test parts FIXED / builder part CLOSED |
| GATE-14 | 14-REVIEW IN-01..05 fixed | Section "Builder fixes", per-item exact code and byte-identity argument |
| GATE-15 | 15-REVIEW IN-02, IN-03 fixed; IN-01 re-routed | Section "Builder fixes" and "Hint tests" |
| BOOK-01 | `requirements-completed` frontmatter on 11-13 SUMMARY files | Section "BOOK-01": per-plan mapping table and safe staging |
| BOOK-02 | V2-01/V2-02 listed as deferred | Confirmed present in REQUIREMENTS.md (lines 73-74, 111-112); no edit needed |
</phase_requirements>

## Summary

Phase 16 is a test, bookkeeping and one-builder-behaviour phase. The publisher (`scripts/publish_archive_assessment_applicability_authority_v2.py`) stays byte-unchanged, the frozen reply and 2.0.2 notice builders stay byte-unchanged, and the sent 2.0.3 notice output stays byte-identical. Nothing in the repo pins the 2.0.3 notice builder's digest (no test, manifest or CI step; CI only runs it with `--validate`), so builder edits cannot break a hash gate.

Three findings change the plan shape. (1) **BASE-04 is already implemented**: commit `8dd3778` (12-01) already rewrote `HINT` ("EMS_ALLOW_NO_HISTORY=1 only skips tests guarded by require_history, and tests that read pinned history directly still fail") and the shallow check already reports unrecognised output verbatim (`printed {out!r}`, message "cannot tell whether ... is shallow"). The 11-REVIEW text is stale. Phase 16 should verify, add one small wording assertion, and ledger both rows `FIXED` with evidence `8dd3778`. `aa_history.py` is imported only by tests and conftest, never by a builder. (2) **15 IN-02's duplicate test no longer exists in the shape the review described**: the review's real-git duplicate was replaced; what remains is the parametrised mocked test `test_git_show_error_hint_names_long_paths_only_when_git_reports_them` (line 744), which is the only owner of the positive `Filename too long` hint. Fold it into `test_git_show_error_names_full_sha_and_fetch_hint` (line 346) rather than deleting coverage. (3) **The deep-root test's real reproduction hinges on git's stat of the `<sha>:<path>` string**, not on the checkout tree, so a root of about 100+ characters already triggers it; the existing loop produces a root of about 150-170 characters.

**Primary recommendation:** Execute as four small commits: (a) tests only (BASE-01/03 overlay test, BASE-02, BASE-04 wording assertion, 12 IN-07 test parts, 15 IN-02 fold, 14 IN-05 test nits); (b) builder behaviour-only fixes with the byte-identity gate; (c) the closure ledger plus REQUIREMENTS/ROADMAP edits (GATE-13/15 reword, BOOK-02 confirm); (d) BOOK-01 SUMMARY frontmatter, staged by explicit path. Run clone-based tests through CI (`workflow_dispatch`) because local `git clone` crashes.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| D-10 baseline check (clone + validate) | Test layer (`tests/`) | Publisher CLI (read-only) | The publisher is the system under test; no publisher edit allowed |
| Notice builder behaviour fixes | Standalone builder script | Test layer | Output bytes are frozen; only behaviour on error/write paths changes |
| History hint wording | Test helper (`tests/aa_history.py`) | Skip-guard tests | Already implemented; verify only |
| Review closure ledger and requirement text | Planning docs | Verifier | No code path; verifier checks ledger vs GATE-13/14/15 |
| SUMMARY frontmatter | Planning docs | git staging | CRLF working copy vs LF index; stage explicit paths |

## Standard Stack

Existing stack only; no new packages. `[VERIFIED: CLAUDE.md, ems-validate.yml]`

| Library | Version | Purpose |
|---------|---------|---------|
| Python | 3.12 (local 3.12.10, CI 3.12) | `shutil.rmtree(onexc=)` exists from 3.12, safe on both |
| pytest | local 8.4.2/9.1.1 caches seen; CI unpinned | tests |
| jsonschema | 4.26.0 pinned in CI | schema validation |
| git | 2.54.0.windows.1 local; ubuntu-latest in CI | seam under test |

**Package Legitimacy Audit:** No external packages are installed or recommended in this phase. Nothing to audit.

**Installation:** none.

## Architecture Patterns

### Flow (D-10 baseline test after the fix)

```
REAL_ROOT working tree --(read)--> publication_paths() (10) + publisher script
        |                                   |
        |   git clone --shared (HEAD)       |  LF-normalise bytes
        v                                   v
   clone/ (HEAD checkout) --overlay copy--> clone/  --git add (literal) --> diff --cached --quiet?
                                                                              | yes: no-op, skip commit
                                                                              | no : git commit (identity via -c)
        v
   read clone's publication record + REAL authority source_lineage.supersedes
        |-- record names superseded version --> run --validate --at-pin
        |-- otherwise ----------------------> run --validate
        v
   outcome(): rc, last non-empty STDOUT line; PASS or JSON {"status":"PASS"}; stderr kept for the message
        v
   mutate live catalog (overwrite, delete) --> outcome unchanged
```

### Pattern: D-10 test (BASE-01, BASE-03) - exact current code and the target

Current code (`tests/test_archive_assessment_lineage_validation.py` lines 357-378): clones HEAD with `git -c core.longpaths=true clone --shared -q`, sets `core.longpaths true`, `outcome()` runs plain `--validate` with `text=True` (locale codec) and returns `(returncode, last line of stdout+stderr)`; asserts `before == (0, 'PASS')`; then overwrites and deletes `clone/MODULE.CATALOG_REL` and asserts the outcome is unchanged.

Facts needed to implement the target:
- **The 10 D-05 publication paths are not a constant**: they are `MODULE.publication_paths()` (publisher line 596): `rel(AUTHORITY)`, `rel(SCHEMA)`, `rel(SIGNOFF)` plus `generated/archive-assessment/ems-aa3-v2/<n>` for `N_MATRIX, N_SEMANTIC, N_NEGATIVE, N_TRACE, N_CERT, N_REPORT, N_MANIFEST`. The publisher is `rel(MODULE.SCRIPT)`. The publication record (`rel(MODULE.PUBLICATION_RECORD)`) is NOT among them and stays as committed in the clone. `[VERIFIED: publisher lines 596, 795]`
- **Mode decision**: the publisher itself (line 841) treats the record as "superseded" when `record['authority_id'] == sup['authority_id'] and record['version'] == sup['version']` with `sup = authority['source_lineage']['supersedes']`. Mirror that exactly: read the authority from the working tree (`REAL_ROOT / MODULE.rel(MODULE.AUTHORITY)`), read the record from the clone, choose `--at-pin` iff they match. At-pin mode additionally requires `record['publication_commit'] == sup['commit']` and `authority_sha256 == sup['sha256']`, which hold when the record is genuinely the superseded one.
- **At current HEAD** the record is `EMS-AA3-...-2.0.3` / version 2.0.3 / `publication_commit 1544dc19...`, and the authority is 2.0.3 whose `supersedes` is 2.0.2 (`ae15c74...`). So the test picks plain mode. Plain mode at HEAD passes today (CI at `91d8847` ran the validators green): it needs `git_not_shallow`, `git_is_ancestor(pub, HEAD)`, byte equality `git_show(pub, p) == git_show(HEAD, p)` for all 10 paths, and `check_tree_matches_head`. `[VERIFIED: publisher lines 830-860, 13-01 SUMMARY]`
- **Overlay of an unchanged tree is a no-op**: after the LF-normalised copy, `git add` produces an empty index diff; guard with `git diff --cached --quiet` (exit 0 means nothing to commit, skip `git commit`). Never call `git commit` unconditionally, "nothing to commit" returns 1.
- **Line endings**: `git ls-files --eol` shows the publisher and many files as `i/lf w/crlf` on this machine (core.autocrlf=true). All 10 publication paths carry `text eol=lf` in `.gitattributes` (authority, schema, signoff, `generated/archive-assessment/ems-aa3-v2/**`); the publisher script has no eol attribute. Plain mode compares raw `git_show(pub, p)` to `git_show(head, p)` (byte equality, not LF-normalised), so the overlay commit must store LF blobs. Copy `data = (REAL_ROOT/rel).read_bytes().replace(b'\r\n', b'\n')` and commit with `-c core.autocrlf=false`; then the blob equals the committed LF blob.
- **Git identity and signing in the clone**: use per-command flags, no config writes: `git -c user.name=t -c user.email=t@t -c commit.gpgsign=false -c core.autocrlf=false -C`/`cwd=clone`. The existing `git(*args, cwd=...)` helper in the test file accepts `cwd`. Use `--literal-pathspecs` on `add`.
- **`--validate --at-pin` prints** one JSON line `{"status": "PASS", "mode": "AT_PIN", "deferred": ["PUBLICATION_RECORD_BINDING: ..."]}`; plain prints `PASS`. `[VERIFIED: publisher line 825]`
- **`outcome()` target**: `subprocess.run([...], cwd=clone, capture_output=True, text=True, encoding='utf-8', errors='replace', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})`. Set `PYTHONIOENCODING`, otherwise a child Python on Windows writes pipes in the ANSI codepage and the UTF-8 decode only masks the problem (this was the 13-REVIEW IN-03 root cause). Take the last non-empty line of `r.stdout`; status = `'PASS'` if the line equals `PASS`, or `json.loads(line)['status']` when it parses as an object with a `status` key (guard JSON errors: a non-JSON non-PASS line becomes the raw line). Return `(r.returncode, status_or_line)`. Put `r.stderr` into the assert message only.
- **Both-modes honesty**: assert the baseline `before == (0, 'PASS')`, assert the mode chosen is the expected one for the record (e.g. at HEAD plain), and keep the live-catalog overwrite/delete comparison `after == before`.
- **`require_history(REAL_ROOT, commits=PINNED_COMMITS)`** already guards the test; keep it (assert, never skip, under `EMS_FAIL_ON_SKIP=1`).
- **Red window (D-08a)**: after Phase 17's first publisher edit plain mode compares `pub` vs overlaid HEAD, so this test fails until the 2.0.4 publication. Do not weaken it. Document this in the test with a short comment and in the ledger row.

### Pattern: BASE-02 deep-root test

Current state (`tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` lines 714-736, quick task 261118-cgq): no skips; builds `clone = TMP/deep/(d*20)/.../c` by appending 20-char directories while `len(clone)+1+len(long_rel) <= 270`, with `long_rel = generated/archive-assessment/ems-aa3-v2/<N_NEGATIVE>` (about 120 characters); falls back to `TMP/deep/c` if the root would be >= 240 characters; clones `--shared --no-checkout` with default config, sets `core.longpaths false`; asserts `MODULE.git_show(PUB, long_rel) == git show PUB:long_rel -- (cwd=clone)`. The executor's "reproduces without `--`" assertion was removed in 72a5c06 because it was conditional and could never fail, so the test is currently equality-only and would also pass on a root where the original bug never reproduced.

What actually triggers the failure `[CITED: 15-REVIEW-FIX.md and builder test fixtures: "failed to stat 'eeee:registry/x.json': Filename too long"]`: without `--`, git tries to stat the string `<sha>:<rel>` relative to the cwd to resolve ambiguity between a revision and a filename. The length that matters is `len(cwd) + 1 + len(f'{PUB}:{long_rel}')` (41 + 120 = about 161), not the working-tree file. So a root longer than about 100 characters, with `core.longpaths=false`, reproduces it; the executor reproduced it at a root of 157 characters (git exit 128). `[VERIFIED: 261118-cgq-SUMMARY.md]`

Recommended mechanics:
1. Only the win32 branch claims MAX_PATH coverage. Compute the root as now (target about 150-200 characters). Assert as preconditions: `len(str(clone)) + 1 + len(f'{PUB}:{long_rel}') > 260` and `len(str(clone)) <= 200` (cap: `--shared` clone writes `.git/hooks/*.sample`, about 34 chars under `.git`, and `git clone` with `core.longpaths=false` fails if any created path exceeds 259; 240 is too generous, 200 leaves margin).
2. On win32, run real git without `--`: `subprocess.run(['git', '-c', 'core.longpaths=false', 'show', f'{PUB}:{long_rel}'], cwd=clone, capture_output=True)` and `assert r.returncode != 0 and b'Filename too long' in r.stderr`, with a failure message that says the deep-root test did not reproduce the failure. Then assert `MODULE.git_show(PUB, long_rel)` equals the `--` form. Use `pytest.fail`/`assert`, never `pytest.skip` (conftest turns skips into failures under `EMS_FAIL_ON_SKIP=1`).
3. If `TMP` is already so long that the controlled root would exceed the cap on win32, fail loudly with a message naming the length ("shorten TEMP"), do not fall back silently to a shallow root (that would reintroduce the tautology). The 240 fallback becomes dead code.
4. Non-Windows branch: shallow clone root under TMP, assert only equality with the `--` form; no MAX_PATH claim in the test name, comment or message. `sys.platform == 'win32'` selects the branch (no skipif).
5. Keep the mocked `test_git_show_passes_double_dash` (line 702) which asserts `argv[-1] == '--'` on every platform, so the `--` regression is guarded on Linux CI too.

Caveat: if Windows is configured with `LongPathsEnabled=1` plus a long-path-aware git, the reproduction assertion could fail on that machine. That is the intended "fail loudly" behaviour per BASE-02, but it is untested here (local clone crashes), so the first real evidence is the operator's run on a working git or CI. Record this in the plan as a verification note. `[ASSUMED]` that this machine reproduces (the executor's run did at 157 characters).

### Pattern: builder behaviour-only fixes (GATE-14, GATE-15)

All lines in `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` (607 lines, working copy CRLF, index LF). Current code and the fix, each with the byte-identity argument. `--build` output is a pure function of `load_inputs()` + `build_notice()` + `render_markdown()` + `schema()`; none of the fixes below touch those return values.

| Item | Current code (line) | Fix | Output bytes |
|------|---------------------|-----|--------------|
| 14 IN-01 | `pinned_raw_digest` defined at 165-167, no callers (grep across scripts/tests: none). `CATALOG_COMMIT` defined at 48, unused in the builder (tests use it at line 216). `lineage_entries` line 224: `at = e.get('commit', NOTICE_PUBLICATION_COMMIT)` | Delete `pinned_raw_digest`. Add `EXPECTED_LINEAGE_COMMIT = {'catalog_reference': CATALOG_COMMIT, 'v1_baseline': CATALOG_COMMIT, 'supersedes': PREVIOUS_2_0_2_COMMIT}` and after computing `at` raise `AuthorityError(f'source_lineage {key}: commit {at} differs from the expected commit')` unless `at == EXPECTED_LINEAGE_COMMIT.get(key, NOTICE_PUBLICATION_COMMIT)`. Keep `CATALOG_COMMIT` (now used). The lineage entry must also stay without a `commit` for the 4 other keys; if an entry carries a `commit` other than the pin, that now fails closed | Unchanged. Verified from the committed authority: `catalog_reference` and `v1_baseline` have commit `62a8955dc28d9458cd1167fad314926e057c31fc` (= `CATALOG_COMMIT`), `supersedes` has `ae15c7458e49c8f55cc58c61bab04bc716aa9892` (= `PREVIOUS_2_0_2_COMMIT`), the other 4 keys have no `commit` (default to the pin). Existing test `test_lineage_entries_recomputes_all_seven` (line 216) already asserts `recomputed_at` per key |
| 14 IN-02 | `_WRAPPED` (290) catches `ValueError, OSError, KeyError, TypeError, AttributeError, ImportError, jsonschema.*`. Class matched by name at 300, 319, 325 (`type(e).__name__ == 'GitHistoryError'`); line 319 re-raises `GitHistoryError(str(e))`, dropping the "pinned baseline" context. `load_inputs` (335-) and `build_notice` read `record['manifest_sha256']` (348), `a['relative_path']`, `pinned_json` (JSONDecodeError/UnicodeDecodeError, both ValueError subclasses) with no domain wrapping | Wrap bodies of `load_inputs` and `build_notice` in `except AuthorityError: raise` then `except (ValueError, KeyError, TypeError) as e: raise AuthorityError(f'... {type(e).__name__}: {e}') from e`. Use `isinstance(e, pub.GitHistoryError)` in the second and third try blocks where `pub` is bound; at 300 `pub` is not bound (load failed) so guard with a try or keep `AuthorityError` pass-through. Line 319: `raise GitHistoryError(f'pinned baseline rejected the unmutated inputs: {type(e).__name__}: {e}')` | Unchanged (error paths only) |
| 14 IN-03 | `main` (591-604): `--build` writes `NOTICE_JSON`/`NOTICE_MD` (602) then `validate_notice()` (603); `--emit-schema` writes the schema without validating | In `--build`: compute `notice`, `json_text`, `md_text`, `schema_text = jtext(schema())` in memory; `jsonschema.Draft202012Validator.check_schema(schema())` and `validate_notice_object(notice, inputs)` (already in-memory) first; then write each file to `path.with_name(path.name + '.tmp')` (`newline='\n'`, UTF-8) and `os.replace` all three; then call `validate_notice()` as the post-check. A failure before the replace step leaves nothing written. `dump()`/`write_text()` helpers (86-91) currently write in place; add an atomic variant, keep the old ones for `--emit-schema` | Unchanged: the committed schema already equals `schema()` (checked by `validate_notice` line 584), JSON via `jtext`, Markdown via `render_markdown`, same LF writes |
| 14 IN-04 | line 423 `'rule': r['not_applicable_rule']` (inside a dict comprehension in `build_notice`; line 398 only tests `is None`) | `copy.deepcopy(r['not_applicable_rule'])`; add `import copy` | Unchanged (equal value). `rule_text(r['not_applicable_rule'])` can keep reading the source |
| 14 IN-05 | tests: `rmtree(..., onerror=_rm_readonly)` at 643, 719, 736 (`_rm_readonly(func, path, exc)` at 634); `run_in_clone` (655-658) joins `stdout + stderr`; `test_pinned_run_paths_stay_in_temp_materialisation` (170-192) asserts temp dir is outside `ROOT` (always true) | `onexc=_rm_readonly` (3-arg callback signature is compatible; local and CI are 3.12). `run_in_clone`: `lines = stdout.splitlines()` filtered, return `(r.returncode, lines[-1] if lines else '')`, with stderr in a message. The WR-01 live-tamper containment case already exists as `test_live_data_file_edit_does_not_change_notice` (683) and `test_live_publisher_and_decisions_builder_edit_does_not_change_notice` (674) plus the module-root and `git_run` assertions at 187-192: record the always-true assertion at 183 as "confirmed: closed by tests 674/683 and 187-192" in the ledger, or delete the redundant `not ... is_relative_to(ROOT)` half | Test-only |
| 15 IN-02 | line 744 `test_git_show_error_hint_names_long_paths_only_when_git_reports_them` (parametrised mock, 3 stderr cases) repeats `'fetch full history (git fetch --unshallow)'` from line 346; the review's original real-git duplicate is already gone | Fold the three-case mocked check into `test_git_show_error_names_full_sha_and_fetch_hint` (one test owns the fetch hint, the negative `core.longpaths` assertion for real git "invalid object", and the positive case for `Filename too long`), then delete the line 744 test. Do not drop the positive `Filename too long` case, it is the only owner of `hint += '; on Windows set core.longpaths true ...'` (builder line 106) | Test-only |
| 15 IN-03 | line 102: `except OSError as e: raise GitHistoryError(f'{relative_path}@{commit}: git unavailable: {e}; fetch full history (git fetch --unshallow)')` | `...git unavailable: {e}; install git and ensure it is on PATH`. Add a test: monkeypatch `MODULE.subprocess.run` to raise `FileNotFoundError('git')`; `pytest.raises(GitHistoryError, match='git unavailable')`; assert `'install git' in msg` and `'fetch' not in msg` | Unchanged (error path; never reaches output) |
| 15 IN-01 | `C:\ems` is in the sent registry JSON (builder string near line 427, `prerequisites`); `contains_absolute` (92-96) only checks the start of a string | **Do not change**: D-03 closes it for 2.0.3 ("sent text is immutable"), DEFERRED-19. Do not touch `contains_absolute` here either (changing it to scan the whole string would make the committed JSON fail `validate_notice_object` line 562) | Unchanged |

**Byte-identity gate (D-02)** - recommend two steps, because `git status` on this machine reports `M` for these files without a real diff (line-ending/stat noise; `git ls-files --eol` shows `i/lf w/lf` for all three notice outputs): (1) `python scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py --build` then `--validate` prints `PASS`; (2) `git diff --exit-code -- registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md schemas/archive_assessment_demo3_w1_req_001_notice_2_0_3.schema.json` exits 0, plus an explicit byte compare of each working file with `git show HEAD:<path>` (for example a tiny Python one-liner comparing `read_bytes()` with `subprocess.check_output(['git','show','HEAD:'+p])`) so a spurious auto-refresh cannot hide a change. Also run `--validate` in CI (already present, line 100 of the workflow). Because `--build` now writes the schema, the gate must run before `--build` mutates anything: take the `git show HEAD:` snapshot first.

Builder edit hazards:
- The builder working copy is CRLF while the index is LF; use an editor that preserves line endings, then confirm `git diff --stat` for the file shows only intended hunks (git normalises on add).
- The pinned publisher's `AuthorityError` is a different class from the builder's `AuthorityError`; both subclass `ValueError`, so the pinned one lands in `_WRAPPED` via `ValueError`. Do not "simplify" `_WRAPPED`.
- Do not wrap `jsonschema.ValidationError` in `validate_notice_object`: the test at line 402 expects it raw.
- No digest pins the builder: `grep` of tests, registry, CI shows only `--validate` invocation (workflow line 100) and `SCRIPT_REL` string use. `[VERIFIED]`

### Pattern: 12 IN-07 test parts (D-06)

- Reply test `tests/test_archive_assessment_demo3_w1_req_001_reply.py` line 386: `({'cat_exc': OSError('git gone')}, 'in the repository history')`. The frozen builder message at `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:354` is `cannot check whether the frozen commit {sha} is in the repository history: {e}`, so change the match to `'cannot check whether the frozen commit'`. `[VERIFIED]`. The test file is not a frozen builder; the 11-CONTEXT freeze covers the builders only (reply and 2.0.2 notice builder scripts), "Reply and notice bytes stay frozen" refers to those outputs/scripts.
- `tests/test_archive_assessment_applicability_authority_v2_publication.py` line 548-550 `test_at_pin_binding_reads_supersedes_from_authority`: delete the `inspect.getsource(...)` assertion lines (`src = ...`, `assert 'SUPERSEDED_V2_0_' not in src and ...`); keep the behavioural part (the `other` authority identity round-trip with `pytest.raises(... superseded {sup['version']} publication commit)`). Check whether `inspect` has other uses in the file before removing the import (ruff F401).
- Reply-builder message ("not in the repository history" for the regex-failure branch, line 349-350): CLOSED, frozen.

### Pattern: BASE-04

`tests/aa_history.py` at HEAD already holds the fix (lines 10-11 `HINT`; lines 26-31 report `printed {out!r}` and "cannot tell whether {root} is shallow"). It was made in `8dd3778` (D-11 of 12-01) and is covered by `test_history_problem_unrecognised_shallow_output_is_problem` (skip_guard lines 175-189, asserts `repr(out) in msg`, "cannot tell whether", not "is a shallow repository") and `test_require_history_fail_and_opt_out`. The only gap: no test asserts the HINT text itself says the opt-out reaches only guarded tests. Add one assertion (for example on `aa_history.HINT`: `'only skips tests guarded by require_history' in HINT and 'still fail' in HINT`) so a later edit cannot regress IN-08. Ledger: 11 IN-08 and IN-09 `FIXED`, evidence `8dd3778` + the named tests. `aa_history` is imported by `tests/conftest.py` and test modules only; no builder imports it `[VERIFIED: grep scripts/]`, so nothing "lands only in a frozen builder".

### Pattern: BOOK-01

Current frontmatter keys (read from the files and the plan files):

| Files | Current key | Source of truth for the mapping (PLAN frontmatter `requirements:`) |
|-------|-------------|---------------------------------------------------------------------|
| 11-01..11-06 | `requirements: [FROZEN-01]`, `[FROZEN-02]`, `[FROZEN-03]`, `[FROZEN-04]`, `[FROZEN-03]`, `[FROZEN-03]` | same, matches PLANs 11-01..06 |
| 12-01..12-08 | **no requirements key at all** | PLAN: 12-01 `[GATE-09]`; 12-02 `[GATE-08, GATE-09]`; 12-03 `[GATE-10]`; 12-04 `[GATE-07, GATE-10]`; 12-05 `[PIN-01]`; 12-06 `[PIN-02, GATE-06]`; 12-07 `[PIN-01, PIN-02, GATE-06]`; 12-08 `[PIN-01, PIN-02]` |
| 13-01..13-04 | `requirements: [PUB-10, PUB-11]`, `[PUB-10, PUB-11, PUB-12]`, `[PUB-10, PUB-12]`, `[PUB-10, PUB-11, PUB-12]` | same, matches PLANs 13-01..04 |

v1.2.0 traceability (`.planning/milestones/v1.2.0-REQUIREMENTS.md` lines 85-102) assigns FROZEN-01..04, GATE-06..10, PIN-01/02, PUB-10..12 to phases 11/12/13 as Complete. The 14-0x SUMMARY convention is `requirements-completed: [..]` (14-01 line 15, 14-02 line 12). Recommendation: **add** a `requirements-completed:` line (same list as the plan's `requirements`) directly after the `requirements:` line where it exists, and add both nothing else; for 12-0x, add only `requirements-completed:`. Keep existing `requirements:` lines untouched (minimal diff, no risk to tooling that reads it). The 12-0x lists must be checked against each SUMMARY's actual delivery (for example 12-01's SUMMARY says its folded items "carry no own requirement ID" and supports GATE-09), but the PLAN list is the documented traceability.

Safe staging (`core.autocrlf=true`): these files are `i/lf w/crlf`, so `git status` shows `M` and `git diff --ignore-cr-at-eol` is empty. Edit the working copy keeping CRLF endings, then `git add -- <the 18 explicit paths>` (git converts CRLF to LF on add), then verify `git diff --cached --stat` shows about 1 line added per file and nothing else, and `git diff --cached --ignore-cr-at-eol --stat` matches. Never `git add -A`, `git add .` or `git add .planning`: the working tree has many unrelated `M` files (config.json, 07-10 SUMMARY files) that must stay out of the commit. Use `git commit -m ... -- <paths>` or confirm `git diff --cached --name-only` lists exactly the 18 files before committing. If one staged diff shows more than the frontmatter line, restore the index entry (`git restore --staged <path>`) and re-edit.

### Pattern: BOOK-02 and requirement text (D-10)

`.planning/REQUIREMENTS.md` already contains V2-01 and V2-02 in the Future section (lines 73-74) and in the traceability table as `Deferred` (lines 111-112). BOOK-02 needs confirmation only (note it in the closure commit). GATE-13 (lines 23-30) and GATE-15 (lines 37-40) need the rewording from D-10; add Phase 17 rows (GATE-13 deferred items) and a Phase 19 row (GATE-15 IN-01) in the traceability table, and align ROADMAP success criteria 3 (and the Phase 17/19 criteria).

### Closure ledger rows (D-09), evidence to cite

| Item | Disposition | Reason / evidence |
|------|-------------|-------------------|
| 11 IN-08 | FIXED | `8dd3778` HINT text; new HINT assertion test |
| 11 IN-09 | FIXED | `8dd3778`; `test_history_problem_unrecognised_shallow_output_is_problem` |
| 12 IN-01, IN-02, IN-03, IN-04 | DEFERRED-17 | publisher messages/ordering; no publisher edit in Phase 16 (D-04) |
| 12 IN-05 | SUPERSEDED-BY-SEC-04 | literal pathspecs |
| 12 IN-06 | split: digest-check move DEFERRED-17; decisions-builder scope SUPERSEDED-BY-SEC-02 | D-04, D-05 |
| 12 IN-07 | FIXED (test parts); CLOSED (reply-builder message, frozen) | D-06 |
| 14 IN-01..IN-05 | FIXED | builder + test commit hashes |
| 15 IN-01 | DEFERRED-19 (closed for 2.0.3: sent text immutable) | D-03 |
| 15 IN-02, IN-03 | FIXED | test names above |

### Anti-Patterns to Avoid
- **`git commit` without a diff check** in the clone: exits 1 when the overlay is a no-op.
- **Copying the working tree wholesale** into the clone: pulls unrelated state in (violates D-08).
- **`git add -A`/`.planning` staging** for BOOK-01.
- **A conditional reproduction assertion** (the removed 66248f4 shape): it can never fail. Assert unconditionally on win32.
- **`pytest.skip` for any guard**: conftest converts skips to failures under `EMS_FAIL_ON_SKIP=1`; use `pytest.fail`/`assert`.
- **Editing the publisher, frozen reply or 2.0.2 notice builders** to make a test easier: forbidden.
- **Re-running `--emit-schema`/`--build` before taking the HEAD byte snapshot** for the identity gate.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Atomic write | custom journaling | `Path.write_text(...,newline)` to a sibling temp file then `os.replace` | same-volume rename is atomic on Windows and POSIX |
| Byte-identity of the sent notice | a new digest registry | `git show HEAD:<path>` byte compare + `git diff --exit-code` + the existing `validate_notice` rebuild compare | existing mechanisms; no new certified artifact |
| Mode detection for D-10 | hard-coded 2.0.2/2.0.3 constants | the authority's `source_lineage.supersedes` + the record, as in publisher line 841 | stays correct at 2.0.4 and later |
| Clone identity config | writing `.git/config` | `git -c user.name=... -c user.email=...` per command | no persistent state, works under any global config |

## Common Pitfalls

### Pitfall 1: CRLF blobs break plain-mode byte equality
**What goes wrong:** the overlay commit stores CRLF content (autocrlf=false with CRLF working copies), and `git_show(pub,p) != git_show(head,p)` fails in plain mode.
**How to avoid:** copy LF-normalised bytes (`replace(b'\r\n', b'\n')`) for all 11 files; commit with `core.autocrlf=false`.
**Warning signs:** "differs between the publication commit and HEAD" at HEAD where nothing changed.

### Pitfall 2: Child Python output codec on Windows
**What goes wrong:** the child writes cp1252 to a pipe; decoding as UTF-8 with `errors='replace'` mangles non-ASCII failure text. **How to avoid:** `PYTHONIOENCODING=utf-8` in the child env and `encoding='utf-8', errors='replace'` in the parent.

### Pitfall 3: Deep-root clone cannot be created
**What goes wrong:** root too long, `git clone` itself fails with `core.longpaths=false`. **How to avoid:** cap the root at about 200 characters, assert the precondition, and fail loudly if TMP is too long to build a controlled root.

### Pitfall 4: Builder `--build` partial files
**What goes wrong:** writing JSON/MD first, schema stale or validation fails. **How to avoid:** validate in memory, then temp-file + `os.replace`, then post-check `validate_notice()`.

### Pitfall 5: git status noise mistaken for a real change
**What goes wrong:** the three notice outputs show `M` (stat/eol noise) so `git diff --exit-code` looks unreliable; or conversely a real change is dismissed as noise. **How to avoid:** compare against `git show HEAD:path` bytes as well, and `git diff --ignore-cr-at-eol --stat` for the SUMMARY files.

### Pitfall 6: Bash/`git clone` crash on this machine
Git's bundled `sh.exe` aborts with `add_item ... errno 1` intermittently (observed again during this research: the same git command succeeded and failed on consecutive calls). Tests that `git clone` (D-10 outcome test, `make_clone` tests `test_live_*`, deep-root) are unreliable locally; use CI `workflow_dispatch` as authoritative evidence for them. Subagents have no PowerShell tool, so the orchestrator runs tests (per STATE.md).

## Code Examples

### D-10 overlay and mode selection (sketch, adapt style to the test file)
```python
# Source: derived from publisher lines 596, 795, 825, 841 (read-only)
def overlay(clone):
    rels = [*MODULE.publication_paths(), MODULE.rel(MODULE.SCRIPT)]
    for r in rels:
        dest = clone / r
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((REAL_ROOT / r).read_bytes().replace(b'\r\n', b'\n'))
    base = ['-c', 'core.autocrlf=false', '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false']
    assert git(*base, '--literal-pathspecs', 'add', '--', *rels, cwd=clone).returncode == 0
    if git(*base, 'diff', '--cached', '--quiet', cwd=clone).returncode != 0:   # 1 = there is something to commit
        assert git(*base, 'commit', '-q', '-m', 'overlay working-tree publication paths', cwd=clone).returncode == 0

def validate_mode(clone):
    sup = json.loads((REAL_ROOT / MODULE.rel(MODULE.AUTHORITY)).read_text(encoding='utf-8'))['source_lineage']['supersedes']
    rec = json.loads((clone / MODULE.rel(MODULE.PUBLICATION_RECORD)).read_text(encoding='utf-8'))
    superseded = rec.get('authority_id') == sup['authority_id'] and rec.get('version') == sup['version']
    return ['--validate', '--at-pin'] if superseded else ['--validate']
```

### Atomic three-file write (builder `--build`)
```python
# Source: stdlib os.replace; helper style matches the builder's one-line helpers
def write_atomic(p: Path, text: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.tmp')
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f: f.write(text)
    return tmp
# --build: stage all three temps, then os.replace each, then validate_notice(); remove temps in a finally
```

## State of the Art

| Old approach | Current approach | Impact |
|--------------|------------------|--------|
| `rmtree(onerror=)` | `rmtree(onexc=)` (3.12) | `onerror` deprecated in 3.12; CI and local are 3.12 |
| Equality-only deep-root test | Win32: assert the no-`--` failure reproduces | Test now fails if it cannot fail |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | This Windows machine still reproduces `Filename too long` without `--` at a root of about 150-170 characters with `core.longpaths=false` (shown by the executor run at 157, 2026-11-18, but not re-run here because local `git clone` crashes) | BASE-02 | The new assertion fails on a machine with system-wide long paths; that is the intended loud failure, but the planner should expect to verify on a working machine or CI-Windows |
| A2 | The 12-0x SUMMARY `requirements-completed` lists equal the PLAN lists (PLAN frontmatter is the documented traceability; SUMMARY bodies were not audited per plan) | BOOK-01 | A requirement attributed to a plan that did not deliver it; verify against each SUMMARY body |
| A3 | Root cap of about 200 characters keeps `git clone --shared` creatable under `core.longpaths=false` (derived from `.git/hooks/*.sample` path lengths, not measured) | BASE-02 | Clone fails for some TMP lengths; adjust cap |

## Open Questions

1. **How strictly to read "remove the duplicated hint test" (15 IN-02)?**
   - What we know: the real-git duplicate named in the review no longer exists; the mocked parametrised test at line 744 is the sole owner of the positive long-path hint.
   - Recommendation: fold its three cases into the line 346 test and delete 744 (coverage preserved, one hint test).
2. **Should the Phase 16 byte-identity gate also pin hashes?**
   - Recommendation: no new artifact; `git show HEAD:` compare + `git diff --exit-code` + `--validate` (existing rebuild compare) is sufficient. The notice is not hash-certified by a manifest.
3. **Does 12-0x frontmatter need a `requirements:` key as well?**
   - Recommendation: add only `requirements-completed:` (14-0x convention).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | all tests, builders | yes | 3.12.10 | none needed |
| git | clone-based tests, gates | yes, but `sh.exe` crashes intermittently on clone | 2.54.0.windows.1 | CI `workflow_dispatch` (ubuntu, `fetch-depth: 0`) for clone tests |
| Bash tool | research/ad hoc | flaky (observed failing 3 of ~12 calls) | - | PowerShell from the orchestrator |
| pytest | tests | yes (8.4.2 / 9.1.1 caches present) | - | none needed |

**Missing dependencies with no fallback:** none. **With fallback:** reliable local `git clone` (use CI for clone tests).

## Validation Architecture

(`workflow.nyquist_validation` is false in `.planning/config.json`; included because the requester asked for it.)

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (CI installs unpinned) with `jsonschema==4.26.0` |
| Config file | none (no pytest.ini/pyproject); `tests/conftest.py` holds the `EMS_FAIL_ON_SKIP` guards |
| Quick run command | `python -m pytest tests/test_archive_assessment_skip_guard.py tests/test_archive_assessment_lineage_validation.py -p no:cacheprovider -q --basetemp=<scratch>` |
| Full suite command | `EMS_FAIL_ON_SKIP=1 python -m pytest tests/test_archive_assessment_*.py -p no:cacheprovider -q --basetemp=<fresh dir>` (about 593 s) |

Set `EMS_FAIL_ON_SKIP=1` in PowerShell with `$env:EMS_FAIL_ON_SKIP='1'`. Use a fresh `--basetemp` under the session scratchpad each run (`tmp_path` is not usable here without it; old `.pytest-temp` dirs exist in the repo root and are ignored/untracked).

### Phase Requirements to Test Map
| Req | Behaviour | Test | Command | Exists |
|-----|-----------|------|---------|--------|
| BASE-01/03 | D-10 baseline in the right mode on working tree | `test_d10_live_catalog_edit_or_delete_does_not_change_validate_outcome` (rewritten) | `pytest tests/test_archive_assessment_lineage_validation.py -k validate_outcome` | rewrite; clone test, CI authoritative |
| BASE-02 | deep root reproduces failure without `--` | `test_git_show_double_dash_survives_deep_checkout_root_with_real_git` (strengthened) | `pytest tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py -k deep_checkout` | strengthen; CI exercises the non-win32 branch only |
| BASE-04 | HINT/shallow wording | skip_guard tests + new HINT assertion | `pytest tests/test_archive_assessment_skip_guard.py` | add one assertion |
| GATE-14 | lineage commit cross-check, domain errors, atomic build, deepcopy | new tests in notice 2.0.3 test file (wrong-commit lineage; malformed blob raises `AuthorityError`; `--build` leaves no partial files with a forced validation failure on a temp copy; mutating the built notice does not change inputs) | `pytest tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py -k "lineage or malformed or build or deepcopy"` | add |
| GATE-15 | missing-git hint, single hint test | new/merged tests | `-k git_show_error` | edit |
| GATE-13 (IN-07) | `cat_exc` match; behavioural at-pin test | edit two existing tests | `pytest tests/test_archive_assessment_demo3_w1_req_001_reply.py -k resolve_record_commit`; `pytest tests/test_archive_assessment_applicability_authority_v2_publication.py -k at_pin_binding` | edit |
| D-02 gate | `--build` leaves three files unchanged | command, not a test | `python scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py --build` then `git diff --exit-code -- <3 files>` and byte compare with `git show HEAD:` | run by plan |
| BOOK-01/02, ledger | frontmatter + ledger consistent | grep check | e.g. grep `requirements-completed` over the 18 files; staged diff name check | manual/grep |

### Sampling Rate
- Per task: the targeted `-k` command above.
- Per wave: all of `tests/test_archive_assessment_*.py` with `EMS_FAIL_ON_SKIP=1` locally (clone tests may crash locally; expect to rely on CI for them).
- Phase gate: pushed branch, CI `archive-assessment` job green via `workflow_dispatch` with 0 skipped, and the 7 CI validators PASS (publisher, decisions builder, rule proposals x2, reply, 2.0.2 notice, 2.0.3 notice), plus `git diff` on the publisher, reply builder and 2.0.2 notice builder empty (`git diff --exit-code -- scripts/publish_archive_assessment_applicability_authority_v2.py scripts/build_archive_assessment_demo3_w1_req_001_reply.py scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py`, with the CRLF caveat: use `--ignore-cr-at-eol` or compare to `HEAD` blobs).

### Wave 0 Gaps
None for infrastructure. New tests go into existing files.

## Security Domain

`security_enforcement` is enabled. This phase adds no network, credential or privilege surface.

| ASVS Category | Applies | Control |
|---------------|---------|---------|
| V5 Input validation | yes (builder malformed-input wrapping) | fail closed with `AuthorityError`; `bad_rel` path checks remain |
| V6 Cryptography | no | existing SHA-256 only; do not change |
| V2/V3/V4 | no | none |

| Threat | STRIDE | Mitigation |
|--------|--------|------------|
| Tampered lineage commit in the pinned authority | Tampering | `EXPECTED_LINEAGE_COMMIT` cross-check (14 IN-01) |
| Partial/stale generated files after a failed `--build` | Tampering | validate in memory, atomic replace (14 IN-03) |
| Test clone commits leaking into the real repo | Tampering | clone is under temp; per-command `-c` identity, no config writes; never `push` from the clone |
| Committing unrelated working-tree changes with BOOK-01 | Info disclosure / integrity | explicit paths only; verify `git diff --cached --name-only` |

## Project Constraints (from CLAUDE.md)
- Python 3.12, `jsonschema`, PyYAML, pytest; match file style (builder: single-quote compact helpers; tests: single quotes, 4-space).
- `pathlib.Path`, explicit `encoding='utf-8'`; deterministic JSON `json.dumps(value, indent=2, sort_keys=True) + '\n'`.
- Fail closed with domain exceptions; build/validate separation; no absolute paths in registry JSON.
- Do not publish or edit unrelated uncommitted work; commits must contain only deliberate changes. Hash certification: do not hand-edit certified artifacts (publisher, authority, manifest).
- All file changes happen inside a GSD workflow (this phase's execution).

## Sources

### Primary (HIGH confidence): read directly from the repository at HEAD 9a10810
- `tests/test_archive_assessment_lineage_validation.py` lines 321-378; `tests/aa_history.py`; `tests/conftest.py`; `tests/test_archive_assessment_skip_guard.py` lines 125-215
- `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` lines 150-240, 330-370, 600-790; reply test lines 342-395; v2 publication test lines 530-575
- `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py` (lines cited inline); `scripts/build_archive_assessment_demo3_w1_req_001_reply.py` lines 340-360
- `scripts/publish_archive_assessment_applicability_authority_v2.py` lines 375-440, 596, 792-866
- `.planning/phases/{11,12,13,14,15}-*/**-REVIEW.md`, `.planning/quick/261118-cgq-*/261118-cgq-SUMMARY.md`, `.planning/milestones/v1.2.0-{REQUIREMENTS,MILESTONE-AUDIT}.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.github/workflows/ems-validate.yml`, `.gitattributes`
- `registry/archive_assessment_applicability_authority_v2.json` (lineage commits) and the publication record, via Python read

### Secondary / not re-verified (MEDIUM)
- The deep-root reproduction on this machine (A1) and the clone-based tests: could not run locally (git `sh.exe` crash).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH (no new packages)
- Architecture and code locations: HIGH (read at line level)
- BASE-02 reproduction on Windows: MEDIUM (A1, A3)
- Pitfalls: HIGH (derived from code and prior review/fix notes)

**Research date:** 2026-11-18
**Valid until:** until the next commit touches the cited files (about 7 days; Phase 17 edits the publisher and invalidates the D-10 red-window notes only in timing, not in design)
