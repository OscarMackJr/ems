# Requirements: EMS Not-Applicable Rule Publication — v1.3.0 Authority 2.0.4 Tech-Debt Closure

**Defined:** 2026-11-18
**Core Value:** For every one of the 21 requested controls, EMS publishes an explicit, machine-readable, authority-backed applicability decision that Hayes can cite — so that "EMS decided" is always distinguishable from "EMS has not decided yet".

**Source:** `.planning/milestones/v1.2.0-MILESTONE-AUDIT.md` (tech_debt) and the phase 11-15 REVIEW files.

**Invariant for every requirement:** decisions do not change. There are 21 decided controls (3 rules and 18 no-rule, `AA4-GOV-001`..`021`) and 59 `NOT_YET_DECIDED`, and the decisions digest stays `4e746d1f…`. The frozen reply (2.0.1) and 2.0.2 notice builders stay byte-unchanged.

## v1.3.0 Requirements

### Test Robustness (BASE)

- [ ] **BASE-01**: The D-10 baseline assertion passes at the next publication commit, the one Hayes pins, as well as at later commits. It does not demand that plain `--validate` returns PASS at a commit where the record cannot exist yet. (13-REVIEW WR-01)
- [ ] **BASE-02**: The deep-root `git_show` test is not tautological. On Windows with a deep root it asserts that `Filename too long` reproduces without `--`, and it fails loudly if that does not happen. On other platforms it asserts the `--` behaviour without claiming MAX_PATH coverage. The test runs no skips under `EMS_FAIL_ON_SKIP=1`. (N-1, quick-261118-cgq)
- [ ] **BASE-03**: The D-10 validate test checks the working tree under test, not committed HEAD. `outcome()` decodes subprocess output as UTF-8 and keeps stderr separate from stdout. (13-REVIEW IN-02, IN-03)
- [ ] **BASE-04**: The history-failure hint describes what `EMS_ALLOW_NO_HISTORY=1` actually skips. An unrecognised shallow-check output is reported verbatim. Both are fixed only where the code is outside the frozen builders; otherwise they are recorded as out of scope. (11-REVIEW IN-08, IN-09)

### Schema and Gates (GATE)

- [ ] **GATE-11**: The published schema pins the superseded digests, so a 2.0.4 authority that names different superseded 2.0.3/2.0.2 digests fails schema validation. (13-REVIEW WR-02)
- [ ] **GATE-12**: The sign-off `scope` no longer repeats a digest in unchecked free text; the digest is either removed or checked. (13-REVIEW IN-01)
- [ ] **GATE-13**: Each 12-REVIEW info item (IN-01..IN-07) is either fixed with a test or closed with a recorded reason:
  - IN-01: the plain-mode error message.
  - IN-02: the "HEAD is the publication commit" diagnosis.
  - IN-03: the at-pin wrong-record error points to plain mode.
  - IN-04: the shallow check runs before history reads.
  - IN-05: literal pathspecs.
  - IN-06: GATE-06 scope.
  - IN-07: weak assertions.
- [ ] **GATE-14**: Each 14-REVIEW info item (IN-01..IN-05) is either fixed with a test or closed with a recorded reason:
  - IN-01: unused helpers, and lineage recompute commits are cross-checked.
  - IN-02: malformed input raises a domain exception.
  - IN-03: `--build` writes atomically and refreshes the schema.
  - IN-04: the notice is decoupled from the input authority.
  - IN-05: test nits.
- [ ] **GATE-15**: Each 15-REVIEW info item is fixed:
  - IN-01: there is no absolute Windows path in the registry JSON string.
  - IN-02: the duplicated hint test is removed.
  - IN-03: the hint for a missing git binary does not tell the reader to fetch history.

### Security (SEC)

- [ ] **SEC-01**: The pinned publisher's digest is checked against the certification before the publisher is executed. A mismatch fails closed without running it. (Phase 14 security observation)
- [ ] **SEC-02**: The pinned decisions-builder blob has a manifest digest, and `--validate` checks it. (Phase 14 security observation)
- [ ] **SEC-03**: The CI secret-pattern scan covers `*.md` files. (Phase 14 security observation)
- [ ] **SEC-04**: The git seam runs isolated from the caller's environment:
  - It drops inherited `GIT_*` variables such as `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` and `GIT_OBJECT_DIRECTORY`.
  - It disables replace refs (`--no-replace-objects` / `GIT_NO_REPLACE_OBJECTS=1`).
  - It uses literal pathspecs.
  - A test shows that a hostile `GIT_*` environment cannot redirect a fail-closed check. (12-REVIEW WR-02 / AR-03)

### Publication (PUB)

- [ ] **PUB-13**: `EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.4` is published with certification, manifest and traceability, and it supersedes 2.0.3 at `1544dc1`. It is published once, after all code and schema changes.
- [ ] **PUB-14**: No decision changes. The decisions digest stays `4e746d1f…`, and all 80 rows are identical to 2.0.3.
- [ ] **PUB-15**: The publication commit contains only this milestone's deliberate changes. The CI `archive-assessment` job is green, with 0 skips, at both the publication commit and the shipped head. `--validate --at-pin` gives PASS at the pin, and plain `--validate` gives PASS at the record commit.

### Notice (NOTICE)

- [ ] **NOTICE-04**: A generated notice, checked by `--validate`, cites the 2.0.4 id, version and commit and gives Hayes the three-step verify sequence:
  - The step 1 clone command includes `-c core.longpaths=true` (W-3).
  - The line on plain `--validate` says exactly what it binds (W-4).
- [ ] **NOTICE-05**: When the notice is sent, the commit that was sent is recorded in a committed planning or registry artifact. The 2.0.3 send commit (91d8847 or later) is recorded too, if it was sent.

### Bookkeeping (BOOK)

- [ ] **BOOK-01**: The SUMMARY files for phases 11-13 carry `requirements-completed` frontmatter that matches the v1.2.0 traceability. Unrelated working-tree state in those files stays out of the commit.
- [ ] **BOOK-02**: The traceability table lists V2-01 and V2-02 as deferred.

## Future Requirements

- **V2-01**: Rule-or-no-rule decisions for the other 59 controls.
- **V2-02**: Hayes re-run confirmation (on the Hayes side).

## Out of Scope

| Item | Reason |
|------|--------|
| W-2: the frozen reply and 2.0.2 notice builders call `git show` without `--` | The frozen builders must stay byte-unchanged; affects only EMS-side Flow B under a deep Windows root |
| 11-REVIEW IN-01 (the reply has no publication-before-record ancestry check) and any fix that needs an edit to a frozen builder | Same reason: frozen historical validators |
| 11-REVIEW WR-03 ordering, and the imperative `pytest.xfail()` reported as xfailed | Accepted in 11-05 |
| 11-REVIEW WR-05 (the collection-skip guard is session-wide) | A warning, not in the selected tech debt; revisit if it bites |
| Any decision change | Decisions are unchanged by this milestone, as in v1.1.0 and v1.2.0 |
| Landing the unrelated uncommitted work in the tree | Kept out of this project's commits (project constraint) |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| V2-01 | — (future) | Deferred |
| V2-02 | — (future, Hayes-side) | Deferred |

**Coverage:**
- v1.3.0 requirements: 20 total
- Mapped to phases: 0 (filled by roadmap)

---
*Requirements defined: 2026-11-18*
*Last updated: 2026-11-18 after initial definition*
