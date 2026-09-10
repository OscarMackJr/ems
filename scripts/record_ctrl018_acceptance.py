import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import Draft202012Validator


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rp(root, rel):
    return root / Path(rel.replace("\\", "/"))


ap = argparse.ArgumentParser()
ap.add_argument("--ems-root", required=True)
ap.add_argument("--spec", required=True)
ap.add_argument("--schema", required=True)
ap.add_argument("--decision", required=True, choices=["ACCEPT", "REJECT"])
ap.add_argument("--owner", required=True)
ap.add_argument("--source", required=True)
ap.add_argument("--rationale", required=True)
args = ap.parse_args()

if not args.source.startswith("HUMAN_"):
    raise SystemExit("decision_source must begin with HUMAN_")

ems = Path(args.ems_root).resolve()
spec = load(Path(args.spec))
schema = load(Path(args.schema))
pre = load(rp(ems, spec["acceptance_output"]).parent / "acceptance_preflight.json")
if pre.get("status") != "PASS":
    raise SystemExit("preflight not PASS")

record = {
    "record_version": "1.0",
    "recorded_at_utc": datetime.now(UTC).isoformat(),
    "wave": "2D",
    "control_id": "EMS-CTRL-018",
    "target_id": "REPO-001",
    "request_id": pre["request_id"],
    "acceptance_decision": args.decision,
    "acceptance_state": "ACCEPTED" if args.decision == "ACCEPT" else "REJECTED",
    "decision_owner": args.owner,
    "decision_source": args.source,
    "decision_rationale": args.rationale,
    "input_hashes": pre["input_hashes"],
    "applicability_authority": pre["applicability_authority"],
    "hayes_verify_result": pre["hayes_verify"],
    "promotion_authorized": args.decision == "ACCEPT",
    "promotion_state": "QUALIFIED_NOT_PROMOTED" if args.decision == "ACCEPT" else "NOT_PROMOTED",
}
Draft202012Validator(schema).validate(record)
rp(ems, spec["acceptance_output"]).write_text(json.dumps(record, indent=2), encoding="utf-8")
print(json.dumps(record, indent=2))
