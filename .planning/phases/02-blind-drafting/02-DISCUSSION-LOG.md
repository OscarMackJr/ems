# Phase 2: Blind Drafting - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-13
**Phase:** 2-Blind Drafting
**Areas discussed:** Permitted drafting inputs, Drafting posture, Proposals file form, Proving blindness, Requirement wording, Drafter brief content, One drafter or two, Rationale standard

---

## Permitted drafting inputs

Scouting finding presented first: none of the 21 catalog entries has a `description`; other EMS files add little (collector names, tier lists, scope rationales that quote Wave 2A row counts).

| Question | Options | Selected |
|----------|---------|----------|
| What may a draft cite as an input? | Catalog entry only / Catalog + named EMS definition files / Write descriptions first | Catalog entry only |
| May a rationale lean on general knowledge of the named practice? | Yes, stated as an assumption / Yes, no separate labelling / No, literal fields only | Yes, stated as an assumption |
| How does each proposal list its inputs? | Catalog fields copied in + catalog hash / Path reference only / You decide | Catalog fields copied in + catalog hash |
| How are the Phase 1 shape and field definitions treated? | Declared once as 'drafting frame' / Not listed | Declared once as 'drafting frame' |

**Notes:** All recommended options taken.

---

## Drafting posture

| Question | Options | Selected |
|----------|---------|----------|
| Which way does the draft lean when name and scope do not settle it? | Lean to 'no rule' / Lean to a narrow rule / Best single judgment, no lean | Lean to 'no rule' |
| How is a shaky draft signalled? | Confidence + alternative considered / Confidence level only / Rationale text only | Confidence + alternative considered |
| How are the six non-REPOSITORY-scoped controls treated? | Draft within the shape, flag the limit / Scope never drives the draft / Allow 'defer' as a third outcome | Draft within the shape, flag the limit |
| How narrow is a proposed rule? | Fewest conditions that justify it / Belt and braces / You decide | Fewest conditions that justify it |

---

## Proposals file form

| Question | Options | Selected |
|----------|---------|----------|
| What form does the file take? | JSON + schema + pytest / JSON + a rendered Markdown view / Markdown only | JSON + schema + pytest |
| Where does it live? | registry/, named and marked as draft / A separate proposals directory / docs/ | registry/, named and marked as draft |
| How is the JSON produced? | Hand-authored JSON + validator script / Content embedded in a builder script / You decide | Hand-authored JSON + validator script |
| May it change after the drafting commit? | Frozen; hash recorded / Typo fixes allowed with a new commit | Frozen; hash recorded |

**Notes:** The preview shown for the JSON layout used EMS-CTRL-052 as a layout illustration only; it is not a proposal.

---

## Proving blindness

Fact presented: in tracked files, the target assessment is mentioned only under `.planning/`; PROJECT.md states an aggregate figure; no per-control result is in the repository.

| Question | Options | Selected |
|----------|---------|----------|
| Who writes the 21 proposals? | Isolated drafter with a fixed brief / Normal GSD executor / You draft, I only validate | Isolated drafter with a fixed brief |
| Does the user read proposals before the drafting commit? | No, commit first, review in Phase 3 / Mechanical check only / I review content first | No, commit first, review in Phase 3 |
| What happens on validator failure? | Same drafter fixes, mechanical feedback only / Fresh drafter re-drafts all 21 / Orchestrator fixes mechanical errors | Same drafter fixes, mechanical feedback only |
| Where is the drafting commit SHA recorded? | A drafting-record file, committed next in Phase 2 / Only in Phase 3 decision records / You decide | A drafting-record file, committed next in Phase 2 |
| What does the forbidden-term check cover? | Proposals file, brief and drafting record; fixed term list / Proposals file only / You decide | Proposals file, brief and drafting record; fixed term list |

---

## Requirement wording

| Question | Options | Selected |
|----------|---------|----------|
| How to square DRAFT-02 with the interpretation and drafting frame? | Amend DRAFT-02 and criterion 2 / Keep wording, record the reading in CONTEXT | Amend DRAFT-02 and criterion 2 |
| Publish the fact that the catalog has no description for the 21? | Yes, stated once in the header / Yes, and log a deferred item / No | Yes, stated once in the header |
| When is the amended wording applied? | Now, with this context commit / As the first task of the Phase 2 plan / Change the wording | Now, with this context commit |

**Notes:** The user approved the amended wording as previewed; it was applied to REQUIREMENTS.md and ROADMAP.md in the context commit.

---

## Drafter brief content

| Question | Options | Selected |
|----------|---------|----------|
| Which catalog entries does the drafter see? | Only the 21 / All 80 entries, draft only the 21 | Only the 21 |
| How much is the drafter told about purpose? | Task and semantics only / Also that an external assessor will consume it | Task and semantics only |
| Does the user approve the brief before use? | Yes, I approve the brief first / No, the brief follows CONTEXT.md | Yes, I approve the brief first |
| How is the drafter kept from reading anything else? | Material inlined, no file tools needed / Separate directory outside the repo / You decide | Material inlined, no file tools needed |

---

## One drafter or two

| Question | Options | Selected |
|----------|---------|----------|
| One drafting run or two? | One drafter / Two drafters, first is the proposal / Two drafters, disagreement becomes 'no rule' | One drafter |
| What if a run is unusable for a non-mechanical reason? | Re-run from scratch, record it / Stop and ask me | Re-run from scratch, record it |
| What does the drafting record say about who drafted? | AI drafter, model id, no authority / 'Drafted by tooling', no model named | AI drafter, model id, no authority |

---

## Rationale standard

| Question | Options | Selected |
|----------|---------|----------|
| How much does each rationale say? | Two to four sentences, fixed points / One sentence / Full argument per control | Two to four sentences, fixed points |
| May rationales share wording? | Each stands alone / Shared reason codes allowed | Each stands alone |

---

## Claude's Discretion

- File names for the proposals file, schema, validator script, test, brief and drafting record
- Location of the brief and drafting record (tracked)
- JSON key names and enum values
- Ordering of tooling commits around the brief and drafting commits, within the stated constraints
- Behaviour of the ancestor-commit test in shallow clones

## Deferred Ideas

- Other EMS files as drafting inputs
- Approved catalog descriptions for controls that lack them (considered, no backlog item requested)
- A second independent drafter
- A generated Markdown view of the proposals
