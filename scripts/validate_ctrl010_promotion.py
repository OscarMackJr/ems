import argparse, hashlib, json
from pathlib import Path
def load(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()
def rp(root,rel): return root/Path(rel.replace("\\","/"))
ap=argparse.ArgumentParser();ap.add_argument("--ems-root",required=True);ap.add_argument("--spec",required=True)
a=ap.parse_args();ems=Path(a.ems_root).resolve();spec=load(Path(a.spec));errors=[]
accp=rp(ems,spec["acceptance_output"]);prop=rp(ems,spec["promotion_output"]);evp=rp(ems,spec["promoted_evidence_output"])
for p in (accp,prop,evp):
    if not p.exists(): errors.append(f"missing {p}")
if not errors:
    acc=load(accp);pro=load(prop)
    if acc.get("acceptance_state")!="ACCEPTED": errors.append("acceptance not ACCEPTED")
    if pro.get("promotion_state")!="PROMOTED": errors.append("promotion not PROMOTED")
    if pro.get("acceptance_record_sha256")!=sha(accp): errors.append("acceptance hash mismatch")
    if pro.get("authoritative_evidence_sha256")!=sha(evp): errors.append("evidence hash mismatch")
out={"status":"PASS" if not errors else "FAIL","control_id":"EMS-CTRL-010","target_id":"REPO-001","acceptance_state":"ACCEPTED" if not errors else "UNKNOWN","promotion_state":"PROMOTED" if not errors else "UNKNOWN","errors":errors}
rp(ems,spec["validation_output"]).write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2));raise SystemExit(0 if not errors else 1)
