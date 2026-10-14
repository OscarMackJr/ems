---
phase: 04-certified-publication
plan: 06
subsystem: archive-assessment-publication
tags: [publication, signoff, authority-v2]
requires: [04-05]
provides:
  - published EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0 (21 decided, 59 undecided)
  - Oscar Mack sign-off record bound to authority LF digest
key-files:
  created:
    - registry/archive_assessment_applicability_authority_v2.json
    - registry/archive_assessment_applicability_authority_v2_signoff.json
    - generated/archive-assessment/ems-aa3-v2/ (seven outputs)
metrics:
  completed: 2026-10-14
---

# Phase 4 Plan 06: Certified Publication Summary

Published EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0 after Oscar Mack's recorded sign-off (EMS_GOVERNANCE_AUTHORITY, 2026-10-14): 21 decided (3 RULE_PUBLISHED: CTRL-030 and CTRL-039 production=KNOWN_FALSE, CTRL-052 ai_enabled=KNOWN_FALSE; 18 NO_RULE_WILL_BE_PUBLISHED) and 59 NOT_YET_DECIDED.

Publication SHA: 54a7fd09114704a97a7a48fce5f89aebeb48c90a

- Authority LF sha256: de36e227be4ccc95f4a8a8a08247cf6e49f7682908c7f425f8cc02bbaa1da353 (matched the approved digest on re-run)
- Manifest sha256: 64c6c0e0dc216ed157962e2bab804e1b6f252fe25838efd76ed98e935b0e1680
- --validate-signoff, --validate: PASS (before and after commit); second --publish byte-identical
- pytest -k archive_assessment: 364 passed, 1 skipped
- Commit contains exactly the nine planned paths; unrelated modified files (adjudication_rules.json, policy_decisions.json) remain unstaged. Nothing pushed, tagged or merged.

## Deviations from Plan

None - plan executed as written. Tasks 1 and 2 produced no commits by design.

## Self-Check: PASSED
