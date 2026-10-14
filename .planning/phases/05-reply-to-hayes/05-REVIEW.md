---
phase: 05-reply-to-hayes
reviewed: 2026-10-14T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
  - schemas/archive_assessment_demo3_w1_req_001_reply.schema.json
  - tests/test_archive_assessment_demo3_w1_req_001_reply.py
  - .gitattributes
findings:
  critical: 0
  warning: 7
  info: 6
  total: 13
status: issues_found
---

# Phase 5: Code Review Report

**Reviewed:** 2026-10-14
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Reviewed the DEMO3-W1-REQ-001 reply generator, its emitted schema, its pytest module and the `.gitattributes` LF additions. I also checked the read-only helpers the generator imports from `publish_archive_assessment_applicability_authority_v2.py`.

Current state: `pytest tests/test_archive_assessment_demo3_w1_req_001_reply.py` passes (17 tests), `--validate` prints PASS, and the committed schema equals `schema()`. The current reply data is correct.

The problems are in the guards that keep it correct:
- `--validate` anchors the authority and the manifest to the publication record. It does not anchor the sign-off, the decision records (the source of every "Reason:" line) or the reply schema file.
- Several mutation tests are tautological. They pass for any change and never exercise `validate_reply()`. I confirmed that `validate_reply_object()` accepts a reply with swapped AA4-GOV ids and an all-zero authority digest.
- The fixed prose has one claim that contradicts the authority's published resolution table.

No blocker was found. All 21 entries currently match the authority and the decision records.

## Warnings

### WR-01: Mutation tests are tautological and never exercise the real validator

**File:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py:40-47, 89-93, 116-119, 139-146`
**Issue:** `rejected()` returns `reply != build()` when `validate_reply_object` accepts the mutation. Any mutation makes the reply differ from a fresh build, so this branch is always true. The tests for swapped AA4 ids, the `KNOWN_TRUE` rule flip and the zeroed `authority_sha256` cannot fail. The comment says `validate_reply()` "turns [this] into a failure by byte comparison", but no test writes a mutated reply to disk and calls `validate_reply()`. The byte-comparison path is only exercised on the happy path. Probe result: `validate_reply_object` accepted a reply with `controls[0].authority` and `controls[1].authority` swapped and `pin.authority_sha256 = '0'*64`.
**Fix:** Run each schema-valid mutation through the real file-comparison path:
```python
def assert_validate_rejects(reply, monkeypatch, tmpdir):
    p = Path(tmpdir) / 'reply.json'
    V2.dump(p, reply)
    monkeypatch.setattr(MODULE, 'REPLY_JSON', p)
    with pytest.raises(REJECTS):
        MODULE.validate_reply()
```
Use a module-level `TemporaryDirectory` (per the Windows `tmp_path` note) and drop the `reply != build()` fallback.

### WR-02: `--validate` does not anchor the sign-off or the decision records, so reason lines and approver fields can drift while it prints PASS

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:196-211`
**Issue:** `validate_reply()` rebuilds the reply from the working-tree `SIGNOFF` and `GOVERNANCE_DECISIONS` and compares it with the committed reply. It then checks only the authority and manifest digests against the publication record. If someone edits `decided.rationale` and regenerates the reply, `--validate` still prints PASS, and the reply quotes a reason that differs from the record bound at `54a7fd0`. The same applies to `approval.approver` / `approval.role` in the sign-off: `build_reply` copies them unchecked, and the schema accepts any non-empty string. The manifest (sign-off digest) and the decision traceability (`decision_record_sha256`) do bind both files, but only `V2.validate_published()` checks them. That runs in pytest, not in this CLI, and CI does not run pytest.
**Fix:** Call the publisher's full check inside `validate_reply()`, or check the two digests directly:
```python
V2.validate_published()  # or:
man = {a['relative_path']: a['sha256'] for a in manifest['artifacts']}
if man.get(V2.rel(V2.SIGNOFF)) != V2.lf_digest(V2.SIGNOFF): raise V2.AuthorityError('sign-off differs from the published manifest')
trace = V2.load(V2.OUT / V2.N_TRACE)
if any(r['decision_record_sha256'] != V2.lf_digest(V2.GOVERNANCE_DECISIONS) for r in trace['decision_records']): raise V2.AuthorityError('decision records differ from the published traceability')
```
Also call `V2.validate_signoff(signoff, record['authority_sha256'])` in `build_reply`.

### WR-03: The committed reply schema is never compared with `schema()`

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:207-208, 237-241`
**Issue:** `validate_reply()` validates the reply against the on-disk schema and, separately, against the in-memory `schema()`. It never checks that the two are the same. A hand edit to `schemas/archive_assessment_demo3_w1_req_001_reply.schema.json` that loosens it would still pass `--validate`, and so would a stale file after `schema()` changes without `--emit-schema`. Hayes reads that file as the published contract. `--build` also does not regenerate it, so build and schema can drift. Unlike the v2 publisher's schema, no manifest digest binds this schema.
**Fix:**
```python
if V2.lf_bytes(REPLY_SCHEMA.read_bytes()) != V2.jtext(schema()).encode('utf-8'):
    raise V2.AuthorityError('reply schema differs from a fresh build')
```

### WR-04: The prose claim "No control resolves until..." contradicts the published resolution table

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:117-118` (rendered at `docs/DEMO3_W1_REQ_001_REPLY.md:68`)
**Issue:** The reply says "No control resolves until the target description carries the eight classification facts." The authority's `not_applicable_semantics.resolution` says `NO_RULE_WILL_BE_PUBLISHED` resolves to `APPLICABLE` with condition `ALWAYS`. `V2.resolve_applicability` returns `APPLICABLE` for those 18 controls with empty facts. A RULE_PUBLISHED control needs only its one named field, not all eight. The sentence just before it says "A control with NO_RULE_WILL_BE_PUBLISHED is applicable whatever the facts", so the two sentences conflict. Hayes treats EMS as the authority, so a citable EMS statement that disagrees with the EMS semantics block is a correctness defect in the reply. The wording follows D-15, but D-15 means the Hayes-side classification-prerequisites gate, not EMS semantics.
**Fix:** Say whose gate it is. For example: "Hayes's resolver resolves no control until the target description carries the eight classification facts (the per-row classification_prerequisites). Under the EMS resolution table alone, NO_RULE_WILL_BE_PUBLISHED is APPLICABLE whatever the facts." Then regenerate the reply.

### WR-05: Generated-file validation test skips silently when the reply is missing

**File:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py:181-186`
**Issue:** `@pytest.mark.skipif(not REAL_JSON.exists(), ...)` means that deleting `registry/archive_assessment_demo3_w1_req_001_reply.json` turns the D-02 byte-equality test into a skip instead of a failure. The files are committed deliverables now, so their absence is a defect. `validate_reply()` already raises "not generated" for that case.
**Fix:** Remove the `skipif` decorator.

### WR-06: `--push-check` always exits 0, including on "NOT on" and "UNKNOWN"

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:218-230`
**Issue:** The send gate (D-06) only prints its result. It returns exit 0 whether the publication commit is on the remote, not on it, or unknown. A wrapper or operator script cannot gate on it, which goes against the project's fail-closed CLI convention. Also, if `sha` is not present locally, `merge-base --is-ancestor` returns exit 128, and the script reports that as "NOT on" when the real state is "cannot determine".
**Fix:** Call `sys.exit(0)` only when the commit is on the remote branch. Otherwise exit non-zero, and handle `returncode not in (0, 1)` from `merge-base` as UNKNOWN.

### WR-07: `first_sentence` breaks on abbreviations and ignores newline sentence breaks

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:35-36`
**Issue:** The split `(?<=\.) (?=[A-Z])` cuts after any period followed by a space and a capital. Probe: `first_sentence('See e.g. Section 2. Next one.')` returns `'See e.g.'`. A period followed by a newline is not treated as a break, so the whole multi-line rationale is returned. That would also break the `  Reason:` list-item line in the Markdown. The current 21 rationales happen to be safe, and `test_first_sentence_for_all_records` checks only current data. A later superseding record (v2.0.1) could silently publish a truncated reason "copied word for word".
**Fix:** Fail closed when the result looks wrong:
```python
s = re.split(r'(?<=\.)\s+(?=[A-Z])', text, maxsplit=1)[0]
if '\n' in s or not s.endswith('.') or re.search(r'\b(e\.g|i\.e|etc|vs)\.$', s):
    raise V2.AuthorityError('rationale first sentence cannot be cut deterministically')
```
Add unit cases for an abbreviation, a newline and a text with no period.

## Info

### IN-01: Unused `manifest` parameter in `build_reply`

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:39`
**Issue:** `manifest` is accepted but never read. The pin's `manifest_sha256` comes from the publication record.
**Fix:** Remove the parameter, or use it (see WR-02).

### IN-02: Unused imports in the test module

**File:** `tests/test_archive_assessment_demo3_w1_req_001_reply.py:4, 7`
**Issue:** `json` and `tempfile` are imported but unused, so ruff F401 would flag them.
**Fix:** Remove them, or use `tempfile` for the module-level temp dir needed by WR-01.

### IN-03: Missing RULE_PUBLISHED row raises a bare `StopIteration`

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:56`
**Issue:** `next(...)` with no default raises `StopIteration`, not the domain `AuthorityError`, if no decided row has a rule.
**Fix:** Use `next((...), None)` and raise `V2.AuthorityError('no RULE_PUBLISHED row for the example')`.

### IN-04: Published-shape field names are hard-coded and not checked against the authority

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:72-75`
**Issue:** These values are constants or publisher constants, not read from the authority file: `per_control_fields`, `top_level_field`, `per_control_ids_field`, `semantics_block`, and `per_control_ids_carry` (which is `V2.DECISIONS`). D-02 asks that values be taken from the files. They match today: I checked that every row's `decision_ids` equals AA1-GOV-001..008 and that the top-level keys exist. Nothing would detect drift.
**Fix:** Assert that `top_level_field in authority`, `semantics_block in authority`, every field in `per_control_fields` is in each row, and every row's `decision_ids == V2.DECISIONS`.

### IN-05: Abbreviated record commit is typed, and the reply schema is loose

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:23, 172-178`
**Issue:** `RECORD_COMMIT_ABBREV = '0ce89f2'` is typed and published as a 7-character abbreviation. D-05 says values are "never typed", and an abbreviation can become ambiguous. Only the git-gated pytest checks it. The schema also leaves fields unconstrained that a Hayes-side consumer might rely on: `example_decided_row` is just `{'type': 'object'}`, `from_authority.roles` has no `minItems`/enum, `not_yet_decided.count` is not tied to 80 - 21, and AA4 authority uniqueness is not enforced.
**Fix:** Resolve the full SHA with `git log --diff-filter=A --format=%H -- <record>` at build time, or publish the full SHA. Tighten the schema (`roles` enum = `APPROVER_ROLES`, `count` const 59, `example_decided_row` reusing the control-item shape).

### IN-06: CLI flags are not mutually exclusive

**File:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py:233-244`
**Issue:** `--build --emit-schema` silently runs only `--emit-schema`.
**Fix:** Use `parser.add_mutually_exclusive_group(required=True)`.

---

_Reviewed: 2026-10-14_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
