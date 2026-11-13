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

## Milestone: v1.1.0 — Authority 2.0.2 Lineage Correction

**Shipped:** 2026-11-13
**Phases:** 4 (7-10) | **Plans:** 17 | **Commits:** 107 (2026-10-15 → 2026-11-12, including 2 quick tasks)

### What Was Built
- The AA1 manifest was committed under `-text`, and each `source_lineage` digest got its own normalisation scope, recomputed by `validate_lineage`.
- Five gate fixes:
  - a mandatory, commit-verified publication record;
  - mutation gates that count only `AuthorityError` rejections;
  - a pinned catalog read;
  - a shallow-clone guard;
  - `norm_templated` uniqueness.
- The v2 schema was closed (29 mutations).
- Authority 2.0.2 was published at `ae15c74`, with the decisions digest unchanged and CI green.
- A generated, validated notice to Hayes, `052f0f1`.

### What Worked
- One republication after all code changes, with the red window declared in advance: the red set stayed at the 3 accepted tests until `ae15c74`, and then 720 passed.
- Code review in each phase before the publication phase. CR-01 and WR-01/02 from Phase 8 were closed before 2.0.2 shipped, which applies v1.0.0 lesson 1.
- Generating the notice from the published authority and validating it against that authority, with no hand-written claims about enforcement (applies v1.0.0 lesson 2).

### What Was Inefficient
- A commit cannot record its own SHA. Plain `--validate` therefore fails at the pinned commit by design, and the notice does not explain how to verify at the pin.
- Frozen validators (the reply and the notice) still import live publisher constants. A future publisher change could break documents that should never change.
- Most SUMMARY files used `requirements:` instead of `requirements-completed:`, so the tooling under-reported requirement coverage at audit.

### Patterns Established
- Per-digest `RAW_BYTES` / `CRLF_TO_LF` declarations, so a digest cannot be read under the wrong scope.
- A frozen reference (pinned commit) for shared registries that an authority depends on.
- `--pre-publication` as an explicit, named mode in place of silent skips.

### Key Lessons
1. Design the verification path at the pinned commit before publishing. Hayes reads at the pin, not at the record commit.
2. Frozen documents need frozen validators. Copy the constants they depend on at freeze time instead of importing live code.
3. Use the canonical SUMMARY frontmatter keys so that audits can count requirements mechanically.

### Cost Observations
- As in v1.0.0, tests and validators ran from the orchestrator, because Bash and subagent PowerShell are unavailable here.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Key Change |
|-----------|--------|------------|
| v1.0.0 | 6 | Human-gated authority publication with blind drafting; tech-debt phase inserted after review |
| v1.1.0 | 4 | All code changes first, then one republication with a declared red window; review before publication |

### Cumulative Quality

| Milestone | Archive-assessment tests | Validators |
|-----------|--------------------------|------------|
| v1.0.0 | 492 passing | 5 `--validate` CLIs PASS |
| v1.1.0 | 720 passing | `--validate` PASS (authority at the record commit, notice) |

### Top Lessons (Verified Across Milestones)

1. Review before publication. v1.0.0 needed an extra phase because review came after publication; v1.1.0 closed its findings before publishing.
2. Plan the hash-certification red window explicitly. Done in both milestones; it held in v1.1.0.
3. Generate external documents from the authority and never hand-write claims about enforcement.
