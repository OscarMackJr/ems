import argparse
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path


def load_jsonl(path):
    rows=[]
    with Path(path).open("r",encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


ap=argparse.ArgumentParser()
ap.add_argument("--ems-root",required=True)
ap.add_argument("--batch-id",required=True)
ap.add_argument("--decisions",required=True)
ap.add_argument("--promotion-root",required=True)
ap.add_argument("--evidence-root",required=True)
args=ap.parse_args()

ems=Path(args.ems_root).resolve()
promotion_root=Path(args.promotion_root)
evidence_root=Path(args.evidence_root)
records=[]
errors=[]

for row in load_jsonl(args.decisions):
    if row.get("batch_id") != args.batch_id:
        errors.append(f"decision batch mismatch: {row.get('control_id')}/{row.get('target_id')}")
        continue
    if row.get("acceptance_state") != "ACCEPTED":
        continue
    if row.get("evidence_state") != "SUFFICIENT":
        errors.append(f"accepted row is not SUFFICIENT: {row.get('control_id')}/{row.get('target_id')}")
        continue

    src=Path(row["source_evidence_path"])
    if not src.exists():
        errors.append(f"missing source evidence: {src}")
        continue
    if sha(src) != row["evidence_sha256"]:
        errors.append(f"evidence hash mismatch: {row.get('control_id')}/{row.get('target_id')}")
        continue

    dst=evidence_root/row["control_id"]/row["target_id"]/"evidence.json"
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dst)

    rec={
        "record_version":"1.0",
        "batch_id":args.batch_id,
        "wave":"2D",
        "control_id":row["control_id"],
        "target_id":row["target_id"],
        "result_state":row["result_state"],
        "acceptance_state":"ACCEPTED",
        "promotion_state":"PROMOTED",
        "promoted_at_utc":datetime.now(UTC).isoformat(),
        "authoritative_evidence_path":str(dst.relative_to(ems)).replace("\\","/"),
        "authoritative_evidence_sha256":sha(dst),
        "result_sha256":row["result_sha256"],
        "decision_owner":row.get("decision_owner"),
        "acceptance_mode":row.get("acceptance_mode"),
    }
    recp=promotion_root/row["control_id"]/row["target_id"]/"promotion_record.json"
    recp.parent.mkdir(parents=True,exist_ok=True)
    recp.write_text(json.dumps(rec,indent=2),encoding="utf-8")
    records.append(rec)

summary={
    "status":"PASS" if not errors else "FAIL",
    "batch_id":args.batch_id,
    "promoted_count":len(records),
    "promoted_pass_count":sum(r["result_state"]=="PASS" for r in records),
    "promoted_fail_count":sum(r["result_state"]=="FAIL" for r in records),
    "errors":errors,
}
print(json.dumps(summary,indent=2))
raise SystemExit(0 if not errors else 1)
