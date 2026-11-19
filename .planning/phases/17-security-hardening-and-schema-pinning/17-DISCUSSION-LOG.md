# Phase 17: Security Hardening and Schema Pinning - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md. This log preserves the alternatives considered.

**Date:** 2026-11-18
**Phase:** 17-security-hardening-and-schema-pinning
**Areas discussed:** pinned-code checks (SEC-01/02), git seam isolation (SEC-04), sign-off scope (GATE-12), schema pin breadth (GATE-11)

---

## Pinned-code checks (SEC-01/02)

| Option | Description | Selected |
|--------|-------------|----------|
| 2.0.3 builder now + 2.0.4 later | Fix hash-before-exec in the 2.0.3 notice builder as a behaviour-only change. Phase 19 copies it. | ✓ |
| 2.0.4 path only | Leave the sent 2.0.3 builder as it is. | |

| Option | Description | Selected |
|--------|-------------|----------|
| Mirror GATE-06 | Add a `decisions_builder_script` manifest entry. Check the live builder in both modes and the builder at the publication commit in plain mode, before exec. | ✓ |
| Manifest digest, live check only | Check the live builder only. | |

| Option | Description | Selected |
|--------|-------------|----------|
| Frozen-constant digest | Use the LF digest of the builder blob at `1544dc1`, checked before exec in the 2.0.3 builder. | ✓ |
| No change for 2.0.3 | SEC-02 applies from 2.0.4 only. | |

**User's choice:** the recommended option in all three questions.

---

## Git seam isolation (SEC-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Publisher + 2.0.3 builder + tests | Also covers the `live_git_subprocess` shim and `aa_history.py`. Frozen builders are CLOSED. | ✓ |
| Publisher only | Applies to the publisher seam only. | |

| Option | Description | Selected |
|--------|-------------|----------|
| Env + replace + literal + no system/global config | Settings the seam needs are passed via `-c`. | ✓ |
| Env + replace + literal only | The WR-02 minimum. | |

| Option | Description | Selected |
|--------|-------------|----------|
| Copy in each script | Standalone pattern. A test asserts the copies agree. | ✓ |
| Shared module | One helper, outside the publisher digest. | |

**User's choice:** the recommended option in all three questions.

---

## Sign-off scope (GATE-12)

| Option | Description | Selected |
|--------|-------------|----------|
| Free text, no digests | Reject hex runs of 7 to 64 characters. The scope must name the id and version. | ✓ |
| Checked tokens | The scope must contain the id, version, digest and commit[:7], and all are checked. | |
| Exact generated string | The scope must equal a sentence the publisher generates. | |

| Option | Description | Selected |
|--------|-------------|----------|
| 2.0.4 forward only | Historical sign-offs validate under their own rules. | ✓ |
| You decide | | |

---

## Schema pin breadth (GATE-11)

| Option | Description | Selected |
|--------|-------------|----------|
| All fixed lineage digests | `supersedes` (both digests), `v1_baseline.sha256` and `governance_decisions.sha256` | ✓ |
| Supersedes only | The WR-02 minimum. | |

| Option | Description | Selected |
|--------|-------------|----------|
| From constants, test-cross-checked | `schema()` emits the values from constants. A test recomputes them from git. | ✓ |
| You decide | | |

---

## Claude's Discretion

- SEC-03 secret-scan mechanics
- `git show` vs `git cat-file blob`
- Hostile-env test mechanics
- Commit grouping and order
- Test names

## Deferred Ideas

- Phase 19: the 2.0.4 notice builder copies SEC-01 and SEC-04 and adds 15 IN-01.
- Out of scope: SEC-04 in the frozen reply and 2.0.2 notice builders.
