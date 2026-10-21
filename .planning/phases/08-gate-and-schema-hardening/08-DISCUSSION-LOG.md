# Phase 8 Discussion Log

**Date:** 2026-10-20
**Areas discussed:** Pre-publication mode, Mutation gate strictness, Catalog freezing, Shallow-clone lookup
**Claude's discretion:** GATE-05 (`norm_templated`), SCHEMA-07 (`additionalProperties: false`)

## Pre-publication mode
| Question | Options | Selected |
|----------|---------|----------|
| How the window is expressed | Explicit CLI flag / Implicit superseded match | Explicit CLI flag (`--pre-publication`) |
| Record absent in plain --validate | Fail / Fail unless flag | Fail |
| Verify publication_commit contains the bytes | Yes via git_show / No | Yes via git_show |

## Mutation gate strictness
| Question | Options | Selected |
|----------|---------|----------|
| What counts as rejection | Domain errors only / Domain + record crashes | Domain errors only |
| Mutations rejected only by crash | Harden validators / Stop and ask | Harden validators |
| Output detail | Keep shape / Add exception class | Keep shape |

## Catalog freezing
| Question | Options | Selected |
|----------|---------|----------|
| Frozen reference | Catalog at pinned commit / Embedded snapshot | Pinned commit |
| Pin commit | 62a8955 / d5c1a73 / 31addfa | 62a8955 |
| No git history | Fail closed / Skip with note | Fail closed |
| Proof tests | Both directions / Tamper only | Both |

The catalog's LF digest `12bb1a9d…` is identical at 62a8955, 31addfa and HEAD. Its last change was in d5c1a73 (2026-08-12).

## Shallow-clone lookup
| Question | Options | Selected |
|----------|---------|----------|
| Shallow behaviour | Detect and fail / Verify introducing commit / Both | Detect and fail |
| Output-neutral | Yes, no regeneration / Regenerate if needed | Yes |

## Deferred
- Exception class in negative-invariant output
- Introducing-commit verification for the reply record lookup
