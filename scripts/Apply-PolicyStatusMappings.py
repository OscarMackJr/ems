import argparse,csv,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--effective-compliance",required=True)
    ap.add_argument("--policy-queue",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    with Path(a.policy_queue).open(encoding="utf-8-sig",newline="") as fh:
        policies=list(csv.DictReader(fh))
    mappings={
        p["control_id"]:(p.get("approved_status_mapping") or "").strip()
        for p in policies if (p.get("approved_status_mapping") or "").strip()
    }

    with Path(a.effective_compliance).open(encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))

    changed=[]
    for r in rows:
        target=mappings.get(r["control_id"])
        if not target:
            continue
        old=r["compliance_status"]
        if old in {"POLICY_PENDING","FAIL","WARNING","NOT_EVALUATED"}:
            r["pre_policy_resolution_status"]=old
            r["compliance_status"]=target
            changed.append({
                "repository_name":r["repository_name"],
                "control_id":r["control_id"],
                "before":old,
                "after":target
            })
        else:
            r.setdefault("pre_policy_resolution_status","")

    if rows and "pre_policy_resolution_status" not in rows[0]:
        for r in rows:r["pre_policy_resolution_status"]=""

    with Path(a.out).open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys()))
        w.writeheader();w.writerows(rows)

    print(json.dumps({"changed_count":len(changed),"changed_rows":changed},indent=2))

if __name__=="__main__":main()
