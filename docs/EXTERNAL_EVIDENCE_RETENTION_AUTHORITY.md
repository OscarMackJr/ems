# External Evidence Retention Authority

This authority applies only to external-review synthetic evidence. It does not certify compliance, production readiness, or permission to execute the Hometown pilot.

Software Development produces and business-owns the evidence. CSO is the storage authority for the approved logical retention authority, **Egnyte / TWG/TechAudits**. The former `retention_owner: Software Development` field did not distinguish those roles and is clarified by this authority; it never granted engineering self-authorization over the CSO-controlled storage location.

Retention is three years. A longer legal or management hold overrides deletion. Retention-policy, hold, deletion, and storage-administrator assignments remain open until recorded by the appropriate controlled authority.

`Z:\Shared\TWG\TechAudits` is a non-authoritative operational mapping only. It is currently inaccessible. No evidence may be written until CSO confirms authorized write access, an approved operational access mechanism, destination readiness, and sufficient hold/deletion semantics.

## State transition and supersession retention

The package is initially `STAGED_LOCAL`; it may transition only to `CSO_APPROVED_STORAGE` after CSO authorization, approved access, destination readiness, recorded hold/deletion authority, immutable or versioned storage layout, and per-artifact SHA-256 equality. The transition records the logical path, source/retained hash equality, timestamp, and authorization reference.

Onboarding certifications, supersession records, immutable machine results, and append-only human-review supplements are retained for the same three-year-or-longer-hold period. A successor supplements rather than rewrites or deletes a prior record.
