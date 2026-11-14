# Phase 11: Frozen Validators - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-14
**Phase:** 11-frozen-validators
**Areas discussed:** Freeze mechanism, Frozen CLI modes, Skip-to-fail scope, Proof of independence

---

## Freeze mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Local literals + git check | Builders copy needed constants/functions; pytest asserts equality with publisher blob at frozen commit | ✓ |
| Exec publisher from git | Load publisher at frozen commit at runtime | |
| Shared frozen module | One new module for both snapshots | |

| Option (helpers) | Description | Selected |
|--------|-------------|----------|
| Copy into each builder | Zero V2 imports | ✓ |
| Keep importing V2 for these | Freeze only semantic values | |

| Option (schema) | Description | Selected |
|--------|-------------|----------|
| Compare to schema at its commit | git_show equality, no regeneration | ✓ |
| Regenerate from frozen literals | Keep schema() | |

| Option (anchor) | Description | Selected |
|--------|-------------|----------|
| Publication commit | 31addfa / ae15c74 | ✓ |
| Artifact commit | e781f08 / notice commit | |

**User's choice:** all recommended options.

---

## Frozen CLI modes

| Option | Description | Selected |
|--------|-------------|----------|
| Remove; --validate only | No write path to frozen bytes | ✓ |
| Keep, but refuse with an error | Flags exit non-zero | |
| Keep, write only to a temp path | Diffing aid | |

| Option (--push-check) | Description | Selected |
|--------|-------------|----------|
| You decide | Keep if read-only and meaningful | ✓ |
| Keep unchanged | | |
| Remove | | |

---

## Skip-to-fail scope

| Option | Description | Selected |
|--------|-------------|----------|
| All archive_assessment tests | Every pinned-blob skip fails | ✓ |
| Reply, notice, publication only | | |

| Option (git_ready) | Description | Selected |
|--------|-------------|----------|
| Fail, unless explicitly opted out | Env var opt-out for local offline runs | ✓ |
| Fail, always | | |
| Keep the skips | | |

| Option (exist guards) | Description | Selected |
|--------|-------------|----------|
| Convert to fail | Artifacts are committed | ✓ |
| Leave them | | |

| Option (CI guard) | Description | Selected |
|--------|-------------|----------|
| Yes, fail on any skip | | ✓ |
| No, code changes are enough | | |

---

## Proof of independence

| Option | Description | Selected |
|--------|-------------|----------|
| Static + behavioural | AST no-import + mutated live publisher in sys.modules | ✓ |
| Static only | | |
| Behavioural only | | |

| Option (test rigor) | Description | Selected |
|--------|-------------|----------|
| Specific match + direct call | 10-REVIEW WR-03/IN-01 fixes | ✓ |
| Plus a mutation sweep | | |

| Option (reply tests) | Description | Selected |
|--------|-------------|----------|
| Yes, same treatment | | ✓ |
| Notice only | | |

---

## Claude's Discretion

- Reply `--push-check`: keep or remove (D-06)
- Opt-out env var name, `git_ready` de-duplication, CI skip-guard mechanism
- Helper/constant names, commit split

## Deferred Ideas

- Retrofit CLAIM-style enforcement to the 2.0.2 notice (Phase 14 covers 2.0.3 only)
- Mutation-sweep meta-test
- Runtime exec of the historical publisher
