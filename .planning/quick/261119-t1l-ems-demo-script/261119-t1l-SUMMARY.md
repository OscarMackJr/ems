---
quick_id: 261119-t1l
status: complete
date: 2026-11-19
---

# Quick Task 261119-t1l: EMS demo script — Summary

## Deliverables

- `DEMO-SCRIPT.md`: a one-page demo walkthrough covering setup, the question, verify steps 1-3, the decisions,
  governance, a failure table and the known Hayes-pin gap.
- `show_decisions.py`: a read-only helper. It prints the authority id and the counts per decision state, the 3
  rules with their conditions and authorities, and the 18 no-rule decisions.

## Rehearsal (2026-11-19, orchestrator, fresh clone)

Setup:

- Clone: `git clone -c core.longpaths=true https://github.com/OscarMackJr/ems.git`, into the session scratchpad
  (a deep Windows root). Exit 0, `is-shallow-repository` false.
- Environment: `py -3.12 -m venv .venv` gave Python 3.12.10. `pip install -r requirements.txt jsonschema==4.26.0`
  exited 0.

Verify steps:

| Step | Ref and commit | Exit | Time | Output |
|---|---|---|---|---|
| 1 | `ems-aa3-authority-2.0.3` (1544dc19ba235d732c832d1651895550ed5a265d) | 0 | ~27 s from clone start, including install | `{"status": "PASS", "mode": "AT_PIN", "deferred": ["PUBLICATION_RECORD_BINDING: the publication record naming this commit is written in the next commit; run plain --validate at the record commit or any later commit to check it"]}` |
| 2 | `ems-demo-2026-12` (755cb275564f44b0af15dcad86267d809fe23f79), plain `--validate` | 0 | 6 s | `PASS` |
| 3 | `ems-demo-2026-12`, notice builder `--validate` | 0 | 6 s | `PASS` |

Decisions, from `show_decisions.py`:

- 80 controls: `NOT_YET_DECIDED`=59, `NO_RULE_WILL_BE_PUBLISHED`=18, `RULE_PUBLISHED`=3.
- The 3 rules:

  | Control | Condition | Authority |
  |---|---|---|
  | EMS-CTRL-030 | `production=KNOWN_FALSE` | AA4-GOV-014 |
  | EMS-CTRL-039 | `production=KNOWN_FALSE` | AA4-GOV-016 |
  | EMS-CTRL-052 | `ai_enabled=KNOWN_FALSE` | AA4-GOV-018 |

- The 18 no-rule decisions are AA4-GOV-001..013, 015, 017 and 019..021.

The clone's working tree stayed clean: `.venv` is ignored.

## Notes

- The tagged commit does not contain the helper. The demo runs it from the main checkout's path. Before the demo,
  copy it next to the clone if a different machine is used.
- The label text was refined after the rehearsal run: no-rule now reads "can never resolve to not-applicable". The
  logic is unchanged.
- Day 8-10 of the plan: rehearse once more on the demo machine itself.
