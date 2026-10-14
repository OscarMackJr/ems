# Phase 5: Reply to Hayes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-14
**Phase:** 05-reply-to-hayes
**Areas discussed:** Reply form and source, The commit Hayes pins to, Disclosing review findings, What each control entry says

---

## Reply form and source

| Question | Options | Selected |
|----------|---------|----------|
| Format | Markdown + JSON (recommended) / Markdown only | Markdown + JSON |
| Source of the 21-control list | Generated + test (recommended) / Hand-written + test / Hand-written only | Generated + test |
| Location | docs/ + registry/ (recommended) / releases/ / You decide | docs/ + registry/ |
| Voice | From the EMS authority (recommended) / Neutral record | From the EMS authority |

**User's choice:** all recommended options.

---

## The commit Hayes pins to

| Question | Options | Selected |
|----------|---------|----------|
| Pin SHA | 54a7fd0 with the others as context (recommended) / 54a7fd0 only / The reply commit | 54a7fd0 with the others as context |
| Push status | Push before sending (recommended) / Ignore push status | Push before sending |
| Digests | Yes, the LF digests (recommended) / SHA only | Yes, the LF digests |
| Shape | Paths, fields and an example row (recommended) / Point to the schema | Paths, fields and an example row |

**User's choice:** all recommended options.

---

## Disclosing review findings

| Question | Options | Selected |
|----------|---------|----------|
| Disclose the gaps in the publication checks | Brief, factual note (recommended) / Full list / Leave them out | Brief, factual note |
| WR-01 (certification PASS for checks the publisher doesn't run) | Yes, name it (recommended) / Cover it in the general note | Yes, name it |
| v2.0.1 | Possible, no date (recommended) / Commit to it / Don't mention it | Possible, no date |

**User's choice:** all recommended options.

---

## What each control entry says

| Question | Options | Selected |
|----------|---------|----------|
| Detail per control | State, id, rule and one line (recommended) / State, id, rule only / Full rationale | State, id, rule and one line |
| Dual-role statement | In the opening, exact text (recommended) / Footnote | In the opening, exact text |
| Date for the 59 | No date, say so (recommended) / Give a target date | No date, say so |
| Rule effect | Plain words and a caution (recommended) / Rule text only | Plain words and a caution |

**User's choice:** all recommended options.
**Notes:** Claude's reading: `decided.rationale` runs to several sentences, so "one line" means its first sentence, copied word for word.

## Claude's Discretion

- File and field names, the order of sections in the letter, how the commits are split, how "first sentence" is cut, and the wording of the fixed prose.

## Deferred Ideas

- The v2.0.1 release that hardens the publication checks; V2-01 (the other 59 controls); V2-02 (a Hayes re-run); adding V2-01 and V2-02 to the REQUIREMENTS.md traceability table.
