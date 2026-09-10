import argparse
import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


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


def applicability(ems, spec):
    inspected = []
    for rel in spec["ems_applicability_matrix_candidates"]:
        path = rp(ems, rel)
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("control_id") == spec["control_id"] and row.get("target_id") == spec["target_id"]:
                    decision = (row.get("applicability_state") or "").strip().upper()
                    inspected.append({"source": str(path), "decision": decision or "UNKNOWN", "source_sha256": sha(path)})
                    if decision == "APPLICABLE":
                        return {"status": "PASS", "decision": decision, "source": str(path), "source_sha256": sha(path), "inspected_sources": inspected}
                    if decision == "NOT_APPLICABLE":
                        return {"status": "FAIL", "decision": decision, "source": str(path), "source_sha256": sha(path), "inspected_sources": inspected}
    return {"status": "FAIL", "decision": "UNKNOWN", "source": None, "source_sha256": None, "inspected_sources": inspected}


ap = argparse.ArgumentParser()
ap.add_argument("--ems-root", required=True)
ap.add_argument("--hayes-root", required=True)
ap.add_argument("--spec", required=True)
args = ap.parse_args()

ems = Path(args.ems_root).resolve()
hayes = Path(args.hayes_root).resolve()
spec = load(Path(args.spec))
paths = {
    "envelope": rp(hayes, spec["hayes_return_envelope_relative_path"]),
    "cert": rp(hayes, spec["hayes_live_certification_relative_path"]),
    "evidence": rp(hayes, spec["hayes_evidence_relative_path"]),
    "result": rp(hayes, spec["hayes_result_relative_path"]),
}
errors = [f"missing Hayes {key}: {path}" for key, path in paths.items() if not path.exists()]
if errors:
    print(json.dumps({"status": "FAIL", "errors": errors}, indent=2))
    raise SystemExit(1)

env = load(paths["envelope"])
cert = load(paths["cert"])
for field, expected in (
    ("control_id", "EMS-CTRL-018"),
    ("target_id", "REPO-001"),
    ("evaluation_state", "COMPLETE"),
    ("evidence_state", "SUFFICIENT"),
    ("acceptance_state", "PENDING_EMS_ACCEPTANCE"),
    ("promotion_state", "NOT_PROMOTED"),
):
    if env.get(field) != expected:
        errors.append(f"{field} mismatch")

hashes = {
    "evidence_sha256": sha(paths["evidence"]),
    "result_sha256": sha(paths["result"]),
    "certification_sha256": sha(paths["cert"]),
}
for field, value in hashes.items():
    if env.get(field) != value:
        errors.append(f"{field} mismatch")

if cert.get("status") != "PASS":
    errors.append("Hayes certification not PASS")

app = applicability(ems, spec)
if app["status"] != "PASS":
    errors.append(f"EMS applicability is {app['decision']}")

preflight = {
    "component": "EMS",
    "phase": "CTRL-018 Pilot Result Acceptance Preflight",
    "prepared_at_utc": datetime.now(UTC).isoformat(),
    "status": "PASS" if not errors else "FAIL",
    "wave": "2D",
    "control_id": "EMS-CTRL-018",
    "target_id": "REPO-001",
    "request_id": env.get("request_id"),
    "hayes_verify": {
        "evaluation_state": env.get("evaluation_state"),
        "evidence_state": env.get("evidence_state"),
        "result_state": env.get("result_state"),
        "acceptance_state": env.get("acceptance_state"),
        "promotion_state": env.get("promotion_state"),
        "evaluated_branch": env.get("evaluated_branch"),
    },
    "applicability_authority": {
        "system": "EMS",
        "decision": app["decision"],
        "source": app["source"],
        "source_sha256": app["source_sha256"],
        "inspected_sources": app["inspected_sources"],
    },
    "input_hashes": hashes,
    "errors": errors,
}
out = rp(ems, spec["acceptance_output"]).parent / "acceptance_preflight.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(preflight, indent=2), encoding="utf-8")
print(json.dumps(preflight, indent=2))
raise SystemExit(0 if not errors else 1)
