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
regp = rp(ems, spec["baseline_registration"])
certp = rp(ems, spec["certification_output"])
manifestp = rp(ems, spec["manifest_output"])
errors = []

for path in (regp, certp, manifestp):
    if not path.exists():
        errors.append(f"missing {path}")

if not errors:
    registration = load(regp)
    cert = load(certp)
    if registration.get("status") != "PASS" or registration.get("baseline_state") != "AUTHORITATIVE":
        errors.append("baseline not authoritative")
    if cert.get("status") != "PASS" or cert.get("baseline_registration_sha256") != sha(regp):
        errors.append("certification/hash invalid")

out = {"status": "PASS" if not errors else "FAIL", "wave": "2D", "control_id": "EMS-CTRL-018", "target_id": "REPO-001", "baseline_state": "AUTHORITATIVE" if not errors else "BLOCKED", "errors": errors}
print(json.dumps(out, indent=2))
raise SystemExit(0 if not errors else 1)
