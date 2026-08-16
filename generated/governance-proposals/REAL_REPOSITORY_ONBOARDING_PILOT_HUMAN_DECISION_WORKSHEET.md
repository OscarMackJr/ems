# Real Repository Onboarding Pilot — Human Decision Worksheet

All choices remain PENDING_APPROVAL. No real repository, credential, or EMS change is authorized by this worksheet.

## ROP-01 — Pilot repository selection

Which one repository is authorized for the first real pilot?

CANDIDATE-A: Exactly one repository explicitly named by the human governance owner and documented in the approval response.

CANDIDATE-B: Do not authorize a real-repository pilot.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: NONE
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-02 — Pilot authorization authority

Who may authorize this one non-production real-repository pilot?

CANDIDATE-A: Designated EMS governance authority with named approval record.

CANDIDATE-B: No authorization; pilot remains blocked.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-01
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-03 — Controlled repository ID allocation

Who allocates the immutable REPO-sequence ID and when?

CANDIDATE-A: EMS Governance allocates the next unique REPO-sequence only after ROP-01 and ROP-02 approval.

CANDIDATE-B: No allocation; pilot remains blocked.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-01, ROP-02
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-04 — Repository registration metadata

What must be recorded before ID allocation?

CANDIDATE-A: Canonical host, owner, repository name, URL, lifecycle state, default branch, pilot flag, and accountable owner.

CANDIDATE-B: No registration; pilot remains blocked.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-03
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-05 — Classification confirmation authority

Who confirms material repository classification?

CANDIDATE-A: Named accountable business/service owner and EMS classification authority jointly confirm values.

CANDIDATE-B: Values remain UNKNOWN and conditional controls route to HUMAN_REVIEW.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-04
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-06 — Classification attribute values

How are material attributes recorded?

CANDIDATE-A: Record human-confirmed production, internet exposure, customer data, AI use, owner, tier, criticality, and data classification; unconfirmed values remain UNKNOWN.

CANDIDATE-B: Record all material values UNKNOWN and do not authorize conditional execution.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-05
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-07 — Local execution mapping approval

How is real checkout access approved?

CANDIDATE-A: Named operator receives a read-only local execution mapping recorded separately from controlled identity.

CANDIDATE-B: No local mapping; pilot execution blocked.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-03
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-08 — Checkout/reference approval

What checkout state is permitted?

CANDIDATE-A: Verified canonical remote, approved default branch or explicit ref, captured commit SHA, and clean worktree.

CANDIDATE-B: No checkout approval; pilot blocked.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-07
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-09 — Repository evidence access

Which repository evidence access is allowed?

CANDIDATE-A: Read-only approved repository checkout and API evidence with provenance captured.

CANDIDATE-B: No repository evidence access; repository evidence routes to HUMAN_REVIEW.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-07
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-10 — CI/CD evidence access

Which CI/CD evidence access is allowed?

CANDIDATE-A: Read-only approved CI/CD execution records bound to repository and revision.

CANDIDATE-B: No CI/CD evidence access; affected controls route to HUMAN_REVIEW.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-02
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-11 — Service evidence access

Which service evidence access is allowed?

CANDIDATE-A: Read-only approved service-evidence source; repository evidence remains supporting only.

CANDIDATE-B: No service evidence access; service controls route to HUMAN_REVIEW.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-02
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-12 — Organization evidence access

Which organization evidence access is allowed?

CANDIDATE-A: Read-only approved organization-evidence source; repository evidence remains supporting only.

CANDIDATE-B: No organization evidence access; organization controls route to HUMAN_REVIEW.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-02
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-13 — Credential/security boundary

What credential posture applies?

CANDIDATE-A: Named least-privilege read-only credentials, no evidence-bundle persistence, revocation after pilot, and incident stop path.

CANDIDATE-B: No credentials; sources requiring them remain unavailable.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-09, ROP-10, ROP-11, ROP-12
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-14 — Human-review owner

Who owns WS7 review?

CANDIDATE-A: Named primary reviewer plus named backup/escalation role; decisions are attributable and append-only.

CANDIDATE-B: No reviewer; unresolved review items remain OPEN and pilot cannot close.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-02
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-15 — Exception escalation authority

Who approves pilot exceptions?

CANDIDATE-A: Named EMS governance authority approves time-bounded exceptions with rationale and remediation.

CANDIDATE-B: No exception authority; exceptions stop the pilot.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-02
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-16 — Evidence-retention location

Where is pilot evidence retained?

CANDIDATE-A: Named approved controlled evidence repository with integrity protection and access owner.

CANDIDATE-B: No approved location; pilot cannot close.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-02
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-17 — Retention and holds

What retention rule applies?

CANDIDATE-A: Retain pilot evidence for three years; legal, regulatory, contractual, audit, and investigation holds override deletion.

CANDIDATE-B: No retention approval; pilot cannot close.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-16
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-18 — Pilot success criteria

What proves pilot execution success?

CANDIDATE-A: All stated chain/integrity criteria execute; supported controls execute, unsupported/unresolved controls remain visible, without requiring all controls PASS.

CANDIDATE-B: Do not set success criteria; pilot not authorized.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-03, ROP-06, ROP-08, ROP-14, ROP-16
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-19 — Pilot stop criteria

When must the pilot stop fail-closed?

CANDIDATE-A: Stop on identity/classification/hash/registry/checkout/credential/evidence/contract/semantic/immutability/local-path/production-mutation failures.

CANDIDATE-B: No stop criteria; pilot not authorized.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-18
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-20 — Reassessment/change handling

How are material changes handled?

CANDIDATE-A: Use WS10 reassessment decision; local execution configuration alone is non-material and no compliance result is inferred.

CANDIDATE-B: No change handling; pilot cannot close.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-18
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-21 — Pilot report recipients

Who receives the closeout report?

CANDIDATE-A: Named EMS governance authority, repository owner, human-review owner, and evidence-retention owner.

CANDIDATE-B: No recipients; pilot cannot close.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-14, ROP-16
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-22 — Pilot evidence classification

How is pilot evidence classified?

CANDIDATE-A: Synthetic/real-pilot evidence is controlled pilot evidence, non-production authorization evidence, and never production evidence.

CANDIDATE-B: No classification; pilot not authorized.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-02
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-23 — Explicit non-production boundary

What authorization boundary applies?

CANDIDATE-A: Real repository but non-production authorization only; no production readiness, production authorization, organization-wide deployment, or blanket compliance certification.

CANDIDATE-B: No boundary approval; pilot not authorized.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-02
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value

## ROP-24 — Pilot operating procedure

Which procedure authorizes execution?

CANDIDATE-A: Approve the controlled pilot procedure after all prerequisite approvals and no unresolved dependencies.

CANDIDATE-B: No procedure approval; pilot remains blocked.

Recommended: CANDIDATE-A
Why: Preserves a controlled, least-privilege, fail-closed non-production pilot boundary.
Risk: Unauthorized real access, evidence-boundary breach, or ungoverned pilot execution if unresolved.
Dependencies: ROP-18, ROP-19, ROP-20, ROP-21, ROP-22, ROP-23
Selection: [ ] CANDIDATE-A  [ ] CANDIDATE-B  [ ] Other explicit approved value
