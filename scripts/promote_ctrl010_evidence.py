import argparse, hashlib, json, shutil
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
ap=argparse.ArgumentParser();ap.add_argument("--ems-root",required=True);ap.add_argument("--hayes-root",required=True);ap.add_argument("--spec",required=True);ap.add_argument("--schema",required=True)
a=ap.parse_args();ems=Path(a.ems_root).resolve();hayes=Path(a.hayes_root).resolve();spec=load(Path(a.spec));schema=load(Path(a.schema))
accp=rp(ems,spec["acceptance_output"]);acc=load(accp)
if acc.get("acceptance_state")!="ACCEPTED" or acc.get("promotion_authorized") is not True: raise SystemExit("promotion not authorized")
src=rp(hayes,spec["hayes_evidence_relative_path"]);expected=acc["input_hashes"]["evidence_sha256"]
if sha(src)!=expected: raise SystemExit("source evidence hash changed")
dst=rp(ems,spec["promoted_evidence_output"]);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
if sha(dst)!=expected: raise SystemExit("promoted evidence hash mismatch")
rec={"record_version":"1.0","promoted_at_utc":datetime.now(UTC).isoformat(),"wave":"2D","control_id":"EMS-CTRL-010","target_id":"REPO-001","request_id":acc["request_id"],"promotion_state":"PROMOTED","source_system":"Hayes Verify","authority_system":"EMS","authoritative_evidence_path":str(dst.relative_to(ems)).replace("\\","/"),"authoritative_evidence_sha256":sha(dst),"source_evidence_sha256":sha(src),"acceptance_record_sha256":sha(accp),"decision_owner":acc["decision_owner"],"decision_source":acc["decision_source"]}
Draft202012Validator(schema).validate(rec);rp(ems,spec["promotion_output"]).write_text(json.dumps(rec,indent=2),encoding="utf-8");print(json.dumps(rec,indent=2))
