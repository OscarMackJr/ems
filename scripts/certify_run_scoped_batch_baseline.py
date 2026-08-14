import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


ap=argparse.ArgumentParser()
ap.add_argument("--ems-root",required=True)
ap.add_argument("--batch-id",required=True)
ap.add_argument("--promotion-root",required=True)
ap.add_argument("--manifest",required=True)
ap.add_argument("--registration",required=True)
ap.add_argument("--certification",required=True)
args=ap.parse_args()

ems=Path(args.ems_root).resolve()
promotion_root=Path(args.promotion_root)
errors=[]
items=[]

for recp in promotion_root.rglob("promotion_record.json"):
    rec=json.loads(recp.read_text(encoding="utf-8-sig"))
    if rec.get("batch_id") != args.batch_id:
        errors.append(f"promotion record batch mismatch: {recp}")
        continue
    ev=ems/rec["authoritative_evidence_path"]
    if not ev.exists():
        errors.append(f"missing authoritative evidence: {ev}")
        continue
    if sha(ev) != rec["authoritative_evidence_sha256"]:
        errors.append(f"authoritative evidence hash mismatch: {ev}")
        continue
    items.append({
        "batch_id":args.batch_id,
        "control_id":rec["control_id"],
        "target_id":rec["target_id"],
        "result_state":rec["result_state"],
        "promotion_record":str(recp.relative_to(ems)).replace("\\","/"),
        "promotion_record_sha256":sha(recp),
        "evidence_path":str(ev.relative_to(ems)).replace("\\","/"),
        "evidence_sha256":sha(ev),
        "result_sha256":rec["result_sha256"],
    })

manifest={
    "manifest_version":"1.0",
    "batch_id":args.batch_id,
    "wave":"2D",
    "generated_at_utc":datetime.now(UTC).isoformat(),
    "status":"PASS" if not errors else "FAIL",
    "promoted_count":len(items),
    "pass_count":sum(i["result_state"]=="PASS" for i in items),
    "fail_count":sum(i["result_state"]=="FAIL" for i in items),
    "items":items,
    "errors":errors,
}
manifestp=Path(args.manifest)
manifestp.parent.mkdir(parents=True,exist_ok=True)
manifestp.write_text(json.dumps(manifest,indent=2),encoding="utf-8")

registration={
    "baseline_version":"1.0",
    "batch_id":args.batch_id,
    "wave":"2D",
    "registered_at_utc":datetime.now(UTC).isoformat(),
    "status":"PASS" if not errors else "FAIL",
    "baseline_state":"AUTHORITATIVE" if not errors else "BLOCKED",
    "manifest_sha256":sha(manifestp),
    "promoted_count":len(items),
    "pass_count":manifest["pass_count"],
    "fail_count":manifest["fail_count"],
    "errors":errors,
}
regp=Path(args.registration)
regp.parent.mkdir(parents=True,exist_ok=True)
regp.write_text(json.dumps(registration,indent=2),encoding="utf-8")

cert={
    "component":"EMS",
    "phase":"Wave 2D Run-Scoped Batch Baseline Certification",
    "certified_at_utc":datetime.now(UTC).isoformat(),
    "status":"PASS" if not errors else "FAIL",
    "batch_id":args.batch_id,
    "baseline_state":registration["baseline_state"],
    "promoted_count":len(items),
    "pass_count":manifest["pass_count"],
    "fail_count":manifest["fail_count"],
    "baseline_registration_sha256":sha(regp),
    "manifest_sha256":sha(manifestp),
    "errors":errors,
}
certp=Path(args.certification)
certp.parent.mkdir(parents=True,exist_ok=True)
certp.write_text(json.dumps(cert,indent=2),encoding="utf-8")
print(json.dumps(cert,indent=2))
raise SystemExit(0 if not errors else 1)
