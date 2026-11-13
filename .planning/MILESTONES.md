# Milestones

## v1.1.0 Authority 2.0.2 Lineage Correction (Shipped: 2026-11-13)

**Delivered:** EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2, published at commit ae15c7458e49c8f55cc58c61bab04bc716aa9892. Each lineage digest now declares its own scope and can be recomputed from a committed file. The gates and schema fail closed. No applicability decision changed. A generated notice to Hayes asks it to re-pin.

**Phases completed:** 4 phases (7-10), 17 plans
**Git range:** 1ed5bd8 → c33abba (107 commits, 2026-10-15 → 2026-11-12, including 2 quick tasks); 36 non-planning files, +3,803 / −225 lines
**Tag:** none (Hayes pins by commit; same decision as v1.0.0)

**Key accomplishments:**

- AA1 manifest committed under `-text` (`bb7c067`, raw SHA-256 `f0da8e2e…`). Every `source_lineage` digest declares `RAW_BYTES` or `CRLF_TO_LF` and is recomputed by `validate_lineage`, which fails closed.
- Gates fail closed:
  - the publication record is mandatory and checked against its commit (with an explicit `--pre-publication` mode);
  - mutation gates count only `AuthorityError` rejections;
  - the catalog is read at the pinned commit `62a8955`;
  - a shallow clone makes the lookup fail with an explicit message;
  - cross-note uniqueness compares `norm_templated` forms.
- The v2 schema is closed at the top level, on rows and on `not_applicable_semantics`, and 29 mutations are rejected.
- 2.0.2 signed off by Oscar Mack and published at `ae15c74`, with the record commit at `a71257e`:
  - the decisions digest is unchanged (`4e746d1f…`), all 80 rows are identical to 2.0.1, and the counts stay at 21 decided and 59 undecided;
  - CI run `43332405316` is green;
  - the red window is closed (720 passed).
- A generated, `--validate`-checked notice to Hayes (`052f0f1`) cites 2.0.2 and names the 2.0.1 digest-scope error.

**Audit:** tech_debt. 14/14 requirements, 4/4 phases, integration 14/14, flows 1/1 ([v1.1.0-MILESTONE-AUDIT.md](./milestones/v1.1.0-MILESTONE-AUDIT.md)).
**Known deferred items at close:** 0 open artifacts. The scan flagged 3 v1.0-era quick tasks as `missing`, but all 3 have a complete SUMMARY. Tech debt is listed in the audit:
  - plain `--validate` fails at the pin `ae15c74` by design;
  - frozen validators load live publisher constants;
  - the publisher-script digest is checked only by pytest;
  - 10-REVIEW warnings are open.

---

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
