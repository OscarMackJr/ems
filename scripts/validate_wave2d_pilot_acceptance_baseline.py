import argparse
import hashlib
import json
from pathlib import Path


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()


def rp(root, rel):
    return root / Path(rel.replace("\\", "/"))


ap = argparse.ArgumentParser()
ap.add_argument("--ems-root", required=True)
ap.add_argument("--spec", required=True)
a = ap.parse_args()

ems = Path(a.ems_root).resolve()
spec = load(Path(a.spec))
regp = rp(ems, spec["baseline_registration"])
certp = rp(ems, spec["certification_output"])
manp = rp(ems, spec["manifest_output"])

errors = []
for path in (regp, certp, manp):
    if not path.exists():
        errors.append(f"missing {path}")

if not errors:
    reg = load(regp)
    cert = load(certp)
    man = load(manp)

    if reg.get("status") != "PASS":
        errors.append("baseline registration not PASS")
    if reg.get("baseline_state") != "AUTHORITATIVE":
        errors.append("baseline not AUTHORITATIVE")
    if cert.get("status") != "PASS":
        errors.append("certification not PASS")
    if cert.get("baseline_registration_sha256") != sha(regp):
        errors.append("baseline registration hash mismatch")

    manifest_by_path = {
        item["path"]: item["sha256"]
        for item in man.get("artifacts", [])
    }
    for rel in (
        spec["baseline_registration"],
        spec["acceptance_record"],
        spec["promotion_record"],
        spec["promotion_validation"],
        spec["authoritative_evidence"],
        spec["applicability_source"],
        spec["certification_output"],
    ):
        path = rp(ems, rel)
        if manifest_by_path.get(rel) != sha(path):
            errors.append(f"manifest hash mismatch: {rel}")

out = {
    "status": "PASS" if not errors else "FAIL",
    "wave": spec["wave"],
    "control_id": spec["control_id"],
    "target_id": spec["target_id"],
    "baseline_state": "AUTHORITATIVE" if not errors else "BLOCKED",
    "errors": errors,
}
print(json.dumps(out, indent=2))
raise SystemExit(0 if not errors else 1)
