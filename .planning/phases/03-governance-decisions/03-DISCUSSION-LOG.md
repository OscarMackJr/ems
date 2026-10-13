# Phase 3: Governance Decisions - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-13
**Phase:** 3-Governance Decisions
**Areas discussed:** How you give the 21, Changed and rejected, Record contents and ids, Drafter's open points

---

## How you give the 21

### How do you want to give your disposition for each of the 21 proposals?

| Option | Description | Selected |
|--------|-------------|----------|
| Worksheet file (Recommended) | Generated worksheet lists all 21; you fill in a disposition and any decided text per control outside the chat; validator refuses it until all 21 are individually filled; the filled worksheet is committed as evidence | ✓ |
| One at a time in session | Each control shown in chat and answered before the next; answers transcribed into records and confirmed | |
| Grouped in session | Controls shown in small groups, answered per control within the group; closer to a batch approval | |

**User's choice:** Worksheet file

### What form should the worksheet take?

| Option | Description | Selected |
|--------|-------------|----------|
| Markdown view + JSON answers (Recommended) | Read-only Markdown page shows each proposal in full; answers typed into a separate small JSON file; the JSON is validated and committed | ✓ |
| Single JSON worksheet | Drafted content and blank answer fields side by side in one JSON file | |
| CSV worksheet | One row per control, editable in Excel | |

**User's choice:** Markdown view + JSON answers

### When you approve a proposal as drafted, what must your answer contain?

| Option | Description | Selected |
|--------|-------------|----------|
| Disposition plus own note (Recommended) | Every control needs a disposition and a short note in your own words; validator rejects empty notes and identical notes repeated across controls | ✓ |
| Disposition only | Notes required only for changed or rejected | |
| Disposition plus confirmations | Disposition and explicit yes/no confirmations, no free text on approval | |

**User's choice:** Disposition plus own note

### What part may an AI agent play while you fill in the answers?

| Option | Description | Selected |
|--------|-------------|----------|
| None in the answers (Recommended) | Answers start blank; no agent pre-fills, suggests or writes a note; agents only generate the view, run the validator and report errors; the record states the answers were typed by you | ✓ |
| Explain on request | No agent writes in the file, but may explain a proposal or the semantics on request | |
| Agent may suggest | An agent may offer a recommended disposition per control | |

**User's choice:** None in the answers

---

## Changed and rejected

### If you reject a proposal, what may that control end as?

| Option | Description | Selected |
|--------|-------------|----------|
| Must still be decided (Recommended) | Every one of the 21 ends as rule or no-rule; rejecting a rule means no rule; rejecting a no-rule means supplying a rule | ✓ |
| May stay not yet decided | A rejection can leave the control NOT_YET_DECIDED; PUB-04 and the roadmap would need amending | |
| Rejected means no rule | Rejection always resolves to NO_RULE_WILL_BE_PUBLISHED | |

**User's choice:** Must still be decided

### Where is the line between 'changed' and 'rejected'?

| Option | Description | Selected |
|--------|-------------|----------|
| By outcome (Recommended) | Approved: all stand. Changed: same outcome kind, altered conditions or rationale. Rejected: outcome flips. Validator checks disposition against decided outcome | ✓ |
| By your judgment | No mechanical test | |
| Rationale edits are not changes | Rewording only the rationale counts as approved; 'changed' reserved for different conditions | |

**User's choice:** By outcome

### For a changed or rejected proposal, who writes the decided rule and decided rationale?

| Option | Description | Selected |
|--------|-------------|----------|
| You write both (Recommended) | You type the decided rule and rationale; validator checks the rule shape; no agent rewords; for approvals the tooling copies the drafted text verbatim | ✓ |
| You give the rule, agent words it | An agent drafts the decided rationale and you approve the wording | |
| Rule only, note is the rationale | The note itself becomes the decided rationale | |

**User's choice:** You write both

### After your answers are committed, how is a later change of mind handled?

| Option | Description | Selected |
|--------|-------------|----------|
| New superseding decision (Recommended) | Committed answers and records are frozen; a change of mind is a new record with a new AA4-GOV id naming the one it supersedes; Phase 4 publishes the latest unsuperseded decision | ✓ |
| Edit until publication | Edit in place up to the publication commit; git history is the only trace | |
| Final, no revision here | No revision in this milestone | |

**User's choice:** New superseding decision

---

## Record contents and ids

### How should the decision records be stored and numbered?

| Option | Description | Selected |
|--------|-------------|----------|
| One file, ids in control order (Recommended) | One registry JSON file; AA4-GOV-001 = EMS-CTRL-009 ... AA4-GOV-021 = EMS-CTRL-079; superseding decisions from 022 | ✓ |
| One file, ids in decision order | Ids issued in the order the answers were filled in | |
| One file per decision | 21 small JSON files plus an index | |

**User's choice:** One file, ids in control order

### How should the dual-role statement appear in each record?

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed sentence plus fields (Recommended) | Same approved sentence and two structured role fields in every record; schema requires both | ✓ |
| Fixed sentence only | One approved sentence, no role fields | |
| Structured fields only | Role fields and a boolean, no prose | |

**User's choice:** Fixed sentence plus fields
**Notes:** Selected preview: `approver` "Oscar Mack"; `approver_roles` `EMS_GOVERNANCE_AUTHORITY`, `HAYES_VERIFY_DEVELOPER`; `dual_role_statement` "Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it." The option stated that the exact sentence is approved before it is used.

### The drafts were written blind, but you know the result of the earlier assessment. Should the records say so?

| Option | Description | Selected |
|--------|-------------|----------|
| Disclose once, plainly (Recommended) | Header statement: the authority knew the per-control result of an earlier assessment when deciding; drafts were written without it; no rule compared with a target in this phase; each record points to it | ✓ |
| Disclose in every record | Same sentence repeated in each record | |
| Do not record it | Records cover the dual role only | |

**User's choice:** Disclose once, plainly

### May your notes, decided rationales or the records name the assessed repository or use its result as a reason?

| Option | Description | Selected |
|--------|-------------|----------|
| No, and test for it (Recommended) | Decisions reasoned from the control and field definitions only; a test scans answers and records for the repository name, commit SHA, assessment date and refusal code; 'Hayes Verify' allowed | ✓ |
| No, by instruction only | Same rule, no automated scan | |
| Allowed if labelled | May mention the assessment as labelled context | |

**User's choice:** No, and test for it

---

## Drafter's open points

### How should your decision treat a scope limitation note (022, 030, 042, 052, 062, 075)?

| Option | Description | Selected |
|--------|-------------|----------|
| Rule on each note (Recommended) | For each of the six, the answer also says whether you accept the note as a true limitation of this version; the record carries the note and your ruling | ✓ |
| Carry the note unchanged | Note copied into the record as drafter content, no separate view | |
| Leave notes in the proposals | Records hold outcome and rationale only | |

**User's choice:** Rule on each note

### May a decision settle what a field definition means (052 / ai_enabled)?

| Option | Description | Selected |
|--------|-------------|----------|
| Decide within the definition as written (Recommended) | Definitions not reworded or extended; if a definition does not safely cover the case, reject the rule; note says how you read it, for this decision only | ✓ |
| Record a binding reading | A decision may state a reading published with the rule | |
| Amend the definition first | Reword and re-approve the definition in the v2 publisher before deciding | |

**User's choice:** Decide within the definition as written

### How should the Markdown view present the 21 proposals?

| Option | Description | Selected |
|--------|-------------|----------|
| Complete and neutral (Recommended) | All 21 in control order, every drafted field verbatim, no ranking, highlighting or summary added by tooling | ✓ |
| Neutral, with an index table | As above, preceded by a plain table copied from the drafts | |
| Attention items first | Rules, scope-noted and MEDIUM-confidence drafts listed first | |

**User's choice:** Complete and neutral

### When you approve a draft, what happens to the drafter's reading of the control name?

| Option | Description | Selected |
|--------|-------------|----------|
| Accepted for this decision only (Recommended) | Record carries the interpretation and states it was accepted as the basis of this decision; it does not define the control; catalog unchanged | ✓ |
| Becomes the control's meaning | Approved interpretation recorded as EMS's reading of the control from now on | |
| Not carried into the record | Interpretation stays in the frozen proposals file | |

**User's choice:** Accepted for this decision only

---

## Claude's Discretion

- File names and locations for the view, answers file, records file, schema, script and tests
- JSON key names and enum values
- How records are built from proposals plus answers, and which digests and dates they carry
- Commit order, provided tests are never red in between and only this project's files are staged
- How identical notes are detected
- Whether the request id may appear in the decision file
- How the two approved wordings are put to the authority for sign-off
- How the human gate is expressed in the plan

## Deferred Ideas

- Rule conditions that express control scope or target type (future authority version)
- Binding readings of a field, or rewording a field definition (future authority version)
- Approved interpretations becoming control definitions, or catalog descriptions
- Allowing a rejected control to stay `NOT_YET_DECIDED`
