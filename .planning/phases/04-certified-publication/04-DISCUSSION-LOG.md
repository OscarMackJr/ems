# Phase 4: Certified Publication - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-14
**Phase:** 4-Certified Publication
**Areas discussed:** Review debt & line endings, What a decided control carries, Output location & determinism, Publication commit & sign-off

In every question the user picked the recommended option. No free-text notes were given.

---

## Review debt & line endings

| Question | Options | Selected |
|----------|---------|----------|
| Which review findings to fix | CR-01..03 + all WR / CR only / CR + WR + Info | CR-01..03 + all WR ✓ |
| EOL pinning | Narrow .gitattributes / Broad .gitattributes / Normalise in code only | Narrow .gitattributes ✓ |
| Digest basis | LF-normalised, stated / Raw bytes + .gitattributes / LF sha256 + git blob ids | LF-normalised, stated ✓ |
| v1 files in .gitattributes | No, leave v1 alone / Yes, include v1 | No, leave v1 alone ✓ |
| Where fixes land | Separate earlier commits / Fold into publication commit | Separate earlier commits ✓ |
| Rewriting frozen decisions file | Regenerate, content unchanged / Never rewrite | Regenerate, content unchanged ✓ |

---

## What a decided control carries

| Question | Options | Selected |
|----------|---------|----------|
| AA4 id placement | Authority field + top-level list / Authority field only / Also append to decision_ids | Authority field + top-level list ✓ |
| Link to decision records | Path + LF sha256 in lineage / Path only | Path + LF sha256 in lineage ✓ |
| Row content | Lean rows / Copy decided rationale into rows | Lean rows ✓ |
| Decided-set strictness | Pin exact 21 ids in validator / Derive from records | Pin exact 21 ids ✓ |
| 59-vs-v1 proof | Field-by-field diff in validator and test / Test only | Field-by-field diff ✓ |

---

## Output location & determinism

| Question | Options | Selected |
|----------|---------|----------|
| Output location | New ems-aa3-v2/ force-added / Tracked registry/ files / Overwrite ems-aa3/ | New ems-aa3-v2/ ✓ |
| Timestamps | Fixed publication date / now() like v1 | Fixed publication date ✓ |
| Reproducibility check | --validate rebuilds and compares / Manifest digest check only | --validate rebuilds and compares ✓ |
| Output set | Mirror v1 set + decision traceability / Minimal set | Mirror v1 + traceability ✓ |
| Inputs | Tracked inputs only / Allow local AA2 files | Tracked inputs only ✓ |

---

## Publication commit & sign-off

| Question | Options | Selected |
|----------|---------|----------|
| Authority sign-off | Blocking checkpoint, recorded / Checkpoint, not recorded / No sign-off | Blocking checkpoint, recorded ✓ |
| Publication commit content | Generated outputs only / Code + outputs together | Generated outputs only ✓ |
| Recording the publication SHA | Follow-up record + test / Leave to Phase 5 / Annotated git tag | Follow-up record + test ✓ |
| Push/merge | Nothing; authority pushes / Push branch at end | Nothing; authority pushes ✓ |

---

## Claude's Discretion

- Names for the new id list, lineage entry, normalisation field, v2 output files, sign-off record and publication record
- Whether to extend the v2 publisher or add a sibling script, and the CLI flag names
- Where the shared LF digest helper lives
- How tests skip before the publication commit exists (no red tests between commits)
- How many review-fix commits there are, and their order
- The `published_on` value and the wording of the sign-off summary

## Deferred Ideas

- Phase 3 review Info items IN-01..05
- Broad or v1-inclusive .gitattributes
- Git tag, push and merge (left to the authority)
- Rationale or scope-note rulings in authority rows
