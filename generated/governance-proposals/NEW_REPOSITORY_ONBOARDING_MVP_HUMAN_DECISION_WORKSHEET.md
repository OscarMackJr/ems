# New Repository Onboarding MVP — Human Decision Worksheet

No selection is pre-checked. Highest risk: ONB-003-01, ONB-002-02, ONB-004-01, ONB-005-02, ONB-009-01.

## ONB-001-01

**Question:** Who allocates the first controlled repository ID?

**CANDIDATE-A:** EMS Governance allocates the next unused immutable REPO-<sequence> identifier after approved registration.
**CANDIDATE-B:** A deterministic host-owner-name identifier is assigned automatically.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** NONE
**Risk:** ID collision or unaccountable identity.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-001-02

**Question:** How are uniqueness and lifecycle continuity enforced?

**CANDIDATE-A:** repository_id is immutable; canonical host/owner/name is unique; rename, transfer, archive, delete, and replacement are immutable lifecycle events linked to original identity.
**CANDIDATE-B:** Canonical host/owner/name is immutable and every rename creates a new repository_id.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-001-01
**Risk:** Historical evidence becomes orphaned.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-001-04

**Question:** What minimum registration metadata is required?

**CANDIDATE-A:** Require repository_id, canonical host/owner/name, accountable owner, default branch, lifecycle status, registration approver/timestamp, and classification snapshot reference.
**CANDIDATE-B:** Require repository_id, canonical host/owner/name, and default branch only.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-001-01
**Risk:** Target cannot be attributed or bound to classification.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-001-03

**Question:** What approval is required before controlled targeting?

**CANDIDATE-A:** Automation may propose registration, but an accountable EMS repository authority must confirm identity and minimum metadata before controlled targeting.
**CANDIDATE-B:** Automation registers immediately and seeks later confirmation.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-001-01, ONB-001-04
**Risk:** Unconfirmed discovery becomes authority.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-002-01

**Question:** What classification model is authoritative?

**CANDIDATE-A:** Controlled snapshot records owner, tier, criticality, production, internet exposure, customer data, AI enabled, and data classification; human confirms criticality, production, customer data, AI, and data classification; discovery only proposes with provenance.
**CANDIDATE-B:** All attributes may be inferred from repository/GitHub metadata.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-001-04
**Risk:** Sensitive applicability relies on unverified metadata.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-005-01

**Question:** What is the local-path boundary?

**CANDIDATE-A:** Uncommitted execution-local mapping is keyed by controlled repository_id and never supplies identity, classification, or applicability authority.
**CANDIDATE-B:** Store local paths in controlled repository registry.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-001-02
**Risk:** Machine paths become authority.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-002-02

**Question:** How is UNKNOWN classified?

**CANDIDATE-A:** UNKNOWN is explicit with source/timestamp; it never becomes false or NOT_APPLICABLE; a dependent policy condition yields APPLICABILITY_UNRESOLVED and HUMAN_REVIEW.
**CANDIDATE-B:** UNKNOWN is treated as false pending later review.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-002-01
**Risk:** Controls silently skipped.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-002-04

**Question:** How do classification changes affect past assessment?

**CANDIDATE-A:** Bind immutable classification snapshot hash; applicability/evidence-authority changes require a new run and never rewrite prior snapshots.
**CANDIDATE-B:** Replace past classifications with current values.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-002-01
**Risk:** Outcomes become non-reproducible.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-005-02

**Question:** What checkout validation is required?

**CANDIDATE-A:** Require path, Git repository, canonical remote match, default branch/reference, commit SHA, and dirty status; missing/mismatch blocks execution.
**CANDIDATE-B:** Require an existing local path only.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-005-01, ONB-001-02
**Risk:** Wrong checkout is assessed.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-002-03

**Question:** Which UNKNOWN values block onboarding?

**CANDIDATE-A:** Owner, canonical coordinates, lifecycle, production, customer data, data classification, criticality, and policy-condition attributes are BLOCKING_UNKNOWN; tier/internet exposure/AI are conditionally blocking when policy-dependent.
**CANDIDATE-B:** Only canonical coordinates and owner are blocking.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-002-02
**Risk:** Material uncertainty is hidden.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-005-03

**Question:** Can dirty worktrees be assessed?

**CANDIDATE-A:** Clean checkout is required; dirty checkout requires time-bounded exception and non-baseline label.
**CANDIDATE-B:** Dirty checkout is allowed when SHA is captured.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-005-02
**Risk:** Uncommitted content is treated as baseline evidence.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-003-01

**Question:** How is applicability computed for repositories absent from historical freezes?

**CANDIDATE-A:** New-target authority computes APPLICABLE, NOT_APPLICABLE, or APPLICABILITY_UNRESOLVED from current policy hash, immutable classification snapshot, and condition evidence; it never edits historical freezes.
**CANDIDATE-B:** Append new target rows to the historical freeze.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-002-02, ONB-002-03
**Risk:** Historical evidence altered or unresolved applicability collapsed.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-003-02

**Question:** What provenance does each applicability decision retain?

**CANDIDATE-A:** Immutable snapshot stores repository_id, control_id, policy hash, classification hash, condition evidence references/hashes, result/rationale, exception, authority identity, and timestamp.
**CANDIDATE-B:** Store only control_id and result.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-003-01
**Risk:** Decision cannot be audited or replayed.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-006-01

**Question:** How do support states affect completeness?

**CANDIDATE-A:** SUPPORTED_AUTOMATED/HYBRID/HUMAN_EVIDENCE_REQUIRED execute contract; NOT_IMPLEMENTED blocks completeness but is neither FAIL nor NOT_APPLICABLE; APPLICABILITY_UNRESOLVED blocks completeness and cannot PASS.
**CANDIDATE-B:** Treat NOT_IMPLEMENTED and unresolved applicability as FAIL.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-003-01
**Risk:** Coverage confused with compliance.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-003-03

**Question:** When is applicability immutable?

**CANDIDATE-A:** Snapshot freezes with the assessment plan; policy, classification, evidence, or exception changes require a new run rather than mutation.
**CANDIDATE-B:** Recalculate prior applicability in place.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-003-01, ONB-003-02, ONB-002-04
**Risk:** Historical run scope drifts.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-004-01

**Question:** When does an assessment plan freeze?

**CANDIDATE-A:** Freeze before request generation after binding identity, classification hash, EMS/Hayes hashes, applicability, evidence contract, targets, support states, and review requirements.
**CANDIDATE-B:** Allow changes during execution when evidence arrives.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-003-03
**Risk:** Run lacks stable authority boundary.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-004-02

**Question:** How is evidence found after freeze handled?

**CANDIDATE-A:** Attach late evidence as immutable supplement only; material evidence that changes scope/request/result requires a new run.
**CANDIDATE-B:** Modify frozen plan and results in place.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-004-01
**Risk:** Post-hoc rewriting of results.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-006-02

**Question:** What aggregate outcomes are controlled?

**CANDIDATE-A:** COMPLETE needs resolved applicability and terminal outcome/NA for every applicable supported assertion with no blocking review; COMPLETE_WITH_FINDINGS permits FAIL/WARNING; PARTIAL covers unsupported/review/insufficient/unresolved; BLOCKED covers identity/plan/execution failure.
**CANDIDATE-B:** Overall PASS when no automated FAIL exists.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-006-01, ONB-004-01
**Risk:** Partial result misrepresented as compliant.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-007-01

**Question:** What evidence-resolution rule applies?

**CANDIDATE-A:** Record source class, authoritative system, collection time, integrity hash/immutable ID, freshness, and provenance; unavailable authority routes to contract HUMAN_REVIEW/INSUFFICIENT; repository evidence never overrides service/organization authority.
**CANDIDATE-B:** Repository evidence substitutes for unavailable service/organization evidence.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-004-01
**Risk:** Authority boundaries violated.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-008-01

**Question:** What is the human-review queue contract?

**CANDIDATE-A:** Immutable item records run/repository/control/assertion, reason, evidence gap, authority, reviewer authority, action, exception, status and provenance; statuses OPEN, IN_REVIEW, RESOLVED, EXCEPTION_APPROVED, SUPERSEDED.
**CANDIDATE-B:** Unstructured reviewer note without status/provenance.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-004-01, ONB-007-01
**Risk:** Manual decisions cannot be traced.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-008-02

**Question:** What closes a review item?

**CANDIDATE-A:** Closure requires attributable reviewer decision, evidence, rationale, timestamp, and exception/remediation reference; it supplements, never mutates, machine results.
**CANDIDATE-B:** Viewing the item closes it.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-008-01
**Risk:** Risk disappears without decision.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-009-01

**Question:** What immutable bundle is required?

**CANDIDATE-A:** Under generated/onboarding/runs/<RUN-ID>/ retain repository/classification/applicability snapshots, plan, requests/results, review queue, evidence manifest, summary, auditor report, certification; label inputs authoritative snapshots, outputs generated evidence, reports derived, paths local-only.
**CANDIDATE-B:** Retain summary and report only.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-004-01, ONB-007-01, ONB-008-01
**Risk:** Assessment cannot be audited or replayed.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-009-02

**Question:** What does certification prove?

**CANDIDATE-A:** Certification proves run integrity, identity binding, authority hashes, completeness state, and bundle manifest; it does not assert compliance beyond underlying results.
**CANDIDATE-B:** Certification asserts compliance if no automated FAIL exists.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-006-02, ONB-009-01
**Risk:** Certification overstates compliance.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

## ONB-010-01

**Question:** What retention and reassessment model applies?

**CANDIDATE-A:** Retain immutable bundles 3 years unless longer hold; new run for classification/lifecycle/branch/policy/registry/support/evidence/exception/material change; replay reproduces frozen run and review supplements without rewriting.
**CANDIDATE-B:** Retain one year and recompute old results in place.

**Recommended:** CANDIDATE-A
**Why:** Candidate A preserves immutable evidence, explicit authority, and fail-safe human review.
**Dependencies:** ONB-009-01, ONB-009-02
**Risk:** Evidence deleted early or history rewritten.

- [ ] Candidate A
- [ ] Candidate B
- [ ] Other — explicit approved concrete value required

