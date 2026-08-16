# Hometown Pilot Execution-Prerequisite Human Input

All listed records are required before a separate execution-authorization gate. This document does not authorize execution.

## Current classification confirmation

- production: existing controlled value = `True`; select a current human-confirmed value, approver, and timestamp.
- internet_exposed: existing controlled value = `True`; select a current human-confirmed value, approver, and timestamp.
- contains_customer_data: existing controlled value = `True`; select a current human-confirmed value, approver, and timestamp.
- ai_enabled: existing controlled value = `False`; select a current human-confirmed value, approver, and timestamp.
- owner: existing controlled value = `Software Development`; select a current human-confirmed value, approver, and timestamp.
- tier: existing controlled value = `Tier2`; select a current human-confirmed value, approver, and timestamp.
- service_criticality: existing controlled value = `High`; select a current human-confirmed value, approver, and timestamp.
- data_classification: existing controlled value = `['Confidential']`; select a current human-confirmed value, approver, and timestamp.

## Operational assignments and activations
- Name primary and backup review owner; role, authority, effective timestamp.
- Approve required evidence-source access or controlled HUMAN_REVIEW fallback.
- Approve least-privilege credential model or confirm no credential required by source.
- Select approved three-year retention location/process, integrity, holds, access, deletion authority.
- Approve named operator and LOCAL_EXECUTION_ONLY mapping with branch/ref/commit/dirty policy.
