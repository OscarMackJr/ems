---
phase: 07-lineage-source-and-per-digest-scope
reviewed: 2026-10-20T00:00:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - scripts/publish_archive_assessment_applicability_authority_v2.py
  - tests/test_archive_assessment_applicability_authority_v2.py
  - tests/test_archive_assessment_applicability_authority_v2_publication.py
  - tests/test_archive_assessment_lineage_validation.py
  - tests/test_archive_assessment_normalisation_claims.py
  - .gitattributes
findings:
  critical: 0
  warning: 5
  info: 4
  total: 9
status: issues_found
---

# Phase 7: Code Review Report

**Depth:** standard. No python or pytest was run (per instructions). Expected red tests are not findings.

## Summary

The core design holds. `git_show` validates the commit as 40 lowercase hex before spawning, so option injection through the commit is not possible, and `commit:path` cannot be read as an option. It uses argument-list `subprocess` (no shell) and checks `returncode`. It returns raw bytes, and `git show` of a blob applies no smudge filter, so the bytes are the true blob. Every path through `validate_lineage` that raises, or records an error, fails closed, with one exception: WR-01. No digest passes without being recomputed, except through that same exception.

## Warnings

### WR-01: validate_lineage fails open to the working tree when a commit-pinned entry has no commit
**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:337`
**Issue:** `git_show(commit, path) if commit else (ROOT / path).read_bytes()` treats a missing, empty or None `commit` as "use the working file". For `supersedes` and `v1_baseline`, which D-10 says must be recomputed from git, dropping `commit` silently downgrades the check to the checked-out file. The 2.0.0 file in the working tree is now 2.0.1, so `supersedes` would usually fail, but `v1_baseline` could pass. `validate_lineage` is also a standalone function. In the full `--validate` path the schema and `validate_publication` pin the commit, but `validate_lineage` itself does not enforce it. No test removes `commit` from a pinned entry.
**Fix:** Add `PINNED = {'supersedes', 'supersedes_governance_decisions', 'v1_baseline'}`. For labels in `PINNED`, require a commit, for example `if label in PINNED and not commit: errors.append(...); continue`. For the other labels, require that no commit is present, or ignore it. Add a negative test that deletes `commit`.

### WR-02: Non-string commit or normalisation raises a raw TypeError instead of AuthorityError
**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:316, 334`
**Issue:** `re.fullmatch(..., commit or '')` raises TypeError when `commit` is a truthy non-string such as `5` or `[]`. `norm not in NORMALISERS` raises TypeError when `norm` is unhashable, such as a list or dict. `validate_lineage` only catches `OSError` and `AuthorityError`, so a malformed lineage produces a traceback and not the aggregated fail-closed error. It still exits non-zero, but it breaks the D-11 contract that every path raises `AuthorityError`.
**Fix:** In `git_show`, check `isinstance(commit, str)` first. In `validate_lineage`, check `isinstance(norm, str) and norm in NORMALISERS`.

### WR-03: Path guard misses Windows drive-relative paths
**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:85, 317, 335`
**Issue:** `contains_absolute` only rejects `X:` followed by a separator. A value such as `C:foo` passes the guard, and `ROOT / 'C:foo'` on Windows (the primary platform) resolves outside ROOT. Backslash paths with `..` are handled. The path guard is also copy-pasted in `git_show` and `validate_lineage`.
**Fix:** Extract one `safe_rel(path)` helper. It should reject any `:` in the path, and it should resolve the result and assert it stays under ROOT (`(ROOT / p).resolve().is_relative_to(ROOT.resolve())`).

### WR-04: Normalisation-claim tests skip silently, so they can pass vacuously
**File:** `tests/test_archive_assessment_normalisation_claims.py:39-110`
**Issue:** Every test is guarded by `skipif(not X.exists())`. D-13 requires these claims to be proven. If an artifact is deleted or renamed, or its path constant drifts, the test skips and stays green. The suite never asserts that at least one claim test actually ran.
**Fix:** Assert that the files exist in a single non-skipped test. Alternatively, drop the skipif for the committed artifacts. Only the publication record and the manifest, which are written at Phase 9, justify a skip.

### WR-05: test_reply_pin_normalisation_claim will break at Phase 9
**File:** `tests/test_archive_assessment_normalisation_claims.py:103-109`
**Issue:** The test asserts that the sent 2.0.1 reply pin equals the digest of the current `AUTHORITY` and `MANIFEST`. D-14 says the reply stays frozen at 2.0.1. When Phase 9 republishes as 2.0.2, the authority and manifest digests change and the test fails for a reason that is not a defect in the claim. The pin's own claim was verified against its own pinned files, not against the files in the working tree.
**Fix:** Recompute the pin against the 2.0.1 blobs with `git show <pin commit>:<path>`. Alternatively, assert only the `digest_normalisation` string plus the reply prose. Document the expected Phase 9 breakage if it is left as is.

## Info

### IN-01: The "changed declared normalisation" test never reaches recomputation
**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:334`; `tests/test_archive_assessment_lineage_validation.py:99-116`
**Issue:** The `EXPECTED_NORMALISATION` comparison rejects any flipped normalisation before the digest is recomputed. The test passes, but it exercises the expectation table and not recomputation under the other normaliser. On the CRLF fixture a flip to the wrong mode would also fail by hash, but nothing proves that. The `normalisation` field is effectively redundant with the hard-coded table.
**Fix:** Add a test that monkeypatches `EXPECTED_NORMALISATION`, or that recomputes the recorded digest under the wrong normaliser. Or note the redundancy in a comment.

### IN-02: Fixture is not hermetic with respect to git environment
**File:** `tests/test_archive_assessment_lineage_validation.py:76-79`
**Issue:** The `git commit` in the fixture can fail under a global `commit.gpgsign=true`, and a stray `GIT_DIR` or `GIT_INDEX_FILE` in the environment can redirect `git init`/`add`/`commit`. The same stray `GIT_DIR` would redirect `git_show` itself in production code.
**Fix:** Add `-c commit.gpgsign=false` to `base`. In the helper `git()`, set `env={k: v for k, v in os.environ.items() if not k.startswith('GIT_')}`.

### IN-03: Style drift and weak schema expression
**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:655, 350`
**Issue:** `if a !=build_published_authority():` has a missing space. `norm_schema` emits both `enum` and `const`, and the `enum` is inert (the `const` already forces one value). This does not affect D-04 enforcement, but it implies the closed vocabulary is more flexible than it is. `subprocess.run` has no timeout.
**Fix:** Fix the spacing. Use only `const` or only `enum`. Add `timeout=60`.

### IN-04: Working-tree recomputation does not prove the committed blob
**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:337`
**Issue:** Non-commit-pinned entries are hashed from the checked-out file. A locally modified or uncommitted file passes locally while the committed blob differs. CI is a clean checkout, so it is only a local false-positive. The tests in `test_archive_assessment_lineage_validation.py` do check the HEAD blob for the AA1 manifest (D-07).
**Fix:** Optional. Verify against `HEAD` for tracked files, or warn on a dirty status.

---

_Reviewed: 2026-10-20_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
