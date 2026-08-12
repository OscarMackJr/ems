import argparse,csv,json
from pathlib import Path
import yaml

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry",required=True)
    ap.add_argument("--impact-matrix",required=True)
    ap.add_argument("--outdir",required=True)
    a=ap.parse_args()

    reg=yaml.safe_load(Path(a.registry).read_text(encoding="utf-8")) or {}
    controls=reg.get("controls",[])

    with Path(a.impact_matrix).open(encoding="utf-8-sig",newline="") as fh:
        impact=list(csv.DictReader(fh))

    by_control={}
    for r in impact:
        cid=r["control_id"]
        d=by_control.setdefault(cid,{
            "row_count":0,
            "not_evaluated_count":0,
            "repositories":set()
        })
        d["row_count"]+=1
        if r["current_status"]=="NOT_EVALUATED":
            d["not_evaluated_count"]+=1
        d["repositories"].add(r["repository_name"])

    rows=[]
    for c in controls:
        cid=c["control_id"]
        imp=by_control.get(cid,{"row_count":0,"not_evaluated_count":0,"repositories":set()})
        priority="HIGH" if c["scope"]!="REPOSITORY" and imp["not_evaluated_count"]>0 else ("MEDIUM" if imp["not_evaluated_count"]>0 else "LOW")
        rows.append({
            "control_id":cid,
            "control_name":c["control_name"],
            "current_scope":c["scope"],
            "scope_owner":c["scope_owner"],
            "inheritance_allowed":c["inheritance_allowed"],
            "evidence_authority":c["evidence_authority"],
            "classification_status":c["classification_status"],
            "current_rationale":c["rationale"],
            "repository_row_count":imp["row_count"],
            "not_evaluated_row_count":imp["not_evaluated_count"],
            "affected_repositories":";".join(sorted(imp["repositories"])),
            "review_priority":priority,
            "reviewer_decision":"",
            "proposed_scope":"",
            "reviewer_rationale":"",
            "reviewer":"",
            "review_date":""
        })

    out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    with (out/"scope_registry_adjudication_queue.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys()))
        w.writeheader();w.writerows(rows)

    summary={
        "control_count":len(rows),
        "high_priority_count":sum(r["review_priority"]=="HIGH" for r in rows),
        "medium_priority_count":sum(r["review_priority"]=="MEDIUM" for r in rows),
        "low_priority_count":sum(r["review_priority"]=="LOW" for r in rows),
        "non_repository_controls":sum(r["current_scope"]!="REPOSITORY" for r in rows),
        "not_evaluated_rows_represented":sum(r["not_evaluated_row_count"] for r in rows)
    }
    (out/"scope_registry_adjudication_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
