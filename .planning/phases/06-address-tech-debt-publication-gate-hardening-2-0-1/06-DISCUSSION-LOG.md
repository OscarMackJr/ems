# Phase 6: Address tech debt: publication gate hardening (2.0.1) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-14
**Phase:** 06-address-tech-debt-publication-gate-hardening-2-0-1
**Areas discussed:** Fix scope, Version and files, Reply and pin order, Certification honesty

---

## Fix scope

| Option | Description | Selected |
|--------|-------------|----------|
| CR-01, CR-02 + all WR-01..10 | Every 04-REVIEW gate defect in one republish | ✓ |
| CR-01 + CR-02 only | Smallest change | |
| CRs + schema/certification WRs only | CR-01/02, WR-01..04; defer WR-05..10 | |

| Option (Phase 4 IN items) | Description | Selected |
|--------|-------------|----------|
| Only IN-01 and IN-07 | IN-01 falls out of CR-02; IN-07 is a gate | ✓ |
| All IN-01..07 | Clean everything | |
| None beyond CR-02 | Strict CR/WR | |

| Option (Phase 2 WR-01) | Description | Selected |
|--------|-------------|----------|
| Validate against catalog at drafting commit | Frozen files stop depending on the live catalog | ✓ |
| Defer | Not a publication gate | |

| Option (reply IN items + CLAUDE.md wording) | Description | Selected |
|--------|-------------|----------|
| Fix CLAUDE.md; reply IN only if reply regenerated | — | ✓ |
| Fix both | — | |
| Defer both | — | |

**User's choice:** All recommended options.

---

## Version and files

| Option | Description | Selected |
|--------|-------------|----------|
| 2.0.1 | Matches the reply's promise; data unchanged | ✓ |
| 2.1.0 | Treat stricter schema as minor shape change | |

| Option | Description | Selected |
|--------|-------------|----------|
| Overwrite v2 files in place | Same paths; 2.0.0 stays at 54a7fd0 | ✓ |
| Publish beside them | Both versions live in tree | |

| Option (WR-06) | Description | Selected |
|--------|-------------|----------|
| Record script digest at publication; PUBLISHED_ON into sign-off | Script-only edits no longer turn --validate red | ✓ |
| Keep live-digest rebuild | Strictest | |
| You decide | — | |

| Option (WR-05) | Description | Selected |
|--------|-------------|----------|
| Refuse unless --supersede-published | — | ✓ |
| Refuse unconditionally | — | |

| Option (lineage) | Description | Selected |
|--------|-------------|----------|
| supersedes = 2.0.0 @ 54a7fd0; v1 baseline as own field | — | ✓ |
| keep supersedes = v1; add previous_version | — | |

| Option (2.0.0 records) | Description | Selected |
|--------|-------------|----------|
| Overwrite; 2.0.0 stays in git | — | ✓ |
| Publication history file | — | |

**User's choice:** All recommended options.

---

## Reply and pin order

| Option | Description | Selected |
|--------|-------------|----------|
| Hold reply; regenerate for 2.0.1 | Hayes re-pins once | ✓ |
| Send 2.0.0 now; 2.0.1 follows | Two re-pins | |

| Option (disclosure) | Description | Selected |
|--------|-------------|----------|
| Short history note | Supersedes 2.0.0, gates now enforced, no decision changed | ✓ |
| Drop entirely | — | |
| Keep full WR-01 disclosure | — | |

| Option (no-change proof) | Description | Selected |
|--------|-------------|----------|
| Validator + test | Enforced, not asserted | ✓ |
| Test only | — | |

| Option (how to prove) | Description | Selected |
|--------|-------------|----------|
| Decisions-file digest in supersedes + git diff test when history available | — | ✓ |
| Always git show 54a7fd0 | Breaks shallow clones | |
| Frozen snapshot file | Extra tracked file | |

| Option (send gate) | Description | Selected |
|--------|-------------|----------|
| Same gate with new SHA + human read-through | — | ✓ |
| Gate only | — | |

**User's choice:** All recommended options.

---

## Certification honesty

| Option | Description | Selected |
|--------|-------------|----------|
| Publisher runs checks, records real outcomes | Fail closed on any accepted mutation | ✓ |
| Rename fields to cite pytest | — | |

| Option | Description | Selected |
|--------|-------------|----------|
| One list in publisher; pytest parametrizes | — | ✓ |
| You decide | — | |

| Option | Description | Selected |
|--------|-------------|----------|
| Per mutation: id, description, rejecting gate(s) | — | ✓ |
| Just id + REJECTED | — | |

**User's choice:** All recommended options.
**Notes:** Claude stated (not asked) that every gap proven in 04-REVIEW gets its own mutation (D-20).

---

## Claude's Discretion

- Shared-module vs lazy-import for the decisions validator
- Mechanism for Phase 2 WR-01 within the shallow-clone constraint
- Exact field names, mutation ids, gate labels
- Commit count and order (within D-21)
- Wording of the reply history note and sign-off summary

## Deferred Ideas

- Phase 4 IN-02..IN-06; Phase 2 WR-02..WR-10 and IN items; Phase 3 WR/IN items and amendment path
- Push, tag, send (EMS authority)
- V2-01 (other 59 controls), V2-02 (Hayes re-run)
