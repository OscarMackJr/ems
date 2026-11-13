# Phase 10: Notice to Hayes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-13
**Phase:** 10-notice-to-hayes
**Areas discussed:** Notice form and files, Where the content comes from, What the notice cites, Voice, date and send condition

---

## Notice form and files

| Option | Description | Selected |
|--------|-------------|----------|
| MD + JSON + schema | Same as the DEMO3 reply; JSON for Hayes; schema + byte rebuild in --validate | ✓ |
| Markdown only | Simpler; no machine-readable copy | |
| You decide | Claude picks | |

| Option | Description | Selected |
|--------|-------------|----------|
| New builder script | Imports V2 like the reply; frozen reply builder untouched | ✓ |
| Extend the reply builder | Fewer files; edits a just-frozen script | |

| Option | Description | Selected |
|--------|-------------|----------|
| Tied to the request | DEMO3_W1_REQ_001_NOTICE_2_0_2 | ✓ |
| Tied to the authority | EMS_AA3_2_0_2_REPIN_NOTICE | |
| You decide | Claude picks | |

**User's choice:** all recommended options.

---

## Where the content comes from

| Option | Description | Selected |
|--------|-------------|----------|
| Frozen to ae15c74 / a71257e | Constants + git_show from day one; fails closed without history | ✓ |
| Live files, freeze later | Simpler now; retrofit needed at next version | |

| Option | Description | Selected |
|--------|-------------|----------|
| Derived + fixed gate line | Computed from 2.0.2 artifacts; one fixed gate line; states AA1 RAW_BYTES (WR-03) | ✓ |
| Fixed prose, test-checked | Hand-written; can drift | |

| Option | Description | Selected |
|--------|-------------|----------|
| Derived from both authorities | Compare 2.0.1 global claim with 2.0.2 per-digest scope; validator checks | ✓ |
| Fixed sentence | Test checks digest names | |

**User's choice:** all recommended options.

---

## What the notice cites

| Option | Description | Selected |
|--------|-------------|----------|
| Pin + record commit | ae15c74 to pin; a71257e named as the record commit; no CI ids | ✓ |
| Pin + record + CI run | Also cites run 43332405316 | |
| Pin only | Shortest; may confuse | |

| Option | Description | Selected |
|--------|-------------|----------|
| Counts + 3 rules | 21/59, rules in machine form, unchanged decisions digest; points to reply for reasons | ✓ |
| Full per-control list | Self-contained; duplicates the reply | |
| Counts only | No rules restated | |

| Option | Description | Selected |
|--------|-------------|----------|
| Restate, updated | ae15c74 replaces 31addfa; repeat the other Hayes-side steps | ✓ |
| Only ask to re-pin | Leave other steps to the reply | |

**User's choice:** all recommended options.

---

## Voice, date and send condition

| Option | Description | Selected |
|--------|-------------|----------|
| Oscar Mack, with dual-role line | Matches the reply; unsigned until sent | ✓ |
| Neutral EMS notice | Impersonal wording | |

| Option | Description | Selected |
|--------|-------------|----------|
| Own notice date constant | NOTICE_DATE; publication date cited separately | ✓ |
| Publication date | 2026-11-12 | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, blocking review | Rendered Markdown approved before commit | ✓ |
| No, commit then review | Review the committed file before sending | |

| Option | Description | Selected |
|--------|-------------|----------|
| Blocking push checkpoint | Claude pushes after go-ahead (notice + 7 waiting commits) and dispatches CI | ✓ |
| You push yourself | Phase stops after the local commit | |

**User's choice:** all recommended options.

## Claude's Discretion

- Constant, helper and section names; exact JSON shape (closed schema).
- Adding the notice --validate to the CI archive-assessment job (preferred).
- How code commits are split.

## Deferred Ideas

- Citing CI run ids in the notice.
- Regenerating the DEMO3 reply for 2.0.2.
- PR / merge / tag.
- Review hardening WR-02 / WR-04 / IN-05 on existing reply and publisher tests.
