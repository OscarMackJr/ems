"""Build P3 external-evidence retention package artifacts without writing evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

EXPECTED_COUNT = 52
SOURCE_ROOTS = {
    "hayes-verify-onboarding-preflight": Path(
        "C:/temp/standars/hayes-verify-onboarding-preflight"
    )
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tracked_raw_sha256(root: Path, relative: Path) -> str:
    result = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{relative.as_posix()}"], check=True, stdout=subprocess.PIPE)
    return hashlib.sha256(result.stdout).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    p2 = root / "generated/external-review/p2/external_review_external_evidence_index.json"
    output_dir = root / "generated/external-review/p3"
    output_dir.mkdir(parents=True, exist_ok=True)
    index = json.loads(p2.read_text(encoding="utf-8"))
    artifacts: list[dict[str, object]] = []
    errors: list[str] = []

    for run in index["runs"]:
        for artifact in run["artifacts"]:
            evidence_id = artifact["evidence_id"]
            source_key, logical_path = evidence_id.split(":", 1)
            source_root = SOURCE_ROOTS.get(source_key)
            source = source_root / logical_path if source_root else None
            record = {
                "evidence_id": evidence_id,
                "logical_evidence_path": logical_path,
                "source_repository_identity": source_key,
                "source_path": logical_path,
                "source_raw_sha256": artifact["sha256"],
                "package_raw_sha256": None,
                "size_bytes": artifact["size_bytes"],
                "artifact_type": artifact["artifact_class"],
                "related_run": run["logical_run_id"],
                "related_ems_authority": run["related_ems_authority"],
                "related_hayes_version": run["related_hayes_implementation_version"],
                "retention_period": "3 years; longer legal/management hold overrides deletion",
                "sensitivity_classification": "SYNTHETIC_NON_PRODUCTION_EXTERNAL_REVIEW_EVIDENCE",
            }
            if source is None or not source.is_file():
                errors.append(f"source missing for {evidence_id}")
            else:
                actual_hash = sha256(source)
                actual_size = source.stat().st_size
                record["package_raw_sha256"] = actual_hash
                if actual_hash != artifact["sha256"]:
                    errors.append(f"sha256 mismatch for {evidence_id}")
                if actual_size != artifact["size_bytes"]:
                    errors.append(f"size mismatch for {evidence_id}")
            artifacts.append(record)

    if len(artifacts) != EXPECTED_COUNT:
        errors.append(f"expected {EXPECTED_COUNT} artifacts, found {len(artifacts)}")

    manifest = {
        "component": "EMS External Review P3",
        "phase": "External Evidence Retention Finalization",
        "manifest_state": "STAGING_ONLY_PACKAGE_READY" if not errors else "VALIDATION_FAILED",
        "source_p2_evidence_index": "generated/external-review/p2/external_review_external_evidence_index.json",
        "source_p2_evidence_index_sha256": tracked_raw_sha256(root, p2.relative_to(root)),
        "external_evidence_artifact_count": len(artifacts),
        "final_retention_authority": "Egnyte / TWG/TechAudits",
        "operational_mapping": "NOT_AUTHORITATIVE; BLOCKED / INACCESSIBLE",
        "retention_write_authorized": False,
        "staging_only": True,
        "not_final_retention_authority": True,
        "artifacts": artifacts,
        "errors": errors,
    }
    manifest_path = output_dir / "external_evidence_retention_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    blocker = {
        "component": "EMS External Review P3",
        "status": "BLOCKED",
        "certification_scope": "EXTERNAL_EVIDENCE_RETENTION_ONLY",
        "external_evidence_package_ready": not errors,
        "external_evidence_retained": False,
        "retention_write_authorized": False,
        "artifact_count": len(artifacts),
        "manifest_path": str(manifest_path.relative_to(root)).replace("\\", "/"),
        "manifest_sha256": sha256(manifest_path),
        "approved_logical_authority": "Egnyte / TWG/TechAudits",
        "storage_authority": "CSO",
        "operational_access_state": "BLOCKED / INACCESSIBLE",
        "unresolved_action": "CSO must confirm authorized write access and an approved operational access mechanism for Egnyte / TWG/TechAudits; hold/deletion authority must also be recorded.",
        "errors": errors,
    }
    blocker_path = output_dir / "external_evidence_retention_blocker.json"
    blocker_path.write_text(json.dumps(blocker, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"manifest": str(manifest_path), "blocker": str(blocker_path), "errors": errors}))


if __name__ == "__main__":
    main()
