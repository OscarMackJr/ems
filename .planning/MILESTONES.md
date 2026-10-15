# Milestones

## v1.0.0 Not-Applicable Rule Publication (Shipped: 2026-10-15)

**Delivered:** An explicit, authority-backed applicability decision for each of the 21 controls requested by Hayes Verify (DEMO3-W1-REQ-001), published as EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1 at commit 31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb, with a reply that cites it.

**Phases completed:** 6 phases, 31 plans
**Git range:** 153cd05 → c288e49 (132 commits, 2026-10-13 → 2026-10-15); 38 non-planning files, +17,175 lines
**Tag:** none (Hayes pins by commit; a release-style tag was declined to avoid confusion with EMS release tags and authority versions)

**Key accomplishments:**

- A rule shape with machine checks: three decision states, a four-field vocabulary limited to KNOWN_TRUE/KNOWN_FALSE, semantics written out (UNKNOWN never resolves to not-applicable)
- 21 blind proposals drafted from the control catalog alone and committed before any decision (dc3b41c)
- 21 individual governance decisions AA4-GOV-001..021 by Oscar Mack, each with the dual-role statement
- Authority 2.0.1 certified and hash-traced at 31addfa: 21 decided (3 rules, 18 no-rule), 59 NOT_YET_DECIDED
- Publication gates hardened: LF-normalised hashing, exact sign-off role, decisions validator inside the publisher, 26 executed negative mutations
- DEMO3-W1-REQ-001 reply generated from the authority, wording approved; branch pushed, send condition met

**Audit:** tech_debt — 22/22 requirements, 6/6 phases, integration 8/8, flows 3/3 ([v1.0.0-MILESTONE-AUDIT.md](./milestones/v1.0.0-MILESTONE-AUDIT.md))
**Known deferred items at close:** 0 open artifacts; tech debt listed in the audit (06-REVIEW WR-01..WR-05, catalog live coupling, no CI execution of tests/validators)

---
