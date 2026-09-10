import argparse
import hashlib
import json
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


ap = argparse.ArgumentParser()
ap.add_argument("--ems-root", required=True)
ap.add_argument("--spec", required=True)
args = ap.parse_args()

ems = Path(args.ems_root).resolve()
spec = load(Path(args.spec))
errors = []
accept_path = rp(ems, spec["acceptance_output"])
promotion_path = rp(ems, spec["promotion_output"])
evidence_path = rp(ems, spec["promoted_evidence_output"])

for path in (accept_path, promotion_path, evidence_path):
    if not path.exists():
        errors.append(f"missing {path}")

if not errors:
    accept = load(accept_path)
    promotion = load(promotion_path)
    if accept.get("acceptance_state") != "ACCEPTED":
        errors.append("acceptance not ACCEPTED")
    if promotion.get("promotion_state") != "PROMOTED":
        errors.append("promotion not PROMOTED")
    if promotion.get("acceptance_record_sha256") != sha(accept_path):
        errors.append("acceptance hash mismatch")
    if promotion.get("authoritative_evidence_sha256") != sha(evidence_path):
        errors.append("evidence hash mismatch")

out = {
    "status": "PASS" if not errors else "FAIL",
    "control_id": "EMS-CTRL-018",
    "target_id": "REPO-001",
    "acceptance_state": "ACCEPTED" if not errors else "UNKNOWN",
    "promotion_state": "PROMOTED" if not errors else "UNKNOWN",
    "errors": errors,
}
rp(ems, spec["validation_output"]).write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=2))
raise SystemExit(0 if not errors else 1)
