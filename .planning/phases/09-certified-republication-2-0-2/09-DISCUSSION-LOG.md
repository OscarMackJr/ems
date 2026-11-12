# Phase 9: Certified Republication 2.0.2 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-12
**Phase:** 09-certified-republication-2-0-2
**Areas discussed:** Reply after 2.0.2, CI evidence (PUB-09), Supersession lineage, Sign-off summary

---

## Reply after 2.0.2

| Option | Description | Selected |
|--------|-------------|----------|
| Freeze to 2.0.1 | Reply bytes unchanged; validator rebuilds from 2.0.1 inputs via git_show | ✓ |
| Regenerate for 2.0.2 | Rebuild reply citing 2.0.2 after record commit | |
| Drop from CI | Remove reply --validate step | |

| Option | Description | Selected |
|--------|-------------|----------|
| Named constants | 2.0.1 anchors pinned in the reply script | ✓ |
| From reply's own pin | Read commits from the committed reply JSON | |

**User's choice:** Freeze to 2.0.1, anchored by named constants.

---

## CI evidence (PUB-09)

| Option | Description | Selected |
|--------|-------------|----------|
| Green on record commit | CI on the record commit plus a byte-identity check of the publication files | ✓ |
| Pre-pub CI mode | workflow_dispatch input running --pre-publication on the publication commit | |
| Auto-detect in CI | Plain --validate falls back to pre-pub (reverses 08 D-02) | |

| Option | Description | Selected |
|--------|-------------|----------|
| Claude, after a checkpoint | Push with token workaround, dispatch, wait, record | ✓ |
| You push and dispatch | Claude prints commands | |
| Open a PR | Push and open a PR to main | |

| Option | Description | Selected |
|--------|-------------|----------|
| Planning docs only | 09-VERIFICATION.md and STATE.md | ✓ |
| Tracked registry field | CI evidence field in the record or a new file | |

---

## Supersession lineage

| Option | Description | Selected |
|--------|-------------|----------|
| 2.0.1 only | SUPERSEDED_V2_0_1 replaces SUPERSEDED_V2_0_0 | ✓ |
| 2.0.1 + 2.0.0 anchor | Extra decisions_origin entry pinning 2.0.0 | |

| Option | Description | Selected |
|--------|-------------|----------|
| Validator + pytest | 80-row comparison with 2.0.1 via git_show, fail closed | ✓ |
| Pytest only | Test that skips on shallow clones | |

---

## Sign-off summary

| Option | Description | Selected |
|--------|-------------|----------|
| Add a 'what changed' list | Lineage, gates, schema, row-compare result | ✓ |
| Same as 2.0.1 | Only update the supersedes line | |

| Option | Description | Selected |
|--------|-------------|----------|
| Derived where possible | Counts and facts computed; fixed line for the gate fixes | ✓ |
| Fixed text | Static paragraph | |

---

## Claude's Discretion

- Constant and helper names; how the code commits are split; whether the byte-identity check is a pytest or a verification step; keeping the 2.0.0 comparison test.

## Deferred Ideas

- Pre-publication CI mode; a tracked CI-evidence field; a 2.0.0 decisions_origin anchor; a PR, merge or tag; regenerating the reply.
