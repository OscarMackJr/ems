"""Apply the approved P3 terminology clarification to isolated EMS artifacts."""

from __future__ import annotations

import json
from pathlib import Path


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    authority = {
        "authority_id": "EXTERNAL-EVIDENCE-RETENTION-AUTHORITY-V1",
        "authority_scope": "EXTERNAL_REVIEW_SYNTHETIC_EVIDENCE_RETENTION_ONLY",
        "governance_reconciliation": "TERMINOLOGY_CLARIFICATION",
        "clarification": "The former retention_owner value Software Development identifies the evidence-producing and business-owning function. It does not identify the storage authority for Egnyte / TWG/TechAudits.",
        "roles": {"evidence_producer": "Software Development", "evidence_business_owner": "Software Development", "retention_policy_authority": "OPEN", "storage_platform": "Egnyte", "storage_logical_authority": "TWG/TechAudits", "storage_authority": "CSO", "storage_administrator": "OPEN", "retention_hold_authority": "OPEN", "deletion_authority": "OPEN"},
        "retention": {"period": "3 years", "longer_hold_overrides_deletion": True, "write_authorization_required": True, "current_operational_access_state": "BLOCKED / INACCESSIBLE", "non_authoritative_operational_mapping": "Z:\\\\Shared\\\\TWG\\\\TechAudits"},
        "negative_invariants": {"EVIDENCE_PRODUCER_NE_STORAGE_AUTHORITY": "PASS", "SOFTWARE_DEVELOPMENT_NE_CSO": "PASS", "LOCAL_DRIVE_MAPPING_NE_RETENTION_AUTHORITY": "PASS", "GITHUB_NE_FINAL_EVIDENCE_RETENTION_STORE": "PASS", "RETENTION_WRITE_REQUIRES_AUTHORIZATION": True, "CSO_CONTROLLED_LOCATION_NE_ENGINEERING_SELF_AUTHORIZATION": "PASS"},
        "write_gate": {"approved_logical_location": "Egnyte / TWG/TechAudits", "operator_write_access": "UNVERIFIED", "destination_exists_or_creation_approved": "UNVERIFIED", "hold_deletion_semantics": "OPEN", "retention_write_authorized": False},
    }
    write_json(root / "registry/external_evidence_retention_authority.json", authority)
    prerequisites_path = root / "registry/real_repository_onboarding_pilot_execution_prerequisites.json"
    prerequisites = json.loads(prerequisites_path.read_text(encoding="utf-8"))
    record = next(item for item in prerequisites["prerequisites"] if item["id"] == "RETENTION_LOCATION")
    record["closure_criteria"] = "logical location, separated evidence/business owner, and storage authority recorded; authorized operational access and hold/deletion semantics verified"
    record.pop("retention_owner", None)
    record.update({"evidence_producer": "Software Development", "evidence_business_owner": "Software Development", "storage_authority": "CSO", "retention_policy_authority": "OPEN", "retention_hold_authority": "OPEN", "deletion_authority": "OPEN", "retention_authority_reference": "registry/external_evidence_retention_authority.json"})
    write_json(prerequisites_path, prerequisites)
    guide = root / "docs/EXTERNAL_REVIEW_EMS_AUTHORITY_GUIDE.md"
    text = guide.read_text(encoding="utf-8")
    text = text.replace("Egnyte logical authority is TWG/TechAudits, but its current Windows operational mapping is inaccessible.", "Egnyte logical authority is TWG/TechAudits, controlled by CSO. Software Development is the evidence producer and business owner, not the storage authority. Its current Windows operational mapping is inaccessible.")
    guide.write_text(text, encoding="utf-8", newline="\n")
    (root / "docs/EXTERNAL_EVIDENCE_RETENTION_AUTHORITY.md").write_text("# External Evidence Retention Authority\n\nThis authority applies only to external-review synthetic evidence. It does not certify compliance, production readiness, or permission to execute the Hometown pilot.\n\nSoftware Development produces and business-owns the evidence. CSO is the storage authority for the approved logical retention authority, **Egnyte / TWG/TechAudits**. The former `retention_owner: Software Development` field did not distinguish those roles and is clarified by this authority; it never granted engineering self-authorization over the CSO-controlled storage location.\n\nRetention is three years. A longer legal or management hold overrides deletion. Retention-policy, hold, deletion, and storage-administrator assignments remain open until recorded by the appropriate controlled authority.\n\n`Z:\\Shared\\TWG\\TechAudits` is a non-authoritative operational mapping only. It is currently inaccessible. No evidence may be written until CSO confirms authorized write access, an approved operational access mechanism, destination readiness, and sufficient hold/deletion semantics.\n", encoding="utf-8", newline="\n")
    gaps = {"component": "P3 External Evidence Retention Finalization", "p2_open_gap_register_reference": "generated/external-review/p2/external_review_open_gap_register.json", "gaps": [{"gap_id": "P3-GAP-01", "title": "Retention role terminology", "state": "RESOLVED_BY_TERMINOLOGY_CLARIFICATION", "details": {"former_ambiguous_value": "retention_owner = Software Development", "evidence_producer_and_business_owner": "Software Development", "storage_authority": "CSO", "authority_model": "registry/external_evidence_retention_authority.json"}}, {"gap_id": "P3-GAP-02", "title": "CSO retention write access and operational mapping", "state": "OPEN/BLOCKED", "details": {"logical_authority": "Egnyte / TWG/TechAudits", "operational_access": "BLOCKED / INACCESSIBLE", "required_action": "CSO must authorize an operator and operational access mechanism, confirm destination readiness, and record hold/deletion authority."}}, {"gap_id": "P3-GAP-03", "title": "Final external-review baseline certification", "state": "OPEN", "details": {"blocked_by": "P3-GAP-02"}}, {"gap_id": "P3-GAP-04", "title": "Hometown pilot execution", "state": "INTENTIONALLY_NOT_AUTHORIZED", "details": {"repository": "hometown", "controlled_id": "REPO-003", "pilot_execution_authorized": False, "production_authorized": False, "hometown_evaluator_executions": 0}}]}
    write_json(root / "generated/external-review/p3/external_review_open_gap_register.json", gaps)


if __name__ == "__main__":
    main()
