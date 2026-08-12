import argparse,csv,json
from pathlib import Path

TARGET={"EMS-CTRL-034","EMS-CTRL-036","EMS-CTRL-038","EMS-CTRL-039"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--compliance",required=True)
    ap.add_argument("--applicability",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    with Path(a.compliance).open(encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))
    app=json.loads(Path(a.applicability).read_text(encoding="utf-8"))
    amap={(x["repository_name"],x["control_id"]):x for x in app}

    changed=[]
    for r in rows:
        key=(r["repository_name"],r["control_id"])
        if r["control_id"] not in TARGET or key not in amap: continue
        x=amap[key]
        r["applicability"]=x["applicability"]
        r["applicability_reason"]=x["applicability_reason"]
        r["applicability_source"]=x["decision_source"]
        if x["applicability"]=="NOT_APPLICABLE":
            old=r["compliance_status"]
            r["pre_applicability_status"]=old
            r["compliance_status"]="NOT_APPLICABLE"
            changed.append({"repository_name":r["repository_name"],"control_id":r["control_id"],
                            "before":old,"after":"NOT_APPLICABLE"})
        else:
            r.setdefault("pre_applicability_status","")

    for r in rows:
        for c in ("applicability","applicability_reason","applicability_source","pre_applicability_status"):
            r.setdefault(c,"")

    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys()))
        w.writeheader();w.writerows(rows)
    print(json.dumps({"changed_count":len(changed),"changed_rows":changed},indent=2))

if __name__=="__main__":main()
