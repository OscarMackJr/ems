import argparse
import hashlib
import json
from pathlib import Path


def load(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()
def rp(root,rel): return root/Path(rel.replace("\\","/"))
ap=argparse.ArgumentParser();ap.add_argument("--ems-root",required=True);ap.add_argument("--spec",required=True)
a=ap.parse_args();ems=Path(a.ems_root).resolve();spec=load(Path(a.spec));errors=[]
regp=rp(ems,spec["baseline_registration"]);cp=rp(ems,spec["certification_output"]);mp=rp(ems,spec["manifest_output"])
for p in (regp,cp,mp):
    if not p.exists(): errors.append(f"missing {p}")
if not errors:
    reg=load(regp);cert=load(cp)
    if reg.get("status")!="PASS" or reg.get("baseline_state")!="AUTHORITATIVE": errors.append("baseline not authoritative")
    if cert.get("status")!="PASS" or cert.get("baseline_registration_sha256")!=sha(regp): errors.append("certification/hash invalid")
out={"status":"PASS" if not errors else "FAIL","wave":"2D","control_id":"EMS-CTRL-010","target_id":"REPO-001","baseline_state":"AUTHORITATIVE" if not errors else "BLOCKED","errors":errors}
print(json.dumps(out,indent=2));raise SystemExit(0 if not errors else 1)
