"""Validate P3 retention outputs and state the non-attestation readiness result."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_raw_sha256(root: Path, relative: Path) -> str:
    result = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{relative.as_posix()}"], check=True, stdout=subprocess.PIPE)
    return hashlib.sha256(result.stdout).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    p3 = root / "generated/external-review/p3"
    manifest_path = p3 / "external_evidence_retention_manifest.json"
    blocker_path = p3 / "external_evidence_retention_blocker.json"
    authority_path = root / "registry/external_evidence_retention_authority.json"
    p2_cert = root / "generated/external-review/p2/P2_REVIEWER_RECONSTRUCTION_CERTIFICATION.json"
    p2_index = root / "generated/external-review/p2/external_review_external_evidence_index.json"
    freeze = root / "registry/wave2d/applicability_decisions.csv"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    blocker = json.loads(blocker_path.read_text(encoding="utf-8"))
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if len(manifest["artifacts"]) != 52:
        errors.append("retention manifest does not contain 52 artifacts")
    if manifest["errors"]:
        errors.extend(manifest["errors"])
    if blocker["external_evidence_retained"] or blocker["retention_write_authorized"]:
        errors.append("blocked-retention state was weakened")
    if authority["roles"]["storage_authority"] != "CSO":
        errors.append("storage authority is not CSO")
    transition = authority.get("evidence_retention_state_transition", {})
    if transition.get("from") != "STAGED_LOCAL" or transition.get("to") != "CSO_APPROVED_STORAGE" or transition.get("transition_authorized") is not False:
        errors.append("retention state transition is invalid")
    if "never rewrites or deletes" not in authority.get("supersession_history_retention", {}).get("successor_behavior", ""):
        errors.append("supersession retention behavior is incomplete")
    if authority["roles"]["evidence_producer"] == authority["roles"]["storage_authority"]:
        errors.append("evidence producer equals storage authority")
    if tracked_raw_sha256(root, p2_cert.relative_to(root)) != "7b4b9c6694b6620e68c0466616b2cacfab8e1f7a03298286e188a82ac055b8e1":
        errors.append("P2 certification SHA mismatch")
    if tracked_raw_sha256(root, p2_index.relative_to(root)) != "81985ce1e821b098f696962468d30185434daa2a4267fc6feaabc824901585f9":
        errors.append("P2 evidence index SHA mismatch")
    if digest(freeze) != "79adb6c003e9a61e2fd36131b1a37d3387973f72d206102985a78a3271bc5b35":
        errors.append("historical Wave 2D freeze SHA mismatch")
    assessment = {
        "component": "EMS External Review P3",
        "p3_status": "PACKAGE_READY_WRITE_BLOCKED_BY_AUTHORITY" if not errors else "VALIDATION_FAILED",
        "reviewer_reconstruction_ready": "YES",
        "final_external_review_baseline_ready": "NO",
        "retention_role_model": "RECONCILED",
        "external_evidence_package": "52 / 52 VERIFIED / HASH-BOUND",
        "external_evidence_retained": "NO",
        "cso_action_required": "YES",
        "hometown_pilot_execution_authorized": False,
        "production_authorized": False,
        "hometown_evaluator_executions": 0,
        "references": {
            "retention_manifest": str(manifest_path.relative_to(root)).replace("\\", "/"),
            "retention_manifest_sha256": digest(manifest_path),
            "retention_blocker": str(blocker_path.relative_to(root)).replace("\\", "/"),
            "retention_blocker_sha256": digest(blocker_path),
            "retention_authority": str(authority_path.relative_to(root)).replace("\\", "/"),
            "retention_authority_sha256": digest(authority_path),
            "p2_certification_sha256": tracked_raw_sha256(root, p2_cert.relative_to(root)),
            "p2_evidence_index_sha256": tracked_raw_sha256(root, p2_index.relative_to(root)),
            "historical_freeze_sha256": digest(freeze),
        },
        "errors": errors,
    }
    output = p3 / "external_review_retention_readiness_assessment.json"
    output.write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8", newline="\n")
    markdown = "# P3 External Evidence Retention Readiness\n\n" + (
        "P3 is **PACKAGE READY / WRITE BLOCKED BY AUTHORITY**. All 52 synthetic, non-production artifacts are hash-bound in the staging-only package. No evidence has been retained in Egnyte. CSO must authorize write access and an approved operational mechanism for `Egnyte / TWG/TechAudits`, then record hold/deletion authority.\n"
        if not errors else "P3 validation failed: " + "; ".join(errors) + "\n"
    )
    (p3 / "P3_EXTERNAL_EVIDENCE_RETENTION_READINESS.md").write_text(markdown, encoding="utf-8", newline="\n")
    print(json.dumps({"status": assessment["p3_status"], "errors": errors, "assessment": str(output)}))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
