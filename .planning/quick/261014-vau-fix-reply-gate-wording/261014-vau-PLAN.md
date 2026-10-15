---
quick_id: 261014-vau
slug: fix-reply-gate-wording
mode: quick
source: .planning/v1.0.0-MILESTONE-AUDIT.md (AUDIT-W1, AUDIT-W2)
---

# Quick Task 261014-vau: Fix reply gate wording

Make two sentences in the reply's history note state exactly what the code enforces, before the DEMO3-W1-REQ-001 reply is sent. The published authority 2.0.1 (31addfa) is not touched or republished.

## Task 1: Reword ENFORCED_GATES and regenerate the reply

- **files:** `scripts/build_archive_assessment_demo3_w1_req_001_reply.py`, `registry/archive_assessment_demo3_w1_req_001_reply.json`, `docs/DEMO3_W1_REQ_001_REPLY.md`
- **action:**
  - Gate 1 (AUDIT-W2): say the sign-off role must be `EMS_GOVERNANCE_AUTHORITY` and the Hayes Verify developer role is rejected (publisher `SIGNOFF_ROLE`, line 437; mutation `signoff_role_hayes_developer`).
  - Gate 4 (AUDIT-W1): limit the schema claim to what the v2 schema closes (rule, condition, source lineage objects; a field repeated in one rule), and say that an extra field on a decided row is rejected by the Python validator (mutation `extra_field_on_decided_row`, rejected_by PYTHON_VALIDATOR).
  - Keep four gates, no forbidden words; run `--build`.
- **verify:** reply `--validate` PASS; `pytest tests -k archive_assessment` all pass; publisher `--validate` PASS; `git diff` touches only the three files above.
- **done:** Oscar Mack approves the regenerated wording (read-through, as in 06-09) before the commit.

## Out of scope

- Reply schema `from_authority.role` enum (lists both roles as data; the builder enforces the value).
- Any publisher, schema, authority, decisions or generated-output change.
