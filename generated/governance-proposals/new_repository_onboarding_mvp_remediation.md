# New Repository Onboarding MVP — Governance Remediation

Generated: 2026-08-15T16:29:25Z

**State:** READY FOR HUMAN DECISION SELECTION

This is a proposal-only package. Controlled EMS remains authoritative until a separately approved publication. Historical Wave 2D freezes are not changed.

## Controlled sources reviewed

- `registry/repository_registry.yaml`
- `registry/repository_overrides.yaml`
- `docs/REPOSITORY_CLASSIFICATION_GUIDE.md`
- `registry/policy_applicability.yaml`
- `registry/adjudication_rules.json`
- `registry/evidence_authority_registry.yaml`
- `registry/evidence_source_policy.json`
- `registry/wave2d/applicability_decisions.csv`
- `registry/wave2d/test_quality_effective_applicability.yaml`
- `registry/control_catalog.yaml`
- `registry/control_scope_registry.yaml`
- `registry/wave1_evidence_strategies.yaml`
- `registry/collector_acceptance.json`

## Decision summary

- `ONB-001-01` — Who allocates the first controlled repository ID?
- `ONB-001-02` — How are uniqueness and lifecycle continuity enforced?
- `ONB-001-03` — What approval is required before controlled targeting?
- `ONB-001-04` — What minimum registration metadata is required?
- `ONB-002-01` — What classification model is authoritative?
- `ONB-002-02` — How is UNKNOWN classified?
- `ONB-002-03` — Which UNKNOWN values block onboarding?
- `ONB-002-04` — How do classification changes affect past assessment?
- `ONB-003-01` — How is applicability computed for repositories absent from historical freezes?
- `ONB-003-02` — What provenance does each applicability decision retain?
- `ONB-003-03` — When is applicability immutable?
- `ONB-004-01` — When does an assessment plan freeze?
- `ONB-004-02` — How is evidence found after freeze handled?
- `ONB-005-01` — What is the local-path boundary?
- `ONB-005-02` — What checkout validation is required?
- `ONB-005-03` — Can dirty worktrees be assessed?
- `ONB-006-01` — How do support states affect completeness?
- `ONB-006-02` — What aggregate outcomes are controlled?
- `ONB-007-01` — What evidence-resolution rule applies?
- `ONB-008-01` — What is the human-review queue contract?
- `ONB-008-02` — What closes a review item?
- `ONB-009-01` — What immutable bundle is required?
- `ONB-009-02` — What does certification prove?
- `ONB-010-01` — What retention and reassessment model applies?
