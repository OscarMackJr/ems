---
phase: 12-verify-at-pin-and-gate-hardening
reviewed: 2026-11-17T03:33:21Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - .github/workflows/ems-validate.yml
  - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
  - scripts/publish_archive_assessment_applicability_authority_v2.py
  - tests/aa_history.py
  - tests/conftest.py
  - tests/test_archive_assessment_applicability_authority_v2.py
  - tests/test_archive_assessment_applicability_authority_v2_publication.py
  - tests/test_archive_assessment_demo3_w1_req_001_reply.py
  - tests/test_archive_assessment_governance_answers.py
  - tests/test_archive_assessment_governance_decisions.py
  - tests/test_archive_assessment_lineage_validation.py
  - tests/test_archive_assessment_normalisation_claims.py
  - tests/test_archive_assessment_skip_guard.py
findings:
  critical: 1
  warning: 4
  info: 7
  total: 12
status: issues_found
---

# Phase 12: Code Review Report

**Reviewed:** 2026-11-17T03:33:21Z
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

Diff reviewed: `87b5cd5..4fd2947`, covering the 13 scoped files. The main subject was the v2 publisher. That covers the git seam (`git_run`, `git_head`, `git_is_ancestor`, `git_not_shallow`, `git_dirty`, `git show ... --`), `--validate --at-pin`, D-06 ancestry and blob identity, the GATE-06 script digest, GATE-07 schema-first loading and the `SUPERSEDED_V2_0_2` binding.

The D-16 red set is not reported as a defect. It is `test_committed_schema_equals_schema_function`, `test_real_published_files_validate`, `test_publisher_still_valid_and_digest_matches_manifest` and CI validator 1. I found nothing that would stop these from turning green after a correct 2.0.3 publication and record commit. Specifically:

- `schema()` pins `SUPERSEDED_V2_0_2`.
- The 2.0.2 record at the publication commit satisfies the at-pin binding.
- Plain mode accepts the record commit and any later commit.
- CI's archive job uses `fetch-depth: 0`.

The argument validation in the helpers is sound. They validate SHAs and paths before calling git, use no shell, place `--` correctly, and handle unknown shallow output and `merge-base` exit codes other than 0 or 1 by failing closed.

The main defect is the at-pin "clean tree" guarantee (D-04, D-08, D-12). It rests only on `git status --porcelain`, which is silent in four cases:

- a publication file that is ignored and untracked, or that is absent from HEAD (all 7 generated files live under the gitignored `generated/`);
- `skip-worktree` or `assume-unchanged` entries;
- `status.showUntrackedFiles=no`.

I reproduced each case in a scratch repository. Plain mode has a related gap. It ties the working tree to HEAD for only 2 of the 10 publication files, so a dirty tree can PASS while the committed blobs are wrong.

## Critical Issues

### CR-01: At-pin "clean tree" check passes when a publication file is absent from HEAD, ignored, or marked skip-worktree

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:403-408` (`git_dirty`), `:762-765` (at-pin entry)

**Issue:** D-04, D-08 and D-12 make at-pin's whole guarantee that the files validated are the files at HEAD. That guarantee comes only from `git status --porcelain -- <paths>`. Reproduced with git in a scratch repository whose `.gitignore` contains `generated/`, the same as this repository:

1. A file under `generated/` that is untracked or ignored produces **no output**.
2. A tracked `generated/t.json` removed from the index by a *committed* `git rm --cached`, still present on disk, produces **no output**. HEAD no longer contains the file, yet the working tree has it and at-pin validates it.
3. With `-c status.showUntrackedFiles=no` (a user or repo config), an untracked `reg/u.json` produces **no output**.
4. With `git update-index --skip-worktree reg/a.json` followed by an edit, the file produces **no output**. The same applies to `assume-unchanged`. This also defeats D-08 and D-12 for the publisher script, because a skip-worktree-flagged edited `scripts/publish_..._v2.py` is reported as clean.

All 7 generated publication files sit under the gitignored `generated/` directory (`.gitignore:6`). They are tracked only because they were force-added. If a Phase 13 publication commit omits or drops one of them, `--validate --at-pin` at that commit still prints `{"status":"PASS","mode":"AT_PIN",...}` in the operator's tree. Phase 13 uses that gate before writing the record. A defective pin would therefore be recorded, and it would only be caught afterwards by plain mode (the `git_show(pub, p)` failure) or by Hayes's fresh checkout. This is the "wrong publication passes" case, at the single republication. The error text "modified or untracked in the working tree" also promises more than the check delivers.

**Fix:** Make at-pin compare content against HEAD directly instead of trusting status, and harden the status call as a second line:
```python
def at_pin_tree_matches_head(paths: list[str]) -> None:
    head = git_head()
    for p in paths:
        try: blob = git_show(head, p)            # fails closed if p is not in HEAD
        except GitHistoryError as e: raise AuthorityError(f'at-pin: {p} is not committed at HEAD: {e}') from e
        live = ROOT / p
        if not live.is_file() or lf_bytes(live.read_bytes()) != lf_bytes(blob):
            raise AuthorityError(f'at-pin: {p} differs from HEAD')
# and in git_dirty:
r = git_run('--literal-pathspecs', 'status', '--porcelain', '--untracked-files=all', '--ignored=matching', '--', *paths)
```
Call `at_pin_tree_matches_head([*publication_paths(), rel(SCRIPT)])` after `git_not_shallow()`. Also reject any path whose `git ls-files -v` tag is lowercase (assume-unchanged) or `S` (skip-worktree).

## Warnings

### WR-01: Plain `--validate` binds HEAD to the publication commit, but binds the working tree to HEAD for only the authority and manifest

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:812-825`

**Issue:** Plain mode checks three things:

- live files (LF) against a fresh build and the live manifest;
- the live manifest and authority (LF) against the record;
- `git_show(pub, p) == git_show(HEAD, p)` for the 10 paths.

Nothing ties the HEAD or publication-commit blobs of the schema, the sign-off and the six other generated files to the manifest digests. Plain mode also never consults the working tree state (`test_at_pin_dirty_tree_fails_closed` asserts exactly that). Suppose the publication commit contains a stale generated file while the operator's working tree holds the correct one, for example after an uncommitted fix. Plain `--validate` then PASSes locally, though the record commit Hayes pins carries the wrong bytes. CI on a clean checkout would catch it, but the operator's post-record gate in Phase 13 would not.

**Fix:** In the plain-mode block, compare the LF bytes of each HEAD blob with the live file. Equivalently, check each `git_show(pub, p)` against the manifest artifact digest:
```python
for p in publication_paths():
    pb = git_show(pub, p)
    if pb != git_show(head, p): raise AuthorityError(f'{p}: differs between the publication commit and HEAD')
    if lf_bytes(pb) != lf_bytes((ROOT / p).read_bytes()): raise AuthorityError(f'{p}: working tree differs from the publication commit')
```

### WR-02: The git seam inherits the caller's git environment and replace refs, so "fail-closed" checks can read a different repository or substituted objects

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:368-376` (`git_show`, `git_run`)

**Issue:** `subprocess.run(['git', ...], cwd=ROOT)` honours several things that `cwd` does not control:

- `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY` and `GIT_ALTERNATE_OBJECT_DIRECTORIES`, which are set inside git hooks and by some CI or harness wrappers;
- `refs/replace/*` and grafts, which `git show`, `merge-base --is-ancestor` and `rev-parse` all follow.

A `git replace` of the 2.0.2 authority blob, or a `GIT_DIR` that points elsewhere, changes what every pinned-blob cross-check, the D-06 ancestry check and the D-07 pinned-script digest actually compare. Because these validators are the evidence Hayes cites, they should not depend on ambient git state.

**Fix:** Build a sanitized environment once and pass `env=` to both `subprocess.run` calls. Drop the `GIT_*` variables, then set `GIT_NO_REPLACE_OBJECTS=1`, `GIT_LITERAL_PATHSPECS=1` and `GIT_CONFIG_NOSYSTEM=1`. Prefer `git cat-file blob <commit>:<path>` over `git show` for raw blob bytes.

### WR-03: `test_d10_live_catalog_edit_or_delete_does_not_change_validate_outcome` passes when `--validate` is broken

**File:** `tests/test_archive_assessment_lineage_validation.py:357-377`

**Issue:** The test asserts only that the last output line and the exit code are the same before and after the catalog edit or delete. In the current red window `--validate` exits 1 both times with the same `AuthorityError` line, so the test is green without exercising D-10 at all. Any future regression that makes `--validate` fail early, before the catalog is read, also keeps it green. It cannot detect the property it names unless the baseline is PASS.

**Fix:** Assert that the baseline is meaningful. For example, require `before == (0, 'PASS')`, and add it to the D-16 ledger until Phase 13. Alternatively, assert that the failing line is not caused by the catalog, and that the run gets past `validate_lineage`, using a marker or a monkeypatched in-process run.

### WR-04: No test covers at-pin against the real repository layout (ignored `generated/`, index flags, user config)

**File:** `tests/test_archive_assessment_applicability_authority_v2_publication.py:758-786` (`test_real_git_repo_at_pin_passes_and_dirty_fails`), `:1422-1446` (`test_git_dirty_*`)

**Issue:** The only real-git at-pin test builds a temporary repository with **no `.gitignore`** and no index flags. It checks only a working-tree byte edit of the authority and of the script. None of the CR-01 cases is exercised:

- a publication file under an ignored directory that is untracked or deleted from HEAD;
- `skip-worktree` or `assume-unchanged`;
- `status.showUntrackedFiles=no`.

The `git_dirty` unit tests fake `git_run`, so they cannot observe git's real reporting. The gap in CR-01 therefore went unnoticed.

**Fix:** In the temporary repository, write `.gitignore` with `generated/`, then force-add and commit. Then assert that at-pin fails in each of these cases:

- `git rm --cached <out file>` committed;
- `git update-index --skip-worktree <authority>` followed by an edit;
- `git -c status.showUntrackedFiles=no` with an untracked publication file (set it through `git config` in the temporary repository).

## Info

### IN-01: Plain-mode error says "committed authority" but compares the working-tree file

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:813-814`

**Issue:** `record['authority_sha256'] != lf_digest(AUTHORITY)` and the manifest twin compare against the working tree. The messages "does not match the committed authority" and "committed manifest" are inaccurate now that a real committed-blob check exists two lines below.

**Fix:** Say "the authority in the working tree" and "the manifest in the working tree".

### IN-02: The "HEAD is the publication commit" diagnosis can be false

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:809`

**Issue:** A record that still names the superseded publication occurs at the publication commit, but also in the operator's tree after `--publish` and before the publication commit, or on any intermediate commit. The message states as fact that HEAD is the publication commit.

**Fix:** Say "the record still names the superseded X publication (HEAD is the publication commit or earlier)".

### IN-03: At-pin's wrong-record error does not point to plain mode

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:805-806`

**Issue:** Running `--validate --at-pin` at the record commit or later fails with "at-pin record must name the superseded 2.0.2 publication commit". The reverse case (plain mode at the pin) points to `--at-pin`, but this case gives no pointer back to plain `--validate`. Hayes is told to use both commands (PIN-03), so the asymmetry will produce support questions.

**Fix:** When `record` names `a['authority_id']` and `a['version']`, raise "the record already names this publication; run plain --validate here".

### IN-04: Plain-mode shallow check runs after the history reads it guards

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:770`, `:816-819`

**Issue:** `validate_publication` (through `rows_differing_from_previous`), `validate_lineage` and the record `git_show` calls all read pinned history before `git_not_shallow()` at line 819. In a depth-1 clone, plain mode fails closed, but with "git show failed: fatal: invalid object name" instead of the D-06 "shallow; fetch full history" message.

**Fix:** Call `git_not_shallow()` at the top of `validate_published` for both modes.

### IN-05: `git_dirty` passes repository-relative paths as pathspecs

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:403-407`

**Issue:** `bad_rel` does not reject `*`, `?`, `[` or a leading `:(`. Git interprets these as glob or magic pathspecs. In the scratch repository, `git status --porcelain -- 'reg/*.json'` matched other files. Today's callers pass constants only, but the helper is documented for reuse by Phase 13 PUB-12.

**Fix:** Use `git --literal-pathspecs status ...` or set `GIT_LITERAL_PATHSPECS=1` (see WR-02).

### IN-06: GATE-06 self-attestation scope

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:782`, `:670-685`

**Issue:** The digest check lives inside the script it verifies, so an edited publisher can remove it. It also does not cover `scripts/build_archive_assessment_governance_decisions.py`, which `validate_governance_decisions` imports and executes. That builder in turn re-imports the publisher from disk as a second module copy. The decisions file itself is pinned by digest, so this is not a decision-integrity hole. It does mean the "certified validator" is wider than the digested file. The live-script check also runs after `validate_publication`, so a publisher edit is reported through whichever earlier check breaks first, not as "publisher script differs" (as with today's CI validator 1 message).

**Fix:** Move the `lf_digest(SCRIPT)` check to just after loading the manifest. Record the decisions-builder digest in the manifest at the next republication, or document the boundary in the PIN-03 guidance.

### IN-07: Weak or brittle assertions in new tests

**File:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py:386`; `tests/test_archive_assessment_applicability_authority_v2_publication.py` (`test_at_pin_binding_reads_supersedes_from_authority`, line 550); `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:349-350`

**Issue:**
- The `cat_exc` case matches `'in the repository history'`. That string also matches the "is not in the repository history" message, so the test cannot tell the new OSError branch from the missing-commit branch.
- The reply builder's regex-failure branch still says "is not in the repository history" for a malformed frozen constant, which is a false diagnosis. It is unchanged in 12-03, and D-13 limits edits there.
- `test_at_pin_binding_reads_supersedes_from_authority` greps the function source for the literal `a['source_lineage']['supersedes']`, so a harmless refactor breaks it.

**Fix:** Match `'cannot check whether the frozen commit'` for `cat_exc`. Defer the message fix to the post-2.0.3 frozen-builder revisit. Replace the source grep with the behavioural assertion the test already makes.

---

_Reviewed: 2026-11-17T03:33:21Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
