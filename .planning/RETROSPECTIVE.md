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

## Milestone: v1.2.0 — Authority 2.0.3 Verification Hardening

**Shipped:** 2026-11-18
**Phases:** 5 (11-15) | **Plans:** 24 | **Commits:** 128 (2026-11-14 → 2026-11-18, including 1 quick task)

### What Was Built
- Frozen validators. The DEMO3 reply (2.0.1) and the 2.0.2 notice read only git-pinned constants. A missing history fails closed. With `EMS_FAIL_ON_SKIP=1`, every skip fails, including collection-level skips.
- Verify at the pin:
  - `--validate --at-pin` binds the pinned tree to HEAD blobs and names the one check it defers.
  - Plain `--validate` checks ancestry, byte identity, and the publisher-script digest.
  - Malformed input raises domain errors, with schema validation first.
- Authority 2.0.3 was published at `1544dc1` (record commit `87a46d1`) with the decisions digest unchanged and CI green.
- The 2.0.3 notice gives Hayes a three-step verify sequence. Its claims are enforced: the 29 mutations are rerun, the 7 lineage digests are recomputed, and raw ≠ LF is computed.
- Phase 15 and quick task 261118-cgq fixed the long-path failure in notice step 3 and the step 2 wording, and made the deep-root test skip-free.

### What Worked
- Both v1.1.0 lessons were applied directly. Phase 12 built verification at the pin before the republication. Phase 11 froze the validators before any publisher edit, so the reply and the 2.0.2 notice stayed green throughout.
- Gap closure inside phases: 11-05/11-06 and 12-08 (CR-01) closed verifier gaps before moving on.
- Running the milestone audit twice. The first audit found two notice warnings, which led to Phase 15. The re-audit after Phase 15 found that the new Windows-only `skipif` would fail CI under the skip guard (B-1). Both were fixed before close.
- The skip guard proved its worth: CI caught a skip that local Windows runs could never show.

### What Was Inefficient
- Phase 15's verifier marked the Windows-only test "skipped on CI" without checking it against the project's own skip guard, so the CI break surfaced only at the re-audit.
- The B-1 fix went through two rounds. The executor's version had a check that could never fail. Removing it also removed the evidence that `--` is the fix (N-1).
- On this machine Git's `sh.exe` began failing on every local `git clone` during the milestone. Clone-based tests could not run locally, so CI became the only full run.
- At close, the SDK's one-line summary extraction returned meaningless lines from SUMMARY bodies, and the open-artifact scanner flagged complete quick tasks as `missing`.

### Patterns Established
- `--validate --at-pin` as a named mode, with its deferred check stated in its output.
- External notices state their verification steps, and the validator checks each claim.
- Platform-specific tests make a real assertion on every platform instead of skipping.

### Key Lessons
1. Treat the CI skip guard as part of the definition of done. A `skipif` in the archive suite is a CI failure, so verifiers should check skip markers against `EMS_FAIL_ON_SKIP`.
2. When you remove an assertion that cannot fail, replace it with one that can. Do not just delete it.
3. Push and run CI before auditing, so the audit sees the same tree Hayes will see.

### Cost Observations
- As in v1.0.0 and v1.1.0, tests and validators ran from the orchestrator, because subagents lack PowerShell and Bash is unreliable here.
- The re-audit after the fix used one focused, delta-scoped integration check instead of a full re-run.

---

## Milestone: v1.3.0 — Authority 2.0.4 Tech-Debt Closure

**Closed:** 2026-11-22 (partial: Phase 16 and SEC-03 shipped; Phases 17-19 deferred)
**Phases:** 1 of 4 (16) | **Plans:** 5 executed, 9 planned and not executed (Phase 17) | **Commits:** 44 (2026-11-18 → 2026-11-22, including 7 quick tasks)

### What Was Built
- Honest baseline and deep-root tests (BASE-01..04). The D-10 assertion survives the publication commit, and the deep-root `git_show` test can fail.
- Review closure (GATE-13..15): each 12/14/15-REVIEW info item is fixed, closed with a reason or carried, as recorded in `16-REVIEW-CLOSURE.md`.
- Bookkeeping (BOOK-01/02).
- SEC-03 as quick task 261122-v8y: the CI secret scan covers `*.md`, with a `git grep -E` parity guard and a positive control.
- Demo preparation: the demo pin tag, the 2.0.3 notice send record, working-tree and branch cleanup, and a rehearsed demo script.

### What Worked
- Asking what the consumer will pin before republishing. Once Oscar Mack decided that Hayes pins 2.0.3, a 2.0.4 that changes no decision had no reader, and stopping avoided a red window, a sign-off and a notice for nothing.
- Splitting off a change that touches no certified path (SEC-03) so it could ship without a republication.
- Parking Phase 17 behind the demo pin kept the demo commit stable while planning continued.

### What Was Inefficient
- Phase 17 was fully planned (context, research, patterns, 9 plans and a plan-check round) before the consumer question was asked. That planning is now on hold.
- A pasted milestone-close message from the Hayes session was briefly read as describing EMS.
- Local runs stayed unreliable: the `git clone` sh.exe crash and a CRLF working copy of the 2.0.3 notice files gave 4 local failures that CI did not reproduce.

### Patterns Established
- A republication needs a consumer. Check which version the consumer will pin before planning one.
- A change that touches no certified path (CI, tests) can ship outside the republication window.
- Record cross-repository status (the Hayes close, the Hayes pin) as dated, attributed STATE entries.

### Key Lessons
1. Ask "who will pin this?" at milestone start, not after the plans are written.
2. Treat CI `workflow_dispatch` as the authoritative full run on this machine; local clone and EOL failures need a named cause before they are dismissed.
3. Keep deferred plans in place with a re-check note, rather than deleting them or executing them speculatively.

### Cost Observations
- The close and SEC-03 ran inline in the main session; the planning-only and CI-only changes did not need subagents.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Key Change |
|-----------|--------|------------|
| v1.0.0 | 6 | Human-gated authority publication with blind drafting; tech-debt phase inserted after review |
| v1.1.0 | 4 | All code changes first, then one republication with a declared red window; review before publication |
| v1.2.0 | 5 | Frozen validators before publisher edits; verify-at-pin designed before publishing; audit run again after each fix |
| v1.3.0 | 1 of 4 | Republication dropped once the consumer chose to pin 2.0.3; work that touches no certified path shipped separately |

### Cumulative Quality

| Milestone | Archive-assessment tests | Validators |
|-----------|--------------------------|------------|
| v1.0.0 | 492 passing | 5 `--validate` CLIs PASS |
| v1.1.0 | 720 passing | `--validate` PASS (authority at the record commit, notice) |
| v1.2.0 | 1121 passing, 0 skipped (CI) | 7 `--validate` PASS in CI; `--at-pin` PASS at `1544dc1` |
| v1.3.0 | 1148 passing, 0 skipped (CI run `45108276889`) | 7 `--validate` PASS in CI at `d0beb7a` |

### Top Lessons (Verified Across Milestones)

1. Review before publication. v1.0.0 needed an extra phase because review came after publication; v1.1.0 closed its findings before publishing.
2. Plan the hash-certification red window explicitly. Done in both milestones; it held in v1.1.0.
3. Generate external documents from the authority and never hand-write claims about enforcement. In v1.2.0 the validator also enforces those claims.
4. Freeze anything already sent. v1.1.0 identified the risk, and v1.2.0 froze the validators before touching the publisher.
