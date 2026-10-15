---
phase: 06-address-tech-debt-publication-gate-hardening-2-0-1
reviewed: 2026-10-14T00:00:00Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - scripts/publish_archive_assessment_applicability_authority_v2.py
  - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
  - scripts/build_archive_assessment_governance_decisions.py
  - scripts/validate_archive_assessment_rule_proposals.py
  - schemas/archive_assessment_applicability_authority_v2.schema.json
  - schemas/archive_assessment_demo3_w1_req_001_reply.schema.json
  - tests/test_archive_assessment_applicability_authority_v2.py
  - tests/test_archive_assessment_applicability_authority_v2_publication.py
  - tests/test_archive_assessment_demo3_w1_req_001_reply.py
  - tests/test_archive_assessment_governance_decisions.py
  - tests/test_archive_assessment_rule_proposals.py
  - tests/test_archive_assessment_rule_proposals_record.py
findings:
  critical: 0
  warning: 5
  info: 4
  total: 9
status: issues_found
---

# Phase 06: Code Review Report

**Depth:** standard. The six affected test modules were run: 429 passed.

## Summary

No blocker found. UNKNOWN and absent evidence still cannot resolve to not-applicable. `semantic_conflicts()` is a real executed check, and `run_mutations()` raises if any mutation is accepted. The two orchestrator-directed test changes do not materially weaken the guarantee (see "Orchestrator-directed test changes" below). The remaining issues are places where a gate can be skipped silently, or where a pinned digest is recorded but not actually bound.

## Warnings

### WR-01: Publisher script digest is recorded but never verified on validation
**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:~605-612` (`validate_published`) and `build_all_outputs` (`publisher_script`)
**Issue:** `validate_published` only checks that `publisher_script.sha256` is a 64-hex string. It then rebuilds the outputs with that same value (`script_sha256=ps['sha256']`), so the manifest comparison is circular. The publisher script was removed from the `artifacts` list that is digest-checked. The publisher can therefore be edited, or even gutted, after publication, and `--validate` still prints PASS. The only binding is the pytest `test_manifest_publisher_script_digest_matches_publication_commit`. That test compares against `git show <publication_commit>:script`, not against the live script, and it skips on shallow clones.
**Fix:** Have `validate_published` assert that the manifest `publisher_script.sha256` equals the digest of the script at `publication_commit`. Use `git show` and fail closed if git is unavailable. As an alternative, add a test asserting that the live script's digest equals the manifest value, or that the script is unchanged since the publication commit.

### WR-02: Publication record cross-check is skipped when authority_id differs or the record is absent
**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:~509-513`
**Issue:** The `authority_sha256` and `manifest_sha256` binding runs only `if PUBLICATION_RECORD.exists()` and `record.get('authority_id') == a['authority_id']`. A stale record, a tampered `authority_id`, or a deleted record turns the check off, and `--validate` still passes.
**Fix:** Require the record to exist and to match once the authority is published. Raise `AuthorityError` on an `authority_id` mismatch instead of skipping. If the record is legitimately written after the first validate, make that an explicit flag rather than the default.

### WR-03: Frozen-catalog equality check silently degrades to a pass when git/history is unavailable
**File:** `scripts/validate_archive_assessment_rule_proposals.py:~564-573` and `validate_proposal` (~108-117)
**Issue:** If the live catalog differs from the recorded digest and `dc3b41c` cannot be read (shallow CI checkout, no git), `frozen_catalog()` prints a stderr NOTICE and returns `None`. Validation then succeeds with the `catalog_inputs` equality check skipped. In that mode `entry = dict(ci)` is compared with nothing, so a tampered `catalog_inputs` passes. The skip is intentional, and a test asserts it, but a skipped integrity check produces an exit-0 pass indistinguishable from a full check, and the notice is only on stderr.
**Fix:** Fail closed by default and raise `AuthorityError`. Allow the skip only with an explicit opt-in such as `--allow-unverified-catalog`. Alternatively, commit a frozen catalog snapshot, or digests of the 21 entries, so no git access is needed.

### WR-04: Negative-mutation "rejection" accepts incidental crashes as a gate
**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:~415-432` (`mutation_gates`)
**Issue:** `validate_publication` and the other validators are wrapped in `except (AuthorityError, KeyError, TypeError, AttributeError)`. A mutation that causes a KeyError or TypeError because the mutator broke the document shape is recorded as `PYTHON_VALIDATOR` rejection, even though no semantic invariant fired. For example, `_m_digest_and_count` and `lambda a: a['applicability_decision_ids'].pop()` depend on fixture shape. A mutation can therefore appear covered when the intended check never ran. Only mutations flagged `schema_must_reject` are pinned to a specific gate.
**Fix:** Catch only `AuthorityError` for the Python gate. Record unexpected `KeyError`/`TypeError` as a harness error, or assert the expected error text per mutation (an `expect_substring` field on `Mutation`).

### WR-05: Reply builder/validator depends on full git history to derive the pinned record commit
**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:79-81, 262-267`
**Issue:** `pin.publication_record_commit` comes from `git log -n1 -- <record>`. In a shallow clone, `ems-validate.yml`-style CI with the default fetch-depth, this returns the graft commit. That is either the wrong commit, or it equals `publication_commit` and trips the "record commit equals the publication commit" error, so validation cannot run there. A worktree edit to the record that is not yet committed also pins the stale previous commit. The tests handle this with `git_ready()` skips, but `validate_reply()` itself does not.
**Fix:** Detect a shallow repository in `resolve_record_commit()` and raise a clear error ("full history required"). Also verify the record file is clean against HEAD (`git diff --quiet HEAD -- <record>`).

## Orchestrator-directed test changes

- `test_publication_commit_ancestor_and_file_set` (publication test, ~494-514): the relaxation is sound. `set(files) <= expected` still rejects stray files. The authority, sign-off and manifest are required in the commit. `ls-tree` shows every expected file exists at the commit. Every manifest artifact digest is re-verified from the commit's blobs. Residual gap: a file inherited unchanged from 2.0.0 is checked only through the manifest digest. The manifest itself is checked via `authority_sha256` and the required presence of the manifest in the diff. Not a regression.
- `test_record_commit_is_last_change_of_the_record` (reply test, 332-345): the guarantee holds. It asserts that the last record commit is a descendant of `publication_commit` and touches only the record. See IN-02 for the circularity.

## Info

### IN-01: Dead FAIL branches in certification
**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:~366-368`
**Issue:** `semantic['result']` and `negative['result']` have `'FAIL'` branches, but `build_all_outputs` raises before them when `conflicts` is non-empty or a mutation is accepted. `all_rejected` is always True.
**Fix:** Drop the branches, or stop raising and let the FAIL certification be emitted (and fail the publish afterwards).

### IN-02: Reply test asserts the resolver against itself
**File:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py:344-345`
**Issue:** `MODULE.resolve_record_commit() == last` re-runs the same `git log` that computed `last`. It cannot fail independently of line 338.
**Fix:** Drop it, or assert the pin against a literal recorded in the publication notes. `git diff-tree ... .split()` also breaks on paths with whitespace. Use `-z` or `splitlines()`.

### IN-03: Hard-coded claims in the reply history note
**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:30, 82`
**Issue:** `ENFORCED_GATES` and `purpose` are static prose, and `len(enforced_gates) == 4` is asserted. Nothing binds the claim "four gates enforced" to the code, so it can drift from reality.
**Fix:** Add a test that maps each statement to an existing negative mutation or gate id (for example the `signoff_role_hayes_developer` mutation).

### IN-04: Local manifest key access can raise non-domain errors
**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:~505-508`
**Issue:** `manifest['artifacts']` and `art['relative_path']` raise bare KeyError on a malformed manifest instead of `AuthorityError`. This is still fail-closed, but it conflicts with the project error convention.
**Fix:** Guard with `isinstance` checks and raise `AuthorityError`.

---

_Reviewed: 2026-10-14_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
