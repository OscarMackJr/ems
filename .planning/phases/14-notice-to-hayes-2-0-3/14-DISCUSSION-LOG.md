# Phase 14: Notice to Hayes (2.0.3) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-17
**Phase:** 14-notice-to-hayes-2-0-3
**Areas discussed:** Running the mutations, What the notice says, Verify-at-pin guidance, Builder form and gates

---

## Running the mutations

| Option | Description | Selected |
|--------|-------------|----------|
| Pinned publisher blob | git_show publisher (and decisions builder) at 1544dc1, run run_mutations on frozen inputs | ✓ |
| Live publisher, digest-guarded | Import live publisher, require LF digest = manifest | |
| Own mutation list in builder | Builder carries its own copy of mutations | |

| Option | Description | Selected |
|--------|-------------|----------|
| Rerun equals recorded | All rejected, result PASS, rerun list equals frozen file entry for entry | ✓ |
| Rerun only | All rejected; frozen file used only for count | |
| You decide | Planner chooses | |

| Option | Description | Selected |
|--------|-------------|----------|
| Per-mutation list in JSON | JSON lists id + rejected_by; Markdown gives count | ✓ |
| List in both | Markdown lists every id too | |
| Count only | As 2.0.2, backed by rerun | |

---

## What the notice says

| Option | Description | Selected |
|--------|-------------|----------|
| Replaces any earlier pin | 1544dc1 replaces ae15c74 and 31addfa | ✓ |
| Replaces ae15c74 only | Assumes 2.0.2 notice acted on | |
| 2.0.2 notice was never sent | Follow-up to the 2.0.1 reply | |

| Option | Description | Selected |
|--------|-------------|----------|
| Repeat, computed | Raw vs LF sha256 shown per RAW_BYTES file | ✓ |
| One-line pointer only | Refer to 2.0.2 notice | |
| Omit | Not relevant | |

| Option | Description | Selected |
|--------|-------------|----------|
| Derived data + fixed line | Derived diff + one plain line naming verification changes | ✓ |
| Derived data only | No verification line | |
| Full change list | Itemise each requirement | |

| Option | Description | Selected |
|--------|-------------|----------|
| All 7, each recomputed | With the commit recomputed at | ✓ |
| You decide | Planner chooses shape | |

---

## Verify-at-pin guidance

| Option | Description | Selected |
|--------|-------------|----------|
| Full sequence | Clone, checkout, install, --validate --at-pin; prerequisites | ✓ |
| Validate line only | Two validate commands | |

| Option | Description | Selected |
|--------|-------------|----------|
| 87a46d1, or any later commit | Record commit named, descendants also pass | ✓ |
| The notice's own commit | Single checkout | |

| Option | Description | Selected |
|--------|-------------|----------|
| Per-outcome table | Meaning of each result, deferred text quoted from pinned publisher | ✓ |
| Brief prose | One sentence per command | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, as a third step | Hayes runs the notice --validate | ✓ |
| No | Authority only | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, as a fixed constant | https://github.com/OscarMackJr/ems.git | ✓ |
| Placeholder | Hayes fills in | |

---

## Builder form and gates

| Option | Description | Selected |
|--------|-------------|----------|
| New standalone file | notice_2_0_3 builder with own frozen constants | ✓ |
| Shared helper module | Touches frozen 2.0.2 builder | |

| Option | Description | Selected |
|--------|-------------|----------|
| Live file now, freeze later | Committed schema byte-compared to builder function | ✓ |
| Freeze at commit | Schema commit constant as in 2.0.2 | |

| Option | Description | Selected |
|--------|-------------|----------|
| Same as Phase 10 | Blocking Markdown review, blocking push, CI green; no PR/merge/tag | ✓ |
| Also open a PR | PR to main after CI | |

| Option | Description | Selected |
|--------|-------------|----------|
| Add validator + tests | CI validator entry + per-claim tests with specific match | ✓ |
| Tests only | No CI entry | |

---

## Claude's Discretion

- Names, JSON shape, exact wording of the fixed line and outcome table, commit split.

## Deferred Ideas

- Freezing the notice schema at a commit constant; PR/merge/tag; previously deferred review items.
