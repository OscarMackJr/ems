# Phase 12: Verify-at-Pin and Gate Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-16
**Phase:** 12-verify-at-pin-and-gate-hardening
**Areas discussed:** Verify-at-pin mode, Byte-identity scope, Publisher digest rule, WR-05 skip-hook noise

---

## Verify-at-pin mode

| Option | Description | Selected |
|--------|-------------|----------|
| Rename to --at-pin | `--validate --at-pin` replaces `--pre-publication`. One mode, a name that makes sense to Hayes | ✓ |
| Keep --pre-publication | No rename. Hayes runs `--validate --pre-publication` at the pin | |
| Add --at-pin as alias | Both flags run the same code | |

| Option | Description | Selected |
|--------|-------------|----------|
| From source_lineage.supersedes | Read from the authority's own validated supersedes entry; one source of truth | ✓ |
| Per-release constant | Use a `SUPERSEDED_V2_0_2` constant directly | |

| Option | Description | Selected |
|--------|-------------|----------|
| JSON with deferred list | `{"status":"PASS","mode":"AT_PIN","deferred":[...]}`; plain `--validate` still prints `PASS` | ✓ |
| PASS plus a text line | `PASS` followed by a 'deferred: ...' line | |

| Option | Description | Selected |
|--------|-------------|----------|
| Fail on dirty publication paths | `git status --porcelain` on the publication paths; fail if modified or untracked | ✓ |
| No cleanliness check | Rely on the byte and digest checks | |

**User's choice:** All recommended options.

---

## Byte-identity scope

| Option | Description | Selected |
|--------|-------------|----------|
| The 10 publication files | AUTHORITY, SCHEMA, SIGNOFF and every file in OUT, from the path constants | ✓ |
| Manifest artifacts list | Whatever the manifest names | |
| 10 files + publisher script | Also require the publisher script to be unchanged | |

| Option | Description | Selected |
|--------|-------------|----------|
| Git blobs pub vs HEAD + ancestry | `merge-base --is-ancestor`, then compare `git show` at pub and at HEAD | ✓ |
| Working-tree LF vs pub blob | Compare working-tree files with the pub blobs; no ancestry check | |

**User's choice:** All recommended options.

---

## Publisher digest rule

| Option | Description | Selected |
|--------|-------------|----------|
| Both live and pinned | Live script and pub-commit script must both equal the manifest digest; later edits turn it red until republication | ✓ |
| Pinned blob only | Only the pub-commit script must equal the digest | |
| Live script only | Only the live file must equal the digest | |

| Option | Description | Selected |
|--------|-------------|----------|
| Live script == manifest (at pin) | At the pin the live script is the pinned one, guaranteed by the clean-tree check | ✓ |
| Defer it like the record binding | A second deferred item | |

**User's choice:** All recommended options.

---

## WR-05 skip-hook noise

| Option | Description | Selected |
|--------|-------------|----------|
| Fold in: narrow CI + scope hook | CI targets `tests/test_archive_assessment_*.py`; hook scoped to archive modules; guard test | ✓ |
| Fold in: narrow CI only | Change only the CI target | |
| Defer | Record WR-05 for after 2.0.3 | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, with WR-05 (IN-08/IN-09) | Wording fixes in `tests/aa_history.py` in the same commit | ✓ |
| Defer | Leave them for later | |

**User's choice:** All recommended options.

---

## Claude's Discretion

- Helper names, deferred-check wording and error messages.
- How GATE-07..10 are split into commits. The test/CI commit goes first while everything is green.
- Whether at-pin mode and plain mode share one function.

## Deferred Ideas

- 11-REVIEW IN-01..IN-07 (frozen-builder and test polish): after 2.0.3.
- V2-01 and V2-02: still deferred per PROJECT.md.
