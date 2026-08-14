import argparse
import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import Draft202012Validator


def load(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()
def rp(root,rel): return root/Path(rel.replace("\\","/"))
def app(path,cid,tid):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        for row in csv.DictReader(f):
            if row.get("control_id")==cid and row.get("target_id")==tid:
                return (row.get("applicability_state") or "").strip().upper()
    return "UNKNOWN"
ap=argparse.ArgumentParser();ap.add_argument("--ems-root",required=True);ap.add_argument("--spec",required=True);ap.add_argument("--schema",required=True)
a=ap.parse_args();ems=Path(a.ems_root).resolve();spec=load(Path(a.spec));schema=load(Path(a.schema))
p={k:rp(ems,spec[k]) for k in ("acceptance_record","promotion_record","promotion_validation","authoritative_evidence","applicability_source")}
errors=[f"missing {k}: {v}" for k,v in p.items() if not v.exists()]
if errors: print(json.dumps({"status":"FAIL","errors":errors},indent=2));raise SystemExit(1)
acc=load(p["acceptance_record"]);pro=load(p["promotion_record"]);val=load(p["promotion_validation"]);ad=app(p["applicability_source"],"EMS-CTRL-010","REPO-001")
if acc.get("acceptance_state")!="ACCEPTED": errors.append("acceptance not ACCEPTED")
if pro.get("promotion_state")!="PROMOTED": errors.append("promotion not PROMOTED")
if val.get("status")!="PASS": errors.append("promotion validation not PASS")
if ad!="APPLICABLE": errors.append(f"applicability={ad}")
if pro.get("acceptance_record_sha256")!=sha(p["acceptance_record"]): errors.append("acceptance hash mismatch")
if pro.get("authoritative_evidence_sha256")!=sha(p["authoritative_evidence"]): errors.append("evidence hash mismatch")
reg={"baseline_version":"1.0","registered_at_utc":datetime.now(UTC).isoformat(),"wave":"2D","control_id":"EMS-CTRL-010","target_id":"REPO-001","request_id":acc.get("request_id"),"status":"PASS" if not errors else "FAIL","baseline_state":"AUTHORITATIVE" if not errors else "BLOCKED","acceptance_state":acc.get("acceptance_state"),"promotion_state":pro.get("promotion_state"),"result_state":acc.get("hayes_verify_result",{}).get("result_state"),"applicability_decision":ad,"hashes":{"acceptance_record_sha256":sha(p["acceptance_record"]),"promotion_record_sha256":sha(p["promotion_record"]),"promotion_validation_sha256":sha(p["promotion_validation"]),"authoritative_evidence_sha256":sha(p["authoritative_evidence"]),"applicability_source_sha256":sha(p["applicability_source"])},"errors":errors}
if not errors: Draft202012Validator(schema).validate(reg)
regp=rp(ems,spec["baseline_registration"]);regp.parent.mkdir(parents=True,exist_ok=True);regp.write_text(json.dumps(reg,indent=2),encoding="utf-8")
cert={"component":"EMS","phase":"CTRL-010 Pilot Acceptance Baseline Certification","certified_at_utc":datetime.now(UTC).isoformat(),"status":"PASS" if not errors else "FAIL","baseline_registration":spec["baseline_registration"],"baseline_registration_sha256":sha(regp),"wave":"2D","control_id":"EMS-CTRL-010","target_id":"REPO-001","baseline_state":reg["baseline_state"],"acceptance_state":reg["acceptance_state"],"promotion_state":reg["promotion_state"],"result_state":reg["result_state"],"applicability_decision":reg["applicability_decision"],"errors":errors}
cp=rp(ems,spec["certification_output"]);cp.parent.mkdir(parents=True,exist_ok=True);cp.write_text(json.dumps(cert,indent=2),encoding="utf-8")
man={"status":"PASS" if not errors else "FAIL","artifacts":[{"path":spec["baseline_registration"],"sha256":sha(regp)},{"path":spec["acceptance_record"],"sha256":sha(p["acceptance_record"])},{"path":spec["promotion_record"],"sha256":sha(p["promotion_record"])},{"path":spec["promotion_validation"],"sha256":sha(p["promotion_validation"])},{"path":spec["authoritative_evidence"],"sha256":sha(p["authoritative_evidence"])},{"path":spec["applicability_source"],"sha256":sha(p["applicability_source"])},{"path":spec["certification_output"],"sha256":sha(cp)}],"errors":errors}
rp(ems,spec["manifest_output"]).write_text(json.dumps(man,indent=2),encoding="utf-8")
print(json.dumps(cert,indent=2));raise SystemExit(0 if not errors else 1)
