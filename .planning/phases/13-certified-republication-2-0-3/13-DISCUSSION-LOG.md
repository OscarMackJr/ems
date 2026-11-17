# Phase 13: Certified Republication 2.0.3 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-17
**Phase:** 13-certified-republication-2-0-3
**Areas discussed:** CI evidence (SC3), At-pin proof (PIN-01), 'What changed' in sign-off, WR-03 + post-publish commits

---

## CI evidence (SC3)

**Which commit carries the green CI run?**

| Option | Description | Selected |
|--------|-------------|----------|
| Record commit | As in 2.0.2 (09 D-04). Plain `--validate` there proves byte identity to the publication commit (12 D-06). SC3 is reworded explicitly. No CI change. | ✓ |
| Add an at-pin CI step | Run `--validate --at-pin` in CI when HEAD is the publication commit. This is a CI and publisher change before publication. | |
| Both commits, at-pin manually | Green CI at the record commit, plus a recorded manual at-pin run. | |

**Should the PUB-12 commit-contents check be a test or a verification command?**

| Option | Description | Selected |
|--------|-------------|----------|
| Verification command | `git show --stat` of each commit is checked against `publication_paths()` and recorded in 13-VERIFICATION.md. | ✓ |
| Pytest | A permanent test, but it would be a test edit after publication. | |
| You decide | | |

**Follow-up:** the user confirmed that, with the WR-03 commit after the record commit, the CI evidence is the green run at that head SHA (record commit plus 1).

---

## At-pin proof (PIN-01)

**Where is `--validate --at-pin` run?**

| Option | Description | Selected |
|--------|-------------|----------|
| Both | The operator tree right after the publication commit, then a fresh full clone checked out at the publication SHA. | ✓ |
| Working tree only | As in 2.0.2. | |
| Fresh clone only | | |

**Where is the evidence recorded?**

| Option | Description | Selected |
|--------|-------------|----------|
| Planning docs only | 13-VERIFICATION.md and STATE.md (09 D-06). | ✓ |
| Also in the publication record | Changes the record's schema shape. | |

---

## 'What changed' in sign-off

**Is the existing "What changed in 2.0.3" section the one to sign off on?**

| Option | Description | Selected |
|--------|-------------|----------|
| Keep as is | No publisher change; derived facts plus one gate line. | ✓ |
| Add a frozen-validators line | Needs a publisher edit before the dry run. | |
| Trim the gate line | Needs a publisher edit before the dry run. | |

**How is the sign-off record written?**

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse 2.0.2 wording | The exact 2.0.2 dual-role statement and the approval date, written only after approval. | ✓ |
| I'll write the statement | | |

---

## WR-03 + post-publish commits

**Where does the WR-03 test fix land?**

| Option | Description | Selected |
|--------|-------------|----------|
| Test commit after record | A separate test-only commit before the push, so the record commit stays record-only. | ✓ |
| In the record commit | | |
| Defer to after milestone | | |

**Push and CI?**

| Option | Description | Selected |
|--------|-------------|----------|
| Same as 2.0.2 | A blocking go-ahead, then push, dispatch and wait, confirming green at the head SHA. No PR, merge or tag. | ✓ |
| I push myself | | |

---

## Claude's Discretion

- How the fresh clone is made (it must be full and non-shallow, at the publication SHA).
- How plan tasks are split around the human checkpoints.
- The wording of verification commands and evidence tables.

## Deferred Ideas

- WR-02 (`GIT_*` env scrubbing).
- 12-REVIEW IN-*, 11-REVIEW IN-*.
- `.gitattributes eol=lf`.
- V2-01 and V2-02.
