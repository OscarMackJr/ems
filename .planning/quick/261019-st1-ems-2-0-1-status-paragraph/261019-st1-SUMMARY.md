---
quick_id: 261019-st1
slug: ems-2-0-1-status-paragraph
status: complete
completed: 2026-10-19
key-files:
  created:
    - .planning/quick/261019-st1-ems-2-0-1-status-paragraph/261019-st1-PLAN.md
    - .planning/quick/261019-st1-ems-2-0-1-status-paragraph/261019-st1-SUMMARY.md
---

# Quick Task 261019-st1: EMS 2.0.1 status paragraph — Summary

Wrote a one-paragraph status for a developer and a documentation consultant. Delivered in the session on 2026-10-15; recorded here unchanged.

## Status paragraph

**EMS status: authority 2.0.1 is live.** The headline is that EMS can now answer the question "does this control even apply?" In version 1.0.0 the archive-assessment applicability authority was polite but no help. All 80 controls said `APPLICABILITY_UNRESOLVED`, and the schema set `not_applicable_rule` to `null`. So when Hayes Verify ran against a real repository, all 21 controls it asked about came back with `EMS_NOT_APPLICABLE_RULE_ABSENT`. Hayes had predicted exactly that, which is both impressive and a little embarrassing for us. Version 2.0.x fixes it. We defined a strict rule shape: four classification fields, only `KNOWN_TRUE` and `KNOWN_FALSE`, and `UNKNOWN` never counts as not-applicable. We drafted proposals for all 21 controls blind, using only the control catalog, and committed them before anyone looked at a target. Oscar then made 21 individual governance decisions on the record, each one noting that he is both the EMS approver and the Hayes developer. The result is 3 published rules and 18 explicit "no rule" decisions. The other 59 controls are now marked `NOT_YET_DECIDED` instead of just staying quiet. 2.0.1 contains exactly the same decisions as 2.0.0. The difference is that the publication gates are tougher: hashing now normalises line endings, the sign-off role must match exactly, and 26 deliberately broken inputs were each confirmed to be rejected. It's certified at commit `31addfa`, CI is green (492 tests passing), and the reply to Hayes has been sent. Next up: Hayes re-pins to the new commit and re-runs, ideally watching some controls actually resolve. On our side, we'll fix a lineage-hash mismatch (the authority says the source hashes ignore line-ending differences, but three of them don't). We'll also clear a few review items and probably start deciding some of the other 59 controls.

## Notes

- Facts as of 2026-10-15. Since then Hayes has deferred the re-pin to `31addfa` to a later Hayes phase, so "next up" is further out than the paragraph suggests.
- Executed inline (no planner or executor agents); no registry, schema, script or test changed.
