# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0.0 — Not-Applicable Rule Publication

**Shipped:** 2026-10-15
**Phases:** 6 | **Plans:** 31 | **Commits:** 132 (2026-10-13 → 2026-10-15)

### What Was Built
- A v2 applicability rule shape with three decision states and a four-field KNOWN_TRUE/KNOWN_FALSE vocabulary
- 21 blind proposals, 21 individual governance decisions (AA4-GOV-001..021), each with the dual-role statement
- Authority 2.0.1 at 31addfa: certified, hash-traced, 26 executed negative mutations; 21 decided, 59 undecided
- The DEMO3-W1-REQ-001 reply, generated from the authority and validated against it

### What Worked
- The fixed order (shape → blind draft → human decisions → publish → reply), each step in its own commit, so git history shows the order
- Human gates at the points that matter: field-definition wording, 21 individual dispositions, sign-off, and reply read-through
- Generating the reply from the authority (`build_reply` raises if any row disagrees with its record), so the prose and the data cannot drift on per-control content

### What Was Inefficient
- Code review after Phases 1-4 surfaced fail-open gates (CRLF digests, the Hayes developer role accepted at sign-off, the publisher not validating its decisions), which needed a whole extra phase (6) and a republish
- Hash certification of the live publisher script made every publisher edit turn real-file tests red until republication; Phase 6 plans first assumed green between commits (red set was 18, not 5)
- Reply prose about enforcement ("the schema rejects unknown fields") was hand-written, not derived from the code, and overstated it; caught only at milestone audit

### Patterns Established
- LF-normalised SHA-256 (`lf_digest`) plus `.gitattributes` for every certified input
- Executed mutation harness: each negative invariant is run, and the validator that rejects it is recorded
- Stage by explicit path only; unrelated working-tree changes never enter a project commit
- Run pytest with `-p no:cacheprovider --basetemp=.pytest-temp/<name>` on this machine

### Key Lessons
1. Run code review before the first publication, not after: a fail-open gate found after publication costs a version bump and a new sign-off.
2. Any sentence in an external reply that describes what the code enforces should be checked against the code (or generated from it) before read-through.
3. When a manifest pins a live script's digest, plan the red-test window explicitly; never paper over it with skips.
4. On this machine Bash is broken and GSD subagents have no PowerShell, so tests and validators must run from the orchestrator.

### Cost Observations
- Notable: the integration checker could only trace statically; the orchestrator had to run the 492 tests and the five validators itself

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Key Change |
|-----------|--------|------------|
| v1.0.0 | 6 | Human-gated authority publication with blind drafting; tech-debt phase inserted after review |

### Cumulative Quality

| Milestone | Archive-assessment tests | Validators |
|-----------|--------------------------|------------|
| v1.0.0 | 492 passing | 5 `--validate` CLIs PASS |

### Top Lessons (Verified Across Milestones)

1. (to be confirmed by later milestones)
