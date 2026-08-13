import argparse
import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import Draft202012Validator


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()


def rp(root, rel):
    return root / Path(rel.replace("\\", "/"))


def find_applicability(path, control_id, target_id):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        if row.get("control_id") == control_id and row.get("target_id") == target_id:
            return (row.get("applicability_state") or "").strip().upper(), row
    return "UNKNOWN", None


ap = argparse.ArgumentParser()
ap.add_argument("--ems-root", required=True)
ap.add_argument("--spec", required=True)
ap.add_argument("--schema", required=True)
a = ap.parse_args()

ems = Path(a.ems_root).resolve()
spec = load_json(Path(a.spec))
schema = load_json(Path(a.schema))

paths = {
    "acceptance": rp(ems, spec["acceptance_record"]),
    "promotion": rp(ems, spec["promotion_record"]),
    "validation": rp(ems, spec["promotion_validation"]),
    "evidence": rp(ems, spec["authoritative_evidence"]),
    "applicability": rp(ems, spec["applicability_source"]),
}
errors = []
for name, path in paths.items():
    if not path.exists():
        errors.append(f"missing {name}: {path}")

if errors:
    print(json.dumps({"status": "FAIL", "errors": errors}, indent=2))
    raise SystemExit(1)

accept = load_json(paths["acceptance"])
promo = load_json(paths["promotion"])
val = load_json(paths["validation"])
app_decision, app_row = find_applicability(
    paths["applicability"],
    spec["control_id"],
    spec["target_id"],
)

if accept.get("acceptance_state") != "ACCEPTED":
    errors.append("acceptance_state is not ACCEPTED")
if accept.get("promotion_authorized") is not True:
    errors.append("promotion_authorized is not true")
if promo.get("promotion_state") != "PROMOTED":
    errors.append("promotion_state is not PROMOTED")
if val.get("status") != "PASS":
    errors.append("promotion validation status is not PASS")
if val.get("acceptance_state") != "ACCEPTED":
    errors.append("promotion validation acceptance state is not ACCEPTED")
if val.get("promotion_state") != "PROMOTED":
    errors.append("promotion validation promotion state is not PROMOTED")
if app_decision != "APPLICABLE":
    errors.append(f"applicability decision is {app_decision}")

if promo.get("acceptance_record_sha256") != sha256(paths["acceptance"]):
    errors.append("promotion record acceptance hash mismatch")
if promo.get("authoritative_evidence_sha256") != sha256(paths["evidence"]):
    errors.append("promotion record evidence hash mismatch")
if promo.get("source_evidence_sha256") != sha256(paths["evidence"]):
    errors.append("source/promoted evidence hash mismatch")

result_state = accept.get("hayes_verify_result", {}).get("result_state")
if result_state != "PASS":
    errors.append(f"accepted Hayes result_state is {result_state!r}, expected PASS")

registration = {
    "baseline_version": "1.0",
    "registered_at_utc": datetime.now(UTC).isoformat(),
    "wave": spec["wave"],
    "control_id": spec["control_id"],
    "target_id": spec["target_id"],
    "request_id": accept.get("request_id"),
    "status": "PASS" if not errors else "FAIL",
    "baseline_state": "AUTHORITATIVE" if not errors else "BLOCKED",
    "acceptance_state": accept.get("acceptance_state"),
    "promotion_state": promo.get("promotion_state"),
    "result_state": result_state,
    "applicability_decision": app_decision,
    "decision_owner": accept.get("decision_owner"),
    "decision_source": accept.get("decision_source"),
    "decision_rationale": accept.get("decision_rationale"),
    "hashes": {
        "acceptance_record_sha256": sha256(paths["acceptance"]),
        "promotion_record_sha256": sha256(paths["promotion"]),
        "promotion_validation_sha256": sha256(paths["validation"]),
        "authoritative_evidence_sha256": sha256(paths["evidence"]),
        "applicability_source_sha256": sha256(paths["applicability"]),
    },
    "authoritative_paths": {
        "acceptance_record": spec["acceptance_record"],
        "promotion_record": spec["promotion_record"],
        "authoritative_evidence": spec["authoritative_evidence"],
        "applicability_source": spec["applicability_source"],
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
    "phase": "Pilot Acceptance Baseline Certification",
    "certified_at_utc": datetime.now(UTC).isoformat(),
    "status": "PASS" if not errors else "FAIL",
    "baseline_registration": spec["baseline_registration"],
    "baseline_registration_sha256": sha256(regp),
    "wave": spec["wave"],
    "control_id": spec["control_id"],
    "target_id": spec["target_id"],
    "baseline_state": registration["baseline_state"],
    "acceptance_state": registration["acceptance_state"],
    "promotion_state": registration["promotion_state"],
    "result_state": registration["result_state"],
    "applicability_decision": registration["applicability_decision"],
    "errors": errors,
}
certp = rp(ems, spec["certification_output"])
certp.parent.mkdir(parents=True, exist_ok=True)
certp.write_text(json.dumps(cert, indent=2), encoding="utf-8")

manifest = {
    "component": "EMS",
    "wave": spec["wave"],
    "control_id": spec["control_id"],
    "target_id": spec["target_id"],
    "created_at_utc": datetime.now(UTC).isoformat(),
    "status": "PASS" if not errors else "FAIL",
    "artifacts": [
        {"path": spec["baseline_registration"], "sha256": sha256(regp)},
        {"path": spec["acceptance_record"], "sha256": sha256(paths["acceptance"])},
        {"path": spec["promotion_record"], "sha256": sha256(paths["promotion"])},
        {"path": spec["promotion_validation"], "sha256": sha256(paths["validation"])},
        {"path": spec["authoritative_evidence"], "sha256": sha256(paths["evidence"])},
        {"path": spec["applicability_source"], "sha256": sha256(paths["applicability"])},
        {"path": spec["certification_output"], "sha256": sha256(certp)},
    ],
    "errors": errors,
}
manp = rp(ems, spec["manifest_output"])
manp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

print(json.dumps(cert, indent=2))
raise SystemExit(0 if not errors else 1)
