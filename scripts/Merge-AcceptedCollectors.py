import argparse,csv,json
from pathlib import Path

ACCEPTED={"EMS-CTRL-015","EMS-CTRL-025","EMS-CTRL-031","EMS-CTRL-033","EMS-CTRL-037"}
POLICY_PENDING={"EMS-CTRL-020"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--baseline",required=True)
    ap.add_argument("--refined-v2",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    with Path(a.baseline).open(encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))

    refined=json.loads(Path(a.refined_v2).read_text(encoding="utf-8"))
    by={(x["repository_name"],x["control_id"]):x for x in refined if x["control_id"] in ACCEPTED}

    for r in rows:
        key=(r["repository_name"],r["control_id"])
        if key in by:
            x=by[key]
            r["pre_collector_acceptance_status"]=r["compliance_status"]
            r["compliance_status"]=x["status"]
            r["collector_version"]="v2"
            r["collector_assertions_json"]=json.dumps(x.get("assertions",{}),separators=(",",":"))
        else:
            r.setdefault("pre_collector_acceptance_status","")
            r.setdefault("collector_version","")
            r.setdefault("collector_assertions_json","")

        if r["control_id"] in POLICY_PENDING:
            r["pre_policy_pending_status"]=r["compliance_status"]
            r["compliance_status"]="POLICY_PENDING"
        else:
            r.setdefault("pre_policy_pending_status","")

    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0].keys())
    with out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(rows)

    counts={}
    for r in rows:counts[r["compliance_status"]]=counts.get(r["compliance_status"],0)+1
    print(json.dumps({"row_count":len(rows),"status_counts":counts},indent=2))

if __name__=="__main__":main()
