import argparse
import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import Draft202012Validator


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rp(root, rel):
    return root / Path(rel.replace("\\", "/"))


def app(path, control_id, target_id):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("control_id") == control_id and row.get("target_id") == target_id:
                return (row.get("applicability_state") or "").strip().upper()
    return "UNKNOWN"


ap = argparse.ArgumentParser()
ap.add_argument("--ems-root", required=True)
ap.add_argument("--spec", required=True)
ap.add_argument("--schema", required=True)
args = ap.parse_args()

ems = Path(args.ems_root).resolve()
spec = load(Path(args.spec))
schema = load(Path(args.schema))
paths = {key: rp(ems, spec[key]) for key in ("acceptance_record","promotion_record","promotion_validation","authoritative_evidence","applicability_source")}
errors = [f"missing {key}: {path}" for key, path in paths.items() if not path.exists()]
if errors:
    print(json.dumps({"status": "FAIL", "errors": errors}, indent=2))
    raise SystemExit(1)

accept = load(paths["acceptance_record"])
promotion = load(paths["promotion_record"])
validation = load(paths["promotion_validation"])
decision = app(paths["applicability_source"], "EMS-CTRL-018", "REPO-001")

if accept.get("acceptance_state") != "ACCEPTED":
    errors.append("acceptance not ACCEPTED")
if promotion.get("promotion_state") != "PROMOTED":
    errors.append("promotion not PROMOTED")
if validation.get("status") != "PASS":
    errors.append("promotion validation not PASS")
if decision != "APPLICABLE":
    errors.append(f"applicability={decision}")
if promotion.get("acceptance_record_sha256") != sha(paths["acceptance_record"]):
    errors.append("acceptance hash mismatch")
if promotion.get("authoritative_evidence_sha256") != sha(paths["authoritative_evidence"]):
    errors.append("evidence hash mismatch")

registration = {
    "baseline_version": "1.0",
    "registered_at_utc": datetime.now(UTC).isoformat(),
    "wave": "2D",
    "control_id": "EMS-CTRL-018",
    "target_id": "REPO-001",
    "request_id": accept.get("request_id"),
    "status": "PASS" if not errors else "FAIL",
    "baseline_state": "AUTHORITATIVE" if not errors else "BLOCKED",
    "acceptance_state": accept.get("acceptance_state"),
    "promotion_state": promotion.get("promotion_state"),
    "result_state": accept.get("hayes_verify_result", {}).get("result_state"),
    "applicability_decision": decision,
    "hashes": {
        "acceptance_record_sha256": sha(paths["acceptance_record"]),
        "promotion_record_sha256": sha(paths["promotion_record"]),
        "promotion_validation_sha256": sha(paths["promotion_validation"]),
        "authoritative_evidence_sha256": sha(paths["authoritative_evidence"]),
        "applicability_source_sha256": sha(paths["applicability_source"]),
    },
    "errors": errors,
}
if not errors:
    Draft202012Validator(schema).validate(registration)

regp = rp(ems, spec["baseline_registration"])
regp.parent.mkdir(parents=True, exist_ok=True)
regp.write_text(json.dumps(registration, indent=2), encoding="utf-8")

cert = {
    "component": "EMS",
    "phase": "CTRL-018 Pilot Acceptance Baseline Certification",
    "certified_at_utc": datetime.now(UTC).isoformat(),
    "status": "PASS" if not errors else "FAIL",
    "baseline_registration": spec["baseline_registration"],
    "baseline_registration_sha256": sha(regp),
    "wave": "2D",
    "control_id": "EMS-CTRL-018",
    "target_id": "REPO-001",
    "baseline_state": registration["baseline_state"],
    "acceptance_state": registration["acceptance_state"],
    "promotion_state": registration["promotion_state"],
    "result_state": registration["result_state"],
    "applicability_decision": registration["applicability_decision"],
    "errors": errors,
}
cp = rp(ems, spec["certification_output"])
cp.parent.mkdir(parents=True, exist_ok=True)
cp.write_text(json.dumps(cert, indent=2), encoding="utf-8")

manifest = {
    "status": "PASS" if not errors else "FAIL",
    "artifacts": [
        {"path": spec["baseline_registration"], "sha256": sha(regp)},
        {"path": spec["acceptance_record"], "sha256": sha(paths["acceptance_record"])},
        {"path": spec["promotion_record"], "sha256": sha(paths["promotion_record"])},
        {"path": spec["promotion_validation"], "sha256": sha(paths["promotion_validation"])},
        {"path": spec["authoritative_evidence"], "sha256": sha(paths["authoritative_evidence"])},
        {"path": spec["applicability_source"], "sha256": sha(paths["applicability_source"])},
        {"path": spec["certification_output"], "sha256": sha(cp)},
    ],
    "errors": errors,
}
rp(ems, spec["manifest_output"]).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(cert, indent=2))
raise SystemExit(0 if not errors else 1)
