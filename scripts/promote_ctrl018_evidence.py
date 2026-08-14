import argparse
import hashlib
import json
import shutil
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


ap = argparse.ArgumentParser()
ap.add_argument("--ems-root", required=True)
ap.add_argument("--hayes-root", required=True)
ap.add_argument("--spec", required=True)
ap.add_argument("--schema", required=True)
args = ap.parse_args()

ems = Path(args.ems_root).resolve()
hayes = Path(args.hayes_root).resolve()
spec = load(Path(args.spec))
schema = load(Path(args.schema))
accept_path = rp(ems, spec["acceptance_output"])
accept = load(accept_path)

if accept.get("acceptance_state") != "ACCEPTED" or accept.get("promotion_authorized") is not True:
    raise SystemExit("promotion not authorized")

source = rp(hayes, spec["hayes_evidence_relative_path"])
expected = accept["input_hashes"]["evidence_sha256"]
if sha(source) != expected:
    raise SystemExit("source evidence hash changed")

dest = rp(ems, spec["promoted_evidence_output"])
dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(source, dest)
if sha(dest) != expected:
    raise SystemExit("promoted evidence hash mismatch")

record = {
    "record_version": "1.0",
    "promoted_at_utc": datetime.now(UTC).isoformat(),
    "wave": "2D",
    "control_id": "EMS-CTRL-018",
    "target_id": "REPO-001",
    "request_id": accept["request_id"],
    "promotion_state": "PROMOTED",
    "source_system": "Hayes Verify",
    "authority_system": "EMS",
    "authoritative_evidence_path": str(dest.relative_to(ems)).replace("\\", "/"),
    "authoritative_evidence_sha256": sha(dest),
    "source_evidence_sha256": sha(source),
    "acceptance_record_sha256": sha(accept_path),
    "decision_owner": accept["decision_owner"],
    "decision_source": accept["decision_source"],
}
Draft202012Validator(schema).validate(record)
rp(ems, spec["promotion_output"]).write_text(json.dumps(record, indent=2), encoding="utf-8")
print(json.dumps(record, indent=2))
