import argparse,csv,json,shutil
from pathlib import Path
import yaml

def owner_for(scope):
    return {
        "REPOSITORY":"Software Development",
        "SERVICE":"Software Development",
        "APPLICATION":"Software Development",
        "PLATFORM":"Software Development / Platform",
        "ORGANIZATION":"Engineering Leadership",
        "EMS":"EMS Governance"
    }[scope]

def authority_for(scope):
    return {
        "REPOSITORY":"Repository evidence",
        "SERVICE":"Service evidence",
        "APPLICATION":"Application evidence",
        "PLATFORM":"Platform evidence",
        "ORGANIZATION":"Organizational evidence",
        "EMS":"EMS evidence"
    }[scope]

def inherit_for(scope):
    return scope!="REPOSITORY"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--queue",required=True)
    ap.add_argument("--registry",required=True)
    ap.add_argument("--out-report",required=True)
    a=ap.parse_args()

    with Path(a.queue).open(encoding="utf-8-sig",newline="") as fh:
        q=list(csv.DictReader(fh))
    qmap={r["control_id"]:r for r in q}

    rpath=Path(a.registry)
    reg=yaml.safe_load(rpath.read_text(encoding="utf-8"))
    backup=rpath.with_suffix(rpath.suffix+".pre-adjudication.bak")
    shutil.copy2(rpath,backup)

    changes=[];approved=0;deferred=0

    for c in reg["controls"]:
        r=qmap.get(c["control_id"])
        if not r: continue
        d=(r.get("reviewer_decision") or "").strip()
        if d=="APPROVED":
            c["classification_status"]="APPROVED"
            c["rationale"]=r["reviewer_rationale"].strip()
            approved+=1
        elif d=="RECLASSIFY":
            old=c["scope"]
            new=r["proposed_scope"].strip()
            c["scope"]=new
            c["scope_owner"]=owner_for(new)
            c["inheritance_allowed"]=inherit_for(new)
            c["evidence_authority"]=authority_for(new)
            c["classification_status"]="APPROVED"
            c["rationale"]=r["reviewer_rationale"].strip()
            approved+=1
            changes.append({"control_id":c["control_id"],"before":old,"after":new})
        elif d=="DEFER":
            deferred+=1
            c["classification_status"]="PROVISIONAL"

    rpath.write_text(yaml.safe_dump(reg,sort_keys=False),encoding="utf-8")
    report={
        "approved_count":approved,
        "deferred_count":deferred,
        "reclassified_count":len(changes),
        "reclassifications":changes,
        "backup":str(backup)
    }
    Path(a.out_report).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out_report).write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
